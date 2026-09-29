#!/usr/bin/env python3
"""Build the BR-018 symbolic protocol pack. No patient, report or answer data."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = next(
    parent for parent in Path(__file__).resolve().parents if (parent / "workbench.toml").is_file()
)
STAGE = Path(__file__).resolve().parents[1]
WARNING = {
    "label": "Symbolic illustration — no CT/report pair has been admitted;",
    "text": "request candidate data through the",
    "url": "https://huggingface.co/datasets/ibrahimhamamci/CT-RATE",
    "link_label": "Official CT-RATE access page",
}
SOURCES = [
    "groups/longitudinal-reading/presentation/sources/report-backed-reading-audit.json",
    "groups/longitudinal-reading/presentation/briefs/tb3-report-backed-reading.md",
    "groups/longitudinal-reading/presentation/sources/report-backed-reading-resolution.json",
    "groups/longitudinal-reading/ideas/report-backed-diagnostic-reading.md",
    "docs/research-rounds/BR-018-report-backed-diagnosis.md",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(out, name, value, role):
    data = (json.dumps(value, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
    (out / name).write_bytes(data)
    return {
        "file": name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "provenance": "source-derived-teaching",
        "role": role,
    }


def build(out):
    out.mkdir(parents=True, exist_ok=False)
    pins = {rel: sha((STAGE / rel) if (STAGE / rel).exists() else (ROOT / rel)) for rel in SOURCES}
    source = {
        "kind": "BR-018-proposed-symbolic-input",
        "warning": WARNING,
        "admitted_pairs": 0,
        "model_trials": 0,
        "actual_volume": None,
        "actual_report": None,
        "patient_claims": None,
        "viewer_roles": [
            "axial",
            "coronal",
            "sagittal",
            "window-level",
            "orientation-aware location",
        ],
        "context_slots": ["age", "sex", "indication", "technique", "available comparisons"],
        "location_convention": "RAS millimetres proposed; no case affine or numeric coordinates verified",
        "solver_visible": "Complete native examination and only verified pre-exam context if a case is later admitted",
        "private_not_input": [
            "original report",
            "source/patient mapping",
            "curator claim table",
            "target labels",
        ],
    }
    output = {
        "kind": "BR-018-proposed-empty-answer-schema",
        "is_actual_answer": False,
        "filename": "answer.json",
        "empty_fields": {
            "findings": [],
            "impression": [],
            "limitations": [],
            "evidence_summary": [],
        },
        "finding_slots": ["observation", "location", "certainty", "evidence"],
        "certainty_vocabulary": ["present", "possible", "indeterminate"],
        "evidence_location_slots": ["image filename", "view and slice OR physical RAS-mm location"],
        "counts_or_scores": None,
    }
    reference = {
        "kind": "BR-018-private-evaluator-schema-only",
        "is_actual_report": False,
        "claim_slots": ["exact report excerpt", "anatomy", "negation", "uncertainty", "laterality"],
        "source_claim_routes": ["matched", "missed", "contradicted", "unresolved"],
        "solver_addition_routes": [
            "supported",
            "explicitly contradicted",
            "unmentioned-needs-review",
        ],
        "rule": "Report silence alone is not evidence that an image-grounded addition is false.",
        "proposed_controls": [
            "empty",
            "indiscriminately positive",
            "deliberately contradictory",
            "copied-reference host-only baseline",
        ],
        "control_results": None,
    }
    assets = [
        write(out, "source.json", source, "illustration"),
        write(out, "output.json", output, "illustration"),
        write(out, "reference.json", reference, "reader-reference-reveal"),
    ]
    notice = (
        "# BR-018 symbolic protocol teaching pack\n\n"
        "No patient CT, report, paired case, model answer, clinical finding or score is included. "
        "The case count and trial count are both zero. All diagrams and schema cards are symbolic. "
        "The proposed original report and curator claims belong to a private evaluator, not solver input. "
        "The official CT-RATE dataset is gated; request access at "
        "https://huggingface.co/datasets/ibrahimhamamci/CT-RATE. "
        "A clinical report is a fallible report-concordance reference, not independent pathology truth.\n"
    )
    path = out / "NOTICE.md"
    path.write_text(notice)
    raw = path.read_bytes()
    assets.append(
        {
            "file": "NOTICE.md",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "provenance": "source-derived-teaching",
            "role": "illustration",
        }
    )
    manifest = {
        "schema": 1,
        "id": "symbolic-report-reading-v1",
        "frame": "abstract-orientation-only",
        "units": "none",
        "license": "LicenseRef-TB3-symbolic-teaching",
        "label_license": "LicenseRef-TB3-symbolic-teaching",
        "reference_policy": "reader-reference-reveal",
        "sources": pins,
        "checks": {
            "admitted_pairs": 0,
            "model_trials": 0,
            "native_patient_assets": 0,
            "model_execution": False,
        },
        "assets": assets,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, separators=(",", ":")) + "\n")
    print(f"wrote symbolic pack {out}; {len(pins)} document pins; 0 patient assets")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output)
