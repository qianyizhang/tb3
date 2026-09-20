#!/usr/bin/env python3
"""Derive the BR-016 tour from retained native arrays, weak labels and answers."""
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'presentation/tours/data'
BASE = 'runs/br016-aneurysm'
sources = {}


def source(path):
    p = ROOT / path
    sources[str(path)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return p


def read(path):
    return json.loads(source(path).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, separators=(',', ':')) + '\n')


def main():
    ledger = read('docs/evidence/br016-results.json')
    refs = read(BASE + '/blind-review/references.json')
    cases, images = {}, []
    for name, subject, review in [('N02', '022', 'R03'), ('N01', '013', 'R02'), ('N03', '000', 'R01')]:
        task = 'aneurysm-' + name.lower()
        meta = read(f'{BASE}/build/{task}/volume.json')
        volume = np.load(source(f'{BASE}/build/{task}/brain.npz'))['volume']
        row = next(r for r in ledger['rows'] if r['task'] == task + '-v2' and r['phase'] == 'sol-xhigh')
        answer = read(row['answer_path'])
        assert answer == row['answer']
        expected = read(f'{BASE}/tasks/{task}-v2/tests/expected.json')
        spacing = np.array(meta['spacing_mm'])
        case = {'shape': list(volume.shape), 'spacing': spacing.tolist(), 'answer': answer['aneurysms'],
                'grade': row['grade'], 'source_assisted': row['annotation_inventory_exposed'],
                'agent_seconds': row['agent_seconds'], 'planes': []}
        def image(a, suffix, high):
            filename = f'aneurysm-{name.lower()}-{suffix}.png'
            gray = np.uint8(np.clip(a / high, 0, 1) * 255)
            Image.fromarray(np.flipud(gray.T)).save(OUT / filename)
            images.append(filename)
            return filename
        case['overview'] = image(volume.max(axis=2), 'overview', meta['display_high'])
        case['overview_aspect'] = volume.shape[0] * spacing[0] / (volume.shape[1] * spacing[1])
        if refs[review]:
            center = np.array(refs[review][0]['center'], dtype=int)
            label_path = next((ROOT / BASE / 'source').glob(f'sub-{subject}*Lesion*nii.gz'))
            label = np.asanyarray(nib.load(source(str(label_path.relative_to(ROOT)))).dataobj) > 0
            assert label.shape == volume.shape
            assert np.allclose(np.argwhere(label).mean(axis=0), center)
            # Keep the original weak mask distinct from the verifier's tolerance region.
            mask_coords = np.argwhere(label)
            case['reference_center'] = center.tolist()
            case['reference_voxels'] = len(mask_coords)
            case['reference_extent_mm'] = ((np.ptp(mask_coords, axis=0) + 1) * spacing).tolist()
            case['accepted_prediction'] = bool(answer['aneurysms']) and ','.join(map(str, answer['aneurysms'][0])) in expected['regions'][0]['accepted_voxels']
            # Native crops, approximately 32 mm wide, without image interpolation.
            half = np.ceil(16 / spacing).astype(int)
            low, high = np.maximum(0, center - half), np.minimum(volume.shape, center + half + 1)
            case['crop_bounds'] = [low.tolist(), high.tolist()]
            for axis in range(3):
                axes = [a for a in range(3) if a != axis]
                frames = []
                for index in range(int(center[axis] - 12), int(center[axis] + 13)):
                    slices = [slice(int(low[a]), int(high[a])) for a in range(3)]
                    slices[axis] = index
                    plane = volume[tuple(slices)]
                    mask = label[tuple(slices)]
                    im = image(plane, f'{axis}-{index}', refs[review][0]['display_high'])
                    overlay = np.zeros((*mask.T.shape, 4), dtype=np.uint8)
                    overlay[mask.T] = [255, 209, 118, 100]
                    overlay_name = f'aneurysm-{name.lower()}-{axis}-{index}-mask.png'
                    Image.fromarray(np.flipud(overlay)).save(OUT / overlay_name)
                    images.append(overlay_name)
                    frames.append({'index': index, 'image': im, 'mask': overlay_name, 'mask_voxels': int(mask.sum())})
                point = answer['aneurysms'][0] if answer['aneurysms'] else None
                case['planes'].append({'axis': axis, 'axes': axes, 'frames': frames,
                    'aspect': plane.shape[0] * spacing[axes[0]] / (plane.shape[1] * spacing[axes[1]]),
                    'point_uv': [(point[axes[0]] - low[axes[0]] + .5) / plane.shape[0], 1 - (point[axes[1]] - low[axes[1]] + .5) / plane.shape[1]] if point else None})
        cases[name] = case
    save('aneurysm.json', {'cases': cases, 'image_files': images,
        'description': 'Native RAS-grid slices: horizontal axis increases rightward, vertical axis upward. Weak source masks, not exact lesion boundaries. Whole-volume maximum projections are explicitly labeled.'})
    prov = json.loads((OUT / 'provenance.json').read_text())
    prov['sources'].update(sources)
    prov['aneurysm_derivation_script'] = 'scripts/prepare_med_tours_aneurysm.py'
    prov['outputs'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'provenance.json'}
    save('provenance.json', prov)
    print(f'Aneurysm: {len(images)} images; {len(sources)} source receipts; native slices and original weak masks.')


if __name__ == '__main__':
    main()
