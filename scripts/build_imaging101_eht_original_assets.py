"""Build native static closure-imaging views; no simulation or reconstruction."""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, sha
from PIL import Image


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def plane(value):
    """Full native grid, explicit unit-flux/log display, no spatial resampling."""
    assert value.shape == (64, 64) and np.isfinite(value).all() and value.min() >= 0
    image = value / value.sum()
    lo, hi = 1e-6, 0.34
    assert image.max() <= hi
    colors = np.array([(0, 0, 0), (110, 0, 0), (230, 65, 0), (255, 215, 55), (255, 255, 230)])
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
    level = (np.log10(np.maximum(image, lo)) - np.log10(lo)) / np.log10(hi / lo)
    pixels = np.rint(level * 255).astype(np.uint8)
    stream = io.BytesIO()
    Image.fromarray(lut[pixels]).save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": [64, 64],
        "range": [lo, hi],
        "scale": "log10",
        "unit": "Fraction of total flux / pixel",
        "stored_sum": float(value.sum()),
        "source_min": float(value.min()),
        "source_max": float(value.max()),
        "display_max": float(image.max()),
        "below_display_floor": int((image < lo).sum()),
        "log10_quantization_max_error_above_floor": float(np.log10(hi / lo) / 510),
        "row_zero": "top",
        "column_zero": "left",
        "pixel_size_uas": 2,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    audit_path = Path("presentation/external-tasks/sources/imaging101-eht-original-audit.json")
    audit = json.loads(audit_path.read_text())
    for row in audit["verified_sources"] + audit["verified_assets"]:
        assert sha(args.sources / row["path"]) == row["sha256"]
    assert sha(Path("scripts/audit_imaging101_eht_original.py")) == audit["script_sha256"]
    task = args.sources / "tasks/eht_black_hole_original"
    raw = arrays(task / "data/raw_data.npz")
    uv, ids, vis = raw["uv_coords"], raw["station_ids"], raw["vis_cal"]
    gains = np.linspace(0.8, 1.2, 7) * np.exp(1j * np.linspace(-0.5, 0.7, 7))
    controls = []
    for kind, prefix, legs, rows in [
        ("phase", "cp", 3, [0, 134, 268]),
        ("amplitude", "lca", 4, [0, 116, 232]),
    ]:
        for row in rows:
            indices, orientations, distances = [], [], []
            for leg in range(1, legs + 1):
                coordinate = raw[f"{prefix}_u{leg}"][row]
                distances_all = np.linalg.norm(np.concatenate([uv, -uv]) - coordinate, axis=1)
                index = int(distances_all.argmin())
                assert distances_all[index] < 1e-3
                indices.append(index % len(uv))
                orientations.append(1 if index < len(uv) else -1)
                distances.append(float(distances_all[index]))
            pairs = [
                ids[i] if sign > 0 else ids[i][::-1]
                for i, sign in zip(indices, orientations, strict=True)
            ]
            values = np.array(
                [
                    vis[i] if sign > 0 else np.conj(vis[i])
                    for i, sign in zip(indices, orientations, strict=True)
                ]
            )
            after = np.array(
                [v * gains[a] * np.conj(gains[b]) for v, (a, b) in zip(values, pairs, strict=True)]
            )
            signs = [1, 1, 1] if kind == "phase" else [1, 1, -1, -1]

            def terms(v, kind=kind):
                return np.degrees(np.angle(v)) if kind == "phase" else np.log(np.abs(v))

            def combine(v, signs=signs, kind=kind, terms=terms):
                result = float(np.dot(signs, terms(v)))
                return (result + 180) % 360 - 180 if kind == "phase" else result

            assert abs(combine(values) - combine(after)) < 1e-10
            controls.append(
                {
                    "kind": kind,
                    "source_row": row,
                    "baseline_indices": indices,
                    "uv_match_error_wavelengths": distances,
                    "pairs": np.array(pairs).tolist(),
                    "stations": sorted({int(s) for pair in pairs for s in pair}),
                    "signs": signs,
                    "before": terms(values).tolist(),
                    "after": terms(after).tolist(),
                    "combined_before": combine(values),
                    "combined_after": combine(after),
                    "stored_closure": float(
                        raw["cp_values_deg" if kind == "phase" else "lca_values"][row]
                    ),
                }
            )
    observed = {}
    for key in ["cp_values_deg", "cp_corrupt_values_deg", "lca_values", "lca_corrupt_values"]:
        observed[key] = raw[key].tolist()
    names = [
        f"{method}_{condition}"
        for method in ["vis_rml", "amp_cp", "closure-only"]
        for condition in ["cal", "corrupt"]
    ]
    images = {
        name: np.load(task / "evaluation/reference_outputs" / f"{name}.npy", allow_pickle=False)
        for name in [*names, "ground_truth", "prior_image"]
    }
    inputs = {
        "uv_Glambda": (uv / 1e9).tolist(),
        "station_pairs": ids.tolist(),
        "station_names": audit["metadata"]["station_names"],
        "vis_cal_abs_Jy": np.abs(vis).tolist(),
        "vis_corrupt_abs_Jy": np.abs(raw["vis_corrupt"]).tolist(),
        "sigma_vis_Jy": raw["sigma_vis"].tolist(),
        "observed": observed,
        "closure_controls": controls,
        "metadata": audit["metadata"],
        "gain_amplitudes": np.abs(gains).tolist(),
        "gain_phases_rad": np.angle(gains).tolist(),
    }
    contract = {
        "names": names,
        "images": [plane(images[name]) for name in names],
        "prior": plane(images["prior_image"]),
        "method_labels": ["Visibility RML", "Amplitude + closure phase", "Closure-only RML"],
    }
    reference = {
        "truth": plane(images["ground_truth"]),
        "native": [audit["flux_normalized_range_metrics"][n] for n in names],
        "generic": [audit["generic_dispatch"][n] for n in names],
        "zero": audit["generic_dispatch"]["zero_control"],
        "physical_truth": audit["generic_dispatch"]["ground_truth_jy"],
        "fallback": audit["fallback_snippet_arithmetic"]["closure-only_corrupt"],
    }
    args.output.mkdir(parents=True, exist_ok=False)
    for name, value in [("inputs", inputs), ("contract", contract), ("reference", reference)]:
        write(args.output / f"{name}.json", value)
    (args.output / "BENCHMARK-LICENSE.txt").write_bytes((args.sources / "LICENSE").read_bytes())
    (args.output / "DATA-LICENSE.txt").write_text("""Source attribution

Imaging-101 Authors 2026; benchmark MIT notice in BENCHMARK-LICENSE.txt.
Synthetic release arrays: starpacker52/imaging-101 at the revision in NOTICE.md.
Task cites Chael et al. 2018, ApJ 857:23 for closure imaging and EHT 2019 for
background. No paper figure, telescope photograph or upstream solver source is
redistributed. These derivatives are not real M87 observations or paper results;
local explanatory use does not establish independent third-party license grants.
""")
    (args.output / "NOTICE.md").write_text("""# Static closure-imaging views

Benchmark commit dc2f668939b21e8312e22529615def610f8611df; asset revision
 a9de559b54849a25988a8a0d8a5e869063a5a7a3. The
[source audit](../../external-tasks/sources/imaging101-eht-original-audit.json)
retains hashes for 79 source files and all 40 released assets.

Rebuild with scripts/build_imaging101_eht_original_assets.py, --sources and a
fresh --output in the existing NumPy/Pillow environment. No source-module import,
random draw, simulation, optimization, model trial or runtime installation.

Input views retain all 421 measured rows, 21 station pairs and seven station
names. No conjugate samples are added. Both calibrated and corrupted observations
are supplied. Native closures retain all 269 phases and 233 log ratios; axes must
include the large corrupted log-amplitude outlier. Stored noisy-condition
comparisons are not a deterministic gain-only test.

Six fixed algebra controls select phase rows 0,134,268 and amplitude rows
0,116,232. Each leg is matched to its native UV row or conjugate within 0.001
wavelength. This preserves per-scan geometry, unlike the small first-occurrence
helper. Deterministic station gains have amplitudes 0.8..1.2 and phases
-0.5..0.7 radians. Individual baseline terms change; wrapped phase sums and log
ratios cancel to numerical precision. Amplitude control terms are direct logs
of matched visibilities, not a claim to reproduce every stored debias correction.
Station positions in the graph are schematic, not geographic.

Six saved images retain calibrated/corrupted conditions for visibility RML,
amplitude plus phase, and closure-only RML. Images are 64x64, 2 microarcsecond
pixels, 128 microarcsecond field. Row 0 is top and column 0 left; no celestial
bearing is asserted. Every display image is divided by its own stored sum for
morphology comparison, while original sums remain visible. One shared logarithmic
heat scale spans 1e-6..0.34 fraction of total flux per pixel; smaller values are
black. The 8-bit log quantization error and below-floor count are recorded in
each plane. No spatial interpolation, smoothing or crop is applied.

The stored prior is a reference workflow artifact, not a seeded L1 image file.
Any image-fitting flow diagram is conceptual. The player never fabricates
optimizer iterations or modifies source arrays. Supplied truth and score controls
live in reference.json and are gated to the reference/scoring chapters; truth
stays hidden until the reference chapter midpoint. All L1-L3 actually expose
data/ground_truth.npz, so this is reader ordering rather than solver privacy.

Published scores flux-normalize before range NRMSE. Live filesystem scoring uses
unscaled range NRMSE against a unit-sum reference; physical truth sums to 0.6 Jy.
The fallback/generator uses flux-normalized reference-RMS NRMSE. No pass boundaries
are supplied. Oracle physical-truth and zero controls disclose their roles and
are not new agent solutions. Single saved results do not establish robustness,
noise calibration, optimizer recovery or performance on sky observations.

The audit retains a ten-input/421-output fixture mismatch, a factor-of-two
visibility-loss convention, a TV-gradient sign defect, scan-grouping limitations
and stale notebook metrics. Main saved comparisons use entropy, not TV. No
corrected scientific outcome is inferred from these source observations.
""")
    files = [
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
            "id": "retained-imaging101-eht-original-v1",
            "frame": "source-record",
            "units": "fraction/pixel",
            "license": "LicenseRef-Imaging101-EHT-original-sources",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(audit_path): sha(audit_path),
                "scripts/build_imaging101_eht_original_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_grid": [64, 64],
                "visibility_rows": 421,
                "station_pairs": 21,
                "phase_rows": 269,
                "amplitude_rows": 233,
                "closure_controls": 6,
                "saved_conditions": 6,
                "cropped": False,
                "model_runs": 0,
            },
            "assets": [
                {
                    "file": name,
                    "sha256": sha(args.output / name),
                    "bytes": (args.output / name).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if name == "reference.json"
                    else "illustration",
                }
                for name in files
            ],
        },
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "files": {n: (args.output / n).stat().st_size for n in files},
            }
        )
    )


if __name__ == "__main__":
    main()
