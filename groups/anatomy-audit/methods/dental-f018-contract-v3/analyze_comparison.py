"""Author-only analysis of retained F018/v3 outputs; never modifies scored bytes."""

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / ".local/dental-f018-contract-v3-20260922/comparison"
EXPS = ["dental-f018-contract-v3-astra-medium", "dental-f018-reference-v3-astra-medium"]
NAMES = ["No example", "With F008"]
COLORS = ["#0072B2", "#D55E00"]
GT_COLOR, PRED_COLOR = "#00E0BA", "#FF6ADF"
AXIS_NAMES = ["i (increasing Right)", "j (increasing Posterior)", "k (increasing Inferior)"]


def read(path):
    return json.loads(path.read_text())


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def overlap(g, p):
    gc, pc, inter = int(g.sum()), int(p.sum()), int((g & p).sum())
    return dict(
        gt_voxels=gc,
        prediction_voxels=pc,
        intersection=inter,
        dice=2 * inter / (gc + pc) if gc + pc else None,
        precision=inter / pc if pc else None,
        recall=inter / gc if gc else None,
    )


def contour(ax, mask, coords, color, style="solid", width=1.2):
    if mask.any() and not mask.all():
        ax.contour(
            *coords, mask.T, levels=[0.5], colors=[color], linestyles=[style], linewidths=width
        )


