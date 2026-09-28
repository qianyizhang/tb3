"""Build licensed NLOS teaching views from pinned numerical source arrays."""

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


def image_view(array, maximum):
    # Keep every native pixel. Display-only sqrt and uint8 RGB quantization.
    q = np.sqrt(np.clip(array / maximum, 0, 1))[:, :, None]
    rgb = np.rint(255 * (1 - q) + np.array([38, 75, 67]) * q).astype(np.uint8)
    output = io.BytesIO()
    Image.fromarray(rgb).save(output, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(output.getvalue()).decode(),
        "shape": list(array.shape),
        "maximum": float(maximum),
        "transform": "sqrt(value/maximum), clipped to [0,1], RGB uint8",
        "resampling": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    recpath = Path("presentation/external-tasks/sources/imaging101-nlos-audit.json")
    record = json.loads(recpath.read_text())
    audit = record["reproduction"]["result"]
    assert sha(args.audit / "audit.json") == record["reproduction"]["receipt_sha256"]
    for row in record["asset_downloads"]:
        assert sha(args.sources / row["path"]) == row["sha256"]
    args.output.mkdir(parents=True, exist_ok=False)
    task = args.sources / "tasks/confocal-nlos-fk"
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    vol = np.load(task / "evaluation/reference_outputs/reconstruction.npz", allow_pickle=False)[
        "fk"
    ]
    baseline = np.load(task / "data/baseline_reference.npz", allow_pickle=False)["reconstruction"][
        0
    ]
    hist = json.loads((args.audit / "histograms.json").read_text())
    assert np.array_equal(vol, baseline)
    counts = raw["meas"].sum(axis=2, dtype=np.float64)
    write(
        args.output / "inputs.json",
        {
            "wall": image_view(counts, counts.max()),
            "histograms": hist,
            "raw_shape": list(raw["meas"].shape),
            "meta": audit["metadata"],
            "raw_y64": image_view(raw["meas"][64].T, 42),
        },
    )
    views = [
        {
            "id": "front",
            "label": "Front: maximum over depth",
            "axes": ["x / m", "y / m"],
            "ranges": [[-1, 1], [-1, 1]],
            "image": image_view(vol.max(axis=0), vol.max()),
        },
        {
            "id": "top",
            "label": "Top: maximum over y",
            "axes": ["x / m", "z / m"],
            "ranges": [[-1, 1], [0, 2.4576]],
            "image": image_view(vol.max(axis=1), vol.max()),
        },
        {
            "id": "side",
            "label": "Side: maximum over x",
            "axes": ["y / m", "z / m"],
            "ranges": [[-1, 1], [0, 2.4576]],
            "image": image_view(vol.max(axis=2), vol.max()),
        },
    ]
    scale = 128 * 3e8 * float(raw["bin_resolution"]) / (4 * (float(raw["wall_size"]) / 2))
    probes = []
    for kz in [0.25, 0.5, 0.75]:
        kf = float(np.sqrt(scale**2 * 0.5**2 + kz**2))
        probes.append(
            {
                "kz": kz,
                "kx": 0.5,
                "ky": 0,
                "sample_kf": kf,
                "weight": kz / kf,
                "sample_index": kf * 512 + 512,
            }
        )
    write(
        args.output / "contract.json",
        {
            "views": views,
            "volume_peak": audit["saved_peak"],
            "axes": audit["axes"],
            "stolt": {"scale": scale, "probes": probes},
            "generic": audit["generic_scoring"],
            "native_half": audit["native_half_amplitude_control"],
            "fixture": audit["operator_fixtures"],
        },
    )
    write(
        args.output / "reference.json",
        {
            "front": image_view(baseline.max(axis=0), baseline.max()),
            "equal_to_saved": True,
            "independent_ground_truth": False,
            "shape": list(baseline.shape),
        },
    )
    (args.output / "DATA-LICENSE.txt").write_bytes((args.sources / "upstream/LICENSE").read_bytes())
    (args.output / "BENCHMARK-LICENSE.txt").write_bytes((args.sources / "LICENSE").read_bytes())
    (args.output / "NOTICE.md").write_text("""# Imaging101 confocal NLOS source views

Pinned benchmark: AI4ImagingLab/imaging-101-release
`dc2f668939b21e8312e22529615def610f8611df`; numeric assets: starpacker52/imaging-101
`a9de559b54849a25988a8a0d8a5e869063a5a7a3` on Hugging Face.
The [source audit](../../external-tasks/sources/imaging101-nlos-audit.json) retains
source hashes, original failed fetches, repaired acquisition, staging and metrics.

The benchmark attributes this case to the outdoor measurements of Lindell,
Wetzstein and O'Toole (2019), with 10 minute exposure and a 2 m square relay wall.
Capture provenance is source-attributed; no original MAT-to-NPZ conversion receipt
was acquired. Benchmark MIT terms are in BENCHMARK-LICENSE.txt. Original Stanford
academic/non-commercial code and data terms are in DATA-LICENSE.txt and remain
applicable to these derived views. They are not replaced by the benchmark label.

Inputs retain three exact 2048-bin histograms at source (y,x) indices (32,32),
(64,64), (96,96), the sum over time at every wall pixel, and a y=64 time section.
Calibration uses float64 tofgrid (README incorrectly says float32), floor(delay/32ps),
circular roll and a 512-bin crop. Data are real measurements as attributed by the
source, not generated scenes. The wall image is a sum, not a photograph of the object.

Saved-volume front/top/side views use max projections of the exact float32
(512,128,128) array. PNGs preserve native pixels with sqrt(value/global maximum)
display contrast, then 8-bit RGB quantization. No resampling, filtering or omitted
depth planes. Axis extents follow source volume_axes: x,y -1 to1 m; z0 to2.4576 m.
These inclusive endpoints differ from forward-model half-bin centers. Panels may
stretch pixels to the stated physical extents; array indices and roles stay explicit.

Reference front view is derived separately from baseline_reference.npz and shown
only in the reader reference chapter. Its values exactly equal the saved volume;
no independent ground truth is supplied. Actual released L1-L3 staging copies this
baseline into data/. A reader reveal does not establish hidden evaluation.

Stolt samples are analytic evaluations of the pinned operator mapping, with
kx=.5, ky=0, and kz=.25/.5/.75. The 16x8x8 published solver fixture was checked;
the full-size measurement inverse was not executed. MIP images are saved source
outputs, not the result of the illustrated frequency probes or a fresh agent.

Generic saved-output NCC1/NRMSE0 compares identical arrays; the baseline-copy
control gets the same scores. Half amplitude keeps NCC1 but yields NRMSE.020574.
Native main.py normalizes each volume and removes that amplitude difference.
Shipped metrics have no pass thresholds. No benchmark pass or depth accuracy is
claimed. The saved peak is in the last depth plane; the original MATLAB removes
the last11 planes and has different lateral permutations. Original-author output
equivalence is unverified. All original arrays and metric records remain unchanged.
""")
    names = [
        "inputs.json",
        "reference.json",
        "contract.json",
        "NOTICE.md",
        "DATA-LICENSE.txt",
        "BENCHMARK-LICENSE.txt",
    ]
    manifest = {
        "id": "retained-imaging101-nlos-v1",
        "frame": "source-record",
        "units": "m",
        "license": "Stanford academic/non-commercial",
        "label_license": "MIT",
        "reference_policy": "reader-reference-reveal",
        "sources": {
            str(recpath): sha(recpath),
            "scripts/build_imaging101_nlos_assets.py": sha(Path(__file__)),
        },
        "checks": {
            "histograms": 3,
            "native_bins": 2048,
            "cropped_bins": 512,
            "volume_shape": [512, 128, 128],
            "reference_equals_saved": True,
            "native_image_pixels_preserved": True,
            "full_size_inverse_executed": False,
        },
        "assets": [
            {
                "file": name,
                "sha256": sha(args.output / name),
                "bytes": (args.output / name).stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
            }
            for name in names
        ],
    }
    write(args.output / "manifest.json", manifest)
    print(
        json.dumps(
            {"output": str(args.output), "manifest_sha256": sha(args.output / "manifest.json")}
        )
    )


if __name__ == "__main__":
    main()
