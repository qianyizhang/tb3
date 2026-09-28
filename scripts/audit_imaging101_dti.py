"""Audit retained DTI arrays, fixed numerical controls and evaluator boundaries.

Executes selected pure functions on retained fixtures and five selected pixels.
Never imports the task authoring modules, generates data, fits a complete image,
installs a runtime, or launches an agent. Original arrays remain unchanged.
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
from audit_imaging101_poisson_lowdose import arrays, json_safe, selected, sha, stats

TASK = "diffusion_mri_dti"
COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"
PROBES = [(66, 26), (62, 85), (56, 64), (61, 21), (30, 99)]


def verify_sources(source):
    tree = json.loads((source / "github-tree.json").read_text())
    assert tree["sha"] == COMMIT and not tree["truncated"]
    known = {r["path"]: r for r in tree["tree"]}
    verified = []
    for name in ["fetch-receipt.json", "shared-source-receipt.json"]:
        receipt = json.loads((source / name).read_text())
        assert receipt["revision"] == COMMIT
        for row in receipt["files"]:
            p = source / row["path"]
            data = p.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            assert row["status"] == "verified" and sha(p) == row["sha256"]
            assert len(data) == known[row["path"]]["size"]
            assert blob == row["git_blob_sha1"] == known[row["path"]]["sha"]
            verified.append(row)
    assert len(verified) == 73
    attempts, assets = [], {}
    for name in [
        "asset-fetch-receipt.json",
        "asset-alternate-receipt.json",
        "asset-curl-receipt.json",
        "asset-short-domain-receipt.json",
    ]:
        for row in json.loads((source / name).read_text()):
            attempts.append(row)
            if row["status"] == "verified":
                assert row["revision"] == REVISION
                p = source / row["path"]
                assert sha(p) == row["sha256"] and p.stat().st_size == row["size"]
                assets[row["path"]] = row
    listing = json.loads((source / "hf-task-tree.json").read_text())
    listing_receipt = json.loads((source / "hf-task-tree-receipt.json").read_text())
    assert listing_receipt["sha256"] == sha(source / "hf-task-tree.json")
    assert listing_receipt["link_header"] is None
    files = [r for r in listing if r["type"] == "file"]
    assert len(assets) == len(files) == 13
    assert set(assets) == {r["path"] for r in files}
    for row in files:
        if "lfs" in row:
            assert row["lfs"]["oid"] == assets[row["path"]]["sha256"]
    assert not any(r["path"].endswith("metrics.json") for r in files)
    return verified, assets, attempts, listing_receipt


def fixture_checks(task, ns):
    result = {}

    def compare(label, actual, expected):
        error = float(np.max(np.abs(actual - expected)))
        assert np.allclose(actual, expected, rtol=1e-10, atol=1e-12), (label, error)
        result[label] = error

    f = arrays(task / "evaluation/fixtures/tensor_roundtrip.npz")
    compare("elements", ns["elements_from_tensor"](f["input_tensor"]), f["output_elements"])
    compare("tensor", ns["tensor_from_elements"](*f["output_elements"]), f["output_tensor"])
    f = arrays(task / "evaluation/fixtures/design_matrix.npz")
    compare(
        "design_matrix", ns["build_design_matrix"](f["input_bvals"], f["input_bvecs"]), f["output"]
    )
    f = arrays(task / "evaluation/fixtures/stejskal_tanner.npz")
    compare(
        "signal",
        ns["stejskal_tanner_signal"](
            f["input_S0"], f["input_D"], f["input_bvals"], f["input_bvecs"]
        ),
        f["output_signal"],
    )
    f = arrays(task / "evaluation/fixtures/scalar_maps.npz")
    for name in ["fa", "md"]:
        compare(name, ns[f"compute_{name}"](f["input_evals"]), f[f"output_{name}"])
    for method in ["ols", "wls"]:
        f = arrays(task / f"evaluation/fixtures/{method}_fit.npz")
        tensor, s0 = ns[f"fit_dti_{method}"](
            f["input_dwi"], f["input_bvals"], f["input_bvecs"], f["input_mask"]
        )
        compare(f"{method}_tensor", tensor, f["output_tensor"])
        compare(f"{method}_s0", s0, f["output_S0"])
    f = arrays(task / "evaluation/fixtures/eig_decomposition.npz")
    ev, vectors, fa, md = ns["tensor_eig_decomposition"](f["input_tensor_elems"], f["input_mask"])
    for name, actual in [("evals", ev), ("fa_map", fa), ("md_map", md)]:
        compare(name, actual, f[f"output_{name}"])
    # Eigenvector signs are arbitrary; compare their rank-one projectors.
    projectors = np.einsum("...ik,...jk->...kij", vectors, vectors)
    expected = np.einsum("...ik,...jk->...kij", f["output_evecs"], f["output_evecs"])
    compare("eigenvector_projectors", projectors, expected)
    f = arrays(task / "evaluation/fixtures/metrics.npz")
    for name in ["ncc", "nrmse"]:
        compare(name, ns[f"compute_{name}"](f["input_x"], f["input_y"]), f[f"output_{name}"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, out = args.sources, args.output
    out.mkdir(parents=True, exist_ok=False)
    task = source / "tasks" / TASK
    verified, assets, attempts, listing = verify_sources(source)
    metadata = json.loads((task / "data/meta_data.json").read_text())
    raw = arrays(task / "data/raw_data.npz")
    truth = arrays(task / "data/ground_truth.npz")
    saved = {m: arrays(task / f"evaluation/reference_outputs/dti_{m}.npz") for m in ["ols", "wls"]}
    mask = truth["tissue_mask"][0]
    assert raw["dwi_signal"].shape == (1, 128, 128, 31)
    assert int(mask.sum()) == 7186
    ns = {"np": np}
    selections = {}
    for filename, names in [
        (
            "physics_model.py",
            [
                "tensor_from_elements",
                "elements_from_tensor",
                "tensor_from_eig",
                "build_design_matrix",
                "stejskal_tanner_signal",
                "compute_fa",
                "compute_md",
            ],
        ),
        ("solvers.py", ["fit_dti_ols", "fit_dti_wls", "tensor_eig_decomposition"]),
        ("preprocessing.py", ["preprocess_dwi"]),
        ("visualization.py", ["compute_ncc", "compute_nrmse"]),
        ("generate_data.py", ["_rotation_matrix_from_axis"]),
    ]:
        selections[filename] = selected(task / "src" / filename, names, ns)
    fixtures = fixture_checks(task, ns)
    dwi, measured_s0 = ns["preprocess_dwi"](raw["dwi_signal"], raw["bvals"], raw["bvecs"])
    B = ns["build_design_matrix"](raw["bvals"], raw["bvecs"])
    assert np.linalg.matrix_rank(B) == 7
    assert np.array_equal(measured_s0, raw["dwi_signal"][0, ..., 0])
    assert np.array_equal(np.unique(raw["bvals"]), [0, 1000])
    assert np.allclose(np.linalg.norm(raw["bvecs"][1:], axis=1), 1, atol=1e-7)

    def tensor(e):
        return ns["tensor_from_elements"](*np.moveaxis(e, -1, 0))

    def metrics(estimate, reference):
        return {n: ns[f"compute_{n}"](estimate, reference, mask=mask) for n in ["ncc", "nrmse"]}

    derived, native_scores = {}, {}
    for name, data in {"truth": truth, **saved}.items():
        ev = np.linalg.eigvalsh(tensor(data["tensor_elements"][0]))
        clipped = np.maximum(ev, 0)
        errors = {}
        for scalar in ["fa", "md"]:
            computed = ns[f"compute_{scalar}"](clipped)
            computed = np.where(mask, computed, 0)
            error = float(np.max(np.abs(computed - data[f"{scalar}_map"][0])))
            assert error < (2e-7 if scalar == "fa" else 1e-9), (name, scalar, error)
            errors[scalar] = error
        derived[name] = {
            "map_max_abs_errors_from_saved_tensor": errors,
            "negative_eigenvalue_voxels": int(np.any(ev[mask] < 0, axis=-1).sum()),
            "minimum_masked_eigenvalue": float(ev[mask].min()),
            "mask_voxels": int(mask.sum()),
        }
        if name != "truth":
            native_scores[name] = {
                k: metrics(data[f"{k}_map"][0], truth[f"{k}_map"][0]) for k in ["fa", "md"]
            }

    # These five pixels are deliberately selected after reference inspection, one
    # per distinct source tensor. This is an explanatory control, not a trial.
    pixels = np.array([dwi[y, x] for y, x in PROBES])[None, ...]
    probe_fits = {}
    for method in ["ols", "wls"]:
        elems, s0 = ns[f"fit_dti_{method}"](pixels, raw["bvals"], raw["bvecs"])
        expected = np.array([saved[method]["tensor_elements"][0, y, x] for y, x in PROBES])
        error = float(np.max(np.abs(elems[0] - expected)))
        assert error < 1e-8, (method, error)
        predicted = ns["stejskal_tanner_signal"](s0, tensor(elems), raw["bvals"], raw["bvecs"])
        linear = np.exp(np.column_stack([np.log(s0[0]), elems[0]]) @ B.T)
        assert np.allclose(predicted[0], linear, atol=1e-12)
        probe_fits[method] = {
            "max_abs_tensor_error_vs_saved": error,
            "tensor_elements": elems[0].tolist(),
            "fitted_s0": s0[0].tolist(),
            "predicted_signal": predicted[0].tolist(),
        }
    probes = []
    for y, x in PROBES:
        D = tensor(truth["tensor_elements"][0, y, x])
        ev, vectors = np.linalg.eigh(D)
        probes.append(
            {
                "row": y,
                "column": x,
                "signal": dwi[y, x].tolist(),
                "truth_tensor": D.tolist(),
                "truth_eigenvalues": ev[::-1].tolist(),
                "truth_principal_axis_absolute": np.abs(vectors[:, -1]).tolist(),
                "principal_axis_unique": bool(ev[-1] - ev[-2] > 1e-10),
                "truth_fa": float(truth["fa_map"][0, y, x]),
                "truth_md": float(truth["md_map"][0, y, x]),
            }
        )
    notebook_probes = []
    for label, (y, x) in zip(
        ["White matter (high FA)", "Gray matter (low FA)", "CSF (isotropic)"],
        [(45, 64), (64, 64), (64, 50)],
        strict=True,
    ):
        notebook_probes.append(
            {
                "source_label": label,
                "row": y,
                "column": x,
                "in_tissue_mask": bool(mask[y, x]),
                "fa": float(truth["fa_map"][0, y, x]),
                "md": float(truth["md_map"][0, y, x]),
                "tensor_elements": truth["tensor_elements"][0, y, x].tolist(),
            }
        )
    generator_ast = ast.parse((task / "src/generate_data.py").read_text())
    regions = next(
        ast.literal_eval(n.value)
        for n in generator_ast.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "TISSUE_REGIONS" for t in n.targets)
    )
    orientation = []
    for _lo, _hi, values, direction, _s0, label in regions:
        R = ns["_rotation_matrix_from_axis"](direction)
        D = R @ np.diag(values) @ R.T
        stored = ns["elements_from_tensor"](D).astype(np.float32)
        match = np.all(truth["tensor_elements"][0] == stored, axis=-1) & mask
        assert match.any(), label
        ev, vectors = np.linalg.eigh(D)
        unique = bool(ev[-1] - ev[-2] > 1e-10)
        direction_array = np.array(direction) / np.linalg.norm(direction)
        alignment = float(abs(vectors[:, -1] @ direction_array)) if unique else None
        orientation.append(
            {
                "source_label": label,
                "declared_direction": direction,
                "source_rotation_maps_z_to_declared_axis": bool(
                    np.allclose(R[:, 2], direction_array)
                ),
                "stored_tensor_elements": stored.tolist(),
                "matching_voxels": int(match.sum()),
                "principal_axis_unique": unique,
                "actual_principal_axis_absolute": np.abs(vectors[:, -1]).tolist()
                if unique
                else None,
                "absolute_alignment_with_declared_axis": alignment,
            }
        )
    assert all(
        r["absolute_alignment_with_declared_axis"] == 0
        for r in orientation
        if r["principal_axis_unique"]
    )

    harness = source / "evaluation_harness"
    spec = importlib.util.spec_from_file_location(
        "dti_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=ref)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("dti-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer.py"] = selected(
        harness / "scorer.py",
        ["_compute_quality_metrics", "_compute_quality_metrics_generic"],
        scorer_ns,
        "Scorer",
    )
    custom_ns = {"np": np, "Path": Path, "os": os, "_imp": lambda _: SimpleNamespace(**ns)}
    selections["custom"] = selected(
        harness / "task_scoring_custom.py",
        ["_bases", "_find", "score_diffusion_mri_dti"],
        custom_ns,
    )
    custom_fn = custom_ns["score_diffusion_mri_dti"]
    custom = {"both_saved_files": custom_fn(task, task / "evaluation/reference_outputs")}
    for method in ["ols", "wls"]:
        dest = out / "custom" / method
        dest.mkdir(parents=True)
        shutil.copy2(
            task / f"evaluation/reference_outputs/dti_{method}.npz", dest / f"dti_{method}.npz"
        )
        custom[method] = custom_fn(task, dest)
        assert custom[method] == native_scores[method]["fa"]
    assert custom["both_saved_files"] == custom["ols"]
    for name, fields in {
        "oracle_fa_only": {"fa_map": truth["fa_map"]},
        "oracle_fa_with_zero_md_and_tensor": {
            "fa_map": truth["fa_map"],
            "md_map": np.zeros_like(truth["md_map"]),
            "tensor_elements": np.zeros_like(truth["tensor_elements"]),
        },
        "oracle_fa_with_background_corruption": {
            "fa_map": np.where(truth["tissue_mask"], truth["fa_map"], 100.0)
        },
    }.items():
        dest = out / "custom" / name
        dest.mkdir(parents=True)
        np.savez(dest / "reconstruction.npz", **fields)
        custom[name] = custom_fn(task, dest)
        assert custom[name]["nrmse"] == 0 and np.isclose(custom[name]["ncc"], 1)
    generic = {}
    for name, value in {
        **{f"{m}_fa": saved[m]["fa_map"] for m in saved},
        **{f"{m}_md": saved[m]["md_map"] for m in saved},
        **{f"{m}_tensor": saved[m]["tensor_elements"] for m in saved},
        "oracle_fa": truth["fa_map"],
        "oracle_md": truth["md_map"],
        "oracle_tensor": truth["tensor_elements"],
        "zeros_fa": np.zeros_like(truth["fa_map"]),
        "oracle_fa_with_background_corruption": np.where(
            truth["tissue_mask"], truth["fa_map"], 100.0
        ),
    }.items():
        dest = out / "generic" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", value)
        driver = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
            runner=SimpleNamespace(container=str(dest.parent)),
        )
        result = scorer_ns["_compute_quality_metrics"](driver)
        chosen, chosen_path = ref.load_reference_array(task, np.squeeze(value).shape)
        keys = [k for k, v in truth.items() if np.array_equal(chosen, np.squeeze(v))]
        result["selected_reference_keys"] = keys
        result["selected_reference_path"] = str(chosen_path.relative_to(source))
        assert "passed" not in result and "boundaries" not in result
        generic[name] = result
    assert generic["oracle_md"]["selected_reference_keys"] == ["fa_map"]
    assert generic["oracle_fa"]["nrmse"] == generic["oracle_tensor"]["nrmse"] == 0
    assert generic["oracle_md"]["nrmse"] > 0.5

    # Exercise the dispatch without a host workspace; no Docker process or
    # runner command is launched. Its legacy fallback accepts only .npy truth.
    fallback_commands = []
    fallback_driver = SimpleNamespace(
        config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
        runner=SimpleNamespace(container=None, exec=lambda cmd: fallback_commands.append(cmd)),
    )
    fallback_driver._compute_quality_metrics_generic = lambda: scorer_ns[
        "_compute_quality_metrics_generic"
    ](fallback_driver)
    fallback = scorer_ns["_compute_quality_metrics"](fallback_driver)
    assert fallback == {
        "error": "ground_truth.npy not found in task directory",
        "scorer": "generic",
    }
    assert not fallback_commands

    stage_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("dti-audit")}
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
        for filename in ["ground_truth.npz", "raw_data.npz", "meta_data.json"]:
            assert sha(dest / "data" / filename) == sha(task / "data" / filename)
        assert not (dest / "src").exists() and not (dest / "evaluation").exists()
        staging[level] = {
            "visible_paths": visible,
            "available_files_copied": sorted(
                str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()
            ),
            "truth_and_mask_copied": True,
            "commands_intercepted": commands,
        }
    notebook = json.loads((task / "notebooks/diffusion_mri_dti.ipynb").read_text())
    notebook_metrics = ["".join(o["text"]) for o in notebook["cells"][15]["outputs"] if "text" in o]
    report = {
        "schema": 1,
        "entry_id": "imaging101-diffusion-mri-dti",
        "date": "2026-09-29",
        "reviewer": "assistant",
        "source_commit": COMMIT,
        "asset_revision": REVISION,
        "script_sha256": sha(Path(__file__)),
        "helper_script_sha256": sha(
            Path(__file__).with_name("audit_imaging101_poisson_lowdose.py")
        ),
        "verified_sources": verified,
        "verified_assets": list(assets.values()),
        "asset_attempts": attempts,
        "published_listing": listing,
        "metadata": metadata,
        "arrays": {
            name: {k: stats(v) for k, v in values.items()}
            for name, values in {"raw": raw, "truth": truth, **saved}.items()
        },
        "gradient_table": {
            "bvals": raw["bvals"].tolist(),
            "bvecs": raw["bvecs"].tolist(),
            "design_matrix": B.tolist(),
            "rank": int(np.linalg.matrix_rank(B)),
            "condition_number_unscaled_units": float(np.linalg.cond(B)),
            "condition_number_unit_norm_columns": float(
                np.linalg.cond(B / np.linalg.norm(B, axis=0))
            ),
        },
        "fixture_max_abs_errors": fixtures,
        "saved_derived_maps": derived,
        "native_masked_metrics": native_scores,
        "selected_probes": probes,
        "selected_probe_fits": probe_fits,
        "probe_selection": "Five post-hoc pixels, one per distinct retained truth tensor. No random sample or clinical labels.",
        "notebook_probe_check": notebook_probes,
        "orientation_controls": orientation,
        "custom_scoring": custom,
        "generic_scoring": generic,
        "no_filesystem_workspace_dispatch": {
            "result": fallback,
            "runner_commands_executed": len(fallback_commands),
            "scope": "Source branch control only; no container or remote execution.",
        },
        "notebook_historical_metric_text": notebook_metrics,
        "threshold_availability": "metrics.json absent from both pinned code tree and complete 13-file asset listing; notebook boundary text is historical, not a staged evaluator file.",
        "staging": staging,
        "source_function_selections": selections,
        "scope": {
            "agent_runs": 0,
            "full_image_fits": 0,
            "generator_runs": 0,
            "runtime_installs": 0,
            "saved_data": "One synthetic 128x128 phantom; no patient data or clinical validity claim.",
            "controls": "Eight retained helper fixtures; five post-hoc native pixels; saved-array metric/eigenvalue checks; evaluator oracle/no-op controls; file seeding with installers intercepted.",
            "reference_boundary": "All L1-L3 expose truth and tissue mask. A future reader reveal is not solver privacy.",
        },
    }
    (out / "audit.json").write_text(json.dumps(json_safe(report), indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(out / "audit.json"),
                "sha256": sha(out / "audit.json"),
                "verified_assets": len(assets),
                "native_metrics": native_scores,
                "generic_oracle_md": generic["oracle_md"],
                "saved_derived_maps": derived,
            }
        )
    )


if __name__ == "__main__":
    main()
