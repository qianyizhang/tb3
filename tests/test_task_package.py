"""Portable packages must work without author paths and reject changed inputs."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tb3_medical import task_package as package


class TaskPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        script = self.root / "evaluate.py"
        script.write_text(
            "import argparse,json\nfrom pathlib import Path\n"
            "p=argparse.ArgumentParser();p.add_argument('--answer');a=p.parse_args()\n"
            "print(json.dumps({'reward':int((Path(a.answer)/'answer.json').exists())}))\n"
        )
        expected = self.root / "expected.json"
        expected.write_text('{"reward":1}\n')
        answer = self.root / "answer.json"
        answer.write_text('{"answer":42}\n')
        self.manifest = {
            "experiment_id": "study",
            "cases": {
                "example": {
                    "evaluator": "cases/example/evaluate.py",
                    "controls": {
                        "oracle": {"answer": "saved/answer", "reward": 1},
                        "nop": {"answer": "cases/example/nop", "reward": 0},
                    },
                    "observations": [
                        {
                            "attempt_id": "old",
                            "source_evaluation": "original",
                            "answer": "saved/answer",
                            "expected": "saved/expected.json",
                        }
                    ],
                }
            },
            "files": [],
        }
        for source, name in [
            (script, "cases/example/evaluate.py"),
            (expected, "saved/expected.json"),
            (answer, "saved/answer/answer.json"),
        ]:
            self.manifest["files"].append(
                {
                    "source": source.name,
                    "path": name,
                    "size": source.stat().st_size,
                    "sha256": package.sha(source),
                    "mode": 0o644,
                    "case": "example",
                    "origin": "artifact",
                    "role": "task",
                }
            )
        self.recipe = self.root / "recipe.json"
        package.write(self.recipe, self.manifest)

    def build(self):
        dest = self.root / "portable"
        package.materialize(self.root, "recipe.json", dest)
        return dest

    def test_standalone_replay_after_author_sources_are_removed(self):
        dest = self.build()
        for name in ["evaluate.py", "expected.json", "answer.json", "recipe.json"]:
            (self.root / name).unlink()
        result = subprocess.run(
            [sys.executable, str(dest / "reproduce.py"), "replay"],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["all_match"])
        self.assertFalse(any("source" in f for f in package.read(dest / "manifest.json")["files"]))

    def test_recovery_from_transferred_input_root(self):
        dest = self.build()
        (self.root / "answer.json").unlink()
        restored = self.root / "restored"
        package.materialize(self.root, "recipe.json", restored, input_root=dest)
        self.assertEqual((restored / "saved/answer/answer.json").read_text(), '{"answer":42}\n')

    def test_bundle_preserves_review_flags_and_writes_lineage(self):
        from tb3_medical import core as c, workflow as w

        experiment = {"id": "study", "reproduction_manifest": "recipe.json"}
        state = {"assessment": "needs_review", "attention": True}
        with (
            patch.object(c, "lookup", return_value=experiment),
            patch.object(c, "projection", return_value={"study": {"current": state}}),
        ):
            with self.assertRaisesRegex(c.MedicalError, "needs review"):
                w.bundle(self.root, "study", self.root / "denied")
            self.assertFalse((self.root / "denied").exists())
            result = w.bundle(self.root, "study", self.root / "handoff", include_flagged=True)
        manifest = package.read(self.root / "handoff/manifest.json")
        self.assertEqual(manifest["source_assessments"], {"study": state})
        record = package.read(self.root / "exports/records" / (result["record"] + ".json"))
        self.assertEqual(record["review_flags_at_export"], {"study": state})
        self.assertEqual(
            record["manifest_sha256"], package.sha(self.root / "handoff/manifest.json")
        )

    def test_replay_appends_observation_and_preserves_original_execution(self):
        from tb3_medical import core as c, workflow as w

        dest = self.build()
        experiment = {
            "id": "study",
            "group_id": "g",
            "record_path": "groups/g/experiments/study/experiment.toml",
            "reproduction_manifest": "recipe.json",
        }
        original = {"execution_state": "interrupted", "outcome": "unknown"}
        with patch.object(c, "load", return_value={"original": original}):
            result = w.replay_package(
                self.root,
                experiment,
                dest,
                package.read(dest / "manifest.json"),
                "example",
                sys.executable,
            )
            w.replay_package(
                self.root,
                experiment,
                dest,
                package.read(dest / "manifest.json"),
                "example",
                sys.executable,
            )
        files = list((self.root / "groups/g/experiments/study/evaluations").glob("*.json"))
        self.assertEqual(len(files), 1)
        row = package.read(files[0])
        self.assertEqual(row["evaluation_kind"], "saved_output_replay")
        self.assertEqual(row["execution_state"], "interrupted")
        self.assertEqual(row["outcome"], "unknown")
        self.assertTrue(result["all_match"])
        self.assertEqual(original, {"execution_state": "interrupted", "outcome": "unknown"})

    def test_changed_input_fails_before_creating_destination(self):
        (self.root / "answer.json").write_text("{}\n")
        with self.assertRaisesRegex(ValueError, "Changed preparation input"):
            self.build()
        self.assertFalse((self.root / "portable").exists())

    def test_tampering_stops_evaluator(self):
        dest = self.build()
        marker = self.root / "should-not-run"
        (dest / "cases/example/evaluate.py").write_text(f"open({str(marker)!r},'w').close()\n")
        with self.assertRaisesRegex(ValueError, "Changed package input"):
            package.evaluate(dest, package.read(dest / "manifest.json"), "example", dest)
        self.assertFalse(marker.exists())

    def test_path_escape_and_duplicate_destination_are_rejected(self):
        self.manifest["files"][0]["path"] = "../escaped"
        package.write(self.recipe, self.manifest)
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.build()
        self.manifest["files"][0]["path"] = "saved/expected.json"
        package.write(self.recipe, self.manifest)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.build()

    def test_noop_failure_is_expected_but_metric_mismatch_fails_replay(self):
        dest = self.build()
        manifest = package.read(dest / "manifest.json")
        self.assertTrue(package.controls(dest, manifest)["all_expected"])
        target = dest / "saved/expected.json"
        target.write_text('{"reward":0}\n')
        entry = next(e for e in manifest["files"] if e["path"] == "saved/expected.json")
        entry.update(size=target.stat().st_size, sha256=package.sha(target))
        package.write(dest / "manifest.json", manifest)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(package.main(["replay", "--root", str(dest)]), 1)

    def test_metric_comparison_preserves_schema_booleans_and_finiteness(self):
        self.assertTrue(package.compare({"distance": 2.0}, {"distance": 2.0 + 1e-9}))
        self.assertFalse(package.compare({"distance": 2.0}, {"distance": 3.0}))
        self.assertFalse(package.compare({"passed": 1}, {"passed": True}))
        self.assertFalse(package.compare({"distance": float("nan")}, {"distance": 0.0}))
        self.assertFalse(package.compare({"a": 1, "b": 2}, {"a": 1}))


if __name__ == "__main__":
    unittest.main()
