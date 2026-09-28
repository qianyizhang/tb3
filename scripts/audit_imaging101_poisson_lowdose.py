"""Audit the inconsistent pinned low-dose CT release without running a solver.

Rechecks source/asset identities, evaluates selected pure arithmetic functions,
and scores retained arrays in explicitly separate diagnostic reference contexts.
Never generates measurements, installs SVMBIR, or executes reconstruction code.
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

COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"
TASK = "ct_poisson_lowdose"


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


def arrays(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def json_safe(value):
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return str(value)
    return value


def stats(array):
    return {
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "min": float(array.min()),
        "max": float(array.max()),
        "nonfinite": int((~np.isfinite(array)).sum()),
        "array_sha256": hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest(),
    }


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
            verified.append(row)
    assert len(verified) == 73
    assert json.loads((source / "hf-revision.json").read_text())["sha"] == REVISION
    hf_tree = {r["path"]: r for r in json.loads((source / "data-tree.json").read_text())}
    assets = []
    for row in json.loads((source / "asset-fetch-receipt.json").read_text()):
        assert row["revision"] == REVISION
        valid = row["status"] == "verified"
        p = source / row["path"] if valid else source / "recovery" / Path(row["path"]).name
        digest = sha(p)
        assert p.stat().st_size == row["size"]
        assert (digest == row["sha256"]) == valid
        if not valid:
            assert not (source / row["path"]).exists()
            assert digest == hf_tree[row["hf_path"]]["lfs"]["oid"]
        assets.append(
            {**row, "observed_sha256": digest, "manifest_match": valid, "local_path": str(p)}
        )
    assert sum(r["manifest_match"] for r in assets) == 4 and len(assets) == 6
    meta = json.loads((task / "data/meta_data.json").read_text())
    raw = arrays(source / "recovery/raw_data.npz")
    old_truth = arrays(source / "recovery/ground_truth.npz")["phantom"].squeeze()
    physics = arrays(task / "evaluation/fixtures/physics_model_fixtures.npz")
    fixture = arrays(task / "evaluation/fixtures/metrics_fixtures.npz")
    saved = arrays(task / "evaluation/reference_outputs/reconstructions.npz")
    fixture_truth = physics["param_phantom"]
    ns = {"np": np}
    selections = {}
    for file, names in [
        (
            "src/physics_model.py",
            ["poisson_pre_log_model", "post_log_transform", "compute_poisson_weights"],
        ),
        ("src/visualization.py", ["compute_ncc", "compute_nrmse", "centre_crop"]),
    ]:
        selections[file] = selected(task / file, names, ns)
    cc = ns["centre_crop"]

    def metrics(a, b):
        return {"ncc": ns["compute_ncc"](a, b), "nrmse": ns["compute_nrmse"](a, b)}

    fixture_checks = {
        "reference_is_exact_physics_phantom_crop": np.array_equal(
            cc(fixture_truth), fixture["input_reference"]
        ),
        "fbp_is_exact_saved_crop": np.array_equal(
            cc(saved["recon_fbp"].squeeze()), fixture["input_estimate_fbp"]
        ),
        "pwls_is_exact_saved_crop": np.array_equal(
            cc(saved["recon_pwls_low"].squeeze()), fixture["input_estimate_pwls"]
        ),
    }
    assert all(fixture_checks.values())
    fixture_scores = {}
    for key in ["fbp", "pwls"]:
        m = metrics(fixture[f"input_estimate_{key}"], fixture["input_reference"])
        for name, value in m.items():
            assert np.isclose(value, float(fixture[f"output_{name}_{key}"]), rtol=1e-12, atol=1e-12)
        fixture_scores[key] = m
    physics_error = float(
        np.max(
            np.abs(
                ns["poisson_pre_log_model"](
                    physics["output_forward_proj"], float(physics["param_I0"])
                )
                - physics["output_transmission"]
            )
        )
    )
    assert physics_error < 1e-12
    dose_checks = {}
    for name, dose in [("low", 1000), ("high", 50000)]:
        weights = raw[f"weights_{name}_dose"]
        expected = raw[f"sinogram_{name}_dose"]
        error = float(np.max(np.abs(ns["post_log_transform"](weights, dose) - expected)))
        assert error < 1e-12 and np.array_equal(ns["compute_poisson_weights"](weights), weights)
        dose_checks[name] = {
            "matching_I0": dose,
            "postlog_max_abs_error": error,
            "count_floor_bins": int(np.count_nonzero(weights == 1)),
            "total_bins": int(weights.size),
        }
    dose_checks["low"]["metadata_I0_max_abs_error"] = float(
        np.max(
            np.abs(
                ns["post_log_transform"](raw["weights_low_dose"], meta["I0_low_dose"])
                - raw["sinogram_low_dose"]
            )
        )
    )
    assert np.isclose(dose_checks["low"]["metadata_I0_max_abs_error"], np.log(1000 / 300))
    assert not np.array_equal(old_truth, fixture_truth)

    # Separate contexts demonstrate scoring behavior, not valid benchmark results.
    harness = source / "evaluation_harness"
    spec = importlib.util.spec_from_file_location(
        "poisson_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=ref)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("poisson-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer.py"] = selected(
        harness / "scorer.py",
        ["_compute_quality_metrics", "_compute_quality_metrics_generic"],
        scorer_ns,
        "Scorer",
    )
    custom_ns = {"np": np, "Path": Path, "os": os, "_imp": lambda _: SimpleNamespace(**ns)}
    selections["task_scoring_custom.py"] = selected(
        harness / "task_scoring_custom.py",
        ["_bases", "_find", "_crop_common", "score_ct_poisson_lowdose"],
        custom_ns,
    )
    score_ns = {
        "Path": Path,
        "log": logging.getLogger("poisson-audit"),
        "_custom": SimpleNamespace(
            is_custom=lambda _: True,
            CUSTOM_SCORERS={
                TASK: {"pass": {"ncc": (">=", "ncc_boundary"), "nrmse": ("<=", "nrmse_boundary")}}
            },
            score_custom=lambda _, t, r: custom_ns["score_ct_poisson_lowdose"](t, r),
        ),
    }
    selections["task_scoring.py"] = selected(
        harness / "task_scoring.py", ["score_task", "_load_metrics_json", "_check_pass"], score_ns
    )
    contexts = {}
    for label, gt in [
        ("hf-1000-condition", old_truth),
        ("fixture-reference-diagnostic-only", fixture_truth),
    ]:
        context = out / label / "task"
        shutil.copytree(task, context)
        np.savez(context / "data/ground_truth.npz", phantom=gt[np.newaxis])
        if label == "hf-1000-condition":
            shutil.copy2(source / "recovery/ground_truth.npz", context / "data/ground_truth.npz")
            shutil.copy2(source / "recovery/raw_data.npz", context / "data/raw_data.npz")
        outside = np.ones_like(gt, dtype=bool)
        outside[26:230, 26:230] = False
        controls = {
            "oracle": gt,
            "half-reference": gt * 0.5,
            "outside-crop-only": gt + outside * 0.1,
            "zero": gt * 0,
        }
        scores = {}
        for name, array in {**{k: v.squeeze() for k, v in saved.items()}, **controls}.items():
            dest = out / label / "scores" / name / "output"
            dest.mkdir(parents=True)
            np.save(dest / "reconstruction.npy", array)
            driver = SimpleNamespace(
                config=SimpleNamespace(task=SimpleNamespace(task_dir=context)),
                runner=SimpleNamespace(container=str(dest.parent)),
            )
            generic = scorer_ns["_compute_quality_metrics"](driver)
            native = score_ns["score_task"](TASK, context, dest.parent)
            assert generic.get("passed") is None and native["passed"] is None
            scores[name] = {"generic_full_image": generic, "task_aware_crop": native}
        assert scores["outside-crop-only"]["task_aware_crop"]["nrmse"] == 0
        assert scores["outside-crop-only"]["generic_full_image"]["nrmse"] > 0.1
        scores["saved-npz-custom-key-selection"] = score_ns["score_task"](
            TASK, context, context / "evaluation/reference_outputs"
        )
        assert (
            scores["saved-npz-custom-key-selection"]["nrmse"]
            == scores["recon_pwls_low"]["task_aware_crop"]["nrmse"]
        )
        contexts[label] = {"reference": stats(gt), "scores": scores}

    # Actual file-seeding code with every installation command intercepted.
    stage_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("poisson-audit")}
    selections["runner.py"] = selected(
        harness / "runner.py", ["_get_visible_paths"], stage_ns, "BenchmarkRunner"
    )
    selections["local_runner.py"] = selected(
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
            task_dir=(out / "hf-1000-condition/task").resolve(),
            exec=lambda cmd, log=commands: log.append(cmd),
        )
        visible = stage_ns["_get_visible_paths"](driver)
        stage_ns["start"](driver, visible)
        assert sha(dest / "data/ground_truth.npz") == sha(source / "recovery/ground_truth.npz")
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "truth_copied": True,
            "files": sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()),
            "commands_intercepted": commands,
        }
    fallback, fallback_path = ref.load_reference_array(task, (256, 256))
    assert np.array_equal(fallback, saved["recon_fbp"].squeeze())
    hf_listing = json.loads((source / "history/hf-task-tree.json").read_text())
    assert not any(r["path"].endswith("metrics.json") for r in hf_listing)
    assert not any(
        r["path"].startswith(f"tasks/{TASK}/") and r["path"].endswith("metrics.json")
        for r in tree["tree"]
    )
    notebook = json.loads((task / "notebooks/ct_poisson_lowdose.ipynb").read_text())
    text_outputs = [
        {"cell": i, "text": "".join("".join(o.get("text", [])) for o in c.get("outputs", []))}
        for i, c in enumerate(notebook["cells"])
        if any("text" in o for o in c.get("outputs", []))
    ]
    report = {
        "schema": 1,
        "entry_id": "imaging101-ct-poisson-lowdose",
        "date": "2026-09-29",
        "reviewer": "assistant",
        "disposition": "blocked-source-input",
        "source_commit": COMMIT,
        "asset_revision": REVISION,
        "audit_script_sha256": sha(Path(__file__)),
        "verified_sources": verified,
        "assets": assets,
        "runtime": {
            "numpy": np.__version__,
            "svmbir_available": importlib.util.find_spec("svmbir") is not None,
            "scope": "Selected pure NumPy functions; not the declared numpy<2/SVMBIR runtime.",
        },
        "metadata": meta,
        "recovered_raw": {k: stats(v) for k, v in raw.items()},
        "recovered_truth": stats(old_truth),
        "physics_fixture": {k: stats(v) for k, v in physics.items()},
        "saved_arrays": {k: stats(v) for k, v in saved.items()},
        "fixture_checks": fixture_checks,
        "fixture_scores": fixture_scores,
        "transmission_fixture_max_abs_error": physics_error,
        "dose_consistency": dose_checks,
        "scoring_diagnostics": contexts,
        "staging": staging,
        "missing_truth_fallback": {
            "path": str(fallback_path.relative_to(source)),
            "key": "recon_fbp",
            "note": "Generic reference discovery falls back to a saved reconstruction if ground truth is absent. This does not repair the missing input.",
        },
        "metrics_file_present": False,
        "notebook_historical_stdout": text_outputs,
        "source_function_selections": selections,
        "history_receipts": {
            str(p.relative_to(source)): sha(p) for p in sorted((source / "history").glob("*.json"))
        },
        "execution_scope": {
            "model_runs": 0,
            "solver_iterations": 0,
            "data_generator_runs": 0,
            "runtime_installs": 0,
            "reference_substitution": "Only in separately labeled diagnostic directories; pinned source and recovery files unchanged.",
        },
    }
    (out / "audit.json").write_text(json.dumps(json_safe(report), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(out / "audit.json"),
                "sha256": sha(out / "audit.json"),
                "verified_sources": len(verified),
                "verified_assets": 4,
                "mismatched_assets": 2,
                "fixture_scores": fixture_scores,
            }
        )
    )


if __name__ == "__main__":
    main()
