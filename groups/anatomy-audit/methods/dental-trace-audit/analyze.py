"""Read-only diagnostic of three frozen dental attempts; never runs solver scripts.

Run with an existing numpy/nibabel/scipy/matplotlib environment. All generated
media and detailed trace indexes stay in a fresh local output directory.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from scipy.optimize import linear_sum_assignment

RUNS = [
    ("F018 medium", "dental-ct-only-astra-medium", "21af29aaf8034aa6"),
    ("F018 xhigh", "dental-f018-astra-xhigh", "68d5acdeb63f4262"),
    ("F002 medium", "dental-f002-astra-medium", "4338cd3dae024fc8"),
]
TEETH = [q * 10 + i for q in range(1, 5) for i in range(1, 9)]
GROUPS = {
    "Jawbones": [1, 2],
    "Sinuses": [5, 6],
    "Airway": [7],
    "Teeth": TEETH,
    "Pulps": [k + 100 for k in TEETH],
    "Main canals": [3, 4],
    "Small canals": [103, 104, 105],
    "Restorations": [8, 9, 10],
}
PAIRS = [(3, 4), (5, 6), (103, 104)] + [
    (a + i + off, b + i + off)
    for off in (0, 100)
    for a, b in ((10, 20), (30, 40))
    for i in range(1, 9)
]
PERM = np.arange(149)
for left, right in PAIRS:
    PERM[left], PERM[right] = right, left


def digest(path):
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def mean(values):
    values = [v for v in values if v is not None]
    return float(np.mean(values)) if values else None


def scores(cm):
    gc, pc = cm.sum(1), cm.sum(0)
    return {
        k: float(2 * cm[k, k] / (gc[k] + pc[k])) if gc[k] + pc[k] else None
        for ids in GROUPS.values()
        for k in ids
    }


def trace_index(path):
    calls, messages, failures = [], [], []
    for line, raw in enumerate(path.open(), 1):
        event = json.loads(raw)
        item = event.get("payload", {})
        if event["type"] != "response_item":
            continue
        if item.get("type") == "custom_tool_call":
            code = item.get("input", "")
            calls.append(
                {
                    "line": line,
                    "timestamp": event["timestamp"],
                    "tool": item["name"],
                    "view_image_expressions": code.count("tools.view_image("),
                    "script_paths": sorted(set(re.findall(r"/app/work/[\w.-]+\.py", code))),
                }
            )
        elif item.get("type") == "message" and item.get("role") == "assistant":
            messages.append(
                {
                    "line": line,
                    "timestamp": event["timestamp"],
                    "text": " ".join(c.get("text", "") for c in item.get("content", [])),
                }
            )
        elif item.get("type") == "custom_tool_call_output":
            # Only text output; do not copy inline image data or hidden reasoning.
            for content in item.get("output", []):
                txt = content.get("text", "")
                if "Traceback (most recent call last)" in txt:
                    failures.append({"line": line, "text": txt})
    return {"calls": calls, "messages": messages, "tracebacks": failures}


def image_panel(ax, ct, labels, title, axis=2, index=55, crop=None):
    gray = np.take(ct, index, axis=axis).T
    lab = np.take(labels, index, axis=axis).T
    rgb = np.repeat(np.clip((gray + 400) / 2900, 0, 1)[..., None], 3, axis=2)
    for k in np.unique(lab):
        if k in TEETH:
            color = plt.get_cmap("tab20")((TEETH.index(k) % 20) / 19)[:3]
        elif k in (8, 9, 10):
            color = {8: (1, 0.3, 0.6), 9: (1, 0.75, 0.15), 10: (0.15, 0.8, 1)}[k]
        else:
            continue
        rgb[lab == k] = 0.4 * rgb[lab == k] + 0.6 * np.array(color)
        pos = np.argwhere(lab == k)
        if len(pos) >= 20:
            y, x = pos.mean(0)
            ax.text(
                x,
                y,
                str(k),
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                bbox={"facecolor": "black", "alpha": 0.75, "pad": 1},
            )
    ax.imshow(rgb, origin="lower")
    if crop:
        ax.set_xlim(crop[:2])
        ax.set_ylim(crop[2:])
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("native i (voxel)")
    ax.set_ylabel("native j (voxel)" if axis == 2 else "native k (voxel)")


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "audit.json").exists():
        raise SystemExit("Choose a fresh output directory; existing audit retained")
    report = {"diagnostic_only": True, "source_files_unchanged": None, "runs": [], "hashes": {}}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    for name, exp, aid in RUNS:
        trial = next((repo / ".local/attempts" / ("attempt-" + aid) / "job").glob("task__*"))
        task = repo / ".local" / exp / "task"
        files = {
            "ct": task / "environment/data/ct.nii.gz",
            "gt": task / "tests/reference.nii.gz",
            "prediction": trial / "artifacts/app/answer/segmentation.nii.gz",
            "metrics": trial / "verifier/metrics.json",
            "trace": next((trial / "agent/sessions").glob("**/*.jsonl")),
            "method": trial / "artifacts/app/answer/method.md",
            "instruction": task / "instruction.md",
            "scorer": task / "tests/score.py",
        }
        files.update({"script:" + p.name: p for p in (trial / "artifacts/app/work").glob("*.py")})
        for path in files.values():
            report["hashes"][str(path.relative_to(repo))] = digest(path)
        ci, gi, pi = [nib.load(files[k]) for k in ("ct", "gt", "prediction")]
        g, p = [np.asanyarray(im.dataobj).astype(np.uint8) for im in (gi, pi)]
        assert g.shape == p.shape == ci.shape and np.allclose(gi.affine, pi.affine)
        cm = np.zeros((149, 149), dtype=np.int64)
        for z in range(g.shape[2]):
            cm += np.bincount(
                (g[:, :, z].astype(np.int32) * 149 + p[:, :, z]).ravel(), minlength=149**2
            ).reshape(149, 149)
        raw, swapped = scores(cm), scores(cm[:, PERM])
        frozen = json.loads(files["metrics"].read_text())
        assert abs(mean(raw.values()) - frozen["macro_dice"]) < 1e-12
        for row in frozen["per_label"]:
            assert raw[row["id"]] == row["dice"]
        fg = float(2 * cm[1:, 1:].sum() / (cm[1:, :].sum() + cm[:, 1:].sum()))
        assert fg == frozen["foreground_dice"]
        trace = trace_index(files["trace"])
        (out / f"{exp}-trace-index.json").write_text(json.dumps(trace, indent=2))
        gc, pc = cm.sum(1), cm.sum(0)
        row = {
            "name": name,
            "experiment_id": exp,
            "attempt_id": "attempt-" + aid,
            "original_macro": mean(raw.values()),
            "fixed_lr_diagnostic_macro": mean(swapped.values()),
            "foreground_dice": fg,
            "active_labels_original": sum(v is not None for v in raw.values()),
            "active_labels_lr_diagnostic": sum(v is not None for v in swapped.values()),
            "exec_calls": len(trace["calls"]),
            "view_image_call_expressions": sum(c["view_image_expressions"] for c in trace["calls"]),
            "traceback_outputs": len(trace["tracebacks"]),
            "axis_codes": nib.aff2axcodes(ci.affine),
            "affine": ci.affine.tolist(),
            "groups": {},
            "per_label": [],
            "centroids": {},
        }
        for label, ids in GROUPS.items():
            row["groups"][label] = {
                "original_mean": mean(raw[k] for k in ids),
                "lr_diagnostic_mean": mean(swapped[k] for k in ids),
                "active_lr_labels": sum(swapped[k] is not None for k in ids),
            }
        for k in raw:
            best = np.argsort(cm[k])[::-1][:5]
            row["per_label"].append(
                {
                    "id": k,
                    "gt_voxels": int(gc[k]),
                    "pred_voxels": int(pc[k]),
                    "original_dice": raw[k],
                    "lr_diagnostic_dice": swapped[k],
                    "top_prediction_ids": [[int(j), int(cm[k, j])] for j in best if cm[k, j]],
                }
            )
        for k in [3, 4, 5, 6, 11, 21, 31, 41, 38, 48]:
            row["centroids"][k] = {
                key: np.argwhere(a == k).mean(0).tolist() if np.any(a == k) else None
                for key, a in (("gt", g), ("prediction", p))
            }
        # Tooth + pulp objects: one-to-one maximum-overlap assignment, ignoring FDI.
        # Includes unmatched GT/predicted objects as zero. This is an optimistic
        # post-hoc geometric diagnostic, not a new accepted score.
        gt_ids = [k for k in TEETH if gc[k] + gc[k + 100]]
        pr_ids = [k for k in TEETH if pc[k] + pc[k + 100]]
        n = max(len(gt_ids), len(pr_ids))
        dice = np.zeros((n, n))
        for i, a in enumerate(gt_ids):
            for j, b in enumerate(pr_ids):
                intersection = cm[np.ix_([a, a + 100], [b, b + 100])].sum()
                dice[i, j] = 2 * intersection / (gc[a] + gc[a + 100] + pc[b] + pc[b + 100])
        ri, cj = linear_sum_assignment(-dice)
        row["whole_tooth_assignment_diagnostic"] = {
            "mean_dice_including_unmatched": float(dice[ri, cj].mean()),
            "gt_objects": len(gt_ids),
            "predicted_objects": len(pr_ids),
            "matched": [
                [gt_ids[i], pr_ids[j], float(dice[i, j])]
                for i, j in zip(ri, cj)
                if i < len(gt_ids) and j < len(pr_ids)
            ],
        }
        # Restorations union asks whether gross shape overlaps under any restoration ID.
        ids = [8, 9, 10]
        den = gc[ids].sum() + pc[ids].sum()
        row["restoration_union_dice"] = float(2 * cm[np.ix_(ids, ids)].sum() / den) if den else None
        report["runs"].append(row)
        if name == "F018 xhigh":
            ct = np.asanyarray(ci.dataobj)
            fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
            for ax, a, title in zip(
                axes,
                [g, p, PERM[p]],
                ["Reference IDs", "Saved agent IDs", "Fixed L/R ID swap — diagnostic"],
            ):
                image_panel(ax, ct, a, title, crop=(75, 330, 20, 195))
            fig.suptitle(
                "F018 · Same voxel positions, opposing tooth IDs (native k = 55)", fontsize=16
            )
            fig.savefig(out / "f018-identity.png", dpi=170)
            plt.close(fig)
            fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
            for ax, j in zip(axes, (145, 205)):
                ax.imshow(ct[:, j, :].T, origin="lower", cmap="gray", vmin=-400, vmax=2100)
                ax.contour(
                    np.isin(g[:, j, :], [3, 4]).T, levels=[0.5], colors=["#ffba38"], linewidths=2
                )
                ax.contour(
                    np.isin(p[:, j, :], [3, 4]).T, levels=[0.5], colors=["#21d5ec"], linewidths=2
                )
                ax.set(
                    xlim=(50, 365),
                    ylim=(70, 230),
                    xlabel="native i (voxel)",
                    ylabel="native k (voxel)",
                    title=f"Native coronal j = {j}",
                )
            fig.suptitle(
                "F018 xhigh · Main canal outlines: reference gold, agent cyan\nBoth sides pooled; identity cannot explain the remaining offsets",
                fontsize=14,
            )
            fig.savefig(out / "f018-canal-residuals.png", dpi=170)
            plt.close(fig)
        if name == "F002 medium":
            ct = np.asanyarray(ci.dataobj)
            fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
            for ax, a, title in zip(
                axes,
                [np.zeros_like(g), g, p],
                ["CT with metal streaks", "Reference", "Saved agent output"],
            ):
                image_panel(ax, ct, a, title, index=125, crop=(65, 335, 20, 215))
            fig.suptitle(
                "F002 · Restoration disagreement (native k = 125)\n8 bridge = pink · 9 crown = gold · 10 implant = cyan; numeric IDs unchanged",
                fontsize=14,
            )
            fig.savefig(out / "f002-restorations.png", dpi=170)
            plt.close(fig)
        print(
            name,
            json.dumps(
                {
                    "macro": row["original_macro"],
                    "lr": row["fixed_lr_diagnostic_macro"],
                    "groups": row["groups"],
                    "whole_teeth": row["whole_tooth_assignment_diagnostic"][
                        "mean_dice_including_unmatched"
                    ],
                }
            ),
            flush=True,
        )
    fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
    groups = list(GROUPS)
    x = np.arange(len(groups))
    width = 0.24
    for j, run in enumerate(report["runs"]):
        vals = [run["groups"][k]["lr_diagnostic_mean"] for k in groups]
        ax.bar(
            x + (j - 1) * width,
            [100 * v if v is not None else np.nan for v in vals],
            width,
            label=run["name"],
        )
    ax.set(
        xticks=x,
        xticklabels=groups,
        ylim=(0, 105),
        ylabel="Mean per-label Dice (%)",
        title="Residual performance after a fixed L/R ID swap — diagnostic only",
    )
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    fig.savefig(out / "residual-by-structure.png", dpi=170)
    plt.close(fig)
    report["source_files_unchanged"] = all(
        digest(repo / p) == sha for p, sha in report["hashes"].items()
    )
    assert report["source_files_unchanged"]
    (out / "audit.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
