"""Build a local interactive postmortem using real CT pixels and retained results."""
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from present import png
from score import score

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br022-registration-postmortem'


def read(path):
    return json.loads(path.read_text())


def main():
    results = read(OUT / 'results.json')
    analysis = read(OUT / 'solver-analysis.json')
    source = ROOT / 'runs/br021-deformable/author'
    truth = read(source / 'truth.json')
    queries = read(source / 'public-2d/queries.json')
    frame = read(source / 'public-2d/view.json')
    view = np.load(source / 'public-2d/view.npy')
    basis = np.array(frame['slice_to_world'])[:3, :2]
    with np.load(source / 'public-2d/volume.npz') as z:
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
    rows = [('Original selected miss', results['retrospective_selected_attempt'])]
    rows += [(f"Fresh attempt {row['phase'][-1]}", row) for row in results['prospective_rows'] if row['phase'].startswith('terra')]
    for name, row in rows:
        answer = read(ROOT / row['answer_path'])
        data['methods'][name] = {'grade': score(answer, truth), 'seconds': row['agent_seconds'],
                                 'images': [destination(p) for p in answer['points_world_mm']]}
    baseline = read(OUT / 'ablations/translation-multiscale.json')
    data['methods']['Author · translation + larger context'] = {
        'grade': score(baseline, truth), 'seconds': None,
        'images': [destination(p) for p in baseline['points_world_mm']]}
    template = Path(__file__).with_name('br022_review.html').read_text()
    review = OUT / 'review'
    review.mkdir(exist_ok=True)
    (review / 'index.html').write_text(template.replace('__DATA__', json.dumps(data).replace('</', '<\\/')))
    print(review / 'index.html')


if __name__ == '__main__':
    main()
