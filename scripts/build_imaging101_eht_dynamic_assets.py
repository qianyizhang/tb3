"""Build native dynamic EHT views from pinned arrays; no reconstruction."""

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
    "error": [(68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)],
    "signed": [(40, 82, 140), (248, 248, 240), (174, 64, 30)],
}


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def plane(a, bounds=(0.0, 0.075), palette="heat", unit="Jy/pixel"):
    assert a.shape == (30, 30) and np.isfinite(a).all()
    lo, hi = bounds
    assert a.min() >= lo and a.max() <= hi
    quantized = np.rint((a - lo) / (hi - lo) * 255).astype(np.uint8)
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
    # Source plots use origin lower; source DFT coordinates decrease along
    # BOTH array axes. Do not borrow celestial labels from the UQ example.
    image = Image.fromarray(lut[quantized[::-1]])
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": [30, 30],
        "range": list(bounds),
        "unit": unit,
        "palette": palette,
        "source_min": float(a.min()),
        "source_max": float(a.max()),
        "quantization_max_abs_error": (hi - lo) / 510,
        "row_zero": "bottom",
        "column_zero": "left",
        "pixel_size_uas": 3.4,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-eht-dynamic-audit.json")
    record = json.loads(record_path.read_text())
    for row in record["verified_sources"] + record["verified_assets"]:
        assert sha(args.sources / row["path"]) == row["sha256"]
    assert sha(Path("scripts/audit_imaging101_eht_dynamic.py")) == record["script_sha256"]
    task = args.sources / "tasks/eht_black_hole_dynamic"
    raw = arrays(task / "data/raw_data.npz")
    gt = arrays(task / "data/ground_truth.npz")["images"]
    saved = {
        k: np.load(
            task / "evaluation/reference_outputs" / (k + "_reconstruction.npy"), allow_pickle=False
        )
        for k in ["static", "starwarps"]
    }
    assert gt.shape == (12, 30, 30)
    selected_rows = [0, 8, 16, 27]
    coords = (14.5 - np.arange(30)) * record["metadata"]["pixel_size_rad"]
    xx, yy = np.meshgrid(coords, coords)
    kernels = []
    for row in selected_rows:
        u, v = raw["uv_0"][row]
        kernel = np.exp(-2j * np.pi * (u * xx + v * yy))
        kernels.append(
            {
                "frame": 0,
                "baseline": row,
                "station_pair": raw["station_ids_0"][row].tolist(),
                "uv_Glambda": [float(u / 1e9), float(v / 1e9)],
                "real": plane(kernel.real, (-1.0, 1.0), "signed", "DFT weight"),
                "imaginary": plane(kernel.imag, (-1.0, 1.0), "signed", "DFT weight"),
            }
        )
    # Evaluate only the documented prior formula, not any task authoring module.
    p = (np.arange(30) - 14.5) * 3.4
    px, py = np.meshgrid(p, p)
    width = 50 / (2 * np.log(2) ** (1 / 6))
    prior = np.exp(-((np.hypot(px, py) / width) ** 6))
    prior = np.maximum(prior, 0.05 * prior.max())
    prior *= 2 / prior.sum()
    assert abs(prior.sum() - 2) < 1e-14
    inputs = {
        "times_hours": raw["frame_times"].tolist(),
        "frames": [
            {
                "uv_Glambda": (raw[f"uv_{t}"] / 1e9).tolist(),
                "vis_real_Jy": raw[f"vis_{t}"].real.tolist(),
                "vis_imaginary_Jy": raw[f"vis_{t}"].imag.tolist(),
                "sigma_complex_RMS_Jy": raw[f"sigma_{t}"].tolist(),
                "station_pairs": raw[f"station_ids_{t}"].tolist(),
            }
            for t in range(12)
        ],
        "station_names": record["metadata"]["station_names"],
        "kernels": kernels,
        "prior": plane(prior),
        "metadata": record["metadata"],
        "prior_flux_Jy": float(prior.sum()),
    }
    contract = {
        "videos": {name: [plane(frame) for frame in video] for name, video in saved.items()},
        "metrics": {
            name: record["native_video_metric_replay"][name]
            for name in ["starwarps", "static_per_frame"]
        },
        "diagnostics": {
            name: record["temporal_diagnostics"][name] for name in ["starwarps", "static_per_frame"]
        },
        "generic_starwarps": record["generic_dispatch_replay"]["starwarps"],
        "historical_recipe": record["task_recipe_replay"],
        "staging": {k: v["available_files_copied"] for k, v in record["staging"].items()},
        "source_defects": record["source_defects"],
        "covariance_ratio": 2,
        "thresholds_available": False,
    }
    error = abs(gt - saved["starwarps"])
    error_top = float(np.ceil(error.max() * 1000) / 1000)
    controls = {
        "starwarps": saved["starwarps"],
        "oracle_time_mean_repeated": np.repeat(gt.mean(0)[None, ...], 12, axis=0),
        "oracle_truth_reversed": gt[::-1],
        "oracle_first_frame_repeated": np.repeat(gt[:1], 12, axis=0),
    }
    reference = {
        "truth": [plane(frame) for frame in gt],
        "error": [plane(frame, (0.0, error_top), "error") for frame in error],
        "diagnostics": record["temporal_diagnostics"]["oracle_truth"],
        "controls": [
            {
                "id": k,
                "first": plane(a[0]),
                "last": plane(a[-1]),
                "native": record["native_video_metric_replay"][k]["average"],
                "generic": record["generic_dispatch_replay"][k],
                "direction_change_deg": record["temporal_diagnostics"][k][
                    "array_polar_moment_net_change_deg"
                ],
                "difference_error_ratio": record["temporal_diagnostics"][k][
                    "adjacent_difference_error_ratio"
                ],
            }
            for k, a in controls.items()
        ],
    }
    args.output.mkdir(parents=True, exist_ok=False)
    for name, value in [("inputs", inputs), ("contract", contract), ("reference", reference)]:
        write(args.output / f"{name}.json", value)
    (args.output / "BENCHMARK-LICENSE.txt").write_bytes((args.sources / "LICENSE").read_bytes())
    (args.output / "DATA-LICENSE.txt").write_text("""Source attribution

Imaging-101 Authors, AI4ImagingLab/imaging-101-release; MIT notice retained in
BENCHMARK-LICENSE.txt. Synthetic dynamic EHT arrays are from starpacker52/imaging-101
at the pinned revision in NOTICE.md. Algorithm attribution: Bouman et al.,
Reconstructing Video from Interferometric Measurements of Time-Varying Sources,
arXiv:1711.01357v2. Source methods say they were adapted from achael/eht-imaging.

No upstream algorithm code, paper figure, telescope photograph or trained model
is included. This is a local explanatory derivative of the released synthetic
arrays, not publication or an independent license grant for third-party material.
""")
    (args.output / "NOTICE.md").write_text("""# Dynamic EHT source views

Benchmark `dc2f668939b21e8312e22529615def610f8611df`; asset revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3`. The
[source audit](../../external-tasks/sources/imaging101-eht-dynamic-audit.json)
records all 73 source and 18 asset hashes, fixture replay and scoring controls.

Rebuild with scripts/build_imaging101_eht_dynamic_assets.py using --sources
and a fresh --output destination in the existing NumPy/Pillow environment.
No source module import, simulation, solver, EM optimization or install runs.

All twelve native 30x30 frames remain in original order, with epoch times from
0 to 6 hours. Display time is an explanatory clock, not observation duration or
EM iteration. This is a synthetic crescent with an EHT-inspired array; the
source generator retains all 28 station pairs without an elevation cut.

Full grids use source origin=lower: PNG rows are flipped vertically, with
array row zero at the bottom and column zero at the left. The source DFT l and m
both decrease with array index. Use array coordinates; do not copy RA/Dec labels
from another task. Pixel size is 3.4 microarcseconds; full field is 102 microarcseconds.
Brightness-direction moments use atan2(row-center,column-center), describing
array brightness direction rather than celestial position angle or warp parameters.

Brightness images share 0..0.075 Jy/pixel. Absolute error uses a separately
labeled full-range upper bound rounded upward to 0.001 Jy/pixel. DFT kernel real
and imaginary weights share -1..1. Explicit interpolated RGB palettes and 8-bit
quantization have recorded maximum error; no crop, smoothing or spatial resampling.

Input plots use exactly 28 stored u/v points and complex visibilities per epoch.
No conjugate copies are counted. Component bars use sigma/sqrt(2), following the
generator's complex-RMS convention. The source inference helper uses sigma squared
per real/imaginary component, twice the nominal generator variance; retain this
source discrepancy. Kernel witnesses are fixed baseline rows 0,8,16,27 at epoch 0.
They evaluate the source DFT formula only, with no reference image or inversion.

The prior is the source's 50 microarcsecond FWHM, power-six super-Gaussian with
5-percent floor, normalized to 2 Jy. The temporal diagram is conceptual; highlight
passes are not measured trajectories or EM states. Source defaults to a four-
parameter affine warp without translation and process covariance 1e-7 times identity.

Saved static and StarWarps arrays are historical outputs. Native metrics average
twelve per-frame centered correlations and range-normalized errors. The legacy
task recipe flattens the video; local generic dispatch uses cosine correlation
and global-range error. No current pass boundaries exist. The older no-workspace
fallback requires 2D; local replay does not establish Docker equivalence.

Truth images, errors, truth diagnostics and answer-based controls live in
reference.json. They mount only in explicit reference/diagnostics/scoring chapters;
reference chapter's first half remains hidden. A repeat of truth's time mean or
first frame and reversed truth are oracle scoring controls, not reconstructions.
Actual L1-L3 expose ground_truth.npz, so reader reveal is not evaluator privacy.

Native image scores improve for saved StarWarps, but its descriptive brightness
direction advances 57.88 degrees versus 90 in truth and 88.61 in static. Supplemental
adjacent-difference error also differs from total-image error. Do not generalize
from one saved synthetic video, claim a calibrated motion estimate, or rewrite
scores. Pinned main.py has a SyntaxError; no fresh solver execution is established.
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
            "id": "retained-imaging101-eht-dynamic-v1",
            "frame": "source-record",
            "units": "Jy/pixel",
            "license": "LicenseRef-Imaging101-EHT-dynamic-sources",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(record_path): sha(record_path),
                "scripts/build_imaging101_eht_dynamic_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_grid": [30, 30],
                "frames": 12,
                "baselines_per_frame": 28,
                "kernel_rows": selected_rows,
                "all_saved_frames": True,
                "model_runs": 0,
                "cropped": False,
                "shared_brightness_range": [0, 0.075],
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
                "error_max": error_top,
                "files": {n: (args.output / n).stat().st_size for n in names},
            }
        )
    )


if __name__ == "__main__":
    main()
