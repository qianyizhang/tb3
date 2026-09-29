"""Build deterministic symbolic PANTHER teaching packs from pinned ReX contracts.

No patient scan, preparer, prediction, scorer, or source label is read or produced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "workbench.toml").is_file())
SOURCE_ROOT = Path(".local/explainers/core-20260929/rex-cellseg-panther-source")
PACKS = {1: "retained-rex-panther-task1-symbolic-v1", 2: "retained-rex-panther-task2-symbolic-v1"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")


def build(root: Path, source_root: Path, receipt_path: Path, output: Path, task: int) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing destination: {output}")
    receipt = json.loads(receipt_path.read_text())
    entry = f"rexmle-panther-task{task}"
    if receipt.get("entry_id") != entry or receipt.get("illustration_basis") != "symbolic":
        raise ValueError("Wrong task receipt or illustration basis")
    if any(not a.get("attempted_at") for a in receipt["attempts"]):
        raise ValueError("Undated source attempt")
    sources = {f"presentation/external-tasks/sources/{entry}-resolution.json": sha(receipt_path)}
    for info in receipt["source_files"]:
        path = source_root / info["path"]
        if sha(path) != info["sha256"]:
            raise ValueError(f"Changed pinned adapter {path}")
        sources[str(path.relative_to(root))] = info["sha256"]
    api = source_root / receipt["official_dataset"]["api_path"]
    if sha(api) != receipt["official_dataset"]["api_sha256"]:
        raise ValueError("Changed official metadata")
    sources[str(api.relative_to(root))] = sha(api)
    code_archive = source_root / receipt["source_archive"]["path"]
    if sha(code_archive) != receipt["source_archive"]["sha256"]:
        raise ValueError("Changed pinned ReX archive")
    sources[str(code_archive.relative_to(root))] = sha(code_archive)
    variant = {
        1: {
            "name": "Diagnostic arterial T1",
            "modality": "contrast-enhanced arterial-phase T1 MRI",
            "scanner": "diagnostic Siemens MRI",
            "image_pattern": "*_0001_0000.mha",
            "label_pattern": "<first-two-ID>.mha",
            "annotated_source_count": 92,
            "conditional_train_count": 73,
            "conditional_test_count": 19,
            "helper": "public train/images and train/labels; optional ImagesTr_unlabeled other-sequence scans if directory exists",
            "domain_boundary": "Unlabeled other-sequence scans are method help, not arterial labels or a paired test reference.",
        },
        2: {
            "name": "Treatment-room MR-Linac T2",
            "modality": "T2 MRI during radiotherapy",
            "scanner": "Elekta Unity MR-Linac",
            "image_pattern": "*_0000.mha",
            "label_pattern": "<patient-ID>.mha",
            "annotated_source_count": 50,
            "conditional_train_count": 40,
            "conditional_test_count": 10,
            "helper": "public train/images and train/labels; task-specific case/scan metadata",
            "domain_boundary": "Task 1 is another imaging domain, not the same patient or a registered current-session label.",
        },
    }[task]
    source = {
        "entry_id": entry,
        "illustration_basis": "symbolic",
        "actual_patient_pixels": False,
        "source_status": "official dataset restricted; no matching native MHA or tumor mask available locally",
        "acquisition_route": "https://zenodo.org/records/15192302",
        "variant": variant,
        "staging_rule": "sort matched ImagesTr/LabelsTr cases; train_test_split(test_size=0.2,random_state=42)",
        "conditional_counts": "counts apply only if all described annotated source cases match; preparer was not executed",
        "public_test": "images only",
        "private_test": "held-out labels and test_labels.csv",
        "mha_geometry": {
            "dimensions": None,
            "spacing_mm": None,
            "origin_mm": None,
            "direction": None,
            "explanation": "native MHA geometry must be read from each acquired image; no patient geometry was invented",
        },
        "label_semantics": {
            "0": "background",
            "1": "tumor target",
            "2": "possible pancreas in source GT; pinned grader extracts GT == 1",
        },
        "license_boundary": {
            "official_record": "cc-by-nc-4.0, restricted access and no redistribution",
            "rex_config": "CC BY-NC-SA 4.0",
            "resolved": False,
        },
    }
    output_schema = {
        "status": "not-retained",
        "prediction": None,
        "submission": None,
        "score": None,
        "csv": "submission/submission.csv",
        "csv_columns": ["image_id", "predicted_mask_path"],
        "relative_prediction_pattern": "predictions/<image_id>.mha",
        "prediction_semantics": "binary 0 background / 1 tumor; one MHA per held-out image_id, expected native input dimensions and geometry",
        "grader": {
            "metrics": ["Dice", "5-mm Surface Dice", "HD95", "MASD", "tumor-volume RMSE"],
            "shape_mismatch": "nearest-neighbor resize of prediction to GT array shape",
            "spacing": "physical surface and volume metrics use prediction-file spacing",
            "affine_origin_direction_equality_checked": False,
            "task2_latency_measured": False,
        },
    }
    # Symbolic unit-grid only. No anatomy, tumor outline or substitute patient scan.
    diagram = {
        "kind": "symbolic-index-operation",
        "frame": "symbolic-unit-grid",
        "units": "unitless",
        "index_grid": [5, 5, 3],
        "index_axes": ["i", "j", "k"],
        "world_formula": "physical_mm = origin_mm + direction_matrix × diag(spacing_mm) × [i,j,k]",
        "target_grid": "same native MHA dimensions and physical metadata as current input",
        "symbols": {
            "input": "unobserved MHA volume",
            "output": "empty binary tumor-mask socket",
            "private": "unobserved held-out label; no reference image asset",
        },
        "patient_geometry_values": None,
    }
    output.mkdir(parents=True)
    dump(output / "source.json", source)
    dump(output / "output.json", output_schema)
    dump(output / "diagram.json", diagram)
    (output / "NOTICE.md").write_text(
        f"# ReX PANTHER Task {task} symbolic teaching pack\n\n"
        "This pack contains no patient scan, tumor mask, derived pixel or result. The official "
        "PANTHER record https://zenodo.org/records/15192302 restricts access and says research "
        "requesters may not redistribute files. Its metadata names CC-BY-NC-4.0; the pinned "
        "ReX config says CC BY-NC-SA 4.0. Those terms are not reconciled here. The diagrams "
        "use unitless indexing only, with deliberately absent native MHA dimensions, spacing, "
        "origin and direction. No preparer, model, grader or trial ran.\n"
    )
    assets = ["source.json", "output.json", "diagram.json", "NOTICE.md"]
    manifest = {
        "schema": 1,
        "id": PACKS[task],
        "frame": "symbolic-unit-grid",
        "units": "unitless",
        "license": "LicenseRef-PANTHER-restricted-unresolved",
        "label_license": None,
        "reference_policy": "no-reference-assets",
        "source_class": "source-derived-teaching",
        "illustration_basis": "symbolic",
        "runtime_geometry": "source-records",
        "sources": sources,
        "checks": {
            "actual_patient_scan": False,
            "actual_tumor_label": False,
            "prediction_or_score": False,
            "reference_asset": False,
        },
        "assets": [
            {
                "file": f,
                "sha256": sha(output / f),
                "bytes": (output / f).stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "illustration",
            }
            for f in assets
        ],
    }
    dump(output / "manifest.json", manifest)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=ROOT)
    p.add_argument("--source-root", type=Path)
    p.add_argument("--receipt", type=Path)
    p.add_argument("--task", type=int, choices=(1, 2), required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    root = args.repo_root.resolve()
    receipt = (
        args.receipt
        or root
        / f"presentation/external-tasks/sources/rexmle-panther-task{args.task}-resolution.json"
    )
    build(
        root,
        (args.source_root or root / SOURCE_ROOT).resolve(),
        receipt.resolve(),
        args.output.resolve(),
        args.task,
    )


if __name__ == "__main__":
    main()
