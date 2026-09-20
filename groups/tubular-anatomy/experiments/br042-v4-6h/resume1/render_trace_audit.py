"""Render the measured bottlenecks; generated media stay under runs/."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / "runs/br042-resume-trace-audit-20260921"


def main():
    funnel = json.loads((HERE / "candidate-funnel.json").read_text())["results"][0]
    metrics = json.loads((HERE / "evaluation.json").read_text())["metrics"]
    medium = next(r["score"] for r in json.loads((ROOT / "runs/br042-all-vessels-v3/results.json").read_text())["runs"] if r["phase"] == "astra-medium")
    prior = json.loads((HERE.parent / "evaluations/saved-output-review.json").read_text())["comparison"][-1]["metrics"]
    colors = {"geometry": "#327ea5", "labeled": "#218477", "candidate": "#d59425"}
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig = plt.figure(figsize=(13, 8.2), facecolor="white")
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], hspace=.65, wspace=.38)
    fig.suptitle("BR-042: where the extra work stopped helping", fontsize=21, x=.055, ha="left", y=.97)
    fig.text(.055, .919, "One CTA case · original scores preserved · all measurements below use the 1 mm tolerance", color="#52616d")
    ax = fig.add_subplot(gs[0, 0])
    labels = ["V3 medium\n46m 34s, complete", "V4 xhigh\n2h 48m, interrupted", "Same session resumed\n4h 14m combined, complete"]
    geom = [100 * m["geometry"]["length_weighted_recall_1mm"] for m in [medium, prior, metrics]]
    lab = [100 * m["labeled"]["length_weighted_recall_1mm"] for m in [medium, prior, metrics]]
    y = np.arange(3)
    ax.barh(y - .17, geom, .29, color=colors["geometry"], label="Geometry")
    ax.barh(y + .17, lab, .29, color=colors["labeled"], label="Correct label")
    for i, (g, l) in enumerate(zip(geom, lab)):
        ax.text(g + 1, i - .17, f"{g:.1f}%", va="center", fontsize=10)
        ax.text(l + 1, i + .17, f"{l:.1f}%", va="center", fontsize=10)
    ax.set(yticks=y, yticklabels=labels, xlim=(0, 108), xlabel="Reference-length coverage (%)")
    ax.invert_yaxis()
    ax.set_title("Same aggregate score after resume", loc="left", fontweight="bold", pad=14)
    ax.legend(frameon=False, ncol=2, loc="lower right", bbox_to_anchor=(1.02, -.5), fontsize=10)
    ax = fig.add_subplot(gs[0, 1])
    keys = ["D2", "OM1", "OM2", "Other"]
    rows = [metrics["per_reference_category"][str(k)] for k in [5, 6, 7, 14]]
    gv = [r["geometry_recall_1mm"] * 100 for r in rows]
    lv = [r["labeled_recall_1mm"] * 100 for r in rows]
    y = np.arange(4)
    ax.barh(y - .17, gv, .29, color=colors["geometry"])
    ax.barh(y + .17, lv, .29, color=colors["labeled"])
    for i, (g, l) in enumerate(zip(gv, lv)):
        ax.text(g + 1, i - .17, f"{g:.1f}%", va="center", fontsize=10)
        ax.text(l + 1, i + .17, f"{l:.0f}%", va="center", fontsize=10)
    ax.set(yticks=y, yticklabels=keys, xlim=(0, 114), xlabel="Within each reference category (%)")
    ax.invert_yaxis()
    ax.set_title("Small misses also shift downstream names", loc="left", fontweight="bold", pad=14)
    ax = fig.add_subplot(gs[1, 0])
    stages = ["skeleton", "after_existing_path_exclusion", "after_size_filter", "accepted_components"]
    stage_labels = ["Raw\nskeleton", "Remove near\nexisting paths", "Component\nsize filter", "Parent-gap\nfilter", "Final\nsubmission"]
    for name, color, key in [("D2", colors["candidate"], "5"), ("OM1", "#b65365", "6")]:
        vals = [funnel["branches"][name][s]["coverage_1mm"] * 100 for s in stages]
        vals.append(metrics["per_reference_category"][key]["geometry_recall_1mm"] * 100)
        ax.plot(range(5), vals, "o-", lw=2.5, ms=7, color=color, label=name)
        for i, v in enumerate(vals):
            dy = 6 if name == "D2" else -10
            if v < 5: dy = 6 if name == "D2" else -11
            ax.annotate(f"{v:.1f}", (i, v), xytext=(0, dy), textcoords="offset points", ha="center", fontsize=10, color=color)
    ax.set(xticks=range(5), xticklabels=stage_labels, ylim=(-13, 109), ylabel="Reference coverage by nearby points (%)")
    ax.tick_params(axis="x", labelsize=9)
    ax.legend(frameon=False, loc="center right")
    ax.set_title("Replayed pipeline: two different failure stages", loc="left", fontweight="bold", pad=14)
    ax.text(0, -.33, "Candidate points are unordered; this is not a recovered-vessel score.", transform=ax.transAxes, fontsize=9, color="#52616d")
    ax = fig.add_subplot(gs[1, 1])
    ax.axis("off")
    notes = [
        ("D2: candidate rejected", "Candidate #3 has 87 points and covers 87.8%.\nIt is withheld as a possible tissue ridge."),
        ("OM1: candidate discarded", "A 13-voxel fragment is 4.55 mm from accepted paths.\nThe fixed parent-gap cutoff is 2.2 mm."),
        ("No demonstrated GT-imposed ceiling", "Reference self-score: 100%. Pure relabeling cannot fix\nthe remaining geometry: category-mean coverage is 75.5%."),
    ]
    for y, (title, body) in zip([.96, .62, .28], notes):
        ax.text(0, y, title, transform=ax.transAxes, va="top", fontsize=12, fontweight="bold")
        ax.text(0, y - .105, body, transform=ax.transAxes, va="top", fontsize=10, linespacing=1.55, color="#3d4d59")
    fig.subplots_adjust(left=.20, right=.965, top=.85, bottom=.13)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "bottlenecks.png", dpi=170, facecolor="white")
    plt.close(fig)
    print(OUT / "bottlenecks.png")


if __name__ == "__main__":
    main()
