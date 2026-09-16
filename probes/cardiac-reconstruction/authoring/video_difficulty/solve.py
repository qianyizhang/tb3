"""Image-based author baselines; reads ONLY one public-input directory.

DIS parameters are OpenCV's medium preset, without label-selected tuning.
Warp signed distance fields with target-to-source flow to avoid repeated
binary-mask interpolation. Temporal interpolation is an image-free control.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pilot import NPOLAR, NAZIMUTH, ray_profile, mesh, signed_volume


def signed_distance(mask):
    return (distance_transform_edt(mask) - distance_transform_edt(~mask)).astype('float32')


def profiles_from_masks(masks, angles, cx, cy):
    query = np.arange(NAZIMUTH) * 2 * np.pi / NAZIMUTH
    out = []
    for t in range(masks.shape[1]):
        values, aa = [], []
        for v, angle in enumerate(angles):
            for pos, shift in [(True, 0), (False, np.pi)]:
                values.append(ray_profile(masks[v, t], cx, cy, pos))
                aa.append(np.deg2rad(angle) + shift)
        order = np.argsort(aa)
        aa, values = np.asarray(aa)[order], np.asarray(values)[order]
        profile = np.stack([np.interp(query, aa, values[:, j], period=2 * np.pi) for j in range(NPOLAR)], axis=1)
        profile[:, 0], profile[:, -1] = values[:, 0].mean(), values[:, -1].mean()
        out.append(profile)
    return np.asarray(out)


def save_prediction(out, name, fields, geo):
    masks = fields > 0
    profiles = profiles_from_masks(masks, geo['view_angles_degrees'], geo['rotation_axis_x_px'], geo['origin_y_px'])
    ms = [mesh(p, geo['in_plane_spacing_mm']) for p in profiles]
    vertices, faces = np.array([m[0] for m in ms]), ms[0][1]
    volumes = np.array([signed_volume(v, faces) / 1000 for v in vertices])
    path = out / f'{name}-mesh.npz'
    np.savez_compressed(path, input_view_masks=masks, radius_px=profiles, vertices=vertices, faces=faces, volume_ml=volumes)
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'ef_percent': float(100 * (1 - volumes.min() / volumes.max())),
            'max_volume_frame_1based': int(volumes.argmax()) + 1,
            'min_volume_frame_1based': int(volumes.argmin()) + 1}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    cv2.setNumThreads(1)
    geo = json.loads((a.input / 'geometry.json').read_text())
    manifest = json.loads((a.input / 'manifest.json').read_text())
    for fn, digest in manifest.items():
        assert hashlib.sha256((a.input / fn).read_bytes()).hexdigest() == digest
    anchors = np.array(geo['anchor_frames_1based']) - 1
    frames, shape = geo['frame_count'], geo['shape_hw']
    yy, xx = np.indices(shape, dtype='float32')
    controls, tracked = [], []
    for v in range(4):
        images = [np.asarray(Image.open(a.input / f'video/view_{v:02d}/frame_{t+1:03d}.png').convert('L')) for t in range(frames)]
        seeds = [signed_distance(np.asarray(Image.open(a.input / f'anchors/view_{v:02d}/frame_{t+1:03d}.png')) > 0) for t in anchors]
        dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        # flow(target, source) provides the remapping coordinates in source.
        to_previous = [None] + [dis.calc(images[t], images[t-1], None) for t in range(1, frames)]
        to_next = [dis.calc(images[t], images[t+1], None) for t in range(frames-1)] + [None]
        trajectories = []
        for anchor, seed in zip(anchors, seeds):
            fields = np.empty((frames, *shape), dtype='float32')
            fields[anchor] = seed
            for t in range(anchor + 1, frames):
                f = to_previous[t]
                fields[t] = cv2.remap(fields[t-1], xx+f[..., 0], yy+f[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            for t in range(anchor - 1, -1, -1):
                f = to_next[t]
                fields[t] = cv2.remap(fields[t+1], xx+f[..., 0], yy+f[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            trajectories.append(fields)
        control, tracking = [], []
        for t in range(frames):
            w = float(np.clip((t - anchors[0]) / (anchors[-1] - anchors[0]), 0, 1)) if len(anchors) > 1 else 0
            control.append((1-w)*seeds[0] + w*seeds[-1])
            tracking.append((1-w)*trajectories[0][t] + w*trajectories[-1][t])
        controls.append(control)
        tracked.append(tracking)
        print('tracked view', v, flush=True)
    result = {'kind': 'public_input_author_baseline_not_model_trial',
              'input_manifest_sha256': hashlib.sha256((a.input / 'manifest.json').read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'anchors_1based': (anchors+1).tolist(), 'opencv': cv2.__version__,
              'flow': 'DIS medium preset; consecutive target-to-source backward warp; signed-distance fields',
              'predictions': {}}
    result['predictions']['control'] = save_prediction(a.output, 'control', np.asarray(controls), geo)
    result['predictions']['dis'] = save_prediction(a.output, 'dis', np.asarray(tracked), geo)
    result['elapsed_seconds'] = time.perf_counter() - start
    (a.output / 'solver-receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
