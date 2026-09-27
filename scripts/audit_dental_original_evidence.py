"""Verify retained dental sources and saved evaluations; never execute a solver."""

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


def audit(root, out, trace, pulp):
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        if expected is not None:
            assert digest == expected, str(relative)
        pins[str(relative)] = digest
        return root / relative

    group = Path("groups/anatomy-audit")
    evidence = group / "findings/evidence"
    prior = read(pin(evidence / "dental-trace-root-causes.json"))
    for key in [
        "source_hashes",
        "supplemental_input_hashes",
        "generated_artifacts",
        "author_scripts",
    ]:
        for path, digest in prior[key].items():
            pin(path, digest)
    old = read(root / ".local/dental-trace-audit-20260921/analysis/audit.json")
    fresh = read(pin(trace / "audit.json"))
    assert fresh == old
    for path, digest in fresh["hashes"].items():
        pin(path, digest)
    gates = read(pin(pulp))
    assert gates == read(root / ".local/dental-trace-audit-20260921/analysis/f002-pulp-gates.json")
    assert gates["totals"] == prior["f002_pulp_gate_counts"]
    for path, digest in gates["hashes"].items():
        pin(path, digest)
    docs = read(pin(evidence / "dental-dataset-contract-audit.json"))
    for item in docs["sources"]:
        pin(item["file"], item["sha256"])

    source = Path(".local/dental-followups-20260921/source")
    extraction = read(pin(source / "extraction-receipt.json"))
    for item in extraction["files"]:
        pin(item["output"], item["sha256"])
    archive_labels = read(root / source / "dataset.json")["labels"]
    task = Path(".local/dental-ct-only-astra-medium/task")
    labels = read(pin(task / "environment/data/labels.json"))
    assert len(labels) == 78 and max(map(int, labels)) == 148
    assert labels == {str(ident): name for name, ident in archive_labels.items()}
    cases = []
    for case, exp in [
        ("F018", "dental-ct-only-astra-medium"),
        ("F002", "dental-f002-astra-medium"),
    ]:
        native = Path(".local") / exp / "task"
        ct = nib.load(pin(native / "environment/data/ct.nii.gz"))
        gt = nib.load(pin(native / "tests/reference.nii.gz"))
        archive_ct = nib.load(root / source / f"ToothFairy3F_{case[1:]}_0000.nii.gz")
        archive_gt = nib.load(root / source / f"ToothFairy3F_{case[1:]}.nii.gz")
        np.testing.assert_array_equal(ct.dataobj, archive_ct.dataobj)
        np.testing.assert_array_equal(gt.dataobj, archive_gt.dataobj)
        np.testing.assert_array_equal(ct.affine, gt.affine)
        if case == "F018":
            viewer = Path("runs/toothfairy3-partial-20260921/viewer-f018")
            for folder, suffix, image in [
                ("imagesTr", "_0000", ct),
                ("labelsTr", "", gt),
            ]:
                original = nib.load(pin(viewer / folder / f"ToothFairy3F_018{suffix}.nii.gz"))
                np.testing.assert_array_equal(image.affine, original.affine)
                np.testing.assert_array_equal(image.dataobj, original.dataobj)
            assert not np.array_equal(ct.affine, archive_ct.affine)
            assert nib.aff2axcodes(ct.affine) == ("L", "P", "I")
        else:
            np.testing.assert_array_equal(ct.affine, archive_ct.affine)
            assert nib.aff2axcodes(ct.affine) == ("L", "P", "S")
        np.testing.assert_allclose(nib.affines.voxel_sizes(ct.affine), [0.3] * 3, atol=1e-7)
        cases.append(
            {
                "case": case,
                "ct": str(native / "environment/data/ct.nii.gz"),
                "reference": str(native / "tests/reference.nii.gz"),
                "shape": list(ct.shape),
                "affine": ct.affine.tolist(),
                "archive_affine": archive_ct.affine.tolist(),
                "header_axis_codes": list(nib.aff2axcodes(ct.affine)),
                "header_is_not_physical_laterality_authority": True,
                "reference_foreground_classes": len(np.unique(np.asanyarray(gt.dataobj))) - 1,
                "source_arrays_exactly_equal": True,
            }
        )

    # The inspected frozen scorer defines a pure function and a guarded CLI.
    # Calling the function regrades saved outputs, without the logging CLI.
    scorer = pin(task / "tests/score.py")
    namespace = {"__name__": "dental_saved_output_replay"}
    exec(compile(scorer.read_text(), str(scorer), "exec"), namespace)
    replays, freezes, infrastructure = [], {}, []
    for exp in prior["experiment_ids"]:
        exp_dir = root / group / "experiments" / exp
        for path in (exp_dir / "freezes").glob("*.json"):
            freeze = read(pin(path))
            digest = hashlib.sha256(
                json.dumps(freeze["files"], sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            assert digest == freeze["task_digest"]
            for name, digest in freeze["files"].items():
                pin(Path(freeze["snapshot_path"]) / name, digest)
                pin(Path(freeze["source_path"]) / name, digest)
            freezes[freeze["task_digest"]] = len(freeze["files"])
        old_result = read(pin(evidence / (exp + ".json")))
        for path, digest in old_result["evidence"].items():
            pin(path, digest)
        for path in (exp_dir / "evaluations").glob("observation-*.json"):
            observation = read(pin(path))
            for item in observation["evidence"]:
                pin(item["path"], item["sha256"])
            trial = pin(observation["source_result"]).parent
            if observation["exception_type"] is not None:
                assert observation["attempt_id"] == "attempt-8ea2455a1f3a4a96"
                infrastructure.append(
                    {
                        "attempt": observation["attempt_id"],
                        "exception": observation["exception_type"],
                        "scope": "Retained authentication-only invocation; not model segmentation performance.",
                    }
                )
                continue
            score = read(pin(trial / "verifier/metrics.json"))
            answer = trial / "artifacts/app/answer/segmentation.nii.gz"
            if answer.exists():
                pin(answer)
            ref = root / ".local" / exp / "task/tests/reference.nii.gz"
            replay = namespace["score"](answer, ref, labels)
            assert score == replay, observation["attempt_id"]
            replays.append(
                {
                    "attempt": observation["attempt_id"],
                    "experiment": exp,
                    "agent": observation["agent"],
                    "effort": observation["reasoning_effort"],
                    "answer": str(answer.relative_to(root)),
                    "score": replay,
                    "seconds": observation["timing"]["agent"],
                }
            )
    assert len(replays) == 7 and len(infrastructure) == 1 and len(freezes) == 2
    for path, digest in pins.items():
        assert sha(root / path) == digest, path
    receipt = {
        "schema": 1,
        "entry": "tb3-dental-original",
        "reviewer": "assistant",
        "status": "source-audit-complete-story-pending",
        "source_pins": pins,
        "cases": cases,
        "task_digests": freezes,
        "replays": replays,
        "infrastructure_observations": infrastructure,
        "diagnostics": fresh["runs"],
        "pulp_gates": gates["totals"],
        "pulp_by_tooth": gates["per_tooth"],
        "original_evidence_unchanged": True,
        "new_model_runs": 0,
        "source_arrays_equal": True,
        "original_scores_exact_replay": True,
        "prior_trace_diagnostics_exact_reproduction": True,
        "terms": {
            "publisher": "CC BY-NC-SA 4.0",
            "archive": "CC-BY-SA 4.0",
            "treatment": "Preserve conflict; local research derivations retain publisher noncommercial/share-alike notice. No public redistribution is authorized.",
            "page": "https://ditto.ing.unimore.it/toothfairy3/",
            "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        },
        "limits": [
            "Two selected cases, three completed model attempts; no population or effort-effect claim.",
            "Clinical orientation and detailed annotation conventions remain unadjudicated.",
            "Fixed ID permutation is diagnostic, changes the active-class denominator, and never changes saved output geometry.",
            "Reference-selected views are reader diagnostics, not solver inputs or exhaustive clinical review.",
            "Custom active-class evaluator is not the official competition scoring contract.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "pins": len(pins),
                "saved_replays": len(replays),
                "infrastructure": len(infrastructure),
                "cases": cases,
                "digests": freezes,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--pulp", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output.resolve(), args.trace, args.pulp)
