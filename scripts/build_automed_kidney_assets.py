"""Build the bounded, source-derived AutoMedBench kidney teaching pack.

Reads the recovered official KiTS19 case and retained source audit. Never runs a
model or the historical task author modules. Run with the existing nibabel venv.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "workbench.toml").is_file())
SOURCE = ROOT / ".local/explainers/core-20260929/kidney-source"
PIN = {
    "imaging.nii.gz": "cdae5f3e0fbc7c98ab0430b3de42677abda2c1cf93ae0f86bd29fb8606688cb7",
    "segmentation.nii.gz": "d1019d9a690e193e167cadf3518499e9ed54c1c7757ce520152a3ed072159e09",
}
AUDIT = ROOT / "presentation/external-tasks/sources/automed-kidney-audit.json"
AUDIT_PIN = "1849dc0a39b3d3a6d7a2d825735397779b9e63264419506b9ab60cea245b953e"
GEOMETRY = SOURCE / "geometry-review.json"
GEOMETRY_PIN = "30d86bc5e027b113e10ac6d5357fa7ff86b0d3e7524f9506f7392b9bd5f0cb9c"
DATA_LICENSE = ROOT / ".local/explainers/completion-20260927/039-source/kits19/data/LICENSE"
DATA_LICENSE_PIN = "b74fbcfc8ced6f7893b729b2685fc23cf221c72bcd716bd04cd884bf8a33bd48"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_json(pack: Path, name: str, value: object) -> None:
    (pack / name).write_text(json.dumps(value, separators=(",", ":"), ensure_ascii=False) + "\n")


def png_uri(array: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(array).save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="fresh pack directory; existing paths are refused",
    )
    args = parser.parse_args()
    pack = args.output.resolve()
    if pack.exists():
        parser.error(f"refusing to overwrite existing output: {pack}")
    for name, sha in PIN.items():
        assert digest(SOURCE / name) == sha, f"source hash mismatch: {name}"
    assert digest(AUDIT) == AUDIT_PIN, "pinned audit changed"
    assert digest(GEOMETRY) == GEOMETRY_PIN, "geometry review changed"
    assert digest(DATA_LICENSE) == DATA_LICENSE_PIN, "KiTS19 data license changed"
    ct = nib.load(SOURCE / "imaging.nii.gz")
    gt = nib.load(SOURCE / "segmentation.nii.gz")
    assert ct.shape == gt.shape == (611, 512, 512)
    assert np.array_equal(ct.affine, gt.affine)
    assert tuple(nib.aff2axcodes(ct.affine)) == ("I", "P", "L")
    assert np.allclose(ct.header.get_zooms()[:3], (0.5, 0.919921875, 0.919921875))
    source_views, reference_views = [], []
    for index in (288, 311, 344):
        vox = np.asarray(ct.dataobj[index, :, :])
        lab = np.asarray(gt.dataobj[index, :, :])
        assert np.isfinite(vox).all() and set(np.unique(lab)).issubset({0, 1, 2})
        # Fixed WL=40, WW=400: visible HU interval [-160, 240]. No spatial resampling.
        gray = np.clip((vox + 160) / 400 * 255, 0, 255).astype(np.uint8)
        overlay = np.zeros((512, 512, 4), dtype=np.uint8)
        organ = lab == 1
        lesion = lab == 2
        overlay[organ] = (31, 187, 197, 135)
        overlay[lesion] = (250, 183, 56, 180)
        source_views.append({"index": index, "ct_png": png_uri(gray), "window_hu": [-160, 240]})
        reference_views.append(
            {
                "index": index,
                "overlay_png": png_uri(overlay),
                "organ_voxels": int(np.count_nonzero(lab > 0)),
                "lesion_voxels": int(np.count_nonzero(lesion)),
            }
        )
    audit = json.loads(AUDIT.read_text())
    examples = []
    for f in audit["fixtures"]:
        d = f["dice"]
        examples.append(
            {
                "id": f["name"],
                "quick_check_complete": f["quick_check"]["complete"],
                "format_valid": f["format"]["output_format_valid"],
                "organ_dice": d["mean_organ_dice"],
                "lesion_dice_positive": d["mean_lesion_dice"],
                "lesion_positive_cases": d["n_lesion_positive"],
                "cases": d["n_patients"],
            }
        )
    assert len(examples) == 6
    pack.mkdir(parents=True, exist_ok=False)
    save_json(
        pack,
        "source.json",
        {
            "case": "case_00000",
            "kind": "actual source CT; no model output",
            "shape": list(ct.shape),
            "spacing_mm": [0.5, 0.919921875, 0.919921875],
            "axis_codes": ["I", "P", "L"],
            "affine": ct.affine.tolist(),
            "views": source_views,
            "source_sha256": PIN["imaging.nii.gz"],
            "source_url": "https://huggingface.co/datasets/neheller/KiTS-Challenge-Imaging/resolve/65f1f295873a326230153c7e1de0c7dba10f0b29/images/case_00000.nii.gz",
        },
    )
    save_json(
        pack,
        "output.json",
        {
            "saved_prediction": None,
            "patient_path": "agents_outputs/<patient_id>/",
            "required": ["organ.nii.gz", "lesion.nii.gz"],
            "empty_artifacts": [
                {"name": "organ.nii.gz", "data": None},
                {"name": "lesion.nii.gz", "data": None},
            ],
            "shape": list(ct.shape),
            "affine": ct.affine.tolist(),
            "values": "binary 0/1; lesion must be separate; same native CT grid",
            "steps": [
                {
                    "id": "S1",
                    "name": "Research",
                    "action": "Choose a kidney/lesion segmentation method; inspect terms and label conventions.",
                },
                {
                    "id": "S2",
                    "name": "Set up",
                    "action": "Prepare dependencies, checkpoint and local paths.",
                },
                {
                    "id": "S3",
                    "name": "Validate",
                    "action": "Run one case and inspect both masks, native shape, affine and binary values.",
                },
                {
                    "id": "S4",
                    "name": "Infer",
                    "action": "Process all cases; keep patient identity and geometry.",
                },
                {
                    "id": "S5",
                    "name": "Submit",
                    "action": "Write both named NIfTI masks in each patient folder.",
                },
            ],
            "tiers": [
                {
                    "name": "Lite",
                    "help": "Named KiTS19 checkpoint and requirements are supplied; the agent still validates and writes outputs.",
                },
                {
                    "name": "Standard",
                    "help": "Model-choice and comparison guidance is supplied, without Lite's named checkpoint.",
                },
            ],
            "config_budget_seconds": 3600,
            "fixture_scope": audit["fixture_scope"],
            "fixtures": examples,
            "audit_sha256": AUDIT_PIN,
        },
    )
    save_json(
        pack,
        "reference.json",
        {
            "kind": "private source annotation for reader reveal; not model output or solver assistance",
            "source_sha256": PIN["segmentation.nii.gz"],
            "mapping": [
                {"target": "organ.nii.gz", "rule": "source label 1 OR 2", "color": "#1fbbc5"},
                {"target": "lesion.nii.gz", "rule": "source label 2", "color": "#fab738"},
            ],
            "views": reference_views,
            "source_url": "https://raw.githubusercontent.com/neheller/kits19/456b293435b25303bbc7995f094f83a0afdff0eb/data/case_00000/segmentation.nii.gz",
        },
    )
    (pack / "NOTICE.md").write_text(
        "# KiTS19 case_00000 teaching extract\n\n"
        "Source CT and annotation are licensed CC-BY-NC-SA-4.0. Derived 2D PNGs "
        "show three native axial planes under a fixed CT window; no spatial resampling. "
        "The annotation is reader-only and appears solely after explicit reveal. "
        "This local noncommercial teaching pack contains no model prediction or clinical score.\n\n"
        "Official source: https://github.com/neheller/kits19 . Source revisions and "
        "hashes are in manifest.json and the source-resolution receipt.\n"
    )
    (pack / "DATA-LICENSE.txt").write_bytes(DATA_LICENSE.read_bytes())
    assets = []
    for name, role in (
        ("source.json", "illustration"),
        ("output.json", "illustration"),
        ("reference.json", "reader-reference-reveal"),
        ("NOTICE.md", "illustration"),
        ("DATA-LICENSE.txt", "illustration"),
    ):
        p = pack / name
        assets.append(
            {
                "file": name,
                "sha256": digest(p),
                "bytes": p.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": role,
            }
        )
    save_json(
        pack,
        "manifest.json",
        {
            "id": "retained-automed-kidney-v1",
            "frame": "KiTS19-case_00000-IPL",
            "units": "mm",
            "license": "CC-BY-NC-SA-4.0",
            "label_license": "CC-BY-NC-SA-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                "imaging.nii.gz": PIN["imaging.nii.gz"],
                "segmentation.nii.gz": PIN["segmentation.nii.gz"],
                "presentation/external-tasks/sources/automed-kidney-audit.json": AUDIT_PIN,
                ".local/explainers/core-20260929/kidney-source/geometry-review.json": GEOMETRY_PIN,
                ".local/explainers/completion-20260927/039-source/kits19/data/LICENSE": DATA_LICENSE_PIN,
                "scripts/build_automed_kidney_assets.py": digest(Path(__file__)),
            },
            "checks": {
                "native_shape_affine_match": True,
                "native_views": 3,
                "no_spatial_resampling": True,
                "nonclinical_fixtures": 6,
                "saved_prediction": False,
                "model_run": False,
            },
            "assets": assets,
        },
    )
    print("built", pack, "3 native views; 6 pinned nonclinical fixtures")


if __name__ == "__main__":
    main()
