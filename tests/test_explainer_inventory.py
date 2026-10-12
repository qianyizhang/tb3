"""Evidence availability joins retain missing data and execution boundaries."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tb3_medical import storage
from tb3_medical.explainers.inventory import HASH_LIMIT, artifact, build_inventory


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write(
            "presentation/EXPLAINER-SCOPE.json",
            {
                "schema": 1,
                "groups": [{"group_id": "research", "priority": "P0", "scope": "core"}],
                "entries": [
                    {"entry_id": "real", "group_id": "research", "automatic_completion": True},
                    {"entry_id": "symbolic", "group_id": "research", "automatic_completion": True},
                    {"entry_id": "excluded", "group_id": "research", "automatic_completion": False},
                ],
            },
        )
        self.write(
            "presentation/EXPLAINER-LEDGER.json",
            {
                "schema": 1,
                "entries": [
                    {
                        "entry_id": "real",
                        "catalogue": "presentation/leaf.json",
                        "source_review": {"receipt": "audit.json"},
                    },
                    {
                        "entry_id": "symbolic",
                        "catalogue": "presentation/leaf.json",
                        "source_asset_readiness": "all assets ready",
                    },
                    {"entry_id": "excluded", "catalogue": "missing.json"},
                ],
            },
        )
        self.write(
            "presentation/leaf.json",
            {
                "entries": [
                    {
                        "id": "real",
                        "experiments": [{"id": "experiment-a", "scope": "condition-one"}],
                        "illustration": {"story_id": "real-story"},
                    },
                    {
                        "id": "symbolic",
                        "experiments": [{"id": "absent", "scope": "not yet retained"}],
                        "illustration": {"story_id": "absent-story"},
                    },
                ]
            },
        )
        self.write("audit.json", {"source_pins": {"native.json": "0" * 64, "absent.npy": "1" * 64}})
        self.write("native.json", {"value": 2})
        self.write("groups/demo/presentation/stories/real-story.story.md", "retained story")
        self.write(
            "groups/demo/experiments/a/experiment.toml",
            'id = "experiment-a"\nprotocol = "protocol.md"\n',
        )
        self.write("groups/demo/experiments/a/protocol.md", "condition-one")
        self.write(
            "groups/demo/experiments/a/attempts/model.json",
            {"id": "model", "source_result": "runs/model/result.json"},
        )
        self.write(
            "groups/demo/experiments/a/attempts/oracle.json",
            {"id": "oracle", "source_result": "runs/oracle/result.json"},
        )
        self.write(
            "groups/demo/experiments/a/attempts/missing.json",
            {"id": "missing", "source_result": "runs/missing/result.json"},
        )
        for agent in ("model", "oracle"):
            self.write(
                f"runs/{agent}/result.json",
                {
                    "config": {
                        "agent": {
                            "name": "codex" if agent == "model" else "oracle",
                            "model_name": "test/model",
                        },
                        "task": {"path": "task"},
                    }
                },
            )
            self.write(f"runs/{agent}/agent/trajectory.json", {"steps": [{"action": "inspect"}]})
        self.write("runs/model/artifacts/app/answer.json", {"point": [1, 2, 3]})
        self.write("task/instruction.md", "return a point")

    def write(self, relative: str, value: object) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value))

    def test_join_preserves_conditions_and_excludes_symbolic_assets_from_traces(self) -> None:
        report = build_inventory(self.root)
        self.assertEqual(report["summary"]["core_entries"], 2)
        self.assertEqual(report["summary"]["entries_with_model_trace_artifacts"], 1)
        real, symbolic = report["entries"]
        self.assertEqual(real["experiments"][0]["scope"], "condition-one")
        self.assertEqual(real["coverage"]["attempt_records"], 3)
        self.assertEqual(real["coverage"]["model_attempts_identified"], 1)
        self.assertEqual(real["coverage"]["model_attempts_with_submitted_outputs"], 1)
        self.assertEqual(symbolic["candidate_basis"], "source-resolution-or-task-mechanism")
        self.assertEqual(symbolic["experiments"][0]["status"], "not-retained")
        self.assertEqual(symbolic["story"]["status"], "not-retained")
        missing = next(
            item for item in real["experiments"][0]["attempts"] if item["attempt_id"] == "missing"
        )
        self.assertEqual(missing["source_result"]["status"], "not-retained")
        self.assertFalse(missing["trace_artifacts_present"])

    def test_audit_pins_compare_retained_bytes_without_claiming_missing_sources(self) -> None:
        row = build_inventory(self.root)["entries"][0]
        sources = {item["path"]: item for item in row["audit_source_pins"]}
        self.assertFalse(sources["native.json"]["hash_matches"])
        self.assertEqual(sources["absent.npy"]["status"], "not-retained")
        self.assertEqual(sources["native.json"]["sha256"], storage.sha(self.root / "native.json"))

    def test_paths_and_large_files_have_explicit_limits(self) -> None:
        self.assertEqual(artifact(self.root, None)["status"], "not-declared")
        self.assertEqual(artifact(self.root, "../outside.json")["status"], "outside-workspace")
        self.assertEqual(artifact(self.root, "/etc/hosts")["status"], "outside-workspace")
        (self.root / "large.bin").write_bytes(b"x" * (HASH_LIMIT + 1))
        large = artifact(self.root, "large.bin", expected="a" * 64)
        self.assertEqual(large["hash_status"], "skipped-size-limit")
        self.assertNotIn("sha256", large)
        self.assertNotIn("hash_matches", large)
        self.assertEqual(large["declared_sha256"], "a" * 64)
        (self.root / "link").symlink_to("/etc/hosts")
        self.assertEqual(artifact(self.root, "link")["status"], "outside-workspace")


if __name__ == "__main__":
    unittest.main()
