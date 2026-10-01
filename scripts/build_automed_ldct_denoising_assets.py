"""Build symbolic LDCT contracts; no source module import or task execution."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-ldct-denoising-task"
PACK = "symbolic-automed-ldct-denoising-v1"


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

    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "symbolic",
            "pixels": None,
            "patient": None,
            "native_geometry": None,
            "case_ids": None,
            "private_reference": None,
            "input": "Public input.npy: declared 512 \u00d7 512 float32 HU. No matched noisy-clean Full array.",
            "units": "HU declared; prose \u22121300..3200, field \u22121024..3000; actual spacing/orientation/dose unverified.",
            "simulation": "LDCT_SimNICT; helper calls HighI0 = 10³. Noise realization/seed/operator and AAPM/native split mapping absent; no quarter-dose equivalence inferred.",
            "excluded": "ReX LDCT-IQA normalized training TIFF is not this HU denoising input/reference pair.",
        },
    )
    put(
        "helper.json",
        {
            "initially_visible": False,
            "weights": None,
            "reference": None,
            "lite": "DRUNet/deepinv GPU inference-only; choose HU mapping, sigma and inverse. BM3D fallback allowed. No checkpoint hash or run.",
            "standard": "Compare at least 3 inference-only candidates, at least 2 DNNs. No benchmark training. model_info BM3D/DnCNN/Restormer; S1 example 2 classical + 1 DNN conflicts.",
            "window": "Guidance \u22121024..3072 HU → [0,1]; clipping can discard extremes and inverse must restore declared scale. Not an acquired transformation.",
            "source_claims": "Performance/baseline prose and baseline_bands are retained task policy, not newly measured results.",
        },
    )
    put(
        "operation.json",
        {
            "executed": False,
            "steps": [
                "Plan HU mapping",
                "Denoise with chosen sigma",
                "Invert to HU",
                "Submit every case",
            ],
            "limitations": "Symbolic contracts only; no pixels, normalization, model, denoising, scorer or shuffled control executed.",
        },
    )
    put(
        "output.json",
        {
            "path": "agents_outputs/<case_id>/enhanced.npy",
            "prediction": None,
            "score": None,
            "reference": None,
            "shape": None,
            "format": "Declared 512 \u00d7 512 float32 HU; actual checker: finite floating 2D array matching private reference shape, no float32/range guard.",
            "coverage": "All evaluator-supplied PATIENT_IDS (not independently verified unique patients); valid-count/all-ID completion, every format valid for non-F. Means omit NaNs per metric, retain infinities; n_valid=non-NaN PSNR. No actual denominator.",
            "rules": {
                "raw": "PSNR dB uses private per-ID data_range CSV else ref extrema; MSE ≤1e\u221212→99. SSIM Gaussian/population covariance can be negative. No positive/finite range guard.",
                "lpips": "LPIPS AlexNet lower better; independently min-max each array to [-1,1], constant → 0, grayscale repeated 3 channels. Absolute HU offset/scale lost from this metric.",
                "rating": "Present v3 A 42.798 dB / .9863 SSIM; B 40.798/.9463; C 38.798/.9163, AND gates. No LPIPS gate. For TASK=ldct-denoising-task with corresponding /eval deployment; actual launcher environment absent. Older fallback differs. No finite-score guard; NaN less-than comparisons can bypass v3 thresholds. Any invalid format/aborted/no PSNR or completion < .5→F.",
                "normalization": "Clipped(PSNR\u221230)/15, clipped SSIM, clipped(1\u2212LPIPS/.30); mean rounded 4 decimals, 0\u20131. Field named clinical does not establish clinical accuracy.",
                "pass": "SSIM≥.9663058295715962\u2212.02; fraction across all per-ID records, including missing. Shuffle rotates reference IDs by 1; one-ID rotation is unchanged.",
            },
            "boundary": "Private reference.npy/ground_truth.csv remain absent. No model output, measured PSNR/SSIM/LPIPS, patient identity or clinical accuracy.",
        },
    )
    (a.output / "DATA-LICENSE.txt").write_text(
        "LicenseRef-TB3-symbolic-teaching; source-backed authored contract records only. No AAPM image or redistribution permission asserted.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nNo patient pixels, private reference, participant result or clinical claim.\n"
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
            "frame": "LDCT-declared-HU-inference-contract-symbolic-only",
            "units": "declared-HU-contract; no observed pixel calibration",
            "runtime_geometry": "source-records",
            "sources": {rel: hashlib.sha256(a.receipt.read_bytes()).hexdigest()},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
