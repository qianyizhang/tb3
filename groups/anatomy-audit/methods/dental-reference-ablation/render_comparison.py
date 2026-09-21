"""Author-only paired metrics and native-grid visuals; never changes solver outputs."""

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
BATCH = ROOT / ".local/dental-reference-ablation-20260921"
OUT = BATCH / "comparison"
EXPS = ["dental-f002-contract-v2-astra-medium", "dental-f002-reference-v2-astra-medium"]
NAMES = ["No example", "With F008 example"]
COLORS = ["#0072B2", "#D55E00"]
GT_COLOR = "#00C99B"
PRED_COLOR = "#E76BF3"


def load_data():
    records, predictions, states = [], [], []
    for exp in EXPS:
        base = ROOT / ".local" / exp
        state = json.loads((base / "operator-state.json").read_text())
        assert state["state"] == "terminal"
        metrics = json.loads((base / "replay/metrics.json").read_text())
        records.append(metrics)
        states.append(state)
        p = Path(state["trial_path"]) / "artifacts/app/answer/segmentation.nii.gz"
        predictions.append(np.asanyarray(nib.load(p).dataobj).astype(np.uint8))
    task = ROOT / ".local" / EXPS[0] / "task"
    ct = np.asanyarray(nib.load(task / "environment/data/ct.nii.gz").dataobj).astype(np.float32)
    gt = np.asanyarray(nib.load(task / "tests/reference.nii.gz").dataobj).astype(np.uint8)
    return records, predictions, states, ct, gt


def pooled(gt, prediction, ids):
    g = np.isin(gt, ids)
    p = np.isin(prediction, ids)
    intersection = int(np.count_nonzero(g & p))
    gc, pc = int(g.sum()), int(p.sum())
    return {
        "gt_voxels": gc,
        "prediction_voxels": pc,
        "intersection": intersection,
        "precision": intersection / pc if pc else None,
        "recall": intersection / gc if gc else None,
        "dice": 2 * intersection / (gc + pc) if gc + pc else None,
    }


def overview(records):
    keys = [
        ("All-label macro Dice", lambda r: r["macro_dice"]),
        (
            "Whole-tooth shape Dice",
            lambda r: r["whole_tooth_geometry_and_identity"][
                "geometry_mean_dice_with_unmatched_zero"
            ],
        ),
        (
            "Correct tooth identity / GT count",
            lambda r: r["whole_tooth_geometry_and_identity"]["correctly_identified_gt_recall"],
        ),
        ("Pulp macro Dice", lambda r: r["groups"]["pulp"]["macro_dice"]),
        ("Main-canal macro Dice", lambda r: r["groups"]["inferior_alveolar_canals"]["macro_dice"]),
        ("Small-canal macro Dice", lambda r: r["groups"]["small_canals"]["macro_dice"]),
        ("Jawbone macro Dice", lambda r: r["groups"]["jawbones"]["macro_dice"]),
        ("Sinus macro Dice", lambda r: r["groups"]["sinuses"]["macro_dice"]),
        ("Pharynx Dice", lambda r: r["groups"]["pharynx"]["macro_dice"]),
        (
            "Restoration pooled Dice",
            lambda r: r["groups"]["restoration_subtypes_under_review"]["pooled_geometry_dice"],
        ),
    ]
    fig, ax = plt.subplots(figsize=(10, 6.7))
    y = np.arange(len(keys))
    for n, record in enumerate(records):
        values = [f(record) for _, f in keys]
        ax.scatter(
            values,
            y + (n - 0.5) * 0.22,
            color=COLORS[n],
            s=48,
            marker="o" if n == 0 else "D",
            label=NAMES[n],
            zorder=3,
        )
        for row, value in enumerate(values):
            ax.annotate(
                f"{value:.3f}",
                (value, row + (n - 0.5) * 0.22),
                xytext=(7, 0),
                textcoords="offset points",
                va="center",
                fontsize=9,
                color=COLORS[n],
            )
    ax.set(
        yticks=y,
        yticklabels=[k for k, _ in keys],
        xlim=(0, 1.08),
        xticks=np.arange(0, 1.01, 0.2),
        xlabel="Reference agreement (higher is better)",
    )
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.18)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.04), ncol=2, frameon=False)
    fig.suptitle(
        "One annotated example: gains in identity and canals, lower pulp overlap",
        fontsize=13,
        y=0.99,
    )
    fig.text(
        0.02,
        0.015,
        "Same F002 scan · one Astra-medium attempt per condition · no output relabeling\nShape, identity and per-label overlap measure different things. These are not clinical validation scores.",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.075, 1, 0.95])
    fig.savefig(OUT / "metrics.png", dpi=170)
    plt.close(fig)


