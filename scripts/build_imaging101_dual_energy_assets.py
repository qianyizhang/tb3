"""Derive native dual-energy CT views from pinned, audited source arrays."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def picture(array, high):
    values = np.asarray(array, dtype=np.float64)
    assert values.ndim == 2 and np.all(np.isfinite(values))
    assert values.min() >= 0 and values.max() <= high
    pixels = np.rint(np.clip(values / high, 0, 1) * 255).astype(np.uint8)
    stream = io.BytesIO()
    Image.fromarray(pixels).save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": list(values.shape),
        "range": [0, high],
        "transform": "linear",
        "display": "uint8 grayscale; native pixels, no resampling",
        "clipped_pixels": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-dual-energy-audit.json")
    record = json.loads(record_path.read_text())
    assert sha(args.audit / "audit.json") == record["reproduction"]["receipt_sha256"]
    for row in record["asset_downloads"]:
        if row["status"] == "verified":
            assert sha(args.sources / row["path"]) == row["sha256"]
    audit = record["reproduction"]["result"]
    args.output.mkdir(parents=True, exist_ok=False)
    task = args.sources / "tasks/ct_dual_energy"
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    truth = np.load(task / "data/ground_truth.npz", allow_pickle=False)
    saved = np.load(
        task / "evaluation/reference_outputs/reference_reconstruction.npz", allow_pickle=False
    )
    write(
        args.output / "inputs.json",
        {
            "counts": [picture(raw[k][0], 1_600_000) for k in ["sinogram_low", "sinogram_high"]],
            "energies": raw["energies"][0].tolist(),
            "spectra": raw["spectra"][0].tolist(),
            "mus": raw["mus"][0].tolist(),
            "theta": raw["theta"][0].tolist(),
            "metadata": audit["metadata"],
        },
    )
    write(
        args.output / "contract.json",
        {
            "maps": [picture(saved[k][0], 1.6) for k in ["tissue_map", "bone_map"]],
            "sinograms": [picture(saved[k][0], 11) for k in ["tissue_sinogram", "bone_sinogram"]],
            "rays": audit["ray_diagnostics"],
            "native": audit["native_metrics"],
            "generic": audit["generic_scoring"],
            "fbp": audit["saved_state_replay"],
            "calibration": audit["calibration_comparison"],
            "body_mask_pixels": audit["body_mask_pixels"],
            "staging": {k: v["files"] for k, v in audit["staging"].items()},
        },
    )
    write(
        args.output / "reference.json",
        {
            "maps": [picture(truth[k][0], 1.6) for k in ["tissue_map", "bone_map"]],
            "solver_visible_all_levels": True,
            "body_mask_pixels": audit["body_mask_pixels"],
        },
    )
    for dest, src in [
        ("BENCHMARK-LICENSE.txt", "LICENSE"),
        ("DATA-LICENSE.txt", "upstream/LICENSE"),
    ]:
        (args.output / dest).write_bytes((args.sources / src).read_bytes())
    (args.output / "NOTICE.md").write_text("""# Imaging101 dual-energy CT source views

Benchmark source: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`. Numeric release:
starpacker52/imaging-101 at `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [audit](../../external-tasks/sources/imaging101-dual-energy-audit.json)
pins source, data, licenses, download failures and numerical replay.
BENCHMARK-LICENSE.txt retains the benchmark MIT notice; DATA-LICENSE.txt retains
Giavanna Jadick's MIT notice for the cited dex-ct-sim source. Its Siddon/fan-beam
geometry is different from this benchmark's parallel-beam adaptation.

One synthetic 128x128 phantom, not a patient scan. Native images preserve every
pixel with labeled linear contrast and uint8 quantization, with zero clipping.
Count sinograms have 128 detector rows and 180 angle columns (0..179 degrees).
They share a 0..1600000 count scale. Material sinograms share 0..11 g/cm2;
saved and truth density maps share 0..1.6 g/cm3. Native centers are indexed
0..127; 1 mm spacing means a 128 mm field edge to edge. No laterality or clinical
orientation is implied. Selected-ray circles use pixel centers, never edges.

Exact supplied spectra and attenuation coefficients have 131 bins, 20..150 keV.
Plots retain every numerical sample. Spectra are photons per 1 keV bin. The
mass attenuation curves are cm2/g; the released approximate values are preserved,
not replaced by selected official NIST values. Green labels tissue material or
low-energy spectrum according to the explicit legend; orange labels bone or
high energy. Material and spectral quantities never share an unlabeled plot.

Three saved material ray estimates feed the source polychromatic forward model.
The charts illustrate exp(-a_t mu_t - a_b mu_b), then spectral weighting and
energy summation. They are forward diagnostics at a saved state, not iterations
that generated the reconstruction. Native saved sinograms divided by 0.1 cm and
ramp filtered backprojected, with negative values clipped to zero, reproduce the
stored maps exactly in scikit-image 0.25.2. No material optimization was run.

Truth maps live only in reference.json and are mounted only after reader reveal
in the reference chapter. Dashed purple frames label reference panels. This
presentation boundary is not solver privacy: actual L1-L3 file seeding exposes
both maps and both material sinograms in data/ground_truth.npz.

Native two-material metrics use the 8797/16384 pixel truth body mask, cosine NCC
and range-normalized RMSE. Generic scoring selects a single truth key by shape,
compares whole arrays and does not validate both materials. Control scores are
new saved-array/constructed-control replays, not historical outcomes. No metrics
file or pass thresholds are shipped. The unavailable tiny inverse fixture remains
explicitly unverified. This pack establishes no agent or clinical performance.
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
            "id": "retained-imaging101-dual-energy-v1",
            "frame": "source-record",
            "units": "mm",
            "license": "MIT",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(record_path): sha(record_path),
                "scripts/build_imaging101_dual_energy_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_image_pixels_preserved": True,
                "image_shape": [128, 128],
                "sinogram_shape": [128, 180],
                "energy_samples": 131,
                "selected_rays": 3,
                "material_optimization_iterations": 0,
                "saved_fbp_max_abs_error": 0.0,
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
                "sizes": {n: (args.output / n).stat().st_size for n in names},
            }
        )
    )


if __name__ == "__main__":
    main()
