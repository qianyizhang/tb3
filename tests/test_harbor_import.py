"""Evidence-boundary tests using synthetic Harbor runs, never real credentials."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tb3_medical import harbor as core


PHASE = {
    "started_at": "2026-09-12T00:00:00Z",
    "finished_at": "2026-09-12T00:00:01Z",
}
TASK_CHECKSUM = "a" * 64
DEFAULT = object()


class HarborImportTests(unittest.TestCase):
    def imported(self, source):
        return core.import_trial(self.root, source)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tb3-catalog-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "workspace"
        self.runs = self.root / "runs"
        self.runs.mkdir(parents=True)

    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def fixture(self, name="trial", *, job=None, reward=0, agent="codex",
                cases=DEFAULT, artifact=DEFAULT, checksum=TASK_CHECKSUM,
                overrides=None):
        """Return an individual result, with no dependency on a real run tree."""
        source = self.runs / (job or name) / name / "result.json"
        result = {
            **PHASE,
            "task_name": "probe",
            "trial_name": name,
            "task_checksum": checksum,
            "config": {
                "agent": {
                    "name": agent,
                    "model_name": "openai/test-model",
                    "kwargs": {"reasoning_effort": "high"},
                },
                "environment": {"type": "docker"},
            },
            "agent_info": {"name": agent, "version": "0.1.0"},
            "agent_setup": copy.deepcopy(PHASE),
            "agent_execution": copy.deepcopy(PHASE),
            "verifier": copy.deepcopy(PHASE),
            "verifier_result": {"rewards": {"reward": reward}},
            "agent_result": {"n_input_tokens": 23, "n_cache_tokens": 7, "n_output_tokens": 11},
            "exception_info": None,
        }
        result.update(overrides or {})
        self.write_json(source, result)
        self.write_json(source.parent.parent / "lock.json", {"harbor": {"version": "0.14.0"}})
        if cases is DEFAULT:
            cases = {"passed": ["baseline"], "failures": []} if reward == 1 else {
                "passed": ["baseline"], "failures": ["nested-case: observed result differs"]
            }
        stdout = source.parent / "verifier" / "test-stdout.txt"
        stdout.parent.mkdir(parents=True, exist_ok=True)
        if cases is not None:
            stdout.write_text(cases if isinstance(cases, str) else json.dumps(cases), encoding="utf-8")
        if artifact is DEFAULT:
            artifact = str(reward)
        if artifact is not None:
            (stdout.parent / "reward.txt").write_text(str(artifact), encoding="utf-8")
        return source

    def test_model_and_control_outcomes_are_distinct(self):
        for name, agent, reward, expected in (
            ("pass", "codex", 1, "model_pass"),
            ("candidate", "codex", 0, "model_failure_candidate"),
            ("oracle-pass", "oracle", 1, "control_pass"),
            ("oracle-fail", "oracle", 0, "control_fail"),
            ("nop-fail", "nop", 0, "control_fail"),
        ):
            with self.subTest(name=name):
                row = core.import_trial(self.root, self.fixture(name, agent=agent, reward=reward))
                self.assertEqual(row["classification"], expected)
                self.assertFalse(row["qualifying_final_trial"])
                self.assertEqual(row["harbor_version"], "0.14.0")

    def test_execution_error_and_incomplete_take_precedence_over_contradictions(self):
        for name, overrides, expected in (
            ("error", {"exception_info": {"exception_type": "AgentTimeoutError"}}, "execution_error"),
            ("incomplete", {"finished_at": None}, "incomplete"),
        ):
            with self.subTest(name=name):
                source = self.fixture(name, reward=1, artifact=0,
                                      cases={"passed": [], "failures": ["case: mismatch"]},
                                      overrides=overrides)
                self.assertEqual(core.import_trial(self.root, source)["classification"], expected)

    def test_disabled_multistep_and_missing_execution_are_not_model_outcomes(self):
        base_config = {"agent": {"name": "codex"}, "verifier": {"disable": True}}
        for name, overrides in (
            ("disabled", {"config": base_config}),
            ("multistep", {"step_results": [{"reward": 1}]}),
            ("no-agent-end", {"agent_execution": {"started_at": PHASE["started_at"]}}),
            ("no-verifier-end", {"verifier": {"started_at": PHASE["started_at"]}}),
            ("invalid-agent", {"config": {"agent": {"name": {"unexpected": "object"}}}}),
        ):
            with self.subTest(name=name):
                row = core.import_trial(self.root, self.fixture(name, reward=1, overrides=overrides))
                self.assertEqual(row["classification"], "unknown")

    def test_nonbinary_nonfinite_and_boolean_rewards_are_unknown(self):
        for index, reward in enumerate((0.5, True, False, float("nan"), float("inf"), "1", None)):
            with self.subTest(reward=reward):
                source = self.fixture(f"reward-{index}", reward=reward, artifact=None)
                self.assertEqual(core.import_trial(self.root, source)["classification"], "unknown")

    def test_reward_artifact_disagreement_and_invalid_text_are_unknown(self):
        for index, artifact in enumerate((0, "invalid", "nan")):
            with self.subTest(artifact=artifact):
                row = core.import_trial(self.root, self.fixture(f"artifact-{index}", reward=1, artifact=artifact))
                self.assertEqual(row["classification"], "unknown")
                self.assertTrue(row["warnings"])

    def test_snapshot_checksum_never_falls_back_to_result_hash(self):
        for index, checksum in enumerate((None, "", "not-a-checksum", {"value": TASK_CHECKSUM}, True)):
            with self.subTest(checksum=checksum):
                row = self.imported(self.fixture(f"snapshot-{index}", checksum=checksum))
                self.assertIsNone(row["task_checksum"])
                self.assertIsNone(row["task_sha256"])
                self.assertEqual(len(row["source_sha256"]), 64)
                self.assertTrue(row["warnings"])
                self.assertFalse(row["qualifying_final_trial"])

    def test_opaque_task_checksum_is_kept_distinct_from_source_and_evidence_hashes(self):
        source = self.fixture()
        row = core.import_trial(self.root, source)
        self.assertEqual(row["task_checksum"], TASK_CHECKSUM)
        self.assertEqual(row["checksum_kind"], "harbor.task_checksum")
        self.assertIsNone(row["task_sha256"])
        self.assertNotEqual(row["task_checksum"], row["source_sha256"])
        self.assertNotEqual(row["task_checksum"], row["evidence_sha256"])

    def test_private_config_environment_trajectory_and_exception_text_are_not_exported(self):
        canary = "PRIVATE_CANARY_NEVER_EXPORT"
        source = self.fixture(overrides={
            "config": {
                "agent": {"name": "codex", "model_name": "openai/test", "kwargs": {
                    "reasoning_effort": "high", "api_key": canary, "instructions": canary,
                }},
                "environment": {"type": "docker", "env": {"AUTH_TOKEN": canary}},
                "auth": canary,
            },
            "exception_info": {"exception_type": "SetupError", "exception_message": canary, "traceback": canary},
            "agent_result": {"n_input_tokens": 1, "metadata": {"secret": canary}},
        })
        self.write_json(source.parent / "agent" / "trajectory.json", {"messages": [{"content": canary}]})
        self.write_json(source.parent.parent / "lock.json", {"harbor": {"version": "0.14.0"}, "env": canary})
        row = core.import_trial(self.root, source)
        self.assertNotIn(canary, json.dumps(row))
        self.assertEqual(row["exception_type"], "SetupError")
        self.assertTrue(any(item["path"].endswith("trajectory.json") for item in row["evidence"]))

    def test_raw_verifier_details_and_free_text_metadata_are_not_exported(self):
        canary = "PRIVATE_DETAIL_CANARY"
        source = self.fixture(cases={"passed": ["baseline"], "failures": [
            f"case-a: Authorization: Bearer {canary}",
            {"name": "case-b", "error": {"traceback": canary}},
        ]}, overrides={
            "config": {
                "agent": {"name": "codex", "model_name": {"secret": canary},
                          "kwargs": {"reasoning_effort": f"free text {canary}"}},
                "environment": {"type": {"secret": canary}},
            },
            "agent_info": {"version": f"version details {canary}"},
        })
        row = core.import_trial(self.root, source)
        self.assertNotIn(canary, json.dumps(row))
        self.assertEqual({case["name"] for case in row["cases"]}, {"baseline", "case-a", "case-b"})
        self.assertTrue(all(not case.get("detail") for case in row["cases"]))

    def test_case_parser_supports_one_json_summary_inside_log_output(self):
        source = self.fixture(cases='setup log\n{"passed":["clean"],"failures":["edge: mismatch"]}\nteardown\n')
        row = core.import_trial(self.root, source)
        self.assertEqual([(case["name"], case["status"]) for case in row["cases"]],
                         [("clean", "passed"), ("edge", "failed")])

    def test_case_parser_does_not_merge_multiple_or_contradictory_summaries(self):
        for name, cases in (
            ("duplicate-case", {"passed": ["same"], "failures": ["same: mismatch"]}),
            ("multiple-reports", '{"passed":["a"],"failures":[]}\n{"passed":[],"failures":["b: mismatch"]}'),
            ("unsupported", '{"successful": 10, "failed": 0}'),
        ):
            with self.subTest(name=name):
                row = core.import_trial(self.root, self.fixture(name, cases=cases))
                self.assertEqual(row["cases"], [])
                self.assertTrue(row["warnings"])

    def test_artifact_symlink_escape_does_not_read_outside_workspace(self):
        source = self.fixture()
        outside = self.base / "outside.py"
        outside.write_text("print('outside')", encoding="utf-8")
        artifact = source.parent / "artifacts" / "app" / "solution.py"
        artifact.parent.mkdir(parents=True)
        artifact.symlink_to(outside)
        with self.assertRaises(core.CatalogError):
            core.import_trial(self.root, source)

    def test_source_and_stdout_changes_during_import_are_rejected(self):
        original_parser = core.parse_cases
        for name, target in (("result-race", "result"), ("stdout-race", "stdout")):
            with self.subTest(target=target):
                source = self.fixture(name)

                def change_after_parse(stdout):
                    parsed = original_parser(stdout)
                    changed = source if target == "result" else stdout
                    changed.write_text(changed.read_text(encoding="utf-8") + "\n", encoding="utf-8")
                    return parsed

                with patch.object(core, "parse_cases", side_effect=change_after_parse):
                    with self.assertRaises(core.CatalogError):
                        core.import_trial(self.root, source)
