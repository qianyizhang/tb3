#!/usr/bin/env python3
"""Build a source-pinned symbolic BCER cardiac workflow; never run upstream tools."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "bcer-long-cardiac-full"
RECEIPT_KEY = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def put_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    root = next((p for p in Path(__file__).resolve().parents if (p / ".git").exists()), None)
    if root is None:
        raise RuntimeError("repository root unavailable")
    receipt = json.loads(a.receipt.read_text())
    if receipt["entry_id"] != ENTRY:
        raise ValueError("wrong receipt")
    for pin in receipt["source_pins"]:
        raw = (root / pin.get("local_path", pin["path"])).read_bytes()
        if len(raw) != pin["bytes"] or sha(raw) != pin["sha256"]:
            raise ValueError(f"source pin mismatch: {pin['path']}")
        if pin.get("git_blob_sha"):
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != pin["git_blob_sha"]:
                raise ValueError(f"Git blob mismatch: {pin['path']}")
    out = a.output.resolve()
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    put_json(
        out / "source.json",
        {
            "title": ENTRY,
            "role": "symbolic-case-input",
            "modalities": ["cine NIfTI", "or raw cine H5"],
            "case_bytes": None,
            "native_geometry": None,
            "reference": None,
            "notice": {
                "label": "Symbolic BCER cardiac workflow; source case unavailable",
                "text": receipt["top_warning"],
                "url": receipt["acquisition_route"],
                "link_label": "Official ACDC data route",
            },
        },
    )
    put_json(
        out / "operation.json",
        {
            "type": "source-code-derived-static-operation",
            "operation_observed": False,
            "stages": receipt["task_contract"]["required_stage_success"],
            "conditional_branch": "Raw cine H5 requires reconstruction to NIfTI; cine NIfTI enters segmentation directly. Reconstruction is not a required-success stage.",
            "feature_dependency": "ROI-feature CSV and classifier JSON are parallel outputs from segmentation; classifier computes from masks, not that CSV.",
            "phase_modes": [
                {
                    "id": "single_3d",
                    "label": "One 3D phase",
                    "behavior": "No temporal curve; one frame may serve as both ED and ES.",
                },
                {
                    "id": "cine_4d_with_info",
                    "label": "4D with valid Info.cfg ED/ES",
                    "behavior": "1-based phase values select source frames; classifier records zero-based indices.",
                },
                {
                    "id": "cine_4d_without_info",
                    "label": "4D without valid ED/ES",
                    "behavior": "Segment all frames by default; classifier may use LV-volume extrema.",
                },
            ],
            "segmentation": receipt["segmentation_mechanism"],
            "classifier": receipt["classifier_mechanism"],
            "report": receipt["report_mechanism"],
        },
    )
    put_json(
        out / "output.json",
        {
            "role": "required-schema-only",
            "path": "BCER artifact registry",
            "schema": {
                "seg_path": None,
                "feature_table_path": None,
                "classification_path": None,
                "report_json_path": None,
            },
            "prediction": None,
            "score": None,
            "reference": None,
            "invariants": [i["id"] for i in receipt["task_contract"]["invariants"]],
            "checks": "Five required tool successes plus four artifact paths form TCR denominator nine; separate tool-success and file invariants. No clinical accuracy check.",
            "observed_result": False,
        },
    )
    (out / "NOTICE.md").write_text(
        receipt["top_warning"] + "\n" + receipt["acquisition_route"] + "\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Original symbolic teaching text derived from pinned MIT-licensed BCER code. No ACDC/M&Ms patient images or labels included.\n"
    )
    assets = [
        {
            "file": p.name,
            "bytes": len(p.read_bytes()),
            "sha256": sha(p.read_bytes()),
            "role": "illustration",
            "provenance": "source-derived-teaching",
        }
        for p in sorted(out.iterdir())
    ]
    put_json(
        out / "manifest.json",
        {
            "id": "retained-bcer-long-cardiac-full-workflow-v1",
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
            "sources": {RECEIPT_KEY: sha(a.receipt.read_bytes())},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
