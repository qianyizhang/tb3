"""Public-input-only global affine motion fit from four video planes.

This is a deliberately limited but coherent volumetric baseline. It has no
regional contraction model. Out-of-plane speckle motion is not observable by
ordinary 2D optical flow; score that limitation rather than claiming recovery.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    cv2.setNumThreads(1)
    for name, digest in json.loads((a.input/'manifest.json').read_text()).items():
        assert hashlib.sha256((a.input/name).read_bytes()).hexdigest() == digest
    geo = json.loads((a.input/'geometry.json').read_text())
    init = dict(np.load(a.input/'initial_mesh.npz'))
    X = init['points']; center = np.array(geo['initial_center'])
    observations, design = [], []
    counts = []
    for i, plane in enumerate(geo['planes']):
        u, v, origin = np.array(plane['u']), np.array(plane['v']), np.array(plane['origin'])
        normal = np.cross(u, v)
        eligible = np.abs(np.einsum('nj,j->n', X-origin, normal)) < 1.5
        ids = np.where(eligible)[0]
        pts = X[ids]
        pixels0 = np.stack([np.einsum('nj,j->n', pts-origin, ax)/geo['spacing_mm']+geo['pixel_center'] for ax in [u,v]], axis=1)
        good = np.all((pixels0 > 5)&(pixels0 < geo['image_size']-6), axis=1)
        pts, pixels0 = pts[good], pixels0[good]
        pixels = pixels0.copy()
        image0 = np.asarray(Image.open(a.input/f'view_{i}/frame_01.png'))
        trajectory = [pixels.copy()]
        dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        for t in range(1, geo['frames']):
            target = np.asarray(Image.open(a.input/f'view_{i}/frame_{t+1:02d}.png'))
            flow = dis.calc(image0, target, None)
            disp = np.stack([map_coordinates(flow[..., j], pixels[:, ::-1].T, order=1, mode='nearest') for j in range(2)], axis=1)
            pixels += disp
            trajectory.append(pixels.copy())
            image0 = target
        trajectory = (np.array(trajectory)-pixels0)*geo['spacing_mm']
        for j, ax in enumerate([u,v]):
            design.append(np.c_[np.einsum('i,nj->nij', ax, pts-center).reshape(-1,9), np.repeat(ax[None], len(pts), axis=0)])
            observations.append(trajectory[:,:,j])
        counts.append(len(pts))
    A = np.concatenate(design)
    Y = np.concatenate(observations, axis=1)
    parameters = np.linalg.lstsq(A, Y.T, rcond=None)[0].T
    gradients = parameters[:, :9].reshape(-1,3,3)+np.eye(3)
    offsets = parameters[:,9:]
    prediction = np.einsum('tij,nj->tni', gradients, X-center)+center+offsets[:,None]
    np.savez_compressed(a.output/'prediction.npz', points=prediction, affine_gradients=gradients, offsets=offsets)
    receipt = dict(kind='public_input_only_author_affine_video_baseline', sample_points_per_plane=counts,
                   public_manifest_sha256=hashlib.sha256((a.input/'manifest.json').read_bytes()).hexdigest(),
                   prediction_sha256=hashlib.sha256((a.output/'prediction.npz').read_bytes()).hexdigest(),
                   script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   opencv=cv2.__version__, method='Consecutive DIS medium; material seeds within 1.5 mm of four initial planes; linear least-squares affine fit',
                   design_rank=int(np.linalg.matrix_rank(A)), elapsed_seconds=time.perf_counter()-start)
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
