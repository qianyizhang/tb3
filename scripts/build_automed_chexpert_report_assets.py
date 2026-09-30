"""Build a source-pinned symbolic report contract without importing the harness."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml

ENTRY = "automedbench-full-chexpert-plus-cxr-task"
PACK = "symbolic-automed-chexpert-report-v1"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    root = a.source_root.resolve()
    r = json.loads(a.receipt.read_text())
    if r["entry_id"] != ENTRY:
        raise ValueError("Wrong receipt")
    for row in r["source_pins"]:
        raw = (root / row["path"]).read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("Stale source pin: " + row["path"])
    cfgpin = next(
        x
        for x in r["source_pins"]
        if x["path"].endswith("/tasks/chexpert-plus-cxr-task/config.yaml")
    )
    cfg = yaml.safe_load((root / cfgpin["path"]).read_text())
    schemapin = next(x for x in r["source_pins"] if x["path"].endswith("/cxr_12class.yaml"))
    schema = yaml.safe_load((root / schemapin["path"]).read_text())
    if (
        cfg["grouping_unit"] != "study"
        or cfg["input_format"] != "jpg"
        or cfg["clinical_score_backend"] != "lightweight"
    ):
        raise ValueError("Unexpected task contract")
    if cfg["agent_output_subdir"] != "agent_outputs" or cfg["output_filename"] != "report.txt":
        raise ValueError("Unexpected output path")
    out = a.output.resolve()
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)

    def put(name, obj):
        (out / name).write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")

    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "symbolic",
            "input": "public/<case_id>/images/frontal JPEG",
            "unit": cfg["grouping_unit"],
            "pixels": None,
            "case_ids": None,
            "patient_join": None,
            "partition": "configured test_100_v1; actual discovered case count absent",
            "original_boundary": "Stanford original DICOM differs from named mirror frontal JPEG; no physical scale/orientation inferred",
            "model_output": None,
            "private_reference": None,
        },
    )
    put(
        "helper.json",
        {
            "classes": list(schema["labels"]),
            "schema_boundary": "12 binary text regex concepts differ from original14 CheXpert labels; no image-derived finding or patient answer",
            "rules": "Positive match without any global negative match =>1. Uncertain wording may match positive; no ternary uncertainty interpretation.",
            "tiers": {
                "lite": "Source names CheXagent-2-3b single-frontal report path; weights/availability unverified.",
                "standard": "Source asks comparison of at least two named report candidates; gated access and weights remain provisioning work.",
            },
            "patient_labels": None,
            "training_labels": "No verified public training annotation retained; current mirror rows are validation, never held-out Full answers.",
        },
    )
    put(
        "operation.json",
        {
            "steps": [
                "Verify single frontal view and staged case identity",
                "Provision tier method and its preprocessing",
                "Generate report under text constraints",
                "Submit every discovered case without reading private references",
            ],
            "executed": False,
        },
    )
    put(
        "output.json",
        {
            "path": cfg["agent_output_subdir"] + "/<case_id>/" + cfg["output_filename"],
            "text": None,
            "format": "UTF8 decode + ASCII printable characters; 40..8000 chars, >=20 alphabetic, nonblank",
            "completeness": "Every discovered case valid and count>0; any missing/invalid => rating F and zeroed aggregate clinical components",
            "macro": ".7 mean per-case observation F1 + .3 mean per-case ROUGE-L F1; all case_ids denominator, max(n,1)",
            "micro": "Pool TP/FP/FN across cases; separate diagnostic, not configured clinical score; raw values may persist after gate",
            "selector": "Nonempty Findings preferred; otherwise entire report. No separate Impression selection.",
            "empty_positive": "Both positive sets empty => F1=1 convention; no result observed",
            "workflow": "S1-S3 default0 absent optional judge; weights .25/.15/.35/.15/.10",
            "overall": ".5 workflow + .5 lightweight clinical_score; valid required, .80/.55 rating thresholds",
            "boundary": "Text regex agreement/ROUGE are proxies, not independent clinical image interpretation or patient benefit",
            "private_reference": None,
            "score": None,
            "rating": None,
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nNo patient image/report, private label, model output or metric included.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "LicenseRef-TB3-symbolic-teaching: original task-specific teaching records. Underlying CheXpert Plus/Mirror terms unresolved; no patient image or narrative redistributed. Full envelope holds release until Stanford terms/source revision recorded.\nOfficial acquisition: "
        + r["acquisition_route"]
        + "\n"
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "helper.json",
        "operation.json",
        "output.json",
        "source.json",
    ]
    assets = [
        {
            "file": name,
            "bytes": (out / name).stat().st_size,
            "sha256": hashlib.sha256((out / name).read_bytes()).hexdigest(),
            "provenance": "symbolic-protocol",
            "role": "illustration",
        }
        for name in names
    ]
    put(
        "manifest.json",
        {
            "id": PACK,
            "frame": "symbolic-case-workflow",
            "units": "unitless",
            "license": "LicenseRef-TB3-symbolic-teaching",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "symbolic",
            "sources": {
                "presentation/external-tasks/sources/" + ENTRY + "-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest()
            },
            "assets": assets,
            "checks": {
                "patient_pixels": False,
                "model_run": False,
                "scorer_run": False,
                "private_reference": False,
            },
        },
    )


if __name__ == "__main__":
    main()
