"""Build pinned closure/posterior teaching views; no training or observation generation."""

from __future__ import annotations

import argparse
import base64
import io
import json
from itertools import combinations
from pathlib import Path

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, selected, sha
from PIL import Image


def combine_closure(values, signs, phase):
    total = np.dot(signs, values if phase else np.log(values))
    return float((total + 180) % 360 - 180) if phase else float(total)


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def plane(a, bounds=(0.0, 0.0022), palette="heat"):
    assert a.shape == (64, 64) and np.isfinite(a).all()
    lo, hi = bounds
    assert a.min() >= lo and a.max() <= hi
    colors = np.array(
        [(0, 0, 0), (110, 0, 0), (230, 65, 0), (255, 215, 55), (255, 255, 230)]
        if palette == "heat"
        else [(68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)]
    )
    lut = (
        np.column_stack(
            [
                np.interp(np.arange(256), np.linspace(0, 255, len(colors)), colors[:, c])
                for c in range(3)
            ]
        )
        .round()
        .astype(np.uint8)
    )
    image = Image.fromarray(lut[np.rint((a - lo) / (hi - lo) * 255).astype(np.uint8)])
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": [64, 64],
        "range": list(bounds),
        "palette": palette,
        "unit": "Fraction of total flux / pixel",
        "row_zero": "top",
        "column_zero": "left",
        "pixel_size_uas": 1.875,
        "source_min": float(a.min()),
        "source_max": float(a.max()),
        "quantization_max_abs_error": (hi - lo) / 510,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path(
        "presentation/external-tasks/sources/imaging101-eht-features-dynamic-audit.json"
    )
    record = json.loads(record_path.read_text())
    for row in record["verified_sources"] + record["verified_assets"]:
        assert sha(args.sources / row["path"]) == row["sha256"]
    assert sha(Path("scripts/audit_imaging101_eht_features_dynamic.py")) == record["script_sha256"]
    task = args.sources / "tasks/eht_black_hole_feature_extraction_dynamic"
    raw = arrays(task / "data/raw_data.npz")
    gt = arrays(task / "data/ground_truth.npz")
    refdir = task / "evaluation/reference_outputs"
    params = np.load(refdir / "all_params.npy", allow_pickle=False)
    weights = np.load(refdir / "all_weights.npy", allow_pickle=False).astype(float)
    images = np.load(refdir / "all_images.npy", allow_pickle=False)
    weights /= weights.sum(axis=1)[:, None]
    assert params.shape == (10, 10000, 4) and images.shape == (10, 64, 64)
    namespace = {"np": np, "combinations": combinations}
    selected(
        task / "src/preprocessing.py",
        ["load_frame_data", "_find_triangles", "_find_quadrangles", "extract_closure_indices"],
        namespace,
    )
    selected(task / "src/generate_data.py", ["generate_simple_crescent_image"], namespace)
    # These eight fixed parameter examples illustrate the declared model; they
    # do not use ground truth, optimize a fit or simulate observations.
    model_controls = []
    controls = [
        ("Ring-center diameter", "μas", [30, 70], [30, 10, 0.6, -90], [70, 10, 0.6, -90]),
        ("Gaussian width sigma", "μas", [4, 20], [50, 4, 0.6, -90], [50, 20, 0.6, -90]),
        ("Brightness asymmetry", "unitless", [0, 0.9], [50, 10, 0, -90], [50, 10, 0.9, -90]),
        ("Source angle", "degrees", [-135, -45], [50, 10, 0.6, -135], [50, 10, 0.6, -45]),
    ]
    for label, unit, values, first, last in controls:
        model_controls.append(
            {
                "label": label,
                "unit": unit,
                "values": values,
                "parameters": [first, last],
                "images": [
                    plane(namespace["generate_simple_crescent_image"](64, 120, *p), (0, 0.0045))
                    for p in [first, last]
                ],
            }
        )
    closure_controls = []
    gains = np.linspace(0.8, 1.2, 8) * np.exp(1j * np.linspace(-0.5, 0.7, 8))
    for kind, stations in [("phase", [0, 4, 7]), ("amplitude", [0, 3, 4, 7])]:
        for epoch in [0, 4, 9]:
            frame = namespace["load_frame_data"](raw, epoch)
            ids = frame["station_ids"]
            lookup = {tuple(pair): i for i, pair in enumerate(ids)}
            altered = frame["vis"] * gains[ids[:, 0]] * np.conj(gains[ids[:, 1]])
            if kind == "phase":
                a, b, c = stations
                pairs, signs = [(a, b), (b, c), (a, c)], [1, 1, -1]
                before = [float(np.degrees(np.angle(frame["vis"][lookup[p]]))) for p in pairs]
                after = [float(np.degrees(np.angle(altered[lookup[p]]))) for p in pairs]
            else:
                a, b, c, d = stations
                pairs, signs = [(a, b), (c, d), (a, c), (b, d)], [1, 1, -1, -1]
                before = [float(abs(frame["vis"][lookup[p]])) for p in pairs]
                after = [float(abs(altered[lookup[p]])) for p in pairs]
            first = combine_closure(before, signs, kind == "phase")
            last = combine_closure(after, signs, kind == "phase")
            assert abs(first - last) < 1e-10
            closure_controls.append(
                {
                    "kind": kind,
                    "epoch": epoch,
                    "stations": stations,
                    "pairs": pairs,
                    "signs": signs,
                    "before": before,
                    "after": after,
                    "combined_before": first,
                    "combined_after": last,
                    "baseline_indices": [lookup[p] for p in pairs],
                }
            )
    inputs = {
        "times_hours": raw["frame_times"].tolist(),
        "station_names": record["metadata"]["station_names"],
        "frames": [
            {
                "uv_Glambda": (raw[f"uv_{i}"] / 1e9).tolist(),
                "vis_real_Jy": raw[f"vis_{i}"].real.tolist(),
                "vis_imaginary_Jy": raw[f"vis_{i}"].imag.tolist(),
                "sigma_complex_RMS_Jy": raw[f"sigma_{i}"].tolist(),
                "station_pairs": raw[f"station_ids_{i}"].tolist(),
            }
            for i in range(10)
        ],
        "closure_controls": closure_controls,
        "model_controls": model_controls,
        "metadata": record["metadata"],
        "closure_counts": [56, 70],
        "closure_ranks": [21, 19],
        "gain_amplitudes": np.abs(gains).tolist(),
        "gain_phases_rad": np.angle(gains).tolist(),
    }
    # Common fixed bins cover every retained sample, with no trimming or KDE.
    bounds = [[38, 49], [6, 10], [0.3, 1], [-145, -40]]
    histograms = []
    for j, limits in enumerate(bounds):
        edges = np.linspace(*limits, 61)
        mass = [np.histogram(params[i, :, j], bins=edges, weights=weights[i])[0] for i in range(10)]
        assert np.allclose(np.sum(mass, axis=1), 1, atol=1e-12)
        histograms.append(
            {
                "edges": edges.tolist(),
                "centers": ((edges[:-1] + edges[1:]) / 2).tolist(),
                "mass": np.array(mass).tolist(),
                "bin_width": float(edges[1] - edges[0]),
                "range": limits,
            }
        )
    contract = {
        "images": [plane(a) for a in images],
        "histograms": histograms,
        "means": record["native_metrics"]["posterior_means"],
        "stds": record["native_metrics"]["posterior_stds"],
        "ess": record["effective_sample_sizes"],
        "max_weight": record["maximum_normalized_weight"],
        "saved_image_sums": record["stored_image_flux"],
        "intervals": record["central_68_percent_intervals"],
        "samples_per_frame": 10000,
        "likelihood_ratio": 70,
        "parameter_labels": [
            "Ring-center diameter",
            "Gaussian width sigma",
            "Brightness asymmetry",
            "Source angle",
        ],
        "parameter_units": ["μas", "μas", "unitless", "degrees"],
    }
    error = abs(gt["images"] - images)
    error_top = float(np.ceil(error.max() * 1e5) / 1e5)
    reference = {
        "truth": [plane(a) for a in gt["images"]],
        "error": [plane(a, (0, error_top), "error") for a in error],
        "parameters": np.column_stack(
            [gt[k] for k in ["diameter_uas", "width_uas", "asymmetry", "position_angle_deg"]]
        ).tolist(),
        "biases": record["native_metrics"]["biases"],
        "native": record["native_metrics"],
        "generic": record["generic_dispatch"]["saved_images"],
        "oracle_point": record["linear_summary_controls"]["oracle_collapsed_at_truth"],
        "angle_wrap": record["angle_wrap_control"],
        "truth_in_intervals": record["truth_inside_intervals_per_parameter"],
    }
    args.output.mkdir(parents=True, exist_ok=False)
    for name, value in [("inputs", inputs), ("contract", contract), ("reference", reference)]:
        write(args.output / f"{name}.json", value)
    (args.output / "BENCHMARK-LICENSE.txt").write_bytes((args.sources / "LICENSE").read_bytes())
    (args.output / "DATA-LICENSE.txt").write_text("""Source attribution

Imaging-101 Authors 2026; MIT benchmark notice in BENCHMARK-LICENSE.txt.
Synthetic task arrays: starpacker52/imaging-101 at the revision in NOTICE.md.
Task attribution: Sun et al. 2022, ApJ 932:99 (alpha-DPI), and EHT Collaboration 2022,
ApJL 930:L15 (time-resolved feature displays). No original paper figure, telescope
photograph, upstream algorithm code or trained model is redistributed here.
These local explanatory derivatives do not establish an independent license
grant for third-party material or constitute publication.
""")
    (args.output / "NOTICE.md").write_text("""# Dynamic crescent feature views

Benchmark `dc2f668939b21e8312e22529615def610f8611df`; data revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3`. The
[source audit](../../external-tasks/sources/imaging101-eht-features-dynamic-audit.json)
pins 74 source files and all 9 assets, original scores and staging evidence.

Rebuild with scripts/build_imaging101_eht_features_dynamic_assets.py using
--sources and a fresh --output directory in the existing NumPy/Pillow runtime.
No source-module initialization, random sampling, solver, training or installation.

All 10 native 64x64 frames and original 10000 weights per epoch are retained through
full-support weighted histograms. Observations run 0..7.2 hours at 0.8-hour steps;
playback time is separate. This synthetic crescent is not real Sgr A* data.

Images retain the full grid without cropping or spatial resampling. Row 0 is at
the top and column 0 at the left: explicit array coordinates, not celestial axes.
Pixel size 1.875 microarcseconds, full field 120 microarcseconds. The source's
angle formula uses atan2(grid_y,grid_x); no independent E-of-N calibration is
claimed. Ring diameter means twice the Gaussian radial center, width means sigma.

Saved and truth images share 0..0.0022 fraction-of-total-flux per pixel. They sum
to approximately 1, although metadata's visibility generator uses 0.6 Jy. Absolute
error uses a separate labeled bound rounded upward to 0.00001. Eight fixed model
examples use a separate 0..0.0045 scale. Quantization is 8-bit with explicit RGB
interpolation and maximum errors in each plane record. No image smoothing.

Input views use 28 native UV samples and both complex visibility components.
The 6 fixed closure controls choose stations [0,4,7] for phases and[0,3,4,7] for
amplitudes at frames 0, 4, 9. Station gains are deterministic audit controls:
amplitudes linearly 0.8..1.2 and phases -0.5..0.7 radians. They change individual
visibilities but cancel in wrapped phases and log ratios. No noise is redrawn.
Source 56 phase combinations have linear rank 21; 70 amplitude combinations rank 19.
These are correlated expressions, not 126 independent observations.

Model examples use fixed values unrelated to truth: diameter 30/70, width 4/20,
asymmetry 0/0.9 and angle -135/-45; other parameters are fixed and recorded.
They illustrate the supplied formula, not a fit or measured intermediate state.
Each actual source frame initializes an independent flow; there is no temporal
coupling. Flow/training diagrams remain conceptual.

Each parameter uses 60 fixed bins covering every saved sample and its original
normalized weight. Ridge height is normalized independently for legibility;
bin width is shown. No KDE, trimming, new samples or posterior fitting. Weighted
means and standard deviations preserve original precision within float32
roundoff. ESS is 1/sum(w^2), not a count of independent experimental cases.

Truth, errors, parameter biases, scoring values and oracle examples live in
reference.json and appear only in explicit reference/diagnostics/scoring scenes.
The reference scene stays hidden until its midpoint. Actual L1-L3 expose both
ground_truth.npz and answer-bearing meta_data: this is reading order, not privacy.

Native angle error is 6.08 degrees; generic image NCC/NRMSE is 0.996218/0.022811.
Generic dispatch rejects the native posterior shape and has no pass boundaries.
Oracle point distributions use answers; zero bias with zero spread does not
validate uncertainty. The fixed [-179,179] wrap example is not present in the saved
angle range. Ten snapshots do not establish uncertainty calibration.

The pinned source weights likelihood 70 times more during training than importance
reweighting, relative to its log-density term. Latents/checkpoints are missing;
do not infer corrected outcomes. Source design mentions UVFITS but release uses
NPZ. The no-filesystem fallback requires an absent NPY reference. No new agent
pass, NUFFT equivalence, runtime recovery or population claim is established.
""")
    names = [
        "inputs.json",
        "contract.json",
        "reference.json",
        "NOTICE.md",
        "DATA-LICENSE.txt",
        "BENCHMARK-LICENSE.txt",
    ]
    write(
        args.output / "manifest.json",
        {
            "id": "retained-imaging101-eht-features-dynamic-v1",
            "frame": "source-record",
            "units": "fraction/pixel",
            "license": "LicenseRef-Imaging101-EHT-feature-sources",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(record_path): sha(record_path),
                "scripts/build_imaging101_eht_features_dynamic_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_grid": [64, 64],
                "frames": 10,
                "samples_per_frame": 10000,
                "baselines_per_frame": 28,
                "histogram_bins": 60,
                "full_histogram_mass": True,
                "closure_controls": 6,
                "model_examples": 8,
                "model_runs": 0,
                "cropped": False,
            },
            "assets": [
                {
                    "file": n,
                    "sha256": sha(args.output / n),
                    "bytes": (args.output / n).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal" if n == "reference.json" else "illustration",
                }
                for n in names
            ],
        },
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "error_top": error_top,
                "files": {n: (args.output / n).stat().st_size for n in names},
            }
        )
    )


if __name__ == "__main__":
    main()
