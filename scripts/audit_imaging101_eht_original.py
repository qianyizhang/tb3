"""Audit pinned EHT closure imaging without simulation or reconstruction.

Verify released bytes, replay selected fixture arithmetic and saved-array scoring,
and intercept local staging. Never import upstream authoring modules, construct
an optimizer, install ehtim, generate observations or launch an agent.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import hashlib
import importlib.util
import json
import logging
import math
import os
import shutil
import warnings
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, json_safe, selected, sha, stats

TASK = "eht_black_hole_original"
COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def maximum_error(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def verify(source):
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    known = {r["path"]: r for r in tree["tree"]}
    receipt = json.loads((source / "fetch-receipt.json").read_text())
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
    assert len(sources) == 79 and len(assets) == 40
    return sources, assets, listing


def compare(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape
    return {
        "shape": list(actual.shape),
        "max_abs_error": maximum_error(actual, expected),
        "relative_l2_error": float(
            np.linalg.norm(actual - expected) / (np.linalg.norm(expected) + 1e-30)
        ),
    }


def main(numerical_warnings):
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
    assert (task / "data/meta_data").read_bytes() == (task / "data/meta_data.json").read_bytes()
    ref_dir = task / "evaluation/reference_outputs"
    saved = {p.stem: np.load(p, allow_pickle=False) for p in sorted(ref_dir.glob("*.npy"))}
    assert all(v.shape == (64, 64) and np.isfinite(v).all() for v in saved.values())
    assert len(saved) == 10 and len(raw) == 20
    assert np.array_equal(truth["image"], saved["ground_truth"])
    assert np.array_equal(truth["image_jy"], saved["ground_truth_jy"])
    assert np.allclose(truth["image_jy"], 0.6 * truth["image"])
    fixtures = {
        str(p.relative_to(task / "evaluation/fixtures")): arrays(p)
        for p in sorted((task / "evaluation/fixtures").rglob("*.npz"))
    }
    assert all(
        np.isfinite(v).all()
        for f in fixtures.values()
        for v in f.values()
        if np.issubdtype(v.dtype, np.number)
    )
    selections, replay = {}, {}
    ns = {"np": np, "math": math, "os": os, "json": json, "combinations": combinations}
    selections["fixed_reference_formula"] = selected(
        task / "src/generate_data.py", ["make_ring_image"], ns
    )
    reference_formula = compare(ns["make_ring_image"](N=64), truth["image"])
    assert reference_formula["max_abs_error"] < 1e-14
    names = [
        "load_observation",
        "load_metadata",
        "find_triangles",
        "find_quadrangles",
        "_find_baseline",
        "compute_closure_phases",
        "compute_log_closure_amplitudes",
        "closure_phase_sigma",
        "closure_amplitude_sigma",
    ]
    selections["preprocessing"] = selected(task / "src/preprocessing.py", names, ns)
    assert all(
        np.array_equal(v, raw[k]) for k, v in ns["load_observation"](str(task / "data")).items()
    )
    assert ns["load_metadata"](str(task / "data")) == meta
    for name in names[2:]:
        if name == "_find_baseline":
            continue
        f = fixtures[f"preprocessing/{name}.npz"]
        values = [v for k, v in f.items() if k.startswith("input_")]
        if name.startswith("find_"):
            values[1] = int(values[1])
        expected = next(v for k, v in f.items() if k.startswith("output_"))
        replay[name] = compare(ns[name](*values), expected)
        assert replay[name]["max_abs_error"] < 1e-12
    loaded = fixtures["preprocessing/load_observation.npz"]
    assert np.array_equal(raw["vis_cal"][:5], loaded["output_vis_cal_first"])
    assert np.array_equal(raw["uv_coords"][:5], loaded["output_uv_first"])
    assert (
        json.loads((task / "evaluation/fixtures/preprocessing/load_metadata.json").read_text())
        == meta
    )
    selections["operator"] = selected(
        task / "src/physics_model.py", ["_triangle_pulse_F", "_ftmatrix"], ns
    )
    methods = [
        "forward",
        "adjoint",
        "dirty_image",
        "psf",
        "visibility_chisq",
        "visibility_chisq_grad",
        "chisq_cphase_from_uv",
        "chisqgrad_cphase_from_uv",
        "chisq_logcamp_from_uv",
        "chisqgrad_logcamp_from_uv",
    ]
    selections["physics_arithmetic"] = selected(
        task / "src/physics_model.py", methods, ns, "ClosureForwardModel"
    )
    matrices = fixtures["physics_model/amatrices.npz"]
    matrix_errors = {}
    contraction_controls = {}
    for a_key, uv_key in [
        ("A_full", "uv_coords"),
        *[(f"A_cp{i}", f"cp_u{i}") for i in range(1, 4)],
        *[(f"A_lca{i}", f"lca_u{i}") for i in range(1, 5)],
    ]:
        assert np.array_equal(raw[uv_key], matrices[uv_key])
        value = ns["_ftmatrix"](meta["pixel_size_rad"], 64, raw[uv_key])
        matrix_errors[a_key] = compare(value, matrices[a_key])
        assert matrix_errors[a_key]["max_abs_error"] < 1e-14
        # Independent non-BLAS contraction checks numerical results even if
        # this machine's NumPy/Accelerate matmul emits floating-point warnings.
        vector = truth["image_jy"].ravel()
        contraction_controls[a_key] = compare(value @ vector, np.einsum("ij,j->i", value, vector))
        assert contraction_controls[a_key]["max_abs_error"] < 1e-12
    matrix_fixture = fixtures["physics_model/ftmatrix.npz"]
    replay["ftmatrix"] = compare(
        ns["_ftmatrix"](
            float(matrix_fixture["pixel_size_rad"]),
            int(matrix_fixture["N"]),
            matrix_fixture["uv_rows"],
        ),
        matrix_fixture["A_rows"],
    )
    model = SimpleNamespace(A=matrices["A_full"], N=64)
    for name in ["forward", "adjoint", "dirty_image", "psf"]:
        setattr(model, name, lambda *args, name=name: ns[name](model, *args))
    for name, input_key, output_key in [
        ("forward", "input_image", "output_vis"),
        ("adjoint", "input_vis", "output_image"),
        ("dirty_image", "input_vis", "output_image"),
        ("psf", None, "output_psf"),
    ]:
        f = fixtures[f"physics_model/{name}.npz"]
        v = getattr(model, name)(*[f[input_key]] if input_key else [])
        replay[name] = compare(v, f[output_key])
        assert replay[name]["max_abs_error"] < 1e-10
    # The forward_unit fixture declares ten UV rows but retains 421 outputs.
    f = fixtures["physics_model/forward_unit.npz"]
    small_forward = (
        ns["_ftmatrix"](float(f["param_pixel_size_rad"]), int(f["param_N"]), f["param_uv_coords"])
        @ f["input_image"].ravel()
    )
    forward_unit = {
        "declared_uv_rows": len(f["param_uv_coords"]),
        "stored_output_rows": len(f["output_vis"]),
        "first_ten_comparison": compare(small_forward, f["output_vis"][:10]),
        "full_observation_comparison": compare(model.forward(f["input_image"]), f["output_vis"]),
        "status": "Fixture parameters and output lengths disagree; do not treat its full output as a ten-row operator test.",
    }
    closure_replay = {}
    for term, prefix, nlegs in [("cphase", "cp", 3), ("logcamp", "lca", 4)]:
        f = fixtures[f"physics_model/chisq_{term}.npz"]
        values = [f[f"{prefix}_u{i}"] for i in range(1, nlegs + 1)]
        values += [
            f[f"{prefix}_values" + ("_deg" if prefix == "cp" else "")],
            f[f"{prefix}_sigmas" + ("_deg" if prefix == "cp" else "")],
        ]
        for condition in ["gt", "pert"]:
            image = f[f"input_image_{condition}"]
            args_ = [image.ravel(), 64, meta["pixel_size_rad"], *values]
            value = ns[f"chisq_{term}_from_uv"](*args_)
            grad = ns[f"chisqgrad_{term}_from_uv"](*args_)
            row = {
                "value": value,
                "value_comparison": compare(value, f[f"output_chisq_{condition}"]),
                "gradient_comparison": compare(grad, f[f"output_grad_{condition}"]),
            }
            assert row["value_comparison"]["relative_l2_error"] < 1e-10
            assert row["gradient_comparison"]["relative_l2_error"] < 1e-10
            closure_replay[f"{term}_{condition}"] = row
    f = fixtures["physics_model/chisq_vis.npz"]
    vis_value = ns["visibility_chisq"](model, f["input_image"], raw["vis_cal"], raw["sigma_vis"])
    vis_grad = ns["visibility_chisq_grad"](
        model, f["input_image"], raw["vis_cal"], raw["sigma_vis"]
    )
    vis_replay = {
        "source_value": vis_value,
        "stored_value": float(f["output_chisq"]),
        "value_ratio": vis_value / float(f["output_chisq"]),
        "gradient_comparison_to_twice_fixture": compare(vis_grad, 2 * f["output_grad"]),
        "scope": "Helper divides by M; the ehtim fixture and solver objective divide by 2M.",
    }
    assert (
        np.isclose(vis_replay["value_ratio"], 2)
        and vis_replay["gradient_comparison_to_twice_fixture"]["relative_l2_error"] < 1e-10
    )
    regularizers = {}
    for cls, prefix in [
        ("GullSkillingRegularizer", "gs"),
        ("SimpleEntropyRegularizer", "simple"),
        ("TVRegularizer", "tv"),
    ]:
        reg_ns = {"np": np}
        selections[cls] = selected(task / "src/solvers.py", ["value_and_grad"], reg_ns, cls)
        f = fixtures["solvers/tv_regularizer.npz" if prefix == "tv" else "solvers/regularizers.npz"]
        driver = (
            SimpleNamespace(epsilon=1e-6)
            if prefix == "tv"
            else SimpleNamespace(prior=f["prior_image"])
        )
        value, grad = reg_ns["value_and_grad"](driver, f["input_image"])
        regularizers[prefix] = {
            "value": value,
            "value_comparison": compare(
                value, f["output_val" if prefix == "tv" else f"{prefix}_val"]
            ),
            "gradient_comparison": compare(
                grad.ravel(), f["output_grad" if prefix == "tv" else f"{prefix}_grad"].ravel()
            ),
        }
        assert regularizers[prefix]["value_comparison"]["relative_l2_error"] < 1e-12
        assert regularizers[prefix]["gradient_comparison"]["relative_l2_error"] < 1e-12
        if prefix == "tv":
            # An explicit fixed arithmetic counterexample, independent of the
            # fixture copied from this same implementation. No optimization.
            x = np.array([[1.0, 2.0, 4.0], [3.0, 5.0, 7.0]])
            direction = np.array([[1.0, -2.0, 3.0], [-1.0, 1.0, -2.0]])
            _, gradient = reg_ns["value_and_grad"](driver, x)
            finite_differences = {}
            for epsilon in [1e-4, 1e-5, 1e-6]:
                plus, _ = reg_ns["value_and_grad"](driver, x + epsilon * direction)
                minus, _ = reg_ns["value_and_grad"](driver, x - epsilon * direction)
                finite_differences[str(epsilon)] = (plus - minus) / (2 * epsilon)
            dot = float(np.sum(gradient * direction))
            assert all(np.isclose(v, -dot, rtol=1e-7) for v in finite_differences.values())
            regularizers[prefix]["directional_derivative_control"] = {
                "image": x.tolist(),
                "direction": direction.tolist(),
                "source_gradient_dot_direction": dot,
                "central_differences": finite_differences,
                "finding": "Retained TV helper gradient has the opposite sign to the derivative of its returned value; the matching fixture repeats this defect. Main released six-method comparison uses gs/simple, not TV.",
            }
    triangles = ns["find_triangles"](raw["station_ids"], 7)
    quadrangles = ns["find_quadrangles"](raw["station_ids"], 7)
    gains = np.linspace(0.8, 1.2, 7) * np.exp(1j * np.linspace(-0.5, 0.7, 7))
    ids = raw["station_ids"]
    altered = raw["vis_cal"] * gains[ids[:, 0]] * np.conj(gains[ids[:, 1]])
    cp = ns["compute_closure_phases"](raw["vis_cal"], ids, triangles)
    gained_cp = ns["compute_closure_phases"](altered, ids, triangles)
    ca = ns["compute_log_closure_amplitudes"](raw["vis_cal"], ids, quadrangles)
    gained_ca = ns["compute_log_closure_amplitudes"](altered, ids, quadrangles)
    gain_control = {
        "phase_wrapped_max_error_rad": float(
            np.max(np.abs((cp - gained_cp + np.pi) % (2 * np.pi) - np.pi))
        ),
        "logamp_max_error": maximum_error(ca, gained_ca),
        "scope": "Fixed station multipliers applied algebraically to the same released samples; no noise draw or simulated observation. Checks cancellation only, not scan grouping.",
    }
    assert (
        gain_control["phase_wrapped_max_error_rad"] < 1e-12
        and gain_control["logamp_max_error"] < 1e-12
    )
    first_triangle_uv_sums = []
    for i, j, k in triangles:
        uv_sum = np.zeros(2)
        for a, b in [(i, j), (j, k), (k, i)]:
            index, conjugate = ns["_find_baseline"](ids, a, b)
            uv_sum += (-1 if conjugate else 1) * raw["uv_coords"][index]
        first_triangle_uv_sums.append(float(np.linalg.norm(uv_sum)))
    grouping = {
        "station_pairs": len(np.unique(np.sort(ids, axis=1), axis=0)),
        "visibility_rows": len(ids),
        "first_match_triangles": len(triangles),
        "first_match_quadrangles": len(quadrangles),
        "stored_per_scan_closure_phases": len(raw["cp_values_deg"]),
        "stored_per_scan_logamps": len(raw["lca_values"]),
        "first_triangle_uv_closure_norm_wavelengths": first_triangle_uv_sums,
        "stored_triangle_uv_closure_max_wavelengths": float(
            np.max(np.linalg.norm(raw["cp_u1"] + raw["cp_u2"] + raw["cp_u3"], axis=1))
        ),
        "scope": "The small preprocessing helper picks the first row per station pair and loses scan identity; main.py uses the supplied per-scan UV arrays instead. Raw archive has no timestamps.",
    }
    noise_differences = {}
    gain_fixture = fixtures["preprocessing/gain_invariance.npz"]
    for label, phase_a, phase_b, amp_a, amp_b in [
        (
            "raw",
            raw["cp_values_deg"],
            raw["cp_corrupt_values_deg"],
            raw["lca_values"],
            raw["lca_corrupt_values"],
        ),
        (
            "gain_fixture",
            gain_fixture["cp_cal_deg"],
            gain_fixture["cp_corrupt_deg"],
            gain_fixture["lca_cal"],
            gain_fixture["lca_corrupt"],
        ),
    ]:
        phase = (phase_b - phase_a + 180) % 360 - 180
        amp = amp_b - amp_a
        noise_differences[label] = {
            "phase_wrapped_rms_deg": float(np.sqrt(np.mean(phase**2))),
            "phase_wrapped_max_abs_deg": float(np.max(np.abs(phase))),
            "logamp_rms": float(np.sqrt(np.mean(amp**2))),
            "logamp_max_abs": float(np.max(np.abs(amp))),
        }
    metric_ns, generator_ns = {"np": np}, {"np": np}
    selections["image_metrics"] = selected(
        task / "src/visualization.py", ["compute_metrics"], metric_ns
    )
    selections["generator_metric_only"] = selected(
        task / "generate_ehtim_references.py", ["compute_metrics"], generator_ns
    )
    native_metrics = {k: metric_ns["compute_metrics"](v, truth["image"]) for k, v in saved.items()}
    generator_metrics = {
        k: generator_ns["compute_metrics"](v, truth["image"]) for k, v in saved.items()
    }
    original_metrics = json.loads((ref_dir / "metrics.json").read_text())
    names = {"vis_rml": "Vis RML", "amp_cp": "Amp+CP", "closure-only": "Closure-only"}
    for method, label in names.items():
        for condition in ["cal", "corrupt"]:
            actual = native_metrics[f"{method}_{condition}"]
            assert all(
                actual[k] == v for k, v in original_metrics[f"{label} ({condition})"].items()
            )
    f = fixtures["visualization/compute_metrics.npz"]
    m = metric_ns["compute_metrics"](f["input_estimate"], f["input_reference"])
    replay["image_metrics"] = {k: compare(m[k], f[f"output_{k}"]) for k in ["nrmse", "ncc"]}
    old_m = generator_ns["compute_metrics"](f["input_estimate"], f["input_reference"])
    replay["image_metrics"]["source_range_nrmse"] = m["nrmse"]
    replay["image_metrics"]["stored_nrmse"] = float(f["output_nrmse"])
    replay["image_metrics"]["generator_rms_nrmse"] = old_m["nrmse"]
    replay["image_metrics"]["finding"] = (
        "Fixture retains the older reference-RMS denominator; current visualization helper uses reference range. Original fixture is unchanged."
    )
    assert old_m["nrmse"] == float(f["output_nrmse"]) and m["ncc"] == float(f["output_ncc"])
    harness = source / "evaluation_harness"
    spec = importlib.util.spec_from_file_location(
        "eht_original_reference_scoring", harness / "reference_scoring.py"
    )
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=reference)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("eht-original-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer"] = selected(
        harness / "scorer.py", ["_compute_quality_metrics"], scorer_ns, "Scorer"
    )
    generic = {}
    score_values = {
        **saved,
        "zero_control": np.zeros((64, 64)),
        "closure_corrupt_unit_flux_control": saved["closure-only_corrupt"]
        / saved["closure-only_corrupt"].sum(),
    }
    for name, value in score_values.items():
        dest = out / "scoring" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", value)
        driver = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
            runner=SimpleNamespace(container=str(dest.parent)),
        )
        generic[name] = scorer_ns["_compute_quality_metrics"](driver)
    assert generic["ground_truth"]["nrmse"] == 0 and generic["ground_truth_jy"]["nrmse"] > 0
    assert all(v["passed"] is None for v in generic.values())
    # Replay only the captured fallback metric snippet in a local directory;
    # never create Docker or invoke runner.exec / a shell.
    scorer_class = next(
        n
        for n in ast.parse((harness / "scorer.py").read_text()).body
        if isinstance(n, ast.ClassDef) and n.name == "Scorer"
    )
    method = next(
        n
        for n in scorer_class.body
        if isinstance(n, ast.FunctionDef) and n.name == "_compute_quality_metrics_generic"
    )
    snippet_node = next(
        n
        for n in ast.walk(method)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "snippet" for t in n.targets)
    )
    snippet = ast.literal_eval(snippet_node.value)
    snippet_tree = ast.parse(snippet)
    # Extract arithmetic after array loading, before final print; arrays are
    # supplied directly, so no imports, filesystem checks or process calls run.
    start = next(
        i
        for i, n in enumerate(snippet_tree.body)
        if isinstance(n, ast.Assign)
        and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id == "out"
        and isinstance(n.value, ast.BinOp)
    )
    nodes = snippet_tree.body[start:-1]
    fallback = {}
    for name in ["closure-only_corrupt", "ground_truth_jy"]:
        scope = {"np": np, "out": saved[name].copy(), "gt": truth["image"].copy()}
        exec(
            compile(ast.Module(body=nodes, type_ignores=[]), str(harness / "scorer.py"), "exec"),
            scope,
        )
        fallback[name] = {k: float(scope[k]) for k in ["nrmse", "ncc", "mse", "psnr", "ssim"]}
    stage_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("eht-original-audit")}
    selections["visible_paths"] = selected(
        harness / "runner.py", ["_get_visible_paths"], stage_ns, "BenchmarkRunner"
    )
    selections["local_staging"] = selected(
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
            "copied_files": sorted(
                str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()
            ),
        }
    notebook_outputs = {}
    for notebook in sorted((task / "notebooks").glob("*.ipynb")):
        cells = json.loads(notebook.read_text())["cells"]
        text = "\n".join(
            f"CELL {i}\n" + "\n".join("".join(o.get("text", [])) for o in cell.get("outputs", []))
            for i, cell in enumerate(cells)
        )
        path = out / f"{notebook.stem}-retained-output.txt"
        path.write_text(text)
        notebook_outputs[notebook.name] = {"cells": len(cells), "output_sha256": sha(path)}
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
        "selected_functions": selections,
        "raw_array_schema": {
            k: {
                "shape": list(v.shape),
                "dtype": str(v.dtype),
                "nonfinite": int((~np.isfinite(v)).sum()),
            }
            for k, v in raw.items()
        },
        "truth_array_stats": {k: stats(v) for k, v in truth.items()},
        "reference_formula_replay": reference_formula,
        "retained_arrays": {k: {**stats(v), "sum": float(v.sum())} for k, v in saved.items()},
        "fixture_array_schemas": {
            name: {k: {"shape": list(v.shape), "dtype": str(v.dtype)} for k, v in f.items()}
            for name, f in fixtures.items()
        },
        "fixture_replays": replay,
        "matrix_replays": matrix_errors,
        "independent_einsum_contraction_controls": contraction_controls,
        "forward_unit_fixture_inconsistency": forward_unit,
        "closure_chisq_replays": closure_replay,
        "visibility_chisq_convention": vis_replay,
        "regularizer_replays": regularizers,
        "fixed_gain_control": gain_control,
        "closure_grouping": grouping,
        "released_calibrated_corrupt_differences": noise_differences,
        "noise_scope": "Source independently calls noisy observation routines; calibrated/corrupt differences are not a pure deterministic gain test. No noise calibration or repeated trial inferred.",
        "original_metrics": original_metrics,
        "flux_normalized_range_metrics": native_metrics,
        "generator_flux_normalized_rms_metrics": generator_metrics,
        "generic_dispatch": generic,
        "fallback_snippet_arithmetic": fallback,
        "metric_conventions": "metrics.json matches src/visualization.py: flux-match then range NRMSE. Generator and fallback use flux-match then reference-RMS NRMSE. Live filesystem scorer uses range NRMSE without flux-match, against unit-sum ground_truth.npy. All lack task pass/fail boundaries.",
        "reference_scale": {
            "image_sum": float(truth["image"].sum()),
            "image_jy_sum": float(truth["image_jy"].sum()),
            "README_issue": "README calls image Jy/pixel, but it is unit-sum; image_jy is the 0.6 Jy image. Live scorer selects the unit-sum image.",
        },
        "staging": staging,
        "notebook_outputs": notebook_outputs,
        "provenance_limits": [
            "Saved arrays and fixtures are pinned, but notebooks retain different outputs and warnings; notebook replay was not performed.",
            "cpca_tv.npy is retained and scored descriptively; no matching authoring call or optimization trace was found in the pinned task code.",
            "No end-to-end optimizer convergence or fresh reconstruction is established by fixed numerical parity.",
        ],
        "numerical_runtime": {
            "numpy": np.__version__,
            "warning_count": len(numerical_warnings),
            "warnings": sorted(
                {f"{w.filename}:{w.lineno}: {w.message}" for w in numerical_warnings}
            ),
            "scope": "Warnings retained. All loaded numeric arrays and compared results are finite. DFT matrix-vector results also match independent non-BLAS einsum contractions; warnings alone do not establish corrupted numerical outputs.",
        },
        "scope": "Pinned source/array audit, selected fixture arithmetic, saved-output metrics and intercepted local staging only. No ehtim installation, observation generation, random sampling, reconstruction, model trial or scientific efficacy claim.",
    }
    (out / "audit.json").write_text(json.dumps(json_safe(record), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "sources": len(sources),
                "assets": len(assets),
                "native_corrupt_closure": native_metrics["closure-only_corrupt"],
                "generic_corrupt_closure": generic["closure-only_corrupt"],
                "grouping": grouping,
                "output": str(out / "audit.json"),
            },
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    with warnings.catch_warnings(record=True) as numerical_warnings:
        warnings.simplefilter("always", RuntimeWarning)
        main(numerical_warnings)
