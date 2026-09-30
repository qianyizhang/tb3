#!/usr/bin/env python3
"""Create the source-code-derived symbolic BCER long-brain pack in a fresh path.

This verifies retained code bytes; it never invokes BCER tools, a model or an evaluator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "bcer-long-brain-full"
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
    repo = next(
        (
            p
            for p in Path(__file__).resolve().parents
            if (p / "presentation/EXPLAINER-SCOPE.json").exists()
        ),
        None,
    )
    if repo is None:
        raise RuntimeError("repository root not found")
    receipt_bytes = args.receipt.read_bytes()
    receipt = json.loads(receipt_bytes)
    if receipt["entry_id"] != ENTRY:
        raise ValueError("wrong entry receipt")
    brief = repo / receipt["brief"]["path"]
    if brief.is_file() and digest(brief.read_bytes()) != receipt["brief"]["sha256"]:
        raise ValueError("canonical brief pin mismatch")
    for pin in receipt["source_pins"]:
        raw = (repo / pin["path"]).read_bytes()
        if len(raw) != pin["bytes"] or digest(raw) != pin["sha256"]:
            raise ValueError(f"source pin mismatch: {pin['path']}")
        if "git_blob_sha" in pin:
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != pin["git_blob_sha"]:
                raise ValueError(f"Git blob mismatch: {pin['path']}")
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    contract = receipt["task_contract"]
    write_json(
        out / "source.json",
        {
            "role": "symbolic-case-input",
            "title": ENTRY,
            "modalities": ["T1", "T1c", "T2", "FLAIR"],
            "case_bytes": None,
            "native_geometry": None,
            "reference": None,
            "notice": {
                "label": "Symbolic BCER workflow; source case unavailable",
                "text": receipt["top_warning"],
                "url": receipt["acquisition_route"],
                "link_label": "Official BraTS data route",
            },
        },
    )
    write_json(
        out / "operation.json",
        {
            "role": "source-code-derived-static-operation",
            "type": "ordered-tool-chain",
            "stages": contract["required_stage_success"],
            "conditional_branch": "register T2/FLAIR to T1c only if not already co-registered",
            "feature_dependency": "ROI features require a segmentation; the rule-based grade consumes those features",
            "operation_observed": False,
            "observed_trace": None,
            "required_stages": contract["required_stage_success"],
            "conditional_registration": contract["conditional_registration"],
            "segmentation_fallback": contract["segmentation_fallback"],
            "grade_rule": contract["grade_rule"],
            "report_consumption": contract["report_consumption"],
            "tcr_checks": contract["tcr_checks"],
            "success_rule_tool_checks": contract["success_rule_tool_checks"],
            "invariant_checks": contract["invariant_checks"],
        },
    )
    write_json(
        out / "output.json",
        {
            "role": "required-schema-only",
            "path": "BCER artifact registry",
            "schema": {key["data_key"]: None for key in contract["required_artifacts"]},
            "prediction": None,
            "reference": None,
            "invariants": [key["id"] for key in contract["invariants"]],
            "checks": "five stages + five artifact paths; seven invariants; no case-level accuracy metric",
            "seg_path": None,
            "wt_mask_path": None,
            "feature_table_path": None,
            "classification_path": None,
            "predicted_grade": None,
            "report_json_path": None,
            "tool_trace": None,
            "score": None,
            "expert_mask": None,
            "true_grade": None,
            "observed_result": False,
        },
    )
    (out / "NOTICE.md").write_text(
        receipt["top_warning"] + "\n" + receipt["acquisition_route"] + "\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Original symbolic teaching text derived from pinned MIT-licensed BCER code. No BraTS patient data or labels included.\n"
    )
    assets = []
    for path in sorted(out.iterdir()):
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
        out / "manifest.json",
        {
            "id": "retained-bcer-long-brain-full-workflow-v1",
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
            "sources": {RECEIPT_KEY: digest(receipt_bytes)},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
