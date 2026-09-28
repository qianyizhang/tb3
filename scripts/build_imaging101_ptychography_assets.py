"""Derive native-pixel ptychography views from the pinned source audit."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import h5py
import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def picture(array, low, high, *, logarithmic=False):
    values = np.asarray(array, dtype=np.float64)
    assert values.ndim == 2 and np.all(np.isfinite(values))
    if logarithmic:
        q = np.log1p(np.clip(values, low, high)) / np.log1p(high)
    else:
        q = (values - low) / (high - low)
    pixels = np.rint(np.clip(q, 0, 1) * 255).astype(np.uint8)
    stream = io.BytesIO()
    Image.fromarray(pixels).save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": list(values.shape),
        "range": [float(low), float(high)],
        "transform": "log1p" if logarithmic else "linear",
        "display": "uint8 grayscale; native pixels, no resampling",
        "clipped_pixels": int(((values < low) | (values > high)).sum()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-ptychography-audit.json")
    record = json.loads(record_path.read_text())
    assert sha(args.audit / "audit.json") == record["reproduction"]["receipt_sha256"]
    for row in record["asset_downloads"]:
        assert sha(args.sources / row["path"]) == row["sha256"]
    audit = record["reproduction"]["result"]
    args.output.mkdir(parents=True, exist_ok=False)
    task = args.sources / "tasks/conventional_ptychography"
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    positions = np.load(task / "data/positions.npy", allow_pickle=False)
    truth = np.load(task / "data/ground_truth.npz", allow_pickle=False)["object"]
    with h5py.File(task / "evaluation/reference_outputs/recon.hdf5") as hf:
        obj, errors = np.squeeze(hf["object"][()]), hf["error"][()]
    samples = []
    for diagnostic in audit["selected_projection_diagnostics"]:
        j = diagnostic["scan"]
        projection = np.load(args.audit / f"projection-{j}.npz", allow_pickle=False)
        assert np.array_equal(projection["measured"], raw["ptychogram"][j])
        samples.append(
            {
                **diagnostic,
                "measured": picture(projection["measured"], 0, 32966, logarithmic=True),
                "estimated": picture(projection["estimated"], 0, 32966, logarithmic=True),
                "projected": picture(projection["projected"], 0, 32966, logarithmic=True),
            }
        )
    write(
        args.output / "inputs.json",
        {
            "samples": samples,
            "positions": positions.tolist(),
            "encoders": raw["encoder"].astype(float).tolist(),
            "metadata": audit["metadata"],
            "coverage": audit["patch_coverage"],
        },
    )
    write(
        args.output / "contract.json",
        {
            "amplitude": picture(np.abs(obj), 0, float(np.abs(obj).max())),
            "phase": picture(np.angle(obj), -float(np.pi), float(np.pi)),
            "errors": errors.tolist(),
            "generic": audit["generic_scoring"],
            "native_phase": audit["native_phase_controls"],
            "saved_forward": audit["saved_forward_diagnostics"],
            "coordinate_formula": "round(encoder_m / dxp_m) + 542//2 - 128//2",
            "rounding": "numpy round (ties to even)",
        },
    )
    write(
        args.output / "reference.json",
        {
            "phase": picture(np.angle(truth), -float(np.pi), float(np.pi)),
            "amplitude": picture(np.abs(truth), 0, float(np.abs(obj).max())),
            "shape": list(truth.shape),
            "unit_magnitude": True,
            "phase_bar_pixels": int((np.angle(truth) > 1).sum()),
            "solver_visible_all_levels": True,
        },
    )
    for dest, src in [
        ("BENCHMARK-LICENSE.txt", "LICENSE"),
        ("DATA-LICENSE.txt", "upstream/LICENSE"),
    ]:
        (args.output / dest).write_bytes((args.sources / src).read_bytes())
    (args.output / "NOTICE.md").write_text("""# Imaging101 conventional ptychography source views

Benchmark source: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`. Numeric data:
starpacker52/imaging-101 at `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [audit](../../external-tasks/sources/imaging101-ptychography-audit.json)
pins source, data, original licenses, failed/recovered fetch and diagnostics.
BENCHMARK-LICENSE.txt retains its MIT label. DATA-LICENSE.txt preserves the
original PtyLab Academic License Agreement for the attributed source algorithms.
No claim that benchmark MIT replaces those upstream terms is made.
Attribution: Loetgering et al., PtyLab.m/py/jl, Optics Express 31 (2023),
13763-13797; the upstream agreement also requests the 2021 PtyLab COSI citation.

This is one synthetic USAF pure-phase case, not a measured specimen. Three
128x128 diffraction frames use scan indices0,49,99 and a common log1p grayscale
range0..32966. Count values are neither rounded to integers nor regenerated.
Source generator adds a Poisson draw to its expectation;14-bit is not a cap.

All100 native positions and encoders are retained. Pixel upper-left corners are
round(encoder/dxp)+207. Probe/object pixels are3.4331597222 micrometers. Geometry
panels show rectangular extraction windows, not actual beam support. Every image
preserves source pixels with only labeled linear/log contrast and uint8 display
quantization. Object axes use pixel centers0..541; detector axes0..127. Physical
sampling is explicit. Images and outlines share the same coordinate mapping.

Projection diagnostics start from the exact source seed42 object/probe
initialization. They apply one detector intensity projection at each of three
selected scans. No object or probe update, inverse iteration, generation or agent
was executed. These pictures do not produce the saved reconstruction.

Saved amplitude and raw angle come from recon.hdf5. Phase images use the same
linear -pi..pi radian range as synthetic truth. Display does not subtract phase
means; the separately labeled native scores do. Stored error history has350
samples and is not an animation of intermediate object estimates.

Truth phase and amplitude live only in reference.json and require reader reveal.
This is a presentation boundary: releasedL1-L3 staging actually copies both truth
files. Generic scoring discards phase, giving the correct/erased/conjugated truth
identical NCC1/MSE0. Zero magnitude range produces infinite NRMSE, even for exact
truth. No pass boundaries are shipped. Native saved-phase scores replay the
original0.9757/0.0434 values without new reconstruction or historical rewriting.
""")
    names = [
        "inputs.json",
        "contract.json",
        "reference.json",
        "NOTICE.md",
        "DATA-LICENSE.txt",
        "BENCHMARK-LICENSE.txt",
    ]
    manifest = {
        "id": "retained-imaging101-ptychography-v1",
        "frame": "source-record",
        "units": "um",
        "license": "PtyLab academic/non-commercial",
        "label_license": "MIT",
        "reference_policy": "reader-reference-reveal",
        "sources": {
            str(record_path): sha(record_path),
            "scripts/build_imaging101_ptychography_assets.py": sha(Path(__file__)),
        },
        "checks": {
            "native_image_pixels_preserved": True,
            "scan_positions": 100,
            "selected_scans": [0, 49, 99],
            "object_shape": [542, 542],
            "detector_shape": [128, 128],
            "stored_error_samples": 350,
            "inverse_iterations_executed": 0,
            "truth_unit_magnitude": True,
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
    }
    write(args.output / "manifest.json", manifest)
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
