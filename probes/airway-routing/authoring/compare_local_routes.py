"""Development screen: fixed CT-vs-mask path costs; reference used only to score.

Endpoints are reference-assisted public requests. This screens geometric routing,
not anatomical naming, and does not certify a repair mask or bronchoscope access.
"""
import argparse
import json
from pathlib import Path
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.graph import MCP_Geometric


def solve(im, pr, sp, start, end, image):
    allowed = pr | (im < -500) if image else np.ones(pr.shape, bool)
    radius = ndi.distance_transform_edt(pr, sampling=sp)
    costs = np.full(pr.shape, np.inf, np.float32)
    costs[allowed] = 8.
    costs[pr] = 1. / (0.25 + radius[pr])
    mcp = MCP_Geometric(costs, sampling=tuple(sp), fully_connected=True)
    dist, _ = mcp.find_costs([tuple(start)], [tuple(end)])
    if not np.isfinite(dist[tuple(end)]):
        return None
    return np.array(mcp.traceback(tuple(end)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    a = p.parse_args()
    root = Path("runs/br033-airway-routing") / ("case" + a.case)
    source = Path("runs/br033-brain-routing/airway-access/data") / a.case
    ni = nib.load(source / f"{a.case}_CT_HR.nii.gz")
    im = np.asarray(ni.dataobj)
    gt = np.asarray(nib.load(source / f"{a.case}_CT_HR_label_airways.nii.gz").dataobj) > 0
    pr = np.asarray(nib.load(root / "airways/prediction/labels_Airways.nii.gz").dataobj) > 0
    sp = nib.affines.voxel_sizes(ni.affine)
    cc, _ = ndi.label(pr, np.ones((3, 3, 3)))
    main_cc = np.argmax(np.bincount(cc.ravel())[1:]) + 1
    report = json.loads((root / "screen/screen.json").read_text())
    results = []
    out = root / "route-screen"
    out.mkdir(exist_ok=True)
    for candidate in report["candidates"]:
        labels = candidate["prediction_components_at_ends"]
        if main_cc not in labels or len(labels) < 2 or candidate["skeleton_voxels"] < 3:
            continue
        center = np.array(candidate["center_ijk"])
        lo = np.maximum(0, np.floor(center - 18. / sp).astype(int))
        hi = np.minimum(pr.shape, np.ceil(center + 18. / sp).astype(int))
        sl = tuple(slice(int(x), int(y)) for x, y in zip(lo, hi))
        local_cc, local_gt, local_pr, local_im = cc[sl], gt[sl], pr[sl], im[sl]
        boundary = np.array(candidate["boundary_ijk"])
        starts = boundary[cc[tuple(boundary.T)] == main_cc]
        # Public start is a seed on the proximal retained prediction.
        start = starts[0] - lo
        gt_points = np.argwhere(local_gt)
        gt_tree = cKDTree(gt_points * sp)
        for target_cc in labels:
            if target_cc == main_cc:
                continue
            points = np.argwhere((local_cc == target_cc) & local_gt)
            if not len(points):
                continue
            # Select a well-inside distal seed, far from proximal anchor.
            radius = ndi.distance_transform_edt(local_cc == target_cc, sampling=sp)
            d = np.linalg.norm((points - start) * sp, axis=1)
            ranks = d + radius[tuple(points.T)] * 2
            end = points[np.argmax(ranks)]
            record = {"gap_id": candidate["id"], "target_component": target_cc,
                      "start_ijk": (start + lo).tolist(), "end_ijk": (end + lo).tolist(),
                      "lo": lo.tolist(), "hi": hi.tolist(), "methods": {}}
            for image in [False, True]:
                name = "image" if image else "mask_only"
                path = solve(local_im, local_pr, sp, start, end, image)
                if path is None:
                    record["methods"][name] = {"found": False}
                    continue
                new = path[~local_pr[tuple(path.T)]]
                ds = gt_tree.query(new * sp)[0] if len(new) else np.array([0.])
                record["methods"][name] = {"found": True, "path_samples": len(path),
                    "new_path_samples": len(new), "new_center_inside_reference": float(local_gt[tuple(new.T)].mean()) if len(new) else 1.,
                    "new_center_max_distance_to_reference_mm": float(ds.max()),
                    "new_center_mean_distance_to_reference_mm": float(ds.mean()),
                    "length_mm": float(np.linalg.norm(np.diff(path, axis=0) * sp, axis=1).sum()),
                    "new_HU_median": float(np.median(local_im[tuple(new.T)])) if len(new) else None}
                np.save(out / f"gap{candidate['id']}-component{target_cc}-{name}.npy", path + lo)
            results.append(record)
    final = {"predeclared_costs": {"outside_prediction": 8., "image_allowed_HU": "< -500", "mask_medial_cost": "1/(.25+radius_mm)"},
             "selection": "reference-assisted endpoints and candidates, development screen only", "routes": results}
    (out / "comparison.json").write_text(json.dumps(final, indent=2) + "\n")
    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    main()
