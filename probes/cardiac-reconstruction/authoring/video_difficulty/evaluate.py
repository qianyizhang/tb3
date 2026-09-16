"""Private author evaluation. Predictions must already exist and match receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.ndimage import binary_erosion, distance_transform_edt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pilot import HOLDOUT, VIEWS, read_mask, reconstruct, render_mask, mesh, signed_volume, dice, summary


def topology(vertices, faces, volumes):
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    areas = np.linalg.norm(np.cross(vertices[:, faces[:, 1]] - vertices[:, faces[:, 0]],
                                   vertices[:, faces[:, 2]] - vertices[:, faces[:, 0]]), axis=-1)/2
    return dict(boundary_edges=int((counts == 1).sum()), nonmanifold_edges=int((counts > 2).sum()),
                degenerate_triangles=int((areas < 1e-10).sum()), positive_volumes=bool(np.all(volumes > 0)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--extra', type=Path, help='Optional frozen stronger-method NPZ')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    geo = json.loads((a.run / 'public/one_anchor/geometry.json').read_text())
    cx, cy, spacing = geo['rotation_axis_x_px'], geo['origin_y_px'], geo['in_plane_spacing_mm']
    frames, shape = geo['frame_count'], geo['shape_hw']
    predictions, receipts = {}, {}
    for condition, prefix in [('one-anchor-v1', 'one'), ('two-anchors-v1', 'two')]:
        receipt = json.loads((a.run / condition / 'solver-receipt.json').read_text())
        receipts[condition] = receipt
        for method, info in receipt['predictions'].items():
            path = a.run / condition / f'{method}-mesh.npz'
            assert hashlib.sha256(path.read_bytes()).hexdigest() == info['sha256']
            predictions[f'{prefix}_{method}'] = dict(np.load(path))
    if a.extra:
        predictions['one_refined'] = dict(np.load(a.extra))
        receipts['extra'] = {'sha256': hashlib.sha256(a.extra.read_bytes()).hexdigest(), 'path': str(a.extra)}
    # Every prediction was serialized and hashed before accessing private labels.
    for name, views in [('clean', VIEWS['four']), ('dense', VIEWS['dense'])]:
        profiles = reconstruct(a.source, frames, views, cx, cy)
        ms = [mesh(p, spacing) for p in profiles]
        vertices, faces = np.array([m[0] for m in ms]), ms[0][1]
        volumes = np.array([signed_volume(v, faces)/1000 for v in vertices])
        predictions[name] = dict(radius_px=profiles, vertices=vertices, faces=faces, volume_ml=volumes)
        np.savez_compressed(a.output / f'{name}-mesh.npz', **predictions[name])
    reference = predictions['dense']['volume_ml']
    refef = float(100*(1-reference.min()/reference.max()))
    stats, curves = {}, {}
    for name, pred in predictions.items():
        curves[name] = pred['volume_ml'].tolist()
        dd, hh, observed = [], [], []
        anchors = [1, 16] if name.startswith('two_') else [1]
        for t in range(frames):
            for view in HOLDOUT:
                truth = read_mask(a.source, view, t)
                section = render_mask(pred['radius_px'][t], view, shape, cx, cy)
                dd.append(dice(truth, section))
                ta, pa = truth ^ binary_erosion(truth), section ^ binary_erosion(section)
                distances = np.r_[distance_transform_edt(~ta)[pa], distance_transform_edt(~pa)[ta]] * spacing
                hh.append(float(np.quantile(distances, .95)))
            if 'input_view_masks' in pred and t not in anchors:
                for i, v in enumerate(VIEWS['four']):
                    observed.append(dice(read_mask(a.source, v, t), pred['input_view_masks'][i, t]))
        volumes = pred['volume_ml']
        ef = float(100*(1-volumes.min()/volumes.max()))
        topo = topology(pred['vertices'], pred['faces'], volumes)
        stats[name] = dict(heldout_dice=summary(dd), heldout_hd95_mm=summary(hh),
                           unsupplied_input_frame_dice=summary(observed) if observed else None,
                           unsupplied_input_frame_count=len(observed), ef_percent=ef,
                           ef_error_vs_dense_reference_pp=abs(ef-refef),
                           volume_curve_mape_vs_dense_percent=float(100*np.mean(abs(volumes/reference-1))),
                           max_volume_frame_1based=int(volumes.argmax())+1,
                           min_volume_frame_1based=int(volumes.argmin())+1,
                           min_volume_ml=float(volumes.min()), max_volume_ml=float(volumes.max()), topology=topo)
        s = stats[name]
        s['gates'] = dict(dice=s['heldout_dice']['mean'] >= .9,
                          hd95=s['heldout_hd95_mm']['mean'] <= 1,
                          volume=s['volume_curve_mape_vs_dense_percent'] <= 10,
                          ef=s['ef_error_vs_dense_reference_pp'] <= 5,
                          topology=topo['positive_volumes'] and not any(topo[k] for k in ['boundary_edges', 'nonmanifold_edges', 'degenerate_triangles']))
        s['pass'] = all(s['gates'].values())
        print(name, 'Dice', round(s['heldout_dice']['mean'], 4), 'HD95', round(s['heldout_hd95_mm']['mean'], 3),
              'volume', round(s['volume_curve_mape_vs_dense_percent'], 2), 'EFerror', round(s['ef_error_vs_dense_reference_pp'], 2), s['gates'], flush=True)
    result = dict(kind='author_development_screen_not_model_trial', geometry=geo, frames=frames,
                  source_record='https://zenodo.org/records/21322299', source_patient='Patient001',
                  heldout_planes_1based=[v+1 for v in HOLDOUT], derived_reference_is_independent_3d_truth=False,
                  ef_definition='100*(1-min(V)/max(V)); no source clinical phase-index assumption',
                  receipts=receipts, stats=stats,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), elapsed_seconds=time.perf_counter()-start)
    (a.output / 'results.json').write_text(json.dumps(result, indent=2)+'\n')
    (a.output / 'curves.json').write_text(json.dumps(curves)+'\n')


if __name__ == '__main__':
    main()
