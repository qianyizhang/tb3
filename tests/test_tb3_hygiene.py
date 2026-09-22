"""Exercise the commit boundary in temporary Git repositories."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tb3_medical.hygiene import index_files, problems

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "configs/artifact-policy.json").read_text())


class HygieneTests(unittest.TestCase):
    def setUp(self):
        # A caller may be checking an alternate index; fixture Git must stay local.
        self.enterContext(
            patch.dict(
                os.environ,
                {key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
                clear=True,
            )
        )
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.git("init", "-q")
        self.write("configs/artifact-policy.json", json.dumps(POLICY).encode())
        self.git("add", "configs/artifact-policy.json")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def stage(self, name, data):
        self.write(name, data)
        self.git("add", "-f", "--", name)

    def check(self):
        return problems(index_files(self.root))

    def test_checks_staged_bytes_even_when_worktree_fixed(self):
        self.stage("catalog/example.json", b"{broken")
        self.write("catalog/example.json", b"{}")
        self.assertTrue(any("invalid json" in error for error in self.check()))

    def test_unstaged_experiment_and_missing_raw_runs_do_not_affect_check(self):
        self.stage("catalog/trials/example.json", b'{"source_result":"runs/missing/result.json"}')
        self.write("catalog/work-in-progress.json", b"{broken")
        self.write("runs/active/output.bin", b"\0")
        self.assertEqual(self.check(), [])

    def test_force_added_local_files_fail(self):
        self.stage(".gitignore", (ROOT / ".gitignore").read_bytes())
        for name in (
            "runs/job/result.json",
            ".env.local",
            "probes/demo/environment/test.dSYM/info",
            "probes/demo/target/build.txt",
            "cache/__pycache__/module.pyc",
            ".venv/.env.example",
        ):
            with self.subTest(name=name):
                self.stage(name, b"{}")
                self.assertTrue(any(name in error for error in self.check()))

    def test_ignore_patterns_preserve_evidence_and_required_inputs(self):
        self.write(".gitignore", (ROOT / ".gitignore").read_bytes())
        for name, ignored in (
            ("probes/demo/environment/a.dSYM/info", True),
            ("runs/raw.json", True),
            (".venv-extra/bin/python", True),
            ("docs/evidence/summary.json", False),
            ("probes/demo/tests/fixture.tar", False),
            ("probes/demo/environment/Cargo.lock", False),
            (".env.example", False),
        ):
            result = subprocess.run(["git", "-C", str(self.root), "check-ignore", "-q", name])
            self.assertEqual(result.returncode == 0, ignored, name)

    def test_retained_binary_requires_matching_digest_and_reason(self):
        name, data = "probes/demo/tests/fixture.tar", b"fixture\0bytes"
        self.stage(name, data)
        self.assertTrue(any("explicit digest" in error for error in self.check()))
        policy = copy.deepcopy(POLICY)
        policy["retained_artifacts"][name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "reason": "Offline verifier fixture",
        }
        self.stage("configs/artifact-policy.json", json.dumps(policy).encode())
        self.assertEqual(self.check(), [])
        self.stage(name, data + b"changed")
        self.assertTrue(any("artifact changed" in error for error in self.check()))

    def test_large_text_requires_exception(self):
        self.stage("docs/huge.txt", b"x" * (POLICY["max_file_bytes"] + 1))
        self.assertTrue(any("explicit digest" in error for error in self.check()))

    def test_invalid_toml_fails(self):
        self.stage("probes/demo/task.toml", b"version = [")
        self.assertTrue(any("invalid toml" in error for error in self.check()))

    def test_symlink_is_rejected_without_reading_target(self):
        (self.root / "leak").symlink_to("/etc/passwd")
        self.git("add", "leak")
        with self.assertRaisesRegex(ValueError, "unsupported index mode"):
            self.check()


if __name__ == "__main__":
    unittest.main()
