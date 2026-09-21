"""Single-dispatch native operator; it never retries or feeds scores to the solver."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / ".local/ct-organ-segmentation-astra-xhigh"
EXPERIMENT = ROOT / "groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save(state: dict[str, object]) -> None:
    temporary = BASE / "operator-state.tmp"
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(BASE / "operator-state.json")


def ensure_idle_solver_host() -> None:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        check=True,
        capture_output=True,
        text=True,
    )
    task_containers = [line for line in result.stdout.splitlines() if "task__" in line]
    if task_containers:
        raise RuntimeError(
            "another task container is active; wait for terminal review: "
            + ", ".join(task_containers)
        )


def main() -> None:
    if not (BASE / "isolation-preflight.json").is_file():
        raise RuntimeError("isolation preflight has not passed")
    ensure_idle_solver_host()
    with (BASE / "dispatch-once.json").open("x") as marker:
        json.dump({"created_at": now(), "operator_pid": os.getpid()}, marker)

    before = set((EXPERIMENT / "attempts").glob("*.json"))
    command = [
        str(ROOT / ".venv/bin/med"),
        "run",
        "ct-organ-segmentation-astra-xhigh",
        "--model",
        "openai/gpt-6-astra",
        "--effort",
        "xhigh",
        "--harbor",
        str(ROOT / ".venv/bin/harbor"),
    ]
    credentials = tempfile.TemporaryDirectory(prefix="tb3-ct-organ-auth-")
    auth = Path(credentials.name) / "auth.json"
    shutil.copyfile(Path.home() / ".codex/auth.json", auth)
    auth.chmod(0o644)
    environment = dict(os.environ, CODEX_AUTH_JSON_PATH=str(auth))
    log = (BASE / "operator.log").open("x")
    child = subprocess.Popen(
        command,
        cwd=ROOT,
        env=environment,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    state: dict[str, object] = {
        "operator_pid": os.getpid(),
        "med_pid": child.pid,
        "med_pgid": child.pid,
        "command": command,
        "started_at": now(),
        "state": "running",
        "automatic_retries": 0,
    }
    save(state)
    capture = None
    capture_file = None
    while child.poll() is None:
        if "attempt_id" not in state:
            for path in set((EXPERIMENT / "attempts").glob("*.json")) - before:
                attempt = json.loads(path.read_text())
                if attempt["agent"] == "codex":
                    state["attempt_id"] = attempt["id"]
                    state["task_digest"] = attempt["task_digest"]
                    state["attempt_path"] = str(ROOT / ".local/attempts" / attempt["id"])
                    save(state)
        if capture is None and "attempt_path" in state:
            attempt_path = Path(str(state["attempt_path"]))
            for trial in (attempt_path / "job").glob("task__*"):
                project = re.sub("[^a-z0-9_-]", "-", trial.name.lower())
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "-q",
                        "--filter",
                        "label=com.docker.compose.project=" + project,
                        "--filter",
                        "label=com.docker.compose.service=transport",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                container = result.stdout.strip()
                if result.returncode == 0 and container and "\n" not in container:
                    capture_file = (BASE / "model-transport.log").open("x")
                    capture = subprocess.Popen(
                        ["docker", "logs", "--follow", container],
                        stdout=capture_file,
                        stderr=subprocess.STDOUT,
                    )
                    state.update(
                        trial_path=str(trial),
                        compose_project=project,
                        transport_container=container,
                        transport_capture_pid=capture.pid,
                    )
                    save(state)
        time.sleep(3)
    state.update(state="terminal", exit_code=child.returncode, finished_at=now())
    save(state)
    if capture is not None:
        try:
            capture.wait(timeout=15)
        except subprocess.TimeoutExpired:
            capture.terminate()
            capture.wait(timeout=10)
        capture_file.close()
    log.close()
    credentials.cleanup()


if __name__ == "__main__":
    main()
