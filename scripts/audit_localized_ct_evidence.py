"""Read-only source/score audit for the retained localized CT candidate task."""

import argparse
import copy
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import nibabel as nib
import numpy as np

GROUP = Path("groups/longitudinal-reading")
DIGEST = "aeb14dde7d41ffd34bb4dfc83616ade0b1ba8350c9c25a5cbcca046be4671719"
ATTEMPTS = {
    "saved": "attempt-3756134eb4094e9f",
    "oracle": "attempt-090e3d257c014b70",
    "nop": "attempt-59de20ccdc3f453e",
}


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audit(root, output, work):
    if output.exists() or work.exists():
        raise FileExistsError("Audit and working destinations must be fresh")
    work.mkdir(parents=True)
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        value = sha(root / path)
        if expected:
            assert value == expected, path
        pins[str(path)] = value
        return value

    original = GROUP / "findings/evidence/longitudinal-ct-v2-and-localized.json"
    pin(original, "40fc5bb3f21a6aae5415d6b6b822b8f6ef088554639f3e33c4957bbfbbe71974")
    local = Path(".local/longitudinal-ct-image-only-v2/localized")
    retained = read(root / local / "analysis/evidence.json")
    for path, digest in retained["source_files"].items():
        pin(path, digest)
    for name in [
        "analysis/evidence.json",
        "preparation.json",
        "preflight.json",
        "astra-medium/audit.json",
        "image-identities.json",
    ]:
        pin(local / name)
    freeze_file = (
        GROUP
        / "experiments/longitudinal-ct-localized-astra-medium/freezes/freeze-62ecab0c85983e2c3fdd529a.json"
    )
    pin(freeze_file)
    freeze = read(root / freeze_file)
    assert freeze["task_digest"] == DIGEST
    task = root / freeze["snapshot_path"]
    for path, digest in freeze["files"].items():
        pin((task / path).relative_to(root), digest)
    previous_file = next(
        (root / GROUP / "experiments/longitudinal-ct-v2-astra-medium/freezes").glob("*.json")
    )
    pin(previous_file.relative_to(root))
    previous = read(previous_file)
    prior_task = root / previous["snapshot_path"]
    for path, digest in previous["files"].items():
        pin((prior_task / path).relative_to(root), digest)
    assert sha(task / "tests/base_score.py") == sha(prior_task / "tests/score.py")
    for path in ["environment/Dockerfile", "environment/docker-compose.yaml", "tests/Dockerfile"]:
        assert sha(task / path) == sha(prior_task / path)
    prior_evidence_path = Path(
        ".local/longitudinal-ct-image-only-v2/whole-volume/analysis/evidence.json"
    )
    pin(prior_evidence_path, read(root / local / "preparation.json")["source_evidence_sha256"])
    prior_evidence = read(root / prior_evidence_path)
    prior_job = next((root / ".local/attempts/attempt-4749bbfb347f4809/job").glob("task__*"))
    receipt = GROUP / "examples/longitudinal-ct-review-20260922.json"
    pin(receipt, "f98c77d343a1b2432c256e92a852a80be4b63af8227abed09c2ef80e1df94c82")
    for row in read(root / receipt)["files"]:
        if "0a09c8844b" in row["member"]:
            pin(Path(".local/longitudinal-ct-review/raw") / row["member"], row["sha256"])
    source_record = Path(".local/longitudinal-ct-review/source/record-v3.json")
    pin(source_record)
    results, jobs = {}, {}

    def replay(name, answer):
        dest = work / name
        run = subprocess.run(
            [
                sys.executable,
                str(task / "tests/score.py"),
                "--answer",
                str(answer),
                "--reference",
                str(task / "tests/reference"),
                "--output",
                str(dest),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        (work / (name + ".log")).write_text(run.stdout + run.stderr)
        return read(dest / "metrics.json")

    for name, attempt in ATTEMPTS.items():
        job = next((root / ".local/attempts" / attempt / "job").glob("task__*"))
        jobs[name] = job
        pin((job / "verifier/metrics.json").relative_to(root))
        answer = job / "artifacts/app/answer"
        for path in sorted(answer.glob("*")):
            if path.is_file():
                pin(path.relative_to(root))
        fresh = replay(name, answer)
        saved = read(job / "verifier/metrics.json")
        normalized = copy.deepcopy(fresh)
        if name == "nop":
            # The missing-file message embeds the execution-specific answer root.
            normalized["recognition"]["error"] = normalized["recognition"]["error"].replace(
                str(answer), "/app/answer"
            )
        assert normalized == saved, name
        results[name] = {
            "attempt": attempt,
            "exact_saved_replay": fresh == saved,
            "path_normalized_replay": normalized == saved,
            "metrics": saved,
            "fresh_metrics": fresh,
        }
    assert results["saved"]["metrics"] == retained["metrics"]
    job = jobs["saved"]
    judgments = read(job / "artifacts/app/answer/candidate_judgments.json")
    control_results = {}
    for name in [
        "rejected-with-oracle-masks",
        "tumor-with-empty-masks",
        "indeterminate-with-empty-masks",
        "duplicate-id",
        "blank-reason",
        "missing-judgments",
    ]:
        answer = work / (name + "-answer")
        shutil.copytree(
            task / "solution/reference"
            if name == "rejected-with-oracle-masks"
            else job / "artifacts/app/answer",
            answer,
        )
        rows = copy.deepcopy(judgments)
        if name == "tumor-with-empty-masks":
            for row in rows["candidates"]:
                row["judgment"] = "tumor"
        if name == "indeterminate-with-empty-masks":
            for row in rows["candidates"]:
                row["judgment"] = "indeterminate"
        if name == "duplicate-id":
            rows["candidates"][1]["candidate_id"] = "R01"
        if name == "blank-reason":
            rows["candidates"][0]["reason"] = " "
        (answer / "candidate_judgments.json").write_text(json.dumps(rows) + "\n")
        if name == "missing-judgments":
            (answer / "candidate_judgments.json").unlink()
        metrics = replay(name, answer)
        control_results[name] = {
            "metrics": metrics,
            "synthetic": True,
            "output": str(answer.relative_to(root)),
        }
    assert control_results["rejected-with-oracle-masks"]["metrics"]["valid"]
    assert control_results["rejected-with-oracle-masks"]["metrics"]["detection_micro"]["tp"] == 2
    assert (
        control_results["tumor-with-empty-masks"]["metrics"]["recognition"][
            "acceptance_sensitivity"
        ]
        == 1
    )
    assert control_results["indeterminate-with-empty-masks"]["metrics"]["valid"]
    for name in ["duplicate-id", "blank-reason", "missing-judgments"]:
        assert not control_results[name]["metrics"]["valid"]
    candidates = read(task / "tests/reference/candidate_map.json")
    geometry = []
    for candidate, target in candidates.items():
        visit = target["visit"]
        suffix = "BL" if visit == "baseline" else "FU"
        im = nib.load(task / f"environment/data/{visit}.nii.gz")
        data = np.asarray(im.dataobj)
        source = nib.load(
            root / f".local/longitudinal-ct-review/raw/inputsTr/0a09c8844b_{suffix}_img_00.nii.gz"
        )
        assert np.array_equal(im.affine, source.affine) and np.array_equal(
            data, np.asarray(source.dataobj)
        )
        cache = job / f"artifacts/app/work/{visit}.npy"
        pin(cache.relative_to(root))
        assert np.array_equal(data, np.load(cache, mmap_mode="r"))
        assert sha(task / f"environment/data/{visit}.nii.gz") == sha(
            prior_task / f"environment/data/{visit}.nii.gz"
        )
        ref = nib.load(task / f"tests/reference/{visit}_instances.nii.gz")
        g = np.asarray(ref.dataobj)
        old = np.asarray(nib.load(prior_task / f"tests/reference/{visit}_instances.nii.gz").dataobj)
        assert np.array_equal(g, np.where(old == 3, 3, 0))
        assert np.array_equal(im.affine, ref.affine)
        assert nib.aff2axcodes(im.affine) == ("L", "P", "S")
        xyz = np.argwhere(g == 3)
        center = xyz.mean(axis=0)
        selected = xyz[np.argmin(((xyz - center) ** 2).sum(axis=1))]
        assert selected.tolist() == target["native_ijk"]
        prior_prediction = nib.load(prior_job / f"artifacts/app/answer/{visit}_instances.nii.gz")
        pin((prior_job / f"artifacts/app/answer/{visit}_instances.nii.gz").relative_to(root))
        assert not np.any(np.asarray(prior_prediction.dataobj)[g == 3])
        answer = nib.load(job / f"artifacts/app/answer/{visit}_instances.nii.gz")
        assert answer.shape == im.shape and np.array_equal(answer.affine, im.affine)
        assert answer.get_data_dtype() == np.dtype("uint16") and not np.any(
            np.asarray(answer.dataobj)
        )
        for attr in ["qform", "sform"]:
            assert np.array_equal(getattr(answer, "get_" + attr)(), getattr(im, "get_" + attr)())
        spacing = list(map(float, im.header.get_zooms()))
        geometry.append(
            {
                "candidate": candidate,
                "visit": visit,
                "shape": list(im.shape),
                "spacing_mm": spacing,
                "affine_ras": im.affine.tolist(),
                "axes": list(nib.aff2axcodes(im.affine)),
                "native_ijk": selected.tolist(),
                "centroid_ijk": center.tolist(),
                "reference_voxels": len(xyz),
                "volume_ml": len(xyz) * float(np.prod(spacing)) / 1000,
                "reference_bbox_ijk_half_open": [
                    xyz.min(axis=0).tolist(),
                    (xyz.max(axis=0) + 1).tolist(),
                ],
                "source_input_and_cached_arrays_exact": True,
                "scoped_reference_exact": True,
                "previous_foreground_coverage": 0.0,
                "saved_output_empty_exact_grid": True,
            }
        )
    assert read(task / "tests/reference/events.json")["groups"] == [
        read(root / local / "preparation.json")["selected_reference_group"]
    ]
    for path in sorted((job / "artifacts/app/work").iterdir()):
        if path.suffix in [".jpg", ".py"]:
            pin(path.relative_to(root))
    source_rows = list(
        csv.DictReader((root / ".local/longitudinal-ct-review/raw/inputsTr/0a09c8844b.csv").open())
    )
    finding = {
        "schema": 1,
        "scope": "Read-only localized CT source audit and saved-score replay; synthetic verifier diagnostics are not medical/model trials.",
        "attempts": results,
        "source_pins": pins,
        "task_digest": DIGEST,
        "frozen_file_checks": len(freeze["files"]) + len(previous["files"]),
        "geometry": geometry,
        "source_csv_rows": source_rows,
        "candidate_selection": {
            "rule": "Source-positive reference voxel nearest voxel-index centroid; trigger <10% prior foreground coverage; prefer persistent group.",
            "selected": candidates,
            "prior_trigger": prior_evidence["localized_trigger"],
            "units": "native voxel indices, not physical Euclidean centroid distance",
        },
        "verifier_diagnostics": control_results,
        "verifier_limit": "Judgments and masks are validated separately: rejected judgments plus oracle masks still return valid and 2/2 detection. Tumor judgments with empty masks give 2/2 acceptance and 0/2 detection. Original saved answer is consistent (negative judgments, empty masks); original outcomes are unchanged.",
        "fitness": {
            "source": "https://fdat.uni-tuebingen.de/records/qe950-g4h94",
            "accessed": "2026-09-28",
            "annotation_context": "Release Annotation steps 1-3: CT assessment with clinical examination reports, axial manual segmentation, side-by-side cross-visit matching.",
            "solver_context": "Full native CT pair and two exact candidate centers; no clinical report, diagnosis, source identity, source masks or prior trace/results.",
            "adjudication": "Case-specific reports and independent clinical adjudication unavailable; source-positive disagreement does not prove malignancy is visually decidable from CT alone.",
        },
        "trace": {
            "job": str(job.relative_to(root)),
            "center_view_step": 14,
            "mpr_step": 11,
            "explicit_rejection_step": 16,
            "write_judgments_and_empty_masks_step": 17,
            "image_observation_blocks": 10,
            "limit": "Observable calls and saved images establish presentation and explicit judgment, not internal attention or clinical correctness.",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(finding, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "audit": str(output),
                "source_pins": len(pins),
                "frozen_checks": finding["frozen_file_checks"],
                "saved_replays": len(results),
                "controls": len(control_results),
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path)
    args = parser.parse_args()
    root = Path.cwd()
    audit(root, (root / args.output).resolve(), (root / args.work).resolve())


if __name__ == "__main__":
    main()