def contours(ax, image, gt, pred, extent):
    i0, i1, j0, j1 = extent
    ax.imshow(
        image.T,
        cmap="gray",
        vmin=-350,
        vmax=2200,
        origin="lower",
        extent=(i0 - 0.5, i1 - 0.5, j0 - 0.5, j1 - 0.5),
        interpolation="nearest",
    )
    xx, yy = np.arange(i0, i1), np.arange(j0, j1)
    for mask, color, style in [(gt, GT_COLOR, "solid"), (pred, PRED_COLOR, "dashed")]:
        if mask.any() and not mask.all():
            ax.contour(
                xx,
                yy,
                mask.T.astype(float),
                levels=[0.5],
                colors=[color],
                linewidths=1.15,
                linestyles=[style],
            )
    ax.set_xlim(i0 - 0.5, i1 - 0.5)
    ax.set_ylim(j1 - 0.5, j0 - 0.5)
    ax.tick_params(labelsize=8)


def overlays(ct, gt, predictions):
    # All slice/crop selections depend on GT anatomy, not relative performance.
    specs = [
        ("Pulp 111", [111], [11, 111], "max_area", 8),
        ("Main canal 3", [3], [3], "median", 13),
        ("Incisive canal 103", [103], [103], "max_area", 13),
        ("Restorations pooled", [8, 9, 10], [8, 9, 10], "median", 10),
    ]
    fig, axes = plt.subplots(len(specs), 2, figsize=(9.4, 13.5))
    receipt = []
    for row, (name, ids, context, rule, pad) in enumerate(specs):
        mask = np.isin(gt, ids)
        counts = mask.sum(axis=(0, 1))
        k = int(np.argmax(counts)) if rule == "max_area" else int(np.median(np.where(mask)[2]))
        roi = np.isin(gt[:, :, k], context)
        if not roi.any():
            roi = np.isin(gt, context).any(axis=2)
        coords = np.where(roi)
        i0, i1 = (
            max(0, int(coords[0].min()) - pad),
            min(ct.shape[0], int(coords[0].max()) + pad + 1),
        )
        j0, j1 = (
            max(0, int(coords[1].min()) - pad),
            min(ct.shape[1], int(coords[1].max()) + pad + 1),
        )
        sl = (slice(i0, i1), slice(j0, j1), k)
        for col, prediction in enumerate(predictions):
            ax = axes[row, col]
            contours(
                ax, ct[sl], np.isin(gt[sl], ids), np.isin(prediction[sl], ids), (i0, i1, j0, j1)
            )
            ax.set_title(f"{NAMES[col]} | {name}\nnative k = {k}", fontsize=10)
            ax.set_xlabel("native i", fontsize=8)
            ax.set_ylabel("native j", fontsize=8)
        receipt.append(
            {
                "structures": name,
                "labels": ids,
                "k": k,
                "selection": rule,
                "crop_ij": [i0, i1, j0, j1],
            }
        )
    legend = [
        Line2D([0], [0], color=GT_COLOR, lw=2, label="Original GT — solid"),
        Line2D([0], [0], color=PRED_COLOR, lw=2, ls="--", label="Prediction — dashed"),
    ]
    fig.legend(
        handles=legend, loc="upper center", bbox_to_anchor=(0.5, 0.964), ncol=2, frameon=False
    )
    fig.suptitle("Same native slices and crops in both conditions", fontsize=14, y=0.992)
    fig.text(
        0.03,
        0.01,
        "GT-based slice selection; illustrative sections do not replace 3D scores. No flips, registration or mask edits.\nNative i and j increase rightward/downward on these panels; semantic naming uses the declared dataset contract.",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.055, 1, 0.94])
    fig.savefig(OUT / "native-overlays.png", dpi=165)
    plt.close(fig)
    return receipt


