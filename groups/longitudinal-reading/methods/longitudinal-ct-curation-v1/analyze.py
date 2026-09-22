"""Replay immutable outputs and report prospectively declared lesion-size strata."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-curation-v1"


def sha(p):
    with p.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def agree(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(agree(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(agree(x, y) for x, y in zip(a, b))
    return a == b or (isinstance(a, float) and isinstance(b, float) and abs(a - b) <= 1e-12)


def main():
    state = json.loads((BASE / "astra-medium/operator-state.json").read_text())
    assert state["condition_status"] == "completed"
    task = ROOT / ".local/freezes" / state["task_digest"] / "task"
    trial = Path(state["trial_path"])
    answer = trial / "artifacts/app/answer"
    out = BASE / "analysis"
    out.mkdir(exist_ok=False)
    cmd = [
        str(ROOT / ".venv-br037/bin/python"),
        str(task / "tests/evaluate.py"),
        "--answer",
        str(answer),
        "--reference",
        str(task / "tests/reference"),
        "--output",
        str(out / "replay"),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    (out / "replay.log").write_text(result.stdout + result.stderr)
    metrics = json.loads((trial / "verifier/metrics.json").read_text())
    replay = json.loads((out / "replay/metrics.json").read_text())
    assert agree(metrics, replay)
    geometry = json.loads((BASE / "review/geometry.json").read_text())
    rows = []
    figures = []
    for visit in ["baseline", "followup"]:
        if not metrics["visits"][visit]["valid"]:
            continue
        gt = np.asarray(nib.load(task / "tests/reference" / f"{visit}_instances.nii.gz").dataobj)
        pred = np.asarray(nib.load(answer / f"{visit}_instances.nii.gz").dataobj)
        image = nib.load(task / "environment/data" / f"{visit}.nii.gz")
        data = np.asarray(image.dataobj)
        covered = np.bincount(gt[pred > 0].ravel(), minlength=int(gt.max()) + 1)
        by_id = {r["id"]: r for r in geometry["visits"][visit]["labels"]}
        for result in metrics["visits"][visit]["per_gt"]:
            info = by_id[result["gt_id"]]
            volume = info["volume_ml"]
            rows.append(
                {
                    "visit": visit,
                    **result,
                    "volume_ml": volume,
                    "anatomy": info["anatomy"],
                    "source_event": info["event"],
                    "size_stratum": "<=1 mL"
                    if volume <= 1
                    else ">1 to 10 mL"
                    if volume <= 10
                    else ">10 mL",
                    "foreground_coverage": float(covered[result["gt_id"]] / result["voxels"]),
                }
            )
        labels = geometry["visits"][visit]["labels"]
        for page, start in enumerate(range(0, len(labels), 4), 1):
            selected = labels[start : start + 4]
            fig, axes = plt.subplots(
                len(selected),
                3,
                figsize=(12, 3.5 * len(selected)),
                squeeze=False,
                layout="constrained",
            )
            for r, info in enumerate(selected):
                ident = info["id"]
                k = info["max_area_k"]
                center = np.argwhere(gt[:, :, k] == ident).mean(0)
                xy = np.argwhere(gt[:, :, k] == ident)
                extent = (xy.max(0) - xy.min(0) + 1) * np.array(image.header.get_zooms()[:2])
                crop_mm = max(90, float(extent.max() + 20))
                half = crop_mm / 2 / float(image.header.get_zooms()[0])
                window = (-200, 1000) if info["anatomy"] == "Skeleton" else (-160, 240)
                for c in range(3):
                    ax = axes[r, c]
                    ax.imshow(
                        data[:, :, k].T, cmap="gray", vmin=window[0], vmax=window[1], origin="upper"
                    )
                    if c:
                        mask = (gt if c == 1 else pred)[:, :, k].T
                        color = "#20c7dc" if c == 1 else "#d868ed"
                        for value in np.unique(mask):
                            if not value:
                                continue
                            region = mask == value
                            pos = np.argwhere(region).mean(0)[::-1]
                            if np.all(np.abs(pos - center) < half):
                                ax.contour(region, levels=[0.5], colors=[color], linewidths=0.8)
                                ax.text(
                                    pos[0],
                                    pos[1],
                                    str(int(value)),
                                    color=color,
                                    fontsize=9,
                                    clip_on=True,
                                    bbox={"facecolor": "black", "alpha": 0.55, "edgecolor": "none"},
                                )
                    ax.set_xlim(center[0] - half, center[0] + half)
                    ax.set_ylim(center[1] + half, center[1] - half)
                    ax.axis("off")
                    ax.set_title(
                        f"{['CT', 'GT cyan', 'Astra purple'][c]} | {visit} GT{ident}, k={k}\n{info['volume_ml']:.3f} mL, crop {crop_mm:.0f} mm",
                        fontsize=9,
                    )
            fig.suptitle(
                "Case 02: native CT, reference and saved model output\nSolid contours; native i right, j down. Soft HU [-160,240]; bone HU [-200,1000].\nGT-selected views: not exhaustive FP review, never solver input. Longitudinal-CT v3, FDAT, CC BY-NC 4.0.",
                fontsize=11,
            )
            p = out / f"{visit}-{page}.png"
            fig.savefig(p, dpi=130)
            plt.close(fig)
            figures.append({"path": str(p.relative_to(ROOT)), "sha256": sha(p)})
        del data, gt, pred
    strata = []
    for name in ["<=1 mL", ">1 to 10 mL", ">10 mL"]:
        subset = [r for r in rows if r["size_stratum"] == name]
        n = len(subset)
        tp = sum(r["detection_prediction_id"] is not None for r in subset)
        strata.append(
            {
                "stratum": name,
                "gt_count": n,
                "localized": tp,
                "recall": tp / n if n else None,
                "gt_macro_dice": float(np.mean([r["best_one_to_one_dice"] for r in subset]))
                if n
                else None,
                "foreground_coverage_mean": float(
                    np.mean([r["foreground_coverage"] for r in subset])
                )
                if n
                else None,
            }
        )
    evidence = {
        "schema_version": 1,
        "attempt_id": state["attempt_id"],
        "task_digest": state["task_digest"],
        "metrics": metrics,
        "independent_replay_exact": metrics == replay,
        "replay_within_1e12": True,
        "declared_size_strata": strata,
        "per_reference": rows,
        "events": json.loads((answer / "events.json").read_text())
        if (answer / "events.json").is_file()
        else None,
        "report": (answer / "report.md").read_text() if (answer / "report.md").is_file() else None,
        "figures": figures,
        "source_hashes": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [
                trial / "agent/trajectory.json",
                trial / "verifier/metrics.json",
                task / "instruction.md",
                *sorted(answer.glob("*")),
            ]
            if p.is_file()
        },
        "limits": "One purposively selected patient; 22 visit-level instances are not independent patients. Broad cohort and patient metadata were supplied, but individual clinical reports remain unavailable. All plausible candidates are broader than malignant GT. Size strata are descriptive; frozen primary scores are unchanged.",
    }
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: evidence[k]
                for k in [
                    "attempt_id",
                    "independent_replay_exact",
                    "metrics",
                    "declared_size_strata",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
