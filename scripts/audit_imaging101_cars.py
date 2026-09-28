"""Audit pinned CARS staging, numerical arrays and saved-output scoring.

No model, optimization, environment install, Docker launch or historical rewrite.
Selected upstream functions run on retained arrays and explicit diagnostic files.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import logging
import shutil
import warnings
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
    tree = ast.parse(path.read_text())
    body = tree.body
    if class_name:
        body = next(n for n in body if isinstance(n, ast.ClassDef) and n.name == class_name).body
    nodes = [n for n in body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return [{"name": n.name, "lines": [n.lineno, n.end_lineno]} for n in nodes]


def json_safe(value):
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return str(value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.sources
    task = source / "tasks/cars_spectroscopy"
    fetched = json.loads((source / "fetch-receipt.json").read_text())
    tree = json.loads((source / "github-tree.json").read_text())
    assert fetched["revision"] == tree["sha"] == COMMIT and not tree["truncated"]
    verified = [r for r in fetched["files"] if r["status"] == "verified"]
    for r in verified:
        data = (source / r["path"]).read_bytes()
        assert sha(source / r["path"]) == r["sha256"]
        assert (
            hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            == r["git_blob_sha1"]
        )
    assets = json.loads((source / "asset-fetch-receipt.json").read_text())
    for r in assets:
        if r["status"] == "verified":
            assert (source / r["path"]).stat().st_size == r["size"]
            assert sha(source / r["path"]) == r["sha256"]
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    gt = np.load(task / "data/ground_truth.npz", allow_pickle=False)
    saved = np.load(task / "evaluation/reference_outputs/reconstruction.npz", allow_pickle=False)
    y, nu, clean, fitted = (
        raw["measurements"][0],
        raw["nu_axis"][0],
        gt["spectrum"][0],
        saved["y_pred"][0],
    )
    assert y.shape == nu.shape == clean.shape == fitted.shape == (200,)
    assert np.allclose(nu, np.linspace(2280, 2330, 200))
    assert gt["temperature"].tolist() == [2400]

    # Execute only file seeding; record installation commands without running them.
    harness = source / "evaluation_harness"
    ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("cars-audit")}
    selections = {}
    selections["runner.py"] = selected(
        harness / "runner.py", ["_get_visible_paths"], ns, "BenchmarkRunner"
    )
    selections["local_runner.py"] = selected(
        harness / "local_runner.py", ["start"], ns, "LocalRunner"
    )
    seeds = {}
    for level in ["L1", "L2", "L3"]:
        out = args.output / level
        out.mkdir()
        requested = []
        ns["tempfile"] = SimpleNamespace(
            mkdtemp=lambda directory=out, **_: str(directory.resolve())
        )
        obj = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(mode="end_to_end", level=level)),
            task_dir=task.resolve(),
            exec=lambda command, commands=requested: commands.append(command),
        )
        visible = ns["_get_visible_paths"](obj)
        ns["start"](obj, visible)
        files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
        assert sha(out / "data/ground_truth.npz") == sha(task / "data/ground_truth.npz")
        assert not (out / "src").exists() and not (out / "evaluation").exists()
        assert (out / "plan/approach.md").exists() == (level in ["L2", "L3"])
        assert (out / "plan/design.md").exists() == (level == "L3")
        seeds[level] = {
            "visible_paths": visible,
            "copied_files": files,
            "ground_truth_copied": True,
            "installation_commands_intercepted": requested,
        }

    ref = load_module(harness / "reference_scoring.py", "cars_reference_scoring")
    vis = load_module(task / "src/visualization.py", "cars_metrics")
    native_ns = {
        "np": np,
        "Path": Path,
        "TASK_CONFIG": {"cars_spectroscopy": {"recon_files": ["reconstruction.npz"]}},
    }
    selections["task_scoring.py"] = selected(
        harness / "task_scoring.py",
        ["_recon_bases", "_find_recon", "_recipe_cars", "_check_pass"],
        native_ns,
    )
    fixtures = {}
    values = {
        "saved-fit": saved["y_pred"],
        "raw-no-op": raw["measurements"],
        "clean-reference-control": gt["spectrum"],
        "flattened-fit": fitted,
        "temperature-only": np.array([2391.5641794510043]),
    }
    for name, value in values.items():
        out = args.output / "scoring" / name
        (out / "output").mkdir(parents=True)
        np.save(out / "output/reconstruction.npy", value)
        generic = ref.score_reconstruction(task, out)
        fixtures[name] = {"shape": list(value.shape), "generic": generic}
    assert "error" in fixtures["flattened-fit"]["generic"]
    assert fixtures["clean-reference-control"]["generic"]["mse"] == 0.0
    assert "passed" not in fixtures["saved-fit"]["generic"]
    assert all("temperature_error_K" not in f["generic"] for f in fixtures.values())
    native = native_ns["_recipe_cars"](task, task / "evaluation/reference_outputs", vis)
    assert abs(native["temperature_error_K"] - 8.4358205489957) < 1e-9
    out = args.output / "scoring/fit-with-wrong-temperature"
    out.mkdir()
    np.savez(out / "reconstruction.npz", y_pred=saved["y_pred"], temperature_pred=np.array([300.0]))
    wrong_temperature = native_ns["_recipe_cars"](task, out, vis)
    assert wrong_temperature["ncc"] == native["ncc"]
    assert wrong_temperature["temperature_error_K"] == 2100.0
    assert native_ns["_check_pass"](native, {"ncc": (">=", "ncc_boundary")}, {}) is None

    # Four bounded forward evaluations, no optimizer and no generated data writes.
    forward = load_module(task / "src/physics_model.py", "cars_physics")
    meta = json.loads((task / "data/meta_data.json").read_text())
    params = {
        "nu": nu,
        "pressure": meta["pressure_bar"],
        "pump_lw": meta["pump_linewidth_cm-1"],
        "species": "N2",
        "x_mol": 0.79,
        "slit_params": [0.5, 2.0, 0, 0],
    }
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        proposals = {
            str(t): forward.forward_operator(dict(params, temperature=t))
            for t in [2000, 2400, 2800]
        }
        other_x = forward.forward_operator(dict(params, temperature=2400, x_mol=0.2))
    assert all(np.isfinite(value).all() for value in [*proposals.values(), other_x])
    reference_diff = float(np.max(np.abs(proposals["2400"] - clean)))
    mole_fraction_diff = float(np.max(np.abs(proposals["2400"] - other_x)))
    assert reference_diff < 1e-10 and mole_fraction_diff < 1e-12
    np.savez(args.output / "forward-proposals.npz", nu_axis=nu, **proposals, x_mol_02=other_x)
    record = {
        "source_commit": COMMIT,
        "source_files_verified": len(verified),
        "source_fetch_failures": [r for r in fetched["files"] if r["status"] != "verified"],
        "selections": selections,
        "staging": seeds,
        "array_schema": {
            name: {k: {"shape": list(z[k].shape), "dtype": str(z[k].dtype)} for k in z.files}
            for name, z in [("raw", raw), ("ground_truth", gt), ("saved_fit", saved)]
        },
        "generic_scoring": fixtures,
        "native_saved_output_replay": native,
        "native_wrong_temperature_control": wrong_temperature,
        "saved_temperature_K": float(saved["temperature_pred"][0]),
        "ground_truth_temperature_K": float(gt["temperature"][0]),
        "forward_diagnostic": {
            "warnings": sorted({str(w.message) for w in caught}),
            "all_outputs_finite": True,
            "temperatures_K": [2000, 2400, 2800],
            "fixed_x_mol": 0.79,
            "other_x_mol": 0.2,
            "same_temperature_max_difference": mole_fraction_diff,
            "ground_truth_max_difference": reference_diff,
            "file": "forward-proposals.npz",
            "sha256": sha(args.output / "forward-proposals.npz"),
        },
        "thresholds": "Neither pinned Git tree nor downloaded asset manifest contains cars_spectroscopy/evaluation/metrics.json; do not regenerate it or infer a pass.",
        "limits": "Saved-output replay, file seeding with all exec commands intercepted, and four deterministic forward evaluations only. No inverse optimization, agent run, Docker launch, runtime installation or full benchmark execution. The clean-reference diagnostic is an oracle control, never model evidence.",
        "all_assertions_passed": True,
    }
    (args.output / "audit.json").write_text(
        json.dumps(json_safe(record), indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            json_safe(
                {
                    "audit": str(args.output / "audit.json"),
                    "native": native,
                    "generic": fixtures,
                    "reference_diff": reference_diff,
                    "mole_fraction_diff": mole_fraction_diff,
                }
            ),
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
