"""Audit BCER source contracts and replay pure checks on nonclinical fixtures only."""

import argparse
import ast
import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import SimpleITK as sitk

COMMIT = "d10816712793a9e27f2e70640f9afc06f08a0c5c"
SAMPLE = Path("runs/task-brief-samples/bcer")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_functions(path, names, namespace):
    """Compile inspected function definitions, never the module's executable body."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    receipt = json.loads((args.sources / "receipt.json").read_text())
    assert receipt["commit"] == COMMIT
    tree = json.loads((args.sources / "tree.json").read_text())
    assert tree["sha"] == COMMIT and tree["truncated"] is False
    blobs = {v["path"]: v for v in tree["tree"] if v["type"] == "blob"}
    for item in receipt["files"]:
        path = args.sources / item["path"]
        raw = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert blob == item["sha"] == blobs[item["path"]]["sha"]
        assert len(raw) == blobs[item["path"]]["size"]
        item.update(local_path=str(path), sha256=sha(path), bytes=len(raw))
    contract = json.loads((args.sources / "configs/tasks_registry.json").read_text())["tasks"][
        "long_prostate_full"
    ]
    template = json.loads(
        (args.sources / "agent/plans/templates/prostate_full_pipeline.json").read_text()
    )
    sequences = []
    pins = {}
    point = None
    for name, original, prepared in [
        ("T2w", "10001_1000001_t2w.mha", "T2w.nii.gz"),
        ("ADC", "10001_1000001_adc.mha", "ADC.nii.gz"),
        ("DWI_highb", "10001_1000001_hbv.mha", "DWI_bhigh.nii.gz"),
    ]:
        src, dst = SAMPLE / original, SAMPLE / "prepared/10001" / prepared
        a, b = sitk.ReadImage(str(src)), sitk.ReadImage(str(dst))
        pins.update({str(p): sha(p) for p in (src, dst)})
        assert a.GetSize() == b.GetSize()
        assert np.array_equal(sitk.GetArrayFromImage(a), sitk.GetArrayFromImage(b))
        errors = {}
        for field in ["Spacing", "Origin", "Direction"]:
            av, bv = getattr(a, "Get" + field)(), getattr(b, "Get" + field)()
            np.testing.assert_allclose(av, bv, rtol=0, atol=1e-5)
            errors[field.lower()] = float(np.max(np.abs(np.array(av) - bv)))
        if point is None:
            point = a.TransformContinuousIndexToPhysicalPoint([319.5, 319.5, 10.0])
        ijk = a.TransformPhysicalPointToContinuousIndex(point)
        k = int(round(ijk[2]))
        arr = sitk.GetArrayFromImage(a)
        lo, hi = np.percentile(arr, [1, 99.5])
        sequences.append(
            {
                "name": name,
                "original": str(src),
                "prepared": str(dst),
                "size_xyz": list(a.GetSize()),
                "spacing_xyz_mm": list(a.GetSpacing()),
                "origin_lps_mm": list(a.GetOrigin()),
                "direction_lps": list(a.GetDirection()),
                "witness_ijk": list(ijk),
                "slice_k": k,
                "display_percentiles": [1, 99.5],
                "display_range": [float(lo), float(hi)],
                "display_scope": "whole native volume; sequence-specific arbitrary intensities",
                "mha_nifti_voxels_equal": True,
                "mha_nifti_geometry_max_errors": errors,
            }
        )
    original_manifest = SAMPLE / "cases_manifest.jsonl"
    pins[str(original_manifest)] = sha(original_manifest)
    original_row = json.loads(original_manifest.read_text())
    ns = {"Path": Path, "re": re}
    functions = {
        "scripts/manifest_builder.py": selected_functions(
            args.sources / "scripts/manifest_builder.py",
            [
                "_is_high_b_text",
                "_infer_prostate_modalities",
                "_normalize_domain_field",
                "_eval_modal_rule",
                "_task_supported",
            ],
            ns,
        )
    }
    canonical = ns["_infer_prostate_modalities"]([Path(v["prepared"]) for v in sequences])
    supported = ns["_task_supported"](domain="prostate", modalities=canonical, contract=contract)
    original_supported = ns["_task_supported"](
        domain="prostate", modalities=original_row["modalities"], contract=contract
    )
    assert supported is True and original_supported is False
    derived = {
        **original_row,
        "modalities": canonical,
        "supports_tasks": ["long_prostate_full"],
        "notes": "Author representative PI-CAI sample; exact selected modality rules replayed; not an official BCER split or pipeline run. Only this task was checked.",
    }
    (out / "derived-manifest.jsonl").write_text(json.dumps(derived) + "\n")
    evaluator = {"Path": Path, "csv": csv, "json": json}
    functions["benchmark/benchmark_runner.py"] = selected_functions(
        args.sources / "benchmark/benchmark_runner.py",
        [
            "_stage_sort_key",
            "_tool_success",
            "_latest_tool_data",
            "_coerce_path",
            "_resolve_tool_data_path",
            "_resolve_path_spec",
            "_check_required_artifact",
            "_nifti_nonempty",
            "_nifti_spacing_match",
            "_nifti_affine_match",
            "_csv_non_empty",
            "_json_field",
            "_evaluate_invariant",
            "_evaluate_success_rule",
            "_compute_tcr",
        ],
        evaluator,
    )
    examples = []
    for fixture in [
        "missing-files",
        "empty-files",
        "structural-pass",
        "shifted-origin",
        "report-stage-failed",
    ]:
        run = out / fixture
        run.mkdir()
        stages = {tool: [{"ok": True, "data": {}}] for tool in contract["required_stage_success"]}
        case_state = {"stage_outputs": {"1": stages}}
        for spec in contract["required_artifacts"]:
            ext = {"prostate_mask": ".nii.gz", "feature_table": ".csv"}.get(spec["id"], ".json")
            name = spec["id"] + ext
            stages[spec["tool"]][0]["data"][spec["data_key"]] = name
            if fixture != "missing-files":
                (run / name).touch()
        stages["segment_prostate"][0]["data"]["t2w_input_path"] = "synthetic-grid.nii.gz"
        if fixture not in {"missing-files", "empty-files"}:
            array = np.zeros((8, 8, 8), np.uint8)
            array[3, 3, 3] = 1
            grid = sitk.GetImageFromArray(array)
            sitk.WriteImage(grid, str(run / "synthetic-grid.nii.gz"))
            if fixture == "shifted-origin":
                grid.SetOrigin((1.0, 0.0, 0.0))
            sitk.WriteImage(grid, str(run / "prostate_mask.nii.gz"))
            (run / "lesion_candidates.json").write_text('{"num_candidates": 0, "candidates": []}')
            (run / "feature_table.csv").write_text("teaching_value\n1\n")
            (run / "report_json.json").write_text('{"note": "nonclinical teaching fixture"}')
        if fixture == "report-stage-failed":
            stages["generate_report"][0]["ok"] = False
        invariants = [
            evaluator["_evaluate_invariant"](spec=s, case_state=case_state, run_dir=run)
            for s in contract["invariants"]
        ]
        success, detail = evaluator["_evaluate_success_rule"](
            rule=contract["success_criteria"],
            case_state=case_state,
            run_dir=run,
            invariants_by_id={v["id"]: v["ok"] for v in invariants},
        )
        tcr = evaluator["_compute_tcr"](contract=contract, case_state=case_state, run_dir=run)
        examples.append(
            {
                "id": fixture,
                "base_success_rule": success,
                "tcr": tcr,
                "invariants_passed": sum(v["ok"] for v in invariants),
                "invariants": invariants,
            }
        )
        (run / "case_state.json").write_text(json.dumps(case_state, indent=2) + "\n")
        (run / "success-rule.json").write_text(json.dumps(detail, indent=2) + "\n")
    observed = [
        (v["base_success_rule"], v["tcr"]["completed"], v["invariants_passed"]) for v in examples
    ]
    assert observed == [(True, 6, 0), (True, 10, 0), (True, 10, 5), (True, 10, 4), (False, 9, 5)], (
        observed
    )
    audit = {
        "schema": 1,
        "entry_id": "bcer",
        "task": "long_prostate_full",
        "commit": COMMIT,
        "source_files": receipt["files"],
        "source_pins": pins,
        "selected_functions": functions,
        "case": "PI-CAI 10001_1000001",
        "sequences": sequences,
        "witness_lps_mm": list(point),
        "manifest": {
            "original": original_row,
            "original_task_supported": original_supported,
            "derived": derived,
            "derived_task_supported": supported,
            "original_bytes_preserved": True,
        },
        "contract": contract,
        "template": template,
        "validator_examples": examples,
        "scope": "Native representative inputs plus selected pure validator/manifest replay. Five author nonclinical 8-cube fixtures; no pipeline, model, registration, segmentation, lesion detection or report generation was executed. No clinical ground truth or measured model accuracy.",
        "observations": [
            "Pinned documentation describes SR as requiring TCR=1. The selected contract uses six tool_success rules; the runner computes success, TCR and invariants separately. Fixtures exercise that base rule, not the whole controller or fault harness.",
            "A tool_success rule accepts any ok=true record. Artifact paths come from the latest stage's last record. TCR counts six stage checks plus four path-existence checks; five invariants are separate.",
            "The template has eight nodes; DWI registration and feature extraction are optional there. The benchmark contract still requires feature extraction; template optionality is not a benchmark exemption.",
            "Candidates validity checks a nonnegative integer count and a list, not anatomy or count/list equality. CSV checks row count; report checks a truthy JSON value. NIfTI-read failure has a positive-file-size fallback in the nonempty test.",
            "The segmentation source has an explicitly degraded geometric fallback when the MONAI dependency check raises. Its ellipse uses array dimensions; no such fallback was executed here. Missing weights with an available stack raise separately.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(out),
                "verified_source_files": len(receipt["files"]),
                "validator_examples": observed,
                "modalities": canonical,
            }
        )
    )


if __name__ == "__main__":
    main()
