#!/usr/bin/env python3
"""Replay narrow source-screening checks; never launch models or fetch data.

Inputs are the ignored public-source cache described in the round-two manifest.
These checks audit receipts and counterexamples, not submission readiness.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import unicodedata
import zipfile


def read_json(path: Path):
    return json.loads(path.read_text())


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def bindings(path: Path, name: str) -> dict[str, dict[str, str]]:
    """Read only the flat, explicit subcircuit interface in the selected fixture."""
    statements = [line.lower().split() for line in path.read_text().splitlines()
                  if line.strip() and not line.lstrip().startswith("*")]
    header = next(row for row in statements if row[:2] == [".subckt", name])
    ports = header[2:]
    calls = [row for row in statements if row[0].startswith("x") and row[-1] == name]
    assert calls and len(set(ports)) == len(ports)
    assert all(len(row) == len(ports) + 2 for row in calls)
    return {row[0]: dict(zip(ports, row[1:-1], strict=True)) for row in calls}


def normalize(value) -> str:
    return unicodedata.normalize("NFC", str(value)).strip().rstrip(".").lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path(".cache/candidate-search-r2"))
    args = parser.parse_args()
    root = args.cache
    start = time.perf_counter()
    checks = {}

    # A two-node small-signal control, with grounded gates, grounded M1 drain,
    # no body effect, and positive transconductances/output conductances.
    # Solve the KCL matrix directly; compare with the usual cascode heuristic.
    gm1, gm2, go1, go2 = 0.002, 0.004, 0.00001, 0.00002
    a, b, c, d = gm1 + go1 + gm2 + go2, -go2, -(gm2 + go2), go2
    determinant = a * d - b * c
    vx, vo = -b / determinant, a / determinant  # unit output test current
    residual = max(abs(a * vx + b * vo), abs(c * vx + d * vo - 1))
    assert residual < 1e-12
    checks["source_follower_stack_control"] = {
        "method": "Independent two-node KCL, illustrative parameters; not an ngspice replay",
        "gm1_S": gm1, "gm2_S": gm2, "gds1_S": go1, "gds2_S": go2,
        "stack_resistance_ohm": vo,
        "source_follower_approximation_ohm": (1 + gm2 / go2) / gm1 + 1 / go2,
        "usual_cascode_heuristic_ohm": gm2 / (go1 * go2),
        "maximum_KCL_residual_A": residual,
        "limitation": "Topology read from the inspected figure and curated netlist; not a new Terra trial or a proof of image-to-netlist transfer difficulty.",
    }

    # SPICE subcircuit arguments bind by position, regardless of suggestive names.
    parent = root / "netlist/benchmark/Cases/v2_edit_raw/subckt_port_swap/cases"
    run = root / "netlist/example_run/deepseek_demo/edit/subckt_port_swap"
    result = []
    for suffix in ["071", "072"]:
        case = f"complex_subckt_port_swap_{suffix}"
        spec = read_json(parent / case / "case.json")
        target = spec["edit_intent"]["structured_targets"][0]
        name = target["subckt_name"].lower()
        before = bindings(parent / case / "source.sp", name)
        expected = bindings(parent / case / "expected.sp", name)
        predicted = bindings(run / f"{case}.sp", name)
        assert before == expected
        result.append({"case_id": case, "reference_preserves_bindings": True,
                       "published_output_preserves_bindings": before == predicted,
                       "affected_calls": len(before)})
    assert [r["published_output_preserves_bindings"] for r in result] == [False, True]
    checks["subcircuit_port_binding"] = {
        "method": "Independent positional binding comparison; no upstream grader execution",
        "cases": result,
        "limitation": "A simple permutation solves the reference; missing provider completion metadata and unknown Terra difficulty.",
    }

    archive = root / "lingoly/data/chained_responses.zip"
    with zipfile.ZipFile(archive) as zf:
        member = next(name for name in zf.namelist() if "Gemini" in name and "pattern" in name)
        responses = [json.loads(line) for line in zf.read(member).decode().splitlines()]
    language_results = []
    for overall, question in [(20, "Q 1.2"), (20, "Q 1.3"), (171, "Q 1.1"), (171, "Q 1.2")]:
        row = next(r for r in responses if r["overall_question_n"] == overall and r["question_n"] == question)
        actual = {normalize(k): normalize(v) for k, v in row["model_parsed_response"].items()}
        expected = {normalize(k): normalize(v) for k, v in row["expected_answer"].items()}
        assert all(not value.startswith("[") for value in expected.values())
        correct = sum(actual.get(k) == v for k, v in expected.items())
        language_results.append({"overall_question_n": overall,
                                 "obfuscated_question_n": row["obfuscated_question_n"],
                                 "question_n": question, "correct": correct,
                                 "total": len(expected),
                                 "normalization": "NFC, case, outer whitespace and trailing period"})
    checks["linguistic_answer_screen"] = {
        "archive_member": member, "model": "Gemini 2.5 Flash", "cases": language_results,
        "limitation": "Replayed answer comparisons only; these public records lack finish reasons. No fuzzy or alternative-answer cases counted.",
    }

    nmr = []
    for rep in [1, 2, 3]:
        rows = read_jsonl(root / f"nmr/results/LLM_results/llm_rep{rep}_clean.jsonl")
        for cid in ["a923380e-3546-43f2-bd99-c9a6ad98612f", "e7fd4c85-a1f8-423d-80d2-49cd87dd9fa6"]:
            row = next(r for r in rows if r["compound_id"] == cid and r["model_key"] == "gpt")
            nmr.append({"compound_id": cid, "replicate": rep, "model": row["model_id"],
                        "status": row["status"], "finish_reason": row["finish_reason"],
                        "error": row["error"], "completion_tokens": row["usage"]["completion_tokens"],
                        "candidate_count": len(row["candidates"])})
    checks["nmr_completion_audit"] = {
        "cases": nmr,
        "limitation": "No RDKit canonicalization run. Structural observations are manual in the review; prompts omit molecular formula and mass.",
    }

    trials = []
    for path in sorted((root / "trials").glob("*/*/result.json")):
        row = read_json(path)
        lock = read_json(path.parent / "lock.json")
        phase = row["agent_execution"]
        seconds = (dt.datetime.fromisoformat(phase["finished_at"].replace("Z", "+00:00"))
                   - dt.datetime.fromisoformat(phase["started_at"].replace("Z", "+00:00"))).total_seconds()
        error = row["exception_info"]
        trials.append({"task": path.parts[-3], "trial_id": path.parts[-2],
                       "agent_seconds": seconds,
                       "exception_type": error["exception_type"] if error else None,
                       "reward": row["verifier_result"]["rewards"]["reward"],
                       "model": lock["agent"]["model_name"],
                       "reasoning_effort": lock["agent"]["kwargs"]["reasoning_effort"],
                       "task_checksum": row["task_checksum"], "lock_digest": lock["task"]["digest"],
                       "result_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "verifier_log_sha256": hashlib.sha256((path.parent / "verifier/test-stdout.txt").read_bytes()).hexdigest()})
    assert len(trials) == 9
    assert sum(r["exception_type"] is None for r in trials) == 7
    assert sum(r["exception_type"] == "AgentTimeoutError" for r in trials) == 2
    checks["external_terra_receipts"] = {"trials": trials, "completed_verifier_misses": 7,
                                          "excluded_timeouts": 2,
                                          "limitation": "External receipts, not local trials. Historical lock digests and source Git revisions are different namespaces; equality is not asserted."}
    print(json.dumps({"schema_version": 1, "date": "2026-09-12", "checks": checks,
                      "elapsed_seconds": round(time.perf_counter() - start, 6),
                      "model_trials_launched": 0}, indent=2) + "\n", end="")


if __name__ == "__main__":
    main()
