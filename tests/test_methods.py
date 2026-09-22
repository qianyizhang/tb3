"""Exercise method dispatch through the CLI with real, temporary inputs."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tb3_medical import cli, core, task_package, workflow
from tb3_medical.methods import method_for


class MethodTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "workbench.toml").write_text("version=1\n")
        core.write_new(
            self.root / "groups/g/group.json",
            {"schema_version": 2, "kind": "group", "id": "g", "title": "Group"},
        )
        self.experiment = workflow.new(self.root, "g", "study", "Study")
        self.base = self.root / "groups/g/experiments/study"

    def configure(self, method, **fields):
        self.experiment.update(method=method, **fields)
        core.atomic_write(self.base / "experiment.toml", self.experiment)

    def invoke(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            status = cli.main(["--root", str(self.root), *args])
        return (
            status,
            json.loads(output.getvalue()) if output.getvalue() else None,
            error.getvalue(),
        )

    def test_landmark_scoring_verifies_reference_before_scoring(self):
        truth = {
            "points_ijk": {"p": [1, 2, 3]},
            "shape_ijk": [10, 10, 10],
            "linear_voxel_to_mm": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "tolerance_mm": 1,
        }
        core.write_new(self.root / "truth.json", truth)
        core.write_new(
            self.root / "inputs.json",
            {
                "cases": {
                    "one": {
                        "scorer": "mri",
                        "files": [
                            {
                                **core.evidence(self.root, "truth.json"),
                                "destination": "tests/truth.json",
                            }
                        ],
                    }
                }
            },
        )
        core.write_new(
            self.root / "answer/landmarks.json",
            {"space": "voxel_ijk_zero_based", "landmarks": {"p": [1, 2, 3]}},
        )
        self.configure("landmarks", input_manifest="inputs.json")
        args = ("evaluate", "study", "--case", "one", "--answer", str(self.root / "answer"))
        status, result, error = self.invoke(*args)
        self.assertEqual(status, 0, error)
        self.assertEqual(result["reward"], 1)
        (self.root / "truth.json").write_text("{}")
        status, _, error = self.invoke(*args)
        self.assertEqual(status, 1)
        self.assertIn("Changed input", error)

    def prepare_packages(self, expected_reward=1):
        evaluator = self.root / "evaluate.py"
        evaluator.write_text("print('{\"reward\": 1}')\n")
        core.write_new(self.root / "expected.json", {"reward": expected_reward})
        core.write_new(self.root / "answer.json", {"answer": 42})
        (self.root / "instruction.md").write_text("# Task\n\nInspect the sample.\n")
        manifest = {
            "experiment_id": "study",
            "cases": {
                name: {
                    "evaluator": "evaluate.py",
                    "task": "task",
                    "observations": [
                        {
                            "attempt_id": "original-attempt",
                            "source_evaluation": "original-evaluation",
                            "answer": "saved",
                            "expected": "expected.json",
                        }
                    ],
                }
                for name in ("a", "b")
            },
            "files": [
                {
                    "source": source,
                    "path": destination,
                    "sha256": core.sha(self.root / source),
                    "size": (self.root / source).stat().st_size,
                    "mode": 0o644,
                    "case": None,
                    "origin": "artifact",
                    "role": "task",
                }
                for source, destination in (
                    ("evaluate.py", "evaluate.py"),
                    ("expected.json", "expected.json"),
                    ("answer.json", "saved/answer.json"),
                    ("instruction.md", "task/instruction.md"),
                )
            ],
        }
        core.write_new(self.root / "recipe.json", manifest)
        self.configure(
            "task_package",
            reproduction_manifest="recipe.json",
            tasks=[{"id": name, "task_path": "unused/" + name} for name in ("a", "b")],
        )
        for kind, identity, fields in (
            ("attempt", "original-attempt", {}),
            (
                "evaluation",
                "original-evaluation",
                {
                    "attempt_id": "original-attempt",
                    "execution_state": "interrupted",
                    "outcome": "no_verdict",
                },
            ),
        ):
            core.write_new(
                self.base / (kind + "s") / (identity + ".json"),
                {
                    "schema_version": 2,
                    "kind": kind,
                    "id": identity,
                    "group_id": "g",
                    "experiment_id": "study",
                    **fields,
                },
            )
        for name in ("a", "b"):
            preview = workflow.prepare(self.root, "study", name)
            self.assertFalse(preview["executed"])
            self.assertFalse(Path(preview["destination"]).exists())
            workflow.prepare(self.root, "study", name, execute=True)

    def test_package_dispatch_replays_all_cases_without_changing_original_outcome(self):
        self.prepare_packages()
        original = self.base / "evaluations/original-evaluation.json"
        before = original.read_bytes()
        status, result, error = self.invoke("replay", "study", "--python", sys.executable)
        self.assertEqual(status, 0, error)
        self.assertTrue(result["all_match"])
        self.assertEqual(len(result["cases"]), 2)
        self.assertEqual(original.read_bytes(), before)
        self.assertEqual(len(list((self.base / "evaluations").glob("replay-*.json"))), 2)
        status, result, error = self.invoke(
            "evaluate",
            "study",
            "--case",
            "a",
            "--answer",
            str(self.root),
            "--python",
            sys.executable,
        )
        self.assertEqual(status, 0, error)
        self.assertEqual(result, {"reward": 1})

    def test_package_view_and_verification_preserve_portable_cli_outputs(self):
        self.prepare_packages()
        output = self.root / "view.html"
        status, result, error = self.invoke("view", "study", "--case", "b", "--output", str(output))
        self.assertEqual(status, 0, error)
        self.assertEqual(result["cases"][0]["output"], str(output))
        self.assertIn("Inspect the sample", output.read_text())
        bundle = self.root / ".local/reproduction/study/b"
        # Verification must work without discovering an author workspace.
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                cli.main(["--root", str(self.root / "missing"), "verify-package", str(bundle)]), 0
            )

    def test_package_replay_mismatch_is_a_nonzero_cli_result(self):
        self.prepare_packages(expected_reward=0)
        status, result, error = self.invoke("replay", "study", "--case", "a")
        self.assertEqual(status, 1, error)
        self.assertFalse(result["all_match"])
        self.assertEqual(len(result["cases"]), 1)

    def test_unknown_method_cannot_fall_through_to_package_evaluation(self):
        self.configure("historical-only")
        with patch.object(task_package, "evaluate", side_effect=AssertionError("Must not score")):
            status, _, error = self.invoke(
                "evaluate", "study", "--case", "a", "--answer", str(self.root)
            )
        self.assertEqual(status, 1)
        self.assertIn("No maintained method", error)

    def test_landmark_prepare_rejects_package_only_options(self):
        self.configure("landmarks")
        adapter = method_for(self.root, self.experiment)
        with self.assertRaisesRegex(core.MedicalError, "med bundle"):
            adapter.prepare({"id": "a"}, False, input_root=self.root)

    def test_evaluator_rejects_nonobject_json_at_the_process_boundary(self):
        self.prepare_packages()
        bundle = self.root / ".local/reproduction/study/a"
        script = bundle / "evaluate.py"
        script.write_text('print("[]")\n')
        manifest = core.read(bundle / "manifest.json")
        entry = next(item for item in manifest["files"] if item["path"] == "evaluate.py")
        entry.update(sha256=core.sha(script), size=script.stat().st_size)
        with self.assertRaisesRegex(ValueError, "JSON object"):
            task_package.evaluate(bundle, manifest, "a", self.root)
