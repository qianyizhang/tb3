from __future__ import annotations

import importlib.util
import json
import platform
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "tb3.py"
SPEC = importlib.util.spec_from_file_location("tb3_runner", MODULE_PATH)
assert SPEC and SPEC.loader
tb3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tb3)


class TB3RunnerTests(unittest.TestCase):
    def make_tree(self) -> tuple[Path, Path, Path, Path]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        task = root / "task"
        (task / "environment").mkdir(parents=True)
        (task / "solution").mkdir()
        (task / "tests").mkdir()
        (task / "task.toml").write_text("version = 1\n", encoding="utf-8")
        (task / "instruction.md").write_text("task\n", encoding="utf-8")
        (task / "environment" / "Dockerfile").write_text("FROM ubuntu:24.04\n", encoding="utf-8")
        (task / "solution" / "solve.sh").write_text("#!/bin/bash\n", encoding="utf-8")
        (task / "tests" / "Dockerfile").write_text("FROM ubuntu:24.04\n", encoding="utf-8")
        (task / "tests" / "test.sh").write_text("#!/bin/bash\n", encoding="utf-8")
        upstream = root / "upstream"
        checks = upstream / "scripts" / "checks"
        checks.mkdir(parents=True)
        for _, name in tb3.STATIC_CHECKS:
            script = checks / name
            script.write_text(
                "#!/bin/bash\npython3 -c 'import sys; assert sys.version_info[:2] == (3, 12)'\nprintf '%s\\n' \"$0:$1\"\n",
                encoding="utf-8",
            )
        prompt = upstream / "docs" / "prompts" / "hack-trial-prompt.md"
        prompt.parent.mkdir(parents=True)
        prompt.write_text("PINNED RED TEAM PROMPT\n", encoding="utf-8")
        lock = root / "upstream-lock.json"
        files = [path for _, path in tb3.STATIC_CHECKS]
        hashes = {f"scripts/checks/{path}": tb3._sha256_file(checks / path) for path in files}
        hashes["docs/prompts/hack-trial-prompt.md"] = tb3._sha256_file(prompt)
        lock.write_text(json.dumps({"commit": tb3.UPSTREAM_COMMIT, "sha256": hashes}), encoding="utf-8")
        return root, task, upstream, lock

    def test_static_runs_all_pinned_checks_and_captures_evidence(self) -> None:
        root, task, upstream, lock = self.make_tree()
        with patch.object(tb3, "_pinned_commit", return_value=tb3.UPSTREAM_COMMIT):
            status, manifest_path = tb3.run_static(task, upstream, root / "runs", lock)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(status, 0)
        self.assertEqual(len(tb3.STATIC_CHECKS), 22)
        self.assertEqual(len(manifest["checks"]), 22)
        self.assertTrue(manifest["task_sha256"])
        self.assertEqual(manifest["static_runtime"]["python_executable"], sys.executable)
        self.assertEqual(manifest["static_runtime"]["python_version"], platform.python_version())
        for check in manifest["checks"]:
            self.assertEqual(check["exit_code"], 0)
            self.assertTrue((manifest_path.parent / check["stdout"]).is_file())
            self.assertTrue((manifest_path.parent / check["stderr"]).is_file())

    def test_static_refuses_a_missing_check_before_reporting_success(self) -> None:
        root, task, upstream, lock = self.make_tree()
        (upstream / "scripts" / "checks" / tb3.STATIC_CHECKS[-1][1]).unlink()
        with patch.object(tb3, "_pinned_commit", return_value=tb3.UPSTREAM_COMMIT):
            with self.assertRaisesRegex(tb3.RunnerError, "pinned upstream file is missing"):
                tb3.run_static(task, upstream, root / "runs", lock)

    def test_static_refuses_missing_task_inputs_before_upstream_scripts_can_skip(self) -> None:
        root, task, upstream, lock = self.make_tree()
        (task / "tests" / "test.sh").unlink()
        with self.assertRaisesRegex(tb3.RunnerError, "required task files are missing"):
            tb3.run_static(task, upstream, root / "runs", lock)

    def test_static_refuses_an_unresolvable_or_wrong_upstream(self) -> None:
        root, task, upstream, lock = self.make_tree()
        with self.assertRaisesRegex(tb3.RunnerError, "cannot resolve git HEAD"):
            tb3.run_static(task, upstream, root / "runs", lock)
        with patch.object(tb3, "_pinned_commit", return_value="not-the-pin"):
            with self.assertRaisesRegex(tb3.RunnerError, "expected pinned"):
                tb3.run_static(task, upstream, root / "runs", lock)

    def test_default_plan_has_modal_models_trials_and_pinned_cheat_prompt(self) -> None:
        root, task, upstream, _ = self.make_tree()
        commands = tb3.plan_commands(task, "modal", upstream, root / ".venv" / "bin" / "harbor", root / "runs")
        plan = "\n".join(commands)
        self.assertIn("--env modal", plan)
        self.assertIn("openai/gpt-5.6-terra --ae CODEX_FORCE_AUTH_JSON=1 --ak reasoning_effort=high --n-attempts 1", plan)
        self.assertIn("openai/gpt-5.6-sol --ae CODEX_FORCE_AUTH_JSON=1 --ak reasoning_effort=xhigh --n-attempts 3", plan)
        self.assertIn("anthropic/claude-opus-5 --ak reasoning_effort=max --n-attempts 3", plan)
        self.assertIn("CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000", plan)
        self.assertIn("--ae CODEX_FORCE_AUTH_JSON=1", plan)
        self.assertIn("stage-cheat", plan)
        self.assertIn("--n-attempts 1 --job-name tb3-cheat-sol", plan)
        self.assertIn(".venv-validation/bin/harbor' run", plan)
        self.assertNotIn("docker build", plan)
        self.assertNotIn("http_proxy", plan)

    def test_docker_plan_adds_only_the_explicit_docker_build(self) -> None:
        root, task, upstream, _ = self.make_tree()
        plan = "\n".join(tb3.plan_commands(task, "docker", upstream, Path("harbor"), root / "runs"))
        self.assertIn("docker build -t tb3-task-env", plan)
        self.assertIn("--env docker", plan)

    def test_api_key_plan_omits_subscription_only_agent_environment(self) -> None:
        root, task, upstream, _ = self.make_tree()
        plan = "\n".join(tb3.plan_commands(task, "modal", upstream, Path("harbor"), root / "runs", subscription=False))
        self.assertNotIn("CODEX_FORCE_AUTH_JSON", plan)

    def test_agent_proxy_is_shell_quoted_for_every_agent_but_not_analysis(self) -> None:
        root, task, upstream, _ = self.make_tree()
        proxy = "http://192.168.5.2:10808"
        commands = tb3.plan_commands(task, "modal", upstream, Path("harbor"), root / "runs", agent_proxy=proxy)
        agent_commands = [line for line in commands if " --agent " in line or " -a claude-code " in line]
        self.assertEqual(len(agent_commands), 8)
        for command in agent_commands:
            self.assertIn("--ae 'http_proxy=http://192.168.5.2:10808'", command)
            self.assertIn("--ae 'HTTPS_PROXY=http://192.168.5.2:10808'", command)
            self.assertIn("--ae 'NO_PROXY=localhost,127.0.0.1'", command)
        self.assertTrue(all("http_proxy" not in line for line in commands if " analyze " in line))

    def test_agent_proxy_parser_rejects_non_url_and_credentials(self) -> None:
        with self.assertRaises(Exception):
            tb3._agent_proxy_url("localhost:10808")
        with self.assertRaises(Exception):
            tb3._agent_proxy_url("http://name:secret@proxy.invalid:1080")

    def test_stage_cheat_copies_once_and_appends_the_pinned_prompt(self) -> None:
        root, task, upstream, lock = self.make_tree()
        (task / "instruction.md").write_text("Do not cheat the verifier.\nKeep this line.\n", encoding="utf-8")
        destination = root / "runs" / "cheat-stage"
        destination.parent.mkdir()
        with patch.object(tb3, "_pinned_commit", return_value=tb3.UPSTREAM_COMMIT):
            tb3.stage_cheat(task, destination, upstream, lock)
        staged = (destination / "instruction.md").read_text(encoding="utf-8")
        self.assertNotIn("Do not cheat", staged)
        self.assertTrue(staged.endswith("\n\nPINNED RED TEAM PROMPT\n"))
        self.assertIn("Do not cheat", (task / "instruction.md").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(tb3.RunnerError, "already exists"):
            tb3.stage_cheat(task, destination, upstream, lock)


if __name__ == "__main__":
    unittest.main()
