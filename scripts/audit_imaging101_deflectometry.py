"""Audit deflectometry sources, fixed fringe fixtures and saved parameter scoring.

No optical forward model, optimizer, authoring module or installer is executed.
"""

from __future__ import annotations

import argparse
import builtins
import importlib.util
import json
import logging
import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, json_safe, selected, sha, stats
from scipy.io import loadmat

TASK = "differentiable_deflectometry"
COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.sources, args.output
    out.mkdir(parents=True, exist_ok=False)
    task = source / "tasks" / TASK
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    known = {r["path"]: r for r in tree["tree"]}
    sources = []
    for name in ["fetch-receipt.json", "shared-source-receipt.json"]:
        receipt = json.loads((source / name).read_text())
        assert receipt["revision"] == COMMIT
        for row in receipt["files"]:
            p = source / row["path"]
            assert sha(p) == row["sha256"] and p.stat().st_size == known[row["path"]]["size"]
            assert row["git_blob_sha1"] == known[row["path"]]["sha"]
            sources.append(row)
    assert len(sources) == 73
    assets = {}
    attempts = []
    for name in [
        "asset-fetch-receipt.json",
        "asset-alternate-receipt.json",
        "figure-fetch-receipt.json",
        "figure-alternate-receipt.json",
    ]:
        for row in json.loads((source / name).read_text()):
            attempts.append(row)
            if row["status"] == "verified":
                assert row["revision"] == REVISION
                p = source / row["path"]
                assert sha(p) == row["sha256"] and p.stat().st_size == row["size"]
                assets[row["path"]] = row
    listing = [
        row
        for name in ["hf-task-tree.json", "hf-task-tree-page2.json"]
        for row in json.loads((source / name).read_text())
    ]
    assert (
        json.loads((source / "hf-task-tree-page2-receipt.json").read_text())["link_header"] is None
    )
    assert not any(r["path"].endswith("/raw_data.npz") for r in listing)
    assert not (task / "data/raw_data.npz").exists()
    meta = json.loads((task / "data/meta_data.json").read_text())
    truth = arrays(task / "data/ground_truth.npz")
    params = json.loads((task / "evaluation/reference_outputs/optimized_params.json").read_text())
    saved_metrics = json.loads((task / "evaluation/reference_outputs/metrics.json").read_text())
    loss = np.load(task / "evaluation/reference_outputs/loss_history.npy", allow_pickle=False)
    keys = ["surface_0_roc_mm", "surface_1_roc_mm", "thickness_mm"]
    gt = np.array([float(truth[k][0]) for k in keys])
    rec = np.array([1 / params["surface_0_c"], 1 / params["surface_1_c"], params["surface_1_d"]])
    for key, actual, reference in zip(keys, rec, gt, strict=True):
        assert actual == saved_metrics[f"recovered_{key}"]
        assert np.isclose(
            abs(actual - reference) / abs(reference), saved_metrics[f"relative_error_{key}"]
        )
    assert loss.size == saved_metrics["n_iterations"] == 21
    assert float(loss[-1]) == saved_metrics["final_loss"]
    ns = {"np": np}
    selections = {
        "Fringe._solve": selected(task / "src/preprocessing.py", ["_solve"], ns, "Fringe")
    }
    fringe = arrays(task / "evaluation/fixtures/input_fringe_solve.npz")["imgs"]
    expected = arrays(task / "evaluation/fixtures/output_fringe_solve.npz")
    phase_errors = {}
    for i, name in enumerate(["x", "y"]):
        a, b, phase = ns["_solve"](fringe[4 * i : 4 * (i + 1)])
        error = float(np.abs(np.angle(np.exp(1j * (phase - expected[f"true_phase_{name}"])))).max())
        assert error < 1e-12 and np.allclose(a, expected["true_a"]) and np.allclose(b, 2500)
        phase_errors[name] = {
            "max_wrapped_phase_error_radians": error,
            "mean_level": float(a.mean()),
            "returned_b": float(b.mean()),
            "note": "b is squared modulation, not amplitude; these are synthetic 32x32 fixture pixels.",
        }
    selections["crop"] = selected(
        task / "src/preprocessing.py", ["crop_images", "get_crop_offset"], ns
    )
    crop_input = arrays(task / "evaluation/fixtures/input_crop_images.npz")
    crop_expected = arrays(task / "evaluation/fixtures/output_crop_images.npz")
    crop_name = next(k for k, v in crop_input.items() if v.ndim >= 2)
    cropped = ns["crop_images"](crop_input[crop_name], [768, 768])
    center = float(cropped.reshape((-1, 768, 768))[0, 384, 384])
    assert np.isclose(center, float(crop_expected["expected_center_value"]))
    del crop_input, cropped

    harness = source / "evaluation_harness"
    spec = importlib.util.spec_from_file_location(
        "deflectometry_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=ref)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("deflectometry-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer.py"] = selected(
        harness / "scorer.py", ["_compute_quality_metrics"], scorer_ns, "Scorer"
    )
    custom_ns = {"np": np, "Path": Path, "os": os, "json": json}
    selections["custom"] = selected(
        harness / "task_scoring_custom.py",
        ["_bases", "_find", "score_differentiable_deflectometry"],
        custom_ns,
    )
    custom = custom_ns["score_differentiable_deflectometry"](
        task, task / "evaluation/reference_outputs"
    )
    pose_control = out / "pose-control"
    pose_control.mkdir()
    wrong_pose = {**params, "origin": [1000, 1000, 1000], "theta_x": 90, "theta_y": 90}
    (pose_control / "optimized_params.json").write_text(json.dumps(wrong_pose) + "\n")
    ignored_pose = custom_ns["score_differentiable_deflectometry"](task, pose_control)
    assert ignored_pose == custom
    probes = {
        "three-parameter-output": rec,
        "three-parameter-oracle": gt,
        "first-radius-only": gt[:1],
    }
    generic = {}
    for name, value in probes.items():
        dest = out / "scoring" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", value)
        driver = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
            runner=SimpleNamespace(container=str(dest.parent)),
        )
        with np.errstate(invalid="ignore", divide="ignore"):
            generic[name] = scorer_ns["_compute_quality_metrics"](driver)
    assert (
        "error" in generic["three-parameter-output"]
        and "error" in generic["three-parameter-oracle"]
    )
    assert np.isinf(generic["first-radius-only"]["nrmse"])
    assert generic["first-radius-only"]["passed"] is None
    assert "ncc_boundary" not in saved_metrics and "nrmse_boundary" not in saved_metrics
    # Run only the source file-seeding methods; intercept all environment commands.
    stage_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("deflectometry-audit")}
    selections["runner"] = selected(
        harness / "runner.py", ["_get_visible_paths"], stage_ns, "BenchmarkRunner"
    )
    selections["local_runner"] = selected(
        harness / "local_runner.py", ["start"], stage_ns, "LocalRunner"
    )
    staging = {}
    for level in ["L1", "L2", "L3"]:
        dest = out / "staging" / level
        dest.mkdir(parents=True)
        commands = []
        stage_ns["tempfile"] = SimpleNamespace(
            mkdtemp=lambda directory=dest, **_: str(directory.resolve())
        )
        driver = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(mode="end_to_end", level=level)),
            task_dir=task.resolve(),
            exec=lambda cmd, log=commands: log.append(cmd),
        )
        visible = stage_ns["_get_visible_paths"](driver)
        stage_ns["start"](driver, visible)
        assert sha(dest / "data/ground_truth.npz") == sha(task / "data/ground_truth.npz")
        assert sha(dest / "data/lenses/ThorLabs/LE1234-A.txt") == sha(
            task / "data/lenses/ThorLabs/LE1234-A.txt"
        )
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "available_files_copied": sorted(
                str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()
            ),
            "truth_copied": True,
            "lens_prescription_copied": True,
            "raw_images_available": False,
            "commands_intercepted": commands,
        }
    calibration = loadmat(task / "data/calibration/cams.mat")
    report = {
        "schema": 1,
        "entry_id": "imaging101-differentiable-deflectometry",
        "date": "2026-09-29",
        "reviewer": "assistant",
        "source_commit": COMMIT,
        "asset_revision": REVISION,
        "script_sha256": sha(Path(__file__)),
        "helper_script_sha256": sha(
            Path(__file__).with_name("audit_imaging101_poisson_lowdose.py")
        ),
        "verified_sources": sources,
        "verified_assets": list(assets.values()),
        "asset_attempts": attempts,
        "hf_listing_count": len(listing),
        "hf_file_count": sum(r["type"] == "file" for r in listing),
        "metadata": meta,
        "calibration": {k: stats(v) for k, v in calibration.items() if not k.startswith("__")},
        "parameter_order": keys,
        "manufacturer_truth_mm": gt.tolist(),
        "saved_recovered_mm": rec.tolist(),
        "saved_metrics": saved_metrics,
        "loss": {
            "values": loss.tolist(),
            "definition": "Source optimizer records pre-update mean of squared masked residual components across the full grid; differs from valid-pixel mean displacement norm. No optimizer replay.",
        },
        "phase_fixture": phase_errors,
        "crop_fixture": {
            "source_shape": [2048, 2048],
            "crop_shape": [768, 768],
            "offset": ns["get_crop_offset"]([768, 768]).tolist(),
            "center_value": center,
        },
        "custom_scoring": custom,
        "custom_pose_control": {
            "output_pose": {k: wrong_pose[k] for k in ["origin", "theta_x", "theta_y"]},
            "score": ignored_pose,
            "scope": "Custom score ignores pose fields; no ray tracing or claim of optical equivalence.",
        },
        "generic_scoring": generic,
        "staging": staging,
        "source_function_selections": selections,
        "scope": {
            "model_runs": 0,
            "optical_ray_tracer_runs": 0,
            "optimizer_iterations": 0,
            "runtime_installs": 0,
            "native_raw_data_present": False,
            "fixtures": "Synthetic controls, not native camera samples.",
            "saved_displacement_error": "Retained metric only; raw screen-intersection maps absent, so not replayed.",
        },
    }
    (out / "audit.json").write_text(json.dumps(json_safe(report), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(out / "audit.json"),
                "sha256": sha(out / "audit.json"),
                "verified_assets": len(assets),
                "custom_score": custom,
                "generic_scoring": json_safe(generic),
            }
        )
    )


if __name__ == "__main__":
    main()
