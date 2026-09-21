"""Post-hoc diagnostics of saved dental masks; never executes solver programs.

All target-GT-dependent calculations are author-only explanations, not new blind
results. Writes only to a separate local diagnosis directory.
"""

import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/dental-reference-ablation-20260921"
OUT = BASE / "fine-structure-diagnosis"
RUN = ROOT / ".local/dental-f002-reference-v2-astra-medium"
WORK = ROOT / ".local/attempts/attempt-36ee0d66d0a64d55/job/task__5aAvbpS/artifacts/app/work"
TEETH = [q * 10 + n for q in range(1, 5) for n in range(1, 9)]
PULPS = [x + 100 for x in TEETH]
CANALS = [3, 4, 103, 104, 105]
INPUTS = {}


def ball(radius):
    grid = np.ogrid[tuple(slice(-radius, radius + 1) for _ in range(3))]
    return sum(x * x for x in grid) <= radius * radius


def fingerprint(path):
    INPUTS[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    fingerprint(path)
    if path.suffix == ".npy":
        return np.load(path)
    return np.asanyarray(nib.load(path).dataobj)


def score(g, p):
    ng, np_, inter = int(g.sum()), int(p.sum()), int((g & p).sum())
    return {
        "gt": ng,
        "pred": np_,
        "tp": inter,
        "dice": 2 * inter / (ng + np_) if ng + np_ else None,
        "precision": inter / np_ if np_ else 0,
        "recall": inter / ng if ng else None,
    }


def hist(a):
    ids, counts = np.unique(a, return_counts=True)
    return {str(int(k)): int(v) for k, v in zip(ids, counts)}


def quant(a):
    return (
        {
            str(q): float(v)
            for q, v in zip(
                [0, 10, 25, 50, 75, 90, 100], np.percentile(a, [0, 10, 25, 50, 75, 90, 100])
            )
        }
        if len(a)
        else {}
    )


def crop(mask, pad=3):
    co = np.array(np.where(mask))
    lo, hi = np.maximum(co.min(1) - pad, 0), np.minimum(co.max(1) + pad + 1, mask.shape)
    return tuple(slice(int(a), int(b)) for a, b in zip(lo, hi))


def rule_study(ct, labels, toothmask, ids):
    """Same fixed first pulp rule on true vs predicted whole-tooth masks.

    No special-tooth limits, component filtering, closure or prior additions here.
    Labels with +100 are unioned back into their own tooth. Pooled geometry only.
    """
    sm = ndi.gaussian_filter(ct, 0.4)
    geometry = np.zeros(ct.shape, bool)
    depth = np.zeros(ct.shape, bool)
    per_tooth = []
    for lab in ids:
        mask = (toothmask == lab) | (toothmask == lab + 100)
        if not mask.any():
            continue
        sl = crop(mask, 2)
        geometry |= mask
        depth[sl] |= ndi.distance_transform_edt(mask[sl]) > 2
        g_local = labels[sl] == lab + 100
        p_local = mask[sl] & (ndi.distance_transform_edt(mask[sl]) > 2) & (sm[sl] < 1250)
        per_tooth.append({"tooth": lab, "score": score(g_local, p_local)})
    g = np.isin(labels, [x + 100 for x in ids])
    low = sm < 1250
    p = geometry & depth & low
    return (
        {
            "fixed_rule": "smoothed CT <1250 AND distance inside individual tooth >2 voxels (0.6 mm)",
            "score": score(g, p),
            "gt_pulp_intensity_quantiles": quant(sm[g]),
            "gt_pulp_above_intensity_cut": int((g & ~low).sum()),
            "gt_pulp_outside_tooth_mask": int((g & ~geometry).sum()),
            "gt_pulp_in_mask_but_depth_rejected": int((g & geometry & ~depth).sum()),
            "gt_pulp_in_depth_but_intensity_rejected": int((g & depth & ~low).sum()),
            "per_tooth": per_tooth,
        },
        p,
        depth,
        sm,
    )


def paint(path, shape, radius, extra=0):
    mask, core = np.zeros(shape, bool), np.zeros(shape, bool)
    for z, p in enumerate(path):
        r = (radius + extra) * min(1, 0.7 + z / 8, 0.7 + (len(path) - z - 1) / 8)
        lo = np.maximum(np.floor(p - r - 1).astype(int), 0)
        hi = np.minimum(np.ceil(p + r + 2).astype(int), shape)
        sl = tuple(slice(start, end) for start, end in zip(lo, hi))
        coords = np.ogrid[sl]
        d = sum((coords[k] - p[k]) ** 2 for k in range(3))
        mask[sl] |= d < r**2
        core[sl] |= d < (r * 0.65) ** 2
    return mask, core


def translation_sensitivity(mask):
    rows = []
    for voxels in [1, 2, 3]:
        scores = []
        for axis in range(3):
            for sign in [-1, 1]:
                shift = np.zeros(3, int)
                shift[axis] = voxels * sign
                p = ndi.shift(mask.astype(np.uint8), shift, order=0, mode="constant") > 0
                scores.append(score(mask, p)["dice"])
        rows.append(
            {
                "offset_mm": voxels * 0.3,
                "mean_dice": float(np.mean(scores)),
                "min_dice": min(scores),
                "max_dice": max(scores),
            }
        )
    return rows


def main():
    OUT.mkdir(exist_ok=True)
    ct = load(RUN / "task/environment/data/ct.nii.gz")
    gt = load(RUN / "task/tests/reference.nii.gz").astype(np.uint8)
    example_ct = load(RUN / "task/environment/reference/ct.nii.gz")
    example_gt = load(RUN / "task/environment/reference/segmentation.nii.gz").astype(np.uint8)
    final = load(WORK.parent / "answer/segmentation.nii.gz").astype(np.uint8)
    assert np.array_equal(final, load(WORK / "final.npy"))
    assert np.array_equal(ct, load(WORK / "target.npy"))
    assert np.array_equal(example_ct, load(WORK / "ref.npy"))
    teeth = load(WORK / "teeth2.npy")
    ids = [x for x in TEETH if np.any(gt == x)]
    result = {
        "purpose": "Author-only post-hoc diagnosis; no modified submission or new model inference",
        "spacing_mm": list(
            map(float, nib.load(RUN / "task/environment/data/ct.nii.gz").header.get_zooms())
        ),
        "pulp": {},
        "canals": [],
    }
    assert np.allclose(result["spacing_mm"], [0.3] * 3)
    print("Fixed-rule transfer tests", flush=True)
    for name, x, s, t, selected in [
        ("example_true_teeth_all32", example_ct, example_gt, example_gt, TEETH),
        ("example_true_teeth_target22_ids", example_ct, example_gt, example_gt, ids),
        ("target_true_teeth", ct, gt, gt, ids),
        ("target_predicted_teeth", ct, gt, teeth, TEETH),
    ]:
        stats, rule, depth, sm = rule_study(x, s, t, selected)
        result["pulp"][name] = stats
        print(name, {k: v for k, v in stats.items() if k != "per_tooth"}, flush=True)
    result["pulp"]["per_label"] = []
    for lab in [x + 100 for x in ids]:
        g, p = gt == lab, final == lab
        row = {
            "label": lab,
            "final": score(g, p),
            "gt_intensity_quantiles": quant(sm[g]),
            "gt_at_or_above1250": int((g & (sm >= 1250)).sum()),
            "gt_outside_all_predicted_teeth": int((g & (teeth == 0)).sum()),
            "gt_inside_depth2": int((g & depth).sum()),
            "gt_passes_fixed_rule": int((g & rule).sum()),
            "prediction_labels_at_gt": hist(final[g]),
            "gt_labels_at_prediction": hist(gt[p]),
        }
        result["pulp"]["per_label"].append(row)
    gp = np.isin(gt, PULPS)
    result["pulp"]["saved_stages"] = {}
    for name in ["atlas2.npy", "teeth_pulp.npy", "teeth_pulp_final.npy", "final.npy"]:
        a = load(WORK / name)
        result["pulp"]["saved_stages"][name] = score(gp, np.isin(a, PULPS))
    result["pulp"]["identity_independent_final_confusion"] = {
        "prediction_at_gt_pulp": hist(final[gp]),
        "gt_at_predicted_pulp": hist(gt[np.isin(final, PULPS)]),
    }
    print("Saved pulp stages", result["pulp"]["saved_stages"], flush=True)
    (OUT / "pulp-checkpoint.json").write_text(json.dumps(result, indent=2) + "\n")
    jawatlas, atlas = load(WORK / "jawatlas.npy"), load(WORK / "atlas2.npy")
    raw0, raw1 = load(WORK / "canals0.npy"), load(WORK / "canals1.npy")
    sm = ndi.gaussian_filter(ct, 0.8)
    valid = ndi.binary_dilation(load(WORK / "jaws1.npy") == 1, structure=ball(1))
    reconstructed = np.zeros(gt.shape, np.uint8)
    for lab in CANALS:
        path = load(WORK / f"final_canal_path{lab}.npy")
        rad = (3.8 if lab == 3 else 3.6) if lab < 5 else (1.6 if lab == 105 else 1.45)
        tube, core = paint(path, gt.shape, rad)
        clipped = tube & valid & ((sm < 900) | (core & (sm < 1500)))
        reconstructed[clipped] = lab
    assert np.array_equal(reconstructed, raw1), (
        "saved canal reconstruction mismatch after overlap priority"
    )
    for lab in CANALS:
        print("Canal", lab, flush=True)
        g, p = gt == lab, final == lab
        path = load(WORK / f"final_canal_path{lab}.npy")
        rad = (3.8 if lab == 3 else 3.6) if lab < 5 else (1.6 if lab == 105 else 1.45)
        tube, core = paint(path, gt.shape, rad)
        clipped = tube & valid & ((sm < 900) | (core & (sm < 1500)))
        # Small crops keep EDT and voxel-translation tests cheap.
        sl = crop(g | tube, 12)
        gsub = g[sl]
        origin = np.array([x.start for x in sl])
        gtpoints = np.argwhere(gsub) + origin
        dist_to_volume = cKDTree(gtpoints * 0.3).query(path * 0.3)[0]
        inside = ndi.map_coordinates(g.astype(np.uint8), path.T, order=0, mode="constant") > 0
        dist_from_gt_to_path = cKDTree(path * 0.3).query(gtpoints * 0.3)[0]
        row = {
            "label": lab,
            "final": score(g, p),
            "paint_radius_mm": rad * 0.3,
            "path_to_gt_voxel_center_mm": quant(dist_to_volume),
            "path_samples_inside_gt_fraction": float(inside.mean()),
            "gt_voxel_to_path_mm": quant(dist_from_gt_to_path),
            "saved_stages": {},
            "misses_outside_unclipped_tube": int((g & ~tube).sum()),
            "misses_from_clipping_inside_tube": int((g & tube & ~clipped).sum()),
            "misses_from_other_canal_priority": int((g & clipped & (raw1 != lab)).sum()),
            "misses_from_final_assembly": int((g & (raw1 == lab) & ~p).sum()),
            "unclipped_tube_score": score(g, tube),
            "fixed_radius_expansion_diagnostics": [],
            "one_axis_gt_translation_sensitivity": translation_sensitivity(gsub),
            "prediction_labels_at_gt": hist(final[g]),
        }
        for name, a in [
            ("atlas2", atlas),
            ("jawatlas", jawatlas),
            ("canals0", raw0),
            ("canals1", raw1),
            ("final", final),
        ]:
            row["saved_stages"][name] = score(g, a == lab)
        for extra in [1, 2, 4]:
            expanded, _ = paint(path, gt.shape, rad, extra)
            row["fixed_radius_expansion_diagnostics"].append(
                {"extra_radius_mm": extra * 0.3, "unclipped": score(g, expanded)}
            )
        result["canals"].append(row)
        print(
            {
                k: row[k]
                for k in [
                    "label",
                    "path_samples_inside_gt_fraction",
                    "path_to_gt_voxel_center_mm",
                    "misses_outside_unclipped_tube",
                    "misses_from_clipping_inside_tube",
                    "misses_from_final_assembly",
                ]
            },
            flush=True,
        )
    for filename in [
        "pulps.py",
        "assemble.py",
        "canals_refine.py",
        "pulp_calibrate.py",
        "register2.py",
    ]:
        fingerprint(WORK / filename)
    result["input_sha256"] = INPUTS
    result["limitations"] = [
        "Target-GT-dependent diagnostic, not a blind result or clinical adjudication.",
        "Path distances are to GT voxel centers, not a clinically adjudicated centerline.",
        "Fixed-rule tests hold cutoffs constant but use true reference or target tooth masks; those oracle inputs were unavailable for the target solver.",
        "Hypothetical expansions and translations are sensitivity tests only; original masks/scores are unchanged.",
    ]
    (OUT / "diagnostics.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Saved", OUT / "diagnostics.json", flush=True)


if __name__ == "__main__":
    main()
