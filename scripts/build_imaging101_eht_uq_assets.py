"""Build EHT teaching views from pinned arrays; no training or new sampling."""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, sha
from PIL import Image

PALETTES = {
    "heat": [(0, 0, 0), (110, 0, 0), (230, 65, 0), (255, 215, 55), (255, 255, 230)],
    "spread": [(68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)],
    "binary": [(250, 248, 252), (128, 82, 161)],
}


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def plane(values, maximum, palette="heat", unit="Jy/pixel"):
    a = np.asarray(values, dtype=float)
    assert a.shape == (32, 32) and np.isfinite(a).all()
    assert a.min() >= 0 and a.max() <= maximum
    quantized = np.rint(a / maximum * 255).astype(np.uint8)
    colors = np.array(PALETTES[palette])
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
    # PNG rows go down; source plots use origin='lower'. RA reversal is an
    # axis-label convention, not a horizontal flip of the underlying image.
    image = Image.fromarray(lut[quantized[::-1]])
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": [32, 32],
        "range": [0, maximum],
        "unit": unit,
        "palette": palette,
        "source_max": float(a.max()),
        "source_min": float(a.min()),
        "quantization_max_abs_error": maximum / 510,
        "row_zero": "bottom",
        "RA_left_to_right_uas": [80, -80],
        "Dec_bottom_to_top_uas": [-80, 80],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-eht-uq-audit.json")
    record = json.loads(record_path.read_text())
    for row in record["verified_sources"] + record["verified_assets"]:
        assert sha(args.sources / row["path"]) == row["sha256"]
    assert sha(Path("scripts/audit_imaging101_eht_uq.py")) == record["script_sha256"]
    task = args.sources / "tasks/eht_black_hole_UQ"
    raw = arrays(task / "data/raw_data.npz")
    truth = arrays(task / "data/ground_truth.npz")["image"]
    fixtures = arrays(task / "evaluation/fixtures/parity/orig_preproc.npz")
    refdir = task / "evaluation/reference_outputs"
    samples = np.load(refdir / "posterior_samples.npy", allow_pickle=False)
    mean = np.load(refdir / "posterior_mean.npy", allow_pickle=False)
    std = np.load(refdir / "posterior_std.npy", allow_pickle=False)
    assert np.array_equal(mean, samples.mean(0)) and np.array_equal(std, samples.std(0))
    selection = list(range(8))
    top = float(
        np.ceil(max(samples[selection].max(), truth.max(), fixtures["prior_image"].max()) * 100)
        / 100
    )
    assert top > 0
    current_flux = record["preprocessing_fixture_replay"]["current_median_all_visibility_flux_Jy"]
    retained_flux = float(fixtures["flux_const"])
    # Independently evaluate the documented Gaussian formula only; no task import.
    coords = (np.arange(32) - 15.5) * 5
    xx, yy = np.meshgrid(coords, coords)
    width = 50 / (2 * np.sqrt(2 * np.log(2)))
    main = np.exp(-(xx**2 + yy**2) / (2 * width**2))
    floor = np.exp(-((xx - 50) ** 2 + (yy - 50) ** 2) / (2 * width**2))
    current_prior = current_flux * (main / main.sum() + 1e-6 * floor / floor.sum())
    assert abs(current_prior.sum() - current_flux * (1 + 1e-6)) < 1e-14
    gains = record["station_gain_control"]["station_gains"]
    witnesses = {}
    # First source closure row of each kind: a deterministic choice, no search.
    for kind, stations, baselines, signs in [
        (
            "phase",
            [raw[f"cp_t{i}"][0].decode() for i in [1, 2, 3]],
            [(0, 1), (1, 2), (2, 0)],
            [1, 1, 1],
        ),
        (
            "amplitude",
            [raw[f"lca_t{i}"][0].decode() for i in [1, 2, 3, 4]],
            [(0, 1), (2, 3), (0, 3), (1, 2)],
            [1, 1, -1, -1],
        ),
    ]:
        edges = []
        for j, (a, b) in enumerate(baselines):
            if kind == "phase":
                index = int(fixtures[f"cp_ind{j}"][0])
                sign = float(fixtures[f"cp_sign{j}"][0])
                vis = raw["vis"][index] if sign == 1 else raw["vis"][index].conjugate()
                assert (
                    (raw["t1"][index].decode(), raw["t2"][index].decode())
                    if sign == 1
                    else (raw["t2"][index].decode(), raw["t1"][index].decode())
                ) == (stations[a], stations[b])
            else:
                index = int(fixtures[f"ca_ind{j}"][0])
                vis = raw["vis"][index]
                pair = (raw["t1"][index].decode(), raw["t2"][index].decode())
                assert set(pair) == {stations[a], stations[b]}
                if pair != (stations[a], stations[b]):
                    vis = vis.conjugate()
            edges.append(
                {
                    "from": a,
                    "to": b,
                    "visibility_index": index,
                    "vis": [float(vis.real), float(vis.imag)],
                    "weight": signs[j],
                }
            )
        values = [complex(*e["vis"]) for e in edges]
        expected = float(raw["cp_values_deg"][0] if kind == "phase" else raw["lca_values"][0])
        got = (
            np.angle(np.prod(values), deg=True)
            if kind == "phase"
            else sum(w * np.log(abs(v)) for w, v in zip(signs, values, strict=True))
        )
        error = (got - expected + 180) % 360 - 180 if kind == "phase" else got - expected
        assert abs(error) < 1e-10
        witnesses[kind] = {
            "source_row": 0,
            "stations": stations,
            "gains": [gains[s] for s in stations],
            "edges": edges,
            "observed": expected,
        }
    unique_times, time_ids = np.unique(raw["times"], return_inverse=True)
    inputs = {
        "uv_Glambda": (raw["uv_coords"] / 1e9).tolist(),
        "time_ids": time_ids.tolist(),
        "times": unique_times.tolist(),
        "phase_deg": raw["cp_values_deg"].tolist(),
        "phase_sigma_deg": raw["cp_sigmas_deg"].tolist(),
        "log_amplitude": raw["lca_values"].tolist(),
        "log_amplitude_sigma": raw["lca_sigmas"].tolist(),
        "witnesses": witnesses,
        "counts": record["observation_counts"],
        "metadata": record["metadata"],
        "current_prior": plane(current_prior, top),
        "retained_prior": plane(fixtures["prior_image"], top),
        "current_flux": current_flux,
        "retained_flux": retained_flux,
    }
    error = abs(truth - mean)
    pixel = (15, 20)  # Fixed central-grid point, independent of reference values.
    contract = {
        "samples": [
            {"source_row": i, "image": plane(samples[i], top), "flux": float(samples[i].sum())}
            for i in selection
        ],
        "mean": plane(mean, top),
        "std": plane(std, float(np.ceil(std.max() * 1000) / 1000), "spread"),
        "sample_count": len(samples),
        "sample_file": "posterior_samples.npy",
        "pixel": {
            "row": pixel[0],
            "column": pixel[1],
            "values": samples[:, pixel[0], pixel[1]].tolist(),
            "mean": float(mean[pixel]),
            "std": float(std[pixel]),
        },
        "native_metrics": record["posterior_replay"]["native_saved_map_metrics"],
        "generic_metrics": record["generic_dispatch_replay"],
        "staging": {k: v["available_files_copied"] for k, v in record["staging"].items()},
        "source_defects": record["source_defects"],
        "alternate_samples": record["posterior_replay"]["sample_sets"]["posterior_samples_1024"],
        "thresholds_available": False,
        "solver_visible_all_levels": True,
    }
    reference = {
        "image": plane(truth, top),
        "error": plane(error, float(np.ceil(error.max() * 1000) / 1000), "spread"),
        "containment": plane(error <= std, 1, "binary", "within ±1 std"),
        "within_std": int((error <= std).sum()),
        "total_pixels": 1024,
        "pixel_truth": float(truth[pixel]),
        "reference_flux": float(truth.sum()),
    }
    args.output.mkdir(parents=True, exist_ok=False)
    for name, value in [("inputs", inputs), ("contract", contract), ("reference", reference)]:
        write(args.output / f"{name}.json", value)
    (args.output / "BENCHMARK-LICENSE.txt").write_bytes((args.sources / "LICENSE").read_bytes())
    (args.output / "DATA-LICENSE.txt").write_text("""Source attribution and scope

Imaging-101 Authors, AI4ImagingLab/imaging-101-release, MIT license retained
in BENCHMARK-LICENSE.txt. Arrays from starpacker52/imaging-101 at the revision
in NOTICE.md. Original DPI: He Sun and Katherine L. Bouman, Deep Probabilistic
Imaging, arXiv:2010.14462v2, https://github.com/HeSunPU/DPI.

Original FITS files match DPI dataset/interferometry1 byte for byte. The inspected
DPI tree has no standalone license file. Benchmark MIT licensing is not treated
as a verified redistribution grant for every upstream scientific asset. This is
a local explanatory derivative with retained provenance, not website publication.
No paper figure, photograph of a telescope or model checkpoint is copied.
""")
    (args.output / "NOTICE.md").write_text("""# EHT uncertainty source views

Benchmark `dc2f668939b21e8312e22529615def610f8611df`, asset revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3`, upstream DPI
`1bf3f02a92796af737bd6fe6233d1d0dd778ffd5`. The
[source audit](../../external-tasks/sources/imaging101-eht-uq-audit.json) records
identities, source defects, arithmetic controls and evaluator boundaries.

Rebuild with the existing NumPy/Pillow environment and the builder's --sources
and fresh --output paths. No dependency installation, learned-network sampling,
training, NUFFT forward model or new scientific trial runs in the builder/player.

All image panels keep the complete 32x32 grid at 5 microarcseconds per pixel.
PNG rows are flipped vertically to reproduce source origin=lower; relative RA
falls from +80 to -80 left-to-right and Dec rises from -80 to +80 bottom-to-top.
There is no horizontal array flip, crop or spatial resampling. Images are colored
from 8-bit quantized values; each record stores its range and error bound. The
heat and spread palettes are explicitly interpolated RGB colors, not scientific
measurements. Sample, mean, reference and helper images share one scale covering
all displayed values. Standard deviation and error each use their labeled full
range rounded upward to 0.001 Jy/pixel. No values are clipped.

Eight saved samples are original rows 0..7 in posterior_samples.npy. All 1024
rows produce the retained mean/std exactly. The alternative file ending _1024
contains different samples and is never substituted. The pixel trace uses all
1024 values at fixed row15,column20 and population std, without a normality
assumption, score-based selection, latent values or new sample generation.

Native u/v data use G wavelengths and one common axis scale. Orange conjugate
points are derived symmetry, not extra measurements. The first closure row of
each kind determines the triangle/quadrangle witnesses. Their node positions
are schematic, not geographic. Edges are conjugated into the stated direction.
Gain control g(t)=abs(g)^t exp(i*t*arg(g)) is a deterministic arithmetic example
with Vab(t)=ga(t)*conj(gb(t))*Vab. It preserves closure quantities while changing
individual visibilities; it does not remove thermal noise. Log-amplitude pairing
follows source indices V12*V34/(V14*V23), unlike the README's denominator order.

Current Gaussian prior uses the all-baseline median flux, 0.2738309775 Jy.
Retained prior uses APEX-ALMA, 2.0444813540 Jy; keep both labeled. The flow diagram
explains the source procedure only, not a retained latent-to-sample correspondence.

Truth, absolute error, containment and the pixel reference value live in
reference.json and mount only after the explicit reader reveal. Actual L1-L3
seed both truth files, so this reveal is not solver privacy. Neither generic
single-image scoring nor the task-native mean score measures uncertainty.
Spatial containment for this one reference does not prove calibration. Native
and generic metric definitions differ and no current pass thresholds are supplied.

The real-2015-observation claim is unresolved; call this the bundled DPI example.
The source main.py syntax error, obsolete obs object and changed prior prevent
using saved outputs as proof of source reproducibility. Preserve original scores.
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
            "id": "retained-imaging101-eht-uq-v1",
            "frame": "source-record",
            "units": "Jy/pixel",
            "license": "LicenseRef-Imaging101-DPI-sources",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(record_path): sha(record_path),
                "scripts/build_imaging101_eht_uq_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_grid": [32, 32],
                "displayed_sample_rows": selection,
                "posterior_count": len(samples),
                "mean_std_exact": True,
                "closure_phase_rows": 465,
                "log_amplitude_rows": 485,
                "visibilities": 938,
                "reference_containment_pixels": 180,
                "pixel_probe": list(pixel),
                "model_runs": 0,
                "runtime_sampling": 0,
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
                "shared_brightness_max": top,
                "files": {n: (args.output / n).stat().st_size for n in names},
            }
        )
    )


if __name__ == "__main__":
    main()
