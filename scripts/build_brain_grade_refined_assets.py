#!/usr/bin/env python3
"""Build a symbolic, source-pinned BCER brain-grade teaching pack; never run BCER tools."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "bcer-medium-brain-grade-classify"
RECEIPT_KEY = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = next((p for p in Path(__file__).resolve().parents if (p / ".git").exists()), None)
    if repo is None:
        raise RuntimeError("repository root not found")
    receipt = json.loads(args.receipt.read_text())
    if receipt["entry_id"] != ENTRY:
        raise ValueError("wrong entry receipt")
    for pin in receipt["source_pins"]:
        raw = (repo / pin.get("local_path", pin["path"])).read_bytes()
        if len(raw) != pin["bytes"] or digest(raw) != pin["sha256"]:
            raise ValueError(f"source pin mismatch: {pin['path']}")
        if "git_blob_sha" in pin:
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != pin["git_blob_sha"]:
                raise ValueError(f"Git blob mismatch: {pin['path']}")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    write_json(
        output / "source.json",
        {
            "role": "symbolic-case-input",
            "modalities": ["T1", "T1c", "T2", "FLAIR"],
            "case_bytes": None,
            "native_geometry": None,
            "notice": {
                "label": "Symbolic BCER workflow; source case unavailable",
                "text": receipt["top_warning"],
                "url": receipt["acquisition_route"],
                "link_label": "Official BraTS data route",
            },
            "reference": None,
        },
    )
    write_json(
        output / "operation.json",
        {
            "role": "source-code-derived-static-operation",
            "observed_trace": None,
            "stages": [
                {
                    "id": "identify_sequences",
                    "input": "case manifest",
                    "produces": "four modality bindings",
                    "check": "required stage success",
                },
                {
                    "id": "brats_mri_segmentation",
                    "input": "matched T1/T1c/T2/FLAIR",
                    "produces": "tumor ROI mask",
                    "check": "required stage success",
                },
                {
                    "id": "extract_roi_features",
                    "input": "mask and sequence grids",
                    "produces": "feature-table CSV",
                    "check": "stage success; CSV at least one row",
                },
                {
                    "id": "classify_brain_glioma_grade",
                    "input": "feature-table CSV",
                    "produces": "classification JSON",
                    "check": "stage success; nonempty predicted_grade field",
                },
            ],
            "feature_rule": receipt["feature_tool_rule"],
            "grade_rule": receipt["grade_tool_rule"],
            "structural_score": receipt["structural_score_boundary"],
        },
    )
    write_json(
        output / "output.json",
        {
            "role": "empty-participant-output-schema",
            "path": "feature_table_path CSV + classification_path JSON",
            "schema": {
                "feature_table_path": "CSV with at least one data row",
                "classification_path": "JSON with nonempty predicted_grade",
            },
            "prediction": None,
            "score": None,
            "reference": None,
            "feature_table_path": None,
            "classification_path": None,
            "predicted_grade": None,
            "tool_trace": None,
            "structural_tcr": None,
            "true_grade": None,
            "accuracy": None,
            "observed_result": False,
        },
    )
    (output / "NOTICE.md").write_text(
        receipt["top_warning"] + "\n" + receipt["acquisition_route"] + "\n"
    )
    (output / "DATA-LICENSE.txt").write_text(
        "Original symbolic teaching text derived from pinned MIT-licensed BCER code. No BraTS patient data or labels included.\n"
    )
    assets = []
    for path in sorted(output.iterdir()):
        raw = path.read_bytes()
        assets.append(
            {
                "file": path.name,
                "bytes": len(raw),
                "sha256": digest(raw),
                "role": "illustration",
                "provenance": "source-derived-teaching",
            }
        )
    write_json(
        output / "manifest.json",
        {
            "id": "retained-bcer-medium-brain-grade-classify-workflow-v1",
            "frame": "symbolic-task-workflow",
            "units": "none",
            "license": "LicenseRef-BCER-MIT-symbolic-teaching",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "checks": {
                "native_input": False,
                "private_reference": False,
                "model_run": False,
                "evaluator_run": False,
            },
            "sources": {RECEIPT_KEY: digest(args.receipt.read_bytes())},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
