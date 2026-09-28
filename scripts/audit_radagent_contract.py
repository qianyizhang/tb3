"""Audit pinned RadAgent report plumbing using nonclinical text fixtures only.

No upstream module is imported. Only the listed, inspected functions are compiled;
no agent loop, tool server, model, image operation, or learned metric is executed.
Raw source and fixture output stay local in a fresh destination.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import io
import json
import os
import re
from pathlib import Path
from typing import Any

COMMIT = "9e9d32936ce24676cba32c81605720fe74a5da5a"
RUNTIME = "minimal_inference/app/runtime/agent_runtime.py"
SCENARIOS = "minimal_inference/app/runtime/dataset_scenarios.py"
CONSTANTS = "minimal_inference/radagent/constants_and_path_utils.py"
BATCH = "minimal_inference/app/cli/minimal_ct_agent_batch.py"
EVALUATION = "radagent/evaluation/process_generated_reports.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal(path: Path, name: str) -> Any:
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError(f"Missing literal {name}: {path}")


def select(path: Path, names: list[str], namespace: dict[str, Any]) -> list[dict[str, Any]]:
    selected = [
        node
        for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    assert {node.name for node in selected} == set(names)
    assert all(not node.decorator_list for node in selected)
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(module, str(path), "exec"), namespace)
    return [
        {"function": node.name, "start_line": node.lineno, "end_line": node.end_lineno}
        for node in selected
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = args.sources.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    tree = json.loads((sources / "tree.json").read_text())
    receipt = json.loads((sources / "fetch-receipt.json").read_text())
    assert tree["sha"] == receipt["revision"] == COMMIT and not tree["truncated"]
    blobs = {row["path"]: row for row in tree["tree"] if row["type"] == "blob"}
    verified = set()
    for row in receipt["files"]:
        path = (sources / row["path"]).resolve()
        assert path.is_relative_to(sources)
        raw = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert blob == row["git_blob_sha1"] == blobs[row["path"]]["sha"]
        assert len(raw) == row["bytes"] == blobs[row["path"]]["size"]
        assert sha(path) == row["sha256"]
        verified.add(row["path"])
    required = {RUNTIME, SCENARIOS, CONSTANTS, BATCH, EVALUATION}
    assert required <= verified

    namespace: dict[str, Any] = {
        "json": json,
        "os": os,
        "re": re,
        "Path": Path,
        "Any": Any,
        "CT_RATE_ROOT": out / "fixture-dataset",
        "ART_DEFAULT_PROMPT": literal(sources / RUNTIME, "ART_DEFAULT_PROMPT"),
    }
    selections = {}
    for path, names in [
        (
            RUNTIME,
            ["build_art_user_prompt", "clean_and_convert_to_json", "parse_assistant_decision"],
        ),
        (CONSTANTS, ["path_parse"]),
        (SCENARIOS, ["_split_path", "load_ctrate_report_generation_scenarios"]),
        (BATCH, ["trace_filename", "success_payload", "failure_payload"]),
        (
            EVALUATION,
            ["generate_gt_list", "generate_test_list_from_agent_outputs", "test_if_paired_data"],
        ),
    ]:
        selections[path] = select(sources / path, names, namespace)

    manifest = []
    for i in range(1, 4):
        manifest.append(
            {
                "id": 100 + i,
                "image": f"valid_{i}_a_1.nii.gz",
                "conversations": [
                    {"from": "human", "value": f"<image>\nNONCLINICAL REQUEST {i}"},
                    {"from": "gpt", "value": f"REFERENCE_ONLY_SENTINEL_{i}"},
                ],
            }
        )
    manifest_path = namespace["_split_path"]("val")
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    scenarios = namespace["load_ctrate_report_generation_scenarios"]("val", start_id=0, end_id=1)
    assert len(scenarios) == 2  # The source end index is inclusive.
    assert all("REFERENCE_ONLY_SENTINEL" not in json.dumps(row) for row in scenarios)
    assert all("gt" not in row for row in scenarios)
    ground_truth = namespace["generate_gt_list"](manifest_path)
    assert len(ground_truth) == 3 and all(
        "REFERENCE_ONLY_SENTINEL" in v for v in ground_truth.values()
    )
    prompt = namespace["build_art_user_prompt"]("", scenarios[0]["image_path"])
    assert scenarios[0]["image_path"] in prompt and prompt.count("<image>") == 1
    assert (
        namespace["build_art_user_prompt"](scenarios[0]["task"], scenarios[0]["image_path"])
        == scenarios[0]["task"]
    )

    final = {"action": "final_answer", "answer": "NONCLINICAL OUTPUT A"}
    forms = {
        "strict-json": json.dumps(final),
        "fenced-json": "```json\n" + json.dumps(final) + "\n```",
        "python-literal": repr(final),
        "nonstring-answer": json.dumps({"action": "final_answer", "answer": 7}),
        "nonfinal-action": json.dumps(
            {"action": "call_tool", "tool_name": "report_generation_tool"}
        ),
        "malformed-text": "NONCLINICAL INVALID JSON",
    }
    cases = []
    diagnostics = io.StringIO()
    for name, content in forms.items():
        fixture = out / name
        (fixture / "trajectory").mkdir(parents=True)
        (fixture / "fails").mkdir()
        message = {"role": "assistant", "content": content}
        payload = namespace["success_payload"]([message], scenario=scenarios[0])
        filename = namespace["trace_filename"](scenarios[0]["image_path"], scenarios[0]["task_id"])
        (fixture / "trajectory" / filename).write_text(json.dumps(payload, indent=2) + "\n")
        with contextlib.redirect_stdout(diagnostics):
            read_back = namespace["generate_test_list_from_agent_outputs"](fixture)
        parsed = namespace["parse_assistant_decision"](message)
        expected = "NONCLINICAL OUTPUT A" if name == "strict-json" else ""
        assert read_back == {"valid_1_a_1": expected}
        assert payload[-1]["reward"] == 0.0 and payload[-1]["status"] == "success"
        if name in {"strict-json", "fenced-json", "python-literal"}:
            assert parsed == final
        cases.append(
            {
                "fixture": name,
                "assistant_content": content,
                "runtime_decision": parsed,
                "metric_reader_output": read_back,
                "note": "Constructed serialization fixture; success metadata is supplied directly, not produced by a rollout.",
            }
        )

    fixture = out / "coverage"
    (fixture / "trajectory").mkdir(parents=True)
    (fixture / "fails").mkdir()
    for scenario, failed in [(scenarios[0], False), (scenarios[1], True)]:
        name = namespace["trace_filename"](scenario["image_path"], scenario["task_id"])
        if failed:
            payload = namespace["failure_payload"](
                [], scenario=scenario, error="NONCLINICAL FIXTURE FAILURE"
            )
            folder = "fails"
        else:
            payload = namespace["success_payload"](
                [{"role": "assistant", "content": forms["strict-json"]}], scenario=scenario
            )
            folder = "trajectory"
        (fixture / folder / name).write_text(json.dumps(payload, indent=2) + "\n")
    with contextlib.redirect_stdout(diagnostics):
        outputs = namespace["generate_test_list_from_agent_outputs"](fixture)
        paired, _ = namespace["test_if_paired_data"](dict(ground_truth), outputs)
    assert outputs == {"valid_1_a_1": "NONCLINICAL OUTPUT A", "valid_2_a_1": "Failed"}
    assert set(paired) == set(outputs) and len(paired) == 2
    coverage = {
        "reference_cases": 3,
        "success_traces": 1,
        "failure_traces": 1,
        "absent_cases": 1,
        "paired_cases": 2,
        "metric_reader_output": outputs,
        "paired_reference_keys": sorted(paired),
        "meaning": "Missing output removes its reference. A retained failure remains as literal Failed. No score is computed.",
    }
    # Reuse only these disposable fixture paths to show source reader precedence.
    name = namespace["trace_filename"](scenarios[0]["image_path"], scenarios[0]["task_id"])
    (fixture / "fails" / name).write_text(
        json.dumps(
            namespace["failure_payload"]([], scenario=scenarios[0], error="NONCLINICAL DUPLICATE")
        )
        + "\n"
    )
    outputs = namespace["generate_test_list_from_agent_outputs"](fixture)
    assert outputs["valid_1_a_1"] == "Failed"

    result = {
        "schema": 1,
        "source_commit": COMMIT,
        "scope": "Selected source functions on nonclinical text; no agent, learned scorer, medical processing, or model launch.",
        "source_receipt_sha256": sha(sources / "fetch-receipt.json"),
        "script_sha256": sha(Path(__file__)),
        "verified_source_files": len(verified),
        "selected_functions": selections,
        "scenario_fixture": {
            "selected_cases": 2,
            "inclusive_end_index": True,
            "reference_sentinels_absent_from_scenarios": True,
            "reference_loader_cases": 3,
            "image_path_in_prompt": True,
        },
        "tool_names": literal(sources / RUNTIME, "ART_TOOL_NAMES"),
        "max_steps": literal(sources / RUNTIME, "ART_MAX_STEPS"),
        "serialization_fixtures": cases,
        "coverage_fixture": coverage,
        "duplicate_success_failure": {
            "output": outputs["valid_1_a_1"],
            "meaning": "A failure file overwrites the same scan key from trajectory when both are retained.",
        },
        "native_input_acquired": False,
        "agent_run": False,
        "report_quality_measured": False,
        "visual_acceptance": False,
    }
    (out / "diagnostics.txt").write_text(diagnostics.getvalue())
    (out / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "source_files": len(verified),
                "serialization_fixtures": len(cases),
                "coverage_cases": 3,
                "all_assertions_passed": True,
                "output": str(out / "audit.json"),
            }
        )
    )


if __name__ == "__main__":
    main()
