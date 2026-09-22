"""Native CT panels for the previous recognition disagreement and new recovery."""

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-curation-v1"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    new_state = read(BASE / "astra-medium/operator-state.json")
    old_state = read(
        ROOT / ".local/longitudinal-ct-context-v1/supplied/astra-medium/operator-state.json"
    )
    task = ROOT / ".local/freezes" / new_state["task_digest"] / "task"
    new_answer = Path(new_state["trial_path"]) / "artifacts/app/answer"
    old_answer = Path(old_state["trial_path"]) / "artifacts/app/answer"
    comparison = read(BASE / "comparison.json")
    geometry = read(BASE / "review/geometry.json")
    by_key = {(r["visit"], r["gt_id"]): r for r in comparison["per_reference_transitions"]}
    # First two rows revisit the prior explicit rejection, regardless of outcome.
    selection = [("baseline", 2), ("followup", 2)]
    gains = [k for k, r in by_key.items() if r["transition"] == "gained" and k not in selection]
    losses = [k for k, r in by_key.items() if r["transition"] == "lost" and k not in selection]
    misses = [
        k for k, r in by_key.items() if r["transition"] == "still_missed" and k not in selection
    ]
    selection.extend((gains[:1] + losses[:1] + gains[1:] + losses[1:])[:2])
    if len(selection) < 4:
        selection.extend(misses[: 4 - len(selection)])
    fig, axes = plt.subplots(len(selection), 4, figsize=(13, 3.0 * len(selection)), squeeze=False)
    records = []
    inputs = []
    for visit in ["baseline", "followup"]:
        image_path = task / "environment/data" / f"{visit}.nii.gz"
        gt_path = task / "tests/reference" / f"{visit}_instances.nii.gz"
        old_path = old_answer / f"{visit}_instances.nii.gz"
        new_path = new_answer / f"{visit}_instances.nii.gz"
        image = nib.load(image_path)
        data = np.asarray(image.dataobj)
        masks = [np.asarray(nib.load(p).dataobj) for p in [gt_path, old_path, new_path]]
        inputs.extend([image_path, gt_path, old_path, new_path])
        info = {r["id"]: r for r in geometry["visits"][visit]["labels"]}
        for row_index, (selected_visit, ident) in enumerate(selection):
            if selected_visit != visit:
                continue
            meta = info[ident]
            k = meta["max_area_k"]
            xy = np.argwhere(masks[0][:, :, k] == ident)
            center = xy.mean(0)
            zoom = float(image.header.get_zooms()[0])
            crop_mm = max(55.0, float((xy.max(0) - xy.min(0)).max() * zoom + 20))
            half = crop_mm / (2 * zoom)
            window = (-200, 1000) if meta["anatomy"] == "Skeleton" else (0, 150)
            transition = by_key[(visit, ident)]
            assessment = transition["candidate_assessment"]
            for column, ax in enumerate(axes[row_index]):
                ax.imshow(
                    data[:, :, k].T, cmap="gray", vmin=window[0], vmax=window[1], origin="upper"
                )
                if column:
                    mask = masks[column - 1][:, :, k].T
                    color = ["#20c7dc", "#aa6fe8", "#f8a33d"][column - 1]
                    for value in np.unique(mask):
                        if value:
                            ax.contour(mask == value, levels=[0.5], colors=[color], linewidths=1.2)
                ax.set_xlim(center[0] - half, center[0] + half)
                ax.set_ylim(center[1] + half, center[1] - half)
                ax.set_xticks([])
                ax.set_yticks([])
                label = ["Raw CT", "GT", "Previous context", "Comprehensive curation"][column]
                suffix = f"; p={assessment['p_tumor']:.2f}" if column == 3 and assessment else ""
                ax.set_title(f"{label}{suffix}", fontsize=10)
            axes[row_index, 0].set_ylabel(
                f"{visit} GT{ident} · {transition['transition']}\nk={k}, {meta['volume_ml']:.3f} mL",
                fontsize=10,
            )
            records.append(
                {
                    "visit": visit,
                    "gt_id": ident,
                    "native_k": k,
                    "crop_center_ij": center.tolist(),
                    "crop_mm": crop_mm,
                    "window_hu": list(window),
                    "transition": transition["transition"],
                    "candidate_assessment": assessment,
                }
            )
        del masks, data
    fig.suptitle(
        "Comprehensive curation: native CT and saved masks\nGT-selected crops for explanation only; not solver inputs",
        fontsize=14,
    )
    fig.legend(
        [Line2D([0], [0], color=c, lw=2) for c in ["#20c7dc", "#aa6fe8", "#f8a33d"]],
        ["GT: cyan solid", "Previous: purple solid", "New: orange solid"],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.035),
        ncol=3,
    )
    fig.text(
        0.5,
        0.012,
        "Native i right / j down; axial, no resampling. Longitudinal-CT v3 (FDAT), CC BY-NC 4.0.",
        ha="center",
        fontsize=9,
    )
    fig.subplots_adjust(left=0.11, right=0.99, top=0.91, bottom=0.08, wspace=0.06, hspace=0.22)
    path = BASE / "analysis/curation-comparison.png"
    assert not path.exists()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    manifest = {
        "figure": str(path.relative_to(ROOT)),
        "sha256": sha(path),
        "selection": "GT2 at both visits revisits the prior explicit rejection; then gains and losses when present, otherwise still-missed targets. Author-selected, not representative sampling.",
        "panels": records,
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
        "limits": "Contour absence at one plane is illustrated; 3D detection is determined separately by the frozen scorer. Probability shown only for a strictly matched candidate. No clinical adjudication.",
    }
    (BASE / "analysis/curation-comparison.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
