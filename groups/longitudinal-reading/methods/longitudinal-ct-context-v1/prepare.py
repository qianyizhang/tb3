"""Prepare fresh context conditions from verified frozen bytes; no historical authoring import."""

import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).parent
BASE = ROOT / ".local/longitudinal-ct-context-v1"
OLD = ROOT / ".local/longitudinal-ct-case02"
SOURCE = (
    ROOT / ".local/freezes/e12f6fc10c83c8dfb2bc4ca3bd4cfffc90811bdb7249ad8ddedcf55655b1083a/task"
)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    assert not BASE.exists(), "Never overwrite prepared context study"
    manifest = json.loads((OLD / "task-files.json").read_text())
    for name, digest in manifest.items():
        assert sha(SOURCE / name) == digest, name
    demographics = ROOT / ".local/longitudinal-ct-review/raw/LongitudinalCT_demographics.csv"
    row = next(r for r in csv.DictReader(demographics.open()) if r["ID"] == "bcbe3365e6")
    assert (row["age"], row["sex"], float(row["TimeDiff_BL_FU1_Days"])) == ("44", "female", 121.0)
    BASE.mkdir(parents=True)
    source_record = OLD / "source/record-v3-current.json"
    provenance = {
        "source_task": "codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5",
        "decision": "decision-0025c01d8f434bf6",
        "baseline_attempt": "attempt-92800845745342f4",
        "patient": row["ID"],
        "demographics_file": str(demographics.relative_to(ROOT)),
        "demographics_sha256": sha(demographics),
        "demographics_row": row,
        "source_record_sha256": sha(source_record),
        "sources": [
            "https://fdat.uni-tuebingen.de/records/qe950-g4h94",
            "https://www.nature.com/articles/s41597-026-07466-y",
        ],
        "live_source_review_date": "2026-09-22",
        "field_provenance": {
            "age_years": {"value": 44, "level": "patient CSV", "reference_date": "unspecified"},
            "recorded_sex": {"value": "female", "level": "patient CSV"},
            "interval_days": {"value": 121, "level": "patient CSV"},
            "diagnosis": {
                "value": "metastatic malignant melanoma",
                "level": "paper cohort inclusion",
            },
            "systemic_treatment": {"value": "underwent systemic therapy", "level": "paper cohort"},
            "scan_purpose": {
                "value": "staging and longitudinal therapy response assessment",
                "level": "release cohort",
            },
            "surgical_context": {"value": None, "level": "unavailable"},
            "individual_regimen_and_dates": {"value": None, "level": "unavailable"},
        },
        "limits": "No individual clinical reports. Cohort descriptions do not identify patient-specific regimen or surgical timing. No exact field is assumed inferable from CT.",
        "model_runs_authorized": 2,
        "source_input_hashes": {
            k: v for k, v in manifest.items() if k.startswith("environment/data/")
        },
        "context_block_sha256": sha(METHOD / "context-block.md"),
    }
    (BASE / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    for condition in ["inference", "supplied"]:
        folder = BASE / condition
        task = folder / "task"
        shutil.copytree(SOURCE, task)
        if condition == "inference":
            shutil.rmtree(task / "tests")
            shutil.rmtree(task / "solution/reference")
            (task / "tests").mkdir()
            (task / "solution/reference").mkdir()
            shutil.copyfile(METHOD / "inference-instruction.md", task / "instruction.md")
            shutil.copyfile(METHOD / "score_context.py", task / "tests/score.py")
            (task / "tests/test.sh").write_text("#!/bin/sh\nset -eu\npython /tests/score.py\n")
            (task / "tests/test.sh").chmod(0o755)
            (task / "tests/Dockerfile").write_text(
                "FROM tb3-longitudinal-runtime:validated-v1\nCOPY . /tests\nRUN mkdir -p /app/answer /logs/verifier\n"
            )
            fields = [
                "broad_diagnosis",
                "specific_primary_diagnosis",
                "age_years",
                "recorded_sex",
                "interval_days",
                "baseline_scan_purpose",
                "followup_scan_purpose",
                "systemic_treatment_context",
                "surgical_context",
            ]
            oracle = {
                "schema_version": 1,
                "fields": {
                    key: {
                        "status": "unknown",
                        "value": None,
                        "confidence": 1.0,
                        "basis": "Private schema-only control; no clinical inference.",
                        "alternatives": [],
                    }
                    for key in fields
                },
            }
            (task / "solution/reference/context.json").write_text(
                json.dumps(oracle, indent=2) + "\n"
            )
            (task / "solution/reference/report.md").write_text("Private mechanical control only.\n")
            old_eval = json.loads((OLD / "image-identities.json").read_text())["evaluator"]
            config = (
                (task / "task.toml")
                .read_text()
                .replace(old_eval, "tb3-longitudinal-context-evaluator:v1")
            )
            (task / "task.toml").write_text(config)
        else:
            prompt = (task / "instruction.md").read_text()
            split = "Use your best image-based judgment of lesion presence:"
            assert prompt.count(split) == 1
            prompt = prompt.replace(
                split,
                (METHOD / "context-block.md").read_text().rstrip()
                + "\n\n"
                + "Use your best judgment of lesion presence from the images and supplied broad context:",
            )
            (task / "instruction.md").write_text(prompt)
            shutil.copyfile(task / "instruction.md", METHOD / "supplied-instruction.md")
        identities = json.loads((OLD / "image-identities.json").read_text())
        if condition == "inference":
            identities["evaluator"] = "tb3-longitudinal-context-evaluator:v1"
        (folder / "image-identities.json").write_text(json.dumps(identities, indent=2) + "\n")
        exp_id = f"longitudinal-ct-context-{condition}-astra-medium"
        exp = ROOT / "groups/longitudinal-reading/experiments" / exp_id
        shutil.move(str(exp / "task"), str(folder / "unused-scaffold"))
        path = exp / "experiment.toml"
        path.write_text(
            path.read_text().replace(
                f"groups/longitudinal-reading/experiments/{exp_id}/task",
                f".local/longitudinal-ct-context-v1/{condition}/task",
            )
        )
        (exp / "protocol.md").write_text(
            f"# Clinical context: {condition}\n\n"
            "[Shared frozen design](../../methods/longitudinal-ct-context-v1/protocol.md).\n\n"
            f"This experiment executes only the **{condition}** condition, once, with Astra medium.\n"
        )
        (folder / "preparation.json").write_text(
            json.dumps(
                {
                    "condition": condition,
                    "experiment_id": exp_id,
                    "instruction_sha256": sha(task / "instruction.md"),
                    "scientific_scorer_sha256": sha(task / "tests/score.py"),
                    "solver_identical_to_baseline": True,
                    "input_hashes": {
                        name: sha(task / name) for name in provenance["source_input_hashes"]
                    },
                },
                indent=2,
            )
            + "\n"
        )
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
