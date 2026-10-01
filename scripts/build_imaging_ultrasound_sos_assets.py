"""Index pinned native synthetic projections; never execute a forward or inverse method."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
from pathlib import Path

ENTRY = "imaging101-ultrasound-sos-tomography"
PACK = "retained-imaging-ultrasound-sos-v1"
FRAME = "Ultrasound-native-sinogram-plus-symbolic-slowness-inverse"


def npy(raw):
    if raw[:6] != b"\x93NUMPY" or raw[6] not in (1, 2):
        raise ValueError("Unsupported numeric NPY")
    offset = 10 if raw[6] == 1 else 12
    length = int.from_bytes(raw[8:offset], "little")
    h = ast.literal_eval(raw[offset : offset + length].decode())
    if h["fortran_order"] or h["descr"] != "<f8":
        raise ValueError("Changed numeric source convention")
    return list(
        struct.unpack("<" + str(math.prod(h["shape"])) + "d", raw[offset + length :])
    ), list(h["shape"])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    r = json.loads(a.receipt.read_text())
    if r["entry_id"] != ENTRY or a.output.exists():
        raise ValueError("Wrong entry or nonfresh output")
    for p in r["source_pins"]:
        b = (a.source_root / p["path"]).read_bytes()
        if len(b) != p["bytes"] or hashlib.sha256(b).hexdigest() != p["sha256"]:
            raise ValueError("Stale source pin: " + p["path"])

    def read(suffix):
        pins = [p for p in r["source_pins"] if p["path"].endswith(suffix)]
        if len(pins) != 1:
            raise ValueError("Ambiguous source: " + suffix)
        return a.source_root / pins[0]["path"]

    with zipfile.ZipFile(read("/assets/ultrasound_sos_tomography/data/raw_data.npz")) as z:
        arrays = {k[:-4]: npy(z.read(k)) for k in z.namelist()}
    noisy, shape = arrays["sinogram"]
    clean, clean_shape = arrays["sinogram_clean"]
    _full, full_shape = arrays["sinogram_full"]
    angles, angle_shape = arrays["angles"]
    if (
        shape != [1, 128, 60]
        or clean_shape != shape
        or full_shape != [1, 128, 180]
        or angle_shape != [1, 60]
        or angles != list(range(0, 180, 3))
    ):
        raise ValueError("Changed projection/batch/detector/angle contract")
    with zipfile.ZipFile(read("/assets/ultrasound_sos_tomography/data/ground_truth.npz")) as z:
        speed, speed_shape = npy(z.read("sos_phantom.npy"))
        slowness, slow_shape = npy(z.read("slowness_perturbation.npy"))
    if speed_shape != [1, 128, 128] or slow_shape != speed_shape:
        raise ValueError("Changed source phantom domain")
    if any(abs(d - (1 / c - 1 / 1500)) > 1e-15 for c, d in zip(speed, slowness, strict=True)):
        raise ValueError("Changed speed versus delta-slowness convention")
    out = a.output.resolve()
    out.mkdir(parents=True)

    def put(name, data):
        (out / name).write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")

    put(
        "measurement.json",
        {
            "shape": shape,
            "angles": angles,
            "detector": 64,
            "native_detector_trace": noisy[64 * 60 : 65 * 60],
            "units": "Source projection sums; physical seconds uncalibrated",
            "noisy_range": [min(noisy), max(noisy)],
            "full_shape": full_shape,
            "native_parity": "Exact float64 native indexing; no preprocessing, projection or inverse executed",
        },
    )
    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "mixed",
            "patient": None,
            "private_reference": None,
            "geometry": "Actual parallel-beam radon(circle=True), 128 detector pixels, 60 angles in degrees. Metadata ring radius 50 mm / pixel 0.5 mm is not an implemented physical ring-ray table.",
            "sampling": "7680 sparse projection samples for 16384 image pixels; full 180-angle and clean arrays are source helpers, not additional patients.",
            "units": "Speed m/s and delta-slowness s/m; projection sums omit pixel-length scaling and are not calibrated seconds.",
            "visibility": "Clean/full sinograms and speed/slowness phantom already solver-visible. No sequestered patient/reference condition.",
        },
    )
    put(
        "helper.json",
        {
            "initially_visible": False,
            "solver_visible_truth": True,
            "private_reference": None,
            "native_clean_detector_trace": clean[64 * 60 : 65 * 60],
            "source_center_speed": speed[64 * 128 + 64],
            "source_center_delta_slowness": slowness[64 * 128 + 64],
            "target_role": "Exact source synthetic center [64,64] and clean detector 64 trace; educational source-truth reveal, not a participant reconstruction or private evaluator target.",
            "tiers": {
                "L1": "README, requirements, noisy/clean/full raw arrays and phantom truth",
                "L2": "L1 plus approach",
                "L3": "L2 plus software design",
            },
            "reset": "Covered before paint on backward replay and chapter exit",
        },
    )
    put(
        "operation.json",
        {
            "executed": False,
            "steps": [
                "Keep native detector-by-angle ordering",
                "Audit physical pixel length and signed baseline",
                "Select a source inverse method without running it",
                "Convert delta slowness to speed and specify output reference",
            ],
            "methods": {
                "fbp": "Source ramp-filtered iradon; discrete parallel-beam geometry, not refracted ring paths. No FBP executed.",
                "sart": "Main 30 iterations,relaxation0.15. Named SART uses full-sinogram residual backprojection; normalized row-action textbook equivalence is not verified.",
                "tv": "Main lambda 1e-6, 300 iterations, positivity=False; function default lambda 1e-7 / positivity=True differs. Approximate norm/adjoint steps are not a convergence proof.",
            },
            "baseline": 1500,
            "symbolic_speeds": [1450, 1500, 2500],
            "formula": "delta_s=1/c-1/1500; c=1/max(delta_s+1/1500,1e-8). Illustrative algebra only, no map estimate.",
            "sign": "1450 gives positive delta_s; 2500 gives negative. Main fat-negative comment is inconsistent with formula. Signed perturbation is distinct from positive absolute slowness.",
            "adjoint": "physics adjoint=unfiltered iradon*pi/(2*n_angles); TV updates use unfiltered iradon without this factor. Exact discrete adjoint and step scaling unverified.",
        },
    )
    put(
        "output.json",
        {
            "path": "output/reconstruction.npy",
            "prediction": None,
            "map": None,
            "score": None,
            "reference": None,
            "shape": [128, 128],
            "format": "Generic one real speed NPY, m/s; main reconstructions.npz has multiple delta_s and sos method keys. Saved source results are not participant outputs.",
            "metric": "Generic range-normalized RMSE and uncentered cosine over 16384 speed entries; no flux rescaling in the effective implementation. Generic global SSIM differs from source local skimage SSIM; generic constant-range NRMSE returns infinity.",
            "task_metric": "Main scores delta-slowness crop [13:115,13:115], 102x102=10404 entries. Source NRMSE returns 0.0 for exact zero reference range (generic returns infinity). Source cosine NCC returns 0 for either exact zero norm; source local skimage SSIM uses reference range without a zero-range guard. No score computed.",
            "reference_selection": "Generic discovers data/ground_truth.npz before reconstructions.npz. Shape-matched key ranking gives sos_phantom before slowness_perturbation; full speed m/s reference differs cropped delta_s s/m.",
            "threshold": "Main writes top-level ncc_boundary=0.9*best NCC and nrmse_boundary=1.1*best NRMSE from cropped slowness, plus nested baseline results. Generic attaches these when metrics file is present, even though it scores full speed. No metrics file retained here; no effective threshold or score.",
            "limits": r["reopening_condition"],
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nExact native indexed values and symbolic algebra only. No forward/inverse/preparer/scorer executed.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Pinned imaging-101 MIT software licence below. Synthetic HF dataset-card MIT declaration retained separately; no patient data rights or independent clinical reference claimed. Exact array-indexed derivatives preserve float64 values.\n\n"
        + read("/source-evidence/LICENSE").read_text()
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "measurement.json",
        "source.json",
        "helper.json",
        "operation.json",
        "output.json",
    ]
    put(
        "manifest.json",
        {
            "id": PACK,
            "frame": FRAME,
            "units": "pixel-grid, degrees; uncalibrated projection units",
            "license": "MIT",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "mixed",
            "sources": {
                f"presentation/external-tasks/sources/{ENTRY}-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest()
            },
            "assets": [
                {
                    "file": n,
                    "bytes": (out / n).stat().st_size,
                    "sha256": hashlib.sha256((out / n).read_bytes()).hexdigest(),
                    "provenance": "source-derived-teaching",
                    "role": "illustration",
                }
                for n in names
            ],
            "checks": {
                "native_synthetic_projection": True,
                "symbolic_signed_slowness_rule": True,
                "source_target_reader_reveal": True,
                "private_reference": False,
                "preparer_run": False,
                "operator_run": False,
                "solver_run": False,
                "scorer_run": False,
                "model_run": False,
            },
        },
    )


if __name__ == "__main__":
    main()
