"""Build symbolic MRI SR contracts; no source module import or task execution."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-mri-sr-task"
PACK = "symbolic-automed-mri-sr-v1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    r = json.loads(a.receipt.read_text())
    if r["entry_id"] != ENTRY or a.output.exists():
        raise ValueError("Wrong receipt or nonfresh output")
    brief = a.receipt.parents[3] / f"presentation/external-tasks/briefs/{ENTRY}.md"
    if hashlib.sha256(brief.read_bytes()).hexdigest() != r["brief_sha256"]:
        raise ValueError("Stale maintained brief")
    for pin in r["source_pins"]:
        raw = (a.source_root / pin["path"]).read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Stale source pin")
    a.output.mkdir(parents=True)

    def put(name, value):
        (a.output / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")

    records = {
        "source.json": {
            "basis": "symbolic",
            "pixels": None,
            "patient": None,
            "native_geometry": None,
            "case_ids": None,
            "private_reference": None,
            "input": "Declared 360\u00d7256 float32 LR slice → 720\u00d7512 HR target. No acquired image or actual reconstruction.",
            "units": "Roughly normalized [0,1], not HU or calibrated MR signal. Grid x2 per axis gives x4 samples, not recovered detail or measured resolution.",
            "simulation": "Exact LR-generation kernel/antialiasing/sampling and selected fastMRI slice/coil/contrast/geometry/split join absent. Config case and evaluator patient units are not independently joined.",
            "excluded": "Native upstream raw k-space or authorized public helper is not the exact Full degraded slice/private HR; no mask, coils, ACS or native pixels acquired.",
        },
        "helper.json": {
            "initially_visible": False,
            "weights": None,
            "reference": None,
            "lite": "Swin2SR caidas/swin2SR-classical-sr-x2-64; GPU inference-only, no training. Normalize grayscale→uint8→RGB, output channel mean, resize to HR. No immutable checkpoint revision/hash or execution.",
            "standard": "Compare at least 3 inference-only methods including at least 2 DNNs. Bicubic/Lanczos/SwinIR/Restormer are named source guidance, not recommendations. S1 example 2 classical + 1 DNN conflicts; no benchmark training.",
            "window": "Input 360\u00d7256 → target 720\u00d7512. RGB replication, uint8 quantization, channel reduction and final resize are adaptation choices, not anatomical recovery. Generic S3 same-shape/direct-difference prompt conflicts with this x2 grid.",
            "source_claims": "Retained baseline table/100 count and performance/clinical-transfer assertions are source claims, not newly measured results.",
        },
        "operation.json": {
            "executed": False,
            "steps": [
                "Audit LR/HR grid",
                "Prepare model channels",
                "Resolve x2 target",
                "Submit every case",
            ],
            "limitations": "Source protocol only; no data acquisition, degradation, model, image resampling, reconstruction, scorer or shuffled control executed.",
        },
        "output.json": {
            "path": "agents_outputs/<case_id>/enhanced.npy",
            "prediction": None,
            "score": None,
            "reference": None,
            "shape": None,
            "format": "Declared 720\u00d7512 float32 roughly [0,1]; actual checker accepts finite floating 2D matching private reference shape, no dtype-width/intensity range guard. Generic input-shape prompt conflicts.",
            "coverage": "All evaluator-supplied PATIENT_IDS (not independently verified unique patients); valid-count/all-ID completion, every format valid for non-F. Means omit NaNs per metric, retain infinities; n_valid=non-NaN PSNR. No recovered denominator.",
            "rules": {
                "raw": "PSNR dB uses private per-ID data_range CSV else ref extrema; MSE≤1e\u221212→99. SSIM Gaussian/population covariance can be negative. No positive/finite range guard.",
                "lpips": "LPIPS AlexNet independently min-max maps each array to [-1,1], constant→0, grayscale repeated 3 channels. Absolute intensity/scale shifts can disappear from this metric; not clinical calibration.",
                "rating": "Present v3 A 25.599 dB / .6332 SSIM; B 23.599 / .5932; C 21.599 / .5632 AND gates, no LPIPS gate. Invalid/aborted/no PSNR or completion<.5→F. No finite-score guard; NaN less-than comparisons can bypass v3 thresholds. For TASK=mri-sr-task and corresponding /eval deployment; launcher environment absent. Older v2 LPIPS gates differ.",
                "normalization": "Clipped(PSNR\u221220)/15, clipped SSIM, clipped(1\u2212LPIPS/.50), mean rounded 4 decimals, 0\u20131. Field named clinical does not establish clinical accuracy.",
                "pass": "SSIM≥.6131783537940364\u2212.02; fraction over all per-ID records including missing. Shuffle rotates reference IDs by 1; one-ID rotation unchanged.",
            },
            "boundary": "Private HR reference.npy/ground_truth.csv absent. No actual normalized output, measured PSNR/SSIM/LPIPS or recovered anatomical detail.",
        },
    }
    records["source.json"]["notice"] = r["top_warning"]
    for name, value in records.items():
        put(name, value)
    (a.output / "DATA-LICENSE.txt").write_text(
        "LicenseRef-TB3-symbolic-teaching; source-backed authored contracts only. No fastMRI pixels, data rights or redistribution asserted.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nNo patient pixels, private HR or measured outcome.\n"
    )
    assets = [
        {
            "file": p.name,
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "role": "illustration",
            "provenance": "symbolic-protocol",
        }
        for p in sorted(a.output.iterdir())
    ]
    rel = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": PACK,
            "source_class": "symbolic-protocol",
            "license": "LicenseRef-TB3-symbolic-teaching",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "frame": "MRI-SR-declared-twofold-image-grid-symbolic-only",
            "units": "declared-normalized-image-grid; physical scale absent",
            "runtime_geometry": "source-records",
            "sources": {rel: hashlib.sha256(a.receipt.read_bytes()).hexdigest()},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
