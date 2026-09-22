#!/usr/bin/env python3
"""Focused synthetic checks for the RESECT point scorer."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from score import score


REFERENCE = {
    "cases": [
        {"case_id": "case_a", "initial_us_world_mm": [0, 0, 0], "reference_us_world_mm": [1, 0, 0]},
        {"case_id": "case_b", "initial_us_world_mm": [0, 0, 0], "reference_us_world_mm": [0, 3, 4]},
    ]
}


def write_answer(root, cases):
    root.mkdir()
    (root / "result.json").write_text(json.dumps({"schema_version": 1, "cases": cases}))
    (root / "report.md").write_text("inspection\n")


def main():
    with tempfile.TemporaryDirectory() as name:
        root = Path(name)
        reference = root / "reference.json"
        reference.write_text(json.dumps(REFERENCE))
        oracle = root / "oracle"
        write_answer(
            oracle,
            [
                {"case_id": "case_a", "us_world_mm": [1, 0, 0], "confidence": 1, "evidence": "x"},
                {"case_id": "case_b", "us_world_mm": [0, 3, 4], "confidence": 1, "evidence": "y"},
            ],
        )
        scored = score(oracle, reference)
        assert scored["valid"] and scored["mean_final_error_mm"] == 0
        noop = root / "noop"
        write_answer(
            noop,
            [
                {"case_id": "case_a", "us_world_mm": [0, 0, 0], "confidence": 0.5, "evidence": "x"},
                {"case_id": "case_b", "us_world_mm": [0, 0, 0], "confidence": 0.5, "evidence": "y"},
            ],
        )
        scored = score(noop, reference)
        assert scored["valid"] and scored["mean_final_error_mm"] == 3
        malformed = root / "malformed"
        write_answer(
            malformed,
            [{"case_id": "case_b", "us_world_mm": [0, 0, 0], "confidence": 2, "evidence": ""}],
        )
        assert not score(malformed, reference)["valid"]
    print("score checks passed")


if __name__ == "__main__":
    main()
