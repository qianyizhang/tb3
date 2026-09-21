"""Replay saved masks, summarize timings and render the prespecified middle slices."""

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

from bench import BASE, ORGANS, sha


def overlap(a, b):
    counts = np.bincount(a.astype(np.uint8).ravel() * 2 + b.astype(np.uint8).ravel(), minlength=4)
    tn, fn, fp, tp = map(int, counts)
    return dict(dice=2 * tp / (2 * tp + fp + fn),
                precision=tp / (tp + fp) if tp + fp else 0., recall=tp / (tp + fn))


def main():
    out = BASE / "summary"
    out.mkdir(exist_ok=True)
    manifest = json.loads((BASE / "samples/manifest.json").read_text())
    arrays = np.load(BASE / "samples/arrays.npz")
    provenance = json.loads((BASE / "provisioning.json").read_text())
    result = dict(scope="One CT, six organs, three reference-selected slices per organ; oracle box calibration",
                  provenance=provenance, aggregates={}, per_organ=[], parity=[], controls={}, files={})
    predictions, receipts = {}, {}
    for tag in ("sam2-mps", "lite-mps", "sam2-cpu-subset", "lite-cpu-subset", "sam2-cpu"):
        folder = BASE / "results" / tag
        receipt = json.loads((folder / "receipt.json").read_text())
        assert sha(folder / "masks.npz") == receipt["masks_sha256"]
        assert sha(BASE / "samples/manifest.json") == receipt["sample_manifest_sha256"]
        masks = np.load(folder / "masks.npz")
        for row in receipt["rows"]:
            recomputed = overlap(masks[row["id"] + "_" + row["condition"]], arrays[row["id"] + "_gt"])
            for metric in recomputed:
                assert abs(row[metric] - recomputed[metric]) < 1e-12
        predictions[tag], receipts[tag] = masks, receipt
        result["files"][tag] = dict(receipt_sha256=sha(folder / "receipt.json"),
                                   masks_sha256=receipt["masks_sha256"])
        result["aggregates"][tag] = dict(
            count=receipt["prediction_count"], load_seconds=receipt["load_seconds"],
            warmup_seconds=receipt["warmup_seconds"], process_peak_rss_mib=receipt["process_peak_rss_bytes"] / 2**20,
            encode_median_ms=float(np.median([r["encode_seconds"] for r in receipt["rows"]])) * 1000,
            prompt_median_ms=float(np.median([r["decode_seconds"] for r in receipt["rows"]])) * 1000,
            driver_memory_max_observed_mib=max([r.get("mps_driver_allocated_bytes_observed", 0) for r in receipt["rows"]]) / 2**20)
        for condition in ("tight", "loose"):
            rows = [r for r in receipt["rows"] if r["condition"] == condition]
            result["aggregates"][tag][condition] = dict(
                mean_dice=float(np.mean([r["dice"] for r in rows])),
                median_dice=float(np.median([r["dice"] for r in rows])),
                mean_hd95_mm=float(np.mean([r["hd95_mm"] for r in rows if r["hd95_mm"] is not None])))
    box_scores = {"tight": [], "loose": []}
    for s in manifest["samples"]:
        gt = arrays[s["id"] + "_gt"]
        assert overlap(gt, gt)["dice"] == 1
        assert overlap(np.zeros_like(gt), gt)["dice"] == 0
        for condition, (x0, y0, x1, y1) in s["boxes"].items():
            rectangle = np.zeros_like(gt)
            rectangle[y0:y1, x0:x1] = True
            box_scores[condition].append(overlap(rectangle, gt)["dice"])
    result["controls"] = dict(exact_mask_dice=1., empty_mask_dice=0.,
        independent_mask_replays=sum(r["prediction_count"] for r in receipts.values()),
        filled_box_mean_dice={k:float(np.mean(v)) for k,v in box_scores.items()})
    for model in ("sam2", "lite"):
        cpu_tag = "sam2-cpu" if model == "sam2" else "lite-cpu-subset"
        for row in receipts[cpu_tag]["rows"]:
            key = row["id"] + "_" + row["condition"]
            cpu, mps = predictions[cpu_tag][key], predictions[model + "-mps"][key]
            result["parity"].append(dict(model=model, id=row["id"], condition=row["condition"],
                differing_pixels=int(np.count_nonzero(cpu != mps)),
                cpu_mps_mask_dice=overlap(cpu, mps)["dice"]))
    for organ in ORGANS:
        row = dict(organ=organ)
        for model in ("sam2", "lite"):
            for condition in ("tight", "loose"):
                rows = [r for r in receipts[model + "-mps"]["rows"] if r["organ"] == organ and r["condition"] == condition]
                row[model + "_" + condition] = float(np.mean([r["dice"] for r in rows]))
        result["per_organ"].append(row)
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    with (out / "per-organ.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=result["per_organ"][0].keys())
        writer.writeheader(); writer.writerows(result["per_organ"])
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(11, 5.2), layout="constrained")
    x = np.arange(len(ORGANS))
    palette = ["#277da8", "#93c4d7", "#ba641d", "#edb77d"]
    for i, key in enumerate(("sam2_tight", "sam2_loose", "lite_tight", "lite_loose")):
        label = key.replace("sam2", "SAM 2.1").replace("lite", "LiteMedSAM").replace("_", " · ")
        ax.bar(x + (i - 1.5) * .2, [r[key] for r in result["per_organ"]], .19, label=label, color=palette[i])
    ax.set_xticks(x, ["Liver", "Right kidney", "Gallbladder", "Pancreas", "Right adrenal", "Duodenum"])
    ax.set_ylim(0, 1.05); ax.set_ylabel("Mean 2D Dice (3 slices per organ)")
    ax.set_title("LiteMedSAM tolerates wider boxes better on this CT", loc="left", weight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=2, loc="lower left", framealpha=.95)
    fig.text(.01, -.03, "One patient · 18 organ-slice pairs · reference-derived boxes · tighter +3 mm / wider +15 mm · not full-volume or autonomous scores", fontsize=9)
    fig.savefig(out / "comparison.png", dpi=160, bbox_inches="tight"); plt.close(fig)
    middle = [s for s in manifest["samples"] if s["q"] == .5]
    for condition in ("tight", "loose"):
        fig, axes = plt.subplots(6, 3, figsize=(11, 16), layout="constrained")
        for row, s in enumerate(middle):
            key = s["id"]; gt = arrays[key + "_gt"]
            x0, y0, x1, y1 = s["boxes"]["loose"]
            for col, (title, model, color) in enumerate((("Reference", None, "white"),
                    ("SAM 2.1 Small", "sam2", "#24d7e4"), ("LiteMedSAM", "lite", "#ffae4b"))):
                ax = axes[row, col]
                ax.imshow(arrays[key + "_image"], origin="upper")
                ax.contour(gt, levels=[.5], colors="white", linewidths=1)
                if model:
                    pred = predictions[model + "-mps"][key + "_" + condition]
                    ax.contour(pred, levels=[.5], colors=color, linewidths=1)
                    score = overlap(pred, gt)["dice"]
                    title += f" · Dice {score:.3f}"
                bx0, by0, bx1, by1 = s["boxes"][condition]
                ax.add_patch(Rectangle((bx0, by0), bx1-bx0, by1-by0, fill=False,
                                      edgecolor="#ffe46b", linewidth=.8, linestyle="--"))
                ax.set_xlim(max(0,x0-8), min(gt.shape[1],x1+8))
                ax.set_ylim(min(gt.shape[0],y1+8), max(0,y0-8))
                ax.set_title(title, fontsize=11); ax.set_xticks([]); ax.set_yticks([])
                if col == 0:
                    ax.set_ylabel(s["organ"].replace("_", " ") + f"\nk={s['slice_k']}")
        fig.suptitle(f"{condition.title()} boxes · fixed middle samples\nWhite: reference | cyan/orange: prediction | dashed yellow: prompt", fontsize=14)
        fig.savefig(out / f"overlays-{condition}.png", dpi=130); plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
