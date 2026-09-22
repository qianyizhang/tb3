"""Replay a terminal attempt's frozen evaluator and retain an author-only review."""

import argparse
import hashlib
import importlib.util
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BATCH = ROOT / ".local/dental-f018-contract-v3-20260922"


def sha(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "experiment",
        choices=["dental-f018-contract-v3-astra-medium", "dental-f018-reference-v3-astra-medium"],
    )
    args = parser.parse_args()
    base = ROOT / ".local" / args.experiment
    state = json.loads((base / "operator-state.json").read_text())
    execution = json.loads((Path(state["attempt_path"]) / "execution.json").read_text())
    if state["state"] != "terminal" or execution["execution_state"] == "running":
        raise SystemExit("Attempt is not terminal; no review created")
    trial = Path(state["trial_path"])
    result = json.loads((trial / "result.json").read_text())
    frozen = ROOT / ".local/freezes" / state["task_digest"] / "task"
    manifest = json.loads((BATCH / "preparation-receipt.json").read_text())["experiments"][
        args.experiment
    ]["files"]
    assert all(sha(frozen / name) == value for name, value in manifest.items())
    assert execution["frozen_payload_unchanged"]
    spec = importlib.util.spec_from_file_location(
        "frozen_dental_evaluator", frozen / "tests/score.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = trial / "artifacts/app/answer/segmentation.nii.gz"
    replay = module.score(
        output,
        frozen / "tests/reference.nii.gz",
        json.loads((frozen / "tests/labels.json").read_text()),
    )
    (base / "replay").mkdir(exist_ok=True)
    (base / "replay/metrics.json").write_text(json.dumps(replay, indent=2) + "\n")
    metrics_file = trial / "verifier/metrics.json"
    original = json.loads(metrics_file.read_text()) if metrics_file.exists() else None
    commands = []
    messages = []
    events = Counter()
    trace = trial / "agent/codex.txt"
    for line in trace.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "item.completed":
            item = event.get("item", {})
            events[item.get("type")] += 1
            if item.get("type") == "command_execution":
                commands.append(item.get("command", ""))
            if item.get("type") == "agent_message":
                messages.append(item.get("text", ""))
    candidates = [
        {"command_index": i, "command": command}
        for i, command in enumerate(commands)
        if re.search(
            r"https?://|\bcurl\b|\bwget\b|\brequests\b|urllib|huggingface|git clone|/tests|/solution|/Users|ToothFairy|/app/reference",
            command,
            re.I,
        )
    ]
    transport = Counter()
    for line in (base / "model-transport.log").read_text().splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if "target" in row:
            transport[(row["target"], row.get("allowed"))] += 1
    interval = result.get("agent_execution") or {}
    duration = None
    if interval.get("started_at") and interval.get("finished_at"):
        duration = (
            datetime.fromisoformat(interval["finished_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(interval["started_at"].replace("Z", "+00:00"))
        ).total_seconds()
    audit = {
        "completed_item_types": dict(events),
        "data_access_candidates_requiring_review": candidates,
        "transport": [
            {"target": host, "allowed": allowed, "connections": count}
            for (host, allowed), count in sorted(transport.items())
        ],
        "scope": "Retained commands and proxy host decisions; encrypted payload and pretraining are not adjudicated.",
    }
    (base / "access-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    (base / "agent-messages.json").write_text(json.dumps(messages, indent=2) + "\n")
    evidence = [
        trial / "result.json",
        output,
        trial / "artifacts/app/answer/method.md",
        metrics_file,
        frozen / "tests/score.py",
        frozen / "tests/reference.nii.gz",
        base / "model-transport.log",
        base / "runtime-isolation.json",
        trace,
    ]
    review = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "attempt_id": state["attempt_id"],
        "task_digest": state["task_digest"],
        "state": "replayed_pending_access_review",
        "execution": execution,
        "exception": result.get("exception_info"),
        "valid": replay["valid"],
        "original_macro_dice": None if original is None else original["macro_dice"],
        "replay_macro_dice": replay["macro_dice"],
        "independent_replay_identical": replay == original,
        "agent_seconds": duration,
        "token_usage": result.get("agent_result"),
        "groups": replay.get("groups"),
        "whole_tooth_geometry_and_identity": replay.get("whole_tooth_geometry_and_identity"),
        "canal_surface_metrics": replay.get("canal_surface_metrics"),
        "missing_reference_labels": [
            r["id"]
            for r in replay.get("per_label", [])
            if r["gt_voxels"] and not r["prediction_voxels"]
        ],
        "access_audit": audit,
        "evidence_sha256": {str(p.relative_to(ROOT)): sha(p) for p in evidence if p.is_file()},
        "missing_evidence": [str(p.relative_to(ROOT)) for p in evidence if not p.is_file()],
    }
    target = base / "terminal-review.json"
    if target.exists():
        raise SystemExit("Existing review retained; inspect before any replacement")
    target.write_text(json.dumps(review, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: review[k]
                for k in [
                    "attempt_id",
                    "valid",
                    "original_macro_dice",
                    "independent_replay_identical",
                    "agent_seconds",
                    "missing_reference_labels",
                    "exception",
                ]
            },
            indent=2,
        )
    )
    print("Access candidates:", len(candidates))


if __name__ == "__main__":
    main()