def projections(ct, gt, predictions):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.5))
    image = ct.max(axis=1)
    for n, p in enumerate(predictions):
        gm = np.isin(gt, [3, 4]).any(axis=1)
        pm = np.isin(p, [3, 4]).any(axis=1)
        contours(axes[n], image, gm, pm, (0, ct.shape[0], 0, ct.shape[2]))
        axes[n].set_title(NAMES[n])
        axes[n].set_xlabel("native i")
        axes[n].set_ylabel("native k")
    handles = [
        Line2D([0], [0], color=GT_COLOR, lw=2, label="Original main-canal GT — solid"),
        Line2D([0], [0], color=PRED_COLOR, lw=2, ls="--", label="Predicted main canals — dashed"),
    ]
    fig.legend(
        handles=handles, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.06)
    )
    fig.suptitle("Main canals: whole-volume projection onto native i–k", fontsize=14)
    fig.text(
        0.03,
        0.015,
        "Native j is collapsed; this projection hides depth errors. Canal scores and surface distances use the full 3D masks.",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.22, 1, 0.95])
    fig.savefig(OUT / "canal-projections.png", dpi=180)
    plt.close(fig)


def method_diagram():
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    rows = [
        ["F002 CT + versioned contract", "F002 CT + contract + F008 CT/mask"],
        [
            "Inspect CT; choose tooth/root envelopes",
            "Affine + smooth registration; transfer labels",
        ],
        [
            "Threshold and morphology; agent-chosen paths",
            "Calibrate pulp; align jaws; adapt target masks",
        ],
        [
            "Refine boundaries; paint constrained canal tubes",
            "Correct transferred anatomy; refine canal paths",
        ],
        ["Save mask on the unchanged target grid", "Save mask on the unchanged target grid"],
    ]
    ys = [0.83, 0.65, 0.47, 0.29, 0.11]
    for col, x in enumerate([0.25, 0.75]):
        ax.text(
            x,
            0.965,
            NAMES[col],
            ha="center",
            va="center",
            fontsize=14,
            color=COLORS[col],
            weight="bold",
        )
        for row, y in enumerate(ys):
            box = FancyBboxPatch(
                (x - 0.22, y - 0.055),
                0.44,
                0.11,
                boxstyle="round,pad=0.008",
                facecolor="#F6F8FA",
                edgecolor=COLORS[col],
                linewidth=1.5,
            )
            ax.add_patch(box)
            text = rows[row][col]
            if "; " in text:
                text = text.replace("; ", "\n", 1)
            elif " + F008" in text:
                text = text.replace(" + F008", "\n+ F008")
            ax.text(x, y, text, ha="center", va="center", fontsize=10)
            if row < len(ys) - 1:
                ax.annotate(
                    "",
                    xy=(x, ys[row + 1] + 0.063),
                    xytext=(x, y - 0.063),
                    arrowprops={"arrowstyle": "->", "color": COLORS[col], "lw": 1.5},
                )
    fig.text(
        0.5,
        0.012,
        "Separate fresh attempts. Private GT is used by the evaluator after inference; no score feedback to solvers.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.025, 1, 1])
    fig.savefig(OUT / "method-flow.png", dpi=170)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    records, predictions, states, ct, gt = load_data()
    active = sorted({r["id"] for m in records for r in m["per_label"] if r["dice"] is not None})
    diagnostic = []
    for exp, m, p in zip(EXPS, records, predictions):
        rows = {r["id"]: r for r in m["per_label"]}
        diagnostic.append(
            {
                "experiment": exp,
                "original_macro_dice": m["macro_dice"],
                "active_labels": sum(r["dice"] is not None for r in rows.values()),
                "posthoc_common_label_macro_dice": float(
                    np.mean([rows[k]["dice"] or 0 for k in active])
                ),
                "common_label_set": active,
                "pulp_pooled": pooled(
                    gt, p, [q * 10 + i + 100 for q in range(1, 5) for i in range(1, 9)]
                ),
                "main_canals_pooled": pooled(gt, p, [3, 4]),
                "small_canals_pooled": pooled(gt, p, [103, 104, 105]),
            }
        )
    overview(records)
    slices = overlays(ct, gt, predictions)
    projections(ct, gt, predictions)
    method_diagram()
    summary = {
        "conditions": diagnostic,
        "slice_selection": slices,
        "attempts": [s["attempt_id"] for s in states],
        "all_outputs_preserved": True,
        "figure_sha256": {
            p.name: hashlib.file_digest(p.open("rb"), "sha256").hexdigest()
            for p in OUT.glob("*.png")
        },
    }
    (OUT / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(diagnostic, indent=2))


if __name__ == "__main__":
    main()
