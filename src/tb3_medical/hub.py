"""Inspect local Harbor jobs before an explicit Hub upload."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from . import core as c
from .types import Document

JOB_FILES = ("config.json", "lock.json", "result.json", "analysis.md", "job.log")
TRIAL_FILES = (
    "config.json",
    "result.json",
    "analysis.md",
    "agent",
    "verifier",
    "artifacts",
    "trial.log",
    "exception.txt",
)
STEP_FILES = ("agent", "verifier", "artifacts")


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise c.MedicalError(f"Cannot read Harbor JSON: {path}") from exc


def _job(root: Path, target: str) -> Path:
    if target.startswith("attempt-") and "/" not in target:
        path = root / ".local/attempts" / target / "job"
    else:
        path = root / target
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise c.MedicalError("Harbor job must stay inside the workbench")
    if not resolved.is_dir():
        raise c.MedicalError(f"No local Harbor job: {target}")
    return resolved


def _entries(job: Path, trials: list[Path]) -> list[Path]:
    paths = [job / name for name in JOB_FILES]
    for trial in trials:
        paths.extend(trial / name for name in TRIAL_FILES)
        steps = trial / "steps"
        if steps.is_dir():
            for step in sorted(p for p in steps.iterdir() if p.is_dir()):
                paths.extend(step / name for name in STEP_FILES)
    files: list[Path] = []
    for path in paths:
        if path.is_symlink():
            raise c.MedicalError(f"Upload payload contains a symlink: {path}")
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_symlink():
                    raise c.MedicalError(f"Upload payload contains a symlink: {child}")
                if child.is_file():
                    files.append(child)
    return files


def _nonempty_env(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            (key == "env" and isinstance(item, dict) and bool(item)) or _nonempty_env(item)
            for key, item in value.items()
        )
    return isinstance(value, list) and any(_nonempty_env(item) for item in value)


def inspect(root: Path, target: str, *, include_files: bool = True) -> Document:
    root = root.resolve()
    job = _job(root, target)
    problems: list[str] = []
    for name in ("config.json", "result.json"):
        if not (job / name).is_file():
            problems.append(f"missing {name}")
    if problems:
        return {"job": str(job.relative_to(root)), "status": "blocked", "problems": problems}
    try:
        result = _json(job / "result.json")
    except c.MedicalError:
        problems.append("invalid job result JSON")
        result = {}
    if not isinstance(result, dict) or not result.get("id"):
        problems.append("invalid job result")
        result = {}
    if not result.get("finished_at"):
        problems.append("job is unfinished")
    trials = sorted(
        path for path in job.iterdir() if path.is_dir() and (path / "result.json").is_file()
    )
    if not trials:
        problems.append("no trial results")
    planned = result.get("n_total_trials")
    if isinstance(planned, int) and len(trials) < planned:
        problems.append("trial results are missing")
    for trial in trials:
        try:
            trial_result = _json(trial / "result.json")
        except c.MedicalError:
            problems.append("invalid trial result JSON")
            continue
        if not isinstance(trial_result, dict) or not trial_result.get("id"):
            problems.append("invalid trial result")
        elif not trial_result.get("finished_at"):
            problems.append("trial is unfinished")
    try:
        files = _entries(job, trials)
    except c.MedicalError as exc:
        problems.append(str(exc))
        files = []
    for path in files:
        if path.suffix == ".json":
            try:
                if _nonempty_env(_json(path)):
                    problems.append("nonempty environment values in upload payload")
                    break
            except c.MedicalError:
                problems.append("unreadable JSON in upload payload")
                break
    trajectories = sum((trial / "agent/trajectory.json").is_file() for trial in trials)
    row: Document = {
        "job": str(job.relative_to(root)),
        "job_id": result.get("id"),
        "status": "blocked" if problems else "ready_for_content_review",
        "problems": problems,
        "trials": len(trials),
        "trajectories": trajectories,
        "payload_files": len(files),
        "payload_bytes": sum(path.stat().st_size for path in files),
        "scope": "Harbor 0.14 upload archive entries; review logs, trajectories, artifacts, source rights and private references before transfer.",
    }
    if include_files:
        row["files"] = [str(path.relative_to(job)) for path in files]
    return row


def scan(root: Path) -> Document:
    root = root.resolve()
    attempts = {}
    for path in (root / "groups").glob("*/experiments/*/attempts/attempt-*.json"):
        try:
            record = _json(path)
        except c.MedicalError:
            continue
        if isinstance(record, dict):
            attempts[path.stem] = record.get("experiment_id")
    candidates = sorted((root / ".local/attempts").glob("attempt-*/job"))
    candidates += sorted(
        path.parent
        for path in (root / "runs").glob("*/result.json")
        if (path.parent / "config.json").is_file()
    )
    candidates += sorted(
        path.parent
        for path in (root / "jobs").glob("*/result.json")
        if (path.parent / "config.json").is_file()
    )
    rows = [inspect(root, str(path.relative_to(root)), include_files=False) for path in candidates]
    for row in rows:
        path = Path(row["job"])
        if path.parts[:2] == (".local", "attempts") and len(path.parts) > 2:
            row["experiment_id"] = attempts.get(path.parts[2])
    return {
        "jobs": len(rows),
        "ready_for_content_review": sum(r["status"] == "ready_for_content_review" for r in rows),
        "blocked": sum(r["status"] == "blocked" for r in rows),
        "with_trajectories": sum(bool(r.get("trajectories")) for r in rows),
        "rows": rows,
    }


def upload(root: Path, target: str, *, reviewed: bool, public: bool, executable: str) -> Document:
    root = root.resolve()
    row = inspect(root, target, include_files=False)
    if row["status"] != "ready_for_content_review":
        raise c.MedicalError("Upload blocked: " + "; ".join(row["problems"]))
    if not reviewed:
        raise c.MedicalError(
            "Inspect the payload and pass --reviewed after checking content and rights"
        )
    harbor = shutil.which(executable) or (
        str(root / ".venv/bin/harbor") if executable == "harbor" else None
    )
    if not harbor or not Path(harbor).is_file():
        raise c.MedicalError("Harbor CLI unavailable; pass --harbor PATH")
    command = [harbor, "upload", str(root / row["job"]), "--public" if public else "--private"]
    completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise c.MedicalError(
            f"Harbor upload failed (exit {completed.returncode}); run Harbor auth/login diagnostics locally"
        )
    match = re.search(r"https://hub\.harborframework\.com/jobs/[A-Za-z0-9-]+", completed.stdout)
    failed = re.search(r"\bfailed (\d+) trial\(s\)", completed.stdout)
    n_failed = int(failed.group(1)) if failed else 0
    return {
        "job": row["job"],
        "visibility": "public" if public else "private",
        "url": match.group(0) if match else None,
        "failed_trials": n_failed,
        "uploaded": bool(match) and n_failed == 0,
    }
