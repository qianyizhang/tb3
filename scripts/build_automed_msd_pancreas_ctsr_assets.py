"""Build symbolic MSD Pancreas contracts; no source module import or task execution."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-msd-pancreas-ctsr-task"
PACK = "symbolic-automed-msd-pancreas-ctsr-v1"


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
            "input": "Public ct.nii.gz, same-grid MSD Pancreas x4 z-axis trilinear-degraded volume. Exact degraded volume/HR absent.",
            "units": "HU declared. Native shape, affine, spacing/orientation and physical z mapping unverified. x4 through-plane degradation is not x4 output enlargement in all axes.",
            "simulation": "Config public grid equals hidden HR grid; exact degradation/resampling code, kernel convention, phase and Full slice/patient/split join absent. MSD_Pancreas_CT_SR20/all 20 are declared, not observed count.",
            "excluded": "Official upstream dataset.json: 281 train/139 test, CT 3D, segmentation family. Only metadata/prefix acquired, no image or label displayed. Upstream IDs/splits do not establish Full restoration membership/private target.",
        },
        "helper.json": {
            "initially_visible": False,
            "weights": None,
            "reference": None,
            "lite": "PlainCNN_trilinear_interpolation_x4.pth from ISBI2023 Roldbach repository. Preserve HU, shape, affine/header; no weights/revision/hash or inference acquired.",
            "standard": "Compare all 5 named checkpoints: PlainCNN/AE_Maxpool/UNet trilinear x4 and PlainCNN/AE_Maxpool same-insertion x4. Named compatibility/availability are source guidance, not measured suitability.",
            "window": "Same public/hidden-target grid. Choose normalization and inverse HU mapping, then preserve native NIfTI geometry. Generic binary/organ-lesion segmentation prompts conflict with CT-SR sct.nii.gz.",
            "source_claims": "Lite plan.md; Standard plan.md+plan.png. Source setup uses CUDA0. No explicit benchmark-training rule inferred beyond prescribed pretrained workflow; no task/tool/model run.",
        },
        "operation.json": {
            "executed": False,
            "steps": [
                "Audit z degradation",
                "Normalize / infer",
                "Restore same grid",
                "Submit NIfTI cases",
            ],
            "limitations": "Symbolic protocol only; no resampling, through-plane restoration, native labels, checkpoints, scorer or clinical result.",
        },
        "output.json": {
            "path": "agents_outputs/<case_id>/sct.nii.gz",
            "prediction": None,
            "score": None,
            "reference": None,
            "shape": None,
            "format": "Loadable finite 3D NIfTI; equal private-target shape if reference exists. No on-disk dtype/affine/header/spacing equality guard. HU<-2500 or>5000 and constants warn only; missing predictions leave present-format valid.",
            "coverage": "All supplied IDs form completion denominator; valid scored predictions form MAE/RMSE means, SSIM and finite PSNR have separate subsets. No ID deduplication, actual Full count or missing-file format penalty.",
            "rules": {
                "raw": "Full-volume HU MAE/RMSE without clipping; PSNR fixed 4095 HU. MSE0→infinity, omitted from finite PSNR mean. No configured mask and no GT finiteness/affine guard.",
                "ssim": "Clip[-1024,3071]HU, average valid SSIM planes along array axis 2 regardless of affine. Small planes/errors skipped; no skimage→None. No body/organ ROI in configured route.",
                "rating": "Configured mean SSIM≥.98→tier2/A, ≥.95→tier1/B, else tier0/C if format valid and any score, else F. Finite SSIM guard exists. Partial outputs can retain A/B; no LPIPS or enhancement baseline_bands. Loader failure generic defaults .90/.75 differ.",
                "completion": "Proxy=finite clipped mean SSIM 0\u20131\u00d7n_predicted/allIDs, rounded 4 decimals. Report empty-ID denominator coerced 1; missing/invalid GT or prediction unscored. No measured proxy.",
                "workflow": "S4=.5completion+.5format; S5=.5(anyvalid+positiveproxy)+.5format. S1\u2013S3 None count 0 across full weight denominator 1. Optional judge attached afterwards without recomputation. Overall=.5workflow+.5proxy; progress 2 gates completion≥.9 and format.",
            },
            "boundary": "Private high-resolution ct.nii.gz absent. No predicted volume, medical label, restoration or measured metric. Same array shape/score does not prove anatomical registration or clinical accuracy.",
        },
    }
    records["source.json"]["notice"] = r["top_warning"]
    for name, value in records.items():
        put(name, value)
    (a.output / "DATA-LICENSE.txt").write_text(
        "LicenseRef-TB3-symbolic-teaching; source-backed authored contracts only. No MSD Pancreas pixels, data rights or redistribution asserted.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nNo patient pixels, private CT target or measured outcome.\n"
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
            "frame": "MSD-Pancreas-same-grid-through-plane-degradation-symbolic-only",
            "units": "declared-HU-contract; no observed pixel calibration",
            "runtime_geometry": "source-records",
            "sources": {rel: hashlib.sha256(a.receipt.read_bytes()).hexdigest()},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
