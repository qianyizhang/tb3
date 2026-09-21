"""Render author-only fine-structure diagnostic evidence from retained arrays."""

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.lines import Line2D
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / ".local/dental-reference-ablation-20260921/fine-structure-diagnosis"
RUN = ROOT / ".local/dental-f002-reference-v2-astra-medium"
WORK = ROOT / ".local/attempts/attempt-36ee0d66d0a64d55/job/task__5aAvbpS/artifacts/app/work"
GT_COLOR, PRED_COLOR = "#00A77C", "#CC36CC"


def load(path):
    return np.asanyarray(nib.load(path).dataobj)


def binary_stats(g, p):
    ng, n, tp = int(g.sum()), int(p.sum()), int((g & p).sum())
    return {"gt": ng, "pred": n, "tp": tp, "dice": 2 * tp / (ng + n) if ng + n else None}


def verify_prior_clipping(gt):
    before = np.load(WORK / "teeth_pulp.npy")
    after = np.load(WORK / "teeth_pulp_final.npy")
    atlas = np.load(WORK / "atlas2.npy")
    prior = np.load(WORK / "tooth_priors.npy")
    rows = []
    for lab in [14, 44]:
        whole = (before == lab) | (before == lab + 100)
        coords = np.array(np.where(whole))
        lo = np.maximum(coords.min(1) - 7, 0)
        hi = np.minimum(coords.max(1) + 8, before.shape)
        sl = tuple(slice(start, end) for start, end in zip(lo, hi))
        ap = (atlas == lab) | (atlas == lab + 100)
        shift = np.array(ndi.center_of_mass(prior == lab)) - np.array(ndi.center_of_mass(ap))
        shift[2] = 0
        pulp_prior = ndi.shift((atlas[sl] == lab + 100).astype("uint8"), shift, order=0) > 0
        distance = ndi.distance_transform_edt(~pulp_prior)
        drop = (before[sl] == lab + 100) & (distance > 3.5)
        actual = (before[sl] == lab + 100) & (after[sl] != lab + 100)
        assert np.array_equal(drop, actual)
        rows.append(
            {
                "tooth": lab,
                "allowed_distance_mm": 1.05,
                "prior_xy_shift_voxels": shift.tolist(),
                "removed_pulp_voxels": int(drop.sum()),
                "removed_true_pulp_voxels": int((drop & (gt[sl] == lab + 100)).sum()),
                "saved_stage_difference_exactly_reproduced": True,
            }
        )
    (OUT / "prior-clipping.json").write_text(json.dumps(rows, indent=2) + "\n")
    return rows


def legend(fig, example=False):
    fig.legend(
        handles=[
            Line2D([0], [0], color=GT_COLOR, lw=2, label="Original GT — solid"),
            Line2D(
                [0],
                [0],
                color=PRED_COLOR,
                ls="--",
                lw=2,
                label="Prediction — dashed (target only)" if example else "Prediction — dashed",
            ),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.035),
        ncol=2,
        frameon=False,
    )


def section(ax, ct, gt, pred, lab, context_ids, axis, index=None):
    g = gt == lab
    if index is None:
        index = int(g.sum(axis=tuple(i for i in range(3) if i != axis)).argmax())
    context = np.isin(gt, context_ids)
    if pred is not None:
        context |= pred == lab
    pts = np.array(np.where(context))
    free = [q for q in range(3) if q != axis]
    lo = np.maximum(pts.min(1) - 7, 0)
    hi = np.minimum(pts.max(1) + 8, gt.shape)
    sl = [slice(int(a), int(b)) for a, b in zip(lo, hi)]
    sl[axis] = index
    view = ct[tuple(sl)].T
    gg = g[tuple(sl)].T
    extent = (lo[free[0]], hi[free[0]], hi[free[1]], lo[free[1]])
    ax.imshow(view, cmap="gray", vmin=-400, vmax=3220, extent=extent, interpolation="nearest")
    xx, yy = np.arange(lo[free[0]], hi[free[0]]) + 0.5, np.arange(lo[free[1]], hi[free[1]]) + 0.5
    if gg.any():
        ax.contour(xx, yy, gg, [0.5], colors=[GT_COLOR], linewidths=1.8)
    if pred is not None:
        pp = (pred == lab)[tuple(sl)].T
        if pp.any():
            ax.contour(xx, yy, pp, [0.5], colors=[PRED_COLOR], linestyles="--", linewidths=1.8)
    ax.set_xlabel(f"native {'ijk'[free[0]]}")
    ax.set_ylabel(f"native {'ijk'[free[1]]}")
    return {
        "label": lab,
        "axis": axis,
        "index": index,
        "crop_lo": lo.tolist(),
        "crop_hi": hi.tolist(),
        "choice": "maximum GT area on this native axis",
    }


