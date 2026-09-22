"""Compare saved outputs; selection is author-side and never supplied to a solver."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-curation-v1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    inputs = {
        "image_only": ROOT / ".local/longitudinal-ct-case02/analysis/evidence.json",
        "context_supplied": ROOT
        / ".local/longitudinal-ct-context-v1/supplied/analysis/evidence.json",
        "comprehensive_curation": BASE / "analysis/evidence.json",
    }
    evidence = {name: read(path) for name, path in inputs.items()}
    conditions = []
    for name, e in evidence.items():
        m = e["metrics"]
        conditions.append(
            {
                "condition": name,
                "attempt_id": e["attempt_id"],
                "task_digest": e["task_digest"],
                "detection": m["detection_micro"],
                "per_visit_detection": {v: x["detection"] for v, x in m["visits"].items()},
                "segmentation": {v: x["segmentation"] for v, x in m["visits"].items()},
                "gt_macro_dice": m["segmentation_gt_macro_dice"],
                "association": m["association"],
                "size_strata": e["declared_size_strata"],
            }
        )
    old = {(r["visit"], r["gt_id"]): r for r in evidence["context_supplied"]["per_reference"]}
    new = evidence["comprehensive_curation"]
    candidates = new["metrics"].get("candidate_contract", {}).get("visits", {})
    lookup = {(v, r["id"]): r for v, rows in candidates.items() for r in rows}
    rows = []
    for row in new["per_reference"]:
        key = row["visit"], row["gt_id"]
        before = old[key]["detection_prediction_id"] is not None
        after = row["detection_prediction_id"] is not None
        candidate = lookup.get((row["visit"], row["detection_prediction_id"]))
        rows.append(
            {
                **row,
                "prior_context_detected": before,
                "transition": "gained"
                if after and not before
                else "lost"
                if before and not after
                else "retained"
                if after
                else "still_missed",
                "candidate_assessment": candidate,
            }
        )
    unmatched = []
    for visit, data in new["metrics"]["visits"].items():
        matched = {
            r["detection_prediction_id"]
            for r in data["per_gt"]
            if r["detection_prediction_id"] is not None
        }
        unmatched.extend(
            {"visit": visit, **r} for r in candidates.get(visit, []) if r["id"] not in matched
        )
    output = {
        "schema_version": 1,
        "comparison_classification": "endpoint_only",
        "conditions": conditions,
        "per_reference_transitions": rows,
        "unmatched_candidates": unmatched,
        "probable_tumor_subset": new["metrics"].get("probable_tumor_subset"),
        "confounders": [
            "New goal, exhaustive-review wording, all-size inclusion and structured uncertainty are bundled.",
            "One new run per condition; stochastic variation and prompt intervention cannot be separated.",
            "GT covers expert-deemed malignant lesions, whereas the new output deliberately includes indeterminate candidates.",
            "Reference agreement is not clinical adjudication; GT used unavailable individual clinical reports.",
        ],
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in inputs.values()},
    }
    out = BASE / "comparison.json"
    assert not out.exists()
    out.write_text(json.dumps(output, indent=2) + "\n")
    print(
        json.dumps(
            {
                "transitions": {
                    key: sum(r["transition"] == key for r in rows)
                    for key in ["gained", "lost", "retained", "still_missed"]
                },
                "unmatched_candidates": len(unmatched),
                "conditions": [
                    {
                        "condition": r["condition"],
                        "detection": r["detection"],
                        "gt_macro_dice": r["gt_macro_dice"],
                    }
                    for r in conditions
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
