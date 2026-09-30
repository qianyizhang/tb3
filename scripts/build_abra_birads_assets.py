"""Build one mixed metadata/symbolic BI-RADS pack, without running source code."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    root = a.source_root.resolve()
    receipt = json.loads(a.receipt.read_text())
    if receipt["entry_id"] != "abra-birads":
        raise ValueError("Wrong entry receipt")
    for pin in receipt["source_pins"]:
        path = root / pin["path"]
        raw = path.read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError(f"Stale source pin: {path}")
        if pin.get("git_blob_sha1"):
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != pin["git_blob_sha1"]:
                raise ValueError(f"Stale source Git blob: {path}")
    manifest_pin = next(
        x for x in receipt["source_pins"] if x["path"].endswith("study_manifest.json")
    )
    data = json.loads((root / manifest_pin["path"]).read_text())
    study = next(
        s for s in data["datasets"]["duke_breast"]["studies"] if s["patient_id"] == "Breast_MRI_008"
    )
    if study["study_uid"] != receipt["source_example"]["study_uid"]:
        raise ValueError("Source identity mismatch")
    # Read constants by AST; never import authoring code that can mutate source artifacts.
    scorer_pin = next(
        x for x in receipt["source_pins"] if x["path"].endswith("birads_report_scorer.py")
    )
    tree = ast.parse((root / scorer_pin["path"]).read_text())
    weights = next(
        ast.literal_eval(n.value)
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "FIELD_WEIGHTS" for t in n.targets)
    )
    if weights != {
        "laterality": 0.25,
        "birads_category": 0.30,
        "lesion_count": 0.20,
        "enhancement_present": 0.15,
        "lesion_quadrant": 0.10,
    }:
        raise ValueError("Scorer weight constants changed")
    out = a.output.resolve()
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)

    def put(name: str, value: object) -> None:
        (out / name).write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")

    put(
        "source.json",
        {
            "notice": {
                "label": "Mixed metadata and symbolic workflow",
                "text": receipt["top_warning"],
                "url": receipt["acquisition_route"],
                "link_label": "Official Duke MRI acquisition",
            },
            "basis": "mixed",
            "role": "public-series-metadata-not-task-image",
            "study": {"patient_id": study["patient_id"], "study_uid": study["study_uid"]},
            "series": study["series"],
            "ordering": "Pinned manifest order only; not DCE acquisition time or anatomical alignment",
            "pixels": None,
            "generated_task": None,
        },
    )
    put(
        "operation.json",
        {
            "conditions": [
                {
                    "id": "visual",
                    "label": "Visual assessment",
                    "vision": True,
                    "max_turns": 20,
                    "steps": [
                        "get_study_series",
                        "select_series",
                        "set_viewport_slice + get_dicom_image",
                        "submit_birads_report",
                    ],
                    "assistance": "Series metadata, viewer navigation and breast_mri display preprocessor",
                    "remaining": "Inspect actual images and formulate report; unavailable here",
                },
                {
                    "id": "oracle",
                    "label": "Oracle findings",
                    "vision": False,
                    "max_turns": 10,
                    "steps": [
                        "get_study_series",
                        "query_birads_model(series_uid=matching DCE UID)",
                        "submit_birads_report",
                    ],
                    "assistance": "Task oracle_data returns report-derived answer fields; no CAD inference",
                    "remaining": "Query correct UID and relay fields; oracle response unavailable here",
                },
            ],
            "terminal_action": "submit_birads_report",
            "preprocessor": "Conditional rescale and per-image 1st/99th percentile MRI window; no HU/enhancement measurement",
            "visual_reference_trajectory": "get_study_series; min(MR series count,4) selected series; 3 slice/image pairs per series; submit report",
            "executed": False,
        },
    )
    put(
        "output.json",
        {
            "role": "required-report-schema-only",
            "fields": ["laterality", "lesion_count", "birads_category", "enhancement_present"],
            "optional_quadrant": "findings[0].location_quadrant",
            "values": {
                "laterality": None,
                "lesion_count": None,
                "birads_category": None,
                "enhancement_present": None,
            },
            "submitted_report": None,
            "oracle_response": None,
            "score": None,
            "private_reference": None,
            "weights": weights,
            "denominator_without_quadrant": 0.90,
            "denominator_with_quadrant": 1.0,
            "unscored": ["findings morphology and size", "recommendation"],
        },
    )
    put(
        "derivation.json",
        {
            "role": "general-source-code-policy-not-patient-reference",
            "private_reference": None,
            "rules": receipt["task_contract"]["reference_derivation"],
            "constructed_constants": {"birads_category": 5, "enhancement_present": True},
            "warning": "General code rules only. No Breast_MRI_008 target, image finding or radiologist assessment is claimed.",
            "category_credit": "For expected 5/6, actual 5/6 receives full category credit; actual 4 gets 0.5 and actual 3 gets 0.2. This is an agreement rule, not clinical correctness.",
            "count_credit": "Exact count gets full credit; ±1 gets 0.5.",
            "laterality_caveat": "Missing expected laterality is assigned full credit by source scorer.",
            "quadrant_credit": "Only when expected lesion_quadrant exists; reads first finding location_quadrant, normalized uppercase.",
            "score_boundary": "Latest successful submit_birads_report arguments; weighted sum divided by included weights, rounded to four decimals; no observed score.",
        },
    )
    (out / "NOTICE.md").write_text(
        receipt["top_warning"]
        + "\n"
        + receipt["acquisition_route"]
        + "\nNo private reference or patient image included; derivation is general source-code policy.\n"
    )
    terms = receipt["license_context"]
    (out / "DATA-LICENSE.txt").write_text(
        "ABRA code/manifest metadata: MIT at 688814615dc368a66276798cb864fe9a587d7e6c.\nDuke collection source: CC BY-NC 4.0, https://creativecommons.org/licenses/by-nc/4.0/ . Local noncommercial interpretation only; no images or clinical spreadsheet packaged.\n"
        + terms["official_dataset_citation"]
        + "\nOfficial collection: "
        + terms["collection_url"]
        + "\nSource metadata is quoted from ABRA study_manifest; labels and target-construction diagrams are original task-specific teaching records, not patient findings.\n"
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "derivation.json",
        "operation.json",
        "output.json",
        "source.json",
    ]
    assets = [
        {
            "file": name,
            "bytes": (out / name).stat().st_size,
            "sha256": hashlib.sha256((out / name).read_bytes()).hexdigest(),
            "provenance": "source-derived-teaching",
            "role": "illustration",
        }
        for name in names
    ]
    put(
        "manifest.json",
        {
            "id": "retained-abra-birads-contract-v1",
            "frame": "ABRA-series-manifest-plus-symbolic-report",
            "units": "unitless",
            "license": "LicenseRef-ABRA-MIT-plus-Duke-CC-BY-NC-4.0",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "mixed",
            "sources": {
                "presentation/external-tasks/sources/abra-birads-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest()
            },
            "assets": assets,
            "checks": {
                "patient_pixels": False,
                "model_run": False,
                "scorer_run": False,
                "private_reference": False,
                "oracle_query": False,
            },
        },
    )


if __name__ == "__main__":
    main()
