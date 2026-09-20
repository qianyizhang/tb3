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
from tb3_medical import core as c, workflow as w, packaging, presentation


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

    def test_multi_target_issue_resolves_each_target_independently(self):
        self.add("evaluation", "a"); self.add("evaluation", "b")
        issue = c.issue(self.root, ["a", "b"], "confirmed", "Shared defect", ["proof.txt"], "assistant")
        c.review(self.root, "a", "qualified", "A replay fixed", ["proof.txt"], "assistant", [issue["id"]])
        rows = c.projection(self.root)
        self.assertEqual(rows["a"]["current"]["validity"], "qualified")
        self.assertEqual(rows["b"]["current"]["validity"], "invalidated")
        c.review(self.root, "b", "qualified", "B replay fixed", ["proof.txt"], "assistant", [issue["id"]])
        self.assertEqual(c.projection(self.root)["b"]["current"]["validity"], "qualified")

    def enabled_study(self):
        exp = w.new(self.root, "g", "study", "Study"); exp["execution_enabled"] = True
        c.atomic_write(self.root / c.lookup(self.root, "study")["record_path"], exp)
        return w.freeze(self.root, "study")

    def fake_harbor(self, argv, **kwargs):
        config_path = Path(argv[-1]); config = c.read(config_path)
        agent = config["agents"][0]["name"]
        phase = {"started_at": "2026-09-20T00:00:00Z", "finished_at": "2026-09-20T00:00:01Z"}
        trial = config_path.parent / "job/trial/result.json"
        c.write_new(trial, {**phase, "task_name": "task", "trial_name": "trial", "task_checksum": "a" * 64,
                           "config": {"agent": config["agents"][0]}, "agent_execution": phase,
                           "verifier": phase, "exception_info": None,
                           "verifier_result": {"rewards": {"reward": 1 if agent == "oracle" else 0}}})
        return subprocess.CompletedProcess(argv, 0)

    def test_controls_and_model_plan_use_one_exact_frozen_condition(self):
        frozen = self.enabled_study()
        model = w.plan(self.root, frozen["id"], "codex", "test/model", "high")
        with patch.object(w, "harbor_checksum", return_value="a" * 64), patch.object(w.subprocess, "run", side_effect=self.fake_harbor) as launch:
            with self.assertRaises(c.MedicalError): w.run(self.root, model["id"], "fake-harbor")
            self.assertFalse(launch.called)
            for agent in ("oracle", "nop"):
                planned = w.plan(self.root, frozen["id"], agent)
                self.assertEqual(w.run(self.root, planned["id"], "fake-harbor")["state"], "completed")
            receipt = w.run(self.root, model["id"], "fake-harbor")
            self.assertEqual(len(receipt["collected"]), 1)
        row = c.lookup(self.root, receipt["collected"][0])
        self.assertTrue(row["freeze_checksum_verified"])
        self.assertEqual(row["classification"], "model_failure_candidate")
        self.assertEqual(sum(r["kind"] == "attempt" for r in c.load(self.root).values()), 3)

    def test_experiment_revocation_and_invalidation_block_preexisting_plan(self):
        frozen = self.enabled_study(); planned = w.plan(self.root, frozen["id"], "oracle")
        # Retained immutable freezes made by the earlier interface lack this edge.
        freeze_path = self.root / c.lookup(self.root, frozen["id"])["record_path"]
        original = c.read(freeze_path); original["depends_on"] = []; c.atomic_write(freeze_path, original)
        path = self.root / c.lookup(self.root, "study")["record_path"]; exp = c.read(path)
        exp["execution_enabled"] = False; c.atomic_write(path, exp)
        with patch.object(w.subprocess, "run") as launch:
            with self.assertRaisesRegex(c.MedicalError, "disabled"): w.run(self.root, planned["id"], "fake")
            exp["execution_enabled"] = True; c.atomic_write(path, exp)
            c.issue(self.root, ["study"], "confirmed", "Defect reproduced", ["proof.txt"], "assistant")
            with self.assertRaisesRegex(c.MedicalError, "review"): w.run(self.root, planned["id"], "fake")
            self.assertFalse(launch.called)

    def test_interrupted_execution_collects_into_original_attempt(self):
        frozen = self.enabled_study(); planned = w.plan(self.root, frozen["id"], "oracle")
        def interrupted(argv, **kwargs):
            self.fake_harbor(argv, **kwargs)
            raise KeyboardInterrupt()
        with patch.object(w, "harbor_checksum", return_value="a" * 64), patch.object(w.subprocess, "run", side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt): w.run(self.root, planned["id"], "fake-harbor")
        source = "runs/medical/" + planned["id"] + "/job/trial/result.json"
        row = w.collect(self.root, "study", [source])[0]
        self.assertEqual(row["attempt_id"], "attempt-" + planned["id"])
        self.assertTrue(row["freeze_checksum_verified"])
        self.assertEqual(sum(r["kind"] == "attempt" for r in c.load(self.root).values()), 1)
        self.assertEqual(c.projection(self.root)[row["attempt_id"]]["current"]["execution"]["state"], "interrupted")
        self.assertEqual(w.collect(self.root, "study", [source])[0]["id"], row["id"])

    def test_collection_during_execution_appends_later_binding_without_duplicate_attempt(self):
        frozen = self.enabled_study(); planned = w.plan(self.root, frozen["id"], "oracle"); early = []
        def collect_while_running(argv, **kwargs):
            result = self.fake_harbor(argv, **kwargs)
            source = str((Path(argv[-1]).parent / "job/trial/result.json").relative_to(self.root))
            early.append(w.collect(self.root, "study", [source])[0])
            return result
        with patch.object(w, "harbor_checksum", return_value="a" * 64), patch.object(w.subprocess, "run", side_effect=collect_while_running):
            receipt = w.run(self.root, planned["id"], "fake")
        final = c.lookup(self.root, receipt["collected"][0])
        self.assertFalse(early[0]["freeze_checksum_verified"])
        self.assertTrue(final["freeze_checksum_verified"])
        self.assertNotEqual(early[0]["id"], final["id"])
        self.assertEqual(early[0]["attempt_id"], final["attempt_id"])

    def test_batch_collection_does_not_transfer_managed_identity_or_binding(self):
        frozen = self.enabled_study(); planned = w.plan(self.root, frozen["id"], "oracle")
        with patch.object(w, "harbor_checksum", return_value="a" * 64), patch.object(w.subprocess, "run", side_effect=self.fake_harbor):
            w.run(self.root, planned["id"], "fake")
        managed = "runs/medical/" + planned["id"] + "/job/trial/result.json"
        independent = "runs/independent/trial/result.json"
        c.write_new(self.root / independent, c.read(self.root / managed))
        first, second = w.collect(self.root, "study", [managed, independent])
        self.assertNotEqual(first["attempt_id"], second["attempt_id"])
        self.assertTrue(first["freeze_checksum_verified"])
        self.assertFalse(second["freeze_checksum_verified"])

    def test_portable_rebuild_removes_previous_local_media(self):
        (self.root / "presentation/tours/data").mkdir(parents=True)
        for name in ("index.html", "app.js", "style.css"): (self.root / "presentation" / name).write_text("fixture")
        (self.root / "presentation/tours/data/native-local.bin").write_bytes(b"local array")
        (self.root / "groups/g/presentation").mkdir()
        (self.root / "groups/g/presentation/story.md").write_text("# A portable story")
        group = c.read(self.root / "groups/g/g.json"); group["title"] = "Group"; c.atomic_write(self.root / "groups/g/g.json", group)
        out = self.root / ".cache/site"
        presentation.present(self.root, out, True)
        self.assertTrue((out / "presentation/tours/data/native-local.bin").exists())
        presentation.present(self.root, out, False)
        self.assertFalse((out / "presentation/tours/data/native-local.bin").exists())

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
        path = self.root / "package/manifest.json"; original_manifest = c.read(path)
        altered = {**original_manifest, "qualification": "submission-ready", "remaining_gates": []}; c.atomic_write(path, altered)
        with self.assertRaisesRegex(c.MedicalError, "pinned recipe"): packaging.verify(self.root / "package")
        c.atomic_write(path, original_manifest)
        (self.root / "package/unlisted-runtime.json").write_text('{}')
        with self.assertRaisesRegex(c.MedicalError, "inventory"): packaging.verify(self.root / "package")
        (self.root / "package/unlisted-runtime.json").unlink()
        (self.root / "package/recipe.json").write_text('{}')
        with self.assertRaisesRegex(c.MedicalError, "recipe changed"): packaging.verify(self.root / "package")
        moving = {**recipe, "source_commit": "HEAD"}; c.write_new(self.root / "moving.json", moving)
        with self.assertRaisesRegex(c.MedicalError, "immutable"): packaging.export(self.root, "moving.json", self.root / "moving")
        with self.assertRaises(c.MedicalError): packaging.export(self.root, "recipe.json", self.root / "package")
        (self.root / "proof.txt").unlink()
        with self.assertRaisesRegex(c.MedicalError, "Restore required artifacts"):
            packaging.export(self.root, "recipe.json", self.root / "another")
        self.assertFalse((self.root / "another").exists())


if __name__ == "__main__": unittest.main()
