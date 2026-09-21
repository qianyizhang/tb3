"""Score an answer outside Harbor without requiring the /logs mount."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from score import score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--answer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    task = args.task.resolve()
    result = score(
        args.answer.resolve(),
        task / "tests/reference",
        task / "tests/labels.json",
    )
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "valid": result["valid"],
                "semantic_macro_dice": result["semantic_macro_dice"],
                "matched_macro_dice": result["matched_macro_dice"],
            }
        )
    )


if __name__ == "__main__":
    main()
