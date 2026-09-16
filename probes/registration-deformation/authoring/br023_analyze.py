"""Independent private grading after public-input Sol component execution."""
import hashlib
import json
from pathlib import Path
import re
import numpy as np
from score import score

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br023-sol-registration'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan = read(OUT / 'component-plan.json')
    assert sha(ROOT / plan['protocol_path']) == plan['protocol_sha256']
    for path, expected in plan['source_files'].items():
        assert sha(ROOT / path) == expected
    execution = read(OUT / 'component-execution.json')
    assert execution['component_plan_sha256'] == sha(OUT / 'component-plan.json')
    assert len(execution['conditions']) == len(plan['conditions'])
    for row in execution['conditions']:
        assert row['exit_code'] == 0 and not row['private_labels_mounted'] and row['network'] == 'none'
        for path, expected in row['files'].items():
            assert sha(ROOT / path) == expected
    truth = read(ROOT / 'runs/br021-deformable/tasks/deform-2d/tests/truth.json')
    target = np.array(truth['points_world_mm'])
    with np.load(ROOT / 'runs/br021-deformable/tasks/deform-2d/environment/data/volume.npz') as z:
        affine = z['voxel_to_world']
    # The frozen image uses diagonal voxel axes; compute exact box distances.
    assert np.allclose(affine[:3, :3], np.diag(np.diag(affine)[:3]))
    spacing = np.diag(affine)[:3]
    target_voxel = (target - affine[:3, 3]) / spacing
    public = ROOT / 'runs/br021-deformable/tasks/deform-2d/environment/data'
    frame = read(public / 'view.json')
    queries = read(public / 'queries.json')
    uv = np.array(queries['pixels_uv'][3]) * frame['spacing_xy_mm']
    world = np.einsum('ij,j->i', np.array(frame['slice_to_world']), np.r_[uv, 0, 1])
    nominal = np.einsum('ij,j->i', np.linalg.inv(affine), world)[:3]
    initial_lo = np.floor(nominal - [14, 18, 14]).astype(int)
    initial_hi = np.ceil(nominal + [14, 18, 14]).astype(int)
    later_lo = nominal + [-6, 3, -15]
    later_hi = nominal + [12, 25, 6]
    coarse_geometry = {
        'query': 'q04', 'nominal_voxel': nominal.tolist(), 'manual_target_voxel': target_voxel[3].tolist(),
        'initial_coarse_min_voxel': initial_lo.tolist(), 'initial_coarse_max_voxel': initial_hi.tolist(),
        'initial_coarse_target_inside': bool(np.all((target_voxel[3] >= initial_lo) & (target_voxel[3] <= initial_hi))),
        'initial_coarse_distance_to_box_mm': float(np.linalg.norm((target_voxel[3] - np.clip(target_voxel[3], initial_lo, initial_hi)) * spacing)),
        'later_coarse_min_voxel': later_lo.tolist(), 'later_coarse_max_voxel': later_hi.tolist(),
        'later_coarse_target_inside': bool(np.all((target_voxel[3] >= later_lo) & (target_voxel[3] <= later_hi))),
        'interpretation': 'Offline geometry from the recorded item_7/item_25 grids. The later motion-directed range admits the manual target and excludes the earlier raw winner; this does not isolate the necessity of neighborhood regression.'}
    rows = []
    for case in plan['conditions']:
        file = OUT / 'components' / case['name'] / 'points.json'
        answer = read(file)
        row = {**case, 'answer_path': str(file.relative_to(ROOT)), 'answer_sha256': sha(file),
               'grade': score(answer, truth), 'diagnostics': answer['diagnostics']}
        if case['name'] != 'no_final_refinement':
            initial = np.array([d['initial_voxel'] for d in answer['diagnostics']])
            nearest = np.clip(target_voxel, initial - 3, initial + 3)
            distances = np.linalg.norm((nearest - target_voxel) * spacing, axis=1)
            row['search_box_distance_mm'] = distances.tolist()
            row['search_box_best_possible_rms_mm'] = float(np.sqrt(np.mean(distances ** 2)))
            row['search_box_best_possible_max_mm'] = float(np.max(distances))
        rows.append(row)
    original_path = next((ROOT / 'runs/br023-deform-2d-sol-xhigh-v1-20260916').glob('*/artifacts/app/answer/points.json'))
    original = read(original_path)
    replay = read(OUT / 'components/final_stage_replay/points.json')
    drift = float(np.max(np.linalg.norm(np.array(original['points_world_mm']) - replay['points_world_mm'], axis=1)))
    assert drift == 0
    # The two reseeding interventions must alter q04 only.
    for name in ['early_selected_q04', 'raw_top_q04']:
        variant = read(OUT / f'components/{name}/points.json')
        for i in range(8):
            if i != 3:
                assert variant['points_world_mm'][i] == replay['points_world_mm'][i]
    # Regrade ALL already printed exploratory affine settings. These are
    # descriptive recorded stages, not matched single-component interventions.
    recorded = (OUT / 'recovered/item_16.txt').read_text()
    chunks = re.split(r'\n\s*(q\d\d)\s*\n', '\n' + recorded)
    by_lambda = {x: {} for x in ['0.05', '0.2', '1.0']}
    for i in range(1, len(chunks), 2):
        query, block = chunks[i:i+2]
        for match in re.finditer(r'lam\s+([\d.]+).*?world\s+\[([^\]]+)\]', block, re.S):
            by_lambda[match[1]][query] = [float(x) for x in match[2].split()]
    historical = []
    for strength, points in by_lambda.items():
        assert set(points) == set(truth['query_ids'])
        answer = {'query_ids': truth['query_ids'], 'points_world_mm': [points[k] for k in truth['query_ids']]}
        historical.append({'regularization': float(strength), 'grade': score(answer, truth),
                           'printed_world_points': answer['points_world_mm']})
    result = {
        'round': 'BR-023', 'component_plan_sha256': sha(OUT / 'component-plan.json'),
        'execution_sha256': sha(OUT / 'component-execution.json'),
        'original_answer_path': str(original_path.relative_to(ROOT)), 'original_answer_sha256': sha(original_path),
        'final_stage_replay_maximum_drift_mm': drift, 'conditions': rows,
        'coarse_search_geometry': coarse_geometry,
        'recorded_affine_exploration': {'source_output_path': 'runs/br023-sol-registration/recovered/item_16.txt',
                                       'source_output_sha256': sha(OUT / 'recovered/item_16.txt'), 'all_settings': historical,
                                       'interpretation': 'Different starts/context/objective from final stage; no isolated affine-model effect.'},
        'summary': 'Sol/xhigh passes at 1.56 mm RMS. Its neighborhood-informed q04 choice is decisive under the fixed final refinement; final multiscale polishing is not necessary once the correspondence region has been chosen.',
        'component_intro': 'Exact replay of the final numerical stage matches all eight submitted coordinates. Four fixed interventions change one setting at a time; the earlier visual and numerical work is retained in the starting points.',
        'finding': 'Changing only q04 to its raw top-correlation start produces 34.78 mm error; the earlier chosen start gives 11.03 mm. The neighborhood-informed start yields 1.29 mm. A single small patch and stopping before final refinement both still pass.',
        'limitations': [
            'Post-trace hypotheses on one selected case; no population estimate or controlled model ranking.',
            'Final-stage replay holds earlier semantic/visual decisions and public-derived starts fixed; it does not autonomously replay them.',
            'Reseeding q04 tests its conditional numerical effect, not the complete downstream behavior of an autonomous agent without neighborhood analysis.',
            'The resulting initialization reflects neighborhood regression, updated search bounds, patch scores and visual review; these tests do not separately isolate those upstream contributions.',
            'Single-patch and no-final-refinement results retain earlier multiscale searches, stability checks and refinements.',
            'Small RMS differences among passing variants do not establish a better general or clinical method; reference landmarks are discretized.',
            'Recorded affine exploration changes multiple factors and cannot isolate the causal effect of local affine parameters.',
        ],
    }
    for path in [OUT / 'component-analysis.json', ROOT / 'docs/evidence/br023-component-analysis.json']:
        path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'conditions': [{k: r[k] for k in ['name', 'grade']} for r in rows],
                      'recorded_affine': historical}, indent=2))


if __name__ == '__main__':
    main()
