"""Read saved attempts and reconstruct mask stages; never execute solver scripts.

Run with the existing imaging environment and an explicit repository root/output
directory. All figures and diagnostic metrics are post-hoc, not frozen scores.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import PIL
import scipy
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ATTEMPTS = {
    "astra": "attempt-624605e8cb264dcb/job/task__QsdohUX",
    "sol": "attempt-174a50ea483847e2/job/task__MBUVkyL",
}
SELECTED_STEPS = {
    "astra": [12, 17, 18, 20, 26, 29, 30, 34, 39, 41, 42, 43],
    "sol": [10, 23, 24, 57, 58, 68, 74, 80, 81, 100, 101, 104, 105, 106, 107, 111, 112, 115],
}


def fingerprint(path: Path, root: Path) -> dict:
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": str(path.relative_to(root)), "sha256": digest}


def read_constants(path: Path) -> dict:
    """Allow only literal dict assignments/updates; importing would run code."""
    values = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            values[node.targets[0].id] = ast.literal_eval(node.value)
        elif (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "update"
            and isinstance(node.value.func.value, ast.Name)
        ):
            values[node.value.func.value.id].update(ast.literal_eval(node.value.args[0]))
        else:
            raise ValueError(f"Unexpected contour source statement: {ast.dump(node)[:150]}")
    return values


def metrics(mask: np.ndarray, truth: np.ndarray) -> dict:
    tp = int(np.count_nonzero(mask & truth))
    fp = int(mask.sum()) - tp
    fn = int(truth.sum()) - tp
    return {"tp_voxels": tp, "fp_voxels": fp, "fn_voxels": fn, "dice": 2 * tp / (2 * tp + fp + fn)}


def reconstruct(
    a: np.ndarray, g: np.ndarray, constants: dict, visit: str
) -> tuple[dict, np.ndarray]:
    """Mirror final saved segment.py, exposing its ordered destructive stages."""
    polys = constants["BASE" if visit == "baseline" else "FOLLOW"]
    aorta = constants["BAORTA" if visit == "baseline" else "FAORTA"]
    lateral = constants["BLATERAL" if visit == "baseline" else "FLATERAL"]
    fields = {}
    for z, points in polys.items():
        canvas = Image.new("1", a.shape[:2])
        ImageDraw.Draw(canvas).polygon([tuple(p) for p in points], fill=1)
        mask = np.asarray(canvas).T.copy()
        fields[z] = ndi.distance_transform_edt(mask) - ndi.distance_transform_edt(~mask)
    zs, lzs, aks = sorted(polys), sorted(lateral), sorted(aorta)
    xx, yy = np.ogrid[: a.shape[0], : a.shape[1]]
    bounds = {
        z: np.interp(np.arange(a.shape[1]), [p[0] for p in lateral[z]], [p[1] for p in lateral[z]])
        for z in lzs
    }
    names = [
        "polygon_interpolation",
        "lateral_clip",
        "aortic_exclusion",
        "positive_hu",
        "high_hu_exclusion",
    ]
    counts = {name: {"tp_voxels": 0, "fp_voxels": 0} for name in names}
    out = np.zeros(a.shape, dtype=bool)
    for z in range(zs[0], zs[-1] + 1):
        if z in fields:
            field = fields[z]
        else:
            lo, hi = max(k for k in zs if k < z), min(k for k in zs if k > z)
            t = (z - lo) / (hi - lo)
            field = fields[lo] * (1 - t) + fields[hi] * t
        mask = ndi.gaussian_filter(field, 0.65) > 0

        def record(name):
            tp = int(np.count_nonzero(mask & (g[:, :, z] > 0)))
            counts[name]["tp_voxels"] += tp
            counts[name]["fp_voxels"] += int(mask.sum()) - tp

        record(names[0])
        if lzs[0] <= z <= lzs[-1]:
            if z in bounds:
                bound = bounds[z]
            else:
                lo, hi = max(k for k in lzs if k < z), min(k for k in lzs if k > z)
                t = (z - lo) / (hi - lo)
                bound = bounds[lo] * (1 - t) + bounds[hi] * t
            mask &= xx <= bound[None, :]
        record(names[1])
        cx = np.interp(z, aks, [aorta[k][0] for k in aks])
        cy = np.interp(z, aks, [aorta[k][1] for k in aks])
        near = (xx - cx) ** 2 + (yy - cy) ** 2 < 19**2
        smoothed = ndi.gaussian_filter(a[:, :, z].astype(float), 0.5)
        labels, _ = ndi.label((smoothed > 125) & near)
        seed = labels[round(cx), round(cy)]
        if seed:
            vessel = ndi.binary_dilation(ndi.binary_fill_holes(labels == seed), iterations=1)
            mask &= ~vessel
        record(names[2])
        mask &= ndi.gaussian_filter(a[:, :, z].astype(float), 0.6) > 0
        record(names[3])
        mask &= ~(smoothed > 145)
        record(names[4])
        out[:, :, z] = mask
    labels, component_count = ndi.label(out)
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    final = labels == np.argmax(sizes)
    counts["largest_component"] = metrics(final, g > 0)
    total = int(np.count_nonzero(g))
    for values in counts.values():
        values["fn_voxels"] = total - values["tp_voxels"]
        tp, fp, fn = (values[k] for k in ["tp_voxels", "fp_voxels", "fn_voxels"])
        values["dice"] = 2 * tp / (2 * tp + fp + fn)
    return {
        "stages": counts,
        "components_before_final_filter": component_count,
        "control_planes": len(polys),
        "native_k_range": [zs[0], zs[-1]],
    }, final


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    task = root / ".local/longitudinal-ct-image-only-v1/task"
    trials = {name: root / ".local/attempts" / loc for name, loc in ATTEMPTS.items()}
    evidence = {
        "scope": "Post-hoc saved-trace diagnostics. Not a new trial, scorer revision or clinical adjudication.",
        "traces": {},
        "visits": {},
        "sources": [],
        "diagnostic_runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pillow": PIL.__version__,
            "nibabel": nib.__version__,
        },
    }
    for name, trial in trials.items():
        path = trial / "agent/trajectory.json"
        trace = json.loads(path.read_text())
        selected = [
            {
                "step_id": s["step_id"],
                "timestamp": s.get("timestamp"),
                "message": s.get("message", ""),
                "tool_calls": s.get("tool_calls", []),
            }
            for s in trace["steps"]
            if s["step_id"] in SELECTED_STEPS[name]
        ]
        evidence["traces"][name] = {
            "source": fingerprint(path, root),
            "total_steps": len(trace["steps"]),
            "selected_steps": selected,
        }
    ap = trials["astra"] / "artifacts/app"
    sp = trials["sol"] / "artifacts/app"
    constants = read_constants(ap / "work/contours.py")
    for path in [
        ap / "work/contours.py",
        ap / "work/segment.py",
        sp / "work/render_paired.py",
        sp / "work/render_fusion.py",
        sp / "work/make_candidate_masks.py",
        task / "instruction.md",
        Path(__file__),
    ]:
        evidence["sources"].append(fingerprint(path, root))
    scans, truths = {}, {}
    for visit in ("baseline", "followup"):
        scan_path = task / "environment/data" / f"{visit}.nii.gz"
        truth_path = task / "tests/reference" / f"{visit}_instances.nii.gz"
        pred_path = ap / "answer" / f"{visit}_instances.nii.gz"
        candidate_path = sp / "work" / f"{visit}_candidate.nii.gz"
        for path in [scan_path, truth_path, pred_path, candidate_path]:
            evidence["sources"].append(fingerprint(path, root))
        scan = nib.load(scan_path)
        a = np.load(ap / "work" / f"{visit}.npy", mmap_mode="r")
        assert np.array_equal(a, np.asanyarray(scan.dataobj))
        g = np.asanyarray(nib.load(truth_path).dataobj)
        pred = np.asanyarray(nib.load(pred_path).dataobj) > 0
        candidate = np.asanyarray(nib.load(candidate_path).dataobj) > 0
        stage_info, reconstructed = reconstruct(a, g, constants, visit)
        differences = np.argwhere(reconstructed != pred)
        # Baseline agrees exactly; this different local runtime reconstructs one
        # additional FU voxel. Keep the discrepancy, never substitute masks.
        assert len(differences) == {"baseline": 0, "followup": 1}[visit]
        lesions = {}
        for label in np.unique(g)[1:]:
            ijk = np.argwhere(g == label)
            center = ijk.mean(axis=0)
            lesions[str(int(label))] = {
                "voxels": len(ijk),
                "volume_ml": float(len(ijk) * np.prod(scan.header.get_zooms()) / 1000),
                "ijk_min": ijk.min(axis=0).tolist(),
                "ijk_max": ijk.max(axis=0).tolist(),
                "centroid_ijk": center.tolist(),
                "centroid_ras_mm": nib.affines.apply_affine(scan.affine, center).tolist(),
                "astra_covered_fraction": float(pred[g == label].mean()),
            }
        evidence["visits"][visit] = {
            "affine": scan.affine.tolist(),
            "lesions": lesions,
            "astra_stage_replay": stage_info,
            "astra_saved_mask_exact": len(differences) == 0,
            "astra_reconstruction_different_voxels_ijk": differences.tolist(),
            "astra_saved_foreground_metrics": metrics(pred, g > 0),
            "sol_candidate_voxels": int(candidate.sum()),
            "sol_candidate_gt_overlap_voxels": int(np.count_nonzero(candidate & (g > 0))),
        }
        scans[visit], truths[visit] = scan, g
    b = np.array(evidence["visits"]["baseline"]["lesions"]["3"]["centroid_ras_mm"])
    f = np.array(evidence["visits"]["followup"]["lesions"]["3"]["centroid_ras_mm"])
    evidence["persistent_gt3_world_displacement"] = {
        "delta_xyz_mm": (f - b).tolist(),
        "distance_mm": float(np.linalg.norm(f - b)),
        "meaning": "Reference centroid displacement, including anatomy/pose/shape change; not a registration-error estimate.",
    }
    # GT-selected post-hoc diagnostic; the solver saw none of these overlays.
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    panels = [
        ("baseline", 213, "Baseline target plane"),
        ("followup", 206, "Follow-up at same scanner world Z"),
        ("followup", 216, "Follow-up target plane"),
    ]
    for col, (visit, z, title) in enumerate(panels):
        scan = scans[visit]
        center = np.array(evidence["visits"][visit]["lesions"]["3"]["centroid_ijk"])
        half = round(60 / float(scan.header.get_zooms()[0]))
        x, y = (int(round(v)) for v in center[:2])
        roi = (slice(x - half, x + half), slice(y - half, y + half), z)
        plane = np.asarray(scan.dataobj[roi]).T
        gt = (truths[visit][roi] == 3).T
        wz = float(nib.affines.apply_affine(scan.affine, [x, y, z])[2])
        for row in range(2):
            ax = axes[row, col]
            ax.imshow(plane, cmap="gray", vmin=-160, vmax=240, origin="upper")
            if row and gt.any():
                ax.contour(gt, levels=[0.5], colors=["#26c6da"], linewidths=1.5)
            ax.set_title(
                f"{title}\n{visit} k={z}; world Z={wz:.1f} mm"
                if row == 0
                else ("GT 3: cyan solid contour" if gt.any() else "No GT 3 on this plane"),
                fontsize=10,
            )
            ax.axis("off")
    fig.suptitle("Same scanner coordinates do not establish anatomical correspondence", fontsize=16)
    fig.text(
        0.5,
        0.025,
        "GT-selected post-hoc view; 120 mm native crops; i right, j down; HU [-160, 240].\nGT 3 centroid moves +29.5 mm in world Z. This is not a clinical or registration adjudication.",
        ha="center",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    figure_path = output / "scanner-coordinate-mismatch.png"
    fig.savefig(figure_path, dpi=140)
    plt.close(fig)
    evidence["figure"] = fingerprint(figure_path, root)
    (output / "trace-attribution.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "stage_replay": "Baseline exact; follow-up one voxel differs. Saved masks and scores unchanged.",
                "visits": evidence["visits"],
                "world_displacement": evidence["persistent_gt3_world_displacement"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
