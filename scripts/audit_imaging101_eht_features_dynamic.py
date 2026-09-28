"""Audit released dynamic crescent posteriors and their evaluation contract.

No upstream module initialization, training, inference, observation simulation,
installation or agent trial. Execute selected arithmetic on released arrays,
one fixed geometric fixture, and intercepted local staging only.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import hashlib
import importlib.util
import json
import logging
import os
import shutil
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, json_safe, selected, sha, stats

TASK = "eht_black_hole_feature_extraction_dynamic"
COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"
GT_KEYS = ["diameter_uas", "width_uas", "asymmetry", "position_angle_deg"]


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def maximum_error(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def verify(source):
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    known = {r["path"]: r for r in tree["tree"]}
    receipt = json.loads((source / "fetch-retry-receipt.json").read_text())
    assert receipt["source_commit"] == COMMIT and receipt["asset_revision"] == REVISION
    shared = json.loads((source / "shared-source-receipt.json").read_text())["files"]
    extra = json.loads((source / "extra-asset-receipt.json").read_text())
    manifest = {
        r["path"]: r for r in json.loads((source / "assets_manifest.json").read_text())["assets"]
    }
    sources, assets = [], []
    for row in receipt["files"] + shared + [extra]:
        path = source / row["path"]
        data = path.read_bytes()
        assert row["status"] == "verified" and sha(path) == row["sha256"]
        if row.get("kind", "source") == "source":
            assert len(data) == known[row["path"]]["size"]
            assert blob(data) == known[row["path"]]["sha"]
            sources.append(
                {
                    "path": row["path"],
                    "size": len(data),
                    "sha256": sha(path),
                    "git_blob_sha1": known[row["path"]]["sha"],
                    "status": "verified",
                    "url": f"https://raw.githubusercontent.com/AI4ImagingLab/imaging-101-release/{COMMIT}/{row['path']}",
                }
            )
        else:
            if row["kind"] == "asset":
                assert len(data) == manifest[row["path"]]["size"]
                assert sha(path) == manifest[row["path"]]["sha256"]
            assets.append(
                {
                    "path": row["path"],
                    "size": len(data),
                    "sha256": sha(path),
                    "revision": REVISION,
                    "status": "verified",
                    "url": f"https://hf.co/datasets/starpacker52/imaging-101/resolve/{REVISION}/{row['path']}",
                }
            )
    listing = json.loads((source / "hf-task-tree-receipt.json").read_text())
    assert sha(source / "hf-task-tree.json") == listing["sha256"]
    assert listing["status"] == "verified" and listing["link_header"] is None
    files = {
        r["path"]: r
        for r in json.loads((source / "hf-task-tree.json").read_text())
        if r["type"] == "file"
    }
    assert set(files) == {r["path"] for r in assets}
    for row in assets:
        item = files[row["path"]]
        assert row["size"] == item["size"]
        if "lfs" in item:
            assert row["sha256"] == item["lfs"]["oid"]
        else:
            assert blob((source / row["path"]).read_bytes()) == item["oid"]
    assert len(sources) == 74 and len(assets) == 9
    return sources, assets, listing


def closure_matrices(closure, baselines):
    phase = np.zeros((len(closure["cphase_data"]["cphase"]), baselines))
    amplitude = np.zeros((len(closure["logcamp_data"]["camp"]), baselines))
    for indices, signs in zip(closure["cphase_ind_list"], closure["cphase_sign_list"], strict=True):
        phase[np.arange(len(phase)), indices] += signs
    for indices, sign in zip(closure["camp_ind_list"], [1, 1, -1, -1], strict=True):
        amplitude[np.arange(len(amplitude)), indices] += sign
    return phase, amplitude


def weighted_quantile(values, weights, probabilities):
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order])
    return values[order[np.searchsorted(cumulative, probabilities, side="left")]]


def source_loss_control(path):
    """Execute only scalar arithmetic assignments, without constructing a solver."""
    cls = next(
        n
        for n in ast.parse(path.read_text()).body
        if isinstance(n, ast.ClassDef) and n.name == "AlphaDPISolver"
    )
    result = {}
    for name in ["reconstruct", "importance_resample"]:
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
        allowed = {"camp_weight", "cphase_weight", "scale_factor", "loss_data", "loss_orig"}
        nodes = sorted(
            [
                n
                for n in ast.walk(method)
                if isinstance(n, ast.Assign)
                and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id in allowed
            ],
            key=lambda n: n.lineno,
        )
        # AST inspection proves these assignments use only the supplied scalars
        # and len(); no torch operation, random draw or solver call can run.
        for node in nodes:
            assert all(
                isinstance(n.func, ast.Name) and n.func.id == "len"
                for n in ast.walk(node)
                if isinstance(n, ast.Call)
            )
        ns = {
            "camp_data": {"camp": list(range(70))},
            "cphase_data": {"cphase": list(range(56))},
            "loss_camp": 2.0,
            "loss_cphase": 1.0,
            "logprob": 0.25,
        }
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
        result[name] = {
            "source_lines": [n.lineno for n in nodes],
            "assignments": [ast.unparse(n) for n in nodes],
            "loss_data": ns["loss_data"],
            "loss_orig": ns["loss_orig"],
            "data_contribution": ns["loss_orig"] - ns["logprob"],
        }
    ratio = (
        result["reconstruct"]["data_contribution"]
        / result["importance_resample"]["data_contribution"]
    )
    assert np.isclose(ratio, 70)
    return {
        "fixed_inputs": {"mean_phase_loss": 1, "mean_logcamp_loss": 2, "logprob": 0.25},
        "replay": result,
        "data_contribution_ratio": ratio,
        "scope": "Pinned source weights a different likelihood in importance sampling than in training. Saved latent/log-density arrays and checkpoints are absent; no corrected weights or scores are inferred.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source, out = args.sources, args.output
    out.mkdir(parents=True, exist_ok=False)
    sources, assets, listing = verify(source)
    task = source / "tasks" / TASK
    raw = arrays(task / "data/raw_data.npz")
    truth = arrays(task / "data/ground_truth.npz")
    meta = json.loads((task / "data/meta_data.json").read_text())
    extra_meta = json.loads((task / "data/meta_data").read_text())
    ref_dir = task / "evaluation/reference_outputs"
    params, weights, images = [
        np.load(ref_dir / f"all_{name}.npy", allow_pickle=False)
        for name in ["params", "weights", "images"]
    ]
    assert params.shape == (10, 10000, 4) and weights.shape == (10, 10000)
    assert images.shape == truth["images"].shape == (10, 64, 64)
    assert len(raw) == 42 and "ground_truth_images" not in raw
    assert np.isfinite(params).all() and np.isfinite(weights).all()
    assert np.isfinite(images).all() and np.all(weights >= 0)
    assert np.allclose(weights.sum(axis=1), 1, atol=1e-6)
    selections = {}
    ns = {"np": np, "os": os, "json": json, "combinations": combinations, "GT_KEYS": GT_KEYS}
    selections["preprocessing"] = selected(
        task / "src/preprocessing.py",
        [
            "load_metadata",
            "load_raw_data",
            "load_frame_data",
            "_find_triangles",
            "_find_quadrangles",
            "extract_closure_indices",
            "estimate_flux",
        ],
        ns,
    )
    selections["metrics"] = selected(task / "src/visualization.py", ["compute_frame_metrics"], ns)
    selections["fixed_geometry"] = selected(
        task / "src/generate_data.py",
        [
            "generate_simple_crescent_image",
            "build_dft_matrix",
        ],
        ns,
    )
    selections["physical_units"] = selected(
        task / "src/solvers.py", ["extract_physical_params"], ns, "AlphaDPISolver"
    )
    assert all(
        np.array_equal(raw[k], v) for k, v in ns["load_raw_data"](str(task / "data")).items()
    )
    assert ns["load_metadata"](str(task / "data")) == meta
    fixture = arrays(task / "evaluation/fixtures/basic_pipeline.npz")
    fixture_replay = ns["generate_simple_crescent_image"](
        int(fixture["npix"]),
        *[
            float(fixture[k])
            for k in ["fov_uas", "diameter_uas", "width_uas", "asymmetry", "pa_deg"]
        ],
    )
    fixture_error = maximum_error(fixture_replay, fixture["crescent_image"])
    assert fixture_error < 1e-14
    driver = SimpleNamespace(
        fov_uas=120, r_range=[10, 40], width_range=[1, 40], geometric_model="simple_crescent"
    )
    endpoints = ns["extract_physical_params"](driver, np.array([[0, 0, 0, 0], [1, 1, 1, 1]], float))
    assert np.array_equal(endpoints, [[20, 1, 0, -181], [80, 40, 1, 181]])
    gt_values = np.column_stack([truth[k] for k in GT_KEYS])
    gt_rows = [{k: float(truth[k][i]) for k in GT_KEYS} for i in range(10)]
    assert extra_meta["ground_truth_per_frame"] == gt_rows
    assert "ground_truth_per_frame" not in meta
    metric = ns["compute_frame_metrics"](params, gt_rows, weights, GT_KEYS)
    quoted = json.loads((ref_dir / "metrics.json").read_text())
    replay = {
        "posterior_means": metric["means"].tolist(),
        "posterior_stds": metric["stds"].tolist(),
        "biases": metric["biases"].tolist(),
        "avg_abs_bias": np.abs(metric["biases"]).mean(axis=0).tolist(),
        "avg_std": metric["stds"].mean(axis=0).tolist(),
    }
    metric_errors = {k: maximum_error(v, quoted[k]) for k, v in replay.items()}
    # Retained computations used float32 reductions. Compare against two
    # representable steps at each original mean/std; bias inherits mean error.
    mean_tolerance = 2 * np.abs(np.spacing(np.asarray(quoted["posterior_means"], dtype=np.float32)))
    std_tolerance = 2 * np.abs(np.spacing(np.asarray(quoted["posterior_stds"], dtype=np.float32)))
    assert np.all(np.abs(metric["means"] - quoted["posterior_means"]) <= mean_tolerance)
    assert np.all(np.abs(metric["stds"] - quoted["posterior_stds"]) <= std_tolerance)
    assert np.all(np.abs(metric["biases"] - quoted["biases"]) <= mean_tolerance)
    assert np.all(
        np.abs(np.array(replay["avg_abs_bias"]) - quoted["avg_abs_bias"])
        <= mean_tolerance.max(axis=0)
    )
    assert np.all(
        np.abs(np.array(replay["avg_std"]) - quoted["avg_std"]) <= std_tolerance.max(axis=0)
    )
    normalized = weights.astype(float) / weights.astype(float).sum(axis=1)[:, None]
    ess = 1 / np.sum(normalized**2, axis=1)
    intervals = np.array(
        [
            [weighted_quantile(params[i, :, j], normalized[i], [0.16, 0.5, 0.84]) for j in range(4)]
            for i in range(10)
        ]
    )
    inside = (gt_values >= intervals[:, :, 0]) & (gt_values <= intervals[:, :, 2])
    circle = np.degrees(
        np.angle(np.sum(normalized * np.exp(1j * np.radians(params[:, :, 3])), axis=1))
    )
    controls = {}
    for name, values, ws in [
        ("saved", params, weights),
        ("unweighted_saved_samples", params, np.ones_like(weights)),
        ("oracle_collapsed_at_truth", gt_values[:, None, :], np.ones((10, 1))),
    ]:
        m = ns["compute_frame_metrics"](values, gt_rows, ws, GT_KEYS)
        controls[name] = {
            "means": m["means"].tolist(),
            "stds": m["stds"].tolist(),
            "avg_abs_bias": np.abs(m["biases"]).mean(axis=0).tolist(),
        }
    assert controls["oracle_collapsed_at_truth"]["avg_abs_bias"] == [0, 0, 0, 0]
    wrap_samples = np.array([[[44, 8, 0.5, -179], [44, 8, 0.5, 179]]], float)
    wrap_truth = [{"diameter_uas": 44, "width_uas": 8, "asymmetry": 0.5, "position_angle_deg": 180}]
    wrap = ns["compute_frame_metrics"](wrap_samples, wrap_truth, np.array([[0.5, 0.5]]), GT_KEYS)
    assert wrap["means"][0, 3] == 0 and wrap["biases"][0, 3] == -180
    wrap_control = {
        "fixed_angles_deg": [-179, 179],
        "equal_weights": [0.5, 0.5],
        "source_linear_mean_deg": float(wrap["means"][0, 3]),
        "source_linear_std_deg": float(wrap["stds"][0, 3]),
        "source_bias_against_180_deg": float(wrap["biases"][0, 3]),
        "circular_mean_deg": float(
            np.degrees(np.angle(np.mean(np.exp(1j * np.radians([-179, 179])))))
        ),
        "scope": "Fixed arithmetic counterexample only. Released samples span -139.03 to -45.15 degrees and do not cross this seam; this does not explain their observed bias.",
    }
    closure_rows = []
    formula_errors, dft_diagnostics = [], []
    for i in range(10):
        frame = ns["load_frame_data"](raw, i)
        assert np.array_equal(frame["station_ids"], list(combinations(range(8), 2)))
        closure = ns["extract_closure_indices"](frame)
        phase, amplitude = closure_matrices(closure, 28)
        assert phase.shape == (56, 28) and amplitude.shape == (70, 28)
        assert np.linalg.matrix_rank(phase) == 21 and np.linalg.matrix_rank(amplitude) == 19
        # Fixed, deterministic station gains test algebra on the SAME observations.
        gains = np.linspace(0.8, 1.2, 8) * np.exp(1j * np.linspace(-0.5, 0.7, 8))
        ids = frame["station_ids"]
        altered = dict(frame, vis=frame["vis"] * gains[ids[:, 0]] * np.conj(gains[ids[:, 1]]))
        gained = ns["extract_closure_indices"](altered)
        cp_difference = (
            closure["cphase_data"]["cphase"] - gained["cphase_data"]["cphase"] + 180
        ) % 360 - 180
        ca_difference = maximum_error(
            closure["logcamp_data"]["camp"], gained["logcamp_data"]["camp"]
        )
        assert np.max(np.abs(cp_difference)) < 1e-10 and ca_difference < 1e-12
        # Opposite quadrangle ratio adds the missing log-amplitude direction.
        lookup = {tuple(pair): k for k, pair in enumerate(ids)}
        alternate = np.zeros((70, 28))
        for row, (a, b, c, d) in enumerate(combinations(range(8), 4)):
            for pair, sign in [((a, b), 1), ((c, d), 1), ((a, d), -1), ((b, c), -1)]:
                alternate[row, lookup[pair]] += sign
        assert np.linalg.matrix_rank(np.vstack([amplitude, alternate])) == 20
        closure_rows.append(
            {
                "frame": i,
                "time_hr": float(raw["frame_times"][i]),
                "phase_count": 56,
                "phase_linear_rank": 21,
                "logcamp_count": 70,
                "logcamp_linear_rank": 19,
                "rank_with_second_quadrangle_ratio": 20,
                "phase_unwrapped_range_deg": [
                    float(closure["cphase_data"]["cphase"].min()),
                    float(closure["cphase_data"]["cphase"].max()),
                ],
                "station_gain_wrapped_phase_max_error_deg": float(np.max(np.abs(cp_difference))),
                "station_gain_logcamp_max_error": ca_difference,
                "median_visibility_amplitude_jy": ns["estimate_flux"](frame["vis"]),
                "minimum_visibility_snr": float(np.min(np.abs(frame["vis"]) / frame["vis_sigma"])),
            }
        )
        # Validate the already released reference against its declared fixed
        # formula. Do not call dataset generation or draw noise.
        formula = ns["generate_simple_crescent_image"](64, 120, *gt_values[i])
        formula_errors.append(maximum_error(formula, truth["images"][i]))
        operator = ns["build_dft_matrix"](
            frame["uv_coords"], 64, 1.875 * np.pi / (180 * 3600 * 1e6)
        )
        vis = np.einsum("ij,j->i", operator, truth["images"][i].ravel())
        physical_residual = frame["vis"] - 0.6 * vis
        unit_residual = frame["vis"] - vis
        dft_diagnostics.append(
            {
                "frame": i,
                "physical_flux_0_6_residual_rms_over_stored_sigma": float(
                    np.sqrt(np.mean(np.abs(physical_residual / frame["vis_sigma"]) ** 2))
                ),
                "unit_flux_residual_rms_over_stored_sigma": float(
                    np.sqrt(np.mean(np.abs(unit_residual / frame["vis_sigma"]) ** 2))
                ),
                "scope": "Fixed reference-array DFT, not NUFFT or reconstruction replay; residual norm is descriptive, not a calibrated chi-squared test.",
            }
        )
    assert max(formula_errors) < 1e-14
    harness = source / "evaluation_harness"
    spec = importlib.util.spec_from_file_location(
        "features_reference_scoring", harness / "reference_scoring.py"
    )
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=reference)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("eht-features-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer"] = selected(
        harness / "scorer.py",
        ["_compute_quality_metrics", "_compute_quality_metrics_generic"],
        scorer_ns,
        "Scorer",
    )
    generic = {}
    for name, value in {
        "saved_images": images,
        "saved_params": params,
        "saved_means": metric["means"],
        "oracle_images": truth["images"],
        "oracle_images_times_0_6": truth["images"] * 0.6,
        "oracle_asymmetry_vector": truth["asymmetry"],
        "oracle_angle_vector": truth["position_angle_deg"],
    }.items():
        dest = out / "scoring" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", value)
        driver = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
            runner=SimpleNamespace(container=str(dest.parent)),
        )
        generic[name] = scorer_ns["_compute_quality_metrics"](driver)
    assert generic["oracle_images"]["nrmse"] == 0 and generic["saved_images"]["passed"] is None
    assert "error" in generic["saved_params"] and "error" in generic["saved_means"]
    selected_vector, _ = reference.load_reference_array(task, target_shape=(10,))
    assert np.array_equal(selected_vector, truth["asymmetry"])
    driver = SimpleNamespace(
        config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
        runner=SimpleNamespace(container=None),
    )
    fallback = scorer_ns["_compute_quality_metrics_generic"](driver)
    assert fallback == {"error": "ground_truth.npy not found in task directory"}
    recipe_ns = {"np": np, "Path": Path, "TASK_CONFIG": {TASK: {"extra": {"pa_index": 3}}}}
    selections["native_recipe"] = selected(
        harness / "task_scoring.py",
        ["_recon_bases", "_find_recon", "_recipe_eht_feature"],
        recipe_ns,
    )
    historical_recipe = recipe_ns["_recipe_eht_feature"](task.resolve(), ref_dir.resolve(), None)
    assert np.isclose(
        historical_recipe["position_angle_mae_deg"], replay["avg_abs_bias"][3], atol=1e-5
    )
    # Preserve all source staging behavior, but intercept every installer command.
    stage_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("eht-features-audit")}
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
        for name in ["ground_truth.npz", "raw_data.npz", "meta_data.json", "meta_data"]:
            assert sha(dest / "data" / name) == sha(task / "data" / name)
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "commands_intercepted": commands,
            "ground_truth_npz_copied": True,
            "answer_bearing_metadata_copied": True,
            "copied_files": sorted(
                str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()
            ),
        }
    syntax = {}
    for p in sorted(task.rglob("*.py")):
        ast.parse(p.read_text())
        syntax[str(p.relative_to(task))] = "parses"
    notebook = json.loads(next((task / "notebooks").glob("*.ipynb")).read_text())
    notebook_text = "\n".join(
        "".join(o.get("text", [])) for c in notebook["cells"] for o in c.get("outputs", [])
    )
    (out / "retained-notebook-output.txt").write_text(notebook_text)
    record = {
        "task": TASK,
        "source_commit": COMMIT,
        "asset_revision": REVISION,
        "script_sha256": sha(Path(__file__)),
        "helper_script_sha256": sha(
            Path(__file__).with_name("audit_imaging101_poisson_lowdose.py")
        ),
        "verified_sources": sources,
        "verified_assets": assets,
        "asset_listing": listing,
        "metadata": meta,
        "extra_metadata_keys": sorted(set(extra_meta) - set(meta)),
        "extra_metadata_truth_matches": True,
        "selected_functions": selections,
        "source_syntax": syntax,
        "raw_array_schema": {
            k: {
                "shape": list(v.shape),
                "dtype": str(v.dtype),
                "nonfinite": int((~np.isfinite(v)).sum()),
            }
            for k, v in raw.items()
        },
        "truth_array_stats": {k: stats(v) for k, v in truth.items()},
        "retained_arrays": {
            "params": stats(params),
            "weights": stats(weights),
            "images": stats(images),
        },
        "fixture": {
            "path": "evaluation/fixtures/basic_pipeline.npz",
            "max_error": fixture_error,
            "scope": "One fixed32x32 crescent formula only; no closure, flow, training, importance or calibration fixture.",
        },
        "physical_parameter_endpoints": endpoints.tolist(),
        "fixed_reference_formula_max_error": max(formula_errors),
        "stored_image_flux": images.sum(axis=(1, 2)).tolist(),
        "stored_truth_flux": truth["images"].sum(axis=(1, 2)).tolist(),
        "native_metrics": replay,
        "native_metrics_original_max_errors": metric_errors,
        "native_metrics_tolerance": "Two float32 representable steps at each original mean/std; bias inherits mean tolerance and aggregate uses per-column maximum. Original report remains unchanged.",
        "effective_sample_sizes": ess.tolist(),
        "maximum_normalized_weight": normalized.max(axis=1).tolist(),
        "central_68_percent_intervals": intervals.tolist(),
        "interval_convention": "Weighted empirical inverse CDF at0.16,0.50,0.84; no KDE. Equal-tail, not highest-density intervals; supplemental finite-sample diagnostics only.",
        "truth_inside_intervals_per_parameter": inside.sum(axis=0).tolist(),
        "interval_denom": 10,
        "interval_scope": "Ten dependent snapshots of one synthetic sequence do not establish uncertainty calibration or population coverage.",
        "circular_angle_means_deg": circle.tolist(),
        "angle_wrap_control": wrap_control,
        "linear_summary_controls": controls,
        "closure_diagnostics": closure_rows,
        "fixed_reference_dft_diagnostics": dft_diagnostics,
        "source_likelihood_scaling_control": source_loss_control(task / "src/solvers.py"),
        "generic_dispatch": generic,
        "generic_vector_reference_key": "asymmetry",
        "no_filesystem_fallback": fallback,
        "historical_parameter_recipe": historical_recipe,
        "staging": staging,
        "notebook_output_sha256": sha(out / "retained-notebook-output.txt"),
        "scope": "Saved-array/source audit, fixed geometry/closure/scoring arithmetic and intercepted staging. No Torch/NUFFT runtime, model launch, training, random sampling, observation simulation or new scientific inference.",
    }
    (out / "audit.json").write_text(json.dumps(json_safe(record), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "sources": len(sources),
                "assets": len(assets),
                "metric_errors": metric_errors,
                "effective_sample_sizes": ess.tolist(),
                "historical_recipe": historical_recipe,
                "saved_image_score": generic["saved_images"],
                "output": str(out / "audit.json"),
            },
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
