"""Offline safeguards for the approval-gated, no-retry BR-042 V4 launcher."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('br042_v4_runner', ROOT / 'probes/vessel-geometry/authoring/br042_v4/run.py')
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old = RUNNER.ROOT, RUNNER.B
        self.addCleanup(self.restore)
        self.root = Path(self.tmp.name)
        RUNNER.ROOT = self.root
        RUNNER.B = self.root / 'runs/v4'
        self.task = RUNNER.B / 'tasks/all-vessels'
        self.task.mkdir(parents=True)
        (self.task / 'instruction.md').write_text('Synthetic fixture')
        config = RUNNER.B / 'config.json'
        config.write_text(json.dumps({'n_attempts': 1, 'retry': {'max_retries': 0}, 'environment': {'mounts': None}}))
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        manifest = {'tasks': [{'task_path': str(self.task.relative_to(self.root)), 'files': {'instruction.md': digest(self.task / 'instruction.md')}}], 'configs': {'astra-xhigh': {'path': str(config.relative_to(self.root)), 'sha256': digest(config), 'job_name': 'synthetic-job'}}}
        text = json.dumps(manifest)
        (RUNNER.B / 'freeze.json').write_text(text)
        (self.root / 'docs/evidence').mkdir(parents=True)
        (self.root / 'docs/evidence/br042-v4-freeze.json').write_text(text)
        for name in ['.venv', '.venv-validation']:
            p = self.root / name / 'bin/harbor'
            p.parent.mkdir(parents=True)
            p.write_text('Never executed by these checks')

    def restore(self):
        RUNNER.ROOT, RUNNER.B = self.old

    def test_unmodified_ready_then_extra_public_file_rejected(self):
        RUNNER.verify()
        (self.task / 'patient-hint.txt').write_text('must be rejected')
        with self.assertRaisesRegex(AssertionError, 'Frozen task changed'):
            RUNNER.verify()

    def test_changed_config_rejected(self):
        (RUNNER.B / 'config.json').write_text('{}')
        with self.assertRaisesRegex(AssertionError, 'Launch config changed'):
            RUNNER.verify()

    def test_started_attempt_cannot_restart(self):
        (RUNNER.B / 'events.jsonl').touch()
        with self.assertRaisesRegex(AssertionError, 'already launched'):
            RUNNER.verify()

    def test_existing_job_cannot_overwrite(self):
        (self.root / 'runs/synthetic-job').mkdir()
        with self.assertRaisesRegex(AssertionError, 'Existing run'):
            RUNNER.verify()

    @unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("scipy"), "Optional local imaging runtime")
    def test_controls_do_not_write_into_frozen_task(self):
        (self.task / 'tests').mkdir()
        (self.task / 'solution').mkdir()
        source = ROOT / 'probes/vessel-geometry/authoring/br042_v3/score.py'
        (self.task / 'tests/score.py').write_bytes(source.read_bytes())
        obj = {'centerlines': [{'id': 'synthetic', 'vessel_name': 'Synthetic test vessel', 'points_ras_mm': [[0, 0, 0], [.5, 0, 0], [1, 0, 0]], 'labels': [1, 1, 1]}]}
        for target in ['tests/reference.json', 'solution/centerlines.json']:
            (self.task / target).write_text(json.dumps(obj))
        before = {str(p): p.read_bytes() for p in self.task.rglob('*') if p.is_file()}
        out = RUNNER.control_checks(self.task)
        self.assertTrue(out['split_same_categories']['labeled_pass'])
        self.assertFalse(out['zero_labels']['labeled_pass'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.task.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
