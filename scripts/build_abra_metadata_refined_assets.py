#!/usr/bin/env python3
"""Build a pinned symbolic ABRA metadata pack without running ABRA or reading DICOM."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ENTRY = "abra-metadata-qa"
RECEIPT = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
BRIEF = f"presentation/external-tasks/briefs/{ENTRY}.md"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def put(path: Path, value: object) -> None:
    path.write_text(
        (
            json.dumps(value, sort_keys=True, indent=2)
            if path.name == "manifest.json"
            else json.dumps(value, sort_keys=True, separators=(",", ":"))
        )
        + "\n"
    )


def build(repo: Path, receipt_path: Path, out: Path, verify_local_sources: bool) -> None:
    raw = receipt_path.read_bytes()
    r = json.loads(raw)
    if r["entry_id"] != ENTRY or r["source_commit"] != "688814615dc368a66276798cb864fe9a587d7e6c":
        raise ValueError("wrong entry/source")
    brief = repo / BRIEF
    if brief.is_file() and sha(brief.read_bytes()) != r["brief_sha256"]:
        raise ValueError("brief pin mismatch")
    if verify_local_sources:
        for pin in r["source_files"]:
            data = (repo / pin["path"]).read_bytes()
            if len(data) != pin["bytes"] or sha(data) != pin["sha256"]:
                raise ValueError(f"source mismatch: {pin['path']}")
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if blob != pin["git_blob_sha1"]:
                raise ValueError(f"Git blob mismatch: {pin['path']}")
    if out.exists():
        raise FileExistsError(out)
    match = re.search(r"https?://[^\s;]+", r["acquisition_route"])
    if not match:
        raise ValueError("missing acquisition URL")
    out.mkdir(parents=True)
    source = {
        k: r.get(k)
        for k in (
            "entry_id",
            "illustration_basis",
            "source_commit",
            "task_contract",
            "source_roles",
            "actual_data_gap",
            "acquisition_route",
            "source_example",
        )
    }
    source["notice"] = {
        "label": "Source manifest; no observed task",
        "text": r["top_warning"],
        "url": match.group(0),
        "link_label": "Pinned ABRA source route",
    }
    put(out / "source.json", source)
    put(
        out / "diagram.json",
        {
            "kind": "record-hierarchy",
            "levels": ["study", "series", "instance"],
            "query_families": r["task_contract"]["families"],
            "rendered_pixels": False,
            "source_example_role": "manifest evidence, not observed task response",
            "answer_field": "submit_answer.arguments.answer",
            "reference_field": "expected_outcome.answer (not packed)",
            "counts": r["source_example"]["counts"],
            "formatting_rule": "distinct Modality values sorted lexicographically, joined by comma + space",
            "comparison_visibility": "Illustrative toy comparison hidden until reader reveal; reset hides it",
        },
    )
    put(
        out / "output.json",
        {
            "status": "not-retained",
            "schema": r["task_contract"]["output"],
            "participant_answer": None,
            "participant_trace": None,
            "score": None,
            "private_reference": None,
            "reference_role": r["source_roles"]["reference"],
            "scorer_limit": r["source_roles"]["scorer"],
        },
    )
    (out / "NOTICE.md").write_text(
        f"# {ENTRY} teaching pack\n\n{r['top_warning']}\n\n{r['actual_data_gap']}\n\nManifest fields are legitimate query material; generated expected_outcome, submission and score are absent.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "ABRA code is MIT-licensed. Local LIDC-IDRI CT archive carries CC BY 3.0 and TCIA usage/attribution terms. No DICOM files or image pixels from that archive are included.\n"
    )
    put(
        out / "formatting-fixture.json",
        {
            "role": "illustrative formatting fixture; authored, not patient/model/reference evidence",
            "input_modalities": ["SR", "CT", "SEG", "CT"],
            "operation": "deduplicate, sort lexicographically, join comma + space",
            "illustrative_formatted_string": "CT, SEG, SR",
            "incorrect_order_control": "SR, CT, SEG",
            "not_a_submission": True,
            "not_an_evaluator_reference": True,
            "comparison_visibility": "Hidden until explicit reader reveal; reset hides comparison; permitted source fields remain visible.",
        },
    )
    assets = []
    for p in sorted(out.iterdir()):
        data = p.read_bytes()
        assets.append(
            {
                "file": p.name,
                "bytes": len(data),
                "sha256": sha(data),
                "role": "illustration",
                "provenance": "symbolic-protocol"
                if p.name == "formatting-fixture.json"
                else "source-derived-teaching",
            }
        )
    put(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-abra-metadata-qa-contract-v2",
            "frame": "symbolic-unit-grid",
            "units": "none",
            "license": "LicenseRef-ABRA-MIT-LIDC-IDRI-CC-BY-3.0-metadata-teaching",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "no-reference-assets",
            "checks": {
                "patient_pixels": False,
                "participant_output": False,
                "private_reference_asset": False,
                "model_execution": False,
                "viewer_execution": False,
                "scorer_execution": False,
            },
            "sources": {RECEIPT: sha(raw), BRIEF: r["brief_sha256"]},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", required=True, type=Path)
    p.add_argument("--receipt", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--verify-local-sources", action="store_true")
    a = p.parse_args()
    build(a.repo_root.resolve(), a.receipt.resolve(), a.output.resolve(), a.verify_local_sources)
