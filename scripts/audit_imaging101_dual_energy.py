"""Audit pinned dual-energy CT arrays, native geometry, staging and scoring.

Replays saved intermediates and forward operators. Does not execute material
optimization, generate noisy data, launch an agent, install packages or use Docker.
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
import skimage
from skimage.transform import iradon, radon

COMMIT = "dc2f668939b21e8312e22529615def610f8611df"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_hash(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


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
    v = np.abs(array) if np.iscomplexobj(array) else array
    return {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "range_kind": "magnitude" if np.iscomplexobj(array) else "value",
        "min": float(v.min()),
        "max": float(v.max()),
        "nonfinite": int((~np.isfinite(array)).sum()),
        "array_bytes_sha256": array_hash(array),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.sources, args.output
    out.mkdir(parents=True, exist_ok=False)
    task = source / "tasks/ct_dual_energy"
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    alternates = {
        r["path"]: r for r in json.loads((source / "source-alternate-receipt.json").read_text())
    }
    verified = []
    for name in ["fetch-receipt.json", "shared-source-receipt.json"]:
        receipt = json.loads((source / name).read_text())
        assert receipt["revision"] == COMMIT
        for original in receipt["files"]:
            row = alternates.get(original["path"], original)
            p = source / row["path"]
            data = p.read_bytes()
            assert row["status"] == "verified" and sha(p) == row["sha256"]
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == row["git_blob_sha1"]
            )
            verified.append(row["path"])
    downloads = json.loads((source / "asset-fetch-receipt.json").read_text())
    unavailable = []
    acquired = []
    for row in downloads:
        if row["status"] != "verified":
            unavailable.append(row["path"])
            continue
        p = source / row["path"]
        assert sha(p) == row["sha256"] and p.stat().st_size == row["size"]
        acquired.append(row["path"])
    assert unavailable == ["tasks/ct_dual_energy/evaluation/fixtures/solvers_decompose.npz"]
    assert len(acquired) == 10
    assert (
        json.loads((source / "hf-revision.json").read_text())["sha"]
        == "a9de559b54849a25988a8a0d8a5e869063a5a7a3"
    )
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    truth = np.load(task / "data/ground_truth.npz", allow_pickle=False)
    saved = np.load(
        task / "evaluation/reference_outputs/reference_reconstruction.npz", allow_pickle=False
    )
    meta = json.loads((task / "data/meta_data.json").read_text())
    ns = {"np": np, "json": json, "os": os, "radon": radon, "iradon": iradon}
    selections = {}
    for file, names in [
        ("preprocessing.py", ["load_raw_data", "load_ground_truth", "load_metadata"]),
        (
            "physics_model.py",
            ["get_spectra", "radon_transform", "fbp_reconstruct", "polychromatic_forward"],
        ),
        (
            "generate_data.py",
            ["_nist_tissue_mac", "_nist_bone_mac", "get_attenuation_coefficients"],
        ),
        ("visualization.py", ["compute_ncc", "compute_nrmse", "compute_metrics"]),
    ]:
        selections[file] = selected(task / "src" / file, names, ns)
    counts, spectra, mus, energies, theta = ns["load_raw_data"](task / "data")
    tm, bm, ts, bs = ns["load_ground_truth"](task / "data")
    st, sb, sts, sbs = (
        saved[k][0] for k in ["tissue_map", "bone_map", "tissue_sinogram", "bone_sinogram"]
    )
    assert counts.shape == (2, 128, 180) and mus.shape == spectra.shape == (2, 131)
    assert np.array_equal(theta, np.arange(180)) and np.array_equal(energies, np.arange(20, 151))
    assert np.array_equal(spectra, ns["get_spectra"](energies))
    assert np.array_equal(mus, ns["get_attenuation_coefficients"](energies))
    assert meta["pixel_size_cm"] == 0.1
    fixtures = {}
    fixture_dir = task / "evaluation/fixtures"
    for name, function, inputs, output in [
        ("physics_model_spectra", "get_spectra", ["input_energies"], "output_spectra"),
        (
            "physics_model_attenuation",
            "get_attenuation_coefficients",
            ["input_energies"],
            "output_mus",
        ),
        (
            "physics_model_forward",
            "polychromatic_forward",
            ["input_material_sinograms", "input_spectra", "input_mus"],
            "output_counts",
        ),
        (
            "physics_model_radon",
            "radon_transform",
            ["input_image", "input_theta"],
            "output_sinogram",
        ),
    ]:
        f = np.load(fixture_dir / (name + ".npz"), allow_pickle=False)
        result = ns[function](*(f[k] for k in inputs))
        fixtures[name] = float(np.max(np.abs(result - f[output])))
        assert np.allclose(result, f[output], rtol=1e-12, atol=1e-12)
    f = np.load(fixture_dir / "visualization_metrics.npz", allow_pickle=False)
    for key in ["ncc", "nrmse"]:
        fixtures["visualization_" + key] = abs(
            ns["compute_" + key](f["input_a"], f["input_b"]) - float(f["output_" + key])
        )
        assert fixtures["visualization_" + key] < 1e-14
    f = np.load(fixture_dir / "generate_data_phantom.npz", allow_pickle=False)
    assert np.array_equal(tm, f["output_tissue"]) and np.array_equal(bm, f["output_bone"])
    # Exact saved-state replay, not a new material-decomposition run.
    replay = {}
    for name, gtmap, gtsino, estmap, estsino in [
        ("tissue", tm, ts, st, sts),
        ("bone", bm, bs, sb, sbs),
    ]:
        forward = ns["radon_transform"](gtmap, theta) * meta["pixel_size_cm"]
        back = ns["fbp_reconstruct"](estsino / meta["pixel_size_cm"], theta, output_size=128)
        replay[name] = {
            "truth_radon_max_abs_error": float(np.max(np.abs(forward - gtsino))),
            "saved_fbp_max_abs_error": float(np.max(np.abs(np.maximum(back, 0) - estmap))),
            "negative_fbp_pixels_before_clip": int((back < 0).sum()),
        }
        assert replay[name]["truth_radon_max_abs_error"] < 1e-10
        assert replay[name]["saved_fbp_max_abs_error"] < 1e-10
    body = (tm + bm) > 0.01
    native = {}
    controls = {
        "saved": (st, sb),
        "truth-copy": (tm, bm),
        "erased-bone": (tm, np.zeros_like(bm)),
        "swapped-materials": (bm, tm),
        "half-density": (0.5 * tm, 0.5 * bm),
        "outside-body-added": (st + 10 * (~body), sb + 10 * (~body)),
    }
    for name, (t, b) in controls.items():
        native[name] = ns["compute_metrics"](t, tm, b, bm)
    assert native["outside-body-added"] == native["saved"]
    assert native["truth-copy"]["mean_ncc"] == 1 and native["truth-copy"]["mean_nrmse"] == 0
    assert native["erased-bone"]["mean_ncc"] == 0.5
    expected = ns["polychromatic_forward"](np.stack([ts, bs]), spectra, mus)
    predicted = ns["polychromatic_forward"](np.stack([sts, sbs]), spectra, mus)
    np.savez(
        out / "forward-replay.npz", truth_expected_counts=expected, saved_expected_counts=predicted
    )
    count_checks = {}
    for j, name in enumerate(["low", "high"]):
        delta = counts[j] - expected[j]
        count_checks[name] = {
            "open_beam_photons": float(spectra[j].sum()),
            "expected_range": [float(expected[j].min()), float(expected[j].max())],
            "observed_range": [float(counts[j].min()), float(counts[j].max())],
            "poisson_standardized_mean": float(np.mean(delta / np.sqrt(expected[j]))),
            "poisson_standardized_rms": float(np.sqrt(np.mean(delta**2 / expected[j]))),
            "saved_forward_relative_l1": float(
                np.abs(predicted[j] - counts[j]).sum() / counts[j].sum()
            ),
        }
    ray_diagnostics = []
    for detector, angle in [(64, 0), (16, 90), (41, 45)]:
        a = np.array([sts[detector, angle], sbs[detector, angle]])
        transmission = np.exp(-a @ mus)
        contributions = spectra * transmission
        nu = contributions.sum(axis=1)
        jac = -np.einsum("se,ke,e->sk", spectra, mus, transmission)
        numerical = np.empty((2, 2))
        h = 1e-5
        for k in range(2):
            step = np.zeros(2)
            step[k] = h
            numerical[:, k] = (
                spectra @ np.exp(-(a + step) @ mus) - spectra @ np.exp(-(a - step) @ mus)
            ) / (2 * h)
        assert np.allclose(jac, numerical, rtol=1e-8, atol=1e-5)
        fisher = (jac.T / nu) @ jac
        ray_diagnostics.append(
            {
                "detector_bin": detector,
                "angle_degrees": float(theta[angle]),
                "saved_material_integrals_g_cm2": a.tolist(),
                "observed_counts": counts[:, detector, angle].tolist(),
                "saved_predicted_counts": nu.tolist(),
                "transmission_by_energy": transmission.tolist(),
                "count_contributions_by_energy": contributions.tolist(),
                "count_jacobian": jac.tolist(),
                "finite_difference_max_abs_error": float(np.max(np.abs(jac - numerical))),
                "poisson_fisher_condition_number": float(np.linalg.cond(fisher)),
                "note": "Forward sensitivity at a saved ray; no Newton update or new solution.",
            }
        )
    # Reproduce the actual local file-seeding methods with installation intercepted.
    harness = source / "evaluation_harness"
    staging_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("dual-energy-audit")}
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
        "dual_energy_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)

    # Bind only this relative source import, without importing the harness package.
    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=ref)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("dual-energy-audit"),
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
        "saved-tissue": st,
        "saved-bone": sb,
        "truth-tissue-only": tm,
        "truth-bone-only": bm,
        "two-truth-maps": np.stack([tm, bm]),
        "truth-bone-sinogram": bs,
        "truth-tissue-sinogram": ts,
        "zero-map": np.zeros_like(tm),
        "outside-body-added": st + 10 * (~body),
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
            matches = [
                k
                for k in truth.files
                if truth[k][0].shape == reference.shape and np.array_equal(truth[k][0], reference)
            ]
            references[name] = {
                "path": str(p.relative_to(source)),
                "keys_with_identical_values": matches,
                "shape": list(reference.shape),
            }
    assert references["saved-tissue"]["keys_with_identical_values"] == ["tissue_map"]
    assert references["truth-bone-sinogram"]["keys_with_identical_values"] == ["bone_sinogram"]
    assert generic["truth-tissue-only"]["ncc"] == generic["truth-bone-sinogram"]["ncc"] == 1
    assert generic["truth-tissue-only"]["mse"] == generic["truth-bone-sinogram"]["mse"] == 0
    assert "error" in generic["two-truth-maps"]
    assert all(v.get("passed") is None for v in generic.values())
    dest = out / "scoring/native-npz/output"
    dest.mkdir(parents=True)
    np.savez(
        dest / "reconstructed_maps.npz",
        tissue_map=st,
        bone_map=sb,
        tissue_sinogram=sts,
        bone_sinogram=sbs,
    )
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
    nist = json.loads((source / "nist-selected-values.json").read_text())
    indices = [int(e - 20) for e in nist["energy_keV"]]
    official = np.array(nist["mass_attenuation_cm2_g"])
    released = mus[:, indices]
    calibration = {
        "nist_source": nist,
        "released_values": released.tolist(),
        "relative_difference": ((released - official) / official).tolist(),
        "note": "Source tables are approximate; released values are retained, not replaced by NIST.",
    }
    report = {
        "schema": 1,
        "entry_id": "imaging101-ct-dual-energy",
        "source_commit": COMMIT,
        "verified_source_files": verified,
        "verified_assets": acquired,
        "unavailable_assets": unavailable,
        "raw": {k: stats(raw[k]) for k in raw.files},
        "truth": {k: stats(truth[k]) for k in truth.files},
        "saved": {k: stats(saved[k]) for k in saved.files},
        "metadata": meta,
        "skimage_version": skimage.__version__,
        "calibration_matches_source": True,
        "phantom_fixture_equals_truth": True,
        "fixture_max_abs_errors": fixtures,
        "saved_state_replay": replay,
        "body_mask_pixels": int(body.sum()),
        "total_pixels": int(body.size),
        "native_metrics": native,
        "count_checks": count_checks,
        "ray_diagnostics": ray_diagnostics,
        "staging": staging,
        "generic_reference_selection": references,
        "generic_scoring": generic,
        "metrics_file_present": (task / "evaluation/metrics.json").exists(),
        "calibration_comparison": calibration,
        "source_function_selections": selections,
        "execution_scope": {
            "agent": False,
            "material_optimization_iterations": 0,
            "dataset_generation": False,
            "runtime_install": False,
            "docker": False,
            "forward_fixture": True,
            "saved_fbp_replay": True,
            "staging_file_copy": True,
            "saved_scoring_replay": True,
        },
        "limits": [
            "One synthetic parallel-beam phantom; no acquired scan or clinical accuracy claim.",
            "Released L1-L3 staging exposes both material truth maps and sinograms.",
            "Generic evaluation selects tissue for map-shaped arrays and bone for sinogram-shaped arrays; stacked materials fail reference matching.",
            "Native two-material body-masked metrics and generic single-array whole-image metrics are different.",
            "No metrics.json or pass thresholds shipped; no benchmark pass established.",
            "Tiny inverse-solver fixture was unavailable after bounded TLS/timeouts; no material optimizer was executed.",
            "Original cited simulator uses different geometry and calibration; byte-equivalent upstream behavior is not claimed.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(safe(report), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            safe(
                {
                    k: report[k]
                    for k in [
                        "native_metrics",
                        "generic_scoring",
                        "fixture_max_abs_errors",
                        "saved_state_replay",
                        "count_checks",
                    ]
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
