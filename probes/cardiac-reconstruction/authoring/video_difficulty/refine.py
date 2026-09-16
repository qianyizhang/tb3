"""Development-informed image refinement of the frozen one-anchor DIS output.

No source labels are read here. Constants were recorded after inspecting the
first screen, so this is author development, not a blind test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, binary_fill_holes, label

from solve import save_prediction


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--prediction', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    cv2.setNumThreads(1)
    cv2.setRNGSeed(27)
    geo = json.loads((a.input / 'geometry.json').read_text())
    pred = np.load(a.prediction)['input_view_masks']
    masks = pred.copy()
    for v in range(4):
        for t in range(geo['frame_count']):
            if t + 1 in geo['anchor_frames_1based']:
                continue
            mask = pred[v, t]
            iy, ix = np.where(mask)
            ys = slice(max(0, iy.min()-20), min(mask.shape[0], iy.max()+21))
            xs = slice(max(0, ix.min()-20), min(mask.shape[1], ix.max()+21))
            image = np.array(Image.open(a.input / f'video/view_{v:02d}/frame_{t+1:03d}.png').convert('RGB'))[ys, xs].copy()
            m = mask[ys, xs]
            inside, outside = distance_transform_edt(m), distance_transform_edt(~m)
            seed = inside > .6 * inside.max()
            init = np.full(m.shape, cv2.GC_PR_BGD, dtype='uint8')
            init[m] = cv2.GC_PR_FGD
            init[outside > 15] = cv2.GC_BGD
            init[seed] = cv2.GC_FGD
            cv2.grabCut(image, init, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK)
            foreground = (init == cv2.GC_FGD) | (init == cv2.GC_PR_FGD)
            labels, _ = label(foreground)
            counts = np.bincount(labels[seed])
            counts[0] = 0
            component = binary_fill_holes(labels == counts.argmax())
            masks[v, t] = False
            masks[v, t, ys, xs] = component
        print('refined view', v, flush=True)
    receipt = dict(kind='development_informed_public_input_author_method',
                   script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   input_manifest_sha256=hashlib.sha256((a.input / 'manifest.json').read_bytes()).hexdigest(),
                   prior_prediction_sha256=hashlib.sha256(a.prediction.read_bytes()).hexdigest(),
                   parameters=dict(seed_fraction=.6, exterior_band_px=15, crop_padding_px=20, iterations=5, rng_seed=27),
                   prediction=save_prediction(a.output, 'refined', masks.astype('float32')-.5, geo),
                   elapsed_seconds=time.perf_counter()-start)
    (a.output / 'solver-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
