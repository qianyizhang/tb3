"""Audit pinned NLOS inputs, staging, saved-output scoring and small operators.

No agent, full-size inverse reconstruction, install, Docker or historical write.
The 16x8x8 solver fixture is a unit diagnostic, not a new dataset reconstruction.
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

import numpy as np

COMMIT = "dc2f668939b21e8312e22529615def610f8611df"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def schema(archive):
    return {
        key: {"shape": list(archive[key].shape), "dtype": str(archive[key].dtype)}
        for key in archive.files
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source, out = args.sources, args.output
    task = source / "tasks/confocal-nlos-fk"
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    verified = []
    for receipt in ["fetch-receipt.json", "shared-source-receipt.json"]:
        rows = json.loads((source / receipt).read_text())
        assert rows["revision"] == COMMIT
        for row in rows["files"]:
            p = source / row["path"]
            if row["status"] != "verified" or not p.exists():
                continue
            data = p.read_bytes()
            assert sha(p) == row["sha256"]
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == row["git_blob_sha1"]
            )
            verified.append(row["path"])
    assets = json.loads((source / "asset-fetch-receipt.json").read_text())
    retry = json.loads((source / "raw-alternate-receipt.json").read_text())
    assert retry["status"] == "verified"
    assets = [retry if r["path"] == retry["path"] else r for r in assets]
    for row in assets:
        assert row["status"] == "verified"
        assert (source / row["path"]).stat().st_size == row["size"]
        assert sha(source / row["path"]) == row["sha256"]
    for row in json.loads((source / "context-fetch-receipt.json").read_text()):
        assert row["status"] == "verified-fetch" and sha(source / row["path"]) == row["sha256"]

    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    baseline = np.load(task / "data/baseline_reference.npz", allow_pickle=False)
    saved = np.load(task / "evaluation/reference_outputs/reconstruction.npz", allow_pickle=False)
    fk = np.load(task / "evaluation/reference_outputs/fk_reference.npy", allow_pickle=False)
    vol = saved["fk"]
    assert vol.shape == fk.shape == baseline["reconstruction"][0].shape == (512, 128, 128)
    assert np.array_equal(vol, fk) and np.array_equal(vol, baseline["reconstruction"][0])
    meta = json.loads((task / "data/meta_data").read_text())
    wall, dt = float(raw["wall_size"]), float(raw["bin_resolution"])
    assert wall == meta["wall_size"] == 2.0 and dt == meta["bin_resolution"] == 3.2e-11
    assert raw["meas"].shape == (128, 128, 2048) and raw["tofgrid"].dtype == np.float64

    # Exact selected file-seeding functions; no subprocess commands are executed.
    harness = source / "evaluation_harness"
    ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("nlos-audit")}
    selections = {
        "runner.py": selected(harness / "runner.py", ["_get_visible_paths"], ns, "BenchmarkRunner"),
        "local_runner.py": selected(harness / "local_runner.py", ["start"], ns, "LocalRunner"),
    }
    staging = {}
    for level in ["L1", "L2", "L3"]:
        dest = out / level
        dest.mkdir()
        commands = []
        ns["tempfile"] = SimpleNamespace(
            mkdtemp=lambda directory=dest, **_: str(directory.resolve())
        )
        obj = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(mode="end_to_end", level=level)),
            task_dir=task.resolve(),
            exec=lambda command, requested=commands: requested.append(command),
        )
        visible = ns["_get_visible_paths"](obj)
        ns["start"](obj, visible)
        assert sha(dest / "data/baseline_reference.npz") == sha(
            task / "data/baseline_reference.npz"
        )
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "files": sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()),
            "baseline_copied": True,
            "commands_intercepted": commands,
        }

    ref = load_module(harness / "reference_scoring.py", "nlos_reference_scoring")
    loaded_ref, ref_path = ref.load_reference_array(task, target_shape=vol.shape)
    assert ref_path == task / "evaluation/reference_outputs/reconstruction.npz"
    assert np.array_equal(loaded_ref, vol)
    metrics = {}
    for name, array in [
        ("saved-output", vol),
        ("baseline-copy-control", baseline["reconstruction"]),
        ("half-amplitude-control", vol * 0.5),
        ("front-projection-control", vol.max(axis=0)),
    ]:
        target = out / "scoring" / name
        (target / "output").mkdir(parents=True)
        np.save(target / "output/reconstruction.npy", array)
        metrics[name] = ref.score_reconstruction(task, target)
    assert metrics["saved-output"]["mse"] == metrics["baseline-copy-control"]["mse"] == 0.0
    assert metrics["saved-output"]["passed"] is None
    assert metrics["half-amplitude-control"]["ncc"] == 1.0
    assert metrics["half-amplitude-control"]["nrmse"] > 0
    assert "error" in metrics["front-projection-control"]
    native_ns = {"np": np}
    selections["main.py"] = selected(task / "main.py", ["ncc", "nrmse", "normalise"], native_ns)
    vnorm = native_ns["normalise"](vol.astype(np.float64))
    native = {"ncc": native_ns["ncc"](vnorm, vnorm), "nrmse": native_ns["nrmse"](vnorm, vnorm)}
    native_half = {
        "ncc": native_ns["ncc"](native_ns["normalise"](vol.astype(np.float64) * 0.5), vnorm),
        "nrmse": native_ns["nrmse"](native_ns["normalise"](vol.astype(np.float64) * 0.5), vnorm),
    }

    prep = load_module(task / "src/preprocessing.py", "nlos_preprocessing")
    solver = load_module(task / "src/solvers.py", "nlos_solver")
    fixture_dir = task / "evaluation/fixtures"
    pf = np.load(fixture_dir / "preprocess.npz", allow_pickle=False)
    processed = prep.preprocess_measurements(
        pf["input_meas_store"], None, float(pf["param_bin_res"]), int(pf["param_crop"])
    )
    sf = np.load(fixture_dir / "solvers.npz", allow_pickle=False)
    solved = solver.fk_reconstruction(
        sf["input_meas"], float(sf["param_wall_size"]), float(sf["param_bin_res"])
    )
    fixture_errors = {
        "preprocess_max_abs": float(np.max(np.abs(processed - pf["output_processed"]))),
        "solver_max_abs": float(np.max(np.abs(solved - sf["output_fk"]))),
    }
    assert fixture_errors["preprocess_max_abs"] < 1e-12
    assert np.allclose(solved, sf["output_fk"], rtol=1e-12, atol=1e-10)

    # Three actual histograms, exact calibration/roll/crop; never full-size migration.
    meas, tof = raw["meas"], raw["tofgrid"]
    points = [(32, 32), (64, 64), (96, 96)]
    histograms = []
    for y, x in points:
        shift = -int(np.floor(tof[y, x] / (dt * 1e12)))
        aligned = prep.preprocess_measurements(
            meas[y : y + 1, x : x + 1], tof[y : y + 1, x : x + 1], dt, 512
        )[:, 0, 0]
        assert np.array_equal(aligned, np.roll(meas[y, x], shift)[:512])
        histograms.append(
            {
                "y": y,
                "x": x,
                "tof_ps": float(tof[y, x]),
                "shift_bins": shift,
                "raw": meas[y, x].tolist(),
                "aligned": aligned.tolist(),
            }
        )
    (out / "histograms.json").write_text(json.dumps(histograms) + "\n")
    z, y, x = prep.volume_axes(512, 128, 128, wall, dt)
    assert z[-1] == 2.4576
    record = {
        "source_commit": COMMIT,
        "verified_git_files": sorted(set(verified)),
        "verified_assets": assets,
        "selections": selections,
        "staging": staging,
        "array_schema": {"raw": schema(raw), "baseline": schema(baseline), "saved": schema(saved)},
        "metadata": meta,
        "identical_saved_arrays": {
            "equal": True,
            "array_sha256": hashlib.sha256(vol.tobytes()).hexdigest(),
            "shape": list(vol.shape),
            "files": [
                "data/baseline_reference.npz:reconstruction[0]",
                "evaluation/reference_outputs/reconstruction.npz:fk",
                "evaluation/reference_outputs/fk_reference.npy",
            ],
        },
        "reference_selected": str(ref_path.relative_to(task)),
        "generic_scoring": metrics,
        "native_saved_output_replay": native,
        "native_half_amplitude_control": native_half,
        "retained_metrics": json.loads(
            (task / "evaluation/reference_outputs/metrics.json").read_text()
        ),
        "operator_fixtures": {
            "shape": [16, 8, 8],
            **fixture_errors,
            "scope": "Published toy operator arrays only; not the 512x128x128 inverse problem.",
        },
        "histograms": {
            "path": "histograms.json",
            "sha256": sha(out / "histograms.json"),
            "points": [
                {k: v for k, v in r.items() if k not in ["raw", "aligned"]} for r in histograms
            ],
        },
        "axes": {
            "z_min_max_m": [float(z[0]), float(z[-1])],
            "x_min_max_m": [float(x[0]), float(x[-1])],
            "y_min_max_m": [float(y[0]), float(y[-1])],
            "z_step_m": float(z[1] - z[0]),
            "one_bin_roundtrip_depth_m": 3e8 * dt / 2,
            "convention": "Source volume_axes uses inclusive linspace endpoints; the forward model uses half-bin voxel centers. These are distinct conventions.",
        },
        "saved_peak": {
            "zyx_index": list(map(int, np.unravel_index(vol.argmax(), vol.shape))),
            "value": float(vol.max()),
            "note": "Maximum is in last depth plane; do not infer independent object-depth accuracy.",
        },
        "limits": [
            "No model, agent, full-size inverse reconstruction, Docker, runtime install or historical rewrite.",
            "Baseline copy is an oracle/no-op control; same-array scores are not fresh task execution or independent ground truth.",
            "Original upstream MATLAB swaps lateral axes and zeros the last eleven depth planes before display/output; the released Python solver does not. Original-author byte equivalence is not established.",
            "Retained metrics lack boundary keys. Source main.py could create them on execution, but was not run and no pass is claimed.",
            "Metadata raw depth range 9.8304 m is reduced to source displayed 2.4576 m after 512-bin crop.",
            "Full data use follows original authors' academic/non-commercial license; benchmark MIT declaration does not replace it.",
        ],
        "all_assertions_passed": True,
    }
    (out / "audit.json").write_text(json.dumps(safe(record), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            safe(
                {
                    "audit": str(out / "audit.json"),
                    "metrics": metrics,
                    "fixture_errors": fixture_errors,
                    "histograms": record["histograms"]["points"],
                }
            )
        )
    )


if __name__ == "__main__":
    main()
