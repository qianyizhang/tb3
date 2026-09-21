"""Measure F002 reference pulp lost at saved solver decision gates, read-only.

This is a reviewer diagnostic using GT. It never calls the historical scripts,
changes the submitted answer, or sends information to a solver.
"""

import argparse
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Choose a new output file")
    trial = next((args.repo / ".local/attempts/attempt-4338cd3dae024fc8/job").glob("task__*"))
    work = trial / "artifacts/app/work"
    files = [
        work / "ct.npy",
        work / "refined.npy",
        work / "pulp.py",
        args.repo / ".local/dental-f002-astra-medium/task/tests/reference.nii.gz",
        trial / "artifacts/app/answer/segmentation.nii.gz",
    ]
    hashes = {str(p): hashlib.file_digest(p.open("rb"), "sha256").hexdigest() for p in files}
    a, s = [np.load(p, mmap_mode="r") for p in files[:2]]
    g, pred = [np.asanyarray(nib.load(p).dataobj) for p in files[3:]]
    teeth = [q * 10 + i for q in range(1, 5) for i in range(1, 9)]
    swap = {k: k + (10 if k // 10 in (1, 3) else -10) for k in teeth}
    totals = {
        key: 0
        for key in [
            "gt_pulp",
            "inside_corresponding_tooth_envelope",
            "after_distance_gate",
            "after_intensity_gate",
            "after_slice_gate",
            "final_correct_overlap",
        ]
    }
    rows = []
    for gt_tooth in teeth:
        truth = g == gt_tooth + 100
        n = int(truth.sum())
        if not n:
            continue
        model_tooth = swap[gt_tooth]
        row = {
            "gt_tooth": gt_tooth,
            "model_tooth_after_side_pairing": model_tooth,
            "gt_pulp": n,
            "final_correct_overlap": int(np.count_nonzero(truth & (pred == model_tooth + 100))),
        }
        indices = np.where(s == model_tooth)
        for key in list(totals)[1:-1]:
            row[key] = 0
        if len(indices[0]):
            bb = tuple(
                slice(max(0, int(c.min()) - 3), min(s.shape[j], int(c.max()) + 4))
                for j, c in enumerate(indices)
            )
            envelope = s[bb] == model_tooth
            ref = truth[bb]
            smooth = ndi.gaussian_filter(a[bb], 0.55)
            distance = ndi.distance_transform_edt(envelope)
            row["inside_corresponding_tooth_envelope"] = int(np.count_nonzero(ref & envelope))
            candidate = distance > 1.6
            row["after_distance_gate"] = int(np.count_nonzero(ref & candidate))
            candidate &= smooth < 1180
            row["after_intensity_gate"] = int(np.count_nonzero(ref & candidate))
            zz = np.arange(bb[2].start, bb[2].stop)[None, None, :]
            candidate &= (zz < 66) if model_tooth < 30 else (zz > 127)
            row["after_slice_gate"] = int(np.count_nonzero(ref & candidate))
        for key in totals:
            totals[key] += row[key]
        rows.append(row)
    unchanged = all(
        hashlib.file_digest(Path(p).open("rb"), "sha256").hexdigest() == sha
        for p, sha in hashes.items()
    )
    assert unchanged
    result = {
        "diagnostic_only": True,
        "source_files_unchanged": unchanged,
        "totals": totals,
        "note": "Side-paired GT for diagnosis only. Final stage includes component/core rejection, closing and subsequent cleanup; not strictly monotonic.",
        "per_tooth": rows,
        "hashes": hashes,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(totals))


if __name__ == "__main__":
    main()
