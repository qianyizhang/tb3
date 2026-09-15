"""Exact source-label agreement for BR-011's prototype, not clinical validity."""

import argparse
import json
from pathlib import Path


def grade(answer, expected):
    truth = {r["object_id"]: r["label"] for r in expected["assignments"]}
    rows = answer.get("assignments") if isinstance(answer, dict) else None
    if not isinstance(rows, list):
        return {"success": False, "error": "assignments must be a list"}
    seen = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"object_id", "label"}:
            return {"success": False, "error": "each assignment needs object_id and label"}
        key, label = row["object_id"], row["label"]
        if not isinstance(key, str) or not isinstance(label, str):
            return {"success": False, "error": "object_id and label must be strings"}
        if key in seen:
            return {"success": False, "error": "duplicate object_id"}
        seen[key] = label
    missing, extra = sorted(truth.keys() - seen.keys()), sorted(seen.keys() - truth.keys())
    wrong = sorted(k for k in truth.keys() & seen.keys() if truth[k] != seen[k])
    return {"success": not (missing or extra or wrong), "missing": missing, "extra": extra, "wrong": wrong}


def controls(expected):
    rows = expected["assignments"]
    wrong = {"assignments": [dict(r) for r in rows]}
    wrong["assignments"][0]["label"] = "not-an-anatomical-label"
    cases = [
        ("source_key", expected, True),
        ("reordered", {"assignments": rows[::-1]}, True),
        ("empty", {"assignments": []}, False),
        ("missing", {"assignments": rows[1:]}, False),
        ("duplicate", {"assignments": rows + [rows[0]]}, False),
        ("extra", {"assignments": rows + [{"object_id": "unknown", "label": rows[0]["label"]}]}, False),
        ("wrong_identity", wrong, False),
        ("malformed", {"assignments": "anything"}, False),
    ]
    result = [{"name": n, "expected_success": e, "grade": grade(a, expected)} for n, a, e in cases]
    assert all(r["grade"]["success"] == r["expected_success"] for r in result)
    return {"controls_passed": len(result), "results": result,
            "limitation": "Only scorer behavior is validated; source identity and inferability require independent review."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--answer", type=Path)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    expected = json.loads(args.expected.read_text())
    if args.controls:
        print(json.dumps(controls(expected), indent=2))
    elif args.answer:
        print(json.dumps(grade(json.loads(args.answer.read_text()), expected), indent=2))
    else:
        parser.error("provide --answer or --controls")
