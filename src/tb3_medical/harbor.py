"""Import allowlisted Harbor evidence without changing raw files."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


class HarborError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def workspace_path(root: Path, value: str | Path) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise HarborError("path must stay inside the workspace")
    return path


def relative(root: Path, path: Path) -> str:
    return workspace_path(root, path).relative_to(root.resolve()).as_posix()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise HarborError(f"cannot read JSON: {path.name} ({type(exc).__name__})") from exc


def obj(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def number(value: Any) -> float | None:
    return (
        float(value)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
        else None
    )


def machine_label(value: Any) -> str | None:
    """Machine labels only; nested objects and free-text messages are not exported."""
    return (
        value
        if isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/+\[\]-]{0,199}", value)
        else None
    )


def checksum(value: Any) -> str | None:
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) else None


def seconds(phase: Any) -> float | None:
    phase = obj(phase)
    try:
        start, end = (
            dt.datetime.fromisoformat(phase[k].replace("Z", "+00:00"))
            for k in ("started_at", "finished_at")
        )
        elapsed = (end - start).total_seconds()
        return round(elapsed, 3) if elapsed >= 0 else None
    except (KeyError, AttributeError, TypeError, ValueError):
        return None


def classify(result: dict) -> str:
    """Completion and execution errors take precedence over rewards."""
    if result.get("exception_info") is not None:
        return "execution_error"
    if not result.get("finished_at"):
        return "incomplete"
    if result.get("step_results") or obj(obj(result.get("config")).get("verifier")).get("disable"):
        return "unknown"
    reward = number(obj(obj(result.get("verifier_result")).get("rewards")).get("reward"))
    if seconds(result.get("verifier")) is None or reward not in (0, 1):
        return "unknown"
    agent = machine_label(obj(obj(result.get("config")).get("agent")).get("name"))
    if agent in ("oracle", "nop"):
        return "control_pass" if reward == 1 else "control_fail"
    if not agent or seconds(result.get("agent_execution")) is None:
        return "unknown"
    return "model_pass" if reward == 1 else "model_failure_candidate"


def parse_cases(path: Path) -> tuple[list[dict], list[str]]:
    """Only consume explicit JSON case records; never infer from prose/log counts."""
    if not path.is_file():
        return [], ["No verifier case output is available."]
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        return [], ["Verifier case output could not be read."]
    documents = []
    try:
        documents.append(json.loads(text))
    except ValueError:
        for line in text.splitlines():
            try:
                documents.append(json.loads(line))
            except ValueError:
                continue
    recognized = [
        d
        for d in documents
        if isinstance(d, dict)
        and isinstance(d.get("passed"), list)
        and isinstance(d.get("failures"), list)
    ]
    if len(recognized) != 1:
        return [], [
            "Verifier output has no single supported JSON case summary; inspect raw evidence."
        ]
    report = recognized[0]
    cases = []
    for status, key in (("passed", "passed"), ("failed", "failures")):
        for item in report[key]:
            if isinstance(item, str):
                # Cache probe encodes failure name and explanation in one string.
                name = item.partition(": ")[0] if status == "failed" else item
            elif isinstance(item, dict):
                name = item.get("name") or item.get("case") or item.get("test")
            else:
                continue
            if machine_label(name):
                cases.append({"name": name, "status": status, "detail": ""})
            else:
                return [], [
                    "Verifier case names are not supported machine labels; inspect raw evidence."
                ]
    names = [c["name"] for c in cases]
    if len(names) != len(set(names)):
        return [], ["Duplicate or contradictory verifier case names; inspect raw evidence."]
    return cases, []


def evidence_file(root: Path, path: Path, label: str) -> dict:
    return {"label": label, "path": relative(root, path), "sha256": sha256(path)}


def import_trial(root: Path, source: Path) -> dict:
    source = workspace_path(root, source)
    before = sha256(source)
    result = read_json(source)
    if not isinstance(result, dict) or "config" not in result or "task_name" not in result:
        raise HarborError("not a Harbor individual trial result")
    config = obj(result.get("config"))
    agent = obj(config.get("agent"))
    info = obj(result.get("agent_info"))
    trial_dir, job_dir = source.parent, source.parent.parent
    stdout = trial_dir / "verifier" / "test-stdout.txt"
    stdout_hash = sha256(stdout) if stdout.is_file() else None
    cases, warnings = parse_cases(stdout)
    evidence = [evidence_file(root, source, "Trial result (raw, local)")]
    for name, label in (
        ("verifier/test-stdout.txt", "Verifier cases"),
        ("verifier/reward.txt", "Reward artifact"),
        ("agent/trajectory.json", "Agent trajectory (raw, local)"),
    ):
        path = trial_dir / name
        if path.is_file():
            evidence.append(evidence_file(root, path, label))
    artifacts = trial_dir / "artifacts" / "app"
    if artifacts.is_dir():
        for path in sorted(artifacts.rglob("*")):
            if path.is_file():
                evidence.append(
                    evidence_file(
                        root, path, "Submitted artifact: " + path.relative_to(artifacts).as_posix()
                    )
                )
    lock = job_dir / "lock.json"
    version = None
    if lock.is_file():
        version = obj(obj(read_json(lock)).get("harbor")).get("version")
        evidence.append(evidence_file(root, lock, "Harbor lock (raw, local)"))
    source_relative = relative(root, source)
    trial_name = str(result.get("trial_name") or trial_dir.name)
    identifier = (
        re.sub(r"[^A-Za-z0-9_.-]", "-", trial_name)
        + "-"
        + hashlib.sha256(source_relative.encode()).hexdigest()[:8]
    )
    task_id = (machine_label(result["task_name"]) or "unknown").rsplit("/", 1)[-1]
    reward = number(obj(obj(result.get("verifier_result")).get("rewards")).get("reward"))
    classification = classify(result)
    if result.get("step_results"):
        warnings.append(
            "Multi-step trial requires explicit analysis; top-level reward is not classified."
        )
    if reward == 1 and any(c["status"] == "failed" for c in cases):
        warnings.append("Reward 1 contradicts explicit failed cases; review verifier integrity.")
        if classification not in ("execution_error", "incomplete"):
            classification = "unknown"
    if reward == 0 and cases and all(c["status"] == "passed" for c in cases):
        warnings.append("Reward 0 has no explicit failed case; inspect verifier evidence.")
        if classification not in ("execution_error", "incomplete"):
            classification = "unknown"
    reward_file = trial_dir / "verifier" / "reward.txt"
    if reward_file.is_file():
        try:
            artifact_reward = float(reward_file.read_text().strip())
        except (UnicodeError, ValueError):
            artifact_reward = None
        if artifact_reward != reward:
            warnings.append(
                "Reward artifact disagrees with the trial result; inspect verifier integrity."
            )
            if classification not in ("execution_error", "incomplete"):
                classification = "unknown"
    if not checksum(result.get("task_checksum")):
        warnings.append(
            "Historical Harbor task checksum is missing; snapshot comparison is unavailable."
        )
    if (
        before != sha256(source)
        or stdout_hash != (sha256(stdout) if stdout.is_file() else None)
        or not evidence_matches(root, evidence)
    ):
        raise HarborError("trial evidence changed while being imported; retry collection")
    usage = obj(result.get("agent_result"))
    return {
        "schema_version": 1,
        "id": identifier,
        "job": job_dir.name,
        "trial_name": trial_name,
        "task_id": task_id,
        "agent": machine_label(agent.get("name")) or machine_label(info.get("name")),
        "model": machine_label(agent.get("model_name")),
        "reasoning_effort": machine_label(obj(agent.get("kwargs")).get("reasoning_effort")),
        "agent_version": machine_label(info.get("version")),
        "backend": machine_label(obj(config.get("environment")).get("type")),
        "harbor_version": machine_label(version),
        "execution_mode": "harbor",
        "classification": classification,
        "reward": reward,
        "started_at": result.get("started_at"),
        "finished_at": result.get("finished_at"),
        "timing": {
            "total": seconds(result),
            "setup": seconds(result.get("agent_setup")),
            "agent": seconds(result.get("agent_execution")),
            "verifier": seconds(result.get("verifier")),
        },
        "usage": {
            key: number(usage.get(key))
            for key in ("n_input_tokens", "n_cache_tokens", "n_output_tokens")
        },
        "cases": cases,
        "exception_type": machine_label(obj(result.get("exception_info")).get("exception_type")),
        "evidence": evidence,
        "task_checksum": checksum(result.get("task_checksum")),
        "task_sha256": None,
        "checksum_kind": "harbor.task_checksum",
        "warnings": warnings,
        "source_result": source_relative,
        "source_sha256": before,
        "evidence_sha256": digest_json(evidence),
        "qualifying_final_trial": False,
    }


def evidence_matches(root: Path, evidence: list[dict]) -> bool:
    for item in evidence:
        try:
            path = workspace_path(root, item["path"])
            if not path.is_file() or sha256(path) != item["sha256"]:
                return False
        except (OSError, KeyError, HarborError):
            return False
    return True
