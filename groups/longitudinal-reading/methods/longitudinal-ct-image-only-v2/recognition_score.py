"""Private localized-probe verifier; base scoring is the unchanged v1 scorer."""

import argparse
import json
from pathlib import Path

from base_score import score


def evaluate(answer, reference):
    result = score(answer, reference)
    targets = json.loads((reference / "candidate_map.json").read_text())
    try:
        document = json.loads((answer / "candidate_judgments.json").read_text())
        assert document["schema_version"] == 1
        rows = document["candidates"]
        assert isinstance(rows, list)
        assert sorted(r["candidate_id"] for r in rows) == sorted(targets)
        counts = {name: 0 for name in ["tumor", "normal_or_benign", "indeterminate"]}
        for row in rows:
            assert row["judgment"] in counts
            assert isinstance(row["reason"], str) and row["reason"].strip()
            counts[row["judgment"]] += 1
        result["recognition"] = {
            "valid": True,
            "judgments": rows,
            "reference_positive_candidates": len(targets),
            "accepted_as_tumor": counts["tumor"],
            "rejected_as_normal_or_benign": counts["normal_or_benign"],
            "indeterminate": counts["indeterminate"],
            "acceptance_sensitivity": counts["tumor"] / len(targets),
            "specificity": None,
            "limitation": "Adaptive positive-reference targets only; measures acceptance relative to GT, not clinically adjudicated malignancy or specificity.",
        }
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as error:
        result["recognition"] = {"valid": False, "error": str(error) or type(error).__name__}
        result["valid"] = False
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer", type=Path, default=Path("/app/answer"))
    parser.add_argument("--reference", type=Path, default=Path("/tests/reference"))
    parser.add_argument("--output", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()
    result = evaluate(args.answer, args.reference)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "reward.txt").write_text(str(int(result["valid"])) + "\n")
    print(json.dumps({"valid": result["valid"], "recognition": result["recognition"]}, indent=2))


if __name__ == "__main__":
    main()
