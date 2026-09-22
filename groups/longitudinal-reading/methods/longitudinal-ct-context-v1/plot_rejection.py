"""Native CT illustration of the new attempt's explicitly rejected GT2 focus."""

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


def main():
    state = json.loads((BASE / "supplied/astra-medium/operator-state.json").read_text())
    task = ROOT / ".local/freezes" / state["task_digest"] / "task"
    trial = Path(state["trial_path"])
    out = BASE / "comparison/explicit-gt2-rejection.png"
    assert not out.exists()
    fig, axes = plt.subplots(2, 3, figsize=(10, 7), layout="constrained")
    colors = {"gt": "#20c7dc", "pred": "#ffb34d"}
    for r, (visit, point) in enumerate(
        [("baseline", (190, 199, 406)), ("followup", (182, 165, 524))]
    ):
        x, y, k = point
        ct = np.asarray(nib.load(task / "environment/data" / f"{visit}.nii.gz").dataobj[:, :, k]).T
        gt = np.asarray(
            nib.load(task / "tests/reference" / f"{visit}_instances.nii.gz").dataobj[:, :, k]
        ).T
        pred = np.asarray(
            nib.load(trial / "artifacts/app/answer" / f"{visit}_instances.nii.gz").dataobj[:, :, k]
        ).T
        assert gt[y, x] == 2
        for c, key in enumerate(["ct", "gt", "pred"]):
            ax = axes[r, c]
            ax.imshow(ct, cmap="gray", vmin=-160, vmax=240, origin="upper")
            if key == "gt":
                ax.contour(gt == 2, levels=[0.5], colors=[colors[key]], linewidths=1.2)
            elif key == "pred" and np.any(pred[y - 32 : y + 33, x - 32 : x + 33]):
                ax.contour(pred > 0, levels=[0.5], colors=[colors[key]], linewidths=1.2)
            ax.set_xlim(x - 32, x + 32)
            ax.set_ylim(y + 32, y - 32)
            ax.axis("off")
            ax.set_title(
                f"{visit}, k={k} | {['CT', 'GT2 reference', 'Context-supplied output'][c]}",
                fontsize=10,
            )
    fig.suptitle(
        "Explicitly excluded as cyst-like or vascular\nBoth reported coordinates lie inside source GT2; both masks omit it.",
        fontsize=13,
    )
    fig.legend(
        handles=[
            Line2D([0], [0], color=color, lw=2, label=label)
            for color, label in [
                (colors["gt"], "GT2: cyan solid"),
                (colors["pred"], "Prediction: orange solid (absent here)"),
            ]
        ],
        loc="outside lower center",
        ncol=2,
    )
    fig.savefig(out, dpi=145)
    plt.close(fig)
    (out.with_suffix(".json")).write_text(
        json.dumps(
            {
                "path": str(out.relative_to(ROOT)),
                "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                "geometry": "Native i right, j down; 64-voxel crops at reported points; HU [-160,240].",
                "meaning": "Post-hoc reference agreement illustration, not clinical adjudication or solver input.",
                "source": "Longitudinal-CT v3, Kuestner/Peisen/Gatidis et al., University Hospital Tuebingen, FDAT, CC BY-NC 4.0.",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
