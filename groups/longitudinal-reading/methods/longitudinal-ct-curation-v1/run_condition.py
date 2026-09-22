"""Single-dispatch native med operator; isolation checks retained from the v1 CT operator.

No prior authoring module is imported or executed. One selected condition per call.
"""

from __future__ import annotations
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-curation-v1"
EXPECTED_DIGEST = ""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=check, capture_output=True, text=True)


def active_task_containers() -> list[str]:
    result = run(["docker", "ps", "--format", "{{.Names}}"])
    return [name for name in result.stdout.splitlines() if "task__" in name]


def require_idle_host() -> None:
    active = active_task_containers()
    if active:
        raise RuntimeError("another task container is active: " + ", ".join(active))


def compose_container(project: str, service: str) -> str | None:
    result = run(
        [
            "docker",
            "ps",
            "-q",
            "--filter",
            "label=com.docker.compose.project=" + project,
            "--filter",
            "label=com.docker.compose.service=" + service,
        ],
        check=False,
    )
    containers = [line for line in result.stdout.splitlines() if line]
    if result.returncode or len(containers) > 1:
        raise RuntimeError(f"could not identify one {service} container for {project}")
    return containers[0] if containers else None


def inspect_isolation(
    *, container: str, attempt_path: Path, expected_solver: str, condition: dict[str, object]
) -> dict[str, object]:
    info = json.loads(run(["docker", "inspect", container]).stdout)[0]
    networks = []
    for name in info["NetworkSettings"]["Networks"]:
        network = json.loads(run(["docker", "network", "inspect", name]).stdout)[0]
        networks.append({"name": name, "internal": bool(network["Internal"])})
    mounts = [
        {
            "type": mount["Type"],
            "source": mount["Source"],
            "destination": mount["Destination"],
            "rw": bool(mount["RW"]),
        }
        for mount in info["Mounts"]
    ]
    expected_destinations = {"/logs/agent", "/logs/artifacts", "/logs/verifier"}
    source_root = str(attempt_path.resolve()) + os.sep
    checks = {
        "solver_image_exact": info["Image"] == expected_solver,
        "all_networks_internal": bool(networks) and all(item["internal"] for item in networks),
        "only_standard_log_mounts": (
            {item["destination"] for item in mounts} == expected_destinations
            and all(item["type"] == "bind" for item in mounts)
            and all(str(Path(item["source"]).resolve()).startswith(source_root) for item in mounts)
        ),
        "docker_socket_absent": all(
            item["destination"] != "/var/run/docker.sock" for item in mounts
        ),
        "capabilities_dropped": "ALL" in (info["HostConfig"].get("CapDrop") or []),
        "no_new_privileges": "no-new-privileges:true"
        in (info["HostConfig"].get("SecurityOpt") or []),
        "memory_cap_12_gib": info["HostConfig"].get("Memory") == 12 * 1024**3,
        "cpu_cap_4": info["HostConfig"].get("NanoCpus") == 4_000_000_000,
        "no_gpu_device_requests": not (info["HostConfig"].get("DeviceRequests") or []),
    }
    receipt = {
        "observed_at": now(),
        "condition": condition,
        "container": container,
        "image": info["Image"],
        "networks": networks,
        "mounts": mounts,
        "cap_drop": info["HostConfig"].get("CapDrop"),
        "security_opt": info["HostConfig"].get("SecurityOpt"),
        "memory_cap_bytes": info["HostConfig"].get("Memory"),
        "nano_cpus": info["HostConfig"].get("NanoCpus"),
        "device_requests": info["HostConfig"].get("DeviceRequests"),
        "checks": checks,
        "passed": all(checks.values()),
        "limits_note": "Configured Docker caps are ceilings, not guaranteed host allocation.",
    }
    if not receipt["passed"]:
        raise RuntimeError("live isolation assertion failed: " + json.dumps(receipt))
    return receipt


def terminate(child: subprocess.Popen[bytes]) -> None:
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=10)


