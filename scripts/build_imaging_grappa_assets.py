"""Index pinned native coil values and illustrate ACS rule; never execute GRAPPA."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
from pathlib import Path

ENTRY = "imaging101-mri-grappa"
PACK = "retained-imaging-grappa-v1"
FRAME = "GRAPPA-native-multicoil-plus-symbolic-ACS-inverse"


def npy(raw):
    if raw[:6] != b"\x93NUMPY" or raw[6] not in (1, 2):
        raise ValueError("Unsupported numeric NPY")
    offset = 10 if raw[6] == 1 else 12
    length = int.from_bytes(raw[8:offset], "little")
    h = ast.literal_eval(raw[offset : offset + length].decode())
    if h["fortran_order"] or h["descr"] != "<f4":
        raise ValueError("Changed numeric source convention")
    return list(
        struct.unpack("<" + str(math.prod(h["shape"])) + "f", raw[offset + length :])
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

    brief = a.receipt.parent.parent / "briefs" / f"{ENTRY}.md"
    if hashlib.sha256(brief.read_bytes()).hexdigest() != r["brief_sha256"]:
        raise ValueError("Stale maintained brief")
    for pin in r["source_pins"]:
        if "git_blob_sha1" in pin:
            b = (a.source_root / pin["path"]).read_bytes()
            if (
                hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
                != pin["git_blob_sha1"]
            ):
                raise ValueError("Stale source Git blob")

    def read(suffix):
        pins = [p for p in r["source_pins"] if p["path"].endswith(suffix)]
        if len(pins) != 1:
            raise ValueError("Ambiguous source: " + suffix)
        return a.source_root / pins[0]["path"]

    raw = read("/assets/mri_grappa/data/raw_data.npz")
    if raw.read_bytes() != read("/source-evidence/raw_data.npz").read_bytes():
        raise ValueError("Fresh source archive differs")
    with zipfile.ZipFile(raw) as z:
        arrays = {k[:-4]: npy(z.read(k)) for k in z.namelist()}
    if len(arrays) != 4 or any(shape != [1, 128, 128, 8] for _v, shape in arrays.values()):
        raise ValueError("Changed coil/spatial/batch geometry")
    real = arrays["kspace_full_real"][0]
    imag = arrays["kspace_full_imag"][0]
    sr = arrays["sensitivity_maps_real"][0]
    si = arrays["sensitivity_maps_imag"][0]
    acquired = [row for row in range(128) if row % 2 == 0 or 54 <= row < 74]
    if len(acquired) != 74:
        raise ValueError("Changed symbolic source rule")
    zero_count = sum(
        real[(y * 128 + x) * 8] == 0 and imag[(y * 128 + x) * 8] == 0
        for y in acquired
        for x in range(128)
    )
    if zero_count:
        raise ValueError("Retained acquired coil 0 zero assumption changed")

    def samples(y, x, rr=real, ii=imag):
        return [[rr[(y * 128 + x) * 8 + c], ii[(y * 128 + x) * 8 + c]] for c in range(8)]

    reference, refshape = npy(read("/source-evidence/ground_truth.npy").read_bytes())
    if refshape != [128, 128]:
        raise ValueError("Changed saved RSS reference domain")
    with zipfile.ZipFile(read("/assets/mri_grappa/data/ground_truth.npz")) as z:
        phantom, shape = npy(z.read("image.npy"))
    if shape != [1, 128, 128] or reference == phantom:
        raise ValueError("RSS versus bare phantom distinction changed")
    out = a.output.resolve()
    out.mkdir(parents=True)

    def put(name, data):
        (out / name).write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")

    put(
        "measurement.json",
        {
            "shape": [1, 128, 128, 8],
            "native_center_kspace": samples(64, 64),
            "native_center_sensitivity": samples(64, 64, sr, si),
            "acs_rows": [54, 73],
            "symbolic_rule_retained_rows": acquired,
            "retained_line_count": 74,
            "symbolic_rule": "Illustration of pinned preprocessing; raw archive is fully sampled, no source preparer was executed or undersampled raw artifact created.",
            "native_acquired_coil 0_exact_zero_count": zero_count,
        },
    )
    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "mixed",
            "private_reference": None,
            "patient": None,
            "geometry": "Synthetic Shepp-Logan phantom; native batch 1 x 128 x 128 x 8 coil-last, Gaussian complex sensitivity maps. No acquired patient brain MRI, physical spacing, anatomical orientation or calibrated k-space frequencies.",
            "sampling": "Source rule: retain even phase-encode rows (dim 0) plus ACS 54..73 inclusive. 74/128 lines 57.8125%, effective 128/74≈1.73 versus nominal R=2. Rule illustration only; native archive remains full.",
            "units": "K-space/sensitivity complex pairs and RSS magnitude in arbitrary source units; grid/coil indices are not physical distances.",
            "visibility": "Full k-space and data phantom already solver-visible; evaluation directory absent initially in end-to-end mode does not establish full-data isolation.",
        },
    )
    put(
        "helper.json",
        {
            "initially_visible": False,
            "solver_visible_full_data": True,
            "private_reference": None,
            "source_target_row_col": [51, 64],
            "native_full_target_pairs": samples(51, 64),
            "target_role": "Native full-data row 51, col 64 target across 8 coils; deliberately hidden educational reveal. It is already solver-visible in raw full k-space, not GRAPPA estimate or private evaluator target.",
            "tiers": {
                "L1": "README + full raw data + phantom + requirements",
                "L2": "L1 + approach",
                "L3": "L1 + approach/design",
            },
            "acs": "Fully sampled 20 x 128 x 8 calibration block rows 54..73, distinct from an independent reference.",
            "reset": "Covered before paint on backward replay and chapter exit",
        },
    )
    put(
        "operation.json",
        {
            "executed": False,
            "steps": [
                "Keep native coil-last axes; illustrate R2/ACS20 rule",
                "Extract padded 5 x 5 ACS patches across 8 coils",
                "Fit each unique hole pattern with scaled ridge weights",
                "Interpolate missing k-space, centered IFFT, then RSS",
            ],
            "methods": {
                "calibration": "W=solve(SᴴS+λ₀I,SᴴT).T; λ₀=0.01·||SᴴS||_F/n_sources. Source and target matrices are ACS examples; no weight matrix is computed here.",
                "interpolation": "Source infers mask from first-coil |k|>0, pads k-space/ACS with zeros, skips all-empty patterns and applies cross-coil weights to holes. True acquired zero can be misidentified in other data; native acquired coil 0 exact zeros=0.",
                "combination": "Centered FFT spatial axes (0,1), forward 1/128, inverse 128 after removing batch; coil axis 2 excluded. Image magnitude is sqrt(sum_coils |IFFT(k_c)|²), not a bare phantom or sensitivity-weighted clinical intensity.",
            },
            "kernel": "5x5 rule illustration with central target and acquired-row neighbors; no prediction, inverse FFT or GRAPPA computation.",
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
            "format": "Generic real 128 x 128 NPY versus main source grappa_reconstruction.npz key reconstruction with 1 x 128 x 128 batch. No participant image or saved GRAPPA result is displayed.",
            "metric": "Filesystem generic NRMSE range-normalized RMSE (zero range → infinity) and uncentered cosine over 16384 pixels. No flux scaling; source same broad NRMSE/cosine but denominator epsilon differs: 1e-12 versus generic 1e-30.",
            "task_metric": "Task-local NRMSE also returns infinity for zero range. Source SSIM is skimage local structural_similarity with reference range. Generic SSIM uses whole-image means/variances and max(reference) as scale; these are different estimators. Without a filesystem workspace, the fallback flux-normalizes output and uses relative L2 NRMSE against a 2D NPY reference; this is a separate backend contract.",
            "reference_selection": "Generic first discovers evaluation/reference_outputs/ground_truth.npy (full-data RSS), before data/ground_truth.npz image (bare phantom). If RSS file absent, reference changes. Both shape 128 x 128, unequal pixel values; shape does not establish equivalent physical intensity.",
            "threshold": "Pinned metrics.json contains nested grappa/zerofill source results, no top-level ncc_boundary/nrmse_boundary. Generic passed=None; source metric numbers remain provenance only and are not displayed.",
            "limits": r["reopening_condition"],
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nFull targets are source-visible; teaching reveal does not make task blind. No source preprocessing, GRAPPA, FFT, RSS or scorer was executed.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "AI4ImagingLab imaging-101-release dc2f668939b21e8312e22529615def610f8611df MIT; synthetic starpacker52/imaging-101 assets a9de559b54849a25988a8a0d8a5e869063a5a7a3, native LFS identities verified. Source solver credits adaptation from mckib2/pygrappa; no implementation copied into pack. Direct array-indexed native complex sample pairs preserve float32 values. Symbolic row/kernel geometry follows pinned rule. Local noncommercial teaching.\n\n"
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
            "units": "pixel-grid, coil index; arbitrary units",
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
                "native_full_kspace": True,
                "symbolic_mask_rule": True,
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
