"""Audit pinned Lite multi-organ sources with native metadata and nonclinical fixtures."""

import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
from types import SimpleNamespace

import nibabel as nib
import numpy as np
import pandas as pd
import yaml
from audit_automed_kidney import literals, select

REVISION = "8928073d5c3f3b842a4a4278d9b44f6e8ceaa9c5"
SAMPLE = Path("runs/task-brief-samples/automed")
ORGANS = ["kidney_left", "kidney_right", "liver", "spleen", "aorta"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data, affine):
    path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(nib.Nifti1Image(data, affine), path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    receipts = json.loads((args.sources / "fetch-receipt.json").read_text())
    for row in receipts:
        path = args.sources / row["path"]
        raw = path.read_bytes()
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        assert row["revision"] == REVISION and row["exit_code"] == 0
        assert row["revision_in_headers"] and row["blob_in_headers"]
        assert blob == row["git_blob"] and sha(path) == row["sha256"]
        assert len(raw) == row["bytes"]
        row["local_path"] = str(path)
    source = args.sources / "benchmarks/AutoMedBench-segmentation/eval_seg"
    config = yaml.safe_load((source / "tsg-multiorgan-seg-task/config.yaml").read_text())
    labels = config["tissue_labels"]
    assert len(labels) == 117 and set(labels) == set(range(1, 118))
    models = yaml.safe_load((source / "tsg-multiorgan-seg-task/model_info.yaml").read_text())
    functions = {}
    prompt_ns = {
        "os": os,
        "yaml": yaml,
        "SCRIPT_DIR": str(source.resolve()),
        "PROJECT_DIR": str(source.parent.resolve()),
    }
    functions["task_loader.py"] = select(
        source / "task_loader.py",
        ["discover_tasks", "load_task_config", "load_skill", "load_requirements_path"],
        prompt_ns,
    )
    literals(source / "benchmark_runner.py", prompt_ns)
    for name, filename in {
        "_PREAMBLE": "common/preamble.md",
        "_ENV_LITE": "common/env_lite.md",
        "_S2_LITE": "s2_setup/lite.md",
    }.items():
        prompt_ns[name] = (source / "prompts" / filename).read_text()
    functions["benchmark_runner.py"] = select(
        source / "benchmark_runner.py", ["build_tier_system_prompt"], prompt_ns
    )
    workspace = out / "prompt-fixture"
    workspace.mkdir()
    prompt = prompt_ns["build_tier_system_prompt"](
        SimpleNamespace(name="lite"),
        config,
        models["lite"],
        "/data/public",
        str(workspace),
        task_id=config["task_id"],
    )
    (workspace / "system-prompt.txt").write_text(prompt)
    assert "42=kidney_left" in prompt and "agents_outputs/<patient_id>/dseg.nii.gz" in prompt
    assert all(text in prompt for text in ["S1", "S2", "S3", "S4", "S5", "NEAREST-NEIGHBOUR"])

    namespaces = {}
    for filename, names in {
        "format_checker.py": [
            "_geometry_tolerances",
            "_geometry_error",
            "check_multiclass_mask_file",
            "check_submission",
        ],
        "dice_scorer.py": [
            "_geometry_tolerances",
            "_geometry_error",
            "_multiclass_value_error",
            "dice_coefficient",
            "_load_multiclass_map_with_geometry",
            "score_all_multiclass",
        ],
        "aggregate.py": [
            "compute_s4",
            "compute_s5",
            "compute_task_score_multiclass",
            "compute_workflow_score",
            "compute_overall_score",
            "assign_rating",
            "is_resolved",
            "_build_report_multiclass",
        ],
        "medal_tier.py": ["assign_tier"],
    }.items():
        ns = {
            "os": os,
            "np": np,
            "nib": nib,
            "pd": pd,
            "math": math,
            "ReferenceContractError": type("ReferenceContractError", (RuntimeError,), {}),
        }
        literals(source / filename, ns)
        functions[filename] = select(source / filename, names, ns)
        namespaces[filename] = ns
    fmt = namespaces["format_checker.py"]
    dice = namespaces["dice_scorer.py"]
    aggregate = namespaces["aggregate.py"]
    ids = ["toy_a", "toy_b"]
    affine = np.diag([1.5, 1.5, 1.5, 1.0])
    reference = np.zeros((8, 8, 8), dtype=np.uint8)
    reference[1:3, 1:3, 1:3] = 42
    reference[5:7, 5:7, 5:7] = 43
    public, gt = out / "fixtures/public", out / "fixtures/private/masks"
    for pid in ids:
        save(public / pid / "ct.nii.gz", np.zeros_like(reference), affine)
        for label in [42, 43]:
            save(
                gt / pid / f"{labels[label]}.nii.gz", (reference == label).astype(np.uint8), affine
            )
    examples = []
    for name in [
        "exact",
        "empty",
        "swapped",
        "shifted",
        "probability",
        "missing_one",
        "missing_all",
    ]:
        pred_dir = out / "fixtures" / name
        for i, pid in enumerate(ids):
            if name == "missing_all" or (name == "missing_one" and i == 1):
                continue
            values, geometry = reference.copy(), affine.copy()
            if name == "empty":
                values[:] = 0
            if name == "swapped":
                values = np.where(reference == 42, 43, np.where(reference == 43, 42, 0)).astype(
                    np.uint8
                )
            if name == "shifted":
                geometry[0, 3] = 100
            if name == "probability":
                values = reference.astype(np.float32)
                values[1, 1, 1] = 42.5
            save(pred_dir / pid / "dseg.nii.gz", values, geometry)
        checked = fmt["check_submission"](str(pred_dir), ids, str(public), config)
        scored = dice["score_all_multiclass"](
            str(pred_dir), str(gt), ids, labels, gt_layout="separated"
        )
        medal = namespaces["medal_tier.py"]["assign_tier"](scored["macro_mean_dice"])
        report = aggregate["_build_report_multiclass"](checked, scored, medal, None, config)
        examples.append({"id": name, "format": checked, "dice": scored, "report": report})
    expected = [1, 115 / 117, 115 / 117, 0, 0, 0.5, 0]
    assert [e["format"]["output_format_valid"] for e in examples] == [
        True,
        True,
        True,
        False,
        False,
        True,
        True,
    ]
    for e, score in zip(examples, expected, strict=True):
        assert abs(e["report"]["aggregate"]["task_score"] - score) < 0.000051
        assert all(e["report"]["step_scores"][k] is None for k in ["s1", "s2", "s3"])
    broken = affine.copy()
    broken[0, 3] = 1
    bad_ref = out / "fixtures/bad_reference"
    save(bad_ref / ids[0] / "kidney_left.nii.gz", (reference == 42).astype(np.uint8), affine)
    save(bad_ref / ids[0] / "kidney_right.nii.gz", (reference == 43).astype(np.uint8), broken)
    try:
        dice["score_all_multiclass"](
            str(out / "fixtures/exact"), str(bad_ref), [ids[0]], labels, gt_layout="separated"
        )
    except dice["ReferenceContractError"] as exc:
        reference_error = str(exc)
    else:
        raise AssertionError("Mismatched reference geometry must raise")

    metadata = []
    for name in ["automed-public-hashes", "automed-reference-hashes"]:
        metadata += json.loads(Path(f"runs/task-brief-samples/{name}.json").read_text())
    native = []
    for name in ["ct", *ORGANS]:
        path = SAMPLE / f"{name}.nii.gz"
        row = next(r for r in metadata if r["path"].endswith(f"/{name}.nii.gz"))
        assert row["lfs"]["oid"] == sha(path) and row["size"] == path.stat().st_size
        image = nib.load(path)
        assert image.shape == (333, 333, 336)
        assert fmt["_geometry_error"](image, nib.load(SAMPLE / "ct.nii.gz")) is None
        values = np.asarray(image.dataobj)
        record = {
            "name": name,
            "local_path": str(path),
            "source_path": row["path"],
            "sha256": sha(path),
            "bytes": path.stat().st_size,
            "shape": list(image.shape),
            "affine": image.affine.tolist(),
            "spacing_mm": [float(x) for x in image.header.get_zooms()],
            "axes": list(nib.aff2axcodes(image.affine)),
        }
        if name != "ct":
            assert set(np.unique(values)).issubset({0, 1})
            record["foreground_voxels"] = int(values.sum())
        native.append(record)
    model_receipt = json.loads((args.sources / "totalsegmentator-receipt.json").read_text())
    model_path = Path(model_receipt["local_path"])
    raw = model_path.read_bytes()
    assert (
        hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == model_receipt["git_blob"]
    )
    model_receipt["sha256"] = sha(model_path)
    map_node = next(
        n
        for n in ast.parse(raw).body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "class_map" for t in n.targets)
    )
    model_map = ast.literal_eval(map_node.value)["total"]
    remap = [
        {
            "name": name,
            "model_id": next(k for k, v in model_map.items() if v == name),
            "benchmark_id": next(k for k, v in labels.items() if v == name),
        }
        for name in ORGANS
    ]
    csv = pd.read_csv(SAMPLE / "ground_truth.csv")
    first = csv.iloc[0].to_dict()
    assert len(csv) == 40 and list(first.values()) == ["TSG_00000001", "s1366", 78]
    result = {
        "schema": 1,
        "entry_id": "automedbench-tsg",
        "revision": REVISION,
        "source_files": receipts,
        "model_map_source": model_receipt,
        "selected_functions": functions,
        "config": config,
        "remap": remap,
        "native_assets": native,
        "case_manifest": {
            "cases": len(csv),
            "example": first,
            "sha256": sha(SAMPLE / "ground_truth.csv"),
        },
        "prompt": {
            "path": str(workspace / "system-prompt.txt"),
            "sha256": sha(workspace / "system-prompt.txt"),
            "requirements_copied": (workspace / "requirements.txt").exists(),
            "tier": "lite",
        },
        "validator_examples": examples,
        "reference_geometry_error": reference_error,
        "scope": {
            "source_transport": "Public hf-mirror.com; response revision and Git blob ETags matched, not an authenticated primary-host download.",
            "scoring_conflict": "Config claims nonempty-reference classes only; pinned scorer loops all 117 classes, with empty/empty Dice 1.",
            "missing_outputs": "Scorer omits missing predictions from class averages; aggregate multiplies by completed-patient fraction.",
            "medal_limit": "Medal is assigned before completeness scaling and retained afterward; do not interpret grade as complete coverage.",
            "reference_coverage": "Five retained binary masks; release CSV reports 78 present classes of 117. No full-case score computed.",
            "model_map": "Pinned TotalSegmentator 2.4.0 total map illustrates one compatible version; release requirements permit later versions. Verify actual checkpoint labels.",
            "execution": "Selected inspected functions on two 8x8x8 synthetic grids only. No model, controller, judge, inference or isolation test.",
        },
    }
    (out / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(out),
                "source_files": len(receipts),
                "examples": len(examples),
                "task_scores": [e["report"]["aggregate"]["task_score"] for e in examples],
                "remap": remap,
            }
        )
    )


if __name__ == "__main__":
    main()
