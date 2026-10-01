"""Derive exact masks and source pixel series; never import source operators."""

import argparse
import ast
import base64
import hashlib
import json
import math
import struct
import zipfile
from pathlib import Path

ENTRY = "imaging101-mri-dynamic-dce"
PACK = "retained-imaging-dynamic-mri-v1"
FRAME = "Dynamic-MRI-native-kspace-plus-symbolic-temporal-inverse"


def npy(raw):
    if raw[:6] != b"\x93NUMPY" or raw[6] not in (1, 2):
        raise ValueError("Unsupported NPY")
    offset = 10 if raw[6] == 1 else 12
    length = int.from_bytes(raw[8:offset], "little")
    h = ast.literal_eval(raw[offset : offset + length].decode())
    if h["fortran_order"]:
        raise ValueError("Unsupported array order")
    count = math.prod(h["shape"])
    complex_array = h["descr"] == "<c8"
    if h["descr"] not in ("<c8", "<f4"):
        raise ValueError("Unsupported source dtype")
    vals = struct.unpack(
        "<" + str(count * (2 if complex_array else 1)) + "f", raw[offset + length :]
    )
    return (
        [list(vals[i : i + 2]) for i in range(0, len(vals), 2)] if complex_array else list(vals)
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
    brief = a.receipt.parent.parent / "briefs" / f"{ENTRY}.md"
    if hashlib.sha256(brief.read_bytes()).hexdigest() != r["brief_sha256"]:
        raise ValueError("Stale brief pin")
    for p in r["source_pins"]:
        b = (a.source_root / p["path"]).read_bytes()
        if len(b) != p["bytes"] or hashlib.sha256(b).hexdigest() != p["sha256"]:
            raise ValueError("Stale source pin: " + p["path"])

    def read(suffix):
        pins = [p for p in r["source_pins"] if p["path"].endswith(suffix)]
        if len(pins) != 1:
            raise ValueError("Ambiguous source: " + suffix)
        return a.source_root / pins[0]["path"]

    raw = read("/assets/mri_dynamic_dce/data/raw_data.npz")
    if raw.read_bytes() != read("/source-evidence/raw_data.npz").read_bytes():
        raise ValueError("Fresh native archive differs")
    with zipfile.ZipFile(raw) as z:
        masks, shape = npy(z.read("undersampling_masks.npy"))
        kspace, kshape = npy(z.read("undersampled_kspace.npy"))
    if shape != [1, 20, 128, 128] or kshape != shape:
        raise ValueError("Changed frame/grid/batch geometry")
    if any(v not in (0, 1) for v in masks):
        raise ValueError("Nonbinary native mask")
    if any(pair != [0.0, 0.0] for pair, mask in zip(kspace, masks, strict=True) if not mask):
        raise ValueError("Nonzero unmeasured k-space")
    counts = [int(sum(masks[t * 16384 : (t + 1) * 16384])) for t in range(20)]
    if counts != [2457] * 20:
        raise ValueError("Changed retained acquisition")
    # LSB-first preserves native frame,row,column C order exactly; no Fourier transform.
    packed_masks = bytearray(len(masks) // 8)
    for index, value in enumerate(masks):
        packed_masks[index // 8] |= int(value) << (index % 8)
    with zipfile.ZipFile(read("/assets/mri_dynamic_dce/data/ground_truth.npz")) as z:
        truth, tshape = npy(z.read("dynamic_images.npy"))
        times, time_shape = npy(z.read("time_points.npy"))
    if tshape != shape or time_shape != [20] or times[0] != 0 or times[-1] != 60:
        raise ValueError("Changed source truth/time condition")
    meta = json.loads(read("/assets/mri_dynamic_dce/data/meta_data.json").read_text())
    if meta["sampling_rate"] != 0.15 or meta["noise_level"] != 0.005:
        raise ValueError("Changed retained source metadata")
    out = a.output.resolve()
    out.mkdir(parents=True)

    def put(name, data):
        (out / name).write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")

    put(
        "measurement.json",
        {
            "mask_encoding": "base64-lsb0-frame-row-column",
            "mask_bits_base64": base64.b64encode(packed_masks).decode("ascii"),
            "sample_counts": counts,
            "time_seconds": times,
            "shape": shape,
            "native_kspace_center_64_64": [kspace[t * 16384 + 64 * 128 + 64] for t in range(20)],
            "source_units": "complex k-space arbitrary units; time seconds; grid indices, no physical spacing",
        },
    )
    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "mixed",
            "private_reference": None,
            "patient": None,
            "geometry": "Native 1\u00d720\u00d7128\u00d7128 synthetic grid; batch removed by loader. No coil dimension, sensitivity maps, physical spacing, anatomical orientation or patient acquisition.",
            "sampling": "Variable-density Cartesian random points; central 10\u00d710 square sampled. 2457/16384 samples per frame (14.9963%), not 25% generator defaults or radial GRASP.",
            "time": "Synthetic 20 times from 0\u201360 seconds; arbitrary image intensity is not contrast concentration or a patient perfusion parameter.",
            "noise": "Retained metadata noise 0.005; generator defines relative-to-global-max complex k-space Gaussian noise only on sampled points. Default script uses 0.02 and 25% masks; do not regenerate as the same acquisition.",
        },
    )
    put(
        "helper.json",
        {
            "initially_visible": False,
            "solver_visible_truth": True,
            "private_reference": None,
            "source_pixel_row_col": [49, 79],
            "source_pixel_series": [truth[t * 16384 + 49 * 128 + 79] for t in range(20)],
            "truth_role": "Synthetic ground_truth.npz pixel (49,79), arbitrary intensity; already solver-visible. Teaching reveal only; not reconstruction, diagnosis, ROI average, perfusion or private test reference.",
            "tiers": {
                "L1": "README + data + requirements; truth included with data",
                "L2": "L1 + approach",
                "L3": "L1 + approach/design",
            },
            "reset": "Hide source series on exit and backward replay before paint",
        },
    )
    put(
        "operation.json",
        {
            "executed": False,
            "steps": [
                "Remove batch axis; preserve time and grid order",
                "Per-frame y_t=M_t F(x_t)+masked complex noise",
                "Couple neighbors D_t x=x[t+1]-x[t] across 19 intervals",
                "Separate measured data consistency and temporal TV penalty",
            ],
            "methods": {
                "zero_filled": "Source returns abs(centered orthonormal inverseFFT(y)); aliasing is a mechanism, no baseline image computed here.",
                "temporal_tv": "Source main calls temporal_tv_pgd, lambda 0.001 / max_iter 200 / tol 1e-5. Header ADMM conflicts with executable PGD route; solver function defaults differ.",
                "prox": "Actual Chambolle dual uses complex temporal differences and magnitude projection; despite magnitude-and-phase wording, no explicit magnitude-only denoising in this function. Returned output abs(x).",
            },
            "axes": "Centered ortho FFT only axes(-2,-1); no temporal FFT or coil operation. Step 1 gradient uses F^H M(MFx-y); loss half squared residual plus lambda sum abs(D_t x).",
            "limits": "Temporal TV promotes smooth/piecewise-constant dynamics but can alter rapid changes; no scientific accuracy claim follows.",
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
            "shape": [20, 128, 128],
            "format": "Generic single real numeric array; native source main saves tv_reconstruction.npz key reconstruction in evaluation/reference_outputs. Source saved TV is not participant output.",
            "metric": "Generic MSE averages 327680 array entries; NRMSE=sqrt(MSE)/(global max(gt)-min(gt)); NCC uncentered cosine over whole volume, no flux scaling. Reference discovery picks dynamic_images with shape 20\u00d7128\u00d7128 after squeeze; time_points has wrong shape.",
            "task_metric": "Source reports per-frame errors over 16384 pixels and arithmetic mean over 20 frames, separately full-volume values. These are different aggregations, not 20 patients. Zero-range NRMSE returns 0 in task versus infinity generic; zero-norm NCC/PSNR edge conventions also differ.",
            "scorer_route": "Filesystem scoring discovers data/ground_truth.npz and squeezes the four-dimensional dynamic_images array to (20,128,128); time_points (20,) cannot match this output. No-filesystem scoring instead requires generic ground_truth.npy under reference_outputs or data, absent from the pinned DCE listing; the saved TV NPZ is not a substitute for that filename. Staged files and scorer route must be pinned before any verdict.",
            "threshold": "Pinned asset tree has metrics_detail.json only, no metrics.json boundary file. No generic pass/fail threshold established or score measured.",
            "limits": r["reopening_condition"],
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nSource truth is solver-visible; display reveal does not establish isolation. No FFT, operator, solver, scorer or model executed.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "AI4ImagingLab imaging-101-release revision dc2f668939b21e8312e22529615def610f8611df MIT. Native synthetic starpacker52/imaging-101 asset revision a9de559b54849a25988a8a0d8a5e869063a5a7a3 identities matched retained HF LFS. Exact masks, complex center values and source time/pixel samples derive by array indexing only; no reconstruction. Local noncommercial interpretation.\n\n"
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
            "units": "pixel-grid, seconds; arbitrary intensity",
            "license": "MIT",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "mixed",
            "sources": {
                f"presentation/external-tasks/sources/{ENTRY}-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest(),
                f"presentation/external-tasks/briefs/{ENTRY}.md": hashlib.sha256(
                    brief.read_bytes()
                ).hexdigest(),
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
                "native_synthetic_input": True,
                "source_truth_reader_reveal": True,
                "private_reference": False,
                "operator_run": False,
                "solver_run": False,
                "scorer_run": False,
                "model_run": False,
            },
        },
    )


if __name__ == "__main__":
    main()
