"""Audit parent attachments in a labeled volume, without asserting anatomy."""
import argparse, json
from pathlib import Path
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi

# Named branch chains, not a requirement that the whole CoW be one component.
CHAINS = {
    'R-MCA': [4, 5, 17, 18], 'L-MCA': [6, 7, 19, 20],
    'R-ACA': [4, 11, 13], 'L-ACA': [6, 12, 14],
    'R-PCA': [1, 2, 21], 'L-PCA': [1, 3, 22],
    'R-SCA': [1, 25], 'L-SCA': [1, 26],
}


def audit(a):
    result = {}
    for name, chain in CHAINS.items():
        mask = np.isin(a, chain)
        pos = np.argwhere(mask)
        if not len(pos):
            continue
        lo, hi = pos.min(0), pos.max(0) + 1
        crop = a[tuple(slice(int(x), int(y)) for x, y in zip(lo, hi))]
        cc, n = ndi.label(np.isin(crop, chain), np.ones((3, 3, 3)))
        parents, sizes = np.unique(cc[crop == chain[0]], return_counts=True)
        parent = int(parents[np.argmax(sizes)]) if len(parents) else -1
        result[name] = {'labels': chain, 'components_26': int(n),
            'parent_component': parent,
            'branch_parent_connected_fraction': {
                str(label): float(np.mean(cc[crop == label] == parent)) if np.any(crop == label) else None
                for label in chain[1:]}}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    records = {str(p): audit(np.asarray(nib.load(p).dataobj, dtype=np.uint8)) for p in args.inputs}
    args.output.write_text(json.dumps({'scope': '26-neighbor label-chain attachment screen; numerical connectivity is not clinical adjudication.', 'volumes': records}, indent=2) + '\n')
    print(json.dumps(records, indent=2))
