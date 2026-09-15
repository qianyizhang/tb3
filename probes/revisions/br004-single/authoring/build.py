"""Split the frozen BR-004 batch without altering patient bytes or grading."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
import tarfile

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'probes/dicom-anatomy-audit'
HERE = Path(__file__).resolve().parents[1]
TASKS = HERE / 'tasks'
ORDER = ['case-74', 'case-19', 'case-83', 'case-46', 'case-28', 'case-61', 'case-95', 'case-32']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def main():
    parent_freeze = json.loads((ROOT / 'docs/evidence/br004-anatomy-audit-v1-freeze.json').read_text())
    assert all(sha(SOURCE / name) == value for name, value in parent_freeze['files'].items())
    assert not TASKS.exists(), 'Preserve any existing split snapshot; do not overwrite it.'
    truth = json.loads((SOURCE / 'tests/expected.json').read_text())
    answers = json.loads((SOURCE / 'solution/findings.json').read_text())
    regions = np.load(SOURCE / 'tests/regions.npz', allow_pickle=False)
    spec = importlib.util.spec_from_file_location('scoring', SOURCE / 'tests/scoring.py')
    scorer = importlib.util.module_from_spec(spec); spec.loader.exec_module(scorer)
    with tarfile.open(SOURCE / 'environment/data.tar.gz') as archive:
        source_members = {m.name: archive.extractfile(m).read() for m in archive if m.isfile()}
    cases = json.loads(source_members['cases.json'])
    rows = []
    for cid in ORDER:
        identifier = 'dicom-audit-' + cid.split('-')[1]
        task = TASKS / identifier
        for directory in ['environment', 'tests', 'solution', 'authoring']:
            (task / directory).mkdir(parents=True)
        for name in ['environment/Dockerfile', 'environment/read_case.py',
                     'environment/SOURCE_NOTICE.md', 'environment/DATA-LICENSE.txt',
                     'environment/LABEL-LICENSE.txt', 'tests/Dockerfile',
                     'tests/scoring.py', 'tests/verifier.py', 'tests/test.sh', 'solution/solve.sh']:
            shutil.copy2(SOURCE / name, task / name)
        instruction = (SOURCE / 'instruction.md').read_text()
        instruction = instruction.replace('completed audit to `/app/answer/findings.json`.',
                                          'completed audit to `/app/answer/findings.json`. This task contains one patient.')
        (task / 'instruction.md').write_text(instruction)
        (task / 'task.toml').write_text((SOURCE / 'task.toml').read_text().replace('terminal-bench/dicom-anatomy-audit', 'terminal-bench/' + identifier))
        public_case = next(c for c in cases if c['case_id'] == cid)
        expected = {'cases': [next(c for c in truth['cases'] if c['case_id'] == cid)]}
        correct = {'cases': [next(c for c in answers['cases'] if c['case_id'] == cid)]}
        empty = {'cases': [{'case_id': cid, 'findings': []}]}
        write_json(task / 'tests/expected.json', expected)
        write_json(task / 'solution/findings.json', correct)
        write_json(task / 'environment/findings.json', empty)
        private = {f['region_key']: regions[f['region_key']] for f in expected['cases'][0]['findings']}
        np.savez_compressed(task / 'tests/regions.npz', **private)
        subset = {name: body for name, body in source_members.items() if name.startswith(cid + '/') or name == 'label-list.json'}
        subset['cases.json'] = (json.dumps([public_case], indent=2) + '\n').encode()
        with (task / 'environment/data.tar.gz').open('wb') as raw:
            with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped:
                with tarfile.open(mode='w', fileobj=zipped) as archive:
                    for name, body in sorted(subset.items()):
                        member = tarfile.TarInfo(name); member.size = len(body); member.mode = 0o644
                        archive.addfile(member, io.BytesIO(body))
        with tarfile.open(task / 'environment/data.tar.gz') as archive:
            extracted = {m.name: archive.extractfile(m).read() for m in archive if m.isfile()}
        patient_files = [name for name in extracted if name.startswith(cid + '/')]
        assert all(extracted[name] == source_members[name] for name in patient_files)
        assert extracted['label-list.json'] == source_members['label-list.json']
        assert json.loads(extracted['cases.json']) == [public_case]
        assert scorer.score(correct, expected, private)['passed']
        nop_pass = scorer.score(empty, expected, private)['passed']
        assert nop_pass == (not expected['cases'][0]['findings'])
        all_labels = {'cases': [{'case_id': cid, 'findings': [
            {'label': label, 'point_lps_mm': [0, 0, 0]} for label in public_case['focus_labels']]}]}
        assert not scorer.score(all_labels, expected, private)['passed']
        wrong_location = copy.deepcopy(correct)
        for finding in wrong_location['cases'][0]['findings']:
            finding['point_lps_mm'] = [99999, 99999, 99999]
        if private:
            assert not scorer.score(wrong_location, expected, private)['passed']
        notes = f'''# Single-patient condition: {cid}

Derived from the unchanged BR-004 v1 cohort. Patient DICOM bytes, focus labels,
taxonomy, decoder, discrepancy regions, scorer and 1,800-second allowance are
unchanged. Only the review batch is reduced to this patient. This is one fresh
Terra/max attempt, with no retries or answer guidance. The collection protocol
and source-truth limitations are in docs/research-rounds/BR-004-single-patient-benchmark.md.
An empty-answer control is expected to {'pass' if nop_pass else 'fail'} here.
Clean-task discrimination is checked with a flag-every-label negative control.
No specialist clinical validation or postoperative history is asserted.
'''
        (task / 'authoring/notes.md').write_text(notes)
        snapshot = ROOT / 'runs/br004-single/task-snapshots' / identifier
        shutil.copytree(task, snapshot)
        rows.append({'task_id': identifier, 'case_id': cid, 'task_path': str(task.relative_to(ROOT)),
                     'execution_snapshot': str(snapshot.relative_to(ROOT)),
                     'patient_file_count': len(patient_files), 'patient_bytes_identical_to_v1': True,
                     'patient_files_sha256': {name: hashlib.sha256(extracted[name]).hexdigest() for name in patient_files},
                     'focus_labels_unchanged': True, 'focus_label_count': len(public_case['focus_labels']),
                     'expected_positive_labels': len(private), 'nop_expected_reward': int(nop_pass),
                     'author_reference_pass': True, 'author_all_labels_rejected': True,
                     'source_truth_hold': cid == 'case-46',
                     'source_truth_hold_reason': 'Unresolved anterior L2 component; exact anatomical success is provisional pending adjudication.' if cid == 'case-46' else None,
                     'files': {str(p.relative_to(task)): sha(p) for p in sorted(task.rglob('*')) if p.is_file()}})
    receipt = {'round': 'BR-004', 'condition': 'single-patient-v1', 'captured_at': datetime.now(timezone.utc).isoformat(),
               'parent_freeze': 'docs/evidence/br004-anatomy-audit-v1-freeze.json', 'task_order': ORDER,
               'builder_sha256': sha(Path(__file__)),
               'protocol_sha256': sha(ROOT / 'docs/research-rounds/BR-004-single-patient-benchmark.md'),
               'protocol': {'model': 'openai/gpt-5.6-terra', 'reasoning_effort': 'max', 'model_attempts_per_task': 1,
                            'retries': 0, 'concurrent_model_trials': 1, 'agent_timeout_seconds': 1800,
                            'cpus': 4, 'memory_mb': 4096, 'harbor_model_version': '0.14.0', 'harbor_control_version': '0.18.0'},
               'tasks': rows}
    write_json(ROOT / 'docs/evidence/br004-single-patient-freeze.json', receipt)
    policy_path = ROOT / 'configs/artifact-policy.json'
    policy = json.loads(policy_path.read_text())
    # Preserve concurrent entries; register only the new required fixture paths.
    artifacts = policy['allowed_artifacts'] if 'allowed_artifacts' in policy else policy['retained_artifacts']
    for row in rows:
        for suffix in ['environment/data.tar.gz', 'tests/regions.npz']:
            name = row['task_path'] + '/' + suffix
            artifacts[name] = {'sha256': row['files'][suffix], 'reason': 'Required single-patient derived fixture or private spatial evidence; see docs/evidence/br004-single-patient-freeze.json and the BR-004 single-patient protocol.'}
    write_json(policy_path, policy)
    print(json.dumps({'tasks': len(rows), 'focus_labels': sum(r['focus_label_count'] for r in rows), 'same_patient_bytes': True}, indent=2))

if __name__ == '__main__':
    main()
