"""Compare untouched TA36 predictions with references; no case is admitted here."""
from pathlib import Path
import argparse, hashlib, json
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'runs/br033-brain-routing'
DATA = BASE / 'sources/TopBrain_Data_Release_Batches1n2nTA36_081726'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def component_summary(mask):
    positions = np.argwhere(mask)
    if not len(positions):
        return {'count': 0, 'largest_voxels': []}
    lo, hi = positions.min(0), positions.max(0) + 1
    sl = tuple(slice(int(a), int(b)) for a, b in zip(lo, hi))
    cc, count = ndi.label(mask[sl], np.ones((3, 3, 3)))
    sizes = np.bincount(cc.ravel())[1:]
    return {'count': int(count), 'largest_voxels': sorted(sizes.tolist(), reverse=True)[:8]}


def adjacency(labels):
    pairs = np.zeros((37, 37), dtype=np.int64)
    for axis in range(3):
        a, b = [slice(None)] * 3, [slice(None)] * 3
        a[axis], b[axis] = slice(None, -1), slice(1, None)
        x, y = labels[tuple(a)], labels[tuple(b)]
        valid = (x > 0) & (y > 0) & (x != y)
        pair = np.minimum(x[valid], y[valid]).astype(np.int64) * 37 + np.maximum(x[valid], y[valid])
        pairs += np.bincount(pair, minlength=37 * 37).reshape(37, 37)
    return {f'{a}-{b}': int(pairs[a, b]) for a, b in zip(*np.nonzero(pairs))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--predictions', type=Path, required=True)
    args = ap.parse_args()
    names = json.loads((DATA / 'labelmap_jsons/labels_topbrain_v2_topaneu36class.json').read_text())['labels']
    rows = []
    for p in sorted(args.predictions.glob('topcow_mr_*.nii.gz')):
        refpath = DATA / 'labelsTr_topbrain_v2_topaneu36class' / p.name
        predni, refni = nib.load(p), nib.load(refpath)
        assert predni.shape == refni.shape and np.allclose(predni.affine, refni.affine)
        pred, ref = np.asarray(predni.dataobj, dtype=np.uint8), np.asarray(refni.dataobj, dtype=np.uint8)
        assert pred.max() <= 36 and ref.max() <= 36
        conf = np.bincount((ref.astype(np.uint16) * 37 + pred).ravel(), minlength=37 * 37).reshape(37, 37)
        classes = []
        for name, label in names.items():
            if not label:
                continue
            nr, npred = int(conf[label].sum()), int(conf[:, label].sum())
            if not nr and not npred:
                continue
            classes.append({'name': name, 'label': label, 'reference_voxels': nr, 'predicted_voxels': npred,
                'dice': 2 * int(conf[label, label]) / (nr + npred),
                'reference_components_26': component_summary(ref == label),
                'prediction_components_26': component_summary(pred == label),
                'reference_predicted_as': {namestr: int(conf[label, other]) for namestr, other in names.items() if conf[label, other]},
                'prediction_reference_as': {namestr: int(conf[other, label]) for namestr, other in names.items() if conf[other, label]}})
        row = {'case': p.stem.split('.')[0], 'prediction_sha256': sha(p), 'reference_sha256': sha(refpath),
               'classes': classes, 'reference_adjacency_6': adjacency(ref), 'prediction_adjacency_6': adjacency(pred),
               'admitted': False, 'warning': 'Reference comparison is a curation screen, not anatomical adjudication.'}
        rows.append(row)
        print(row['case'], sorted([(x['name'], round(x['dice'], 3)) for x in classes], key=lambda x: x[1]), flush=True)
    (args.predictions / 'reference-screen.json').write_text(json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    main()
