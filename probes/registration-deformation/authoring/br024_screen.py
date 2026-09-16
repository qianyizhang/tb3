"""Fixed geometric curation on two unused real, manually annotated patients."""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import nibabel as nib
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from geometry import errors, rigid_fit, affine_fit

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br024-harder-registration'
SOURCE = ROOT / 'runs/br021-deformable/source'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def window(value):
    return np.rint(np.clip((value + 1000) / 1200, 0, 1) * 255).astype('uint8')


def main():
    plan = json.loads((OUT / 'plan.json').read_text())
    receipt = json.loads((SOURCE / 'source-receipt.json').read_text())
    for item in receipt['files']:
        assert hashlib.sha256((SOURCE / item['member']).read_bytes()).hexdigest() == item['sha256']
    destination = OUT / 'candidates'
    destination.mkdir(exist_ok=False)
    all_cases = []
    for case in plan['source_cases']:
        images = [nib.load(SOURCE / f'LungCT/imagesTr/LungCT_{case:04d}_{p:04d}.nii.gz') for p in [0, 1]]
        assert np.array_equal(images[0].affine, images[1].affine)
        a = images[0].affine
        hu = [np.asarray(im.dataobj).astype('float32') for im in images]
        indices = [np.loadtxt(SOURCE / f'LungCT/landmarksTr/LungCT_{case:04d}_{p:04d}.csv', delimiter=',') for p in [0, 1]]
        x, y = [np.einsum('ij,nj->ni', a[:3, :3], q) + a[:3, 3] for q in indices]
        triples = np.array(list(itertools.combinations(range(len(x)), 3)))
        normals = np.cross(x[triples[:, 1]] - x[triples[:, 0]], x[triples[:, 2]] - x[triples[:, 0]])
        length = np.linalg.norm(normals, axis=1)
        good = (length > 1500) & (np.max(np.abs(normals), axis=1) < .965 * length)
        triples, normals = triples[good], normals[good] / length[good, None]
        groups = {}
        for start in range(0, len(triples), 1024):
            n, tri = normals[start:start+1024], triples[start:start+1024]
            dist = np.abs(np.einsum('ni,mi->nm', n, x) - np.einsum('ni,ni->n', n, x[tri[:, 0]])[:, None])
            for local in np.flatnonzero(np.sum(dist <= .35, axis=1) >= 8):
                ids = tuple(np.flatnonzero(dist[local] <= .35).tolist())
                groups.setdefault(ids, (tri[local], n[local]))
        candidates, seen = [], set()
        for group, (tri, n0) in groups.items():
            chosen = [group[0]]
            while len(chosen) < 8:
                remaining = [i for i in group if i not in chosen]
                scores = [(min(np.linalg.norm(x[i] - x[j]) for j in chosen), -i, i) for i in remaining]
                chosen.append(max(scores)[2])
            ids = np.array(sorted(chosen))
            key = tuple(ids.tolist())
            if key in seen:
                continue
            p, n = x[tri[0]], n0.copy()
            if n[1] < 0:
                n = -n
            u = np.array([1., 0, 0]); u -= n * np.dot(u, n); u /= np.linalg.norm(u)
            v = np.cross(n, u)
            xy = np.column_stack([np.einsum('ni,i->n', x[ids] - p, u), np.einsum('ni,i->n', x[ids] - p, v)])
            span = np.ptp(xy, axis=0)
            if min(span) < 70:
                continue
            projected = p + np.outer(xy[:, 0], u) + np.outer(xy[:, 1], v)
            rigid, affine = errors(rigid_fit(projected, y[ids]), y[ids]), errors(affine_fit(projected, y[ids]), y[ids])
            if affine['rms_mm'] <= 3.5963:
                continue
            spacing, lo = 1.25, xy.min(0) - 16
            size = np.ceil((span + 32) / spacing).astype(int) + 1
            origin = p + lo[0] * u + lo[1] * v
            corners = np.array([origin + xx * spacing * u + yy * spacing * v for xx in [0, size[0]-1] for yy in [0, size[1]-1]])
            vox = np.einsum('ij,nj->ni', np.linalg.inv(a[:3, :3]), corners - a[:3, 3])
            if not (np.all(vox >= 0) and np.all(vox <= np.array(hu[0].shape)-1)):
                continue
            seen.add(key)
            candidates.append({'indices': ids, 'u': u, 'v': v, 'n': n, 'origin': origin, 'size': size,
                               'uv': (xy-lo)/spacing, 'rigid': rigid, 'affine': affine,
                               'projected': projected, 'area': float(np.prod(span))})
        candidates.sort(key=lambda c: (-c['affine']['rms_mm'], -c['area'], tuple(c['indices'])))
        records = []
        for rank, c in enumerate(candidates[:plan['max_candidates_per_patient']], 1):
            name = f'patient{case}-view{rank}'
            folder = destination / name; public = folder / 'public'; public.mkdir(parents=True)
            ids, u, v, n, origin, size = [c[k] for k in ['indices', 'u', 'v', 'n', 'origin', 'size']]
            pose = np.eye(4); pose[:3, :3] = np.column_stack([u, v, n]); pose[:3, 3] = origin
            yy, xx = np.indices((int(size[1]), int(size[0])))
            world = origin[:, None] + u[:, None]*xx.ravel()*1.25 + v[:, None]*yy.ravel()*1.25
            vox = np.einsum('ij,jn->in', np.linalg.inv(a[:3, :3]), world - a[:3, 3, None])
            view = map_coordinates(hu[0], vox, order=1, prefilter=False).reshape(yy.shape).astype('float32')
            np.savez_compressed(public / 'volume.npz', hu=hu[1], voxel_to_world=a)
            np.save(public / 'view.npy', view, allow_pickle=False)
            Image.fromarray(window(view)).save(public / 'view.png')
            write(public / 'view.json', {'shape': list(view.shape), 'spacing_xy_mm': [1.25, 1.25],
                  'slice_to_world': pose.tolist(), 'phase': 'exhale',
                  'description': 'Nominal exhale acquisition geometry, not the anatomical mapping into inhale.'})
            queries = {'query_ids': [f'q{i+1:02d}' for i in range(8)], 'pixels_uv': c['uv'].tolist()}
            write(public / 'queries.json', queries)
            truth = {'query_ids': queries['query_ids'], 'points_world_mm': y[ids].tolist(),
                     'rms_tolerance_mm': 3., 'max_tolerance_mm': 5.}
            write(folder / 'truth.json', truth)
            row = {'name': name, 'case': case, 'rank': rank, 'source_indices': ids.tolist(),
                   'shape': list(view.shape), 'best_rigid': c['rigid'], 'best_affine': c['affine'],
                   'identity': errors(c['projected'], y[ids]),
                   'off_plane_mm': np.linalg.norm(c['projected'] - x[ids], axis=1).tolist(),
                   'public_path': str(public.relative_to(ROOT)), 'truth_path': str((folder/'truth.json').relative_to(ROOT))}
            write(folder / 'preparation.json', row); records.append(row)
            marked = Image.fromarray(window(view)).convert('RGB').resize((view.shape[1]*3, view.shape[0]*3))
            draw = ImageDraw.Draw(marked)
            for i, (px, py) in enumerate(c['uv']*3):
                draw.ellipse((px-7, py-7, px+7, py+7), outline='#ff8058', width=2)
                draw.text((px+9, py-8), str(i+1), fill='#ffff88')
            marked.save(folder / 'view-marked.png')
        all_cases.append({'case': case, 'near_coplanar_groups': len(groups), 'eligible_distinct_query_sets': len(candidates), 'candidates': records})
    result = {'round': 'BR-024', 'plan_sha256': hashlib.sha256((OUT/'plan.json').read_bytes()).hexdigest(),
              'source_hashes_verified': True, 'cases': all_cases}
    write(OUT / 'screen.json', result); write(ROOT / 'docs/evidence/br024-screen.json', result)
    print(json.dumps([{'case': r['case'], 'groups': r['near_coplanar_groups'], 'eligible': r['eligible_distinct_query_sets'],
                      'candidates': [{'name': c['name'], 'affine_rms': c['best_affine']['rms_mm'], 'shape': c['shape']} for c in r['candidates']]} for r in all_cases], indent=2))


if __name__ == '__main__':
    main()