def main():
    d = json.loads((OUT / "diagnostics.json").read_text())
    ct = load(RUN / "task/environment/data/ct.nii.gz")
    gt = load(RUN / "task/tests/reference.nii.gz").astype(np.uint8)
    ref = load(RUN / "task/environment/reference/ct.nii.gz")
    refgt = load(RUN / "task/environment/reference/segmentation.nii.gz").astype(np.uint8)
    final = load(WORK.parent / "answer/segmentation.nii.gz").astype(np.uint8)
    ids = [x for x in range(111, 149) if np.any(gt == x)]
    evidence = {"saturated_pulp": [], "stage_per_label": {}, "figures": {}, "slice_choices": []}
    evidence["prior_clipping"] = verify_prior_clipping(gt)
    for lab in [115, 116, 131]:
        g = gt == lab
        evidence["saturated_pulp"].append(
            {
                "label": lab,
                "gt_voxels": int(g.sum()),
                "raw_CT_above3000": int((ct[g] > 3000).sum()),
                "raw_CT_at_scan_max": int((ct[g] == ct.max()).sum()),
                "raw_CT_median": float(np.median(ct[g])),
                "example_raw_CT_median": float(np.median(ref[refgt == lab])),
                "example_raw_CT_max": float(ref[refgt == lab].max()),
            }
        )
    prev = None
    for name in ["atlas2.npy", "teeth_pulp.npy", "teeth_pulp_final.npy", "final.npy"]:
        a = np.load(WORK / name)
        rows = []
        for lab in ids:
            g, p = gt == lab, a == lab
            row = {"label": lab, **binary_stats(g, p)}
            if prev is not None:
                row.update(
                    added_tp=int((g & p & (prev != lab)).sum()),
                    removed_tp=int((g & ~p & (prev == lab)).sum()),
                )
            rows.append(row)
        evidence["stage_per_label"][name] = rows
        prev = a
    # Diagnostic exclusion reports both masks with the same IDs removed; no new score.
    selected = [x for x in range(111, 149) if x not in [116, 131]]
    evidence["pulp_pooled_excluding116_131_diagnostic"] = binary_stats(
        np.isin(gt, selected), np.isin(final, selected)
    )
    g105 = gt == 105
    cc, n = ndi.label(g105, np.ones((3, 3, 3)))
    evidence["gt105_components26"] = [
        {
            "voxels": int((cc == i).sum()),
            "centroid_native": list(map(float, ndi.center_of_mass(cc == i))),
        }
        for i in range(1, n + 1)
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.7))
    conditions = ["example_true_teeth_target22_ids", "target_true_teeth", "target_predicted_teeth"]
    values = [d["pulp"][x]["score"]["dice"] for x in conditions]
    axes[0].bar([0, 1, 2], values, color=["#377EB8", "#E69F00", "#D55E00"])
    axes[0].set(
        xticks=[0, 1, 2],
        xticklabels=["F008\ntrue teeth", "F002\ntrue teeth*", "F002\npredicted teeth"],
        ylim=(0, 0.9),
        ylabel="Pooled pulp Dice",
        title="Same fixed pulp rule fails to transfer",
    )
    for i, val in enumerate(values):
        axes[0].text(i, val + 0.025, f"{val:.3f}", ha="center")
    gate = d["pulp"]["target_predicted_teeth"]
    vals = [
        gate["gt_pulp_outside_tooth_mask"],
        gate["gt_pulp_in_mask_but_depth_rejected"],
        gate["gt_pulp_in_depth_but_intensity_rejected"],
        gate["score"]["tp"],
    ]
    axes[1].barh(
        range(4), np.array(vals) / 12242 * 100, color=["#999999", "#888888", "#D55E00", "#009E73"]
    )
    axes[1].set(
        yticks=range(4),
        yticklabels=["Outside tooth", "Too near surface", "Too bright", "Pass initial rule"],
        xlim=(0, 64),
        xlabel="% of F002 GT pulp voxels",
        title="Where the initial pulp rule loses GT",
    )
    axes[1].invert_yaxis()
    for i, v in enumerate(vals):
        axes[1].text(v / 12242 * 100 + 1, i, f"{v / 12242:.1%}", va="center")
    vals = [r["path_samples_inside_gt_fraction"] for r in d["canals"]]
    axes[2].bar(
        range(5),
        np.array(vals) * 100,
        color=["#377EB8", "#377EB8", "#009E73", "#D55E00", "#D55E00"],
    )
    axes[2].set(
        xticks=range(5),
        xticklabels=["Main L", "Main R", "Incisive L", "Incisive R", "Lingual"],
        ylim=(0, 103),
        ylabel="Path samples inside GT (%)",
        title="Canal center paths often miss GT",
    )
    axes[2].tick_params(axis="x", rotation=25)
    for i, val in enumerate(vals):
        axes[2].text(i, val * 100 + 3, f"{val:.0%}", ha="center")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0.14, 1, 1), w_pad=2)
    fig.text(
        0.02,
        0.045,
        "Author-only diagnostics; original scores unchanged. *True target teeth were unavailable to the solver.\nFixed rule: smoothed CT <1250 and tooth interior distance >2 voxels. F008 uses the same 22 tooth IDs as F002.",
        fontsize=10,
    )
    fig.savefig(OUT / "mechanisms.png", dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(10, 10.5))
    for row, lab in enumerate([116, 131]):
        c = section(axes[row, 0], ref, refgt, None, lab, [lab - 100, lab], 1)
        c["case"] = "F008"
        evidence["slice_choices"].append(c)
        axes[row, 0].set_title(f"F008: pulp {lab}, native j={c['index']}")
        c = section(axes[row, 1], ct, gt, final, lab, [lab - 100, lab], 1)
        c["case"] = "F002"
        evidence["slice_choices"].append(c)
        axes[row, 1].set_title(f"F002: pulp {lab}, native j={c['index']}")
    fig.suptitle(
        "The normal example does not show the target's bright pulp-labeled contents", fontsize=13
    )
    fig.tight_layout(rect=(0, 0.12, 1, 0.96))
    legend(fig, example=True)
    fig.text(
        0.03,
        0.012,
        "Same CT display window [-400, 3220]; maximum GT-area coronal slice per label and case.\nThese are source labels, not an adjudication of filling material or true pulp tissue. Missing contour means absent in this section.",
        fontsize=9,
    )
    fig.savefig(OUT / "pulp-label-contents.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.9))
    for ax, lab in zip(axes, [3, 103, 104]):
        c = section(ax, ct, gt, final, lab, [lab], 2)
        c["case"] = "F002"
        evidence["slice_choices"].append(c)
        ax.set_title(f"Canal {lab}: native k={c['index']}")
    fig.suptitle("Placement and width both matter on the original voxel grid", fontsize=13)
    fig.tight_layout(rect=(0, 0.16, 1, 0.95))
    legend(fig)
    fig.text(
        0.025,
        0.01,
        "Maximum GT-area axial slice for each canal; same CT display window [-400, 3220]. Missing prediction contour is section-specific.",
        fontsize=9,
    )
    fig.savefig(OUT / "canal-sections.png", dpi=160)
    plt.close(fig)
    for f in OUT.glob("*.png"):
        evidence["figures"][f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / "supplement.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(
        json.dumps(
            {
                "saturated_pulp": evidence["saturated_pulp"],
                "components105": evidence["gt105_components26"],
                "excluding_two_labels": evidence["pulp_pooled_excluding116_131_diagnostic"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
