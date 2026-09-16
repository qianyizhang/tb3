"""Locate interior label disagreements for source-image review, not admission."""
import argparse, json
from pathlib import Path
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'runs/br033-brain-routing'
DATA = BASE / 'sources/TopBrain_Data_Release_Batches1n2nTA36_081726'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--predictions', type=Path, required=True)
    args = ap.parse_args()
    names = json.loads((DATA / 'labelmap_jsons/labels_topbrain_v2_topaneu36class.json').read_text())['labels']
    byid = {v: k for k, v in names.items()}
    rows = []
    for p in sorted(args.predictions.glob('topcow_mr_*.nii.gz')):
        ni = nib.load(p)
        pred = np.asarray(ni.dataobj, dtype=np.uint8)
        ref = np.asarray(nib.load(DATA / 'labelsTr_topbrain_v2_topaneu36class' / p.name).dataobj, dtype=np.uint8)
        for name, label in names.items():
            if not label or not np.any(ref == label):
                continue
            loc = np.argwhere(ref == label)
            lo = np.maximum(loc.min(0) - 2, 0)
            hi = np.minimum(loc.max(0) + 3, ref.shape)
            sl = tuple(slice(int(x), int(y)) for x, y in zip(lo, hi))
            r, q = ref[sl], pred[sl]
            dist = ndi.distance_transform_edt(r == label, sampling=ni.header.get_zooms()[:3])
            core = dist >= .5
            wrong = core & (q != label)
            cc, n = ndi.label(wrong, np.ones((3, 3, 3)))
            sizes = np.bincount(cc.ravel())
            for k in np.argsort(sizes[1:])[::-1][:4] + 1:
                if sizes[k] < 10:
                    continue
                vox = np.argwhere(cc == k) + lo
                values, counts = np.unique(pred[tuple(vox.T)], return_counts=True)
                center = vox.mean(0)
                rows.append({'case': p.stem.split('.')[0], 'reference_class': name,
                    'core_voxels': int(sizes[k]), 'center_ijk': center.tolist(),
                    'center_ras_mm': nib.affines.apply_affine(ni.affine, center).tolist(),
                    'bbox_ijk': [vox.min(0).tolist(), (vox.max(0) + 1).tolist()],
                    'predicted_as': {byid[int(v)]: int(c) for v, c in zip(values, counts)},
                    'admitted': False})
    rows.sort(key=lambda x: x['core_voxels'], reverse=True)
    (args.predictions / 'review-regions.json').write_text(json.dumps(rows, indent=2) + '\n')
    for r in rows[:24]:
        print(r['case'], r['reference_class'], r['core_voxels'], r['predicted_as'], np.round(r['center_ijk'], 1).tolist())


if __name__ == '__main__':
    main()
