"""Audit pinned fan-beam arrays, operators, saved outputs, staging and scores.

Executes selected pure source functions, fixed operator controls and saved-input
FBP replay. Never runs the dataset generator, iterative solver, agent or installer.
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
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy
from scipy.interpolate import interp1d

COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
ASSET_REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected(path, names, namespace, class_name=None):
    body = ast.parse(path.read_text()).body
    if class_name:
        body = next(n for n in body if isinstance(n, ast.ClassDef) and n.name == class_name).body
    nodes = [n for n in body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return [{"name": n.name, "lines": [n.lineno, n.end_lineno]} for n in nodes]


def safe(value):
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return str(value)
    return value


def stats(array):
    array = np.asarray(array)
    return {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "min": float(array.min()),
        "max": float(array.max()),
        "nonfinite": int((~np.isfinite(array)).sum()),
        "array_bytes_sha256": hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.sources, args.output
    out.mkdir(parents=True, exist_ok=False)
    task = source / "tasks/ct_fan_beam"
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    alternatives = {
        r["path"]: r for r in json.loads((source / "source-alternate-receipt.json").read_text())
    }
    verified = []
    for name in ["fetch-receipt.json", "shared-source-receipt.json"]:
        receipt = json.loads((source / name).read_text())
        assert receipt["revision"] == COMMIT
        for original in receipt["files"]:
            row = alternatives.get(original["path"], original)
            p = source / row["path"]
            data = p.read_bytes()
            assert row["status"] == "verified" and sha(p) == row["sha256"]
            assert len(data) == row["bytes"]
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == row["git_blob_sha1"]
            )
            verified.append(row["path"])
    asset_alternatives = {
        r["path"]: r for r in json.loads((source / "asset-alternate-receipt.json").read_text())
    }
    acquired = []
    for original in json.loads((source / "asset-fetch-receipt.json").read_text()):
        row = asset_alternatives.get(original["path"], original)
        p = source / row["path"]
        assert row["status"] == "verified" and row["revision"] == ASSET_REVISION
        assert sha(p) == row["sha256"] and p.stat().st_size == row["size"]
        acquired.append(row["path"])
    assert len(acquired) == 7
    assert json.loads((source / "hf-revision.json").read_text())["sha"] == ASSET_REVISION
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    truth = np.load(task / "data/ground_truth.npz", allow_pickle=False)
    fixture = np.load(task / "evaluation/fixtures/physics_model_fixtures.npz", allow_pickle=False)
    saved = {
        name: np.load(task / f"evaluation/reference_outputs/recon_{name}.npz", allow_pickle=False)
        for name in ["fbp_full", "fbp_short", "tv_short"]
    }
    meta = json.loads((task / "data/meta_data.json").read_text())
    ns = {"np": np, "interp1d": interp1d, "json": json, "os": os}
    selections = {}
    for file, names in [
        (
            "src/preprocessing.py",
            ["load_sinogram_data", "load_ground_truth", "load_metadata", "preprocess_sinogram"],
        ),
        (
            "src/physics_model.py",
            [
                "fan_beam_geometry",
                "fan_beam_forward_vectorized",
                "fan_beam_backproject",
                "ramp_filter",
                "parker_weights",
                "fan_beam_fbp",
            ],
        ),
        ("src/visualization.py", ["compute_ncc", "compute_nrmse", "centre_crop_normalize"]),
        ("src/solvers.py", ["_prox_l1_norm"]),
    ]:
        selections[file] = selected(task / file, names, ns)
    full, short, angles_full, angles_short, _det_pos = ns["load_sinogram_data"](task)
    full, short = ns["preprocess_sinogram"](full), ns["preprocess_sinogram"](short)
    gt = ns["load_ground_truth"](task)[0]
    assert full.shape == (180, 192) and short.shape == (116, 192) and gt.shape == (128, 128)
    geo_full = ns["fan_beam_geometry"](128, 192, len(angles_full), 256.0, 256.0)
    geo_short = ns["fan_beam_geometry"](
        128, 192, len(angles_short), 256.0, 256.0, meta["short_scan_range_deg"] * np.pi / 180
    )
    assert np.array_equal(geo_full["angles"].astype(np.float32), raw["angles_full"])
    assert np.array_equal(geo_short["angles"].astype(np.float32), raw["angles_short"])
    assert np.array_equal(geo_full["det_pos"].astype(np.float32), raw["det_pos"])
    code_gamma = np.arctan(geo_full["det_pos"][-1] / 256)
    physical_gamma = np.arctan(geo_full["det_pos"][-1] / 512)
    assert np.isclose(np.degrees(code_gamma), meta["fan_half_angle_deg"])
    assert np.isclose(np.degrees(np.pi + 2 * code_gamma), meta["short_scan_range_deg"])
    geometry = {
        "coordinate_units": "pixels; no supplied mm calibration, HU or patient orientation",
        "image_pixel_centers": [-63.5, 63.5],
        "detector_center_range": [float(geo_full["det_pos"][0]), float(geo_full["det_pos"][-1])],
        "detector_spacing": float(geo_full["det_spacing"]),
        "source_to_isocenter": 256,
        "source_to_detector": 512,
        "code_source_xy": "(-256*sin(beta), 256*cos(beta))",
        "code_detector_center_xy": "(256*sin(beta), -256*cos(beta))",
        "code_detector_axis_xy": "(cos(beta), sin(beta))",
        "readme_source_xy": "(256*cos(beta), 256*sin(beta)); differs by a quarter turn",
        "declared_half_fan_degrees": float(np.degrees(code_gamma)),
        "geometric_half_fan_degrees": float(np.degrees(physical_gamma)),
        "declared_sweep_degrees": meta["short_scan_range_deg"],
        "geometric_pi_plus_fan_degrees": float(np.degrees(np.pi + 2 * physical_gamma)),
        "full_angle_step_degrees": float(np.degrees(geo_full["angles"][1])),
        "short_angle_step_degrees": float(np.degrees(geo_short["angles"][1])),
        "endpoints_excluded": True,
        "saved_float32_coordinates_match_rebuilt_geometry": True,
        "note": "Metadata/generator/Parker use det_pos/256, while the source-detector separation is 512. Released geometry and weights are retained unchanged.",
    }
    fixture_geo = ns["fan_beam_geometry"](32, 48, 18, 128.0, 128.0)
    fixtures = {}
    for name, computed in [
        ("forward", ns["fan_beam_forward_vectorized"](fixture["input_phantom"], fixture_geo)),
        ("backprojection", ns["fan_beam_backproject"](fixture["output_sinogram"], fixture_geo)),
        (
            "fbp",
            ns["fan_beam_fbp"](
                fixture["output_sinogram"], fixture_geo, filter_type="hann", cutoff=0.3
            ),
        ),
    ]:
        expected = fixture[
            {
                "forward": "output_sinogram",
                "backprojection": "output_backprojection",
                "fbp": "output_fbp",
            }[name]
        ]
        fixtures[name] = float(np.max(np.abs(computed - expected)))
        assert np.allclose(computed, expected, rtol=1e-12, atol=1e-12)
    # Source FBP replay from saved measurements: no optimization or generation.
    replay = {}
    for name, sino, geo, is_short in [
        ("fbp_full", full, geo_full, False),
        ("fbp_short", short, geo_short, True),
    ]:
        rebuilt = np.maximum(
            ns["fan_beam_fbp"](sino, geo, filter_type="hann", cutoff=0.3, short_scan=is_short), 0
        )
        reference = saved[name]["reconstruction"][0]
        replay[name] = {
            "float64_vs_saved_float32_max_abs_error": float(np.max(np.abs(rebuilt - reference))),
            "float32_exact": bool(np.array_equal(rebuilt.astype(np.float32), reference)),
        }
        assert replay[name]["float32_exact"]
    # Single-pixel controls derive the exact magnification and two-bin splat.
    pixel_controls = []
    for row, col, angle in [(64, 80, 0), (96, 80, 0), (64, 80, 45)]:
        impulse = np.zeros((128, 128))
        impulse[row, col] = 1
        geo = dict(geo_full, angles=geo_full["angles"][[angle]], n_angles=1)
        projected = ns["fan_beam_forward_vectorized"](impulse, geo)[0]
        beta = geo["angles"][0]
        x, y = col - 63.5, row - 63.5
        t = x * np.cos(beta) + y * np.sin(beta)
        s = -x * np.sin(beta) + y * np.cos(beta)
        u = 256 - s
        magnification = 512 / u
        coordinate = t * magnification
        index = (coordinate - geo["det_pos"][0]) / geo["det_spacing"]
        lo = int(index)
        fraction = index - lo
        expected = np.zeros(192)
        expected[lo : lo + 2] = np.array([1 - fraction, fraction]) * magnification
        assert np.allclose(projected, expected, rtol=1e-12, atol=1e-12)
        pixel_controls.append(
            {
                "row": row,
                "column": col,
                "angle_index": angle,
                "angle_degrees": float(np.degrees(beta)),
                "xy_pixels": [x, y],
                "U": float(u),
                "magnification": float(magnification),
                "detector_coordinate": float(coordinate),
                "bins": [lo, lo + 1],
                "weights": projected[[lo, lo + 1]].tolist(),
                "max_abs_error": float(np.max(np.abs(projected - expected))),
                "scope": "Unit-pixel operator diagnostic; not a source phantom or reconstruction.",
            }
        )
    pw = ns["parker_weights"](geo_short["angles"], geo_short["det_pos"], 256)
    assert pw.shape == short.shape and pw.min() >= 0 and pw.max() <= 1
    # A deterministic inner-product check refutes exact Euclidean adjointness.
    rng = np.random.default_rng(47)
    x = rng.normal(size=(32, 32))
    y = rng.normal(size=(18, 48))
    ax = ns["fan_beam_forward_vectorized"](x, fixture_geo)
    by = ns["fan_beam_backproject"](y, fixture_geo)
    left = float(np.vdot(ax, y))
    right = float(np.vdot(x, by))
    adjoint = {
        "seed": 47,
        "shape_image": [32, 32],
        "shape_measurements": [18, 48],
        "inner_Ax_y": left,
        "inner_x_By": right,
        "relative_error": abs(left - right) / max(abs(left), abs(right)),
        "scope": "Euclidean inner product for the shipped discrete forward/backproject pair; no solver run.",
    }
    assert adjoint["relative_error"] > 0.1
    # Its documented radius projection also fails a direct fixed-vector control.
    vector = np.array([[[3.0]], [[4.0]]])
    prox = ns["_prox_l1_norm"](vector, 0.005)
    prox_control = {
        "input": [3, 4],
        "declared_ball_radius": 0.005,
        "output": prox.ravel().tolist(),
        "output_norm": float(np.linalg.norm(prox)),
        "scope": "One helper call. No TV iteration or replacement implementation.",
    }
    assert prox_control["output_norm"] == 5.0
    margin = int(128 * (1 - 0.8) / 2)
    crop = np.s_[margin : 128 - margin, margin : 128 - margin]
    outside = np.ones_like(gt, dtype=bool)
    outside[crop] = False
    arrays = {name: data["reconstruction"][0].astype(np.float64) for name, data in saved.items()}
    controls = {
        "truth": gt,
        "half-truth": gt * 0.5,
        "truth-plus-one": gt + 1,
        "outside-crop-plus-ten": gt + 10 * outside,
        "zero": np.zeros_like(gt),
    }
    gt_crop = ns["centre_crop_normalize"](gt)
    native = {}
    for name, array in {**arrays, **controls}.items():
        normalized = ns["centre_crop_normalize"](array)
        native[name] = {
            "ncc": ns["compute_ncc"](normalized, gt_crop),
            "nrmse": ns["compute_nrmse"](normalized, gt_crop),
            "raw_crop_min": float(array[crop].min()),
            "raw_crop_max": float(array[crop].max()),
        }
    for name in ["truth", "half-truth", "truth-plus-one", "outside-crop-plus-ten"]:
        assert np.isclose(native[name]["ncc"], 1) and native[name]["nrmse"] < 1e-14
    # The notebook retains historical printed values, though metrics.json is absent.
    notebook = json.loads((task / "notebooks/ct_fan_beam.ipynb").read_text())
    historical = "".join(
        "".join(o.get("text", [])) for o in notebook["cells"][17].get("outputs", [])
    )
    for name, ncc, nrmse in [
        ("fbp_full", 0.6518, 0.1929),
        ("fbp_short", 0.5578, 0.2110),
        ("tv_short", 0.9661, 0.0855),
    ]:
        assert round(native[name]["ncc"], 4) == ncc and round(native[name]["nrmse"], 4) == nrmse
    loss = saved["tv_short"]["loss_history"].astype(np.float64)
    loss_record = {
        "samples": int(loss.size),
        "first": float(loss[0]),
        "last": float(loss[-1]),
        "increasing_steps": int(np.count_nonzero(np.diff(loss) > 0)),
        "values": loss.tolist(),
        "definition": "Saved 0.5*sum((A*x-b)^2), without TV penalty; no iterate images and no fresh TV run.",
    }
    # Replay the exact file-seeding methods; intercept every installation command.
    harness = source / "evaluation_harness"
    staging_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("fan-beam-audit")}
    selections["runner.py"] = selected(
        harness / "runner.py", ["_get_visible_paths"], staging_ns, "BenchmarkRunner"
    )
    selections["local_runner.py"] = selected(
        harness / "local_runner.py", ["start"], staging_ns, "LocalRunner"
    )
    staging = {}
    for level in ["L1", "L2", "L3"]:
        dest = out / level
        dest.mkdir()
        commands = []
        staging_ns["tempfile"] = SimpleNamespace(
            mkdtemp=lambda directory=dest, **_: str(directory.resolve())
        )
        runner = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(mode="end_to_end", level=level)),
            task_dir=task.resolve(),
            exec=lambda cmd, log=commands: log.append(cmd),
        )
        visible = staging_ns["_get_visible_paths"](runner)
        staging_ns["start"](runner, visible)
        assert sha(dest / "data/ground_truth.npz") == sha(task / "data/ground_truth.npz")
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "files": sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()),
            "truth_copied": True,
            "commands_intercepted": commands,
        }
    spec = importlib.util.spec_from_file_location(
        "fan_beam_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=ref)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("fan-beam-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer.py"] = selected(
        harness / "scorer.py",
        ["_compute_quality_metrics", "_compute_quality_metrics_generic"],
        scorer_ns,
        "Scorer",
    )
    generic = {}
    references = {}
    for name, array in {
        **arrays,
        **controls,
        "stacked-maps": np.stack(list(arrays.values())),
        "saved-loss-only": loss,
    }.items():
        dest = out / "scoring" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", array)
        runner = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
            runner=SimpleNamespace(container=str(dest.parent)),
        )
        generic[name] = scorer_ns["_compute_quality_metrics"](runner)
        if "error" not in generic[name]:
            reference, p = ref.load_reference_array(task, target_shape=array.shape)
            assert np.array_equal(reference, gt)
            references[name] = {
                "path": str(p.relative_to(source)),
                "key": "phantom",
                "shape": list(reference.shape),
            }
    assert all(v.get("passed") is None for v in generic.values())
    assert "error" in generic["stacked-maps"] and "error" in generic["saved-loss-only"]
    assert generic["half-truth"]["nrmse"] > 0.1 and generic["outside-crop-plus-ten"]["nrmse"] > 1
    dest = out / "scoring/native-npz/output"
    dest.mkdir(parents=True)
    np.savez(dest / "recon_tv_short.npz", reconstruction=arrays["tv_short"])
    driver = SimpleNamespace(
        config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
        runner=SimpleNamespace(container=str(dest.parent)),
    )
    generic["native-npz"] = scorer_ns["_compute_quality_metrics"](driver)
    driver.runner.container = None
    driver._compute_quality_metrics_generic = lambda: scorer_ns["_compute_quality_metrics_generic"](
        driver
    )
    generic["no-filesystem-fallback"] = scorer_ns["_compute_quality_metrics"](driver)
    assert (
        generic["no-filesystem-fallback"]["error"] == "ground_truth.npy not found in task directory"
    )
    assert not any(
        r["path"].startswith("tasks/ct_fan_beam/") and r["path"].endswith("metrics.json")
        for r in tree["tree"]
    )
    report = {
        "schema": 1,
        "entry_id": "imaging101-ct-fan-beam",
        "source_commit": COMMIT,
        "audit_script_sha256": sha(Path(__file__)),
        "verified_source_files": verified,
        "verified_assets": acquired,
        "runtime": {"numpy": np.__version__, "scipy": scipy.__version__},
        "raw": {k: stats(raw[k]) for k in raw.files},
        "truth": {k: stats(truth[k]) for k in truth.files},
        "saved": {name: {k: stats(d[k]) for k in d.files} for name, d in saved.items()},
        "metadata": meta,
        "geometry": geometry,
        "fixture_max_abs_errors": fixtures,
        "saved_fbp_replay": replay,
        "pixel_controls": pixel_controls,
        "parker_weights": {
            "stats": stats(pw),
            "selected_detector_bins": [0, 95, 191],
            "selected_curves": pw[:, [0, 95, 191]].T.tolist(),
            "angles_degrees": np.degrees(geo_short["angles"]).tolist(),
        },
        "adjoint_control": adjoint,
        "tv_projection_control": prox_control,
        "native_crop": {
            "margin": margin,
            "shape": list(gt_crop.shape),
            "pixels": int(gt_crop.size),
            "total_pixels": int(gt.size),
            "normalization": "Independent per-array min-max normalization after cropping",
        },
        "native_metrics": native,
        "notebook_historical_metrics": historical,
        "saved_data_fidelity": loss_record,
        "staging": staging,
        "generic_reference_selection": references,
        "generic_scoring": generic,
        "metrics_file_present": False,
        "source_function_selections": selections,
        "execution_scope": {
            "agent": False,
            "iterative_solver_steps": 0,
            "dataset_generation": False,
            "runtime_install": False,
            "docker": False,
            "source_fbp_replay": True,
            "fixed_operator_controls": True,
            "staging_file_copy": True,
            "generic_and_native_scoring": True,
        },
    }
    np.savez_compressed(
        out / "operator-diagnostics.npz",
        parker_weights=pw,
        angles_short=geo_short["angles"],
        detector_positions=geo_short["det_pos"],
    )
    (out / "audit.json").write_text(json.dumps(safe(report), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "fixtures": fixtures,
                "fbp_replay": replay,
                "geometry": geometry,
                "native": native,
                "generic": safe(generic),
                "adjoint": adjoint,
                "prox": prox_control,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