def run_condition(
    condition: dict[str, object],
    identities: dict[str, str],
    preview_receipt: dict[str, object],
    quota_clearance: dict[str, object],
) -> dict[str, object]:
    slug = condition["slug"]
    condition_dir = BASE / slug
    condition_dir.mkdir(parents=True, exist_ok=True)
    marker = condition_dir / "dispatch-once.json"
    state_path = condition_dir / "operator-state.json"
    if marker.exists():
        if state_path.is_file():
            state = json.loads(state_path.read_text())
            if state.get("state") == "terminal":
                return state
        raise RuntimeError(f"{slug} was already dispatched and is not durably terminal")

    require_idle_host()
    experiment_dir = ROOT / "groups/longitudinal-reading/experiments" / condition["experiment"]
    before = (
        set((experiment_dir / "attempts").glob("*.json"))
        if (experiment_dir / "attempts").exists()
        else set()
    )
    command = [
        str(ROOT / ".venv/bin/med"),
        "run",
        condition["experiment"],
        "--model",
        condition["model"],
        "--effort",
        condition["effort"],
        "--harbor",
        str(ROOT / ".venv/bin/harbor"),
    ]
    if condition.get("diagnostic", True):
        command.append("--diagnostic")
    with marker.open("x") as stream:
        json.dump(
            {"created_at": now(), "operator_pid": os.getpid(), "command": command},
            stream,
            indent=2,
        )
        stream.write("\n")

    credentials = tempfile.TemporaryDirectory(prefix="tb3-longitudinal-image-only-auth-")
    auth = Path(credentials.name) / "auth.json"
    shutil.copyfile(Path.home() / ".codex/auth.json", auth)
    auth.chmod(0o644)
    environment = dict(os.environ, CODEX_AUTH_JSON_PATH=str(auth))
    log = (condition_dir / "operator.log").open("x")
    child = subprocess.Popen(
        command,
        cwd=ROOT,
        env=environment,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    state: dict[str, object] = {
        "condition": condition,
        "preview": preview_receipt,
        "quota_clearance": quota_clearance,
        "operator_pid": os.getpid(),
        "med_pid": child.pid,
        "med_pgid": child.pid,
        "command": command,
        "started_at": now(),
        "state": "running",
        "automatic_retries": 0,
    }
    atomic_write(state_path, state)
    transport_capture: subprocess.Popen[bytes] | None = None
    transport_file = None
    try:
        while child.poll() is None:
            if "attempt_id" not in state and (experiment_dir / "attempts").exists():
                for path in set((experiment_dir / "attempts").glob("*.json")) - before:
                    attempt = json.loads(path.read_text())
                    if attempt.get("agent") == "codex":
                        if attempt.get("task_digest") != EXPECTED_DIGEST:
                            raise RuntimeError("native attempt has the wrong task digest")
                        state.update(
                            attempt_id=attempt["id"],
                            task_digest=attempt["task_digest"],
                            attempt_path=str(ROOT / ".local/attempts" / attempt["id"]),
                        )
                        atomic_write(state_path, state)
                        break
            if "attempt_path" in state:
                attempt_path = Path(str(state["attempt_path"]))
                trials = list((attempt_path / "job").glob("task__*"))
                if len(trials) > 1:
                    raise RuntimeError("more than one Harbor trial found")
                if trials and "trial_path" not in state:
                    trial = trials[0]
                    state["trial_path"] = str(trial)
                    state["compose_project"] = re.sub("[^a-z0-9_-]", "-", trial.name.lower())
                    atomic_write(state_path, state)
                project = state.get("compose_project")
                if project and "live_isolation_path" not in state:
                    main = compose_container(str(project), "main")
                    if main:
                        receipt = inspect_isolation(
                            container=main,
                            attempt_path=attempt_path,
                            expected_solver=identities["solver"],
                            condition=condition,
                        )
                        receipt_path = condition_dir / "live-isolation.json"
                        atomic_write(receipt_path, receipt)
                        state.update(main_container=main, live_isolation_path=str(receipt_path))
                        atomic_write(state_path, state)
                if project and transport_capture is None:
                    transport = compose_container(str(project), "transport")
                    if transport:
                        transport_file = (condition_dir / "model-transport.log").open("x")
                        transport_capture = subprocess.Popen(
                            ["docker", "logs", "--follow", transport],
                            stdout=transport_file,
                            stderr=subprocess.STDOUT,
                        )
                        state.update(
                            transport_container=transport,
                            transport_capture_pid=transport_capture.pid,
                        )
                        atomic_write(state_path, state)
            time.sleep(2)
    except BaseException as exc:
        state.update(operator_error=repr(exc), failed_at=now())
        atomic_write(state_path, state)
        terminate(child)
    finally:
        child.wait()
        state.update(state="terminal", exit_code=child.returncode, finished_at=now())
        if "attempt_path" in state:
            execution = Path(str(state["attempt_path"])) / "execution.json"
            if execution.is_file():
                state["native_execution"] = json.loads(execution.read_text())
        isolation_path = state.get("live_isolation_path")
        isolation_ok = False
        if isolation_path and Path(str(isolation_path)).is_file():
            isolation_ok = json.loads(Path(str(isolation_path)).read_text()).get("passed") is True
        native = state.get("native_execution")
        native_ok = (
            isinstance(native, dict)
            and native.get("execution_state") == "completed"
            and native.get("exit_code") == 0
            and native.get("frozen_payload_unchanged") is True
        )
        transport_ok = (condition_dir / "model-transport.log").is_file()
        if state.get("operator_error"):
            state["condition_status"] = "isolation_or_operator_error"
        elif child.returncode != 0 or not native_ok:
            state["condition_status"] = "execution_error"
        elif not isolation_ok or not transport_ok:
            state["condition_status"] = "evidence_incomplete"
        else:
            state["condition_status"] = "completed"
        atomic_write(state_path, state)
        if transport_capture is not None:
            try:
                transport_capture.wait(timeout=15)
            except subprocess.TimeoutExpired:
                transport_capture.terminate()
                transport_capture.wait(timeout=10)
            assert transport_file is not None
            transport_file.close()
        log.close()
        credentials.cleanup()
    return state


def main():
    global BASE, EXPECTED_DIGEST
    specification = json.loads((BASE / "study.json").read_text())
    EXPECTED_DIGEST = specification["task_digest"]
    condition = {
        "slug": "astra-medium",
        "experiment": specification["experiment_id"],
        "model": "openai/gpt-6-astra",
        "effort": "medium",
        "diagnostic": True,
    }
    identities = json.loads((BASE / "image-identities.json").read_text())
    for expected in identities.values():
        assert (
            run(["docker", "image", "inspect", "--format", "{{.Id}}", expected]).stdout.strip()
            == expected
        )
    preview = json.loads(
        run(
            [
                str(ROOT / ".venv/bin/med"),
                "run",
                condition["experiment"],
                "--model",
                condition["model"],
                "--effort",
                condition["effort"],
                "--preview",
                "--diagnostic",
            ]
        ).stdout
    )
    assert preview["task_digest"] == EXPECTED_DIGEST
    assert json.loads((BASE / "preflight.json").read_text())["passed"] is True
    quota = json.loads((BASE / "quota-astra-medium.json").read_text())
    assert quota["ordinary_usage_allowed"] is True
    state = run_condition(condition, identities, preview, quota)
    print(json.dumps(state, indent=2))
    if state["condition_status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
