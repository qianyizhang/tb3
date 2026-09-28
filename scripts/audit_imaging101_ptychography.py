"""Audit pinned ptychography arrays, staging, forward operators and saved scores.

No agent, reconstruction iterations, dataset generation, install or Docker run.
The published 32-pixel operator fixture and selected initial-state projections
are diagnostics; they do not produce the released reconstruction.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import logging
import shutil
from pathlib import Path
from types import SimpleNamespace

import h5py
import numpy as np

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


def native_phase_metrics(obj, gt):
    # Exact arithmetic and dtype from the phase-metric block in pinned main.py.
    gt_ph = np.angle(gt)
    obj_ph = np.angle(obj)
    obj_ph -= obj_ph.mean()
    gt_ph_c = gt_ph - gt_ph.mean()
    return {
        "ncc": float(
            np.sum(obj_ph * gt_ph_c) / (np.linalg.norm(obj_ph) * np.linalg.norm(gt_ph_c) + 1e-10)
        ),
        "nrmse": float(
            np.sqrt(np.mean((obj_ph - gt_ph_c) ** 2)) / (gt_ph_c.max() - gt_ph_c.min() + 1e-10)
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.sources, args.output
    out.mkdir(parents=True, exist_ok=False)
    task = source / "tasks/conventional_ptychography"
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    verified = []
    for name in ["fetch-receipt.json", "shared-source-receipt.json"]:
        receipt = json.loads((source / name).read_text())
        assert receipt["revision"] == COMMIT
        for row in receipt["files"]:
            p = source / row["path"]
            data = p.read_bytes()
            assert row["status"] == "verified" and sha(p) == row["sha256"]
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == row["git_blob_sha1"]
            )
            verified.append(row["path"])
    downloads = json.loads((source / "asset-fetch-receipt.json").read_text())
    retry = json.loads((source / "fixture-alternate-receipt.json").read_text())[0]
    downloads = [retry if row["path"] == retry["path"] else row for row in downloads]
    for row in downloads:
        p = source / row["path"]
        assert (
            row["status"] == "verified"
            and sha(p) == row["sha256"]
            and p.stat().st_size == row["size"]
        )

    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    gt = np.load(task / "data/ground_truth.npz", allow_pickle=False)["object"]
    gt_npy = np.load(task / "data/ground_truth.npy", allow_pickle=False)
    positions = np.load(task / "data/positions.npy", allow_pickle=False)
    meta = json.loads((task / "data/meta_data.json").read_text())
    historical = json.loads((task / "evaluation/reference_outputs/metrics.json").read_text())
    assert np.array_equal(gt, gt_npy) and np.all(np.abs(gt) == 1)
    with h5py.File(task / "data/simu.hdf5") as hf:
        assert np.array_equal(hf["ptychogram"][()], raw["ptychogram"])
        assert np.array_equal(hf["encoder"][()], raw["encoder"])
        hdf_metadata = {
            k: np.asarray(hf[k][()]).tolist() for k in hf if k not in ["ptychogram", "encoder"]
        }
    with h5py.File(task / "evaluation/reference_outputs/recon.hdf5") as hf:
        saved = np.squeeze(hf["object"][()])
        probe = np.squeeze(hf["probe"][()])
        errors = hf["error"][()]
        saved_schema = {k: stats(hf[k][()]) for k in hf}
    assert saved.shape == gt.shape == (542, 542)
    assert raw["ptychogram"].shape == (100, 128, 128) and len(errors) == 350
    assert errors[-1] == historical["final_error"]

    ns = {
        "np": np,
        "Path": Path,
        "json": json,
        "PtyData": SimpleNamespace,
        "PtyState": SimpleNamespace,
    }
    selections = {"utils.py": selected(task / "src/utils.py", ["fft2c", "ifft2c", "circ"], ns)}
    selections["physics_model.py"] = selected(
        task / "src/physics_model.py",
        [
            "get_object_patch",
            "compute_exit_wave",
            "fraunhofer_propagate",
            "compute_detector_intensity",
        ],
        ns,
    )
    selections["preprocessing.py"] = selected(
        task / "src/preprocessing.py", ["load_experimental_data", "setup_reconstruction"], ns
    )
    data = ns["load_experimental_data"](task / "data")
    state = ns["setup_reconstruction"](data, seed=42)
    assert np.array_equal(state.positions, positions)
    assert state.dxo == meta["dxp_m"]
    coverage = np.zeros(gt.shape, dtype=np.uint16)
    for y, x in positions:
        coverage[y : y + 128, x : x + 128] += 1
    bars = np.angle(gt) > 1

    fixture = np.load(task / "evaluation/fixtures/basic_pipeline.npz", allow_pickle=False)
    rng = np.random.default_rng(42)
    obj = rng.standard_normal((64, 64)) + 1j * rng.standard_normal((64, 64))
    p = rng.standard_normal((32, 32)) + 1j * rng.standard_normal((32, 32))
    patch = ns["get_object_patch"](obj, (10, 15), 32)
    esw = ns["compute_exit_wave"](p, patch)
    det = ns["fraunhofer_propagate"](esw)
    intensity = ns["compute_detector_intensity"](det)
    field = rng.standard_normal((32, 32)) + 1j * rng.standard_normal((32, 32))
    x, y = np.meshgrid(np.arange(32) - 16, np.arange(32) - 16)
    values = {
        "object_patch": patch,
        "exit_wave": esw,
        "detector_field": det,
        "intensity": intensity,
        "intensity_fm": intensity,
        "fft_roundtrip": ns["ifft2c"](ns["fft2c"](field)),
        "circ_mask": ns["circ"](x.astype(float), y.astype(float), 32 * 0.8),
    }
    fixture_checks = {}
    for key, value in values.items():
        fixture_checks[key] = float(
            np.max(np.abs(value.astype(complex) - fixture[key].astype(complex)))
        )
        assert np.allclose(value, fixture[key], atol=1e-11, rtol=1e-11)

    diagnostics = []
    for j in [0, 49, 99]:
        y, x = positions[j]
        patch = state.object[y : y + 128, x : x + 128]
        wave = ns["fft2c"](patch * state.probe)
        estimated = np.abs(wave) ** 2
        measured = raw["ptychogram"][j].astype(np.float64)
        projected_wave = wave * np.sqrt(measured / (estimated + 1e-10))
        projected = np.abs(projected_wave) ** 2
        delta = ns["ifft2c"](projected_wave) - patch * state.probe
        np.savez(
            out / f"projection-{j}.npz",
            estimated=estimated,
            measured=measured,
            projected=projected,
            delta=delta,
        )
        diagnostics.append(
            {
                "scan": j,
                "position_rc": positions[j].tolist(),
                "encoder_m": raw["encoder"][j].astype(float).tolist(),
                "before_relative_l1": float(np.abs(measured - estimated).sum() / measured.sum()),
                "after_relative_l1": float(np.abs(measured - projected).sum() / measured.sum()),
                "zero_estimated_pixels": int((estimated == 0).sum()),
                "note": "One intensity projection from source initialization; no object or probe update.",
            }
        )

    harness = source / "evaluation_harness"
    staging_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("ptychography-audit")}
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
            exec=lambda command, requested=commands: requested.append(command),
        )
        visible = staging_ns["_get_visible_paths"](runner)
        staging_ns["start"](runner, visible)
        for name in ["ground_truth.npy", "ground_truth.npz"]:
            assert sha(dest / "data" / name) == sha(task / "data" / name)
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "files": sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()),
            "both_ground_truth_files_copied": True,
            "commands_intercepted": commands,
        }

    spec = importlib.util.spec_from_file_location(
        "ptychography_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    reference, reference_path = ref.load_reference_array(task, target_shape=gt.shape)
    assert reference_path == task / "data/ground_truth.npy" and np.all(reference == 1)
    generic, phase = {}, {}
    controls = {
        "saved-object": saved,
        "truth-copy": gt,
        "phase-erased-unit": np.ones_like(gt),
        "conjugated-truth": gt.conj(),
    }
    for name, array in controls.items():
        dest = out / "scoring" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", array)
        generic[name] = ref.score_reconstruction(task, dest.parent)
        phase[name] = native_phase_metrics(array, gt)
    assert generic["truth-copy"] == generic["phase-erased-unit"] == generic["conjugated-truth"]
    assert generic["truth-copy"]["ncc"] == 1 and generic["truth-copy"]["mse"] == 0
    assert np.isinf(generic["truth-copy"]["nrmse"]) and generic["truth-copy"]["passed"] is None
    assert round(phase["saved-object"]["ncc"], 4) == historical["phase_ncc"]
    assert round(phase["saved-object"]["nrmse"], 4) == historical["phase_nrmse"]

    final_sum_l1 = 0.0
    final_amplitude_numerator = 0.0
    for j, pos in enumerate(positions):
        y, x = pos
        pred = np.abs(ns["fft2c"](saved[y : y + 128, x : x + 128] * probe)) ** 2
        meas = raw["ptychogram"][j].astype(float)
        final_sum_l1 += float(np.abs(meas - pred).sum() / data.energy_at_pos[j])
        final_amplitude_numerator += float(((np.sqrt(meas) - np.sqrt(pred)) ** 2).sum())
    final_amplitude = final_amplitude_numerator / float(raw["ptychogram"].sum(dtype=float))
    np.save(out / "coverage.npy", coverage)
    report = {
        "schema": 1,
        "entry_id": "imaging101-conventional-ptychography",
        "source_commit": COMMIT,
        "verified_source_files": verified,
        "verified_asset_count": len(downloads),
        "raw": {k: stats(raw[k]) for k in raw.files},
        "truth": stats(gt),
        "saved": saved_schema,
        "metadata": meta,
        "hdf_metadata": hdf_metadata,
        "truth_npy_npz_equal": True,
        "raw_npz_hdf_equal": True,
        "source_positions_match": True,
        "pixel_size_um": state.dxo * 1e6,
        "patch_coverage": {
            "pixels": int((coverage > 0).sum()),
            "total_pixels": int(coverage.size),
            "max_overlap": int(coverage.max()),
            "phase_bar_pixels": int(bars.sum()),
            "covered_bar_pixels": int((bars & (coverage > 0)).sum()),
            "note": "Rectangular 128x128 extraction windows; not an illumination support or accuracy mask.",
        },
        "published_fixture_max_abs_errors": fixture_checks,
        "selected_projection_diagnostics": diagnostics,
        "staging": staging,
        "generic_reference": str(reference_path.relative_to(source)),
        "generic_scoring": generic,
        "native_phase_controls": phase,
        "historical_metrics": historical,
        "saved_forward_diagnostics": {
            "sum_relative_intensity_l1": final_sum_l1,
            "global_squared_amplitude_error": final_amplitude,
            "stored_last_iteration_error": float(errors[-1]),
            "note": "Fresh forward-only diagnostic of final saved arrays. Stored history accumulates residuals before each sequential update, then constraints; it is not this final-state evaluation.",
        },
        "source_function_selections": selections,
        "execution_scope": {
            "agent": False,
            "inverse_iterations": 0,
            "dataset_generation": False,
            "runtime_install": False,
            "docker": False,
            "published_operator_fixture": True,
            "forward_and_projection_diagnostics": True,
            "staging_file_copy": True,
            "saved_scoring_replay": True,
        },
        "limits": [
            "One synthetic source case; saved results, not a fresh reconstruction.",
            "Released L1-L3 packets expose both truth files.",
            "Generic scoring erases phase; constant truth magnitude gives infinite NRMSE even for exact truth.",
            "No pass thresholds shipped; no benchmark pass is established.",
            "Approach text says periodic momentum and amplitude error; solver code uses a 5 percent random trigger and sum of relative intensity L1 residuals.",
            "Generator source adds a Poisson draw to its expectation, rather than replacing it; full generator was not executed.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(safe(report), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            safe(
                {
                    "output": str(out),
                    "phase": phase,
                    "generic": generic,
                    "coverage": report["patch_coverage"],
                    "forward": report["saved_forward_diagnostics"],
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
