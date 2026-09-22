"""V3 dental evaluator with unchanged v2 numeric metrics; private to verifier, never visible to solver."""

import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

TEETH = [q * 10 + i for q in range(1, 5) for i in range(1, 9)]
GROUPS = {
    "jawbones": [1, 2],
    "sinuses": [5, 6],
    "pharynx": [7],
    "tooth_tissue": TEETH,
    "pulp": [k + 100 for k in TEETH],
    "inferior_alveolar_canals": [3, 4],
    "small_canals": [103, 104, 105],
    "restoration_subtypes_under_review": [8, 9, 10],
}


def average(values):
    values = [v for v in values if v is not None]
    return float(np.mean(values)) if values else None


def surface_metrics(g, p, spacing):
    if not g.any() or not p.any():
        return {
            "status": "both_empty" if not g.any() and not p.any() else "one_empty",
            "assd_mm": None,
            "hd95_mm": None,
        }
    locations = np.where(g | p)
    box = tuple(
        slice(max(0, int(c.min()) - 1), min(g.shape[i], int(c.max()) + 2))
        for i, c in enumerate(locations)
    )
    g, p = g[box], p[box]
    gs = g & ~ndi.binary_erosion(g)
    ps = p & ~ndi.binary_erosion(p)
    gx = np.argwhere(gs) * spacing
    px = np.argwhere(ps) * spacing
    dgp = cKDTree(px).query(gx)[0]
    dpg = cKDTree(gx).query(px)[0]
    return {
        "status": "measured",
        "assd_mm": float((dgp.mean() + dpg.mean()) / 2),
        "hd95_mm": float(max(np.percentile(dgp, 95), np.percentile(dpg, 95))),
    }


def score(answer, reference, labels, include_surfaces=True):
    ref = nib.load(reference)
    g = np.asanyarray(ref.dataobj).astype(np.uint8)
    allowed = sorted(map(int, labels))
    path = Path(answer)
    if not path.is_file():
        return {"valid": False, "reason": "missing_output", "macro_dice": 0.0}
    try:
        im = nib.load(path)
        a = np.asanyarray(im.dataobj)
        if a.shape != g.shape or not np.allclose(im.affine, ref.affine, atol=1e-5, rtol=0):
            raise ValueError("geometry mismatch")
        if not np.isfinite(a).all() or not np.equal(a, np.rint(a)).all():
            raise ValueError("noninteger or nonfinite labels")
        if not set(np.unique(a).astype(int)).issubset(allowed):
            raise ValueError("unknown label")
        a = a.astype(np.uint8)
    except Exception as exc:
        return {"valid": False, "reason": str(exc), "macro_dice": 0.0}
    n = max(allowed) + 1
    cm = np.zeros((n, n), dtype=np.int64)
    for z in range(g.shape[2]):
        cm += np.bincount(
            (g[:, :, z].astype(np.int32) * n + a[:, :, z]).ravel(), minlength=n * n
        ).reshape(n, n)
    gc, pc = cm.sum(1), cm.sum(0)
    rows = []
    for k in allowed:
        if not k:
            continue
        den = int(gc[k] + pc[k])
        rows.append(
            {
                "id": k,
                "gt_voxels": int(gc[k]),
                "prediction_voxels": int(pc[k]),
                "intersection": int(cm[k, k]),
                "dice": float(2 * cm[k, k] / den) if den else None,
            }
        )
    per_id = {r["id"]: r["dice"] for r in rows}
    groups = {}
    for name, ids in GROUPS.items():
        den = int(gc[ids].sum() + pc[ids].sum())
        groups[name] = {
            "macro_dice": average(per_id[k] for k in ids),
            "active_labels": sum(per_id[k] is not None for k in ids),
            "pooled_geometry_dice": float(2 * cm[np.ix_(ids, ids)].sum() / den) if den else None,
        }
    gt_ids = [k for k in TEETH if gc[k] + gc[k + 100]]
    pred_ids = [k for k in TEETH if pc[k] + pc[k + 100]]
    count = max(len(gt_ids), len(pred_ids))
    d = np.zeros((count, count))
    for i, gk in enumerate(gt_ids):
        for j, pk in enumerate(pred_ids):
            d[i, j] = (
                2
                * cm[np.ix_([gk, gk + 100], [pk, pk + 100])].sum()
                / (gc[gk] + gc[gk + 100] + pc[pk] + pc[pk + 100])
            )
    ix, jx = linear_sum_assignment(-d)
    matched = [
        {
            "gt_id": gt_ids[i],
            "predicted_id": pred_ids[j],
            "dice": float(d[i, j]),
            "correct_fdi": gt_ids[i] == pred_ids[j],
        }
        for i, j in zip(ix, jx)
        if i < len(gt_ids) and j < len(pred_ids)
    ]
    detected = [r for r in matched if r["dice"] >= 0.5]
    correct = sum(r["correct_fdi"] for r in detected)
    teeth = {
        "geometry_mean_dice_with_unmatched_zero": float(d[ix, jx].mean()) if count else None,
        "gt_object_count": len(gt_ids),
        "predicted_object_count": len(pred_ids),
        "assignment": "one-to-one maximum total Dice of tooth+pulp unions",
        "detection_threshold_dice": 0.5,
        "detected_objects": len(detected),
        "detection_recall": len(detected) / len(gt_ids) if gt_ids else None,
        "detection_precision": len(detected) / len(pred_ids) if pred_ids else None,
        "fdi_correct_among_detected": correct / len(detected) if detected else None,
        "correctly_identified_gt_recall": correct / len(gt_ids) if gt_ids else None,
        "matches": matched,
    }
    surfaces = {}
    if include_surfaces:
        for k in [3, 4, 103, 104, 105]:
            surfaces[str(k)] = surface_metrics(
                g == k, a == k, np.asarray(ref.header.get_zooms()[:3])
            )
    den = gc[1:].sum() + pc[1:].sum()
    return {
        "valid": True,
        "contract_version": "dental-native-rpi-v3",
        "macro_dice": average(r["dice"] for r in rows),
        "per_label": rows,
        "foreground_dice": float(2 * cm[1:, 1:].sum() / den) if den else 1.0,
        "groups": groups,
        "whole_tooth_geometry_and_identity": teeth,
        "canal_surface_metrics": surfaces,
        "interpretation": "No automatic L/R permutation. Clinical laterality and agreement of original annotations with operational boundary rules remain unadjudicated (including occupied pulp, restorations, canal boundaries, jaw and airspace scope); descriptive agreement only, no clinical pass/fail threshold.",
    }


if __name__ == "__main__":
    answer = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/answer/segmentation.nii.gz")
    result = score(
        answer, "/tests/reference.nii.gz", json.loads(Path("/tests/labels.json").read_text())
    )
    out = Path("/logs/verifier")
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    (out / "reward.txt").write_text(str(result["macro_dice"]))
    print(json.dumps({"valid": result["valid"], "macro_dice": result["macro_dice"]}))
