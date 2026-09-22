"""Evidence inventories stay deterministic and separate collection from interpretation."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tb3_medical import cli, evidence
from tb3_medical import core as c


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "workbench.toml").write_text('name = "fixture"\n')
        self.write(
            "groups/g/group.json",
            {"schema_version": 2, "kind": "group", "id": "g", "title": "Group"},
        )
        self.write(
            "groups/g/experiments/e/experiment.toml",
            {
                "schema_version": 2,
                "kind": "experiment",
                "id": "e",
                "group_id": "g",
                "title": "Experiment",
                "experiment_stage": "closed",
            },
        )
        self.write(
            "groups/g/experiments/e/attempts/a.json",
            {
                "schema_version": 2,
                "kind": "attempt",
                "id": "a",
                "group_id": "g",
                "experiment_id": "e",
                "agent": "codex",
                "model": "model-a",
            },
        )
        (self.root / ".local/result.json").parent.mkdir()
        (self.root / ".local/result.json").write_text('{"score": 0.5}\n')
        self.write(
            "groups/g/experiments/e/evaluations/v.json",
            {
                "schema_version": 2,
                "kind": "evaluation",
                "id": "v",
                "group_id": "g",
                "experiment_id": "e",
                "attempt_id": "a",
                "evaluation_kind": "result",
                "execution_state": "completed",
                "outcome": "pass",
                "task_digest": "task-one",
                "collected_at": "2026-02-01T00:00:00+00:00",
                "evidence": [
                    {
                        "label": "Trial result",
                        "path": ".local/result.json",
                        "sha256": c.sha(self.root / ".local/result.json"),
                    }
                ],
            },
        )
        self.write(
            "groups/g/experiments/e/evaluations/old.json",
            {
                "schema_version": 2,
                "kind": "evaluation",
                "id": "old",
                "group_id": "g",
                "experiment_id": "e",
                "attempt_id": "a",
                "evaluation_kind": "result",
                "execution_state": "completed",
                "outcome": "fail",
                "task_digest": "task-one",
                "collected_at": "2026-01-01T00:00:00+00:00",
            },
        )
        self.write(
            "groups/g/experiments/e/freezes/z.json",
            {
                "schema_version": 2,
                "kind": "freeze",
                "id": "z",
                "group_id": "g",
                "experiment_id": "e",
                "task_digest": "task-one",
                "snapshot_path": ".local/freezes/task-one/task",
                "files": {
                    "instruction.md": "i" * 64,
                    "environment/data/image.nii.gz": "d" * 64,
                    "tests/score.py": "s" * 64,
                    "tests/reference/gt.nii.gz": "r" * 64,
                },
            },
        )
        self.write(
            "groups/g/findings/f.json",
            {
                "schema_version": 2,
                "kind": "finding",
                "analysis_kind": "result",
                "id": "f",
                "group_id": "g",
                "title": "Result",
                "claim": "A measured result.",
                "experiment_ids": ["e"],
                "evidence": [
                    {
                        "path": "groups/g/findings/evidence/missing.json",
                        "sha256": "0" * 64,
                    }
                ],
            },
        )
        self.write(
            "groups/g/findings/sibling.json",
            {
                "schema_version": 2,
                "kind": "finding",
                "analysis_kind": "synthesis",
                "id": "sibling",
                "group_id": "g",
                "title": "Sibling",
                "claim": "A separate analysis of the same experiment.",
                "experiment_ids": ["e"],
            },
        )

    def write(self, relative, value):
        c.publish(self.root / relative, value)

    def test_collect_check_and_build_preserve_identity_and_boundaries(self):
        data = evidence.collect(self.root, ["f"])
        self.assertEqual(data["comparability"]["observed_task_digests"], ["task-one"])
        self.assertTrue(data["comparability"]["same_observed_task_digest"])
        self.assertEqual([finding["id"] for finding in data["findings"]], ["f"])
        self.assertNotIn("sibling", {row["id"] for row in data["record_refs"]})
        observations = data["experiments"][0]["observations"]
        self.assertEqual([observation["evaluation_id"] for observation in observations], ["v"])
        roles = data["experiments"][0]["contracts"][0]["roles"]
        self.assertEqual(set(roles), {"instruction", "input", "evaluator", "reference"})
        states = {p["path"]: p["availability"] for p in data["artifacts"]["selected_pointers"]}
        self.assertEqual(states[".local/result.json"], "present")
        self.assertEqual(states["groups/g/findings/evidence/missing.json"], "missing_local")
        self.assertIn("Question ground truth", " ".join(data["interpretation_boundaries"]))

        manifest = self.root / "packet.json"
        evidence.write_manifest(manifest, data)
        self.assertEqual(evidence.check(self.root, manifest)["record_hashes"], "match")
        output = self.root / "packet.md"
        evidence.build(self.root, manifest, output)
        rendered = output.read_text()
        self.assertIn("Machine-built identity and availability index", rendered)
        self.assertIn("Interpretation still required", rendered)

        (self.root / ".local/result.json").write_text('{"score": 0.9}\n')
        with self.assertRaisesRegex(c.MedicalError, "artifact drift"):
            evidence.check(self.root, manifest)
        (self.root / ".local/result.json").write_text('{"score": 0.5}\n')

        missing = self.root / "groups/g/findings/evidence/missing.json"
        missing.parent.mkdir(parents=True)
        missing.write_text("{}\n")
        with self.assertRaisesRegex(c.MedicalError, "artifact drift"):
            evidence.check(self.root, manifest)
        missing.unlink()

        finding = self.root / "groups/g/findings/f.json"
        finding.write_text(finding.read_text().replace("A measured result.", "Changed claim."))
        with self.assertRaisesRegex(c.MedicalError, "manifest is stale"):
            evidence.check(self.root, manifest)

    def test_new_scaffolds_a_first_class_finding_and_cli_collect_writes_only_explicit_output(self):
        result = evidence.new(self.root, "g", "new-analysis", "New analysis", "audit", ["e"])
        row = c.read(self.root / result["record"])
        self.assertEqual((row["kind"], row["analysis_kind"]), ("finding", "audit"))
        self.assertEqual(row["experiment_ids"], ["e"])
        self.assertTrue((self.root / result["report"]).is_file())
        self.assertTrue((self.root / result["evidence"]).is_file())

        output = io.StringIO()
        destination = self.root / "explicit.json"
        with redirect_stdout(output):
            code = cli.main(
                [
                    "--root",
                    str(self.root),
                    "evidence",
                    "collect",
                    "e",
                    "--output",
                    str(destination),
                ]
            )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["output"], str(destination))
        self.assertTrue(destination.is_file())

    def test_invalid_analysis_kind_is_rejected(self):
        row = c.read(self.root / "groups/g/findings/f.json")
        row["analysis_kind"] = "narrative"
        with self.assertRaisesRegex(c.MedicalError, "unknown analysis_kind"):
            c.validate_record(row, "finding")


if __name__ == "__main__":
    unittest.main()
