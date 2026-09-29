"""Build a source-pinned, wholly symbolic BCER brain task explainer pack.

No patient MRI, prediction, annotation, medical tool, or model is generated.
The unit grid is an interface diagram, not an anatomical image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "workbench.toml").is_file())
RESOLUTION = Path("presentation/external-tasks/sources/bcer-brain-resolution.json")
PACK_ID = "retained-bcer-brain-symbolic-v1"
LICENSE = "MIT"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def build(repo_root: Path, output: Path, receipt_override: Path | None = None) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing destination: {output}")
    receipt_path = receipt_override or repo_root / RESOLUTION
    receipt = json.loads(receipt_path.read_text())
    if (
        receipt["entry_id"] != "bcer-short-segment-brain"
        or receipt["illustration_basis"] != "symbolic"
    ):
        raise ValueError("Wrong resolution receipt or illustration basis")
    if any("attempted_at" not in attempt for attempt in receipt["attempts"]):
        raise ValueError("Every acquisition attempt needs attempted_at")
    if receipt["source_commit"] != "d10816712793a9e27f2e70640f9afc06f08a0c5c":
        raise ValueError("Changed BCER commit")
    contract = receipt["task_contract"]
    if contract["required_modalities_all_of"] != ["T1", "T1c", "T2", "FLAIR"]:
        raise ValueError("Changed four-sequence contract")
    if contract["required_artifacts"] != ["seg_path", "wt_mask_path"]:
        raise ValueError("Changed required artifacts")
    license_source = repo_root / "presentation/task-explorer/bcer-workflow/BCER-LICENSE.txt"
    expected_license_sha = next(
        item["sha256"] for item in receipt["sources"] if item["role"] == "BCER-code-license"
    )
    if digest(license_source) != expected_license_sha:
        raise ValueError("Changed BCER MIT license source")

    output.mkdir(parents=True)
    glyphs = {
        "kind": "symbolic-unit-grid",
        "case_pixels": False,
        "patient_anatomy": False,
        "coordinates": "unitless diagram coordinates; no NIfTI affine or claimed voxel size",
        "modalities": [
            {"name": "T1", "alias": "t1_nifti", "tone": "#69a4d9", "slot": 0},
            {"name": "T1c", "alias": "t1c_nifti", "tone": "#ca8fdb", "slot": 1},
            {"name": "T2", "alias": "t2_nifti", "tone": "#80c9b1", "slot": 2},
            {"name": "FLAIR", "alias": "flair_nifti", "tone": "#e5bc70", "slot": 3},
        ],
        "label_key": [
            {"value": 0, "name": "background", "color": "#667484"},
            {"value": 1, "name": "NCR", "color": "#6aafec"},
            {"value": 2, "name": "ED", "color": "#e4b86d"},
            {"value": 4, "name": "ET", "color": "#d477a5"},
        ],
        "whole_tumor_labels": [1, 2, 4],
    }
    operation = {
        "source_commit": receipt["source_commit"],
        "task": receipt["task"],
        "contract": contract,
        "source_roles": receipt["source_roles"],
        "tool_behavior": {
            "normal": "MONAI BraTS bundle with T1c,T1,T2,FLAIR order when dependencies and weights are available",
            "fallback": "If MONAI dependencies fail to load, a heuristic T1c+FLAIR segmentation may be generated; not a learned-model result",
            "observed_execution": False,
        },
        "evaluator_limit": "Stage/path/nonzero checks; no anatomical accuracy metric",
    }
    write_json(output / "diagram.json", glyphs)
    write_json(output / "contract.json", operation)
    (output / "NOTICE.md").write_text(
        "# BCER short brain segmentation symbolic teaching pack\n\n"
        "Source contract: BCER commit d10816712793a9e27f2e70640f9afc06f08a0c5c, "
        "https://github.com/Albertlongzi/BCER. BCER code is MIT licensed.\n\n"
        "The four modality cards are abstract unit grids. They are not MRI, patient anatomy, "
        "model output, or ground truth. No matching local BraTS case, segmentation, or reference "
        "is available. The official BraTS 2021 data-request route is "
        "https://www.med.upenn.edu/cbica/brats2021/.\n\n"
        "The label key and WT union describe source code semantics only. The rendered output "
        "paths are expected file fields, not existing artifacts. No medical tool/model or benchmark "
        "was run to build this pack.\n"
    )
    (output / "BCER-LICENSE.txt").write_bytes(license_source.read_bytes())
    assets = []
    for name in ("diagram.json", "contract.json", "NOTICE.md", "BCER-LICENSE.txt"):
        path = output / name
        assets.append(
            {
                "file": name,
                "sha256": digest(path),
                "bytes": path.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "illustration",
            }
        )
    write_json(
        output / "manifest.json",
        {
            "schema": 1,
            "id": PACK_ID,
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": LICENSE,
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "symbolic",
            "sources": {
                str(RESOLUTION): digest(receipt_path),
                "presentation/task-explorer/bcer-workflow/BCER-LICENSE.txt": digest(license_source),
            },
            "checks": {
                "actual_brain_case": False,
                "model_execution": False,
                "patient_like_pixels": False,
                "reader_reference_asset": False,
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, required=True, help="fresh destination; existing path is rejected"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root; defaults to parent of copied scripts directory",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        help="optional staged receipt for isolated draft build; live integration uses repo-root default",
    )
    args = parser.parse_args()
    build(
        args.repo_root.resolve(),
        args.output.resolve(),
        args.receipt.resolve() if args.receipt else None,
    )
