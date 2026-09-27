"""Read and replay saved CT-organ evidence into a fresh directory; never run inference."""

import argparse
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audit(root, out, slices):
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        digest = sha(root / path)
        if expected is not None:
            assert digest == expected, str(path)
        pins[str(path)] = digest
        return root / path

    group = Path("groups/anatomy-audit")
    old = read(pin(group / "findings/evidence/ct-organ-slice-construction-audit.json"))
    for row in old["files"] + old["analysis_sources"]:
        pin(row["path"], row["sha256"])
    previous = read(root / ".local/ct-organ-slice-audit/report/metrics.json")
    fresh = read(pin(slices / "metrics.json"))
    for key in ["conditions", "same_baseline_strata", "anchor_distance"]:
        assert fresh[key] == previous[key], key
    for path, digest in fresh["input_hashes"].items():
        pin(path, digest)
    task = Path(".local/ct-organ-segmentation-astra-xhigh/task")
    labels = read(pin(task / "tests/labels.json"))["labels"]
    source = Path("runs/br004-v1/source/s1233")
    manifest = read(
        pin(
            group
            / "experiments/ct-organ-segmentation-astra-xhigh/source/selected-source-manifest.json"
        )
    )
    for row in manifest["files"]:
        pin(source / row["path"], row["sha256"])
    ct = nib.load(pin(task / "environment/data/ct.nii.gz"))
    assert ct.shape == (265, 265, 401)
    assert nib.aff2axcodes(ct.affine) == ("R", "A", "S")
    np.testing.assert_array_equal(ct.dataobj, nib.load(root / source / "ct.nii.gz").dataobj)
    coverage = np.zeros(ct.shape, np.uint8)
    for item in labels:
        truth = nib.load(pin(task / "tests/reference" / item["file"]))
        original = nib.load(root / source / "segmentations" / (item["name"] + ".nii.gz"))
        np.testing.assert_array_equal(truth.dataobj, original.dataobj)
        np.testing.assert_array_equal(truth.affine, ct.affine)
        values = np.asarray(truth.dataobj)
        assert set(np.unique(values)) <= {0, 1}
        coverage += values.astype(np.uint8)
    assert int((coverage > 1).sum()) == 57
    tool_evidence = read(
        pin(group / "findings/evidence/ct-organ-segmentation-astra-medium-litemedsam.json")
    )
    for row in tool_evidence["files"]:
        pin(row["path"], row["sha256"])
    tool_work = Path(
        ".local/attempts/attempt-bc57d5f3973843bc/job/task__WhR5ASN/artifacts/app/work"
    )
    batches = [
        "large",
        "small",
        "adrenal",
        "gb",
        "liver_tip",
        "duo_gap",
        "duo_bridge",
        "adrenal_fix",
    ]
    jobs = [read(pin(tool_work / name / "provenance.json"))["jobs"] for name in batches]
    prompt_coverage = {}
    # Reconstruct the diagnostic in native coordinates, separately from the saved
    # image-coordinate implementation. Boxes cover sampled voxel centres, not edges.
    ii, jj = np.indices(ct.shape[:2])
    for ident in range(1, 11):
        boxes = np.zeros(ct.shape, bool)
        for batch in jobs:
            for k, rows in batch.items():
                for row in rows:
                    if row["id"] == ident:
                        x0, y0, x1, y1 = row["box"]
                        boxes[:, :, int(k)] |= (
                            (ii >= x0) & (ii < x1) & (264 - jj >= y0) & (264 - jj < y1)
                        )
        truth = (
            np.asarray(nib.load(root / task / "tests/reference" / f"{ident:02}.nii.gz").dataobj) > 0
        )
        fraction = float(np.count_nonzero(boxes & truth) / np.count_nonzero(truth))
        expected = tool_evidence["analysis"]["prompt_coverage_diagnostic"][str(ident)][
            "fraction_gt_within_agent_box_union"
        ]
        assert abs(fraction - expected) < 1e-12
        prompt_coverage[str(ident)] = fraction
    # This inspected evaluator has only imports, definitions and a guarded main.
    # Execute its functions without writing bytecode or invoking the logging main.
    score_path = pin(task / "tests/score.py")
    namespace = {"__name__": "ct_organ_saved_output_replay"}
    exec(compile(score_path.read_text(), str(score_path), "exec"), namespace)
    replays, freezes = [], {}
    for exp in sorted((root / group / "experiments").glob("ct-organ-segmentation-*")):
        for f in (exp / "freezes").glob("*.json"):
            freeze = read(pin(f.relative_to(root)))
            frozen = Path(freeze["snapshot_path"])
            for name, digest in freeze["files"].items():
                pin(frozen / name, digest)
            freezes[freeze["task_digest"]] = len(freeze["files"])
        for a in (exp / "attempts").glob("*.json"):
            attempt = read(pin(a.relative_to(root)))
            trials = list((root / ".local/attempts" / attempt["id"] / "job").glob("task__*"))
            assert len(trials) == 1, attempt["id"]
            trial = trials[0]
            score = read(pin((trial / "verifier/metrics.json").relative_to(root)))
            answer = trial / "artifacts/app/answer/masks"
            if answer.exists():
                for path in answer.glob("*.nii.gz"):
                    pin(path.relative_to(root))
            replay = namespace["score"](
                answer, root / task / "tests/reference", root / task / "tests/labels.json"
            )
            assert replay == score, attempt["id"]
            replays.append(
                {
                    "attempt": attempt["id"],
                    "experiment": exp.name,
                    "score": replay,
                    "answer": str(answer.relative_to(root)),
                    "metrics": str((trial / "verifier/metrics.json").relative_to(root)),
                }
            )
    for path, digest in pins.items():
        assert sha(root / path) == digest, path
    receipt = {
        "schema": 1,
        "entry": "tb3-ct-organ-segmentation",
        "status": "source-audit-complete-story-pending",
        "source_pins": pins,
        "task_digests": freezes,
        "replays": replays,
        "shape": list(ct.shape),
        "affine": ct.affine.tolist(),
        "spacing_mm": nib.affines.voxel_sizes(ct.affine).tolist(),
        "overlapping_reference_voxels": 57,
        "prompt_coverage_reproduced": prompt_coverage,
        "slice_analysis_reproduced": True,
        "comparison": "matched CT/taxonomy/reference/scorer; tool arm changes skill, instruction and runtime",
        "limits": [
            "one selected public case",
            "one attempt per condition",
            "training overlap unknown",
            "research reference, not independent clinical adjudication",
        ],
        "no_new_inference": True,
        "original_evidence_unchanged": True,
    }
    (out / "audit.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps({"pins": len(pins), "replays": len(replays), "digests": freezes, "overlap": 57})
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--slices", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output.resolve(), args.slices)
