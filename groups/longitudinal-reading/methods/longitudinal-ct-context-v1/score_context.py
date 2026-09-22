"""Mechanical context-output validation only; scientific interpretation is separate."""

import json
import math
from pathlib import Path

FIELDS = {
    "broad_diagnosis",
    "specific_primary_diagnosis",
    "age_years",
    "recorded_sex",
    "interval_days",
    "baseline_scan_purpose",
    "followup_scan_purpose",
    "systemic_treatment_context",
    "surgical_context",
}


def validate(answer: Path) -> dict:
    errors = []
    payload = None
    try:
        payload = json.loads((answer / "context.json").read_text())
        assert isinstance(payload, dict) and payload.get("schema_version") == 1
        fields = payload["fields"]
        assert isinstance(fields, dict) and set(fields) == FIELDS
        for name, field in fields.items():
            assert isinstance(field, dict), name
            assert field["status"] in {"observed", "inferred", "unknown"}, name
            assert field["value"] is None or (
                isinstance(field["value"], (str, int, float))
                and not isinstance(field["value"], bool)
            ), name
            assert (field["status"] == "unknown") == (field["value"] is None), name
            confidence = field["confidence"]
            assert not isinstance(confidence, bool) and isinstance(confidence, (int, float)), name
            assert math.isfinite(confidence) and 0 <= confidence <= 1, name
            assert isinstance(field["basis"], str) and field["basis"].strip(), name
            assert isinstance(field["alternatives"], list) and all(
                isinstance(x, str) for x in field["alternatives"]
            ), name
        assert (answer / "report.md").read_text().strip(), "empty report"
    except (OSError, ValueError, AssertionError, KeyError, TypeError) as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
    return {
        "schema_version": 1,
        "contract_valid": not errors,
        "errors": errors,
        "submission": payload,
        "scientific_score": None,
        "interpretation": "Reward is output validity only. Unknown is valid; no diagnostic correctness is implied.",
    }


def main():
    result = validate(Path("/app/answer"))
    out = Path("/logs/verifier")
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    (out / "reward.txt").write_text("1.0\n" if result["contract_valid"] else "0.0\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
