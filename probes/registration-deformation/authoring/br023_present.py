"""Local review of Sol, historical Terra attempts, and fixed component tests."""
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from present import png
from score import score

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br023-sol-registration'


def read(path):
    return json.loads(path.read_text())


def main():
    receipt = read(OUT / 'results.json')
    analysis = read(OUT / 'component-analysis.json')
    public = ROOT / 'runs/br021-deformable/tasks/deform-2d/environment/data'
    truth = read(ROOT / 'runs/br021-deformable/tasks/deform-2d/tests/truth.json')
    queries = read(public / 'queries.json')
    frame = read(public / 'view.json')
    view = np.load(public / 'view.npy')
    basis = np.array(frame['slice_to_world'])[:3, :2]
    with np.load(public / 'volume.npz') as z:
        volume, affine = z['hu'], z['voxel_to_world']
    yy, xx = np.mgrid[-48:49, -48:49]
    offsets = np.array([xx.ravel(), yy.ravel()]) * .65

    def destination(point):
        world = np.array(point)[:, None] + np.einsum('ij,jn->in', basis, offsets)
        ijk = np.einsum('ij,jn->in', np.linalg.inv(affine[:3, :3]), world - affine[:3, 3, None])
        assert np.all(np.isfinite(ijk))
        patch = map_coordinates(volume, ijk, order=1, prefilter=False, mode='constant', cval=-1000)
        return png(patch.reshape(97, 97))

    data = {'ids': truth['query_ids'], 'source': [],
            'manual': [destination(p) for p in truth['points_world_mm']],
            'methods': {}, 'analysis': analysis}
    for pixel in queries['pixels_uv']:
        coords = np.array(pixel)[:, None] + offsets / np.array(frame['spacing_xy_mm'])[:, None]
        patch = map_coordinates(view, coords[::-1], order=1, prefilter=False, mode='constant', cval=-1000)
        data['source'].append(png(patch.reshape(97, 97)))
    sol = next(r for r in receipt['prospective_rows'] if r['phase'] == 'sol-xhigh')
    rows = [('Sol / xhigh', sol), ('Terra / original selected miss', receipt['retrospective_selected_attempt'])]
    rows += [(f"Terra / repeat {r['phase'][-1]}", r) for r in receipt['historical_terra_replications']]
    for name, row in rows:
        answer = read(ROOT / row['answer_path'])
        data['methods'][name] = {'grade': score(answer, truth), 'seconds': row['agent_seconds'],
                                 'images': [destination(p) for p in answer['points_world_mm']]}
    for row in analysis['conditions']:
        answer = read(ROOT / row['answer_path'])
        data['methods']['Component test / ' + row['label']] = {
            'grade': row['grade'], 'seconds': None,
            'images': [destination(p) for p in answer['points_world_mm']]}
    template = Path(__file__).with_name('br023_review.html').read_text()
    dest = OUT / 'review'
    dest.mkdir(exist_ok=True)
    (dest / 'index.html').write_text(template.replace('__DATA__', json.dumps(data).replace('</', '<\\/')))
    print(dest / 'index.html')


if __name__ == '__main__':
    main()
