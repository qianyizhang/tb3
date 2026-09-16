"""Additional fixed geometric checks, authored after freeze; never retune truth."""
import json
from pathlib import Path
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from solve_baseline import exports, transform
from build_cases import medial_path
from score import score

B = Path("runs/br033-airway-routing/benchmark")


def main():
    results = {}
    for method in ["nearest_component", "straight_anchors"]:
        output = B / method
        assert not output.exists()
        for case in ["A01", "A02", "A03"]:
            src = B / "input" / case
            ni = nib.load(src / "image.nii.gz")
            im, aff = np.asarray(ni.dataobj), ni.affine
            sp = nib.affines.voxel_sizes(aff)
            pr = np.asarray(nib.load(src / "proposed_mask.nii.gz").dataobj) > 0
            edit = np.asarray(nib.load(src / "editable_region.nii.gz").dataobj) > 0
            req = json.loads((src / "request.json").read_text())
            anchors = np.array([req["start_ras_mm"], req["end_ras_mm"]])
            ends = np.rint(transform(anchors, np.linalg.inv(aff))).astype(int)
            cc, _ = ndi.label(pr, np.ones((3, 3, 3)))
            hit = cc[tuple(ends.T)]
            fixed = pr.copy()
            if hit[0] != hit[1]:
                pair = ends.copy()
                if method == "nearest_component":
                    left = np.argwhere((cc == hit[0]) & edit)
                    right = np.argwhere((cc == hit[1]) & edit)
                    dist, idx = cKDTree(left * sp).query(right * sp)
                    k = np.argmin(dist)
                    pair = np.array([left[idx[k]], right[k]])
                length = np.linalg.norm((pair[1] - pair[0]) * sp)
                route = np.linspace(pair[0], pair[1], int(np.ceil(length / .2)) + 1)
                seed = np.zeros(pr.shape, bool)
                seed[tuple(np.rint(route).astype(int).T)] = True
                fixed |= (ndi.distance_transform_edt(~seed, sampling=sp) <= 2.) & edit
            path = medial_path(fixed, sp, ends[0], ends[1])
            exports(output / case, fixed, aff, im, transform(path, aff))
        results[method] = score(output, B / "admitted-truth")
    (B / "additional-geometric-controls.json").write_text(json.dumps({"timing": "authored after freeze and trial dispatch; thresholds unchanged", "results": results}, indent=2) + "\n")
    print(json.dumps({k: {"reward": v["reward"], "A01": v["cases"]["A01"]} for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()
