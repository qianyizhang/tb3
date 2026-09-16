"""Audit the recorded formulation contrast; no solver execution or new trial.

Extract every printed coarse-search candidate from the completed BR-028 trace.
Reference labels are used afterward for diagnostics only, never for selection.
"""
import ast
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/registration-session-publication'
OLD = 'runs/br024-deform-harder-patient3-sol-xhigh-v1-20260916/deform-harder-patient3__NJq7SQn/agent/trajectory.json'
NEW = 'runs/br028-deform-patient3-source3d-sol-xhigh-v1-20260916/deform-patient3-source3d__3tbVdMW/agent/trajectory.json'
TRUTH = 'runs/br028-registration-3d-source/tasks/deform-patient3-source3d/tests/truth.json'


def read(path):
    return json.loads((ROOT / path).read_text())


def main():
    new = read(NEW)
    step = next(s for s in new['steps'] if s['step_id'] == 19)
    blocks = ast.literal_eval(step['observation']['results'][0]['content'])
    output = '\n'.join(b['text'] for b in blocks)
    truth = read(TRUTH)
    expected = dict(zip(truth['query_ids'], truth['points_world_mm']))
    rows = []
    radius = None
    for line in output.splitlines():
        if line.startswith('RADIUS '):
            radius = list(ast.literal_eval(line[7:]))
        elif line.startswith('q0'):
            qid, raw = line.split(' ', 1)
            candidates = ast.literal_eval(raw)
            rows.append({'query': qid, 'radius_voxels': radius,
                         'candidates': [{'rank': i + 1, 'ncc': score,
                                         'printed_world_mm': xyz,
                                         'offset_voxels': offset,
                                         'reference_distance_mm': math.dist(xyz, expected[qid])}
                                        for i, (score, xyz, offset) in enumerate(candidates)]})
    assert len(rows) == 24 and all(len(r['candidates']) == 5 for r in rows)
    messages = {}
    for name, path, ids in [('2d', OLD, [32, 42, 68]), ('3d', NEW, [11, 22, 35, 45])]:
        messages[name] = [{'step': s['step_id'], 'message': s['message']}
                          for s in read(path)['steps'] if s['step_id'] in ids]
    scripts = {}
    for folder, key, names in [
        ('runs/br024-harder-registration/captured-agent-artifacts-patient3', 'files', ['/tmp/localopt7.py']),
        ('runs/br028-registration-3d-source/captured-agent-artifacts', 'latest_files',
         ['/app/local_ncc.py', '/app/refine_local.py', '/app/refine_rigid.py'])]:
        index = read(folder + '/index.json')
        for name in names:
            item = index[key][name]
            assert hashlib.sha256((ROOT / item['object_path']).read_bytes()).hexdigest() == item['sha256']
            scripts[name] = item
    payload = {
        'round': 'BR-028', 'analysis': 'Posthoc formulation contrast and user adjudication follow-up',
        'new_trials': 0, 'new_solver_runs': 0,
        'candidate_note': 'All 120 printed candidates retained. Distances use rounded 0.1 mm trace coordinates and are approximate; these are not new submitted answers.',
        'coarse_search_step': 19, 'coarse_search': rows, 'visible_messages': messages,
        'captured_scripts': scripts,
        'direct_observations': [
            'Full source volume is loaded and sampled by both the coarse search and local refinement.',
            'New search starts at nominal source geometry, not the dense deformation estimate. All reference destinations are within its bounds in the earlier stage audit.',
            'q02 has the same top-ranked candidate at all three patch sizes. q04 has the same top-ranked candidate at the first two sizes and a nearby candidate at the largest size.',
            'The earlier final q04 search excludes the reference by at least 25.50 mm; the new broad search removes that obstruction.',
            'Every complete saved full-volume field fails the frozen point criteria. Local matching, rather than a successful global field alone, supplies the final answer.',
            'The model explicitly describes two nearby q06 candidates along one boundary. The user later accepts the final worst case visually.'
        ],
        'inference': 'Real source depth makes adjacent vessel and boundary structure available to the objective and image review. Combined with search independent of the wrong global fit, this plausibly explains recovery of q02 and q04. No matched 2D-versus-3D solver ablation isolates these contributions.',
        'limits': ['One fresh model attempt per condition.', 'Visible messages and code do not reveal encrypted internal reasoning.', 'A passing 2D author route already exists.', 'User visual acceptance is separate from the unchanged geometric grader and is not clinical validation.'],
        'evidence': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [OLD, NEW, TRUTH,
            'docs/evidence/br024-stage-analysis.json', 'docs/evidence/br028-stage-analysis.json',
            'docs/evidence/br028-results.json']}
    }
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2) + '\n'
    (OUT / 'formulation-analysis.json').write_text(text)
    (ROOT / 'docs/evidence/br028-formulation-analysis.json').write_text(text)
    for row in rows:
        if row['query'] in ['q02', 'q04']:
            print(row['query'], row['radius_voxels'], round(row['candidates'][0]['reference_distance_mm'], 3))


if __name__ == '__main__':
    main()
