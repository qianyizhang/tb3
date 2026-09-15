"""Describe acquired VerSe masks and screen two fixed ordering baselines.

This is author-side curation, not clinical adjudication or a model trial.
All reported geometry uses original NIfTI voxels and physical coordinates.
The preview samples surfaces; it is not a connectivity representation.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import time

import nibabel as nib
import numpy as np


def name(k):
    return f'C{k}' if k <= 7 else f'T{k-7}' if k <= 19 else f'L{k-19}' if k <= 25 else 'T13' if k == 28 else f'unknown-{k}'


def physical(ijk, affine):
    return sum(ijk[:, ax, None] * affine[:3, ax] for ax in range(3)) + affine[:3, 3]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, default=Path('runs/br012-curation/source'))
    p.add_argument('--output', type=Path, default=Path('runs/br012-curation/author'))
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    cases, preview = [], []
    for path in sorted((a.source / 'files').rglob('*msk.nii.gz')):
        img = nib.load(path)
        arr = np.asanyarray(img.dataobj)
        assert arr.ndim == 3
        # Some source masks store integer labels as float64. Validate every
        # value against the narrowed volume before using it; no rounding edits.
        assert np.isfinite(arr).all() and arr.min() >= 0 and arr.max() <= 28
        if arr.dtype != np.uint8:
            narrowed = arr.astype(np.uint8)
            assert all(np.array_equal(arr[i], narrowed[i]) for i in range(arr.shape[0]))
            arr = narrowed
        # Crop empty margins to make per-object calculations inexpensive.
        bounds = [np.flatnonzero(np.any(arr, axis=tuple(j for j in range(3) if j != i))) for i in range(3)]
        offset = np.array([v[0] for v in bounds])
        crop = arr[tuple(slice(int(v[0]), int(v[-1])+1) for v in bounds)]
        source_affine = img.affine.copy()
        lps = np.diag([-1., -1., 1., 1.]) @ source_affine
        voxel_ml = abs(np.linalg.det(source_affine[:3,:3])) / 1000
        ids = np.unique(crop); ids = ids[ids > 0]
        scene_id = path.name.replace('_seg-vert_msk.nii.gz','')
        rng = np.random.default_rng(12012)
        anon = rng.choice(np.arange(100, 999), len(ids), replace=False)
        objects, shown = [], []
        for k, oid in zip(ids, anon):
            coords = np.argwhere(crop == k) + offset
            lo, hi = coords.min(axis=0), coords.max(axis=0)
            local = arr[tuple(slice(int(lo[i]), int(hi[i])+1) for i in range(3))] == k
            pad = np.pad(local, 1)
            eroded = pad[1:-1,1:-1,1:-1].copy()
            for axis in range(3):
                for delta in [-1,1]:
                    s = [slice(1,-1)] * 3
                    s[axis] = slice(0,-2) if delta < 0 else slice(2,None)
                    eroded &= pad[tuple(s)]
            boundary = np.argwhere(local & ~eroded) + lo
            center = physical(coords.mean(axis=0)[None,:], lps)[0]
            edge = physical(boundary, lps)
            assert np.isfinite(edge).all()
            take = min(700, len(edge))
            if '406' in scene_id and int(k) in [17,18]:
                take = min(2000, len(edge))
            chosen = edge[rng.choice(len(edge), take, replace=False)]
            row = {'id':f'o{oid}', 'source_value':int(k), 'source_label':name(int(k)), 'voxel_count':len(coords), 'volume_ml':round(len(coords)*voxel_ml,4), 'centroid_lps_mm':center.round(4).tolist(), 'extent_lps_mm':np.ptp(edge,axis=0).round(4).tolist(), 'boundary_points':len(edge)}
            objects.append(row)
            quantized = np.rint(chosen * 10)
            assert np.abs(quantized).max() < 32768
            encoded = base64.b64encode(quantized.astype('<i2').tobytes()).decode('ascii')
            decoded = np.frombuffer(base64.b64decode(encoded), dtype='<i2').reshape(-1,3) / 10
            assert np.abs(chosen-decoded).max() <= 0.050001
            shown.append({'id':row['id'], 'label':row['source_label'], 'volume_ml':round(row['volume_ml'],2), 'points_int16le_lps_tenths_mm':encoded})
        ordered = sorted(objects, key=lambda r:-r['centroid_lps_mm'][2])
        # I1 receives the exact proposed-label multiset. T13 is between T12 and L1.
        sorted_labels = sorted((int(k) for k in ids), key=lambda k:19.5 if k==28 else k)
        multiset_predictions = [name(k) for k in sorted_labels]
        # I2 assumes a usual sequence; it is GIVEN the top label to isolate the
        # thoracolumbar transition, not to pretend it inferred the FOV anchor.
        top = ordered[0]['source_value']
        fixed_predictions = [name(top+i) if top+i <= 25 else 'overflow' for i in range(len(ordered))]
        case = {'scene':scene_id, 'path':str(path), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'shape':list(arr.shape), 'axis_codes':list(nib.aff2axcodes(source_affine)), 'spacing_mm':[float(x) for x in img.header.get_zooms()], 'object_count':len(ids), 'objects':objects, 'physical_superior_order':[r['source_label'] for r in ordered], 'supplied_multiset_sort':{'correct':sum(r['source_label']==v for r,v in zip(ordered,multiset_predictions)), 'predictions':multiset_predictions}, 'fixed_12_thoracic_sort_given_top_anchor':{'correct':sum(r['source_label']==v for r,v in zip(ordered,fixed_predictions)), 'predictions':fixed_predictions}}
        cases.append(case)
        preview.append({'scene':scene_id, 'objects':shown})
        print(scene_id, 'objects',len(ids), 'multiset',case['supplied_multiset_sort']['correct'], 'fixed',case['fixed_12_thoracic_sort_given_top_anchor']['correct'], flush=True)
        del arr, crop, img
    receipts = [json.loads(p.read_text()) for p in sorted((a.source/'files').rglob('*.receipt.json'))]
    result = {'round':'BR-012','model_trials':0,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_receipts':receipts,'cases':cases,'wall_seconds':round(time.monotonic()-start,3),'limitations':['Source labels are reference annotations, not a new blind review.','Baseline two is given the true top anchor; all other predictions follow a fixed 12-thoracic sequence.','Table patient counts may combine overlapping series.','Surface preview is sampled and not used for geometric measurements.']}
    (a.output/'screen.json').write_text(json.dumps(result,indent=2)+'\n')
    (a.output/'preview.json').write_text(json.dumps(preview,separators=(',',':'))+'\n')


if __name__ == '__main__':
    main()
