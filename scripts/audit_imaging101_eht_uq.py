"""Audit retained EHT closures, posterior arrays and evaluator boundaries.

Only replays saved arrays and selected pure functions. Does not train or sample
a network, install dependencies, import task authoring modules, or run a trial.
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
import torch
from audit_imaging101_poisson_lowdose import arrays, json_safe, selected, sha, stats

TASK = "eht_black_hole_UQ"
COMMIT = "dc2f668939b21e8312e22529615def610f8611df"
REVISION = "a9de559b54849a25988a8a0d8a5e869063a5a7a3"


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


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
            assert row["status"] == "verified" and sha(p) == row["sha256"]
            assert len(data) == known[row["path"]]["size"]
            assert blob(data) == row["git_blob_sha1"] == known[row["path"]]["sha"]
            verified.append(row)
    assert len(verified) == 74
    assets = []
    for name in ["asset-short-domain-receipt.json", "asset-extra-receipt.json"]:
        for row in json.loads((source / name).read_text()):
            p = source / row["path"]
            assert row["status"] == "verified" and row["revision"] == REVISION
            assert sha(p) == row["sha256"] and p.stat().st_size == row["size"]
            assets.append(row)
    listing = json.loads((source / "hf-task-tree.json").read_text())
    receipt = json.loads((source / "hf-task-tree-receipt.json").read_text())
    assert receipt["sha256"] == sha(source / "hf-task-tree.json")
    assert receipt["link_header"] is None
    files = {r["path"]: r for r in listing if r["type"] == "file"}
    assert len(assets) == 28 and len(files) == 30
    for row in assets:
        assert row["size"] == files[row["path"]]["size"]
        if "lfs" in files[row["path"]]:
            assert row["sha256"] == files[row["path"]]["lfs"]["oid"]
        else:
            assert blob((source / row["path"]).read_bytes()) == files[row["path"]]["oid"]
    omitted = [r for name, r in files.items() if name not in {a["path"] for a in assets}]
    assert all(r["path"].endswith(".pt") for r in omitted)
    upstream = json.loads((source / "dpi-github-tree.json").read_text())
    upstream_receipt = json.loads((source / "dpi-github-tree-receipt.json").read_text())
    assert not upstream["truncated"]
    assert sha(source / "dpi-github-tree.json") == upstream_receipt["sha256"]
    origins = []
    for name in ["gt.fits", "obs.uvfits"]:
        p = source / "tasks" / TASK / "data" / name
        matches = [r for r in upstream["tree"] if r.get("sha") == blob(p.read_bytes())]
        assert len(matches) == 1 and matches[0]["size"] == p.stat().st_size
        origins.append({"local_path": str(p.relative_to(source)), **matches[0]})
    extra_sources = json.loads((source / "dpi-source-receipt.json").read_text())
    for row in extra_sources:
        p = source / "upstream-dpi" / row["path"]
        assert sha(p) == row["sha256"] and blob(p.read_bytes()) == row["sha"]
        assert row["revision"] == upstream["sha"]
    return verified, assets, omitted, receipt, origins, extra_sources, upstream["sha"]


def closures(vis, indices):
    phases = sum(
        np.angle(vis[..., ind]) * sign
        for ind, sign in zip(indices["cphase_ind_list"], indices["cphase_sign_list"], strict=True)
    )
    logamp = sum(
        np.log(np.abs(vis[..., ind])) * sign
        for ind, sign in zip(indices["camp_ind_list"], [1, 1, -1, -1], strict=True)
    )
    return phases * 180 / np.pi, logamp


def wrapped_degrees(values):
    return (values + 180) % 360 - 180


def max_error(a, b):
    return float(np.max(np.abs(a - b)))


def fits_header(path):
    data = path.read_bytes()
    cards = []
    for i in range(0, len(data), 80):
        card = data[i : i + 80].decode("ascii")
        cards.append(card.rstrip())
        if card.startswith("END "):
            return cards
    raise ValueError(f"Missing FITS END: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source, out = args.sources, args.output
    out.mkdir(parents=True, exist_ok=False)
    verified, assets, omitted, listing, origins, upstream, upstream_commit = verify_sources(source)
    task = source / "tasks" / TASK
    raw = arrays(task / "data/raw_data.npz")
    truth = arrays(task / "data/ground_truth.npz")["image"]
    ref_dir = task / "evaluation/reference_outputs"
    saved = {
        n: np.load(ref_dir / (n + ".npy"), allow_pickle=False)
        for n in [
            "ground_truth",
            "posterior_mean",
            "posterior_std",
            "posterior_samples",
            "posterior_samples_1024",
        ]
    }
    truth_copy_error = max_error(truth, saved["ground_truth"])
    assert truth_copy_error < 1e-15
    meta = json.loads((task / "data/meta_data.json").read_text())
    assert (task / "data/meta_data").read_bytes() == (task / "data/meta_data.json").read_bytes()
    ns = {"np": np, "torch": torch, "os": os, "json": json}
    selections = {}
    for filename, names in [
        (
            "preprocessing.py",
            [
                "load_observation",
                "extract_closure_indices",
                "build_prior_image",
                "compute_nufft_params",
            ],
        ),
        ("visualization.py", ["compute_metrics", "compute_uq_metrics"]),
        (
            "physics_model.py",
            [
                "Loss_angle_diff",
                "Loss_logca_diff2",
                "Loss_vis_diff",
                "Loss_logamp_diff",
                "Loss_visamp_diff",
                "Loss_l1",
                "Loss_TSV",
                "Loss_flux",
                "Loss_center",
            ],
        ),
    ]:
        selections[filename] = selected(task / "src" / filename, names, ns)
    indices = ns["extract_closure_indices"](raw)
    prior, flux = ns["build_prior_image"](raw["vis"], 32, 160)
    short_baseline = ((raw["t1"] == b"APEX") & (raw["t2"] == b"ALMA")) | (
        (raw["t1"] == b"ALMA") & (raw["t2"] == b"APEX")
    )
    short_flux = float(np.median(abs(raw["vis"][short_baseline])))
    params = ns["compute_nufft_params"](raw["uv_coords"], 32, 160)
    fixtures = task / "evaluation/fixtures"
    parity = arrays(fixtures / "parity/orig_preproc.npz")
    preprocessing = {}
    f = arrays(fixtures / "preprocessing/extract_closure_indices.npz")
    for family, key, oldkey in [
        ("cphase_ind_list", "cphase_ind", "cp_ind"),
        ("cphase_sign_list", "cphase_sign", "cp_sign"),
        ("camp_ind_list", "camp_ind", "ca_ind"),
    ]:
        for j, a in enumerate(indices[family]):
            assert np.array_equal(a, f[f"output_{key}{j}"])
            assert np.array_equal(a, parity[f"{oldkey}{j}"])
    preprocessing["all_ten_closure_index_and_sign_arrays_match_both_fixtures"] = True
    f = arrays(fixtures / "preprocessing/load_observation.npz")
    assert np.array_equal(f["output_vis_first5"], raw["vis"][:5])
    preprocessing["observation_first_five_exact"] = True
    f = arrays(fixtures / "preprocessing/compute_nufft_params.npz")
    preprocessing["trajectory_max_error_vs_fixture"] = max_error(
        params["ktraj_vis"].numpy(), f["output_ktraj_vis"]
    )
    preprocessing["trajectory_max_error_vs_parity"] = max_error(
        params["ktraj_vis"].numpy(), parity["ktraj"]
    )
    preprocessing["pulse_max_error_vs_fixture"] = max_error(
        params["pulsefac_vis"].numpy(), f["output_pulsefac_vis"]
    )
    preprocessing["pulse_max_error_vs_parity"] = max_error(
        params["pulsefac_vis"].numpy(), parity["pulsefac"]
    )
    f = arrays(fixtures / "preprocessing/build_prior_image.npz")
    preprocessing.update(
        {
            "current_median_all_visibility_flux_Jy": flux,
            "upstream_APEX_ALMA_median_flux_Jy": short_flux,
            "APEX_ALMA_visibility_count": int(short_baseline.sum()),
            "retained_fixture_flux_Jy": float(f["output_flux_const"]),
            "retained_parity_flux_Jy": float(parity["flux_const"]),
            "current_prior_sum_Jy": float(prior.sum()),
            "retained_prior_sum_Jy": float(f["output_prior"].sum()),
            "prior_max_error_vs_fixture": max_error(prior, f["output_prior"]),
            "prior_max_error_vs_parity": max_error(prior, parity["prior_image"]),
        }
    )
    assert preprocessing["trajectory_max_error_vs_fixture"] == 0
    assert preprocessing["pulse_max_error_vs_fixture"] == 0
    assert preprocessing["pulse_max_error_vs_parity"] < 1e-7
    assert preprocessing["prior_max_error_vs_fixture"] > 0.01
    assert short_flux == preprocessing["retained_fixture_flux_Jy"]
    cp, ca = closures(raw["vis"], indices)
    raw_replay = {
        "wrapped_closure_phase_max_error_deg": max_error(
            wrapped_degrees(cp - raw["cp_values_deg"]), 0
        ),
        "log_closure_amplitude_max_error": max_error(ca, raw["lca_values"]),
    }
    assert raw_replay["wrapped_closure_phase_max_error_deg"] < 1e-8
    assert raw_replay["log_closure_amplitude_max_error"] < 1e-12
    # Deterministic multiplicative station gains, no new observation simulation.
    stations = sorted(set(raw["t1"]) | set(raw["t2"]))
    gains = {s: (0.6 + j * 0.17) * np.exp(1j * (j * 0.37 - 1)) for j, s in enumerate(stations)}
    corrupted = raw["vis"] * np.array(
        [gains[a] * gains[b].conjugate() for a, b in zip(raw["t1"], raw["t2"], strict=True)]
    )
    cp2, ca2 = closures(corrupted, indices)
    gain_control = {
        "station_gains": {s.decode(): [float(g.real), float(g.imag)] for s, g in gains.items()},
        "visibility_max_change_Jy": max_error(corrupted, raw["vis"]),
        "wrapped_phase_max_change_deg": max_error(wrapped_degrees(cp2 - cp), 0),
        "log_closure_amplitude_max_change": max_error(ca2, ca),
        "scope": "Exact multiplicative station-gain identity on stored visibilities; thermal noise and other corruptions are not removed.",
    }
    assert gain_control["visibility_max_change_Jy"] > 1
    assert gain_control["wrapped_phase_max_change_deg"] < 1e-8
    assert gain_control["log_closure_amplitude_max_change"] < 1e-12
    # Source loss functions on their tiny retained numerical fixtures.
    loss_checks = {}
    for stem, name in [
        ("loss_angle_diff", "Loss_angle_diff"),
        ("loss_logca_diff2", "Loss_logca_diff2"),
        ("loss_vis_diff", "Loss_vis_diff"),
        ("loss_logamp_diff", "Loss_logamp_diff"),
        ("loss_visamp_diff", "Loss_visamp_diff"),
    ]:
        f = arrays(fixtures / "physics_model" / (stem + ".npz"))
        got = ns[name](f["input_sigma"], torch.device("cpu"))(
            torch.tensor(f["input_true"]), torch.tensor(f["input_pred"])
        ).numpy()
        assert np.allclose(got, f["output_loss"], rtol=1e-5, atol=1e-6)
        loss_checks[stem] = max_error(got, f["output_loss"])
    f = arrays(fixtures / "physics_model/loss_priors.npz")
    a = torch.tensor(f["input_image"])
    for label, got in {
        "l1": ns["Loss_l1"](a),
        "tsv": ns["Loss_TSV"](a),
        "flux": ns["Loss_flux"](float(f["config_flux"]))(a),
        "center": ns["Loss_center"](torch.device("cpu"))(a),
    }.items():
        assert np.allclose(got.numpy(), f[f"output_{label}"], rtol=1e-5, atol=1e-6)
        loss_checks[label] = max_error(got.numpy(), f[f"output_{label}"])
    metric_checks = {}
    f = arrays(fixtures / "visualization/compute_metrics.npz")
    for key, got in ns["compute_metrics"](f["input_estimate"], f["input_ground_truth"]).items():
        assert np.isclose(got, f[f"output_{key}"], rtol=1e-12)
        metric_checks[key] = abs(got - float(f[f"output_{key}"]))
    f = arrays(fixtures / "visualization/compute_uq_metrics.npz")
    got = ns["compute_uq_metrics"](f["input_mean"], f["input_std"], f["input_gt"])
    for key in ["calibration", "mean_uncertainty"]:
        assert got[key] == f[f"output_{key}"]
        metric_checks[key] = abs(got[key] - float(f[f"output_{key}"]))
    mean, std = saved["posterior_mean"], saved["posterior_std"]
    native = ns["compute_uq_metrics"](mean, std, truth)
    sample_sets = {}
    for name in ["posterior_samples", "posterior_samples_1024"]:
        a = saved[name]
        assert a.shape == (1024, 32, 32)
        sample_sets[name] = {
            "shape": list(a.shape),
            "array_sha256": stats(a)["array_sha256"],
            "mean_max_error_vs_saved": max_error(a.mean(0), mean),
            "std_max_error_vs_saved": max_error(a.std(0), std),
            "metrics_of_own_mean_and_std": ns["compute_uq_metrics"](a.mean(0), a.std(0), truth),
        }
    assert sample_sets["posterior_samples"]["mean_max_error_vs_saved"] == 0
    assert sample_sets["posterior_samples"]["std_max_error_vs_saved"] == 0
    assert sample_sets["posterior_samples_1024"]["mean_max_error_vs_saved"] > 0.01
    quoted = json.loads((ref_dir / "metrics.json").read_text())
    for key in native:
        assert abs(quoted[key] - native[key]) < 0.0001
    uq = {
        "native_saved_map_metrics": native,
        "within_one_std_pixels": int((abs(truth - mean) <= std).sum()),
        "pixel_count": truth.size,
        "truth_flux_Jy": float(truth.sum()),
        "truth_copy_max_error": truth_copy_error,
        "saved_mean_flux_Jy": float(mean.sum()),
        "mean_flux_error_vs_truth": float(abs(mean.sum() / truth.sum() - 1)),
        "mean_flux_error_vs_retained_prior_target": float(
            abs(mean.sum() / parity["flux_const"] - 1)
        ),
        "quoted_source_metrics": quoted,
        "sample_sets": sample_sets,
        "zero_std_control": ns["compute_uq_metrics"](mean, np.zeros_like(std), truth),
        "one_Jy_std_control": ns["compute_uq_metrics"](mean, np.ones_like(std), truth),
        "scope": "One-image pixel containment is descriptive, not frequentist calibration or confirmation of a Gaussian posterior. No samples generated and no t-SNE or clustering fitted.",
    }
    assert uq["within_one_std_pixels"] == 180 and uq["pixel_count"] == 1024
    # Use only the verified read-only scoring module; inject the relative import
    # for selected dispatch methods instead of importing runners or authoring code.
    harness = source / "evaluation_harness"
    spec = importlib.util.spec_from_file_location(
        "eht_reference_scoring", harness / "reference_scoring.py"
    )
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)

    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "" and level == 1 and fromlist == ("reference_scoring",):
            return SimpleNamespace(reference_scoring=ref)
        return builtins.__import__(name, globals, locals, fromlist, level)

    scorer_ns = {
        "Path": Path,
        "log": logging.getLogger("eht-audit"),
        "__builtins__": {**vars(builtins), "__import__": source_import},
    }
    selections["scorer"] = selected(
        harness / "scorer.py",
        ["_compute_quality_metrics", "_compute_quality_metrics_generic"],
        scorer_ns,
        "Scorer",
    )
    generic = {}
    for name, a in {
        "saved_mean": mean,
        "oracle_truth": truth,
        "zeros": np.zeros_like(mean),
        "ten_times_mean": mean * 10,
        "sample_stack": saved["posterior_samples"],
    }.items():
        dest = out / "scoring" / name / "output"
        dest.mkdir(parents=True)
        np.save(dest / "reconstruction.npy", a)
        driver = SimpleNamespace(
            config=SimpleNamespace(task=SimpleNamespace(task_dir=task)),
            runner=SimpleNamespace(container=str(dest.parent)),
        )
        generic[name] = scorer_ns["_compute_quality_metrics"](driver)
    assert generic["oracle_truth"]["nrmse"] == 0
    assert "error" in generic["sample_stack"]
    assert generic["saved_mean"]["passed"] is None
    assert all(v is None for v in generic["saved_mean"]["boundaries"].values())
    # Identical mean with absent, zero, and exaggerated std has identical scores.
    dest = out / "scoring/saved_mean/output"
    for name, a in {"zero_std": np.zeros_like(std), "one_Jy_std": np.ones_like(std)}.items():
        np.save(dest / "posterior_std.npy", a)
        generic[name] = ref.score_reconstruction(task, dest.parent)
        assert generic[name] == {k: v for k, v in generic["saved_mean"].items() if k != "scorer"}
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
    native_recipe = task_ns["_recipe_generic"](
        TASK, task.resolve(), ref_dir.resolve(), SimpleNamespace(**ns)
    )
    assert native_recipe == {k: native[k] for k in ["ncc", "nrmse"]}
    # Copy actual L1-L3 seed paths, intercept all commands (no install or process).
    stage_ns = {"Path": Path, "shutil": shutil, "log": logging.getLogger("eht-audit")}
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
        for name in ["ground_truth.npz", "gt.fits", "obs.uvfits", "raw_data.npz"]:
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
    assert len(defects) == 1 and defects[0]["line"] == 24
    assert "obs" not in raw
    solver = ast.parse((task / "src/solvers.py").read_text())
    accesses = [
        n.lineno
        for n in ast.walk(solver)
        if isinstance(n, ast.Subscript)
        and isinstance(n.value, ast.Name)
        and n.value.id == "obs_data"
        and isinstance(n.slice, ast.Constant)
        and n.slice.value == "obs"
    ]
    assert len(accesses) == 1
    defects.append(
        {
            "path": "src/solvers.py",
            "line": accesses[0],
            "error": f"DPISolver.reconstruct requires obs_data['obs'], absent from the current loader's {len(raw)} numeric/string array keys. Static contract proof; reconstruct not executed.",
        }
    )
    notebook = json.loads((task / "notebooks/eht_black_hole_UQ.ipynb").read_text())
    notebook_outputs = {
        str(i): ["".join(o["text"]) for o in c.get("outputs", []) if "text" in o]
        for i, c in enumerate(notebook["cells"])
        if any("text" in o for o in c.get("outputs", []))
    }
    report = {
        "schema": 1,
        "entry_id": "imaging101-eht-black-hole-uq",
        "date": "2026-09-29",
        "reviewer": "assistant",
        "source_commit": COMMIT,
        "asset_revision": REVISION,
        "script_sha256": sha(Path(__file__)),
        "helper_script_sha256": sha(
            Path(__file__).with_name("audit_imaging101_poisson_lowdose.py")
        ),
        "verified_sources": verified,
        "verified_assets": assets,
        "omitted_checkpoints": omitted,
        "asset_listing_receipt": listing,
        "upstream_dpi_commit": upstream_commit,
        "upstream_byte_identical_fits": origins,
        "verified_upstream_sources": upstream,
        "pinned_paper": {
            "url": "https://arxiv.org/html/2010.14462v2",
            "scope": "Paper separates synthetic Sgr A* examples from real EHT 2017 M87 data; the task README's real-2015 claim is not established by FITS metadata alone.",
        },
        "fits_headers": {n: fits_header(task / "data" / n) for n in ["gt.fits", "obs.uvfits"]},
        "metadata": meta,
        "raw_array_shapes_and_dtypes": {
            k: {"shape": list(a.shape), "dtype": str(a.dtype)} for k, a in raw.items()
        },
        "observation_counts": {
            "visibilities": len(raw["vis"]),
            "closure_phases": len(cp),
            "log_closure_amplitudes": len(ca),
            "stations": len(stations),
            "timestamps": len(np.unique(raw["times"])),
        },
        "units": {
            "visibility": "Jy",
            "image": "Jy/pixel",
            "uv": "wavelengths",
            "phase": "degrees",
            "log_closure_amplitude": "dimensionless natural logarithm",
            "pixel_size": "5 microarcseconds",
            "orientation": "source plot uses origin lower, relative RA decreases left-to-right; Dec increases bottom-to-top",
        },
        "preprocessing_fixture_replay": preprocessing,
        "raw_closure_replay": raw_replay,
        "station_gain_control": gain_control,
        "loss_fixture_max_errors": loss_checks,
        "metric_fixture_max_errors": metric_checks,
        "posterior_replay": uq,
        "generic_dispatch_replay": generic,
        "task_recipe_replay": native_recipe,
        "staging": staging,
        "source_defects": defects,
        "historical_notebook_outputs": notebook_outputs,
        "selected_pure_functions": selections,
        "scope_limits": [
            "No network training, checkpoint deserialization, posterior generation, optimizer, clustering, agent trial, upstream generator or installation.",
            "torchkbnufft is unavailable in the existing runtime; NUFFT forward fixtures and historical closure residuals were not replayed. Pure losses and preprocessing were replayed with existing CPU torch.",
            "loss_history.npy is an object array and was not deserialized. Both .pt checkpoints and the task PDF are inventoried but not downloaded.",
            "The README writes log-amplitude denominator V13*V24; source indices implement V14*V23 for the supplied station order. All 485 stored values reproduce the implemented convention.",
            "The stored mean and std derive exactly from posterior_samples.npy (1024 images); posterior_samples_1024.npy is a different set and must not be silently substituted.",
            "Source preprocessing changed prior flux versus retained fixtures. Its Fourier pulse matches retained fixtures, while generate_fixtures_safe.py omits the phase factor. Saved outputs are historical artifacts, not proof the pinned main script can regenerate them.",
            "The live generic scorer checks one image, ignores uncertainty, and has no published evaluation/metrics.json thresholds. Its metrics differ from the task-native helper.",
            "One supplied reference and spatial containment do not establish a calibrated astrophysical posterior; two clusters in a chosen t-SNE embedding are not independently verified physical modes.",
            "Real-observation provenance remains unresolved; FITS header labels alone cannot establish it.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(json_safe(report), indent=2, allow_nan=False) + "\n")
    np.savez_compressed(
        out / "derived.npz",
        current_prior=prior,
        retained_prior=parity["prior_image"],
        closure_phase_from_vis=cp,
        log_closure_amplitude_from_vis=ca,
        gain_control_vis=corrupted,
    )
    print(
        json.dumps(
            {
                "verified_sources": len(verified),
                "verified_assets": len(assets),
                "native_metrics": native,
                "generic_saved_mean": generic["saved_mean"],
                "preprocessing": preprocessing,
                "audit_sha256": sha(out / "audit.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
