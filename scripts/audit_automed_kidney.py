"""Inspect pinned AutoMedBench kidney contracts using nonclinical fixtures only."""

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import nibabel as nib
import numpy as np
import pandas as pd
import yaml

COMMIT = "5a9834ce0010c4e97b9eb22a4645321b9529902b"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select(path, names, namespace):
    """Extract inspected functions; never execute an upstream module body."""
    raw = path.read_text()
    nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    future = ast.parse("from __future__ import annotations").body
    exec(compile(ast.Module(body=future + nodes, type_ignores=[]), str(path), "exec"), namespace)
    return {
        n.name: {
            "sha256": hashlib.sha256(ast.get_source_segment(raw, n).encode()).hexdigest(),
            "lines": [n.lineno, n.end_lineno],
        }
        for n in nodes
    }


def literals(path, namespace):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                try:
                    namespace[target.id] = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    if target.id == "TIERS":
                        # This inspected dictionary refers only to two literal thresholds.
                        assert all(
                            isinstance(n, (ast.Dict, ast.Name, ast.Load, ast.Constant))
                            for n in ast.walk(node.value)
                        )
                        namespace[target.id] = eval(
                            compile(ast.Expression(node.value), str(path), "eval"), namespace
                        )


def save(path, array, affine):
    path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(nib.Nifti1Image(array.astype(np.uint8), affine), str(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    receipt = json.loads((args.sources / "receipt.json").read_text())
    tree = json.loads((args.sources / "tree.json").read_text())
    assert receipt["commit"] == tree["sha"] == COMMIT and not tree["truncated"]
    blobs = {r["path"]: r for r in tree["tree"] if r["type"] == "blob"}
    for row in receipt["files"]:
        path = args.sources / row["path"]
        raw = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert blob == row["sha"] == blobs[row["path"]]["sha"]
        assert len(raw) == row["bytes"] == blobs[row["path"]]["size"]
        assert sha(path) == row["sha256"]
    source = args.sources / "eval_seg"
    config = yaml.safe_load((source / "kidney-seg-task/config.yaml").read_text())
    models = yaml.safe_load((source / "kidney-seg-task/model_info.yaml").read_text())
    functions = {}
    prompt_ns = {
        "os": os,
        "yaml": yaml,
        "SCRIPT_DIR": str(source.resolve()),
        "PROJECT_DIR": str(args.sources.resolve()),
    }
    functions["eval_seg/task_loader.py"] = select(
        source / "task_loader.py",
        ["discover_tasks", "load_task_config", "load_skill", "load_requirements_path"],
        prompt_ns,
    )
    literals(source / "benchmark_runner.py", prompt_ns)
    # Exactly the selected binary Lite/Standard overrides used by the runner.
    prompt_files = {
        "_PREAMBLE": "common/preamble.md",
        "_ENV_LITE": "common/env_lite.md",
        "_ENV_STANDARD": "common/env_standard.md",
        "_S1_LITE": "s1_plan/lite.md",
        "_S1_STANDARD": "s1_plan/standard.md",
        "_S2_LITE": "s2_setup/lite.md",
        "_S2_STANDARD_PRO": "s2_setup/standard_pro.md",
        "_S3_ALL_LITE_STANDARD": "s3_validate/lite_standard.md",
        "_S4_LITE_STANDARD": "s4_inference/lite_standard.md",
        "_S5_ALL": "s5_submit/all.md",
        "_IMPORTANT_LITE": "common/important_lite.md",
        "_IMPORTANT_STANDARD": "common/important_standard.md",
    }
    for name, path in prompt_files.items():
        prompt_ns[name] = (source / "prompts" / path).read_text()
    functions["eval_seg/benchmark_runner.py"] = select(
        source / "benchmark_runner.py", ["build_tier_system_prompt"], prompt_ns
    )
    prompts = []
    for tier in ["lite", "standard"]:
        workspace = out / "prompt-fixtures" / tier
        workspace.mkdir(parents=True)
        value = prompt_ns["build_tier_system_prompt"](
            SimpleNamespace(name=tier),
            config,
            models[tier],
            "/data/public",
            str(workspace),
            task_id="kidney-seg-task",
        )
        path = workspace / "system-prompt.txt"
        path.write_text(value)
        has_s3 = "Skill — How to validate on one patient" in value
        assert has_s3
        prompts.append(
            {
                "tier": tier,
                "path": str(path),
                "sha256": sha(path),
                "includes_s3_example": has_s3,
                "requirements_copied": (workspace / "requirements.txt").exists(),
            }
        )
    assert [r["requirements_copied"] for r in prompts] == [True, False]
    scorer = {"np": np, "nib": nib, "os": os, "pd": pd}
    for filename, names in {
        "dice_scorer.py": ["dice_coefficient", "score_patient", "_find_mask", "score_all"],
        "format_checker.py": ["check_decision_csv", "check_mask_file", "check_submission"],
        "medal_tier.py": ["assign_tier"],
        "aggregate.py": [
            "compute_s4",
            "compute_s5",
            "compute_clinical_score",
            "compute_workflow_score",
            "compute_overall_score",
            "assign_rating",
            "is_resolved",
            "build_report",
        ],
    }.items():
        literals(source / filename, scorer)
        functions[f"eval_seg/{filename}"] = select(source / filename, names, scorer)
    quick = {"os": os}
    functions["runner_quick_submission_check"] = select(
        source / "benchmark_runner.py", ["check_submission"], quick
    )
    shape = (8, 8, 8)
    organ = np.zeros(shape, dtype=np.uint8)
    organ[2:4, 2:4, 2:4] = 1
    lesion = np.zeros(shape, dtype=np.uint8)
    lesion[2, 2, 2] = 1
    empty = np.zeros(shape, dtype=np.uint8)
    patients = ["fixture-positive", "fixture-negative"]
    public, reference = out / "public", out / "reference"
    for pid in patients:
        save(public / pid / "ct.nii.gz", empty, np.eye(4))
        save(reference / pid / "organ.nii.gz", organ, np.eye(4))
        save(
            reference / pid / "lesion.nii.gz",
            lesion if pid.endswith("positive") else empty,
            np.eye(4),
        )
    fixtures = []
    for name in [
        "exact-arrays",
        "missing-organ",
        "nonbinary-organ",
        "shifted-affine",
        "missing-patient",
        "empty-lesion",
    ]:
        workspace = out / name
        pred = workspace / "agents_outputs"
        for pid in patients:
            if name == "missing-patient" and pid.endswith("negative"):
                continue
            affine = np.eye(4)
            if name == "shifted-affine":
                affine[0, 3] = 100
            if name != "missing-organ":
                save(
                    pred / pid / "organ.nii.gz",
                    organ * (2 if name == "nonbinary-organ" else 1),
                    affine,
                )
            mask = lesion if pid.endswith("positive") and name != "empty-lesion" else empty
            save(pred / pid / "lesion.nii.gz", mask, affine)
        fmt = scorer["check_submission"](str(pred), patients, str(public), config)
        dice = scorer["score_all"](str(pred), str(reference), patients)
        tier = scorer["assign_tier"](dice["mean_lesion_dice"])
        report = scorer["build_report"](fmt, dice, tier, task_cfg=config)
        quick_result = quick["check_submission"](str(workspace), patients)
        fixtures.append(
            {
                "name": name,
                "quick_check": quick_result,
                "format": fmt,
                "dice": dice,
                "report_before_judge": report,
            }
        )
    indexed = {r["name"]: r for r in fixtures}
    assert indexed["exact-arrays"]["report_before_judge"]["aggregate"]["clinical_score"] == 1
    assert not indexed["missing-organ"]["quick_check"]["complete"]
    assert indexed["missing-organ"]["format"]["output_format_valid"]
    assert indexed["nonbinary-organ"]["format"]["output_format_valid"]
    assert not indexed["nonbinary-organ"]["format"]["per_patient"][patients[0]]["organ"]["valid"]
    assert indexed["shifted-affine"]["report_before_judge"]["aggregate"]["clinical_score"] == 1
    assert indexed["missing-patient"]["report_before_judge"]["aggregate"]["rating"] == "F"
    assert indexed["empty-lesion"]["report_before_judge"]["aggregate"]["clinical_score"] == 0.5
    data = {
        "schema": 1,
        "entry_id": "automedbench",
        "date": "2026-09-28",
        "reviewer": "assistant",
        "status": "source-audit-complete-native-input-unavailable",
        "scope": "Pinned binary kidney Lite/Standard contract. Source inspection and selected-function nonclinical fixtures only; no model, medical pipeline, controller, judge or security-harness execution.",
        "repository": receipt["repository"],
        "commit": COMMIT,
        "source_license_notice": (args.sources / "LICENSE").read_text(),
        "source_files": receipt["files"],
        "selected_functions": functions,
        "config": config,
        "model_assistance": models,
        "prompt_witnesses": prompts,
        "fixture_scope": "Two author 8x8x8 arrays. Empty artificial input, 8-voxel organ and 1-voxel positive lesion; not patient anatomy or medical performance.",
        "fixtures": fixtures,
        "source_pins": {str(Path(__file__).relative_to(Path.cwd())): sha(Path(__file__))},
        "observations": [
            "The source prompt requests two binary masks per patient plus optional decision CSV, with S1 plan, S2 setup, S3 one-patient validation, S4 batch inference and S5 submit_results.",
            "Both rendered Lite and Standard prompts include the S3 validation example. Lite also stages requirements and names a KiTS19 checkpoint; Standard asks for model comparisons. README S1-only wording for Standard differs from prompt assembly.",
            "The runner quick check requires both masks. The format check requires lesion masks but treats organ files as optional and does not propagate an invalid organ mask to its overall format flag.",
            "Mask format and Dice helpers compare array shapes/values, not physical affines. The 100-mm-shifted nonclinical fixture retains perfect array Dice; this is not geometric alignment evidence.",
            "Lesion Dice averages evaluated GT-positive cases; organ Dice averages available evaluated organs. The aggregate completeness gate uses non-null lesion results and zeroes Dice credit on missing patient output.",
            "S1-S3 remain None in deterministic reports until a judge supplies them. No judge scores were generated; these fixture reports are not full benchmark runs.",
            "The root preparation recipe selects the first 20 malignant KiTS19 metadata rows and merges labels 1 or 2 into organ, with label 2 for lesion. Its data/Kidney destination differs from the task loader config data/CruzAbdomen_Kidney. The older eval_seg staging script has another CruzBench path/layout. No staging script was executed.",
            "The retained Full-release archive and multi-organ CT belong to separate releases/tasks; neither proves this pinned kidney condition has its native input or staging layout.",
        ],
        "remaining": [
            "Obtain and hash a licensed native kidney CT/label pair, preferably KiTS19 case_00000; record representative-versus-exact-stage status.",
            "Audit geometry and source-label conversion, then author the task-specific story, integrate, export and perform visual review.",
            "Do not mark the explainer reviewed from this source audit or the synthetic fixtures alone.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(data, indent=2) + "\n")
    print(
        json.dumps(
            {
                "audit": str(out / "audit.json"),
                "source_files": len(receipt["files"]),
                "fixtures": len(fixtures),
                "prompts": len(prompts),
            }
        )
    )


if __name__ == "__main__":
    main()
