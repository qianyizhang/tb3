"""Offline lifecycle tests. No models, Docker, downloads or real trial mutation."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tb3_medical import core as c, workflow as w, packaging


class MedicalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.add("group", "g")
        (self.root / "proof.txt").write_text("review proof")

    def add(self, kind, key, **extra):
        row = {"schema_version": 1, "kind": kind, "id": key, "group_id": "g", **extra}
        c.write_new(self.root / "groups/g" / (key + ".json"), row)
        return row

    def test_decisions_preserve_card_and_actor(self):
        c.add_idea(self.root, "g", "idea", "An idea", "A question", "codex://source")
        original = c.lookup(self.root, "idea")
        c.decide(self.root, "idea", "parked", "Needs reference", "assistant", "codex://source")
        c.decide(self.root, "idea", "selected", "Reference ready", "user", "codex://later")
        self.assertEqual(c.lookup(self.root, "idea"), original)
        self.assertEqual(c.projection(self.root)["idea"]["current"]["disposition"], "selected")
        self.assertEqual(sum(r["kind"] == "decision" for r in c.load(self.root).values()), 2)

    def test_invalidation_propagates_without_rewriting_scores(self):
        self.add("evaluation", "e", reward=1, validity="supported")
        self.add("finding", "f", depends_on=["e"], validity="supported")
        self.add("export", "package", depends_on=["f"])
        self.add("finding", "unaffected", validity="supported")
        before = c.lookup(self.root, "e")
        issue = c.issue(self.root, ["e"], "confirmed", "Verifier bug reproduced", ["proof.txt"], "assistant")
        c.issue(self.root, ["e"], "suspected", "Separate concern", ["proof.txt"], "assistant")
        rows = c.projection(self.root)
        self.assertEqual(rows["e"]["current"]["validity"], "invalidated")
        self.assertEqual(rows["f"]["current"]["validity"], "under_review")
        self.assertTrue(rows["package"]["current"]["need_fix"])
        self.assertEqual(rows["unaffected"]["current"]["validity"], "supported")
        self.assertEqual(c.lookup(self.root, "e"), before)

    def test_review_resolution_requires_current_proof(self):
        self.add("evaluation", "e", reward=0)
        issue = c.issue(self.root, ["e"], "confirmed", "Bug", ["proof.txt"], "assistant")
        (self.root / "correction.txt").write_text("Corrected replay")
        c.review(self.root, "e", "qualified", "Corrected evaluation", ["correction.txt"], "assistant", [issue["id"]])
        self.assertEqual(c.projection(self.root)["e"]["current"]["validity"], "qualified")
        (self.root / "correction.txt").write_text("Different evidence")
        self.assertEqual(c.projection(self.root)["e"]["current"]["validity"], "invalidated")

    def test_missing_local_evidence_is_availability_not_failure(self):
        evidence = c.evidence(self.root, "proof.txt")
        self.add("evaluation", "e", evidence=[evidence], reward=1, validity="qualified")
        (self.root / "proof.txt").unlink()
        row = c.projection(self.root)["e"]
        self.assertEqual(row["current"]["availability"], "missing_local")
        self.assertEqual(row["current"]["validity"], "qualified")
        self.assertEqual(row["reward"], 1)

    def test_duplicate_alias_and_dependency_cycle_are_errors(self):
        self.add("experiment", "a", aliases=["BR-025"])
        self.add("experiment", "b", aliases=["BR-025"])
        with self.assertRaises(c.MedicalError): c.lookup(self.root, "BR-025")
        self.add("finding", "loop", depends_on=["loop"])
        with self.assertRaises(c.MedicalError): c.validate(self.root)

    def test_freeze_is_recoverable_and_plan_requires_controls(self):
        exp = w.new(self.root, "g", "study", "Study")
        with self.assertRaises(c.MedicalError): w.freeze(self.root, "study")
        p = self.root / c.lookup(self.root, "study")["record_path"]
        exp["execution_enabled"] = True; c.atomic_write(p, exp)
        frozen = w.freeze(self.root, "study")
        planned = w.plan(self.root, frozen["id"], "codex", "test/model", "high")
        with self.assertRaises(c.MedicalError): w.check_controls(self.root, planned)
        import shutil
        shutil.rmtree(self.root / frozen["snapshot_path"])
        restored = w.restore_freeze(self.root, frozen)
        self.assertEqual(w.task_files(restored), frozen["files"])
        (restored / "instruction.md").write_text("Mutated")
        with self.assertRaises(c.MedicalError): w.restore_freeze(self.root, frozen)

    def test_failed_launcher_keeps_receipt_and_plan_cannot_retry(self):
        exp = w.new(self.root, "g", "study", "Study"); exp["execution_enabled"] = True
        c.atomic_write(self.root / c.lookup(self.root, "study")["record_path"], exp)
        frozen = w.freeze(self.root, "study")
        planned = w.plan(self.root, frozen["id"], "oracle")
        with patch.object(w, "harbor_checksum", return_value="a" * 64), patch.object(w.subprocess, "run", return_value=subprocess.CompletedProcess([], 9)):
            receipt = w.run(self.root, planned["id"], "fake-harbor")
        self.assertEqual(receipt["state"], "execution_error")
        self.assertTrue(receipt["frozen_payload_unchanged"])
        with patch.object(w, "harbor_checksum", return_value="a" * 64), self.assertRaises(FileExistsError):
            w.run(self.root, planned["id"], "fake-harbor")

    def test_symlink_and_absolute_paths_rejected(self):
        (self.root / "link").symlink_to("proof.txt")
        for path in ["../escape", "/etc/passwd", "link"]:
            with self.assertRaises(c.MedicalError): c.evidence(self.root, path)

    def test_partial_collection_is_one_attempt_with_immutable_observations(self):
        self.add("experiment", "e")
        trial = self.root / "runs/job/trial/result.json"
        record = {"task_name": "demo", "trial_name": "trial", "config": {"agent": {"name": "oracle", "env": {"SECRET": "never-retain"}}}, "finished_at": None}
        c.write_new(trial, record)
        first = w.collect(self.root, "e", [str(trial.relative_to(self.root))])[0]
        self.assertEqual(first["completeness"], "partial")
        self.assertNotIn("never-retain", json.dumps(first))
        record["finished_at"] = "2026-09-20T10:00:00Z"; c.atomic_write(trial, record)
        later = w.collect(self.root, "e", [str(trial.relative_to(self.root))])[0]
        self.assertNotEqual(first["id"], later["id"])
        self.assertEqual(first["attempt_id"], later["attempt_id"])
        w.collect(self.root, "e", [str(trial.relative_to(self.root))])
        self.assertEqual(sum(r["kind"] == "evaluation" for r in c.load(self.root).values()), 2)

    def test_package_hashes_missing_inputs_and_no_overwrite(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "--allow-empty", "-qm", "fixture"], cwd=self.root, check=True)
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        recipe = {"schema_version": 1, "mode": "exact", "qualification": "draft", "source_commit": commit, "depends_on": [], "target_profile": "test", "remaining_gates": ["current TB3 rules"], "files": [{"source": "proof.txt", "destination": "task/license.txt", "sha256": c.sha(self.root / "proof.txt"), "role": "license"}]}
        c.write_new(self.root / "recipe.json", recipe)
        packaging.export(self.root, "recipe.json", self.root / "package")
        self.assertEqual(packaging.verify(self.root / "package")["verified_files"], 1)
        with self.assertRaises(c.MedicalError): packaging.export(self.root, "recipe.json", self.root / "package")
        (self.root / "proof.txt").unlink()
        with self.assertRaisesRegex(c.MedicalError, "Restore required artifacts"):
            packaging.export(self.root, "recipe.json", self.root / "another")
        self.assertFalse((self.root / "another").exists())


if __name__ == "__main__": unittest.main()
