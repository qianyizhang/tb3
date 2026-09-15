"""Build reviewable, unfrozen absorption scenes from original case-28 voxels."""
import json
import shutil
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import ROOT, OUT, sha, write
sys.path.insert(0, str(ROOT / 'probes/revisions/br013/authoring'))
from build import surface
from inspect_scene import load_scene, render
sys.path.insert(0, str(ROOT / 'probes/revisions/br014/authoring'))
from screen_fragments import components, export_piece
sys.path.insert(0, str(Path(__file__).parent))
from inspect_ct import bounds, render_slice, contact_sheet, PLANES

LABELS = ['spleen', 'kidney_right', 'kidney_left', 'gallbladder', 'liver',
          'stomach', 'pancreas', 'adrenal_gland_right', 'adrenal_gland_left',
          'duodenum', 'aorta', 'inferior_vena_cava', 'portal_vein_and_splenic_vein']


def world(p, a):
    return np.sum(np.asarray(p)[..., None, :] * a[:3, :3], axis=-1) + a[:3, 3]


def cropped_components(mask):
    p = np.argwhere(mask); lo = p.min(0); hi = p.max(0) + 1
    return [len(x) for x in components(mask[tuple(slice(x, y) for x, y in zip(lo, hi))])]


def representative(mask, a):
    p = np.argwhere(mask); lo = p.min(0); hi = p.max(0) + 1
    m = np.pad(mask[tuple(slice(x, y) for x, y in zip(lo, hi))], 1)
    depth = 0
    while True:
        inner = np.zeros_like(m)
        inner[1:-1, 1:-1, 1:-1] = (m[1:-1, 1:-1, 1:-1] & m[:-2, 1:-1, 1:-1] &
            m[2:, 1:-1, 1:-1] & m[1:-1, :-2, 1:-1] & m[1:-1, 2:, 1:-1] &
            m[1:-1, 1:-1, :-2] & m[1:-1, 1:-1, 2:])
        if not inner.any():
            q = np.argwhere(m); chosen = q[len(q) // 2] + lo - 1
            return world(chosen, a).tolist(), depth
        m = inner; depth += 1


def main():
    assert not (OUT / 'author/screen.json').exists(), 'Do not overwrite a completed screen'
    source = ROOT / 'runs/br004-v1/source/s1233'
    source_hashes = {}
    masks = {}
    im = nib.load(source / 'ct.nii.gz'); ct = np.asarray(im.dataobj)
    a = np.diag([-1., -1., 1., 1.]) @ im.affine
    assert ct.dtype == np.int16
    receipt = json.loads((source / 'source-receipt.json').read_text())
    available = {Path(x['member']).name: x['sha256'] for x in receipt['files']}
    for label in LABELS:
        path = source / 'segmentations' / f'{label}.nii.gz'
        source_hashes[label] = sha(path)
        assert source_hashes[label] == available[path.name]
        image = nib.load(path)
        assert np.array_equal(image.affine, im.affine) and image.shape == im.shape
        masks[label] = np.asarray(image.dataobj, dtype=bool)
    assert sha(source / 'ct.nii.gz') == available['ct.nii.gz']
    spacing = np.linalg.norm(a[:3, :3], axis=0)
    ml = abs(np.linalg.det(a[:3, :3])) / 1000
    pancreas, duodenum = masks['pancreas'], masks['duodenum']
    eligible = pancreas & ~duodenum
    p = np.argwhere(eligible).astype(np.float32)
    q = surface(duodenum).astype(np.float32)
    distances = np.empty(len(p), dtype=np.float32)
    for start in range(0, len(p), 128):
        d = (p[start:start + 128, None, :] - q[None, :, :]) * spacing
        distances[start:start + 128] = np.sqrt(np.sum(d * d, axis=2).min(axis=1))
    threshold = float(np.quantile(distances, .35))
    partial = np.zeros_like(pancreas)
    partial[tuple(p[distances <= threshold].astype(int).T)] = True
    comp = cropped_components(partial)
    assert partial.sum() * ml >= 15 and (pancreas & ~partial).sum() * ml >= 25
    assert comp[0] / sum(comp) >= .95, 'Reject fragmented distance region'
    rng = np.random.default_rng(1701)
    order = rng.permutation(LABELS).tolist()
    codes = rng.choice(np.arange(100, 1000), len(order), replace=False)
    ids = dict(zip(order, [f'o{x}' for x in codes]))
    records = []
    original_union = np.logical_or.reduce(list(masks.values()))
    for name, region in [('abdomen-m02', partial), ('abdomen-m01', eligible),
                         ('abdomen-n01', np.zeros_like(pancreas))]:
        data = OUT / 'build' / name
        assert not data.exists(); data.mkdir(parents=True)
        changed = {k: v.copy() for k, v in masks.items()}
        if name != 'abdomen-n01':
            changed['duodenum'] |= region
            changed['pancreas'] &= ~region
            if name == 'abdomen-m01':
                # Existing shared boundary voxels already belong to duodenum.
                changed['pancreas'][:] = False
        assert np.array_equal(original_union, np.logical_or.reduce(list(changed.values())))
        assert all(np.array_equal(changed[k], masks[k]) for k in LABELS
                   if k not in ['pancreas', 'duodenum'])
        objects = []
        for color, label in enumerate(order):
            if not changed[label].any():
                continue
            oid = ids[label]
            export_piece(data / f'{oid}.npz', changed[label], a)
            objects.append({'object_id': oid, 'file': f'{oid}.npz', 'color_index': color,
                            'proposed_label': label})
        write(data / 'scene.json', {'coordinates': 'LPS millimetres', 'objects': objects})
        write(data / 'vocabulary.json', sorted(LABELS))
        np.savez_compressed(data / 'ct.npz', hu=ct, affine_lps=a)
        with np.load(data / 'ct.npz') as z:
            assert np.array_equal(z['hu'], ct) and np.array_equal(z['affine_lps'], a)
        obs = load_scene(data); render(obs, data / 'overview.png')
        font = ImageFont.load_default(size=15)
        for o in obs:
            lo, hi = bounds([o]); center = (lo + hi) / 2
            canvas = Image.new('RGB', (1320, 485), (18, 23, 30)); draw = ImageDraw.Draw(canvas)
            for j, (plane, axes) in enumerate(PLANES.items()):
                span = max(180, float(max(hi[axes[0]]-lo[axes[0]], hi[axes[1]]-lo[axes[1]]) + 80))
                image, _ = render_slice(ct, a, [o], plane, float(center[axes[2]]), span=span, size=440)
                canvas.paste(image, (j * 440, 40))
                draw.text((j * 440 + 5, 4), f"{o['object_id']} {o['proposed_label']} | {plane}", font=font, fill='white')
            canvas.save(data / f"ct-{o['object_id']}.png")
        # Uniform preview recipe over the upper abdomen, not a private target position.
        lo, hi = bounds([o for o in obs if o['proposed_label'] not in ['aorta', 'inferior_vena_cava']])
        contact_sheet(ct, a, obs, data / 'ct-overview.png', 'axial',
                      np.linspace(lo[2], hi[2], 8)[1:-1], span=400, size=440)
        private = OUT / 'author' / name; private.mkdir(parents=True)
        findings = []
        if region.any():
            export_piece(private / 'region-0.npz', region, a)
            point, erosion_steps = representative(region, a)
            findings = [{'object_id': ids['duodenum'], 'included_label': 'pancreas',
                         'region_file': 'region-0.npz', 'oracle_point_lps_mm': point}]
        else:
            erosion_steps = None
        key = {'findings': findings, 'point_tolerance_mm': 3.0,
               'objects': {o['object_id']: o['proposed_label'] for o in objects},
               'vocabulary': sorted(LABELS)}
        write(private / 'expected.json', key)
        write(private / 'answer.json', {'findings': [
            {k: (f['oracle_point_lps_mm'] if k == 'point_lps_mm' else f[k])
             for k in ['object_id', 'included_label', 'point_lps_mm']} for f in findings]})
        records.append({'task': name, 'case': 28, 'object_count': len(objects),
                        'included_volume_ml': float(region.sum() * ml),
                        'remaining_pancreas_ml': float(changed['pancreas'].sum() * ml),
                        'duodenum_ml': float(changed['duodenum'].sum() * ml),
                        'payload_voxels': int(region.sum()),
                        'components26': cropped_components(region) if region.any() else [],
                        'oracle_erosion_steps': erosion_steps,
                        'foreground_union_exact': True, 'unaffected_masks_exact': True,
                        'ct_samples_exact': int(ct.size),
                        'public_files': {p.name: sha(p) for p in sorted(data.iterdir())},
                        'private_files': {p.name: sha(p) for p in sorted(private.iterdir())}})
    record = {'round': 'BR-017', 'case': 28, 'source_patient': 's1233',
              'source_mask_sha256': source_hashes, 'source_ct_sha256': sha(source / 'ct.nii.gz'),
              'partial_rule': 'Eligible pancreas voxels with Euclidean distance to source duodenum boundary at or below the 35th percentile.',
              'partial_distance_threshold_mm': threshold, 'partial_components26': comp,
              'source_pancreas_ml': float(pancreas.sum() * ml),
              'source_pancreas_duodenum_overlap_ml': float((pancreas & duodenum).sum() * ml),
              'objects': ids, 'tasks': records,
              'limits': ['Synthetic absorption, no clinical adjudication.',
                         'Whole absorption permits a missing-label cue; partial absorption preserves all names.',
                         'Source CT unchanged; no contour reconstruction or rare-disease diagnosis graded.']}
    write(OUT / 'author/screen.json', record)
    write(ROOT / 'docs/evidence/br017-screen.json', record)
    print(json.dumps({k: record[k] for k in ['partial_distance_threshold_mm', 'partial_components26', 'source_pancreas_ml', 'objects']}))
    print(json.dumps([{k: r[k] for k in ['task', 'object_count', 'included_volume_ml', 'remaining_pancreas_ml', 'duodenum_ml', 'components26']} for r in records]))


if __name__ == '__main__':
    main()
