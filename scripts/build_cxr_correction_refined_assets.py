#!/usr/bin/env python3
"""Build a text-only CXR correction teaching pack from pinned task metadata.

Source bytes are read only to verify hashes; no patient data, task module,
report judge, preparer, evaluator, or credential file is opened or executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CANONICAL_RECEIPT = (
    "presentation/external-tasks/sources/healthagentbench-cxr-correction-resolution.json"
)
PACK_ID = "retained-healthagentbench-cxr-correction-interpretation-v1"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(obj: object) -> bytes:
    return (
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    repo = next(
        (p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()), None
    )
    if repo is None:
        raise RuntimeError("tb3 repository root unavailable")
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(f"refusing existing output: {out}")
    receipt_bytes = args.receipt.resolve().read_bytes()
    receipt = json.loads(receipt_bytes)
    if (
        receipt.get("entry_id") != "healthagentbench-cxr-correction"
        or receipt.get("illustration_basis") != "symbolic"
    ):
        raise ValueError("wrong source receipt")
    pins = receipt["source_pins"]
    if len(pins) != 11 or not all(p.get("local_path") for p in pins):
        raise ValueError("expected 11 explicit local source pins")
    for pin in pins:
        path = repo / pin["local_path"]
        data = path.read_bytes()
        if len(data) != pin["bytes"] or digest(data) != pin["sha256"]:
            raise ValueError(f"source pin mismatch: {pin['path']}")
        git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if git_blob != pin["git_blob"]:
            raise ValueError(f"Git blob mismatch: {pin['path']}")
    source = {
        "role": "symbolic-input-socket",
        "title": "CXR correction case_01 · patient input absent",
        "target_rule": "highest-numbered study folder is current target",
        "manifest_study_count": 12,
        "manifest_prior_study_count": 11,
        "manifest_target_study_count": 1,
        "manifest_counts_are_not_loaded_patient_files": True,
        "current_views": None,
        "prior_views_and_reports": None,
        "target_non_generated_sections_and_draft_findings": None,
        "private_original_target_findings": None,
        "official_report_route": "https://physionet.org/content/mimic-cxr/2.1.0/",
        "official_jpg_route": "https://physionet.org/content/mimic-cxr-jpg/2.1.0/",
        "notice": {
            "label": "Patient CXR and draft unavailable",
            "text": "MIMIC-CXR reports and MIMIC-CXR-JPG views require credentialed access. This is an authored clause-editing protocol with no patient image, report text, answer, judge call, or score.",
            "url": "https://physionet.org/content/mimic-cxr/2.1.0/",
            "link_label": "Official MIMIC-CXR access",
        },
    }
    operation = {
        "type": "constrained-existing-findings-clause-edit",
        "authored_placeholder_clauses": ["Existing draft clause A", "Existing draft clause B"],
        "patient_findings": None,
        "evidence_choices": ["unchecked", "supported", "conflict_or_unsupported"],
        "actions": ["keep_existing", "correct_existing", "remove_existing"],
        "new_finding_action_allowed": False,
        "output_section": "FINDINGS only",
        "reference_only_gold": None,
        "judge_rule": {
            "default_calls": 5,
            "default_required_zero_significant_error_votes": 3,
            "environment_overrides": ["CHEXPROMPT_VOTES", "CHEXPROMPT_PASS_THRESHOLD"],
            "observed_votes": None,
        },
    }
    output = {
        "role": "required-schema-only",
        "path": "/workspace/submission.json",
        "schema": {
            "container": "one JSON list row",
            "task_id": "case_01",
            "final_answer": "literal FINDINGS: header on its own line, followed only by edited existing claims",
        },
        "prediction": None,
        "reference": None,
        "score": None,
    }
    files = {
        "source.json": encoded(source),
        "operation.json": encoded(operation),
        "output.json": encoded(output),
        "NOTICE.md": b"Symbolic CXR correction protocol only; no patient image or report text, answer, judge call, or score. Credentialed MIMIC-CXR reports and MIMIC-CXR-JPG views are not included. https://physionet.org/content/mimic-cxr/2.1.0/\n",
        "DATA-LICENSE.txt": b"LicenseRef-TB3-symbolic-teaching\nAuthored task diagram and text only; no PhysioNet patient asset or report derivative.\n",
    }
    manifest = {
        "id": PACK_ID,
        "frame": "symbolic-task-workflow",
        "units": "none",
        "license": "LicenseRef-TB3-symbolic-teaching",
        "label_license": "LicenseRef-TB3-symbolic-teaching",
        "reference_policy": "no-reference-assets",
        "checks": {
            "native_input": False,
            "private_reference": False,
            "model_run": False,
            "evaluator_run": False,
        },
        "sources": {CANONICAL_RECEIPT: digest(receipt_bytes)},
        "assets": [
            {
                "file": name,
                "bytes": len(data),
                "sha256": digest(data),
                "provenance": "symbolic-protocol",
                "role": "illustration",
            }
            for name, data in sorted(files.items())
        ],
    }
    out.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        (out / name).write_bytes(data)
    (out / "manifest.json").write_bytes(encoded(manifest))
    print(out)


if __name__ == "__main__":
    main()
