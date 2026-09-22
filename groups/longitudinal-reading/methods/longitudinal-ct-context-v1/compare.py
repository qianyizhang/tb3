"""Compare completed saved conditions, retaining original scores and native GT14 views."""

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-context-v1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    out = BASE / "comparison"
    out.mkdir(exist_ok=False)
    original = read(ROOT / ".local/longitudinal-ct-case02/analysis/evidence.json")
    supplied = read(BASE / "supplied/analysis/evidence.json")
    states = {
        c: read(BASE / c / "astra-medium/operator-state.json") for c in ["inference", "supplied"]
    }
    assert all(s["condition_status"] == "completed" for s in states.values())
    it = Path(states["inference"]["trial_path"])
    inferred = read(it / "artifacts/app/answer/context.json")
    rows = []
    for before, after in zip(original["per_reference"], supplied["per_reference"], strict=True):
        assert (before["visit"], before["gt_id"]) == (after["visit"], after["gt_id"])
        rows.append(
            {
                "visit": before["visit"],
                "gt_id": before["gt_id"],
                "volume_ml": before["volume_ml"],
                "before_prediction_id": before["detection_prediction_id"],
                "after_prediction_id": after["detection_prediction_id"],
                "before_dice": before["best_one_to_one_dice"],
                "after_dice": after["best_one_to_one_dice"],
                "before_coverage": before["foreground_coverage"],
                "after_coverage": after["foreground_coverage"],
            }
        )
    summaries = {}
    for name, record in [("image_only", original), ("context_supplied", supplied)]:
        metrics = record["metrics"]
        summaries[name] = {
            "attempt_id": record["attempt_id"],
            "task_digest": record["task_digest"],
            "contract_valid": metrics["valid"],
            "detection": metrics["detection_micro"],
            "foreground_dice": {
                v: metrics["visits"][v]["segmentation"]["foreground_dice"]
                for v in ["baseline", "followup"]
            },
            "gt_macro_dice": metrics["segmentation_gt_macro_dice"],
            "association": metrics["association"],
            "size_strata": record["declared_size_strata"],
            "independent_replay_exact": record["independent_replay_exact"],
        }
    st = Path(states["supplied"]["trial_path"])
    old_state = read(ROOT / ".local/longitudinal-ct-case02/astra-medium/operator-state.json")
    old_trial = Path(old_state["trial_path"])
    frozen = ROOT / ".local/freezes" / states["supplied"]["task_digest"] / "task"
    paths = {
        "ct": frozen / "environment/data/followup.nii.gz",
        "gt": frozen / "tests/reference/followup_instances.nii.gz",
        "old": old_trial / "artifacts/app/answer/followup_instances.nii.gz",
        "new": st / "artifacts/app/answer/followup_instances.nii.gz",
    }
    arrays = {k: np.asarray(nib.load(p).dataobj) for k, p in paths.items()}
    point = (190, 235, 536)
    assert int(arrays["gt"][point]) == 14
    point_check = {
        "native_ijk": point,
        "gt_label": 14,
        "old_prediction_label": int(arrays["old"][point]),
        "new_prediction_label": int(arrays["new"][point]),
    }
    fig, axes = plt.subplots(3, 4, figsize=(12, 9), layout="constrained")
    colors = {"gt": "#20c7dc", "old": "#d868ed", "new": "#ffb34d"}
    for r, k in enumerate([534, 536, 538]):
        for c, key in enumerate(["ct", "gt", "old", "new"]):
            ax = axes[r, c]
            ax.imshow(arrays["ct"][:, :, k].T, cmap="gray", vmin=-160, vmax=240, origin="upper")
            if key != "ct":
                plane = arrays[key][:, :, k].T
                for label in np.unique(plane[195:275, 150:230]):
                    if label:
                        ax.contour(
                            plane == label, levels=[0.5], colors=[colors[key]], linewidths=1.1
                        )
                        yx = np.argwhere(plane == label).mean(0)
                        if 150 <= yx[1] <= 230 and 195 <= yx[0] <= 275:
                            ax.text(
                                yx[1],
                                yx[0],
                                str(int(label)),
                                color=colors[key],
                                fontsize=9,
                                bbox={"facecolor": "black", "alpha": 0.6, "edgecolor": "none"},
                            )
            ax.set_xlim(150, 230)
            ax.set_ylim(275, 195)
            ax.axis("off")
            ax.set_title(
                f"{['CT only', 'Reference', 'Image-only attempt', 'Context supplied'][c]} | k={k}",
                fontsize=10,
            )
    fig.suptitle(
        "Previously excluded focus, follow-up GT14\nSame native slices and HU window; author-selected views, never solver input.",
        fontsize=14,
    )
    fig.legend(
        handles=[
            Line2D([0], [0], color=colors[k], lw=2, label=label)
            for k, label in [
                ("gt", "GT: cyan solid"),
                ("old", "Image-only: purple solid"),
                ("new", "Context supplied: orange solid"),
            ]
        ],
        loc="outside lower center",
        ncol=3,
    )
    figure = out / "gt14-comparison.png"
    fig.savefig(figure, dpi=145)
    plt.close(fig)
    evidence = {
        "schema_version": 1,
        "summaries": summaries,
        "per_reference_comparison": rows,
        "context_inference": inferred,
        "context_inference_contract": read(it / "verifier/metrics.json"),
        "predeclared_focus_point_check": point_check,
        "audits": {c: read(BASE / c / "astra-medium/audit.json") for c in states},
        "controls": read(BASE / "controls.json"),
        "provenance": read(BASE / "provenance.json"),
        "figure": {
            "path": str(figure.relative_to(ROOT)),
            "sha256": sha(figure),
            "geometry": "Native i right, j down; k slices 534/536/538; HU [-160,240].",
            "license": "Longitudinal-CT v3, Kuestner/Peisen/Gatidis et al., University Hospital Tuebingen, FDAT, CC BY-NC 4.0.",
        },
        "sources": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [
                it / "artifacts/app/answer/context.json",
                it / "artifacts/app/answer/report.md",
                BASE / "supplied/analysis/evidence.json",
                ROOT / ".local/longitudinal-ct-case02/analysis/evidence.json",
            ]
        },
        "limits": "One patient; one new attempt per condition. Bundled context and run variation are confounded. GT agreement is not independent clinical adjudication. Exact hidden metadata need not be CT-inferable. Individual clinical reports remain unavailable.",
    }
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps({"summaries": summaries, "focus": point_check}, indent=2))


if __name__ == "__main__":
    main()
