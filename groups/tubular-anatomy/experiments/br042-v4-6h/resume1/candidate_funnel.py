"""Diagnose the saved discovery filter without changing the agent's answer.

The two thresholds are post-hoc engineering diagnostics on a known case. No
reference coordinates enter candidate generation; GT is used only to measure it.
The second threshold is not a validated replacement or a new capability score.
"""
from pathlib import Path
import json
import types

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TRIAL = ROOT / "runs/br042-all-vessels-astra-xhigh-v4-6h-resume1/all-vessels__cr5kdch"
WORK = TRIAL / "artifacts/app/work"
TASK = ROOT / "runs/br042-all-vessels-v4-6h/tasks/all-vessels"
LOCAL = ROOT / "runs/br042-resume-trace-audit-20260921"


def main():
    LOCAL.mkdir(exist_ok=True)
    specs = json.loads((TRIAL / "artifacts/app/answer/vessels.json").read_text())
    paths = dict(np.load(WORK / "paths.npz"))
    # Reconstruct the coronary path inventory at the last candidate-generation call,
    # before the superior atrial branch was added. The old RCA differs by one inserted
    # parent-junction point; remove it using unchanged old coordinates as an alignment key.
    old = json.loads((ROOT / "runs/br042-all-vessels-v4-6h-resume1/restore/answer/centerlines.json").read_text())
    old_rca = next(c for c in old["centerlines"] if c["id"] == "rca")
    affine = nib.load(TASK / "environment/data/image.nii.gz").affine
    world = np.einsum("ij,nj->ni", affine[:3, :3], paths["rca"]) + affine[:3, 3]
    distances, indices = cKDTree(world).query(np.array(old_rca["points_ras_mm"]))
    assert distances.max() < .001 and len(set(indices)) == len(indices)
    paths["rca"] = paths["rca"][indices]
    spacing = nib.affines.voxel_sizes(affine)
    ids = [s["id"] for s in specs if s.get("mode", "vesselness") == "vesselness" and s["id"] != "rca_superior_atrial"]
    tree = cKDTree(np.concatenate([paths[k] for k in ids]) * spacing)
    a = np.load(WORK / "image.npy", mmap_mode="r")
    features = np.load(WORK / "vesselness.npz")
    v, origin = features["v"], features["origin"]
    roi = a[tuple(slice(o, o + n) for o, n in zip(origin, v.shape))]
    score = types.ModuleType("score")
    exec(compile((TASK / "tests/score.py").read_text(), "frozen_score", "exec"), score.__dict__)
    r, rl, rw, _ = score.samples(json.loads((TASK / "tests/reference.json").read_text()))
    inv = np.linalg.inv(affine)
    rv = np.einsum("ij,nj->ni", inv[:3, :3], r) + inv[:3, 3]
    saved = dict(np.load(WORK / "low_candidates.npz"))
    saved_set = {tuple(q) for coords in saved.values() for q in coords}
    results = []
    for threshold in [.018, .006]:
        mask = (v > threshold) & (roi > 80)
        sk = skeletonize(mask)
        coords = np.argwhere(sk) + origin
        retained = coords[tree.query(coords * spacing)[0] > 1.3]
        m = np.zeros(v.shape, bool)
        m[tuple((retained - origin).T)] = True
        labels, _ = ndi.label(m, np.ones((3, 3, 3)))
        sizes = np.bincount(labels.ravel())
        slices = ndi.find_objects(labels)
        sized, accepted, rejected = [], [], []
        for k in np.where((sizes >= 6) & (sizes < 2500))[0]:
            if k == 0:
                continue
            sl = slices[k - 1]
            q = np.argwhere(labels[sl] == k) + np.array([s.start for s in sl]) + origin
            sized.append(q)
            gap = float(tree.query(q * spacing)[0].min())
            if gap < 2.2:
                accepted.append(q)
            else:
                rejected.append({"points": len(q), "gap_mm": gap})
        stages = {"skeleton": coords, "after_existing_path_exclusion": retained,
                  "after_size_filter": np.concatenate(sized), "accepted_components": np.concatenate(accepted)}
        row = {"vesselness_threshold": threshold, "hu_threshold": 80,
               "mask_voxels": int(mask.sum()), "accepted_components": len(accepted),
               "stage_voxels": {k: len(q) for k, q in stages.items()}, "branches": {}}
        if threshold == .018:
            recreated = {tuple(q) for q in stages["accepted_components"]}
            row["recreated_candidate_voxel_set_matches_saved"] = recreated == saved_set
            row["recreated_minus_saved_points"] = len(recreated - saved_set)
            row["saved_minus_recreated_points"] = len(saved_set - recreated)
        for k, name in [(5, "D2"), (6, "OM1"), (7, "OM2")]:
            select = rl == k
            br = {}
            for stage, points in stages.items():
                d = cKDTree(points * spacing).query(rv[select] * spacing)[0]
                br[stage] = {"coverage_1mm": float(np.average(d <= 1, weights=rw[select])),
                             "coverage_2mm": float(np.average(d <= 2, weights=rw[select]))}
            row["branches"][name] = br
            # Identify which full components carry nearby reference signal and
            # exactly which scalar gate would discard those components.
            near_distance, near_index = cKDTree(retained * spacing).query(rv[select] * spacing)
            near_coords = retained[near_index] - origin
            near_component = labels[tuple(near_coords.T)]
            components = []
            for ident in np.unique(near_component[near_distance <= 1]):
                sl = slices[int(ident) - 1]
                q = np.argwhere(labels[sl] == ident) + np.array([s.start for s in sl]) + origin
                gap = float(tree.query(q * spacing)[0].min())
                components.append({"component": int(ident), "points": len(q),
                                   "nearest_existing_path_gap_mm": gap,
                                   "passes_size_gate": bool(6 <= len(q) < 2500),
                                   "passes_parent_gap_gate": gap < 2.2,
                                   "reference_length_nearest_to_component_mm": float(rw[select][(near_component == ident) & (near_distance <= 1)].sum())})
            br["near_reference_components"] = components
        results.append(row)
        np.savez(LOCAL / f"candidate-components-{threshold}.npz", **{str(i): q for i, q in enumerate(accepted)})
        print(json.dumps(row, indent=2), flush=True)
    record = {"scope": "Post-hoc discovery sensitivity; no model execution, answer change or clinical adjudication.",
              "inputs": [str(WORK.relative_to(ROOT)), str((TASK / "tests/reference.json").relative_to(ROOT))],
              "results": results,
              "limits": "All skeleton components include nonarterial/false candidates. More candidate recall is not a validated output improvement."}
    (HERE / "candidate-funnel.json").write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    main()
