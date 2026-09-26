"""Hub preflight must reject copied credentials before invoking Harbor."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tb3_medical import hub
from tb3_medical.errors import MedicalError


class HubTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.job = self.root / ".local/attempts/attempt-example/job"
        trial = self.job / "task__one"
        trial.mkdir(parents=True)
        (self.job / "config.json").write_text('{"agents": [{"env": {}}]}')
        (self.job / "result.json").write_text(
            '{"id": "job-1", "finished_at": "2026-09-23", "n_total_trials": 1}'
        )
        (trial / "config.json").write_text('{"agent": {"env": {}}}')
        (trial / "result.json").write_text(
            '{"id": "trial-1", "finished_at": "2026-09-23", "config": {"agent": {"env": {}}}}'
        )
        (trial / "agent").mkdir()
        (trial / "agent/trajectory.json").write_text("[]")

    def test_inspect_includes_trajectory_and_refuses_copied_env(self):
        row = hub.inspect(self.root, "attempt-example")
        self.assertEqual(row["status"], "ready_for_content_review")
        self.assertEqual(row["trajectories"], 1)
        self.assertIn("task__one/agent/trajectory.json", row["files"])
        trial_result = self.job / "task__one/result.json"
        trial_result.write_text(
            json.dumps(
                {
                    "id": "trial-1",
                    "finished_at": "2026-09-23",
                    "config": {"agent": {"env": {"API_KEY": "secret"}}},
                }
            )
        )
        row = hub.inspect(self.root, "attempt-example")
        self.assertEqual(row["status"], "blocked")
        self.assertIn("nonempty environment values in upload payload", row["problems"])
        with patch("tb3_medical.hub.subprocess.run") as run:
            with self.assertRaises(MedicalError):
                hub.upload(
                    self.root, "attempt-example", reviewed=True, public=False, executable="harbor"
                )
            run.assert_not_called()

    def test_upload_requires_review_and_passes_explicit_visibility(self):
        executable = self.root / "harbor"
        executable.write_text("#!/bin/sh\n")
        executable.chmod(0o755)
        with patch("tb3_medical.hub.subprocess.run") as run:
            with self.assertRaisesRegex(MedicalError, "--reviewed"):
                hub.upload(
                    self.root,
                    "attempt-example",
                    reviewed=False,
                    public=False,
                    executable=str(executable),
                )
            run.assert_not_called()
            run.return_value = subprocess.CompletedProcess(
                [], 0, "View at https://hub.harborframework.com/jobs/job-1", ""
            )
            result = hub.upload(
                self.root,
                "attempt-example",
                reviewed=True,
                public=False,
                executable=str(executable),
            )
            self.assertEqual(result["visibility"], "private")
            self.assertEqual(run.call_args.args[0][-1], "--private")
            hub.upload(
                self.root, "attempt-example", reviewed=True, public=True, executable=str(executable)
            )
            self.assertEqual(run.call_args.args[0][-1], "--public")
            run.return_value = subprocess.CompletedProcess(
                [], 0, "failed 1 trial(s)\nView at https://hub.harborframework.com/jobs/job-1", ""
            )
            partial = hub.upload(
                self.root,
                "attempt-example",
                reviewed=True,
                public=False,
                executable=str(executable),
            )
            self.assertFalse(partial["uploaded"])
            self.assertEqual(partial["failed_trials"], 1)

    def test_unfinished_and_symlink_jobs_are_blocked(self):
        (self.job / "result.json").write_text('{"id": "job-1", "n_total_trials": 1}')
        self.assertIn("job is unfinished", hub.inspect(self.root, "attempt-example")["problems"])
        (self.job / "result.json").write_text(
            '{"id": "job-1", "finished_at": "2026-09-23", "n_total_trials": 1}'
        )
        (self.job / "task__one/agent/link").symlink_to(self.root / "private")
        self.assertEqual(hub.inspect(self.root, "attempt-example")["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