def metrics_figure(records):
    keys = [
        ("All-label macro", lambda r: r["macro_dice"]),
        (
            "Whole-tooth shape",
            lambda r: r["whole_tooth_geometry_and_identity"][
                "geometry_mean_dice_with_unmatched_zero"
            ],
        ),
    ]
    keys += [
        (name, lambda r, k=key: r["groups"][k]["macro_dice"])
        for key, name in [
            ("tooth_tissue", "Tooth tissue"),
            ("pulp", "Pulp"),
            ("inferior_alveolar_canals", "Main canals"),
            ("small_canals", "Small canals"),
            ("jawbones", "Jaws"),
            ("sinuses", "Sinuses"),
            ("pharynx", "Pharynx"),
        ]
    ]
    fig, ax = plt.subplots(figsize=(10, 6))
    for index, record in enumerate(records):
        values = [fn(record) for _, fn in keys]
        y = np.arange(len(keys)) + (index - 0.5) * 0.3
        ax.barh(y, values, height=0.27, color=COLORS[index], label=NAMES[index])
        for pos, val in zip(y, values):
            ax.text(val + 0.012, pos, f"{val:.3f}", va="center", fontsize=9)
    ax.set(
        yticks=np.arange(len(keys)),
        yticklabels=[name for name, _ in keys],
        xlim=(0, 1.09),
        xlabel="Dice against unchanged original annotation",
    )
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=2, frameon=False)
    fig.suptitle("F018 / contract v3 — stronger tooth and pulp overlap; canals remain difficult")
    fig.text(
        0.02,
        0.018,
        "One fresh Astra-medium attempt per condition. Dataset tooth identity: 29/29 in both.\nRestoration labels absent in GT and both outputs; their convention is untested here.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.085, 1, 0.90))
    fig.savefig(OUT / "metrics.png", dpi=165)
    plt.close(fig)


def slice_figure(ct, gt, predictions, selected):
    fig, axes = plt.subplots(len(selected), 3, figsize=(13, 4 * len(selected)))
    selections = []
    for row, (label, reason) in enumerate(selected):
        # Same post-hoc GT-selected native coronal plane in all three columns.
        plane = int(np.argmax((gt == label).sum(axis=(0, 2))))
        masks = [a[:, plane, :] == label for a in [gt, *predictions]]
        union = np.logical_or.reduce(masks)
        if label > 110:
            union |= np.isin(gt[:, plane, :], [label - 100, label])
        points = np.argwhere(union)
        lo = np.maximum(points.min(0) - 9, 0)
        hi = np.minimum(points.max(0) + 10, [ct.shape[0], ct.shape[2]])
        crop = tuple(slice(int(a), int(b)) for a, b in zip(lo, hi))
        coords = [np.arange(lo[d], hi[d]) for d in range(2)]
        image = ct[:, plane, :][crop]
        selections.append(
            dict(
                label=label, reason=reason, axis=1, index=plane, crop_ik=[lo.tolist(), hi.tolist()]
            )
        )
        for col, ax in enumerate(axes[row]):
            ax.imshow(
                image.T,
                origin="lower",
                cmap="gray",
                vmin=-350,
                vmax=2200,
                extent=(lo[0] - 0.5, hi[0] - 0.5, lo[1] - 0.5, hi[1] - 0.5),
            )
            contour(ax, masks[0][crop], coords, GT_COLOR)
            if col:
                contour(ax, masks[col][crop], coords, PRED_COLOR, "dashed")
            ax.set_title(
                f"{'Original GT' if col == 0 else NAMES[col - 1]} | ID {label}, j={plane}",
                fontsize=10,
            )
            ax.set_xlabel(AXIS_NAMES[0])
            ax.set_ylabel(AXIS_NAMES[2])
            if col == 0:
                ax.text(0, 1.15, reason, transform=ax.transAxes, fontsize=10, fontweight="bold")
    fig.legend(
        handles=[
            Line2D([0], [0], color=GT_COLOR, label="GT: solid green"),
            Line2D([0], [0], color=PRED_COLOR, linestyle="--", label="Prediction: dashed magenta"),
        ],
        loc="lower center",
        ncol=2,
    )
    fig.suptitle("Actual F018 CT — identical native coronal slices in each comparison", fontsize=14)
    fig.text(
        0.01,
        0.038,
        "Post-hoc diagnostic slices: maximum GT class area in j. No flips, registration, or prediction editing.\n0.3 mm per voxel. View convention follows the task; clinical laterality is not independently adjudicated.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.078, 1, 0.95), h_pad=3)
    fig.savefig(OUT / "native-slices.png", dpi=170)
    plt.close(fig)
    return selections


def projection_figure(gt, predictions):
    # Binary silhouettes of the complete selected class, not CT slices or surfaces.
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for row, label in enumerate([4, 104]):
        masks = [x == label for x in [gt, *predictions]]
        points = np.argwhere(np.logical_or.reduce(masks))
        lo = np.maximum(points.min(0) - 5, 0)
        hi = np.minimum(points.max(0) + 6, gt.shape)
        crop = tuple(slice(a, b) for a, b in zip(lo, hi))
        for col, collapse in enumerate([2, 1, 0]):
            remaining = [d for d in range(3) if d != collapse]
            ax = axes[row, col]
            coords = [np.arange(lo[d], hi[d]) for d in remaining]
            for mask, color, style in zip(
                masks, ["#008970", *COLORS], ["solid", "dotted", "dashed"]
            ):
                contour(ax, mask[crop].any(axis=collapse), coords, color, style)
            ax.set_xlabel(AXIS_NAMES[remaining[0]])
            ax.set_ylabel(AXIS_NAMES[remaining[1]])
            ax.set_title(f"ID {label} | projection along {'ijk'[collapse]}")
            ax.set_aspect("equal")
            ax.grid(alpha=0.15)
    fig.legend(
        handles=[
            Line2D([0], [0], color=c, linestyle=s, label=n)
            for c, s, n in [
                ("#008970", "solid", "Original GT"),
                (COLORS[0], "dotted", NAMES[0]),
                (COLORS[1], "dashed", NAMES[1]),
            ]
        ],
        loc="lower center",
        ncol=3,
    )
    fig.suptitle("Canal extent and displacement — full-class native-coordinate silhouettes")
    fig.text(
        0.01,
        0.046,
        "Post-hoc selection: worst reference-run surface distance in each canal family (IDs 4 and 104).\nBinary projections can overlap at different depths; they are not voxel overlap or CT cross-sections. 0.3 mm / index.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 0.94))
    fig.savefig(OUT / "canal-projections.png", dpi=170)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records, reviews, states, predictions, files = [], [], [], [], []
    for exp in EXPS:
        base = ROOT / ".local" / exp
        state = read(base / "operator-state.json")
        assert read(base / "terminal-assessment.json")["state"] == "terminal_reviewed"
        assert state["state"] == "terminal"
        states.append(state)
        records.append(read(base / "replay/metrics.json"))
        reviews.append(read(base / "terminal-review.json"))
        path = Path(state["trial_path"]) / "artifacts/app/answer/segmentation.nii.gz"
        files.append(path)
        predictions.append(np.asarray(nib.load(path).dataobj).astype(np.uint8))
    frozen = ROOT / ".local/freezes" / states[0]["task_digest"] / "task"
    ctpath, gtpath = frozen / "environment/data/ct.nii.gz", frozen / "tests/reference.nii.gz"
    files += [ctpath, gtpath]
    ct = nib.load(ctpath).get_fdata(dtype=np.float32)
    gt = np.asarray(nib.load(gtpath).dataobj).astype(np.uint8)
    before_hashes = {str(p.relative_to(ROOT)): digest(p) for p in files}
    per_id = [{r["id"]: r for r in rec["per_label"]} for rec in records]
    pulp_ids = [label for label, r in per_id[0].items() if label > 110 and r["gt_voxels"]]
    gain_id = max(pulp_ids, key=lambda label: per_id[1][label]["dice"] - per_id[0][label]["dice"])
    worst_id = min(pulp_ids, key=lambda label: per_id[1][label]["dice"])
    details = []
    atlas_path = Path(states[1]["trial_path"]) / "artifacts/app/work/atlas.npy"
    atlas = np.load(atlas_path, mmap_mode="r")
    for label in [3, 4, 103, 104, 105, gain_id, worst_id]:
        g = gt == label
        rows = []
        for p in predictions:
            item = overlap(g, p == label)
            gc = np.argwhere(g).mean(0)
            pc = np.argwhere(p == label).mean(0)
            item.update(
                gt_centroid_ijk=gc.tolist(),
                prediction_centroid_ijk=pc.tolist(),
                centroid_displacement_mm=float(np.linalg.norm(pc - gc) * 0.3),
            )
            rows.append(item)
        prior_distances = cKDTree(np.argwhere(atlas == label)).query(np.argwhere(g))[0]
        details.append(
            dict(
                label=label,
                conditions=rows,
                transferred_prior=overlap(g, atlas == label),
                gt_fraction_within_6_voxels_of_prior=float((prior_distances <= 6).mean()),
            )
        )
    pooled = []
    for p in predictions:
        pooled.append(
            {
                name: overlap(np.isin(gt, labels), np.isin(p, labels))
                for name, labels in [
                    ("pulp", pulp_ids),
                    ("main_canals", [3, 4]),
                    ("small_canals", [103, 104, 105]),
                ]
            }
        )
    metrics_figure(records)
    selections = slice_figure(
        ct,
        gt,
        predictions,
        [
            (gain_id, "Largest pulp Dice gain"),
            (worst_id, "Worst remaining pulp Dice"),
            (104, "Incisive canal: zero final overlap"),
        ],
    )
    projection_figure(gt, predictions)
    result = dict(
        experiments=EXPS,
        attempts=[s["attempt_id"] for s in states],
        original_metrics=records,
        pooled=pooled,
        diagnostic_details=details,
        improved_pulp_labels=sum(per_id[1][i]["dice"] > per_id[0][i]["dice"] for i in pulp_ids),
        total_pulp_labels=len(pulp_ids),
        selection=selections,
        usage=[
            dict(
                agent_seconds=r["agent_seconds"],
                **r["token_usage"],
                uncached_input_tokens=r["token_usage"]["n_input_tokens"]
                - r["token_usage"]["n_cache_tokens"],
            )
            for r in reviews
        ],
        evidence_sha256=before_hashes,
        interpretation="Post-hoc diagnostics, unchanged original scores, one repeated development-case pair; no causal/population or clinical truth claim.",
    )
    assert before_hashes == {str(p.relative_to(ROOT)): digest(p) for p in files}
    (OUT / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: result[k]
                for k in [
                    "pooled",
                    "diagnostic_details",
                    "improved_pulp_labels",
                    "usage",
                    "selection",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
