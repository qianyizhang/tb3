"""Build exact numerical teaching arrays from acquired CARS source assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-cars-audit.json")
    record = json.loads(record_path.read_text())
    assert sha(args.audit / "audit.json") == record["reproduction"]["receipt_sha256"]
    for row in record["asset_downloads"]:
        if row["status"] == "verified":
            assert sha(args.sources / row["path"]) == row["sha256"]
    args.output.mkdir(parents=True, exist_ok=False)
    task = args.sources / "tasks/cars_spectroscopy"
    raw = np.load(task / "data/raw_data.npz", allow_pickle=False)
    gt = np.load(task / "data/ground_truth.npz", allow_pickle=False)
    fit = np.load(task / "evaluation/reference_outputs/reconstruction.npz", allow_pickle=False)
    forward = np.load(args.audit / "forward-proposals.npz", allow_pickle=False)
    write(
        args.output / "inputs.json",
        {
            "nu": raw["nu_axis"][0].tolist(),
            "measured": raw["measurements"][0].tolist(),
            "meta": json.loads((task / "data/meta_data.json").read_text()),
        },
    )
    write(
        args.output / "reference.json",
        {
            "clean": gt["spectrum"][0].tolist(),
            "temperature_K": int(gt["temperature"][0]),
            "x_mol": float(gt["x_mol"][0]),
        },
    )
    write(
        args.output / "contract.json",
        {
            "fit": fit["y_pred"][0].tolist(),
            "temperature_K": float(fit["temperature_pred"][0]),
            "proposals": [
                {"temperature_K": t, "curve": forward[str(t)].tolist()} for t in [2000, 2800]
            ],
            "replay": record["reproduction"]["result"]["native_saved_output_replay"],
            "generic": record["reproduction"]["result"]["generic_scoring"],
        },
    )
    (args.output / "DATA-LICENSE.txt").write_bytes((args.sources / "LICENSE").read_bytes())
    (args.output / "NOTICE.md").write_text("""# Imaging101 CARS numerical teaching pack

Source: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`; data revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3` on
[Hugging Face](https://huggingface.co/datasets/starpacker52/imaging-101).
MIT terms are retained in DATA-LICENSE.txt. Exact hashes, staging and scoring
are in [the source audit](../../external-tasks/sources/imaging101-cars-audit.json).

`inputs.json` preserves all 200 source samples with their wavenumber axis and
metadata. No resampling or image synthesis. `reference.json` carries the clean
synthetic spectrum and true parameters, revealed explicitly to the reader.
This display boundary is **not** the released solver boundary: L1/L2/L3 seed the
whole data directory, including ground_truth.npz. L2's approach also names 2400 K.

`contract.json` contains the upstream saved fit, reproduced metrics and two
bounded forward evaluations at 2000 and 2800 K with other parameters fixed.
Those curves are teaching diagnostics, not optimization iterates or agent outputs.
The saved fit is 2391.5641794510043 K, not a new solve. Forward calls emitted
retained NumPy warnings; outputs were finite and source-reference reproduction
agreed within 1.34e-11. No scalar confidence interval is inferred.

Plot x is wavenumber 2280 to 2330 cm^-1, y is dimensionless max-normalized intensity.
Measured points are dark green, saved fit is solid orange, reference is dashed
purple, diagnostic forward curves are blue. Residuals compare saved fit minus
measured at the same source index. Every color has a local key.

No external benchmark or inverse solver was run. Missing pass thresholds stay
missing. One synthetic nonmedical case does not establish capability performance.
""")
    names = ["inputs.json", "reference.json", "contract.json", "NOTICE.md", "DATA-LICENSE.txt"]
    manifest = {
        "id": "retained-imaging101-cars-v1",
        "frame": "source-record",
        "units": "cm^-1",
        "license": "MIT",
        "label_license": "MIT",
        "reference_policy": "reader-reference-reveal",
        "sources": {
            str(record_path): sha(record_path),
            "scripts/build_imaging101_cars_assets.py": sha(Path(__file__)),
        },
        "checks": {
            "samples": 200,
            "resampling": False,
            "original_arrays_preserved": True,
            "new_inverse_solve": False,
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
