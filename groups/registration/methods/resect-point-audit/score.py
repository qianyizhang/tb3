#!/usr/bin/env python3
"""Private evaluator for the two-query RESECT point-audit pilot."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def distance(left, right):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def validate_point(value):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("us_world_mm_must_be_three_values")
    if any(
        isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
        for x in value
    ):
        raise ValueError("us_world_mm_must_be_finite_numbers")
    return [float(x) for x in value]


def score(answer: Path, reference: Path):
    result = {
        "schema_version": 1,
        "reward_meaning": "artifact_contract_only_not_scientific_success",
        "valid": False,
        "cases": [],
    }
    try:
        document = json.loads((answer / "result.json").read_text())
        if document.get("schema_version") != 1 or not isinstance(document.get("cases"), list):
            raise ValueError("invalid_result_document")
        items = document["cases"]
        if [item.get("case_id") for item in items] != ["case_a", "case_b"]:
            raise ValueError("cases_must_be_case_a_then_case_b")
        truth = {item["case_id"]: item for item in json.loads(reference.read_text())["cases"]}
        for item in items:
            case_id = item["case_id"]
            point = validate_point(item.get("us_world_mm"))
            confidence = item.get("confidence")
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not math.isfinite(confidence)
                or not 0 <= confidence <= 1
            ):
                raise ValueError("confidence_must_be_finite_0_to_1")
            if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
                raise ValueError("evidence_must_be_nonempty")
            ref = truth[case_id]
            initial_error = distance(ref["initial_us_world_mm"], ref["reference_us_world_mm"])
            final_error = distance(point, ref["reference_us_world_mm"])
            movement = distance(point, ref["initial_us_world_mm"])
            result["cases"].append(
                {
                    "case_id": case_id,
                    "initial_error_mm": initial_error,
                    "final_error_mm": final_error,
                    "improvement_mm": initial_error - final_error,
                    "relative_improvement": (initial_error - final_error) / initial_error,
                    "improved": final_error < initial_error,
                    "movement_mm": movement,
                    "confidence": float(confidence),
                }
            )
        report = answer / "report.md"
        if not report.is_file() or not report.read_text().strip():
            raise ValueError("report_missing_or_empty")
        result["valid"] = True
        result["mean_initial_error_mm"] = sum(x["initial_error_mm"] for x in result["cases"]) / 2
        result["mean_final_error_mm"] = sum(x["final_error_mm"] for x in result["cases"]) / 2
        result["improved_case_count"] = sum(x["improved"] for x in result["cases"])
    except Exception as exc:
        result["error"] = str(exc)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer", type=Path, default=Path("/app/answer"))
    parser.add_argument("--reference", type=Path, default=Path("/tests/reference.json"))
    parser.add_argument("--output", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = score(args.answer, args.reference)
    (args.output / "metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "reward.txt").write_text(str(int(result["valid"])) + "\n")
    print(
        json.dumps(
            {
                "passed": ["artifact_contract"] if result["valid"] else [],
                "failures": [] if result["valid"] else ["artifact_contract"],
                "reward_meaning": result["reward_meaning"],
            }
        )
    )


if __name__ == "__main__":
    main()
