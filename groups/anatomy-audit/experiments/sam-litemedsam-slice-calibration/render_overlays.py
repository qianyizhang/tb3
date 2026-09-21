"""Legend-only revision of saved middle-slice overlays; never runs a model."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np

COLORS = {"reference": "#ffffff", "sam2": "#24d7e4", "lite": "#ffae4b", "box": "#ffe46b"}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main(base, output):
    output.mkdir(parents=True, exist_ok=False)
    sources = [base / "samples/manifest.json", base / "samples/arrays.npz"]
    manifest = json.loads(sources[0].read_text())
    assert sha(sources[1]) == manifest["arrays_sha256"]
    arrays = np.load(sources[1])
    masks = {}
    for model in ("sam2", "lite"):
        folder = base / "results" / (model + "-mps")
        receipt = json.loads((folder / "receipt.json").read_text())
        assert sha(folder / "masks.npz") == receipt["masks_sha256"]
        masks[model] = np.load(folder / "masks.npz")
        sources += [folder / "receipt.json", folder / "masks.npz"]
    for condition in ("tight", "loose"):
        fig, axes = plt.subplots(6, 3, figsize=(11, 16), layout="constrained")
        middle = [s for s in manifest["samples"] if s["q"] == .5]
        for row, sample in enumerate(middle):
            key = sample["id"]
            gt = arrays[key + "_gt"]
            x0, y0, x1, y1 = sample["boxes"]["loose"]
            for col, (title, model) in enumerate((("Reference", None), ("SAM 2.1 Small", "sam2"), ("LiteMedSAM", "lite"))):
                ax = axes[row, col]
                ax.imshow(arrays[key + "_image"], origin="upper")
                ax.contour(gt, levels=[.5], colors=COLORS["reference"], linewidths=1)
                if model:
                    pred = masks[model][key + "_" + condition]
                    ax.contour(pred, levels=[.5], colors=COLORS[model], linewidths=1)
                    dice = 2 * np.count_nonzero(pred & gt) / (pred.sum() + gt.sum())
                    title += f" · Dice {dice:.3f}"
                bx0, by0, bx1, by1 = sample["boxes"][condition]
                ax.add_patch(Rectangle((bx0, by0), bx1-bx0, by1-by0, fill=False,
                                      edgecolor=COLORS["box"], linewidth=.8, linestyle="--"))
                ax.set_xlim(max(0, x0-8), min(gt.shape[1], x1+8))
                ax.set_ylim(min(gt.shape[0], y1+8), max(0, y0-8))
                ax.set_title(title, fontsize=11)
                ax.set_xticks([]); ax.set_yticks([])
                if col == 0:
                    ax.set_ylabel(sample["organ"].replace("_", " ") + f"\nk={sample['slice_k']}")
        fig.suptitle(f"{condition.title()} boxes · fixed middle samples", fontsize=14)
        handles = [Line2D([0], [0], color=COLORS[key], lw=2,
                          linestyle="--" if key == "box" else "-", label=label)
                   for key, label in (("reference", "Reference"), ("sam2", "SAM 2.1 Small"),
                                      ("lite", "LiteMedSAM"), ("box", "Prompt box"))]
        fig.legend(handles=handles, loc="outside lower center", ncol=4,
                   facecolor="#252b34", edgecolor="#252b34", labelcolor="white", framealpha=1)
        fig.savefig(output / f"overlays-{condition}.png", dpi=130)
        plt.close(fig)
    record = {"change": "Matching-color legend only; saved masks and original figures retained",
              "renderer_sha256": sha(__file__), "sources": {str(p): sha(p) for p in sources},
              "outputs": {p.name: sha(p) for p in sorted(output.glob("*.png"))}}
    (output / "render-receipt.json").write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    main(args.base.resolve(), args.output.resolve())
