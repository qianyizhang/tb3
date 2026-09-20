"""Prepare, execute and collect a selected task; never launch from inspection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib

from . import core as c, harbor


def task_files(path):
    result = {}
    for file in sorted(Path(path).rglob("*")):
        if file.is_symlink():
            raise c.MedicalError(f"Task contains a symlink: {file}")
        if file.is_file() and "__pycache__" not in file.parts and file.suffix != ".pyc":
            result[file.relative_to(path).as_posix()] = c.sha(file)
    return result


def tree_digest(files):
    return hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def new(root, group, key, title):
    owner = c.lookup(root, group)
    if owner["kind"] != "group" or key in c.load(root):
        raise c.MedicalError("Select a group and an unused experiment ID")
    c.identifier(key)
    base = c.destination(root, owner, "experiments") / key
    base.mkdir(parents=True, exist_ok=False)
    row = {
        "schema_version": 2,
        "kind": "experiment",
        "id": key,
        "group_id": group,
        "title": title,
        "experiment_stage": "draft",
        "assessment": "not_assessed",
        "historical": False,
        "protocol": "protocol.md",
        "task_path": str((base / "task").relative_to(root)),
    }
    c.write_new(base / "experiment.toml", row)
    (base / "protocol.md").write_text(
        f"# {title}\n\n## Question and method\n\n## Inputs and reference\n\n## Findings and limits\n"
    )
    task = base / "task"
    for folder in ("environment", "tests", "solution"):
        (task / folder).mkdir(parents=True)
    (task / "instruction.md").write_text("# Task\n\nDescribe the requested deliverable.\n")
    (task / "task.toml").write_text(
        'version = "1.0"\n[agent]\ntimeout_sec = 600.0\n[verifier]\ntimeout_sec = 60.0\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory_mb = 2048\nstorage_mb = 4096\n'
    )
    (task / "environment/Dockerfile").write_text("FROM python:3.12-slim\nWORKDIR /app\n")
    for name in ("tests/test.sh", "solution/solve.sh"):
        (task / name).write_text(
            '#!/bin/sh\nset -eu\necho "Implement the verifier/oracle before qualification" >&2\nexit 1\n'
        )
    group_path = Path(root) / owner["record_path"]
    group_record = c.read(group_path)
    group_record["experiment_ids"] = [*group_record.get("experiment_ids", []), key]
    c.atomic_write(group_path, group_record)
    return row


def task_spec(experiment, case=None):
    tasks = experiment.get("tasks", [])
    if tasks:
        if case is None and len(tasks) == 1:
            return tasks[0]
        for task in tasks:
            if task["id"] == case:
                return task
        raise c.MedicalError("Choose --case from: " + ", ".join(t["id"] for t in tasks))
    if experiment.get("task_path"):
        return {"id": "default", "task_path": experiment["task_path"]}
    raise c.MedicalError("Historical evidence only; no maintained task recipe is declared")


def task_validate(root, experiment, case=None):
    exp = c.lookup(root, experiment)
    if exp["kind"] != "experiment":
        raise c.MedicalError("Select an experiment")
    spec = task_spec(exp, case)
    task = c.inside(root, spec["task_path"])
    required = (
        "instruction.md",
        "task.toml",
        "environment/Dockerfile",
        "tests/test.sh",
        "solution/solve.sh",
    )
    missing = [name for name in required if not (task / name).is_file()]
    if missing:
        raise c.MedicalError("Missing task inputs; prepare first: " + ", ".join(missing))
    tomllib.loads((task / "task.toml").read_text())
    return exp, spec, task, task_files(task)


def prepare(root, experiment, case=None, execute=False):
    exp = c.lookup(root, experiment)
    spec = task_spec(exp, case)
    if exp.get("method") == "landmarks":
        from .landmarks import prepare_case

        return prepare_case(root, exp, spec, execute)
    command = exp.get("prepare_command", [])
    if execute:
        if not command or not all(isinstance(x, str) for x in command):
            raise c.MedicalError("No preparation command; author the task files directly")
        subprocess.run(command, cwd=root, check=True)
    return {"command": command, "executed": execute, "task_path": spec["task_path"]}


def freeze(root, experiment, case=None):
    exp, spec, task, files = task_validate(root, experiment, case)
    digest = tree_digest(files)
    key = "freeze-" + hashlib.sha256((experiment + digest).encode()).hexdigest()[:24]
    records = c.load(root)
    if key in records:
        restore_freeze(root, records[key])
        return records[key]
    snapshot = Path(root) / ".local/freezes" / digest / "task"
    if not snapshot.exists():
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(task, snapshot, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if task_files(snapshot) != files or task_files(task) != files:
        raise c.MedicalError("Task changed while preparing its exact snapshot")
    row = {
        "schema_version": 2,
        "kind": "freeze",
        "id": key,
        "experiment_id": experiment,
        "group_id": exp["group_id"],
        "case": spec["id"],
        "created_at": c.now(),
        "task_digest": digest,
        "files": files,
        "source_path": spec["task_path"],
        "snapshot_path": str(snapshot.relative_to(root)),
    }
    base = Path(root) / Path(exp["record_path"]).parent
    c.write_new(base / "freezes" / (key + ".json"), row)
    return row


def restore_freeze(root, frozen):
    snapshot = c.inside(root, frozen["snapshot_path"])
    if not snapshot.exists():
        source = c.inside(root, frozen["source_path"])
        if task_files(source) != frozen["files"]:
            raise c.MedicalError("Restore the selected frozen inputs before replay or execution")
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, snapshot, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if task_files(snapshot) != frozen["files"]:
        raise c.MedicalError("Frozen task bytes changed")
    return snapshot


def result_state(imported):
    classification = imported["classification"]
    if classification == "execution_error":
        return "error", "no_verdict"
    if classification == "incomplete":
        return ("running" if imported.get("started_at") else "planned"), "no_verdict"
    outcome = {
        "model_pass": "pass",
        "control_pass": "pass",
        "model_failure_candidate": "fail",
        "control_fail": "fail",
    }.get(classification, "no_verdict")
    return "completed", outcome


def collect(root, experiment, sources, binding=None):
    root = Path(root).resolve()
    exp = c.lookup(root, experiment)
    if exp["kind"] != "experiment":
        raise c.MedicalError("Collect into an experiment")
    base = root / Path(exp["record_path"]).parent
    results = []
    for source in sources:
        imported = harbor.import_trial(root, c.inside(root, source))
        rows = c.load(root)
        current_binding = dict(binding or {})
        # A launched attempt owns its output directory even when collection occurs
        # after interruption. External results retain a stable source-path identity.
        owned = next(
            (
                r
                for r in rows.values()
                if r["kind"] == "attempt"
                and r.get("execution_path")
                and c.inside(root, source).is_relative_to(
                    c.inside(root, r["execution_path"]).parent / "job"
                )
            ),
            None,
        )
        if owned:
            receipt = c.read(c.inside(root, owned["execution_path"]))
            frozen = rows[owned["freeze_id"]]
            unchanged = task_files(c.inside(root, frozen["snapshot_path"])) == frozen["files"]
            current_binding = {"attempt_id": owned["id"]}
            if receipt.get("frozen_payload_unchanged") and unchanged:
                current_binding.update(
                    task_digest=frozen["task_digest"], checksum=receipt["harbor_task_checksum"]
                )
        prior = next(
            (
                r
                for r in rows.values()
                if r["kind"] == "evaluation" and r.get("source_result") == imported["source_result"]
            ),
            None,
        )
        identity = (
            prior["attempt_id"]
            if prior
            else current_binding.get("attempt_id")
            or "attempt-" + hashlib.sha256(imported["source_result"].encode()).hexdigest()[:24]
        )
        if identity in rows and rows[identity]["experiment_id"] != experiment:
            raise c.MedicalError("The attempt already belongs to another experiment")
        if identity not in rows:
            c.write_new(
                base / "attempts" / (identity + ".json"),
                {
                    "schema_version": 2,
                    "kind": "attempt",
                    "id": identity,
                    "group_id": exp["group_id"],
                    "experiment_id": experiment,
                    "source_result": imported["source_result"],
                    "diagnostic": True,
                },
            )
        verified = bool(
            current_binding.get("task_digest")
            and current_binding.get("checksum") == imported["task_checksum"]
        )
        proof = current_binding["task_digest"] + current_binding["checksum"] if verified else ""
        key = (
            "observation-"
            + hashlib.sha256((identity + imported["evidence_sha256"] + proof).encode()).hexdigest()[
                :24
            ]
        )
        if key in rows:
            results.append(rows[key])
            continue
        execution, outcome = result_state(imported)
        if owned and imported["classification"] == "incomplete":
            terminal = receipt.get("execution_state")
            if terminal in {"interrupted", "error", "completed"}:
                execution = terminal
        row = {
            **imported,
            "schema_version": 2,
            "kind": "evaluation",
            "id": key,
            "attempt_id": identity,
            "experiment_id": experiment,
            "group_id": exp["group_id"],
            "collected_at": c.now(),
            "execution_state": execution,
            "outcome": outcome,
            "partial": imported["classification"] == "incomplete",
            "task_digest": current_binding.get("task_digest") if verified else None,
            "freeze_checksum_verified": verified,
        }
        row["source_classification"] = row.pop("classification")
        row.pop("qualifying_final_trial", None)
        c.write_new(base / "evaluations" / (key + ".json"), row)
        results.append(row)
    return results


def check_controls(root, digest):
    available = set()
    for row in c.load(root).values():
        if (
            row["kind"] == "evaluation"
            and row.get("task_digest") == digest
            and row.get("freeze_checksum_verified")
            and row["execution_state"] == "completed"
            and row.get("agent") in {"oracle", "nop"}
            and row["outcome"] == ("pass" if row["agent"] == "oracle" else "fail")
        ):
            c.verify_inputs(root, row.get("evidence", []))
            available.add(row["agent"])
    if not {"oracle", "nop"}.issubset(available):
        raise c.MedicalError(
            "Verified runs require oracle pass and no-op fail on this task; use --diagnostic for exploration"
        )


def harbor_checksum(executable, snapshot):
    resolved = Path(shutil.which(executable) or executable).resolve()
    python = resolved.parent / "python"
    if not python.is_file():
        raise c.MedicalError("Select the Harbor executable in its runtime environment")
    digest = subprocess.check_output(
        [
            str(python),
            "-c",
            "import sys; from dirhash import dirhash; print(dirhash(sys.argv[1], 'sha256'))",
            str(snapshot),
        ],
        text=True,
    ).strip()
    if not harbor.checksum(digest):
        raise c.MedicalError("Could not establish the selected Harbor task checksum")
    return digest


def run(
    root,
    experiment,
    agent,
    executable,
    *,
    case=None,
    model=None,
    effort=None,
    diagnostic=False,
    preview=False,
):
    if agent == "codex" and not model:
        raise c.MedicalError("Name the model condition")
    exp, spec, task, files = task_validate(root, experiment, case)
    if preview:
        return {
            "experiment_id": experiment,
            "case": spec["id"],
            "agent": agent,
            "model": model,
            "reasoning_effort": effort,
            "diagnostic": diagnostic,
            "task_digest": tree_digest(files),
            "task_path": str(task),
            "executes": False,
        }
    if not diagnostic and agent == "codex":
        state = c.projection(root)[experiment]["current"]
        if state.get("assessment") in {"needs_review", "invalidated"}:
            raise c.MedicalError("Resolve the experiment issue or use an explicitly diagnostic run")
        check_controls(root, tree_digest(files))
    frozen = freeze(root, experiment, case)
    snapshot = restore_freeze(root, frozen)
    checksum = harbor_checksum(executable, snapshot)
    identity = c.uid("attempt")
    out = Path(root) / ".local/attempts" / identity
    out.mkdir(parents=True, exist_ok=False)
    base = Path(root) / Path(exp["record_path"]).parent
    attempt = {
        "schema_version": 2,
        "kind": "attempt",
        "id": identity,
        "experiment_id": experiment,
        "group_id": exp["group_id"],
        "freeze_id": frozen["id"],
        "task_digest": frozen["task_digest"],
        "case": spec["id"],
        "agent": agent,
        "model": model,
        "reasoning_effort": effort,
        "diagnostic": diagnostic,
        "execution_state": "running",
        "observed_at": c.now(),
        "execution_path": str((out / "execution.json").relative_to(root)),
    }
    c.write_new(base / "attempts" / (identity + ".json"), attempt)
    config_agent = {"name": agent, "env": {}, "kwargs": {}}
    if model:
        config_agent["model_name"] = model
    if effort:
        config_agent["kwargs"]["reasoning_effort"] = effort
    config = {
        "job_name": "job",
        "jobs_dir": str(out),
        "n_attempts": 1,
        "n_concurrent_trials": 1,
        "retry": {"max_retries": 0},
        "environment": {"type": "docker"},
        "agents": [config_agent],
        "tasks": [{"path": str(snapshot)}],
        "artifacts": ["/app"],
    }
    c.write_new(out / "config.json", config)
    receipt = {
        "attempt_id": identity,
        "execution_state": "running",
        "started_at": c.now(),
        "harbor_task_checksum": checksum,
    }
    c.write_new(out / "execution.json", receipt)
    try:
        with (out / "launcher.log").open("x") as log:
            process = subprocess.run(
                [executable, "run", "--config", str(out / "config.json")],
                cwd=root,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        receipt.update(
            execution_state="completed" if process.returncode == 0 else "error",
            exit_code=process.returncode,
        )
    except BaseException as exc:
        receipt.update(
            execution_state="interrupted" if isinstance(exc, KeyboardInterrupt) else "error",
            error_type=type(exc).__name__,
        )
        raise
    finally:
        receipt["finished_at"] = c.now()
        receipt["frozen_payload_unchanged"] = task_files(snapshot) == frozen["files"]
        c.atomic_write(out / "execution.json", receipt)
        key = c.uid("execution")
        c.write_new(
            base / "evaluations" / (key + ".json"),
            {
                "schema_version": 2,
                "kind": "evaluation",
                "id": key,
                "attempt_id": identity,
                "experiment_id": experiment,
                "group_id": exp["group_id"],
                "execution_state": receipt["execution_state"],
                "outcome": "no_verdict",
                "collected_at": receipt["finished_at"],
                "partial": True,
                "evidence": [c.evidence(root, attempt["execution_path"])],
            },
        )
    sources = [str(p.relative_to(root)) for p in sorted((out / "job").glob("*/result.json"))]
    receipt["collected"] = [r["id"] for r in collect(root, experiment, sources)]
    return receipt


def qualify_attempt(root, experiment, identity):
    """Reassess a diagnostic attempt using existing exact inputs and controls.

    This establishes local control eligibility, not current submission approval.
    """
    rows = c.load(root)
    attempt = rows[identity]
    if attempt["kind"] != "attempt" or attempt["experiment_id"] != experiment:
        raise c.MedicalError("Select an attempt from the reviewed experiment")
    if not attempt.get("freeze_id"):
        raise c.MedicalError("This historical attempt has no verified task binding")
    frozen = rows[attempt["freeze_id"]]
    restore_freeze(root, frozen)
    check_controls(root, frozen["task_digest"])
    observations = [
        r
        for r in rows.values()
        if r["kind"] == "evaluation"
        and r["attempt_id"] == identity
        and r["execution_state"] == "completed"
        and r["outcome"] in {"pass", "fail"}
        and r.get("task_digest") == frozen["task_digest"]
        and r.get("freeze_checksum_verified")
    ]
    if not observations:
        raise c.MedicalError("No normally completed scoring observation bound to that exact task")
    selected = max(observations, key=lambda r: r.get("collected_at", ""))
    c.verify_inputs(root, selected.get("evidence", []))
    return {
        "attempt_id": identity,
        "observation_id": selected["id"],
        "task_digest": frozen["task_digest"],
        "scope": "Local exact-task controls verified; target submission rules still apply.",
    }
