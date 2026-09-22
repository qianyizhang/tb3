"""Offline regressions for the supported daily workflow; no model or Docker jobs."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tb3_medical import core as c
from tb3_medical import packaging, presentation
from tb3_medical import workflow as w


class MedicalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "workbench.toml").write_text("version=1\n")
        c.write_new(
            self.root / "groups/g/group.json",
            {
                "schema_version": 2,
                "kind": "group",
                "id": "g",
                "title": "Group",
                "experiment_ids": [],
            },
        )
        w.new(self.root, "g", "study", "Study")
        (self.root / "proof.txt").write_text("review proof")

    def test_explicit_record_locations_ignore_task_payload_and_reads_never_hash(self):
        task = self.root / "groups/g/experiments/study/task"
        (task / "misleading.json").write_text("{invalid payload")
        with patch.object(c, "sha", side_effect=AssertionError("Inspection hashed input")):
            self.assertEqual(c.validate(self.root)["records"], 2)
            self.assertFalse(c.projection(self.root)["study"]["current"]["attention"])
        (self.root / "groups/g/experiments/study/attempts").mkdir()
        c.write_new(
            self.root / "groups/g/experiments/study/attempts/bad.json",
            {"schema_version": 2, "kind": "attempt", "id": "bad"},
        )
        with self.assertRaisesRegex(c.MedicalError, "missing"):
            c.validate(self.root)

    def test_recommendation_does_not_overwrite_accepted_decision(self):
        c.add_idea(self.root, "g", "idea", "Idea", "Question", "codex://source")
        c.decide(self.root, "idea", "selected", "Accepted", "user", "codex://source")
        c.decide(self.root, "idea", "dropped", "Suggestion", "assistant", "codex://source")
        self.assertEqual(c.projection(self.root)["idea"]["current"]["idea_state"], "selected")
        self.assertEqual(c.lookup(self.root, "idea")["idea_state"], "exploring")

    def test_experiment_issue_reaches_summaries_and_scoped_reassessment_clears_attention(self):
        c.write_new(
            self.root / "groups/g/findings/f.json",
            {
                "schema_version": 2,
                "kind": "finding",
                "id": "f",
                "group_id": "g",
                "claim": "Scoped result",
                "experiment_ids": ["study"],
            },
        )
        c.write_new(
            self.root / "exports/records/export.json",
            {
                "schema_version": 2,
                "kind": "export",
                "id": "export",
                "experiment_ids": ["study"],
                "submission_status": "draft",
            },
        )
        issue = c.issue(self.root, ["study"], "Scorer bug", ["proof.txt"], "assistant")
        for key in ("study", "g", "f", "export"):
            self.assertTrue(c.projection(self.root)[key]["current"]["attention"])
        c.review(
            self.root,
            "study",
            "invalidated",
            "Withdraw old conclusion",
            "Old claim",
            ["proof.txt"],
            "assistant",
            [issue["id"]],
        )
        state = c.projection(self.root)
        self.assertFalse(state["study"]["current"]["attention"])
        self.assertEqual(state["export"]["current"]["review_flags"][0]["assessment"], "invalidated")
        c.review(
            self.root,
            "study",
            "usable",
            "Narrower conclusion survives",
            "Corrected scope",
            [],
            "assistant",
        )
        self.assertEqual(c.projection(self.root)["study"]["current"]["assessment"], "usable")
        self.assertEqual(sum(r["kind"] == "review" for r in c.load(self.root).values()), 2)

    def test_issue_flags_comparison_reusing_an_earlier_attempt(self):
        w.new(self.root, "g", "comparison", "Comparison")
        c.write_new(
            self.root / "groups/g/experiments/study/attempts/a.json",
            {
                "schema_version": 2,
                "kind": "attempt",
                "id": "a",
                "group_id": "g",
                "experiment_id": "study",
            },
        )
        c.write_new(
            self.root / "groups/g/experiments/comparison/evaluations/e.json",
            {
                "schema_version": 2,
                "kind": "evaluation",
                "id": "e",
                "experiment_id": "comparison",
                "attempt_id": "a",
                "execution_state": "completed",
                "outcome": "fail",
            },
        )
        issue = c.issue(self.root, ["a"], "Reference defect", [], "assistant")
        self.assertEqual(issue["experiment_ids"], ["comparison", "study"])
        self.assertTrue(c.projection(self.root)["comparison"]["current"]["attention"])

    def fake_harbor(self, argv, **kwargs):
        config_path = Path(argv[-1])
        config = c.read(config_path)
        agent = config["agents"][0]["name"]
        phase = {"started_at": "2026-09-20T00:00:00Z", "finished_at": "2026-09-20T00:00:01Z"}
        c.write_new(
            config_path.parent / "job/trial/result.json",
            {
                **phase,
                "task_name": "task",
                "trial_name": "trial",
                "task_checksum": "a" * 64,
                "config": {"agent": config["agents"][0]},
                "agent_execution": phase,
                "verifier": phase,
                "exception_info": None,
                "verifier_result": {"rewards": {"reward": 1 if agent == "oracle" else 0}},
            },
        )
        return subprocess.CompletedProcess(argv, 0)

    def run_fake(self, agent="oracle", **kwargs):
        return w.run(self.root, "study", agent, "fake-harbor", **kwargs)

    def test_diagnostic_then_controls_then_explicit_qualification(self):
        with (
            patch.object(w, "harbor_checksum", return_value="a" * 64),
            patch.object(w.subprocess, "run", side_effect=self.fake_harbor) as launch,
        ):
            with self.assertRaises(c.MedicalError):
                self.run_fake("codex", model="test/model")
            self.assertFalse(launch.called)
            diagnostic = self.run_fake("codex", model="test/model", diagnostic=True)
            with self.assertRaises(c.MedicalError):
                w.qualify_attempt(self.root, "study", diagnostic["attempt_id"])
            self.run_fake("oracle")
            self.run_fake("nop")
            qualified = w.qualify_attempt(self.root, "study", diagnostic["attempt_id"])
            review = c.review(
                self.root,
                "study",
                "usable",
                "Exact controls",
                "Diagnostic condition",
                [],
                "assistant",
                eligible_attempts=[qualified],
            )
            self.assertEqual(review["eligible_attempts"][0]["attempt_id"], diagnostic["attempt_id"])
            normal = self.run_fake("codex", model="test/model")
            self.assertNotEqual(normal["attempt_id"], diagnostic["attempt_id"])
        self.assertTrue(c.lookup(self.root, diagnostic["attempt_id"])["diagnostic"])

    def test_interruption_and_batch_collection_keep_attempt_identity(self):
        def interrupted(argv, **kwargs):
            self.fake_harbor(argv, **kwargs)
            raise KeyboardInterrupt()

        with (
            patch.object(w, "harbor_checksum", return_value="a" * 64),
            patch.object(w.subprocess, "run", side_effect=interrupted),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_fake()
        attempt = next(r for r in c.load(self.root).values() if r["kind"] == "attempt")
        self.assertEqual(
            c.projection(self.root)[attempt["id"]]["current"]["execution_state"], "interrupted"
        )
        managed = str(Path(attempt["execution_path"]).parent / "job/trial/result.json")
        c.write_new(self.root / ".local/independent/trial/result.json", c.read(self.root / managed))
        first, second = w.collect(
            self.root, "study", [managed, ".local/independent/trial/result.json"]
        )
        self.assertEqual(first["attempt_id"], attempt["id"])
        self.assertNotEqual(first["attempt_id"], second["attempt_id"])
        self.assertTrue(first["freeze_checksum_verified"])
        self.assertFalse(second["freeze_checksum_verified"])

    def test_partial_collect_preserves_terminal_launcher_state(self):
        def interrupted(argv, **kwargs):
            self.fake_harbor(argv, **kwargs)
            path = Path(argv[-1]).parent / "job/trial/result.json"
            payload = c.read(path)
            payload["finished_at"] = None
            c.atomic_write(path, payload)
            raise KeyboardInterrupt()

        with (
            patch.object(w, "harbor_checksum", return_value="a" * 64),
            patch.object(w.subprocess, "run", side_effect=interrupted),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_fake()
        attempt = next(r for r in c.load(self.root).values() if r["kind"] == "attempt")
        path = Path(attempt["execution_path"]).parent / "job/trial/result.json"
        result = w.collect(self.root, "study", [str(path)])[0]
        self.assertTrue(result["partial"])
        self.assertEqual(result["outcome"], "no_verdict")
        self.assertEqual(
            c.projection(self.root)[attempt["id"]]["current"]["execution_state"], "interrupted"
        )

    def test_collection_during_run_appends_binding_without_new_attempt(self):
        early = []

        def collect_running(argv, **kwargs):
            result = self.fake_harbor(argv, **kwargs)
            source = str((Path(argv[-1]).parent / "job/trial/result.json").relative_to(self.root))
            early.extend(w.collect(self.root, "study", [source]))
            return result

        with (
            patch.object(w, "harbor_checksum", return_value="a" * 64),
            patch.object(w.subprocess, "run", side_effect=collect_running),
        ):
            receipt = self.run_fake()
        final = c.lookup(self.root, receipt["collected"][0])
        self.assertFalse(early[0]["freeze_checksum_verified"])
        self.assertTrue(final["freeze_checksum_verified"])
        self.assertNotEqual(early[0]["id"], final["id"])
        self.assertEqual(early[0]["attempt_id"], final["attempt_id"])

    def test_partial_collection_appends_and_scrubs_secrets(self):
        source = ".local/job/trial/result.json"
        trial = {
            "task_name": "demo",
            "trial_name": "trial",
            "config": {"agent": {"name": "oracle", "env": {"SECRET": "never-retain"}}},
            "finished_at": None,
        }
        c.write_new(self.root / source, trial)
        first = w.collect(self.root, "study", [source])[0]
        self.assertTrue(first["partial"])
        self.assertNotIn("never-retain", json.dumps(first))
        trial["finished_at"] = "2026-09-20T10:00:00Z"
        c.atomic_write(self.root / source, trial)
        second = w.collect(self.root, "study", [source])[0]
        self.assertEqual(first["attempt_id"], second["attempt_id"])
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(w.collect(self.root, "study", [source])[0]["id"], second["id"])

    def test_selected_freeze_detects_change_and_restores_missing_snapshot(self):
        import shutil

        frozen = w.freeze(self.root, "study")
        shutil.rmtree(self.root / frozen["snapshot_path"])
        snapshot = w.restore_freeze(self.root, frozen)
        self.assertEqual(w.task_files(snapshot), frozen["files"])
        (snapshot / "instruction.md").write_text("Changed task")
        with self.assertRaises(c.MedicalError):
            w.restore_freeze(self.root, frozen)

    def test_freeze_rejects_added_public_files_without_rewriting_snapshot(self):
        frozen = w.freeze(self.root, "study")
        snapshot = self.root / frozen["snapshot_path"]
        before = w.task_files(snapshot)
        (snapshot / "patient-hint.txt").write_text("Unexpected extra solver input")
        with self.assertRaises(c.MedicalError):
            w.restore_freeze(self.root, frozen)
        self.assertEqual(frozen["files"], before)
        self.assertTrue((snapshot / "patient-hint.txt").exists())

    def test_export_uses_commit_bytes_compact_recipe_and_explicit_flagged_draft(self):
        self.enterContext(
            patch.dict(
                os.environ,
                {key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
                clear=True,
            )
        )
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "add", "proof.txt"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.test",
                "commit",
                "-qm",
                "fixture",
            ],
            cwd=self.root,
            check=True,
        )
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.root, text=True
        ).strip()
        recipe = {
            "schema_version": 2,
            "mode": "exact",
            "source_commit": commit,
            "experiment_ids": ["study"],
            "submission_status": "draft",
            "target_profile": "research",
            "remaining_gates": ["TB3 review"],
            "files": [
                {
                    "origin": "git",
                    "source": "proof.txt",
                    "destination": "proof.txt",
                    "sha256": c.sha(self.root / "proof.txt"),
                }
            ],
        }
        (self.root / "recipe.json").write_text(json.dumps(recipe, separators=(",", ":")))
        (self.root / "proof.txt").write_text("Working tree differs")
        c.issue(self.root, ["study"], "Needs review", [], "assistant")
        with self.assertRaises(c.MedicalError):
            packaging.export(self.root, "recipe.json", self.root / "package")
        packaging.export(self.root, "recipe.json", self.root / "package", include_flagged=True)
        self.assertEqual((self.root / "package/proof.txt").read_text(), "review proof")
        self.assertEqual(packaging.verify(self.root / "package")["verified_files"], 1)
        self.assertEqual(
            c.read(self.root / "package/manifest.json")["review_flags"]["study"]["assessment"],
            "needs_review",
        )
        (self.root / "package/extra").write_text("oops")
        with self.assertRaisesRegex(c.MedicalError, "inventory"):
            packaging.verify(self.root / "package")
        recipe["files"][0]["source"] = "not-in-commit"
        c.atomic_write(self.root / "missing.json", recipe)
        with self.assertRaises(subprocess.CalledProcessError):
            packaging.export(self.root, "missing.json", self.root / "missing", include_flagged=True)
        self.assertFalse((self.root / "missing").exists())

    def test_portable_rebuild_removes_local_media(self):
        (self.root / "presentation/tours/data").mkdir(parents=True)
        for name in ("index.html", "app.js", "style.css"):
            (self.root / "presentation" / name).write_text("fixture")
        (self.root / "presentation/tours/data/native-local.bin").write_bytes(b"local")
        (self.root / "groups/g/presentation").mkdir()
        (self.root / "groups/g/presentation/story.md").write_text("# Group")
        out = self.root / ".local/site"
        presentation.present(self.root, out, True)
        self.assertTrue((out / "presentation/tours/data/native-local.bin").exists())
        presentation.present(self.root, out, False)
        self.assertFalse((out / "presentation/tours/data/native-local.bin").exists())


if __name__ == "__main__":
    unittest.main()
