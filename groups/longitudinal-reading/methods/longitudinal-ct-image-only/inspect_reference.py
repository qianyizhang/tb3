"""Render private reference questions after the first saved attempt; no solver feedback."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-image-only-v1"


def main():
    task = BASE / "task"
    im = nib.load(task / "environment/data/baseline.nii.gz")
    ct = np.asarray(im.dataobj)
    m = np.asarray(nib.load(task / "tests/reference/baseline_instances.nii.gz").dataobj)
    colors = {1: "#45d5e8", 2: "#ffc85a", 4: "#ff8276"}
    fig, axs = plt.subplots(2, 3, figsize=(12, 8), layout="constrained")
    receipt = {"boundary_planes": [], "missed_focus_planes": []}
    for row, (a, c) in enumerate([(1, 2), (1, 4)]):
        contact = (m == a) & ndimage.binary_dilation(m == c)
        k = int(contact.sum(axis=(0, 1)).argmax())
        xy = np.argwhere(contact[:, :, k]).mean(axis=0)
        receipt["boundary_planes"].append(
            dict(labels=[a, c], contact_voxels=int(contact.sum()), k=k, center_ij=xy.tolist())
        )
        for col, ax in enumerate(axs[row]):
            z = k + col - 1
            ax.imshow(ct[:, :, z].T, cmap="gray", vmin=-160, vmax=240)
            for label, color in colors.items():
                if (m[:, :, z] == label).any():
                    ax.contour(
                        (m[:, :, z] == label).T, levels=[0.5], colors=[color], linewidths=1.2
                    )
            ax.set_xlim(xy[0] - 60, xy[0] + 60)
            ax.set_ylim(xy[1] + 60, xy[1] - 60)
            ax.set_title(f"GT {a}/{c} boundary · native k={z}")
            ax.set_xticks([])
            ax.set_yticks([])
    fig.suptitle(
        "Reference boundary review: baseline labels touch in voxelized masks\nGT 1 cyan; GT 2 amber; GT 4 coral. Solid contours. Native axial view; HU [−160, 240].\nVoxel connectivity alone does not establish radiologic confluence or a reference defect.",
        fontsize=12,
    )
    fig.savefig(BASE / "reference-boundaries-reproducible.png", dpi=150)
    plt.close(fig)
    state = json.loads((BASE / "astra-medium/operator-state.json").read_text())
    assert state["state"] == "terminal"
    fig, axs = plt.subplots(2, 3, figsize=(11, 7.5), layout="constrained")
    for row, v in enumerate(["baseline", "followup"]):
        im = nib.load(task / "environment/data" / (v + ".nii.gz"))
        ct = np.asarray(im.dataobj)
        gt = np.asarray(nib.load(task / "tests/reference" / (v + "_instances.nii.gz")).dataobj)
        pred = np.asarray(
            nib.load(
                Path(state["trial_path"]) / "artifacts/app/answer" / (v + "_instances.nii.gz")
            ).dataobj
        )
        k = int(np.count_nonzero(gt == 3, axis=(0, 1)).argmax())
        xy = np.argwhere(gt[:, :, k] == 3).mean(axis=0)
        half = 45 / float(im.header.get_zooms()[0])
        receipt["missed_focus_planes"].append(
            dict(
                visit=v,
                gt_id=3,
                k=k,
                center_ij=xy.tolist(),
                crop_width_mm=90,
                prediction_overlap_voxels=int(((gt == 3) & (pred > 0)).sum()),
            )
        )
        for col, ax in enumerate(axs[row]):
            ax.imshow(ct[:, :, k].T, cmap="gray", vmin=-160, vmax=240)
            if col == 1:
                ax.contour((gt[:, :, k] == 3).T, levels=[0.5], colors=["#45d5e8"], linewidths=1.5)
            if col == 2 and (pred[:, :, k] > 0).any():
                ax.contour((pred[:, :, k] > 0).T, levels=[0.5], colors=["#ffb34d"], linewidths=1.5)
            ax.set_xlim(xy[0] - half, xy[0] + half)
            ax.set_ylim(xy[1] + half, xy[1] - half)
            ax.set_title(
                f"{v} k={k} · "
                + ["CT only", "GT 3 · cyan contour", "Astra · no predicted mask here"][col],
                fontsize=10,
            )
            ax.set_xticks([])
            ax.set_yticks([])
    fig.suptitle(
        "A separate reference lesion is absent from Astra’s masks in both visits\nGT-selected axial planes and 90 mm crops; native i →, j ↓; HU [−160, 240].\nThe source calls this a lymph-node lesion. These views document disagreement, not clinical adjudication.",
        fontsize=11,
    )
    fig.savefig(BASE / "astra-missed-focus.png", dpi=150)
    plt.close(fig)
    (BASE / "reference-figure-provenance.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
