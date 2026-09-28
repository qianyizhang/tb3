"""Audit released dynamic EHT arrays, small fixtures and scoring boundaries.

No upstream module import, generator, EM reconstruction, installation or agent
trial. Only selected numerical helpers and intercepted staging are executed.
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
import warnings
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, json_safe, selected, sha, stats

TASK = "eht_black_hole_dynamic"
COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def error(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def verify(source):
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    known = {r["path"]: r for r in tree["tree"]}
    receipt = json.loads((source / "fetch-retry-receipt.json").read_text())
    assert receipt["source_commit"] == COMMIT and receipt["asset_revision"] == REVISION
    shared = json.loads((source / "shared-source-receipt.json").read_text())["files"]
    extra = json.loads((source / "extra-asset-receipt.json").read_text())
    sources, assets = [], []
    manifest = {
        r["path"]: r for r in json.loads((source / "assets_manifest.json").read_text())["assets"]
    }
    for row in receipt["files"] + shared + [dict(extra, kind="extra-asset")]:
        p = source / row["path"]
        b = p.read_bytes()
        assert row["status"] == "verified" and sha(p) == row["sha256"]
        if row.get("kind", "source") == "source":
            assert blob(b) == known[row["path"]]["sha"]
            assert len(b) == known[row["path"]]["size"]
            sources.append(
                {
                    "path": row["path"],
                    "size": len(b),
                    "sha256": sha(p),
                    "git_blob_sha1": known[row["path"]]["sha"],
                    "status": "verified",
                    "url": f"https://raw.githubusercontent.com/AI4ImagingLab/imaging-101-release/{COMMIT}/{row['path']}",
                }
            )
        else:
            if row["kind"] == "asset":
                assert len(b) == manifest[row["path"]]["size"]
                assert sha(p) == manifest[row["path"]]["sha256"]
            assets.append(
                {
                    "path": row["path"],
                    "size": len(b),
                    "sha256": sha(p),
                    "revision": REVISION,
                    "status": "verified",
                    "url": f"https://hf.co/datasets/starpacker52/imaging-101/resolve/{REVISION}/{row['path']}",
                }
            )
    listing = json.loads((source / "hf-task-tree-receipt.json").read_text())
    assert sha(source / "hf-task-tree.json") == listing["sha256"]
    assert listing["link_header"] is None and listing["status"] == "verified"
    files = {
        r["path"]: r
        for r in json.loads((source / "hf-task-tree.json").read_text())
        if r["type"] == "file"
    }
    assert set(files) == {r["path"] for r in assets}
    for row in assets:
        f = files[row["path"]]
        assert row["size"] == f["size"]
        if "lfs" in f:
            assert row["sha256"] == f["lfs"]["oid"]
        else:
            assert blob((source / row["path"]).read_bytes()) == f["oid"]
    assert len(sources) == 73 and len(assets) == 18
    return sources, assets, listing


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
    truth = arrays(task / "data/ground_truth.npz")["images"]
    ref_dir = task / "evaluation/reference_outputs"
    saved = {
        n: np.load(ref_dir / (n + ".npy"), allow_pickle=False)
        for n in ["ground_truth", "static_reconstruction", "starwarps_reconstruction"]
    }
    assert np.array_equal(truth, saved["ground_truth"]) and truth.shape == (12, 30, 30)
    assert "frames_gt" not in raw and len(raw) == 50
    assert (task / "data/meta_data").read_bytes() == (task / "data/meta_data.json").read_bytes()
    meta = json.loads((task / "data/meta_data.json").read_text())
    selections = {}
    ns = {"np": np, "os": os, "json": json}
    for filename, names in [
        ("preprocessing.py", ["load_observation"]),
        ("visualization.py", ["compute_metrics", "compute_video_metrics"]),
        (
            "physics_model.py",
            [
                "delta_pulse_2d",
                "compute_visibilities",
                "grad_vis",
                "gen_freq_comp",
                "gen_phase_shift_matrix",
                "apply_motion_basis",
                "realimag_stack",
                "gauss_image_covariance",
                "affine_motion_basis",
                "calc_warp_matrix",
                "product_gaussians_lem1",
                "product_gaussians_lem2",
                "get_measurement_terms",
            ],
        ),
    ]:
        selections[filename] = selected(task / "src" / filename, names, ns)
    # DFTForwardModel contains only deterministic array arithmetic, no imports
    # or module initialization. Extract the class without importing src.
    path = task / "src/physics_model.py"
    node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.ClassDef))
    assert node.name == "DFTForwardModel"
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), ns)
    selections["DFTForwardModel"] = {"lines": [node.lineno, node.end_lineno]}
    fixture_dir = task / "evaluation/fixtures"
    fixtures = {}
    runtime_observations = []

    def forward(model, image):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = model.forward(image)
        independent = np.einsum("ij,j->i", model.matrix, image)
        assert np.isfinite(result).all() and np.isfinite(independent).all()
        assert np.allclose(result, independent, atol=1e-12, rtol=1e-12)
        if caught:
            runtime_observations.append(
                {
                    "operation": "DFTForwardModel.forward",
                    "warnings": [str(w.message) for w in caught],
                    "einsum_max_error": error(result, independent),
                    "interpretation": "Runtime warnings retained; returned finite values independently agree with explicit contraction. Not evidence of invalid input or solver failure.",
                }
            )
        return result

    def compare(label, actual, expected):
        fixtures[label] = error(actual, expected)
        assert np.allclose(actual, expected, atol=1e-12, rtol=1e-10), label

    f = arrays(fixture_dir / "physics_model/dft_forward.npz")
    model = ns["DFTForwardModel"](f["input_uv"], int(f["param_N"]), float(f["param_psize"]))
    compare("dft_forward.visibility", forward(model, f["input_imvec"]), f["output_vis"])
    compare("dft_forward.jacobian", model.matrix, f["output_grad"])
    f = arrays(fixture_dir / "physics_model/affine_motion_basis.npz")
    basis = ns["affine_motion_basis"](int(f["param_N"]), float(f["param_psize"]))
    for key, a in zip(
        ["init_x", "init_y", "flowbasis_x", "flowbasis_y", "initTheta"], basis, strict=True
    ):
        compare("affine_motion_basis." + key, a, f["output_" + key])
    f = arrays(fixture_dir / "physics_model/warp_matrix.npz")
    warp = ns["calc_warp_matrix"](
        int(f["param_N"]), float(f["param_psize"]), f["input_theta"], *basis
    )
    compare("warp_matrix", warp, f["output_warp"])
    compare("identity_warp_control", warp, np.eye(64))
    f = arrays(fixture_dir / "physics_model/gauss_covariance.npz")
    cov = ns["gauss_image_covariance"](int(f["param_N"]), float(f["param_psize"]), f["input_imvec"])
    compare("gauss_covariance", cov, f["output_cov"])
    for name, keys in [
        ("prod_gaussians_lem1", ["m1", "S1", "m2", "S2"]),
        ("prod_gaussians_lem2", ["A", "Sigma", "y", "mu", "Q"]),
    ]:
        f = arrays(fixture_dir / "physics_model" / (name + ".npz"))
        got = ns[name.replace("prod_", "product_")](*(f["input_" + k] for k in keys))
        for k, a in zip(["mean", "cov"], got, strict=True):
            compare(name + "." + k, a, f["output_" + k])
    obs = ns["load_observation"](task / "data")
    f = arrays(fixture_dir / "preprocessing/load_observation.npz")
    compare("load_observation.n_frames", obs["n_frames"], f["n_frames"])
    compare("load_observation.frame_times", obs["frame_times"], f["frame_times"])
    for name in ["vis", "sigma", "uv"]:
        compare("load_observation." + name, np.shape(obs[name][0]), f[name + "_0_shape"])
    f = arrays(fixture_dir / "visualization/compute_metrics.npz")
    for k, v in ns["compute_metrics"](f["input_est"], f["input_ref"]).items():
        compare("compute_metrics." + k, v, f["output_" + k])
    omitted_fixtures = {
        "solvers/solve_single_image.npz": "Prior covariance Lambda is absent; exact numerical inputs are incomplete. No solver called.",
        "visualization/compute_video_metrics.npz": "Only three output scalars are stored; input images are absent. Helper instead checked on saved video and original report.",
    }
    predicted = []
    residual_power = []
    real_ranks = []
    noise_cov_ratios = []
    for t in range(12):
        model = ns["DFTForwardModel"](obs["uv"][t], 30, meta["pixel_size_rad"])
        pred = forward(model, truth[t].ravel())
        predicted.append(pred)
        residual_power.append(float(np.mean(abs((obs["vis"][t] - pred) / obs["sigma"][t]) ** 2)))
        real_ranks.append(int(np.linalg.matrix_rank(numpy_real_stack(model.matrix))))
        *_, measured_cov, valid = ns["get_measurement_terms"](
            model, truth[t].ravel(), obs["vis"][t], obs["sigma"][t]
        )
        assert valid and measured_cov.shape == (56, 56)
        ratio = np.diag(measured_cov) / (np.tile(obs["sigma"][t], 2) ** 2 / 2)
        noise_cov_ratios.append([float(ratio.min()), float(ratio.max())])
    assert noise_cov_ratios == [[2.0, 2.0]] * 12
    controls = {
        "starwarps": saved["starwarps_reconstruction"],
        "static_per_frame": saved["static_reconstruction"],
        "oracle_truth": truth,
        "oracle_time_mean_repeated": np.repeat(truth.mean(0)[None, ...], 12, axis=0),
        "oracle_first_frame_repeated": np.repeat(truth[:1], 12, axis=0),
        "oracle_truth_reversed": truth[::-1],
        "starwarps_reversed": saved["starwarps_reconstruction"][::-1],
        "zeros": np.zeros_like(truth),
        "ten_times_starwarps": saved["starwarps_reconstruction"] * 10,
    }
    native = {k: ns["compute_video_metrics"](a, truth) for k, a in controls.items()}
    quoted = json.loads((ref_dir / "metrics.json").read_text())
    for k, old in [("starwarps", "StarWarps"), ("static_per_frame", "Static per-frame")]:
        for metric in ["ncc", "nrmse"]:
            assert abs(native[k]["average"][metric] - quoted[old]["average"][metric]) < 1e-14
            for j in range(12):
                assert (
                    abs(native[k]["per_frame"][j][metric] - quoted[old]["per_frame"][j][metric])
                    < 1e-14
                )
    angles = np.arctan2(*np.mgrid[-14.5:15.5, -14.5:15.5])
    diagnostics = {}
    for k, a in controls.items():
        moment = np.sum(a * np.exp(1j * angles), axis=(1, 2))
        phase = np.rad2deg(np.unwrap(np.angle(moment)))
        diagnostics[k] = {
            "flux_Jy": a.sum((1, 2)).tolist(),
            "adjacent_difference_error_ratio": float(
                np.linalg.norm(np.diff(a, axis=0) - np.diff(truth, axis=0))
                / np.linalg.norm(np.diff(truth, axis=0))
            ),
            "array_polar_moment_angle_deg": (phase % 360).tolist(),
            "array_polar_moment_net_change_deg": float(phase[-1] - phase[0]),
            "array": stats(a),
        }
    harness = source / "evaluation_harness"
    spec = importlib.util.spec_from_file_location(
        "dynamic_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=ref)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("eht-dynamic-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer"] = selected(
        harness / "scorer.py", ["_compute_quality_metrics"], scorer_ns, "Scorer"
    )
    generic = {}
    for name, a in {**controls, "only_one_frame": truth[0]}.items():
        dest = out / "scoring" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", a)
        driver = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
            runner=SimpleNamespace(container=str(dest.parent)),
        )
        generic[name] = scorer_ns["_compute_quality_metrics"](driver)
    assert generic["oracle_truth"]["nrmse"] == 0 and "error" in generic["only_one_frame"]
    assert generic["starwarps"]["passed"] is None
    assert all(v is None for v in generic["starwarps"]["boundaries"].values())
    task_ns = {
        "np": np,
        "Path": Path,
        "GENERIC_RECIPES": json.loads((harness / "task_recipes.json").read_text()),
        "_GENERIC_AGENT_OUTPUTS": ["reconstruction.npy", "reconstruction.npz"],
    }
    selections["task_recipe"] = selected(
        harness / "task_scoring.py",
        [
            "_recon_bases",
            "_find_recon",
            "_apply_transform",
            "_load_spec",
            "_recipe_generic",
            "_std_ncc",
            "_std_nrmse",
        ],
        task_ns,
    )
    recipe = task_ns["_recipe_generic"](
        TASK, task.resolve(), ref_dir.resolve(), SimpleNamespace(**ns)
    )
    assert recipe == ns["compute_metrics"](controls["starwarps"], truth)
    stage_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("eht-dynamic-audit")}
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
        for name in ["ground_truth.npz", "raw_data.npz", "meta_data.json"]:
            assert sha(dest / "data" / name) == sha(task / "data" / name)
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "available_files_copied": sorted(
                str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()
            ),
            "truth_copied": True,
            "commands_intercepted": commands,
        }
    defects = []
    try:
        ast.parse((task / "main.py").read_text())
    except SyntaxError as exc:
        defects.append(
            {"path": "main.py", "line": exc.lineno, "error": exc.msg, "text": exc.text.strip()}
        )
    assert len(defects) == 1 and "build_per_frame_models    from" in defects[0]["text"]
    notebook_outputs = {}
    for p in sorted((task / "notebooks").glob("*.ipynb")):
        notebook_outputs[p.name] = {
            str(i): ["".join(o["text"]) for o in c.get("outputs", []) if "text" in o]
            for i, c in enumerate(json.loads(p.read_text())["cells"])
            if any("text" in o for o in c.get("outputs", []))
        }
    report = {
        "schema": 1,
        "entry_id": "imaging101-eht-black-hole-dynamic",
        "date": "2026-09-29",
        "reviewer": "assistant",
        "source_commit": COMMIT,
        "asset_revision": REVISION,
        "script_sha256": sha(Path(__file__)),
        "helper_script_sha256": sha(
            Path(__file__).with_name("audit_imaging101_poisson_lowdose.py")
        ),
        "verified_sources": sources,
        "verified_assets": assets,
        "asset_listing_receipt": listing,
        "metadata": meta,
        "raw_array_shapes_and_dtypes": {
            k: {"shape": list(a.shape), "dtype": str(a.dtype)} for k, a in raw.items()
        },
        "frame_times_hours": obs["frame_times"].tolist(),
        "fixture_max_errors": fixtures,
        "runtime_observations": runtime_observations,
        "fixtures_not_replayed": omitted_fixtures,
        "forward_diagnostics": {
            "real_measurement_ranks": real_ranks,
            "image_unknowns_per_frame": 900,
            "complex_measurements_per_frame": 28,
            "mean_abs_residual_over_sigma_squared_per_frame": residual_power,
            "measurement_covariance_vs_generator_real_component_variance_ratio": noise_cov_ratios,
            "noise_convention": "Generator uses sigma*(normal+i*normal)/sqrt(2), so sigma is complex RMS; source measurement helper uses sigma squared for each real/imaginary component, twice that nominal variance. Source inspection plus fixed-array helper replay; no random noise generated.",
        },
        "native_video_metric_replay": native,
        "original_reference_metrics": quoted,
        "temporal_diagnostics": diagnostics,
        "generic_dispatch_replay": generic,
        "task_recipe_replay": recipe,
        "staging": staging,
        "source_defects": defects,
        "historical_notebook_outputs": notebook_outputs,
        "selected_pure_functions": selections,
        "scope_limits": [
            "No new measurements, reference generation, StarWarps EM, static reconstruction, optimizer, installation or agent trial.",
            "This release is a synthetic rotating crescent with an EHT-inspired array, not measured black-hole motion. Generator includes all 28 station pairs without an elevation cut; astropy UV synthesis was inspected but not executed.",
            "Native report averages 12 framewise range-NRMSE and centered NCC values. Historical recipe flattens the video first. Live local generic dispatch uses global range-NRMSE and cosine NCC; there are no published pass thresholds.",
            "The no-filesystem-workspace fallback in scorer.py requires a 2D reconstruction and therefore rejects a 3D video; its source was inspected but no Docker path was executed. Local replay is not cross-runner equivalence.",
            "Truth is copied into every L1-L3 end-to-end workspace. Oracle controls diagnose scoring, not reconstruction ability or legitimate blind baselines.",
            "Array polar moments use angle atan2(row-center,column-center) in the source origin-lower display convention; these are descriptive brightness directions, not astrophysical position angles or fitted warp parameters.",
            "Adjacent-difference error is a supplemental diagnostic, not an official benchmark metric; its denominator is the supplied video's 11 frame differences.",
            "The source defaults to a four-parameter affine warp without translation, despite the approach card's six-parameter description. Theta, covariance and optimization traces are not standalone released arrays.",
            "Saved results are historical, not proof that the syntax-invalid pinned main.py can regenerate them. One synthetic video does not establish causal or population-level superiority.",
            "The alternative dynamic_imaging_with_ehtim notebook is a separate setup with no saved outputs and different metric normalization; its parameters must not be mixed into this 30x30 StarWarps bundle.",
            "Root MIT license identifies the release; algorithm source says it was extracted from ehtim, whose upstream provenance and license need separate treatment before redistributing that code. The task PDF is inventoried only.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(json_safe(report), indent=2, allow_nan=False) + "\n")
    np.savez_compressed(out / "derived.npz", truth_forward_vis=np.array(predicted))
    print(
        json.dumps(
            {
                "verified_sources": len(sources),
                "verified_assets": len(assets),
                "native": {k: v["average"] for k, v in native.items()},
                "generic_starwarps": generic["starwarps"],
                "historical_recipe": recipe,
                "audit_sha256": sha(out / "audit.json"),
            },
            indent=2,
        )
    )


def numpy_real_stack(a):
    return np.concatenate((a.real, a.imag), axis=0)


if __name__ == "__main__":
    main()
