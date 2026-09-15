"""Freeze two unchanged tasks and two audits with public regional exclusions."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import importlib.util
import itertools
import json
import shutil

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'docs/research-rounds/BR-004-sol-followup.md'
ORDER = ['case-32', 'case-83', 'case-46', 'case-61']
PATCHES = {
    'case-46': [('vertebrae_L2', [60, 58, 97], [66, 60, 100])],
    'case-61': [('liver', [62, 80, 110], [64, 85, 112]),
                ('heart', [37, 66, 153], [40, 69, 156])],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def load_scorer(path):
    spec = importlib.util.spec_from_file_location('scoring', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def author_controls(task, cid, exclusions):
    scorer = load_scorer(task / 'tests/scoring.py')
    truth = json.loads((task / 'tests/expected.json').read_text())
    oracle = json.loads((task / 'solution/findings.json').read_text())
    empty = {'cases': [{'case_id': cid, 'findings': []}]}
    regions = np.load(task / 'tests/regions.npz', allow_pickle=False)
    positive = bool(truth['cases'][0]['findings'])
    checks = {}

    def check(name, prediction, wanted):
        try:
            actual = scorer.score(prediction, truth, regions)['passed']
        except (ValueError, TypeError):
            actual = False
        assert actual == wanted, (cid, name, actual, wanted)
        checks[name] = {'expected_pass': wanted, 'observed_pass': actual}

    def with_findings(findings):
        return {'cases': [{'case_id': cid, 'findings': findings}]}

    check('oracle', oracle, True)
    check('empty', empty, not positive)
    check('flag_every_label', with_findings([
        {'label': label, 'point_lps_mm': [0, 0, 0]}
        for label in truth['cases'][0]['focus_labels']]), False)
    wrong = copy.deepcopy(oracle)
    for f in wrong['cases'][0]['findings']:
        f['point_lps_mm'] = [99999, 99999, 99999]
    if positive:
        check('correct_label_wrong_point', wrong, False)
    if exclusions:
        assert json.loads((task / 'environment/review-exclusions.json').read_text())['cases'][0]['exclusions'] == truth['cases'][0]['review_exclusions']
        ignored = [{'label': e['label'], 'point_lps_mm': ((np.array(e['min_lps_mm']) + e['max_lps_mm']) / 2).tolist()} for e in exclusions]
        check('excluded_only', with_findings(ignored), not positive)
        check('oracle_plus_excluded', with_findings(oracle['cases'][0]['findings'] + ignored), True)
        # Case 61 includes both the required and excluded heart regions.
        if cid == 'case-61':
            assert sum(f['label'] == 'heart' for f in oracle['cases'][0]['findings'] + ignored) == 2
        extra = {'label': 'kidney_left', 'point_lps_mm': ignored[0]['point_lps_mm']}
        check('wrong_label_at_excluded_point', with_findings(oracle['cases'][0]['findings'] + [extra]), False)
        for i, e in enumerate(exclusions):
            for side in ['min', 'max']:
                boundary = {'label': e['label'], 'point_lps_mm': e[side + '_lps_mm']}
                check(f'closed_boundary_{i}_{side}', with_findings(oracle['cases'][0]['findings'] + [boundary]), True)
                outside = copy.deepcopy(boundary)
                outside['point_lps_mm'][0] += -0.0001 if side == 'min' else 0.0001
                check(f'outside_boundary_{i}_{side}', with_findings(oracle['cases'][0]['findings'] + [outside]), False)
        base = oracle['cases'][0]['findings']
        for i, bad in enumerate([[float('nan'), 0, 0], [0, float('inf'), 0], [0, 0], 'bad', [True, 0, 0], ['1', 0, 0]]):
            check(f'malformed_point_{i}', with_findings(base + [{'label': exclusions[0]['label'], 'point_lps_mm': bad}]), False)
        duplicate = base + base if positive else [extra, extra]
        check('duplicate_in_scope_labels', with_findings(duplicate), False)
        for f in truth['cases'][0]['findings']:
            for e in exclusions:
                if f['label'] == e['label']:
                    inside = np.all((regions[f['region_key']] >= e['min_lps_mm']) & (regions[f['region_key']] <= e['max_lps_mm']), axis=1)
                    assert not inside.any()
        checks['public_private_exclusions_equal'] = True
        checks['planted_regions_disjoint_from_exclusions'] = True
    return checks

def main():
    freeze_path = ROOT / 'docs/evidence/br004-sol-freeze.json'
    assert not freeze_path.exists(), 'Do not rewrite an existing experiment freeze.'
    parent = json.loads((ROOT / 'docs/evidence/br004-single-patient-freeze.json').read_text())
    rows, controls = [], {}
    for cid in ORDER:
        old = next(row for row in parent['tasks'] if row['case_id'] == cid)
        source = ROOT / old['task_path']
        assert all(sha(source / name) == value for name, value in old['files'].items())
        exclusions, patch_receipts = [], []
        task = source
        task_id = old['task_id']
        if cid in PATCHES:
            task_id += '-v2'
            task = HERE / 'tasks' / task_id
            assert not task.exists()
            shutil.copytree(source, task, ignore=shutil.ignore_patterns('__pycache__'))
            private_path = ROOT / f'runs/br004-v1/build/{cid}-private.npz'
            affine = np.load(private_path, allow_pickle=False)['affine']
            for label, lo, hi in PATCHES[cid]:
                corners = np.array(list(itertools.product(*zip(lo, hi))))
                world = corners @ affine[:3, :3].T + affine[:3, 3]
                exclusions.append({'label': label, 'min_lps_mm': (world.min(axis=0) - 6).tolist(),
                                   'max_lps_mm': (world.max(axis=0) + 6).tolist()})
                patch_receipts.append({'label': label, 'source_voxel_min_xyz': lo, 'source_voxel_max_xyz': hi,
                                       'padding_mm': 6, 'source_private_path': str(private_path.relative_to(ROOT)),
                                       'source_private_sha256': sha(private_path), 'affine_lps': affine.tolist()})
            write(task / 'environment/review-exclusions.json', {'cases': [{'case_id': cid, 'exclusions': exclusions}]})
            expected = json.loads((task / 'tests/expected.json').read_text())
            expected['cases'][0]['review_exclusions'] = exclusions
            write(task / 'tests/expected.json', expected)
            docker = task / 'environment/Dockerfile'
            docker.write_text(docker.read_text() + '\nCOPY review-exclusions.json /app/\n')
            config = task / 'task.toml'
            config.write_text(config.read_text().replace('terminal-bench/' + old['task_id'] + '"', 'terminal-bench/' + task_id + '"'))
            instruction = task / 'instruction.md'
            text = instruction.read_text().replace('For each affected focus label, return one', 'After the exclusions below are applied, for each affected focus label return one')
            text = text.replace('multiple points, duplicate labels, and duplicate cases are invalid.',
                                'multiple points per finding, duplicate in-scope labels, and duplicate cases are invalid.')
            marker = 'This is a fixed research audit'
            scope = '''`/app/review-exclusions.json` lists small source regions excluded from this
audit because their annotation status is unresolved. Each entry gives a label
and a closed, axis-aligned box: `min_lps_mm <= point_lps_mm <= max_lps_mm` on
all three patient LPS axes. Findings with that label and a point inside its box
are ignored and do not satisfy any required finding. The remainder of that
label is still in scope. You may report both an excluded region and an actual
error elsewhere for the same label; after exclusions are removed, at most one
finding per label may remain. Every finding must have a finite numeric 3D
point. Regions excluded for one label are not excluded for another label.

'''
            instruction.write_text(text.replace(marker, scope + marker))
            shutil.copy2(HERE / 'authoring/scoring.py', task / 'tests/scoring.py')
            (task / 'authoring/notes.md').write_text(f'''# Corrected audit scope: {cid}

Derived from {old['task_path']}. CT/SEG bytes, focus labels, planted discrepancy
regions and tolerance are unchanged. Public label-specific exclusions match the
private grader. Unresolved source patches are outside scope, not clinically
relabelled. See docs/research-rounds/BR-004-sol-followup.md and the frozen source
patch receipts in docs/evidence/br004-sol-freeze.json. Preserve the old task and
its Terra review. This new condition receives one Sol/xhigh trial.
''')
            assert sha(task / 'environment/data.tar.gz') == old['files']['environment/data.tar.gz']
            assert sha(task / 'tests/regions.npz') == old['files']['tests/regions.npz']
        controls[cid] = author_controls(task, cid, exclusions)
        snapshot = ROOT / 'runs/br004-sol/task-snapshots' / task_id
        assert not snapshot.exists()
        shutil.copytree(task, snapshot, ignore=shutil.ignore_patterns('__pycache__'))
        row = copy.deepcopy(old)
        row.update(task_id=task_id, task_path=str(task.relative_to(ROOT)), execution_snapshot=str(snapshot.relative_to(ROOT)),
                   source_truth_hold=False, source_truth_hold_reason=None, parent_task_path=old['task_path'],
                   task_bytes_unchanged=cid not in PATCHES, patient_bytes_unchanged=True,
                   review_exclusions=exclusions, source_patch_receipts=patch_receipts,
                   source_uncertainty='Original-source patches excluded publicly; no clinical adjudication.' if exclusions else None,
                   files={str(p.relative_to(task)): sha(p) for p in sorted(task.rglob('*')) if p.is_file() and '__pycache__' not in p.parts})
        rows.append(row)
    control_path = ROOT / 'docs/evidence/br004-sol-author-controls.json'
    write(control_path, {'round': 'BR-004', 'condition': 'sol-corrected-scope-v1', 'cases': controls})
    write(freeze_path, {'round': 'BR-004', 'condition': 'sol-corrected-scope-v1', 'captured_at': datetime.now(timezone.utc).isoformat(),
          'parent_freeze': str((ROOT / 'docs/evidence/br004-single-patient-freeze.json').relative_to(ROOT)), 'task_order': ORDER,
          'builder_sha256': sha(Path(__file__)), 'scorer_source_sha256': sha(HERE / 'authoring/scoring.py'),
          'protocol_path': str(PROTOCOL.relative_to(ROOT)), 'protocol_sha256': sha(PROTOCOL),
          'author_controls_path': str(control_path.relative_to(ROOT)), 'author_controls_sha256': sha(control_path),
          'protocol': {'model': 'openai/gpt-5.6-sol', 'reasoning_effort': 'xhigh', 'model_attempts_per_task': 1,
                       'retries': 0, 'concurrent_model_trials': 1, 'agent_timeout_seconds': 1800, 'cpus': 4, 'memory_mb': 4096,
                       'harbor_model_version': '0.14.0', 'harbor_control_version': '0.18.0'}, 'tasks': rows})
    policy_path = ROOT / 'configs/artifact-policy.json'
    policy = json.loads(policy_path.read_text())
    for row in rows:
        if not row['task_bytes_unchanged']:
            for suffix in ['environment/data.tar.gz', 'tests/regions.npz']:
                policy['allowed_artifacts' if 'allowed_artifacts' in policy else 'retained_artifacts'][row['task_path'] + '/' + suffix] = {
                    'sha256': row['files'][suffix], 'reason': 'Required unchanged patient fixture or spatial evidence for the corrected-scope audit; see docs/evidence/br004-sol-freeze.json.'}
    write(policy_path, policy)
    print(json.dumps({'frozen_tasks': len(rows), 'exclusions': {r['case_id']: r['review_exclusions'] for r in rows}, 'author_controls_passed': True}, indent=2))

if __name__ == '__main__':
    main()
