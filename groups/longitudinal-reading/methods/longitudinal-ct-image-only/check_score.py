"""Synthetic controls verify separation of detection, geometry and association."""

import json
import tempfile
from pathlib import Path

import nibabel as nib
import numpy as np

from score import score


def save(root, b, f, groups, affine=None):
    root.mkdir(parents=True, exist_ok=True)
    affine = np.eye(4) if affine is None else affine
    for v, a in [("baseline", b), ("followup", f)]:
        nib.save(nib.Nifti1Image(a.astype(np.uint16), affine), root / f"{v}_instances.nii.gz")
    (root / "events.json").write_text(json.dumps(dict(schema_version=1, groups=groups)))
    (root / "report.md").write_text("Synthetic evaluator control.\n")


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        ref = root / "reference"
        out = root / "answer"
        b = np.zeros((40, 40, 16), np.uint16)
        f = b.copy()
        b[3:7, 3:7, 3:7] = 1
        b[10:14, 3:7, 3:7] = 2
        b[28:32, 28:32, 3:7] = 3
        f[3:14, 3:7, 3:7] = 4
        f[28:32, 28:32, 3:7] = 3
        groups = [
            dict(baseline_ids=[1, 2], followup_ids=[4], event="merging"),
            dict(baseline_ids=[3], followup_ids=[3], event="persistent"),
        ]
        save(ref, b, f, groups)
        save(out, b, f, groups)
        exact = score(out, ref)
        assert exact["valid"] and exact["segmentation_gt_macro_dice"] == 1
        assert (
            exact["detection_micro"]["f1"] == 1
            and exact["association"]["events_end_to_end"]["f1"] == 1
        )
        # Independent arbitrary IDs, including >9, must preserve all metrics.
        bp = np.zeros_like(b)
        fp = np.zeros_like(f)
        for old, new in [(1, 12), (2, 8), (3, 99)]:
            bp[b == old] = new
        for old, new in [(4, 77), (3, 42)]:
            fp[f == old] = new
        perm = [
            dict(baseline_ids=[12, 8], followup_ids=[77], event="merging"),
            dict(baseline_ids=[99], followup_ids=[42], event="persistent"),
        ]
        save(out, bp, fp, perm)
        s = score(out, ref)
        assert s["association"]["events_end_to_end"]["f1"] == 1
        # Correct masks and wrong associations: segmentation/detection remain perfect.
        wrong = [
            dict(baseline_ids=[1, 2], followup_ids=[3], event="merging"),
            dict(baseline_ids=[3], followup_ids=[4], event="persistent"),
        ]
        save(out, b, f, wrong)
        s = score(out, ref)
        assert s["segmentation_gt_macro_dice"] == 1 and s["detection_micro"]["f1"] == 1
        assert (
            s["association"]["links_end_to_end"]["f1"] == 0
            and s["association"]["events_end_to_end"]["f1"] == 0
        )
        # Correct localization, tiny masks: detected but poor delineation.
        tinyb = np.zeros_like(b)
        tinyf = np.zeros_like(f)
        tinyb[4, 4, 4] = 1
        tinyb[11, 4, 4] = 2
        tinyb[29, 29, 4] = 3
        tinyf[8, 4, 4] = 4
        tinyf[29, 29, 4] = 3
        save(out, tinyb, tinyf, groups)
        s = score(out, ref)
        assert s["detection_micro"]["f1"] == 1
        assert s["segmentation_gt_macro_dice"] < 0.05
        # Missing an instance damages end-to-end metrics, not conditional denominators.
        missing = b.copy()
        missing[missing == 2] = 0
        mg = [dict(baseline_ids=[1], followup_ids=[4], event="persistent"), groups[1]]
        save(out, missing, f, mg)
        s = score(out, ref)
        assert s["detection_micro"]["fn"] == 1 and s["association"]["links_end_to_end"]["fn"] == 1
        assert s["association"]["events_conditional_on_detection"]["eligible_gt_groups"] == 1
        # Extra unmatched lesions/edges must count as false positives.
        extra_b = b.copy()
        extra_f = f.copy()
        extra_b[18:20, 18:20, 10:12] = 9
        extra_f[18:20, 18:20, 10:12] = 10
        save(
            out,
            extra_b,
            extra_f,
            groups + [dict(baseline_ids=[9], followup_ids=[10], event="persistent")],
        )
        s = score(out, ref)
        assert s["detection_micro"]["fp"] == 2 and s["association"]["links_end_to_end"]["fp"] == 1
        # Empty outputs are valid contracts but zero scientific recall.
        save(out, np.zeros_like(b), np.zeros_like(f), [])
        s = score(out, ref)
        assert (
            s["valid"]
            and s["detection_micro"]["recall"] == 0
            and s["segmentation_gt_macro_dice"] == 0
        )
        # New/disappearing source classes are exercised independently of the selected CT.
        newb = np.zeros_like(b)
        newf = np.zeros_like(f)
        newb[3:7, 3:7, 3:7] = 15
        newf[28:32, 28:32, 3:7] = 27
        eg = [
            dict(baseline_ids=[15], followup_ids=[], event="disappearing"),
            dict(baseline_ids=[], followup_ids=[27], event="newly_appearing"),
        ]
        save(ref, newb, newf, eg)
        save(out, newb, newf, eg)
        s = score(out, ref)
        assert s["association"]["events_end_to_end"]["f1"] == 1
        # Invalid graph does not discard valid masks' independent measurements.
        save(out, newb, newf, eg + eg[:1])
        s = score(out, ref)
        assert not s["valid"] and s["segmentation_gt_macro_dice"] == 1
        # Wrong affine and missing files are contract failures, never silent resampling.
        bad = np.eye(4)
        bad[0, 3] = 8
        save(out, newb, newf, eg, bad)
        assert not score(out, ref)["valid"]
        (out / "baseline_instances.nii.gz").unlink()
        assert not score(out, ref)["valid"]
        print(
            json.dumps(
                dict(
                    passed=True,
                    controls=[
                        "exact",
                        "independent_ids",
                        "wrong_links",
                        "tiny_masks",
                        "missed_lesion",
                        "false_positive",
                        "empty_valid",
                        "new_and_disappearing",
                        "bad_graph",
                        "bad_geometry",
                        "missing_mask",
                    ],
                )
            )
        )


if __name__ == "__main__":
    main()
