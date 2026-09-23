"""Review-aware execution, concurrent ownership and portable export regressions.

All workspaces are temporary; launchers and Harbor checksums are mocked.
"""

import io
import json
import os
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import patch

from tb3_medical import cli, packaging
from tb3_medical import core as c
from tb3_medical import workflow as w


class WorkflowRefinementTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "workbench.toml").write_text("version=1\n")
        c.write_new(
            self.root / "groups/g/group.json",
            {"schema_version": 2, "kind": "group", "id": "g", "title": "Group"},
        )
        w.new(self.root, "g", "study", "Study")
        w.new(self.root, "g", "other", "Other study")
        # Identical payloads permit deliberate cross-experiment control reuse.
        for name in ("study", "other"):
            (self.root / f"groups/g/experiments/{name}/task/instruction.md").write_text("Task\n")
        self.enterContext(patch.object(w, "harbor_checksum", return_value="a" * 64))
        self.enterContext(patch.object(w.subprocess, "run", side_effect=self.fake_harbor))

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

    def run_fake(self, agent="oracle", experiment="study", **kwargs):
        if agent == "codex":
            kwargs.setdefault("model", "test/model")
        return w.run(self.root, experiment, agent, "fake-harbor", **kwargs)

    def controls(self, experiment="study"):
        oracle = self.run_fake("oracle", experiment)
        nop = self.run_fake("nop", experiment)
        return c.lookup(self.root, oracle["collected"][0]), c.lookup(self.root, nop["collected"][0])

    def append_observation(self, original, **updates):
        row = {k: v for k, v in original.items() if k != "record_path"}
        row.update(id=c.uid("observation"), collected_at=c.now(), **updates)
        base = self.root / f"groups/g/experiments/{row['experiment_id']}/evaluations"
        c.write_new(base / (row["id"] + ".json"), row)
        return row

    def review(self, assessment="usable", resolves=(), **kwargs):
        return c.review(
            self.root,
            "study",
            assessment,
            "Scoped control assessment",
            "Exact task and saved outputs",
            [],
            "assistant",
            resolves,
            **kwargs,
        )

    def invoke(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            status = cli.main(["--root", str(self.root), *args])
        return status, output.getvalue(), error.getvalue()

    def test_agent_environment_reaches_harbor_without_entering_public_records(self):
        env = {
            "CODEX_FORCE_AUTH_JSON": "1",
            "HTTPS_PROXY": "http://runtime-proxy.invalid:10808",
            "OPENAI_API_KEY": "fixture-secret-never-publish",
        }
        source = self.root / ".local/runtime/agent-env.json"
        c.write_new(source, env)
        args = (
            "run",
            "study",
            "--model",
            "test/model",
            "--effort",
            "medium",
            "--diagnostic",
            "--agent-env-file",
            str(source.relative_to(self.root)),
        )
        status, output, error = self.invoke(*args, "--preview")
        self.assertEqual((status, error), (0, ""))
        self.assertEqual(json.loads(output)["agent_env_keys"], sorted(env))
        self.assertNotIn(env["OPENAI_API_KEY"], output)
        self.assertFalse((self.root / ".local/attempts").exists())
        status, output, error = self.invoke(*args)
        self.assertEqual((status, error), (0, ""))
        receipt = json.loads(output)
        attempt = c.lookup(self.root, receipt["attempt_id"])
        config_path = (self.root / attempt["execution_path"]).parent / "config.json"
        config = c.read(config_path)
        self.assertEqual(config["agents"][0]["env"], env)
        self.assertEqual(config["agents"][0]["kwargs"], {"reasoning_effort": "medium"})
        self.assertEqual(config_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(config_path.parent.stat().st_mode & 0o777, 0o700)
        public = output + json.dumps(c.load(self.root))
        self.assertNotIn(env["OPENAI_API_KEY"], public)
        self.assertNotIn(env["HTTPS_PROXY"], public)

    def test_invalid_agent_environment_fails_before_creating_an_attempt(self):
        source = self.root / "agent-env.json"
        for payload in (
            "[]",
            '{"CODEX_FORCE_AUTH_JSON":true}',
            '{"bad=name":"secret"}',
            '{"KEY":"\\u0000"}',
            "{invalid",
        ):
            with self.subTest(payload=payload):
                source.write_text(payload)
                with self.assertRaises(c.MedicalError):
                    self.run_fake("codex", diagnostic=True, agent_env_file=source)
                self.assertFalse((self.root / ".local/attempts").exists())
                self.assertFalse((self.root / "groups/g/experiments/study/freezes").exists())
        source.unlink()
        with self.assertRaises(c.MedicalError):
            self.run_fake("codex", diagnostic=True, agent_env_file=source)

    def test_agent_environment_does_not_copy_ambient_secrets(self):
        with patch.dict(os.environ, {"UNRELATED_SECRET": "never-copy"}):
            receipt = self.run_fake("codex", diagnostic=True)
        attempt = c.lookup(self.root, receipt["attempt_id"])
        config = c.read((self.root / attempt["execution_path"]).parent / "config.json")
        self.assertEqual(config["agents"][0]["env"], {})

    def test_questioned_control_owner_blocks_reuse_and_diagnostic_remains_explicit(self):
        oracle, _ = self.controls()
        self.assertEqual(c.projection(self.root)["study"]["current"]["assessment"], "not_assessed")
        self.run_fake("codex", "other")
        issue = c.issue(self.root, [oracle["attempt_id"]], "Oracle defect", [], "assistant")
        with self.assertRaisesRegex(c.MedicalError, "unresolved review flags"):
            self.run_fake("codex", "other")
        self.run_fake("codex", "other", diagnostic=True)
        # A usable review without an explicit issue resolution is insufficient.
        self.review()
        with self.assertRaises(c.MedicalError):
            self.run_fake("codex", "other")
        self.review(resolves=[issue["id"]])
        self.run_fake("codex", "other")

    def test_invalidated_controls_need_usable_reassessment_or_other_owner(self):
        self.controls()
        self.review("invalidated")
        with self.assertRaises(c.MedicalError):
            self.run_fake("codex", "other")
        self.controls("other")
        self.run_fake("codex", "other")
        # Target assessment remains an independent gate, even with other controls.
        with self.assertRaisesRegex(c.MedicalError, "experiment issue"):
            self.run_fake("codex", "study")
        self.review()
        self.run_fake("codex", "study")

    def test_neutral_review_cannot_reset_an_issue_or_invalidation_before_usable_reassessment(self):
        oracle, _ = self.controls()
        self.review("not_assessed")
        w.check_controls(self.root, oracle["task_digest"])
        issue = c.issue(self.root, [oracle["attempt_id"]], "Oracle defect", [], "assistant")
        before = c.load(self.root)
        with self.assertRaisesRegex(c.MedicalError, "cannot be reset"):
            self.review("not_assessed", resolves=[issue["id"]])
        self.assertEqual(before, c.load(self.root))
        self.review("invalidated", resolves=[issue["id"]])
        before = c.load(self.root)
        with self.assertRaisesRegex(c.MedicalError, "usable scoped reassessment"):
            self.review("not_assessed")
        self.assertEqual(before, c.load(self.root))
        with self.assertRaises(c.MedicalError):
            self.run_fake("codex", "other")
        self.review()
        self.review("not_assessed")
        self.run_fake("codex", "other")

    def test_blocked_control_error_names_relevant_attempt_owner_and_reason(self):
        oracle, nop = self.controls()
        model = self.run_fake("codex", diagnostic=True)
        other_oracle, _ = self.controls("other")
        self.append_observation(other_oracle, task_digest="different-task")
        c.issue(self.root, ["study"], "Oracle scope needs review", [], "assistant")
        c.issue(self.root, ["other"], "Unrelated other task concern", [], "assistant")
        # Remove other no-op from this task's candidate stream as well.
        for row in c.execution_observations(c.load(self.root)).values():
            if row["experiment_id"] == "other" and row.get("agent") == "nop":
                self.append_observation(row, task_digest="different-task")
        with self.assertRaises(c.MedicalError) as caught:
            w.check_controls(self.root, oracle["task_digest"])
        message = str(caught.exception)
        self.assertIn(f"{oracle['attempt_id']} (owner study, needs_review)", message)
        self.assertIn(nop["attempt_id"], message)
        self.assertIn("Oracle scope needs review", message)
        self.assertNotIn(model["attempt_id"], message)
        self.assertNotIn(other_oracle["attempt_id"], message)
        self.assertNotIn("Unrelated other task concern", message)

    def test_latest_control_observation_precedes_outcome_binding_and_completion_filters(self):
        oracle, _ = self.controls()
        for change in (
            {"outcome": "fail"},
            {"partial": True},
            {"execution_state": "error", "outcome": "no_verdict"},
            {"execution_state": "running", "outcome": "no_verdict"},
            {"task_digest": None, "freeze_checksum_verified": False},
            {"task_digest": "different-task"},
        ):
            with self.subTest(change=change):
                self.append_observation(oracle, **change)
                with self.assertRaises(c.MedicalError):
                    w.check_controls(self.root, oracle["task_digest"])
                self.append_observation(oracle)
                w.check_controls(self.root, oracle["task_digest"])

    def test_unbound_launcher_receipt_supersedes_prior_pass(self):
        oracle, _ = self.controls()
        self.append_observation(
            oracle,
            evaluation_kind="execution",
            execution_state="error",
            outcome="no_verdict",
            task_digest=None,
            freeze_checksum_verified=False,
        )
        with self.assertRaises(c.MedicalError):
            w.check_controls(self.root, oracle["task_digest"])

    def test_replay_trace_comparative_and_legacy_saved_reviews_do_not_replace_execution(self):
        oracle, _ = self.controls()
        for kind in (
            "saved_output_replay",
            "retained_saved_output_replay",
            "posthoc_trace_review",
            "comparison",
        ):
            self.append_observation(oracle, evaluation_kind=kind, outcome="fail")
        self.append_observation(oracle, experiment_id="other", outcome="fail")
        self.append_observation(
            oracle,
            evaluation_kind=None,
            source_result=None,
            evidence_sha256=None,
            outcome="fail",
        )
        w.check_controls(self.root, oracle["task_digest"])
        state = c.projection(self.root)[oracle["attempt_id"]]["current"]
        self.assertEqual(state["outcome"], "pass")

    def test_legacy_harbor_results_and_launcher_receipts_keep_execution_semantics(self):
        oracle, _ = self.controls()
        self.append_observation(oracle, evaluation_kind=None)
        w.check_controls(self.root, oracle["task_digest"])
        attempt = c.lookup(self.root, oracle["attempt_id"])
        self.append_observation(
            oracle,
            evaluation_kind=None,
            source_result=None,
            evidence_sha256=None,
            execution_state="error",
            outcome="no_verdict",
            evidence=[c.evidence(self.root, attempt["execution_path"])],
        )
        with self.assertRaises(c.MedicalError):
            w.check_controls(self.root, oracle["task_digest"])

    def test_recollection_verifies_new_evidence_without_hashing_superseded_source(self):
        oracle, _ = self.controls()
        path = self.root / oracle["source_result"]
        payload = c.read(path)
        payload["retained_metadata"] = "new detail"
        c.atomic_write(path, payload)
        recollected = w.collect(self.root, "study", [oracle["source_result"]])[0]
        self.assertNotEqual(oracle["id"], recollected["id"])
        with self.assertRaisesRegex(c.MedicalError, "Changed input"):
            c.verify_inputs(self.root, oracle["evidence"])
        w.check_controls(self.root, oracle["task_digest"])

    def test_changed_candidate_does_not_veto_another_valid_attempt(self):
        oracle, _ = self.controls()
        self.run_fake("oracle")
        (self.root / oracle["source_result"]).write_text("Changed raw result")
        w.check_controls(self.root, oracle["task_digest"])
        # The remaining stale candidate still cannot authorize reuse on its own.
        latest = c.execution_observations(c.load(self.root))
        replacement = next(
            r for r in latest.values() if r.get("agent") == "oracle" and r["id"] != oracle["id"]
        )
        (self.root / replacement["source_result"]).unlink()
        with self.assertRaisesRegex(c.MedicalError, "Unavailable evidence"):
            w.check_controls(self.root, oracle["task_digest"])

    def test_a_b_a_recollection_appends_restored_observation_then_deduplicates(self):
        oracle, _ = self.controls()
        path = self.root / oracle["source_result"]
        original_bytes = path.read_bytes()
        payload = c.read(path)
        payload["verifier_result"]["rewards"]["reward"] = 0
        c.atomic_write(path, payload)
        middle = w.collect(self.root, "study", [oracle["source_result"]])[0]
        with self.assertRaises(c.MedicalError):
            w.check_controls(self.root, oracle["task_digest"])
        path.write_bytes(original_bytes)
        restored = w.collect(self.root, "study", [oracle["source_result"]])[0]
        self.assertEqual(len({oracle["id"], middle["id"], restored["id"]}), 3)
        self.assertEqual(restored["attempt_id"], oracle["attempt_id"])
        self.assertEqual(
            w.collect(self.root, "study", [oracle["source_result"]])[0]["id"], restored["id"]
        )
        w.check_controls(self.root, oracle["task_digest"])

    def test_qualification_uses_latest_execution_and_accepts_completed_scoring_failure(self):
        self.controls()
        result = self.run_fake("codex", diagnostic=True)
        original = c.lookup(self.root, result["collected"][0])
        qualified = w.qualify_attempt(self.root, "study", result["attempt_id"])
        self.assertEqual(qualified["observation_id"], original["id"])
        self.assertEqual(original["outcome"], "fail")
        for change in (
            {"partial": True},
            {"execution_state": "error"},
            {"freeze_checksum_verified": False},
            {"task_digest": "another-task"},
        ):
            with self.subTest(change=change):
                self.append_observation(original, **change)
                with self.assertRaisesRegex(c.MedicalError, "normally completed"):
                    w.qualify_attempt(self.root, "study", result["attempt_id"])
                restored = self.append_observation(original)
                self.append_observation(
                    original, evaluation_kind="saved_output_replay", outcome="pass"
                )
                self.assertEqual(
                    w.qualify_attempt(self.root, "study", result["attempt_id"])["observation_id"],
                    restored["id"],
                )

    def test_combined_resolution_and_qualification_checks_prospective_review_before_publish(self):
        self.controls()
        result = self.run_fake("codex", diagnostic=True)
        issue = c.issue(self.root, ["study"], "Check exact control scope", [], "assistant")
        with self.assertRaises(c.MedicalError):
            w.qualify_attempt(self.root, "study", result["attempt_id"])
        status, output, error = self.invoke(
            "review",
            "study",
            "usable",
            "--reason",
            "Scope checked",
            "--scope",
            "Exact task",
            "--resolves",
            issue["id"],
            "--qualify-attempt",
            result["attempt_id"],
        )
        self.assertEqual(status, 0, error)
        event = json.loads(output)
        self.assertEqual(event["eligible_attempts"][0]["attempt_id"], result["attempt_id"])
        self.assertEqual(c.projection(self.root)["study"]["current"]["assessment"], "usable")

    def test_failed_combined_review_does_not_publish_or_resolve_any_issue(self):
        self.controls()
        result = self.run_fake("codex", diagnostic=True)
        issue = c.issue(self.root, ["study"], "Scope still disputed", [], "assistant")
        original = c.lookup(self.root, result["collected"][0])
        self.append_observation(original, freeze_checksum_verified=False)
        before = c.load(self.root)
        status, _, error = self.invoke(
            "review",
            "study",
            "usable",
            "--reason",
            "Proposed review",
            "--scope",
            "Exact task",
            "--resolves",
            issue["id"],
            "--qualify-attempt",
            result["attempt_id"],
        )
        self.assertEqual(status, 1)
        self.assertIn("normally completed", error)
        self.assertEqual(before, c.load(self.root))
        self.assertEqual(c.projection(self.root)["study"]["current"]["issue_ids"], [issue["id"]])

    def test_remaining_issue_and_nonusable_review_cannot_qualify(self):
        self.controls()
        result = self.run_fake("codex", diagnostic=True)
        first = c.issue(self.root, ["study"], "First scope issue", [], "assistant")
        second = c.issue(self.root, ["study"], "Second scope issue", [], "assistant")
        for assessment, resolves in (
            ("usable", [first["id"]]),
            ("invalidated", [first["id"], second["id"]]),
        ):
            with self.subTest(assessment=assessment):
                before = c.load(self.root)
                with self.assertRaises(c.MedicalError):
                    self.review(assessment, resolves, qualify_attempts=[result["attempt_id"]])
                self.assertEqual(before, c.load(self.root))

    def test_launcher_failure_returns_nonzero_with_retained_receipt(self):
        with patch.object(w.subprocess, "run", return_value=subprocess.CompletedProcess([], 17)):
            status, output, _ = self.invoke(
                "run", "study", "--agent", "oracle", "--harbor", "fake-harbor"
            )
        receipt = json.loads(output)
        self.assertEqual(status, 1)
        self.assertEqual(receipt["exit_code"], 17)
        self.assertEqual(receipt["execution_state"], "error")
        attempt = c.lookup(self.root, receipt["attempt_id"])
        self.assertEqual(c.read(self.root / attempt["execution_path"])["exit_code"], 17)

    def test_completed_scoring_failure_returns_zero_and_preview_does_not_launch(self):
        status, output, error = self.invoke(
            "run", "study", "--agent", "codex", "--model", "test/model", "--diagnostic"
        )
        self.assertEqual(status, 0, error)
        receipt = json.loads(output)
        self.assertEqual(c.lookup(self.root, receipt["collected"][0])["outcome"], "fail")
        with patch.object(w.subprocess, "run", side_effect=AssertionError("Preview launched")):
            status, output, error = self.invoke("run", "study", "--agent", "oracle", "--preview")
        self.assertEqual(status, 0, error)
        self.assertFalse(json.loads(output)["executes"])

    def test_concurrent_new_derives_membership_without_writing_group_and_preserves_dependencies(
        self,
    ):
        path = self.root / "groups/g/group.json"
        group_bytes = path.read_bytes()
        barrier = Barrier(2)

        def create(key):
            barrier.wait()
            return w.new(self.root, "g", key, key)

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(create, ("one", "two")))
        self.assertEqual(path.read_bytes(), group_bytes)
        self.assertEqual(
            c.projection(self.root)["g"]["experiment_ids"], ["one", "other", "study", "two"]
        )
        self.assertEqual(c.validate(self.root)["experiments"], 4)
        c.write_new(
            self.root / "groups/g/findings/f.json",
            {
                "schema_version": 2,
                "kind": "finding",
                "id": "f",
                "group_id": "g",
                "claim": "Study only",
                "experiment_ids": ["study"],
            },
        )
        c.write_new(
            self.root / "exports/records/e.json",
            {
                "schema_version": 2,
                "kind": "export",
                "id": "e",
                "experiment_ids": ["study"],
                "submission_status": "draft",
            },
        )
        c.issue(self.root, ["two"], "New experiment needs review", [], "assistant")
        rows = c.projection(self.root)
        self.assertTrue(rows["g"]["current"]["attention"])
        self.assertFalse(rows["f"]["current"]["attention"])
        self.assertFalse(rows["e"]["current"]["attention"])
        self.assertEqual(c.experiment_ids(rows["g"], rows), rows["g"]["experiment_ids"])


class ExportModeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "script.sh").write_text("#!/bin/sh\nexit 0\n")
        recipe = {
            "schema_version": 2,
            "files": [
                {
                    "destination": "script.sh",
                    "sha256": c.sha(self.root / "script.sh"),
                    "mode": 0o755,
                }
            ],
            "source_commit": "a" * 40,
            "submission_status": "draft",
            "remaining_gates": [],
            "mode": "exact",
            "target_profile": "research",
            "experiment_ids": [],
        }
        c.write_new(self.root / "recipe.json", recipe)
        c.write_new(
            self.root / "manifest.json",
            {**recipe, "recipe_sha256": c.sha(self.root / "recipe.json"), "changes": []},
        )

    @unittest.skipUnless(os.name == "posix", "POSIX executable bits")
    def test_verification_detects_changed_execute_bits_but_allows_read_write_permissions(self):
        path = self.root / "script.sh"
        path.chmod(0o755)
        self.assertEqual(packaging.verify(self.root)["executable_modes"], "verified (POSIX)")
        path.chmod(0o711)
        packaging.verify(self.root)
        for mode in (0o644, 0o744, 0o754):
            path.chmod(mode)
            with (
                self.subTest(mode=oct(mode)),
                self.assertRaisesRegex(c.MedicalError, "executable mode"),
            ):
                packaging.verify(self.root)

    @unittest.skipUnless(os.name == "posix", "POSIX executable bits")
    def test_default_nonexecutable_contract_detects_added_execute_bits(self):
        recipe = c.read(self.root / "recipe.json")
        recipe["files"][0].pop("mode")
        c.atomic_write(self.root / "recipe.json", recipe)
        c.atomic_write(
            self.root / "manifest.json",
            {**recipe, "recipe_sha256": c.sha(self.root / "recipe.json"), "changes": []},
        )
        (self.root / "script.sh").chmod(0o755)
        with self.assertRaisesRegex(c.MedicalError, "executable mode"):
            packaging.verify(self.root)

    def test_nonposix_does_not_claim_to_verify_executable_bits(self):
        with patch.object(packaging, "os", SimpleNamespace(name="nt")):
            result = packaging.verify(self.root)
        self.assertEqual(result["executable_modes"], "not checked (non-POSIX)")
        self.assertEqual(result["verified_files"], 1)


if __name__ == "__main__":
    unittest.main()
