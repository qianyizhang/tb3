"""Evidence-boundary tests using synthetic Harbor runs, never real credentials."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from tb3_medical import core as records
from tb3_medical import harbor as core
from tb3_medical import workflow

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

    def fixture(
        self,
        name="trial",
        *,
        job=None,
        reward=0,
        agent="codex",
        cases=DEFAULT,
        artifact=DEFAULT,
        checksum=TASK_CHECKSUM,
        overrides=None,
    ):
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
            cases = (
                {"passed": ["baseline"], "failures": []}
                if reward == 1
                else {"passed": ["baseline"], "failures": ["nested-case: observed result differs"]}
            )
        stdout = source.parent / "verifier" / "test-stdout.txt"
        stdout.parent.mkdir(parents=True, exist_ok=True)
        if cases is not None:
            stdout.write_text(
                cases if isinstance(cases, str) else json.dumps(cases), encoding="utf-8"
            )
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
                self.assertIsInstance(row, core.ImportedTrial)
                self.assertEqual(row.classification, expected)
                self.assertFalse(row.qualifying_final_trial)
                self.assertEqual(row.harbor_version, "0.14.0")

    def test_import_and_collection_match_pre_refactor_baseline_without_raw_writes(self):
        baseline = json.loads(
            (Path(__file__).parent / "fixtures/harbor-import-baseline.json").read_text()
        )
        records.write_new(
            self.root / "groups/g/group.json",
            {"schema_version": 2, "kind": "group", "id": "g", "title": "Group"},
        )
        workflow.new(self.root, "g", "study", "Study")
        for scenario in baseline["scenarios"]:
            with self.subTest(name=scenario["name"]):
                source = self.fixture(scenario["name"], **scenario["inputs"])
                before = {
                    path: path.read_bytes() for path in self.runs.rglob("*") if path.is_file()
                }
                imported = core.import_trial(self.root, source)
                self.assertEqual(
                    json.dumps(imported.model_dump(mode="python"), sort_keys=True),
                    json.dumps(scenario["imported"], sort_keys=True),
                )
                state = workflow.result_state(imported)
                self.assertEqual([state.execution, state.outcome], scenario["state"])
                self.assertIn(
                    state.execution, records.VOCABULARY["axes"]["execution_state"]["values"]
                )
                self.assertIn(state.outcome, records.VOCABULARY["axes"]["outcome"]["values"])
                relative = str(source.relative_to(self.root))
                with patch.object(records, "now", return_value="2026-09-24T00:00:00Z"):
                    evaluation = workflow.collect(self.root, "study", [relative])[0]
                self.assertEqual(evaluation, scenario["evaluation"])
                persisted = (
                    self.root
                    / "groups/g/experiments/study/evaluations"
                    / (evaluation["id"] + ".json")
                )
                self.assertEqual(
                    persisted.read_text(),
                    json.dumps(scenario["evaluation"], indent=2, allow_nan=False) + "\n",
                )
                repeated = workflow.collect(self.root, "study", [relative])[0]
                self.assertEqual(repeated["id"], evaluation["id"])
                self.assertEqual(
                    {path: path.read_bytes() for path in self.runs.rglob("*") if path.is_file()},
                    before,
                )

    def test_resolved_state_preserves_terminal_partial_and_final_precedence(self):
        partial = self.imported(self.fixture("partial", overrides={"finished_at": None}))
        complete = self.imported(self.fixture("complete", reward=1))
        for terminal in ("interrupted", "error", "completed"):
            with self.subTest(terminal=terminal):
                state = workflow.resolve_observation_state(partial, terminal)
                self.assertEqual(state.execution, terminal)
                self.assertEqual(state.outcome, "no_verdict")
                self.assertTrue(state.partial)
                final = workflow.resolve_observation_state(complete, terminal)
                self.assertEqual(final.execution, "completed")
                self.assertEqual(final.outcome, "pass")
                self.assertFalse(final.partial)

    def test_binding_and_projection_preserve_source_and_wire_contract(self):
        trial = self.imported(self.fixture())
        before = trial.model_dump(mode="python")
        binding = workflow.CollectionBinding("attempt-test", "digest", TASK_CHECKSUM)
        verified = binding.verify(trial)
        self.assertEqual(verified.proof, "digest" + TASK_CHECKSUM)
        self.assertIsNone(
            workflow.CollectionBinding("attempt-test", "digest", "wrong").verify(trial)
        )
        self.assertIsNone(workflow.CollectionBinding("attempt-test").verify(trial))
        row = workflow.evaluation_from_trial(
            trial,
            observation_id="observation-test",
            attempt_id="attempt-test",
            experiment={"id": "study", "group_id": "g"},
            state=workflow.resolve_observation_state(trial),
            verified=verified,
            collected_at="fixed-time",
        )
        self.assertEqual(row["schema_version"], 2)
        self.assertEqual(row["source_classification"], trial.classification)
        self.assertNotIn("classification", row)
        self.assertNotIn("qualifying_final_trial", row)
        self.assertTrue(row["freeze_checksum_verified"])
        self.assertEqual(row["task_digest"], "digest")
        self.assertEqual(trial.model_dump(mode="python"), before)

    def test_normalized_contract_rejects_missing_extra_and_coerced_fields(self):
        expected = self.imported(self.fixture()).model_dump()
        invalid = []
        missing = copy.deepcopy(expected)
        del missing["source_sha256"]
        invalid.append(missing)
        invalid.append({**expected, "unexpected": "field"})
        invalid.append({**expected, "classification": "success"})
        invalid.append({**expected, "reward": "1"})
        invalid.append({**expected, "cases": [{"name": "a", "status": "pass", "detail": ""}]})
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                core.ImportedTrial.model_validate(value)

    def test_execution_error_and_incomplete_take_precedence_over_contradictions(self):
        for name, overrides, expected in (
            (
                "error",
                {"exception_info": {"exception_type": "AgentTimeoutError"}},
                "execution_error",
            ),
            ("incomplete", {"finished_at": None}, "incomplete"),
        ):
            with self.subTest(name=name):
                source = self.fixture(
                    name,
                    reward=1,
                    artifact=0,
                    cases={"passed": [], "failures": ["case: mismatch"]},
                    overrides=overrides,
                )
                self.assertEqual(core.import_trial(self.root, source).classification, expected)

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
                row = core.import_trial(
                    self.root, self.fixture(name, reward=1, overrides=overrides)
                )
                self.assertEqual(row.classification, "unknown")

    def test_nonbinary_nonfinite_and_boolean_rewards_are_unknown(self):
        for index, reward in enumerate((0.5, True, False, float("nan"), float("inf"), "1", None)):
            with self.subTest(reward=reward):
                source = self.fixture(f"reward-{index}", reward=reward, artifact=None)
                self.assertEqual(core.import_trial(self.root, source).classification, "unknown")

    def test_oversized_reward_and_usage_are_unavailable_without_losing_the_trial(self):
        for index, value in enumerate((10**400, -(10**400))):
            with self.subTest(value=value):
                source = self.fixture(
                    f"oversized-{index}",
                    reward=value,
                    artifact=None,
                    overrides={"agent_result": {"n_input_tokens": value, "n_output_tokens": 11}},
                )
                imported = core.import_trial(self.root, source)
                self.assertEqual(imported.classification, "unknown")
                self.assertIsNone(imported.reward)
                self.assertIsNone(imported.usage.n_input_tokens)
                self.assertEqual(imported.usage.n_output_tokens, 11.0)
                state = workflow.result_state(imported)
                self.assertEqual(state.outcome, "no_verdict")
                json.dumps(imported.model_dump(), allow_nan=False)

    def test_reward_artifact_disagreement_and_invalid_text_are_unknown(self):
        for index, artifact in enumerate((0, "invalid", "nan")):
            with self.subTest(artifact=artifact):
                row = core.import_trial(
                    self.root, self.fixture(f"artifact-{index}", reward=1, artifact=artifact)
                )
                self.assertEqual(row.classification, "unknown")
                self.assertTrue(row.warnings)

    def test_snapshot_checksum_never_falls_back_to_result_hash(self):
        for index, checksum in enumerate(
            (None, "", "not-a-checksum", {"value": TASK_CHECKSUM}, True)
        ):
            with self.subTest(checksum=checksum):
                row = self.imported(self.fixture(f"snapshot-{index}", checksum=checksum))
                self.assertIsNone(row.task_checksum)
                self.assertIsNone(row.task_sha256)
                self.assertEqual(len(row.source_sha256), 64)
                self.assertTrue(row.warnings)
                self.assertFalse(row.qualifying_final_trial)

    def test_opaque_task_checksum_is_kept_distinct_from_source_and_evidence_hashes(self):
        source = self.fixture()
        row = core.import_trial(self.root, source)
        self.assertEqual(row.task_checksum, TASK_CHECKSUM)
        self.assertEqual(row.checksum_kind, "harbor.task_checksum")
        self.assertIsNone(row.task_sha256)
        self.assertNotEqual(row.task_checksum, row.source_sha256)
        self.assertNotEqual(row.task_checksum, row.evidence_sha256)

    def test_private_config_environment_trajectory_and_exception_text_are_not_exported(self):
        canary = "PRIVATE_CANARY_NEVER_EXPORT"
        source = self.fixture(
            overrides={
                "config": {
                    "agent": {
                        "name": "codex",
                        "model_name": "openai/test",
                        "kwargs": {
                            "reasoning_effort": "high",
                            "api_key": canary,
                            "instructions": canary,
                        },
                    },
                    "environment": {"type": "docker", "env": {"AUTH_TOKEN": canary}},
                    "auth": canary,
                },
                "exception_info": {
                    "exception_type": "SetupError",
                    "exception_message": canary,
                    "traceback": canary,
                },
                "agent_result": {"n_input_tokens": 1, "metadata": {"secret": canary}},
            }
        )
        self.write_json(
            source.parent / "agent" / "trajectory.json", {"messages": [{"content": canary}]}
        )
        self.write_json(
            source.parent.parent / "lock.json", {"harbor": {"version": "0.14.0"}, "env": canary}
        )
        row = core.import_trial(self.root, source)
        self.assertNotIn(canary, json.dumps(row.model_dump()))
        self.assertEqual(row.exception_type, "SetupError")
        self.assertTrue(any(item.path.endswith("trajectory.json") for item in row.evidence))

    def test_raw_verifier_details_and_free_text_metadata_are_not_exported(self):
        canary = "PRIVATE_DETAIL_CANARY"
        source = self.fixture(
            cases={
                "passed": ["baseline"],
                "failures": [
                    f"case-a: Authorization: Bearer {canary}",
                    {"name": "case-b", "error": {"traceback": canary}},
                ],
            },
            overrides={
                "config": {
                    "agent": {
                        "name": "codex",
                        "model_name": {"secret": canary},
                        "kwargs": {"reasoning_effort": f"free text {canary}"},
                    },
                    "environment": {"type": {"secret": canary}},
                },
                "agent_info": {"version": f"version details {canary}"},
            },
        )
        row = core.import_trial(self.root, source)
        self.assertNotIn(canary, json.dumps(row.model_dump()))
        self.assertEqual({case.name for case in row.cases}, {"baseline", "case-a", "case-b"})
        self.assertTrue(all(not case.detail for case in row.cases))

    def test_case_parser_supports_one_json_summary_inside_log_output(self):
        source = self.fixture(
            cases='setup log\n{"passed":["clean"],"failures":["edge: mismatch"]}\nteardown\n'
        )
        row = core.import_trial(self.root, source)
        self.assertEqual(
            [(case.name, case.status) for case in row.cases],
            [("clean", "passed"), ("edge", "failed")],
        )

    def test_case_parser_does_not_merge_multiple_or_contradictory_summaries(self):
        for name, cases in (
            ("duplicate-case", {"passed": ["same"], "failures": ["same: mismatch"]}),
            (
                "multiple-reports",
                '{"passed":["a"],"failures":[]}\n{"passed":[],"failures":["b: mismatch"]}',
            ),
            ("unsupported", '{"successful": 10, "failed": 0}'),
        ):
            with self.subTest(name=name):
                row = core.import_trial(self.root, self.fixture(name, cases=cases))
                self.assertEqual(row.cases, [])
                self.assertTrue(row.warnings)

    def test_artifact_symlink_escape_does_not_read_outside_workspace(self):
        source = self.fixture()
        outside = self.base / "outside.py"
        outside.write_text("print('outside')", encoding="utf-8")
        artifact = source.parent / "artifacts" / "app" / "solution.py"
        artifact.parent.mkdir(parents=True)
        artifact.symlink_to(outside)
        with self.assertRaises(core.HarborError):
            core.import_trial(self.root, source)

    def test_source_and_stdout_changes_during_import_are_rejected(self):
        original_parser = core.parse_cases
        for name, target in (("result-race", "result"), ("stdout-race", "stdout")):
            with self.subTest(target=target):
                source = self.fixture(name)

                def change_after_parse(stdout, source=source, target=target):
                    parsed = original_parser(stdout)
                    changed = source if target == "result" else stdout
                    changed.write_text(changed.read_text(encoding="utf-8") + "\n", encoding="utf-8")
                    return parsed

                with patch.object(core, "parse_cases", side_effect=change_after_parse):
                    with self.assertRaises(core.HarborError):
                        core.import_trial(self.root, source)
