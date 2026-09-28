"""Derive native fan-beam CT views from pinned, audited arrays; no solver run."""

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


def picture(array, low, high):
    values = np.asarray(array, dtype=np.float64)
    assert values.ndim == 2 and np.all(np.isfinite(values))
    assert values.min() >= low and values.max() <= high
    pixels = np.rint((values - low) / (high - low) * 255).astype(np.uint8)
    stream = io.BytesIO()
    Image.fromarray(pixels).save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": list(values.shape),
        "range": [low, high],
        "transform": "linear",
        "display": "uint8 grayscale; native pixels, no resampling",
        "clipped_pixels": 0,
    }


def normalized_crop(array):
    crop = array[12:116, 12:116].astype(np.float64)
    return (crop - crop.min()) / (crop.max() - crop.min())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-fan-beam-audit.json")
    record = json.loads(record_path.read_text())
    assert sha(args.audit / "audit.json") == record["reproduction"]["receipt_sha256"]
    for row in record["asset_downloads"]:
        assert row["status"] == "verified" and sha(args.sources / row["path"]) == row["sha256"]
    audit = record["reproduction"]["result"]
    args.output.mkdir(parents=True, exist_ok=False)
    task = args.sources / "tasks/ct_fan_beam"
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    truth = np.load(task / "data/ground_truth.npz", allow_pickle=False)["phantom"][0]
    saved = [
        np.load(task / f"evaluation/reference_outputs/recon_{key}.npz", allow_pickle=False)[
            "reconstruction"
        ][0]
        for key in ["fbp_full", "fbp_short", "tv_short"]
    ]
    diagnostics = np.load(args.audit / "operator-diagnostics.npz", allow_pickle=False)
    write(
        args.output / "inputs.json",
        {
            "sinograms": [picture(raw[k][0], -5, 55) for k in ["sino_full", "sino_short"]],
            "angles_degrees": [
                np.degrees(raw[k].astype(np.float64)).tolist()
                for k in ["angles_full", "angles_short"]
            ],
            "detector_positions": raw["det_pos"].tolist(),
            "geometry": audit["geometry"],
        },
    )
    write(
        args.output / "contract.json",
        {
            "maps": [picture(a, 0, 1.6) for a in saved],
            "normalized_maps": [picture(normalized_crop(a), 0, 1) for a in saved],
            "names": ["Full-scan FBP", "Short-scan FBP", "TV-labelled short scan"],
            "keys": ["fbp_full", "fbp_short", "tv_short"],
            "weights": picture(diagnostics["parker_weights"], 0, 1),
            "weight_curves": audit["parker_weights"],
            "pixel_controls": audit["pixel_controls"],
            "native": audit["native_metrics"],
            "generic": audit["generic_scoring"],
            "crop": audit["native_crop"],
            "fbp": audit["saved_fbp_replay"],
            "loss": audit["saved_data_fidelity"],
            "adjoint": audit["adjoint_control"],
            "prox": audit["tv_projection_control"],
            "staging": {k: v["files"] for k, v in audit["staging"].items()},
        },
    )
    write(
        args.output / "reference.json",
        {
            "map": picture(truth, 0, 1.6),
            "normalized_map": picture(normalized_crop(truth), 0, 1),
            "solver_visible_all_levels": True,
        },
    )
    for dest, src in [
        ("BENCHMARK-LICENSE.txt", "LICENSE"),
        ("UPSTREAM-GPL-2.0.txt", "upstream/leehoy/LICENSE"),
    ]:
        (args.output / dest).write_bytes((args.sources / src).read_bytes())
    (args.output / "DATA-LICENSE.txt").write_text("""Source terms and attribution

The released numeric arrays and benchmark source are distributed in Imaging101
with its MIT notice, retained in BENCHMARK-LICENSE.txt. The task explicitly cites
adaptations of leehoy/CTReconstruction (GPL version 2 text retained separately)
and xtie97/CT_fanbeam_recon_numba (no license file in the pinned tree).
The benchmark MIT notice is not assigned to either upstream repository.
This pack contains derived numerical views, no copied upstream implementation.
See NOTICE.md and the source audit for pinned revisions and exact source hashes.
""")
    (args.output / "NOTICE.md").write_text("""# Imaging101 fan-beam CT source views

Benchmark: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`. Numeric release:
starpacker52/imaging-101 at `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [audit](../../external-tasks/sources/imaging101-fan-beam-audit.json)
pins all seven assets, task/shared sources, upstream notices and numerical controls.
BENCHMARK-LICENSE.txt, UPSTREAM-GPL-2.0.txt and DATA-LICENSE.txt retain distinct
terms. The cited curved-detector ray tracer differs from this pixel-driven source.

One synthetic 128x128 phantom. Full/short sinograms have 180/116 angle rows and
192 detector columns. Their shared linear display range is -5..55. Saved and
truth images share 0..1.6 relative attenuation. Native pixels are uint8-quantized
without resampling or clipping. Cropped normalized views retain the actual 104x104
samples and map each crop independently to 0..1; they are explicitly labeled.
All geometry is in pixels, not mm or HU, with no patient orientation implied.

Geometry follows the executed coordinate convention: column x and row y increase
right and down in the diagram, as in the native image. At angle zero the source
is (0,256), below the field; detector center is (0,-256). Source and detector
rotate together. Orange unit-pixel controls illustrate the exact 512/U mapping
and two-bin weights. They are analytical diagnostics, not optimizer iterates.
The declared half-fan angle uses detector position /256 although source-detector
separation is 512. Original angles and Parker weights remain unchanged.

Three saved images are selected without crossfading or invented reconstruction
trajectories. Both saved FBP arrays reproduce exactly at float32 precision.
The recorded 150-step data-fidelity curve is displayed as saved, including 66
increases; it excludes the TV penalty. No iterative solver or agent was run.

Truth assets live in reference.json and mount only after the reader reveal in
the reference chapter, with a dashed purple frame. This presentation boundary
is not solver privacy: actual L1-L3 local seeding includes ground_truth.npz.
The orange dashed square marks the native metric crop, never a segmentation.
Native crop-normalized scores differ from generic full-array scores. Historical
notebook boundaries are not installed: no shipped metrics.json supplies a pass.
Fixed adjoint and radius-projection controls qualify source descriptions without
changing the saved images, historical scores or claiming clinical accuracy.
""")
    names = [
        "inputs.json",
        "contract.json",
        "reference.json",
        "NOTICE.md",
        "DATA-LICENSE.txt",
        "BENCHMARK-LICENSE.txt",
        "UPSTREAM-GPL-2.0.txt",
    ]
    write(
        args.output / "manifest.json",
        {
            "id": "retained-imaging101-fan-beam-v1",
            "frame": "source-record",
            "units": "px",
            "license": "LicenseRef-Imaging101-fan-beam-sources",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(record_path): sha(record_path),
                "scripts/build_imaging101_fan_beam_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_image_pixels_preserved": True,
                "image_shape": [128, 128],
                "sinogram_shapes": [[180, 192], [116, 192]],
                "metric_crop_shape": [104, 104],
                "selected_pixel_controls": 3,
                "iterative_solver_steps": 0,
                "saved_fbp_float32_exact": True,
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
