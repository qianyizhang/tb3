"""Render posthoc operation coverage and matched-plane quality, from saved statistics."""

import argparse
import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from analyze import summ

NAMES = {
    "astra-xhigh": "Astra / xhigh",
    "astra-medium": "Astra / medium",
    "sol-xhigh": "Sol / xhigh",
    "astra-medium-litemedsam": "Astra / medium + LiteMedSAM",
}
COLORS = {
    "authored_polygon": "#277da1",
    "explicit_empty_anchor": "#edc266",
    "interpolated_shape": "#b4c8dc",
    "parametric_ellipsoids": "#ac8bc0",
    "explicit_box": "#138a72",
    "interpolated_box": "#a6d8c4",
    "outside_authored_extent": "#c45c65",
}
LABELS = {
    "authored_polygon": "Agent polygon anchor",
    "explicit_empty_anchor": "Agent empty end anchor",
    "interpolated_shape": "Interpolated shape + cleanup",
    "parametric_ellipsoids": "Parametric ellipsoids",
    "explicit_box": "Explicit box → LiteMedSAM",
    "interpolated_box": "Interpolated box → LiteMedSAM",
    "outside_authored_extent": "Outside construction extent",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", type=Path, required=True)
    args = ap.parse_args()
    out = args.analysis
    data = json.loads((out / "metrics.json").read_text())
    rows = json.loads((out / "slices.json").read_text())
    views = json.loads((out / "views.json").read_text())
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
        }
    )
    fig, ax = plt.subplots(figsize=(13, 5.8))
    conditions = list(NAMES)
    for y, c in enumerate(conditions):
        r = data["conditions"][c]
        offset = 0
        for category in COLORS:
            if category not in r["categories"]:
                continue
            n = r["categories"][category]["pooled"]["n"]
            pct = 100 * n / r["active_organ_slices"]
            ax.barh(y, pct, left=offset, color=COLORS[category], height=0.58)
            if pct > 6:
                ax.text(
                    offset + pct / 2,
                    y,
                    f"{pct:.1f}%",
                    ha="center",
                    va="center",
                    color="white"
                    if category in ["authored_polygon", "explicit_box", "outside_authored_extent"]
                    else "#17202b",
                )
            offset += pct
        ax.text(101, y, f"n={r['active_organ_slices']}", va="center", fontsize=10)
    ax.set_yticks(range(4), [NAMES[c] for c in conditions])
    ax.invert_yaxis()
    ax.set_xlim(0, 110)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Percent of organ–slice pairs with GT or final predicted foreground")
    ax.set_title(
        "Sparse authoring covers about one quarter of the Astra outputs",
        loc="left",
        fontweight="bold",
        pad=18,
    )
    ax.legend(
        handles=[Patch(color=COLORS[k], label=LABELS[k]) for k in COLORS],
        loc="upper center",
        bbox_to_anchor=(0.4, -0.22),
        ncol=2,
        frameon=False,
        fontsize=10,
    )
    fig.subplots_adjust(left=0.25, right=0.96, top=0.87, bottom=0.32)
    fig.savefig(out / "construction-coverage.png", dpi=160)
    plt.close(fig)
    baseline = {(r["id"], r["z"]): r for r in rows if r["condition"] == "astra-medium"}
    tool = {(r["id"], r["z"]): r for r in rows if r["condition"] == "astra-medium-litemedsam"}
    paired = []
    fig, axs = plt.subplots(1, 2, figsize=(14, 6.4), sharey=True)
    for ax, category, title in zip(
        axs,
        ["authored_polygon", "interpolated_shape"],
        ["Same baseline anchor planes", "Same baseline between-anchor planes"],
        strict=True,
    ):
        for idx, organ in enumerate(data["conditions"]["astra-medium"]["organs"]):
            keys = [
                k
                for k, r in baseline.items()
                if r["id"] == organ["id"] and r["gt_present"] and r["category"] == category
            ]
            b = summ([baseline[k] for k in keys])
            t = summ([tool[k] for k in keys])
            paired.append({"organ": organ["name"], "category": category, "baseline": b, "tool": t})
            ax.plot([b["dice"], t["dice"]], [idx, idx], color="#adb5bd", linewidth=2)
            ax.scatter(b["dice"], idx, c="#277da1", s=42)
            ax.scatter(t["dice"], idx, c="#e48a27", s=42)
        ax.set_xlim(0, 1.02)
        ax.set_xlabel("Dice within the identical GT-present slice set")
        ax.set_title(title, fontweight="bold")
        ax.grid(axis="x", alpha=0.18)
    axs[0].set_yticks(
        range(10),
        [o["name"].replace("_", " ") for o in data["conditions"]["astra-medium"]["organs"]],
    )
    axs[0].invert_yaxis()
    axs[1].scatter([], [], c="#277da1", label="Astra / medium")
    axs[1].scatter([], [], c="#e48a27", label="+ LiteMedSAM")
    axs[1].legend(loc="upper left", frameon=False)
    fig.suptitle(
        "Tool benefit depends on organ; it is not confined to between-anchor slices",
        fontsize=14,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.012,
        "Posthoc comparison, one case and one attempt per condition. Paired slice sets remove slice-selection differences, not run-to-run variation.",
        ha="center",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(out / "matched-plane-quality.png", dpi=160)
    plt.close(fig)
    gt_z = {r["z"] for r in rows if r["gt_present"]}
    extra = {}
    for c, x in data["conditions"].items():
        cr = [r for r in rows if r["condition"] == c]
        vz = set(map(int, views[c]["axial_slice_counts"]))
        inter = [r for r in cr if r["category"].startswith("interpolated")]
        extra[c] = {
            "gt_union_axial_slices": len(gt_z),
            "displayed_gt_union_axial_slices": len(vz & gt_z),
            "revisited_gt_union_axial_slices": sum(
                int(z) in gt_z and n > 1 for z, n in views[c]["axial_slice_counts"].items()
            ),
            "authored_nonempty_anchor_pairs_all": sum(len(o["anchors"]) for o in x["organs"]),
            "anchors_on_any_displayed_axial_z": sum(
                len(set(o["anchors"]) & vz) for o in x["organs"]
            ),
            "interpolated_pairs_unchanged_after_postprocess": sum(
                r["postprocess_changed"] == 0 for r in inter
            ),
            "interpolated_pairs": len(inter),
            "any_postprocess_change_pairs": sum(r["postprocess_changed"] > 0 for r in cr),
            "whole_macro_raw": x["raw_macro_dice"],
            "whole_macro_final": x["whole_macro_dice"],
        }
    (out / "supplement.json").write_text(
        json.dumps({"matched_per_organ": paired, "coverage_and_processing": extra}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
