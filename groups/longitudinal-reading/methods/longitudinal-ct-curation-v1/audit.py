"""Summarize saved execution evidence without changing or rerunning an attempt."""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-curation-v1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    folder = BASE / "astra-medium"
    state = json.loads((folder / "operator-state.json").read_text())
    assert state["state"] == "terminal"
    trial = Path(state["trial_path"])
    trajectory = json.loads((trial / "agent/trajectory.json").read_text())
    result = json.loads((trial / "result.json").read_text())
    calls = [c for s in trajectory["steps"] for c in s.get("tool_calls", [])]
    calltext = "\n".join(json.dumps(c) for c in calls)
    prompttext = "\n".join(
        json.dumps(s.get("message", ""))
        for s in trajectory["steps"]
        if s.get("source") in {"user", "system"}
    )
    observations = [
        r.get("content", "")
        for s in trajectory["steps"]
        for r in s.get("observation", {}).get("results", [])
    ]
    task = ROOT / ".local/freezes" / state["task_digest"] / "task"
    instruction = (task / "instruction.md").read_text().strip()
    initial_messages = [
        s.get("message", "")
        for s in trajectory["steps"]
        if s.get("source") in {"user", "system"} and isinstance(s.get("message", ""), str)
    ]
    images = sum(
        str(x).count("'type': 'input_image'") + str(x).count('"type": "input_image"')
        for x in observations
    )
    transport = []
    for line in (folder / "model-transport.log").read_text().splitlines():
        try:
            entry = json.loads(line)
            if "target" in entry and "allowed" in entry:
                transport.append(entry)
        except ValueError:
            pass
    times = result["agent_execution"]
    duration = (
        datetime.fromisoformat(times["finished_at"].replace("Z", "+00:00"))
        - datetime.fromisoformat(times["started_at"].replace("Z", "+00:00"))
    ).total_seconds()
    output = dict(
        condition="case02-comprehensive-curation",
        attempt_id=state["attempt_id"],
        task_digest=state["task_digest"],
        agent_seconds=duration,
        trial_seconds=(
            datetime.fromisoformat(result["finished_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(result["started_at"].replace("Z", "+00:00"))
        ).total_seconds(),
        usage=result["agent_result"],
        native_execution=state["native_execution"],
        exception_info=result["exception_info"],
        trajectory_step_count=len(trajectory["steps"]),
        outer_tool_call_count=len(calls),
        image_observation_blocks=images,
        image_count_method="input_image blocks in retained trajectory observation content; montages count as one block",
        frozen_instruction_verbatim_delivered=any(instruction in m for m in initial_messages),
        source_specific_strings_in_tool_requests={
            x: x.lower() in calltext.lower()
            for x in [
                "bcbe3365e6",
                "fdat.uni-tuebingen.de",
                "Longitudinal-CT",
                "/tests/reference",
                "/solution/reference",
            ]
        },
        source_specific_strings_in_initial_prompt={
            x: x.lower() in prompttext.lower()
            for x in [
                "bcbe3365e6",
                "fdat.uni-tuebingen.de",
                "Longitudinal-CT",
                "liver",
                "lymph node",
                "melanoma",
            ]
        },
        proxy_allowed=dict(Counter(x["target"] for x in transport if x.get("allowed"))),
        proxy_blocked=dict(Counter(x["target"] for x in transport if not x.get("allowed"))),
        live_isolation_passed=json.loads((folder / "live-isolation.json").read_text())["passed"],
        artifacts={
            str(p.relative_to(trial)): sha(p)
            for p in [
                trial / "result.json",
                trial / "agent/trajectory.json",
                trial / "agent/codex.txt",
                trial / "verifier/metrics.json",
            ]
        },
        limits="Observed requests supplement enforced isolation; absence of source strings alone does not prove absence of source assistance. No estimate of clinical validity or unseen prior training.",
    )
    (folder / "audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
