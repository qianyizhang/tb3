"""Replay saved scores, measure coverage and render author-only comparison views."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-image-only-v2"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def agree(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(agree(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(agree(x, y) for x, y in zip(a, b))
    return a == b or (isinstance(a, float) and isinstance(b, float) and abs(a - b) <= 1e-12)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("setting", choices=["whole-volume", "localized"])
    args = parser.parse_args()
    base = BASE / args.setting
    state = json.loads((base / "astra-medium/operator-state.json").read_text())
    assert state["condition_status"] == "completed"
    study = json.loads((base / "study.json").read_text())
    assert state["task_digest"] == study["task_digest"]
    trial = Path(state["trial_path"])
    task = ROOT / ".local/freezes" / state["task_digest"] / "task"
    answer = trial / "artifacts/app/answer"
    out = base / "analysis"
    out.mkdir(exist_ok=False)
    command = [
        str(ROOT / ".venv-br037/bin/python"),
        str(task / "tests/score.py"),
        "--answer",
        str(answer),
        "--reference",
        str(task / "tests/reference"),
        "--output",
        str(out / "replay"),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    (out / "replay.log").write_text(result.stdout + result.stderr)
    replay = json.loads((out / "replay/metrics.json").read_text())
    metrics = json.loads((trial / "verifier/metrics.json").read_text())
    assert agree(replay, metrics)
    previous_path = (
        ROOT / ".local/longitudinal-ct-image-only-v1/astra-medium/operator-state.json"
        if args.setting == "whole-volume"
        else BASE / "whole-volume/astra-medium/operator-state.json"
    )
    previous = json.loads(previous_path.read_text())
    previous_answer = Path(previous["trial_path"]) / "artifacts/app/answer"
    previous_title = (
        "Original Astra" if args.setting == "whole-volume" else "Revised whole-volume Astra"
    )
    visits, coverage, rows = {}, {}, []
    for visit in ["baseline", "followup"]:
        image = nib.load(task / "environment/data" / f"{visit}.nii.gz")
        gt = np.asarray(nib.load(task / "tests/reference" / f"{visit}_instances.nii.gz").dataobj)
        pred = np.asarray(nib.load(answer / f"{visit}_instances.nii.gz").dataobj)
        old = np.asarray(nib.load(previous_answer / f"{visit}_instances.nii.gz").dataobj)
        visits[visit] = {"image": image, "gt": gt, "pred": pred, "old": old}
        coverage[visit] = {}
        for label in np.unique(gt)[1:]:
            xyz = np.argwhere(gt == label)
            k = int(np.count_nonzero(gt == label, axis=(0, 1)).argmax())
            xy = np.argwhere(gt[:, :, k] == label).mean(axis=0)
            row = {
                "voxels": len(xyz),
                "volume_ml": float(len(xyz) * np.prod(image.header.get_zooms()) / 1000),
                "covered_fraction": float((pred[gt == label] > 0).mean()),
                "centroid_ijk": xyz.mean(axis=0).tolist(),
                "max_area_k": k,
            }
            coverage[visit][str(int(label))] = row
            rows.append((visit, int(label), k, xy))
    groups = json.loads((task / "tests/reference/events.json").read_text())["groups"]
    candidates = []
    for group in groups:
        members = [(visit, label) for visit in visits for label in group[visit + "_ids"]]
        if any(coverage[visit][str(label)]["covered_fraction"] < 0.1 for visit, label in members):
            volume = sum(coverage[visit][str(label)]["volume_ml"] for visit, label in members)
            candidates.append((group["event"] != "persistent", -volume, str(group), group))
    selected = sorted(candidates, key=lambda x: x[:3])[0][3] if candidates else None
    fig, axes = plt.subplots(
        len(rows), 4, figsize=(14, 3.2 * len(rows)), squeeze=False, layout="constrained"
    )
    colors = ["#28c8d8", "#ffb34d", "#d868ed"]
    for r, (visit, label, k, center) in enumerate(rows):
        entry = visits[visit]
        plane = np.asarray(entry["image"].dataobj[:, :, k]).T
        half = 75 / float(entry["image"].header.get_zooms()[0])
        for c in range(4):
            ax = axes[r, c]
            ax.imshow(plane, cmap="gray", vmin=-160, vmax=240, origin="upper")
            if c:
                mask = entry[["gt", "old", "pred"][c - 1]][:, :, k].T
                for ident in np.unique(mask)[1:]:
                    region = mask == ident
                    if region.any():
                        ax.contour(region, levels=[0.5], colors=[colors[c - 1]], linewidths=0.8)
                        pos = np.argwhere(region).mean(axis=0)[::-1]
                        if np.all(np.abs(pos - center) < half):
                            ax.text(
                                pos[0],
                                pos[1],
                                str(int(ident)),
                                color=colors[c - 1],
                                fontsize=9,
                                clip_on=True,
                                bbox={"facecolor": "black", "alpha": 0.6, "edgecolor": "none"},
                            )
            ax.set_xlim(center[0] - half, center[0] + half)
            ax.set_ylim(center[1] + half, center[1] - half)
            ax.set_title(
                [
                    f"CT | {visit}, GT {label}, k={k}",
                    "Reference",
                    previous_title,
                    "Revised Astra" if args.setting == "whole-volume" else "Localized Astra",
                ][c],
                fontsize=10,
            )
            ax.axis("off")
    fig.suptitle(
        f"{args.setting}: saved predictions on native CT\nCyan reference / amber previous / purple new; solid contours. Native i right, j down; HU [-160, 240].\nGT-selected maximum-area slices; 150 mm crops. These are author-only views, not solver inputs.\nLongitudinal-CT v3, FDAT, CC BY-NC 4.0; derived review.",
        fontsize=11,
    )
    fig.savefig(out / "comparison.png", dpi=135)
    plt.close(fig)
    evidence = {
        "setting": args.setting,
        "attempt_id": state["attempt_id"],
        "task_digest": state["task_digest"],
        "metrics": metrics,
        "independent_replay_exact": replay == metrics,
        "replay_within_1e12": True,
        "coverage": coverage,
        "localized_trigger": {
            "threshold": 0.1,
            "triggered": selected is not None,
            "selected_reference_group": selected,
            "scope": "Author-only adaptive selection; not input to whole-volume agent",
        },
        "report": (answer / "report.md").read_text(),
        "events": json.loads((answer / "events.json").read_text()),
        "source_files": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [
                trial / "agent/trajectory.json",
                trial / "verifier/metrics.json",
                task / "instruction.md",
                *sorted(answer.glob("*")),
            ]
            if p.is_file()
        },
        "figure": {
            "path": str((out / "comparison.png").relative_to(ROOT)),
            "sha256": sha(out / "comparison.png"),
        },
    }
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: evidence[k]
                for k in [
                    "setting",
                    "attempt_id",
                    "independent_replay_exact",
                    "metrics",
                    "coverage",
                    "localized_trigger",
                    "report",
                    "events",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
