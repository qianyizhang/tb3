#!/usr/bin/env python3
"""Render portable BR-016 teaching figures from retained native arrays.

Requires NumPy and Pillow (the existing .venv-br003 environment). This is an
explicit presentation build, separate from build_site.py and all trial tools.
Source arrays are read-only; all crop/window parameters and hashes are retained.
"""
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'runs/br016-aneurysm/blind-review'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def render():
    manifest = json.loads((SOURCE / 'manifest.json').read_text())
    references = json.loads((SOURCE / 'references.json').read_text())
    cases = {}
    for name, source_id, preferred in [('n01', 'R02', 1), ('n02', 'R03', 2), ('n03', 'R01', 2)]:
        entry = next(c for c in manifest['cases'] if c['id'] == source_id)
        shape, spacing = entry['shape'], entry['spacing_mm']
        refs = references[source_id]
        center = [int(x) for x in refs[0]['center']] if refs else [n // 2 for n in shape]
        high = refs[0]['display_high'] if refs else entry['display_high']
        path = SOURCE / source_id / 'brain.bin'
        volume = np.memmap(path, dtype='<f4', mode='r', shape=tuple(shape))
        # Positive cases show a 48 mm field around the coarse reference centre.
        # The negative case is a whole-field context view, with no lesion marker.
        width = [min(n, round(48 / s)) for n, s in zip(shape, spacing)] if refs else shape
        offset = [max(0, min(n - w, c - w // 2)) for n, w, c in zip(shape, width, center)]
        planes = []
        for axis in range(3):
            remaining = [d for d in range(3) if d != axis]
            slices = [slice(o, o + w) for o, w in zip(offset, width)]
            # Seven-slice maximum-brightness projection, centred at the reference.
            lo, hi = max(0, center[axis] - 3), min(shape[axis], center[axis] + 4)
            slices[axis] = slice(lo, hi)
            pixels = volume[tuple(slices)].max(axis=axis).T[::-1]
            grayscale = np.clip(np.rint(pixels / high * 255), 0, 255).astype('uint8')
            buffer = io.BytesIO()
            Image.fromarray(grayscale).save(buffer, format='PNG')
            planes.append({
                'axis': axis, 'slice': center[axis], 'range': [lo, hi - 1],
                'offset': [offset[d] for d in remaining],
                'width': int(grayscale.shape[1]), 'height': int(grayscale.shape[0]),
                'aspect': grayscale.shape[1] * spacing[remaining[0]] / (grayscale.shape[0] * spacing[remaining[1]]),
                'image': 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode(),
            })
        cases[name] = {
            'source_id': source_id, 'shape': shape, 'spacing': spacing,
            'center': center, 'high': high, 'default_axis': preferred,
            'reference': refs[0] if refs else None,
            'answer': [312, 213, 94] if name == 'n02' else None,
            'planes': planes,
            'source': {'path': str(path.relative_to(ROOT)), 'sha256': digest(path)},
        }
    output = {'description': 'Native-grid, seven-slice brightness projections. Display crops and windows only; no source voxels edited.',
              'reference_source': {'path': str((SOURCE / 'references.json').relative_to(ROOT)), 'sha256': digest(SOURCE / 'references.json')},
              'cases': cases}
    (ROOT / 'site/aneurysm-figures.json').write_text(json.dumps(output, indent=2) + '\n')
    print('Rendered nine native-grid views; source arrays unchanged.')


if __name__ == '__main__':
    render()
