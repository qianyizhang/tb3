"""Post-trial scope audit prompted by the user's visible parent-gap review."""
import hashlib
import json
from pathlib import Path
import sys

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from build_viewer import connectivity

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / "runs/br033-airway-routing/benchmark"
OUT = B.parent / "viewer-review-20260916"


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    volumes = {}
    for case in ["A01", "A02", "A03"]:
        ni = nib.load(B / "input" / case / "proposed_mask.nii.gz")
        before = np.asarray(ni.dataobj) > 0
        after = np.asarray(nib.load(B / "terra-high" / case / "corrected_mask.nii.gz").dataobj) > 0
        req = json.loads((B / "input" / case / "request.json").read_text())
        anchors = np.array([req["start_ras_mm"], req["end_ras_mm"]])
        inv = np.linalg.inv(ni.affine)
        ijk = nib.affines.apply_affine(inv, anchors)
        row = {"case": case, "before": connectivity(before, ni.affine, anchors),
               "after": connectivity(after, ni.affine, anchors),
               "added": int((after & ~before).sum()), "removed": int((before & ~after).sum())}
        rows.append(row)
        volumes[case] = (before, after, ijk, nib.affines.voxel_sizes(ni.affine))
    assert rows[0]["added"] == 578 and rows[0]["after"]["anchors_connected"]
    assert not rows[0]["before"]["anchors_connected"]
    for r in rows[1:]:
        assert r["added"] == r["removed"] == 0
        assert r["after"]["anchors_connected"]
        assert not any(r["after"]["anchors_in_largest_component"])

    for name in ["image.nii.gz", "proposed_mask.nii.gz"]:
        a = nib.load(B / "input/A01" / name)
        c = nib.load(B / "input/A03" / name)
        assert np.array_equal(a.affine, c.affine)
        assert np.array_equal(np.asarray(a.dataobj), np.asarray(c.dataobj))
    provenance = json.loads((B.parent / "terra-viewer-provenance.json").read_text())
    for case, data in provenance.items():
        for filename, expected in data["unchanged_trial_files"].items():
            assert hashlib.sha256((B / "terra-high" / case / filename).read_bytes()).hexdigest() == expected

    frozen = json.loads((B.parent / "freeze.json").read_text())
    for task in frozen["tasks"]:
        root = ROOT / task["task_path"]
        actual = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
        assert actual == task["files"]
    audit = {"trigger": "User browser comments: A02 and A03 still show obvious disconnected airways",
             "finding": "Both control routes lie wholly inside detached fragments. The frozen endpoint-to-endpoint checks pass while parent connections remain unrepaired.",
             "cases": rows, "frozen_task_unchanged": True, "trial_outputs_unchanged": True,
             "A01_A03_identical_input_image_mask_and_affine": True,
             "interpretation": "Control-selection and presentation flaw. The original model follows the narrow task and retains its pass. These are not clinically intact-airway or true-absence controls.",
             "viewer_changes": ["Explicit parent-gap warnings for A02/A03", "Highlight actual A01 added voxels and new surface", "Input/output switches the 3D mesh", "Hide output route on original mesh", "Show anchor locations and connected-component audit"]}
    (ROOT / "docs/evidence/br033-scope-audit.json").write_text(json.dumps(audit, indent=2) + "\n")

    # A static projection provides a direct visual explanation without relying
    # on the blocked browser preview. It is drawn from unchanged mask arrays.
    fig, axes = plt.subplots(1, 4, figsize=(14, 6), facecolor="#0d151b")
    specs = [("A01", False, "A01 · input", "A and B are disconnected"),
             ("A01", True, "A01 · actual output", "578 added voxels bridge the requested route"),
             ("A02", True, "A02 · unchanged", "A and B share a detached fragment"),
             ("A03", True, "A03 · unchanged", "A and B share a detached fragment")]
    for ax, (case, use_after, title, caption) in zip(axes, specs):
        before, after, ijk, spacing = volumes[case]
        mask = after if use_after else before
        # A02's parent and fragment overlap along i; projection along k retains
        # the visible gap. These remain projections, not CT slices.
        axis = 2 if case == "A02" else 0
        dims = [k for k in range(3) if k != axis]
        canvas = np.zeros((mask.shape[dims[1]], mask.shape[dims[0]]), np.uint8)
        canvas[mask.any(axis=axis).T] = 1
        if use_after:
            canvas[(after & ~before).any(axis=axis).T] = 2
        ax.imshow(canvas, origin="lower", interpolation="nearest", aspect=spacing[dims[1]]/spacing[dims[0]],
                  cmap=ListedColormap(["#0d151b", "#7197a9", "#ff55ab"]), vmin=0, vmax=2)
        for point, label in zip(ijk, ["A", "B"]):
            ax.plot(point[dims[0]], point[dims[1]], "o", color="white", markersize=4)
            ax.annotate(label, (point[dims[0]], point[dims[1]]), xytext=(7, -2), textcoords="offset points", color="white", fontsize=11)
        ax.set_title(title, color="white", fontsize=13, pad=12)
        ax.set_xlabel(caption, color="#d9e2e9", fontsize=9, labelpad=12)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.suptitle("The actual repair is A01. A02 and A03 still have parent gaps.", color="white", fontsize=16, y=.99)
    fig.text(.5, .04, "Mask projections in native coordinates · blue: existing mask · magenta: added voxels · white: requested anchors", ha="center", color="#b9cbd8", fontsize=11)
    fig.tight_layout(rect=[0, .09, 1, .95])
    fig.savefig(OUT / "repair-and-unrepaired-controls.png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
