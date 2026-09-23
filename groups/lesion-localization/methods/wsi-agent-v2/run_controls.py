"""Run exact-task Harbor oracle/no-op controls sequentially, with a resume ledger."""

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEST = ROOT / ".local/wsi-agent-v2"
LEDGER = DEST / "controls.json"
MED = ROOT / ".venv/bin/med"
HARBOR = ROOT / ".venv/bin/harbor"
EXPERIMENTS = ROOT / "groups/lesion-localization/experiments"
CASES = [
    ("wsi-hubmap-inventory-v2-sol6-xhigh", "default"),
    ("wsi-tiger-context-v2-sol6-xhigh", "image-only"),
    ("wsi-tiger-context-v2-sol6-xhigh", "tissue-supplied"),
    ("wsi-camelyon-lesion-v2-sol6-xhigh", "positive-existing"),
    ("wsi-camelyon-lesion-v2-sol6-xhigh", "small-positive"),
    ("wsi-camelyon-lesion-v2-sol6-xhigh", "negative"),
    ("wsi-hiesd-patches-v2-sol6-xhigh", "default"),
]


def run(*args: str) -> dict:
    process = subprocess.run(args, cwd=ROOT, env=os.environ.copy(), capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(
            f"Command failed ({process.returncode}): {' '.join(args)}\n"
            f"stdout: {process.stdout[-3000:]}\nstderr: {process.stderr[-3000:]}"
        )
    return json.loads(process.stdout)


def matching_attempts(experiment: str, case: str, agent: str, digest: str) -> list[dict]:
    attempts = EXPERIMENTS / experiment / "attempts"
    found = []
    for path in attempts.glob("*.json"):
        item = json.loads(path.read_text())
        if (
            item.get("case") == case
            and item.get("agent") == agent
            and item.get("task_digest") == digest
        ):
            found.append(item)
    return found


def check_control(experiment: str, case: str, agent: str, attempt: dict, digest: str) -> dict:
    if attempt["task_digest"] != digest:
        raise ValueError(f"Control has a different task digest: {attempt['id']}")
    state = run(str(MED), "show", attempt["id"])
    expected_outcome = "pass" if agent == "oracle" else "fail"
    if (
        state["current"]["execution_state"] != "completed"
        or state["current"]["outcome"] != expected_outcome
    ):
        raise ValueError(f"Unexpected {agent} control outcome: {state}")
    result = {
        "experiment": experiment,
        "case": case,
        "agent": agent,
        "attempt_id": attempt["id"],
        "task_digest": digest,
        "execution_state": state["current"]["execution_state"],
        "outcome": state["current"]["outcome"],
    }
    if agent == "oracle":
        paths = list(
            (ROOT / ".local/attempts" / attempt["id"] / "job").glob("task__*/verifier/metrics.json")
        )
        if len(paths) != 1:
            raise ValueError(f"Expected one oracle metrics file: {attempt['id']}")
        metrics = json.loads(paths[0].read_text())
        if metrics["kind"] == "hubmap" and metrics["reference_recall"] != 1:
            raise ValueError("HuBMAP oracle misses source polygons")
        if metrics["kind"] == "tiger" and any(
            item["cell_recall"] != 1 or item["compartment_accuracy_reference_center"] != 1
            for item in metrics["rois"].values()
        ):
            raise ValueError("TIGER oracle misses cells or tissue classes")
        if metrics["kind"] == "camelyon_lesions" and (
            metrics["false_positive_points"] != 0
            or (metrics["reference_lesion_groups"] and metrics["lesion_group_recall"] != 1)
        ):
            raise ValueError("CAMELYON oracle misses groups or adds false positives")
        if metrics["kind"] == "hiesd_patches" and metrics["accuracy"] != 1:
            raise ValueError("HiESD oracle misses patch classes")
        result["metrics"] = metrics
    return result


def write_ledger(rows: list[dict]) -> None:
    temporary = LEDGER.with_suffix(".json.tmp")
    temporary.write_text(json.dumps({"schema_version": 1, "controls": rows}, indent=2) + "\n")
    temporary.replace(LEDGER)


def main() -> None:
    if not (DEST / "runtime-images.json").exists():
        raise FileNotFoundError("Pinned runtime image receipt is missing")
    rows = json.loads(LEDGER.read_text())["controls"] if LEDGER.exists() else []
    for experiment, case in CASES:
        case_args = [] if case == "default" else ["--case", case]
        preview = run(str(MED), "run", experiment, *case_args, "--agent", "oracle", "--preview")
        digest = preview["task_digest"]
        for agent in ("oracle", "nop"):
            existing = matching_attempts(experiment, case, agent, digest)
            if len(existing) > 1:
                raise ValueError(f"Multiple {agent} controls need review: {experiment} {case}")
            if existing:
                attempt = existing[0]
            else:
                launched = run(
                    str(MED),
                    "run",
                    experiment,
                    *case_args,
                    "--agent",
                    agent,
                    "--harbor",
                    str(HARBOR),
                )
                attempt = run(str(MED), "show", launched["attempt_id"])
            result = check_control(experiment, case, agent, attempt, digest)
            rows = [row for row in rows if row["attempt_id"] != result["attempt_id"]]
            rows.append(result)
            write_ledger(rows)
            print(
                f"{experiment} {case} {agent}: {result['outcome']} {result['attempt_id']}",
                flush=True,
            )


if __name__ == "__main__":
    main()
