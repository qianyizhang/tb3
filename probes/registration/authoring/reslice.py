"""Public forward model. A supplied pose maps slice millimetres to patient LPS."""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image


def render(hu, voxel_to_lps, pose, shape, spacing=(1., 1.)):
    y, x = np.indices(shape, dtype=float)
    q = np.stack([x.ravel()*spacing[0], y.ravel()*spacing[1], np.zeros(x.size), np.ones(x.size)])
    index = np.einsum('ij,jn->in',np.linalg.inv(voxel_to_lps) @ np.asarray(pose),q)
    values = map_coordinates(hu.astype(np.float32), index[:3], order=1,
                             mode='constant', cval=-1024., prefilter=False).reshape(shape)
    return np.rint(np.clip((values+150.)/500., 0, 1)*255).astype(np.uint8)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', default='/app/data')
    p.add_argument('--pose', required=True); p.add_argument('--out', required=True)
    a = p.parse_args(); d = Path(a.data)
    with np.load(d/'volume.npz') as z: hu=z['hu']; affine=z['voxel_to_lps']
    geometry=json.loads((d/'image.json').read_text())
    pose=json.loads(Path(a.pose).read_text())['slice_to_lps']
    Image.fromarray(render(hu, affine, pose, geometry['shape'], geometry['spacing_xy_mm'])).save(a.out)
