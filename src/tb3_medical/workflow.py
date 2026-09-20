"""Explicit task preparation, content-addressed freezes and bounded Harbor runs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib

from . import core as c, harbor


def task_files(path):
    files = {}
    for p in sorted(path.rglob("*")):
        if p.is_symlink():
            raise c.MedicalError(f"Task contains a symlink: {p}")
        if p.is_file() and "__pycache__" not in p.parts:
            files[p.relative_to(path).as_posix()] = c.sha(p)
    return files


def tree_digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def new(root, group, key, title):
    g = c.lookup(root, group)
    if g["kind"] != "group" or key in c.load(root):
        raise c.MedicalError("Select a group and an unused experiment ID")
    c.identifier(key)
    base = c.destination(root, g, "experiments") / key
    base.mkdir(parents=True, exist_ok=False)
    row = {"schema_version": 1, "kind": "experiment", "id": key, "group_id": g["id"],
           "title": title, "lifecycle": "draft", "depends_on": [], "execution_enabled": False,
           "task_path": str((base / "task").relative_to(root)), "prepare_command": [],
           "reproducibility": {"read": "available", "replay": "unverified", "rerun": "unverified"}}
    c.write_new(base / "experiment.json", row)
    (base / "protocol.md").write_text(f"# {title}\n\nQuestion, source selection, ground truth and licensing: TBD.\n\n"
        "Declare cases, conditions, model settings, endpoints and stop rules before running.\n"
        "Separate solver-visible files from evaluator references. Record partial attempts.\n")
    task = base / "task"
    for folder in ("environment", "tests", "solution"):
        (task / folder).mkdir(parents=True)
    (task / "instruction.md").write_text("# Draft task\n\nReplace this scaffold with the solver-facing instruction.\n")
    (task / "task.toml").write_text('version = "1.0"\n\n[metadata]\nauthor_name = "TBD"\n\n[agent]\ntimeout_sec = 600.0\n\n[verifier]\ntimeout_sec = 60.0\n\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory_mb = 2048\nstorage_mb = 4096\n')
    (task / "environment/Dockerfile").write_text("# Pin an appropriate image digest and dependency lock before enabling execution.\nFROM python:3.12-slim\nWORKDIR /app\n")
    (task / "tests/test.sh").write_text("#!/bin/sh\nset -eu\necho 'Draft verifier: implement independent checks' >&2\nexit 1\n")
    (task / "solution/solve.sh").write_text("#!/bin/sh\nset -eu\necho 'Draft oracle: implement a valid solution' >&2\nexit 1\n")
    return row


def task_validate(root, experiment):
    exp = c.lookup(root, experiment)
    if exp["kind"] != "experiment" or not exp.get("task_path"):
        raise c.MedicalError("Historical experiment needs an explicit task_path adapter")
    task = c.inside(root, exp["task_path"])
    required = ("instruction.md", "task.toml", "environment/Dockerfile", "tests/test.sh", "solution/solve.sh")
    missing = [p for p in required if not (task / p).is_file()]
    if missing:
        raise c.MedicalError("Missing task inputs: " + ", ".join(missing))
    with (task / "task.toml").open("rb") as stream:
        tomllib.load(stream)
    return exp, task, task_files(task)


def prepare(root, experiment, execute=False):
    exp = c.lookup(root, experiment)
    command = exp.get("prepare_command", [])
    if execute:
        if not command or not all(isinstance(s, str) for s in command):
            raise c.MedicalError("Declare a prepare_command argv in the experiment first")
        subprocess.run(command, cwd=root, check=True)
    return {"command": command, "executed": execute, "task_path": exp.get("task_path"),
            "note": "Preparation never freezes or launches inference implicitly."}


def freeze(root, experiment):
    root = Path(root).resolve()
    exp, task, files = task_validate(root, experiment)
    if not exp.get("execution_enabled"):
        raise c.MedicalError("Finish source/reference review and set execution_enabled before freezing")
    digest = tree_digest(files)
    key = "freeze-" + digest[:24]
    if key in c.load(root):
        existing = c.lookup(root, key)
        if existing["experiment_id"] != exp["id"]:
            raise c.MedicalError("Identical snapshot is already owned by another experiment")
        return existing
    snapshot = Path(root) / ".cache/medical/freezes" / digest / "task"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.exists():
        if task_files(snapshot) != files:
            raise c.MedicalError("Existing frozen payload changed")
    else:
        shutil.copytree(task, snapshot, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if task_files(snapshot) != files or task_files(task) != files:
        raise c.MedicalError("Task changed during freeze")
    row = {"schema_version": 1, "kind": "freeze", "id": key, "group_id": exp["group_id"],
           "experiment_id": exp["id"], "created_at": c.now(), "task_digest": digest,
           "digest_kind": "sha256-canonical-path-sha256-map-v1", "files": files,
           "source_path": exp["task_path"], "snapshot_path": str(snapshot.relative_to(root)),
           "depends_on": [], "evidence": [c.evidence(root, str(snapshot.relative_to(root) / p)) for p in files]}
    c.write_new(c.destination(root, exp, "experiments") / Path(exp["record_path"]).parent.name / "freezes" / (key + ".json"), row)
    return row


def restore_freeze(root, record):
    snapshot = c.inside(root, record["snapshot_path"])
    if not snapshot.exists():
        source = c.inside(root, record["source_path"])
        if task_files(source) != record["files"]:
            raise c.MedicalError("Frozen payload unavailable; restore files using freeze.files digests")
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, snapshot, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if task_files(snapshot) != record["files"]:
        raise c.MedicalError("Frozen task digest mismatch")
    return snapshot


def plan(root, frozen, agent, model=None, effort=None):
    f = c.lookup(root, frozen)
    if f["kind"] != "freeze" or agent not in {"oracle", "nop", "codex"}:
        raise c.MedicalError("Plan requires a freeze ID and oracle, nop or codex agent")
    if agent == "codex" and not model:
        raise c.MedicalError("A model condition must name its model")
    row = {"schema_version": 1, "kind": "plan", "id": c.uid("plan"),
           "group_id": f["group_id"], "experiment_id": f["experiment_id"], "freeze_id": f["id"],
           "task_digest": f["task_digest"], "agent": agent, "model": model, "reasoning_effort": effort,
           "n_attempts": 1, "max_retries": 0, "concurrency": 1, "created_at": c.now(),
           "depends_on": [f["id"]], "planned_state": "pending"}
    exp = c.lookup(root, f["experiment_id"])
    c.write_new(Path(root) / Path(exp["record_path"]).parent / "plans" / (row["id"] + ".json"), row)
    return row


def collect(root, experiment, sources, task_digest=None, expected_checksum=None):
    exp = c.lookup(root, experiment)
    result = []
    for source in sources:
        src = c.inside(root, source)
        imported = harbor.import_trial(Path(root), src)
        identity = "attempt-" + hashlib.sha256(imported["source_result"].encode()).hexdigest()[:24]
        # Collection snapshots may change as an interrupted trial gains evidence; identity does not.
        observation = "observation-" + hashlib.sha256((identity + imported["evidence_sha256"]).encode()).hexdigest()[:24]
        current = c.load(root)
        if identity not in current:
            attempt = {"schema_version": 1, "kind": "attempt", "id": identity,
                       "group_id": exp["group_id"], "experiment_id": exp["id"],
                       "source_result": imported["source_result"], "depends_on": []}
            c.write_new(Path(root) / Path(exp["record_path"]).parent / "attempts" / (identity + ".json"), attempt)
        elif current[identity]["experiment_id"] != exp["id"]:
            raise c.MedicalError("This attempt already belongs to another experiment")
        if observation not in current:
            row = {**imported, "kind": "evaluation", "id": observation, "attempt_id": identity,
                   "group_id": exp["group_id"], "experiment_id": exp["id"], "collected_at": c.now(),
                   "task_digest": task_digest if expected_checksum and imported["task_checksum"] == expected_checksum else None,
                   "freeze_checksum_verified": bool(expected_checksum and imported["task_checksum"] == expected_checksum),
                   "depends_on": [identity], "validity": "unreviewed",
                   "completeness": "partial" if imported["classification"] == "incomplete" else "observed"}
            c.write_new(Path(root) / Path(exp["record_path"]).parent / "evaluations" / (observation + ".json"), row)
            result.append(row)
        else:
            result.append(current[observation])
    return result


def check_controls(root, plan_record):
    rows = c.projection(root).values()
    available = {r.get("agent") for r in rows if r["kind"] == "evaluation"
                 and r.get("task_digest") == plan_record["task_digest"]
                 and r.get("freeze_checksum_verified")
                 and r.get("classification") in {"control_pass", "control_fail"}
                 and r.get("reward") == (1 if r.get("agent") == "oracle" else 0)
                 and r["current"]["validity"] not in {"invalidated", "under_review", "superseded"}
                 and r["current"]["availability"] == "available"}
    if not {"oracle", "nop"}.issubset(available):
        raise c.MedicalError("Model execution requires normal oracle=1 and nop=0 on this exact freeze")


def run(root, planned, executable):
    p = c.lookup(root, planned)
    if p["kind"] != "plan":
        raise c.MedicalError("Select a plan record")
    f = c.lookup(root, p["freeze_id"])
    snapshot = restore_freeze(root, f)
    current = c.projection(root)[p["id"]]["current"]
    if current["validity"] in {"under_review", "invalidated", "superseded"}:
        raise c.MedicalError("Plan or frozen evidence requires review before execution")
    if p["agent"] == "codex":
        check_controls(root, p)
    checksum = harbor_checksum(executable, snapshot)
    # A plan is single use even after an error/interruption. Retry is a new explicit plan.
    out = Path(root) / "runs/medical" / p["id"]
    out.mkdir(parents=True, exist_ok=False)
    receipt = {"plan_id": p["id"], "state": "running", "started_at": c.now()}
    c.write_new(out / "execution.json", receipt)
    agent = {"name": p["agent"], "env": {}, "kwargs": {}}
    if p.get("model"):
        agent["model_name"] = p["model"]
    if p.get("reasoning_effort"):
        agent["kwargs"]["reasoning_effort"] = p["reasoning_effort"]
    config = {"job_name": "job", "jobs_dir": str(out), "n_attempts": 1, "n_concurrent_trials": 1,
              "retry": {"max_retries": 0}, "environment": {"type": "docker"},
              "agents": [agent], "tasks": [{"path": str(snapshot)}], "artifacts": ["/app"]}
    c.write_new(out / "config.json", config)
    try:
        with (out / "launcher.log").open("x") as log:
            process = subprocess.run([executable, "run", "--config", str(out / "config.json")], cwd=root, stdout=log, stderr=subprocess.STDOUT)
        receipt.update(state="completed" if process.returncode == 0 else "execution_error", exit_code=process.returncode)
    except BaseException as exc:
        receipt.update(state="interrupted" if isinstance(exc, KeyboardInterrupt) else "launcher_error", error_type=type(exc).__name__)
        raise
    finally:
        receipt["finished_at"] = c.now()
        receipt["frozen_payload_unchanged"] = task_files(snapshot) == f["files"]
        c.atomic_write(out / "execution.json", receipt)
    sources = [str(x.relative_to(root)) for x in sorted((out / "job").glob("*/result.json"))]
    receipt["collected"] = [r["id"] for r in collect(root, p["experiment_id"], sources,
        p["task_digest"] if receipt["frozen_payload_unchanged"] else None, checksum)]
    c.atomic_write(out / "execution.json", receipt)
    return receipt


def harbor_checksum(executable, snapshot):
    """Use the selected Harbor runtime's exact checksum algorithm, not our tree digest."""
    resolved = Path(shutil.which(executable) or executable).absolute()
    python = resolved.parent / "python"
    if not python.is_file():
        raise c.MedicalError("Select a Harbor executable with its adjacent Python runtime")
    result = subprocess.check_output([str(python), "-c", "import sys; from dirhash import dirhash; print(dirhash(sys.argv[1], 'sha256'))", str(snapshot)], text=True).strip()
    if not harbor.checksum(result): raise c.MedicalError("Unable to establish Harbor task checksum")
    return result
