"""Reference-assisted curation, never an input-legal repair algorithm."""
import argparse
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--prediction", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    ni = nib.load(a.image)
    im = np.asarray(ni.dataobj)
    gtni, prni = nib.load(a.reference), nib.load(a.prediction)
    assert gtni.shape == prni.shape == ni.shape
    assert np.allclose(ni.affine, gtni.affine) and np.allclose(ni.affine, prni.affine)
    gt, pr = np.asarray(gtni.dataobj) > 0, np.asarray(prni.dataobj) > 0
    sp = nib.affines.voxel_sizes(ni.affine)
    structure = np.ones((3, 3, 3), bool)
    pc, pn = ndi.label(pr, structure)
    sizes = np.bincount(pc.ravel())
    top = np.argsort(sizes[1:])[::-1][:20] + 1
    sk = skeletonize(gt)
    miss = sk & ~pr
    mc, mn = ndi.label(miss, structure)
    boxes = ndi.find_objects(mc)
    candidates = []
    for j, box in enumerate(boxes, 1):
        if box is None:
            continue
        lo = np.maximum([b.start - 2 for b in box], 0)
        hi = np.minimum([b.stop + 2 for b in box], gt.shape)
        sl = tuple(slice(x, y) for x, y in zip(lo, hi))
        this = mc[sl] == j
        pts = np.argwhere(this) + lo
        if len(pts) < 2:
            continue
        boundary = ndi.binary_dilation(this, structure) & sk[sl] & pr[sl]
        boundary_cc, n_boundary = ndi.label(boundary, structure)
        labels = np.unique(pc[sl][boundary]).tolist()
        boundary_pts = np.argwhere(boundary) + lo
        item = {"id": j, "skeleton_voxels": len(pts), "center_ijk": pts.mean(0).tolist(),
                "bounds_ijk": [pts.min(0).tolist(), pts.max(0).tolist()],
                "extent_mm": ((pts.max(0) - pts.min(0)) * sp).tolist(),
                "boundary_clusters": n_boundary, "prediction_components_at_ends": labels,
                "boundary_ijk": boundary_pts.tolist(),
                "HU_percentiles": np.percentile(im[tuple(pts.T)], [0, 25, 50, 75, 100]).tolist()}
        candidates.append(item)
    candidates.sort(key=lambda x: (x["boundary_clusters"] >= 2, x["skeleton_voxels"]), reverse=True)
    report = {"shape": ni.shape, "spacing_mm": sp.tolist(),
              "dice": float(2 * (gt & pr).sum() / (gt.sum() + pr.sum())),
              "reference_voxels": int(gt.sum()), "prediction_voxels": int(pr.sum()),
              "prediction_components": pn,
              "largest_components": [{"id": int(j), "voxels": int(sizes[j])} for j in top],
              "reference_skeleton_voxels": int(sk.sum()),
              "reference_skeleton_coverage": float((sk & pr).sum() / sk.sum()),
              "missing_components": mn, "candidates": candidates,
              "scope": "Reference-assisted candidate screen; omitted reference regions are not automatically false positives."}
    (a.output / "screen.json").write_text(json.dumps(report, indent=2) + "\n")
    nib.save(nib.Nifti1Image(sk.astype("uint8"), ni.affine), a.output / "reference_skeleton.nii.gz")
    print(json.dumps({k: v for k, v in report.items() if k != "candidates"}, indent=2))
    print(json.dumps(candidates[:12], indent=2))


if __name__ == "__main__":
    main()
