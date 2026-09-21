"""Analyze saved artifacts only; never run inference or change frozen outputs."""

from pathlib import Path
import json
import numpy as np
import nibabel as nib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe


def main():
    root = Path(__file__).resolve().parents[5]
    base = root / ".local/ct-organ-segmentation-astra-medium-litemedsam"
    out = base / "review"
    out.mkdir(exist_ok=True)
    analysis = json.loads((base / "analysis.json").read_text())
    rows = analysis["per_organ"]
    pretty = {
        r["id"]: r["name"].replace("adrenal_gland", "adrenal").replace("_", " ").title()
        for r in rows
    }
    colors = {
        "reference": "#ffffff",
        "baseline": "#ed8936",
        "tool": "#00d8e8",
        "xhigh": "#7e57c2",
        "sol": "#999999",
    }
    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(10)
    for i, r in enumerate(rows):
        ax.plot([r["baseline_dice"], r["tool_dice"]], [i, i], color="#b8bcc4", lw=3)
    ax.scatter(
        [r["baseline_dice"] for r in rows], y, c=colors["baseline"], s=65, label="Astra medium"
    )
    ax.scatter(
        [r["tool_dice"] for r in rows],
        y,
        c=colors["tool"],
        edgecolors="#087b83",
        s=65,
        label="Astra medium + LiteMedSAM",
    )
    for i, r in enumerate(rows):
        ax.text(1.025, i, f"{r['delta_dice']:+.3f}", va="center", fontsize=10)
    ax.set_yticks(y, [pretty[r["id"]] for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.13)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_xlabel("Frozen 3D per-organ Dice")
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left")
    ax.set_title(
        "Seven organ Dice scores increase; three decrease\nMacro Dice 0.7342 → 0.7570  |  one case, one attempt per condition",
        loc="left",
        pad=18,
    )
    ax.text(1.025, -0.85, "Δ Dice", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "per-organ-dice.png", dpi=180)
    plt.close(fig)
    ct = np.asarray(
        nib.load(
            root
            / ".local/freezes/669d0880fa05c172ca1b658fce844a5c86e552d91ce2fce1e06659bb9e2808cb/task/environment/data/ct.nii.gz"
        ).dataobj
    )
    gtroot = (
        root
        / ".local/freezes/669d0880fa05c172ca1b658fce844a5c86e552d91ce2fce1e06659bb9e2808cb/task/tests/reference"
    )
    broot = (
        root
        / ".local/attempts/attempt-6979f136149c4e17/job/task__oAtf7Dx/artifacts/app/answer/masks"
    )
    troot = (
        root
        / ".local/attempts/attempt-bc57d5f3973843bc/job/task__WhR5ASN/artifacts/app/answer/masks"
    )
    selection = []

    def overlays(ids, filename):
        fig, axes = plt.subplots(
            len(ids), 3, figsize=(11, 3.5 * len(ids)), squeeze=False, facecolor="#151922"
        )
        for row, id in enumerate(ids):
            fn = f"{id:02}.nii.gz"
            g = np.asarray(nib.load(gtroot / fn).dataobj) > 0
            b = np.asarray(nib.load(broot / fn).dataobj) > 0
            t = np.asarray(nib.load(troot / fn).dataobj) > 0
            k = int(g.sum((0, 1)).argmax())
            masks = [g[:, :, k].T, b[:, :, k].T, t[:, :, k].T]
            points = np.argwhere(masks[0] | masks[1] | masks[2])
            lo = np.maximum(points.min(0) - 12, 0)
            hi = np.minimum(points.max(0) + 13, masks[0].shape)
            selection.append(
                {
                    "organ": id,
                    "axial_k": k,
                    "rule": "largest axial GT cross-section; same slice/crop for all conditions",
                    "crop_yx": [lo.tolist(), hi.tolist()],
                }
            )
            for col, ax in enumerate(axes[row]):
                ax.imshow(ct[:, :, k].T, cmap="gray", vmin=-160, vmax=240, origin="lower")
                co = ax.contour(
                    masks[0], levels=[0.5], colors=[colors["reference"]], linewidths=1.1
                )
                co.set_path_effects([pe.Stroke(linewidth=2.1, foreground="black"), pe.Normal()])
                if col:
                    ax.contour(
                        masks[col],
                        levels=[0.5],
                        colors=[colors["baseline" if col == 1 else "tool"]],
                        linewidths=1.2,
                    )
                ax.set_xlim(lo[1], hi[1])
                ax.set_ylim(lo[0], hi[0])
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_facecolor("#151922")
                r = rows[id - 1]
                title = (
                    pretty[id] + " · GT"
                    if col == 0
                    else ("Astra medium" if col == 1 else "+ LiteMedSAM")
                    + f" · Dice {r['baseline_dice' if col == 1 else 'tool_dice']:.3f}"
                )
                ax.set_title(title, color="white", fontsize=11)
                if col == 0:
                    ax.set_ylabel(f"axial k={k}", color="white")
        handles = [
            Line2D(
                [0],
                [0],
                color=colors[n],
                lw=2,
                label=label,
                path_effects=[pe.Stroke(linewidth=3, foreground="black"), pe.Normal()]
                if n == "reference"
                else [],
            )
            for n, label in [
                ("reference", "Reference"),
                ("baseline", "Astra medium"),
                ("tool", "Astra medium + LiteMedSAM"),
            ]
        ]
        fig.legend(
            handles=handles,
            loc="lower center",
            ncol=3,
            facecolor="#222631",
            labelcolor="white",
            edgecolor="none",
        )
        fig.suptitle(
            "Same CT slice and crop · contours from unchanged frozen masks",
            color="white",
            fontsize=14,
        )
        fig.tight_layout(rect=(0, 0.04, 1, 0.96))
        fig.savefig(out / filename, dpi=170, facecolor=fig.get_facecolor())
        plt.close(fig)

    overlays([6, 4, 8], "selected-boundaries.png")
    overlays([1, 2, 3, 5, 7, 9, 10], "remaining-boundaries.png")
    (out / "slice-selection.json").write_text(json.dumps(selection, indent=2) + "\n")


if __name__ == "__main__":
    main()
