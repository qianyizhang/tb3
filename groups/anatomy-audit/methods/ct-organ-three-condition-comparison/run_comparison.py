"""Sequential, single-dispatch runner for the two fresh comparison conditions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNNER_PATH = Path(__file__).resolve()
BASE = ROOT / ".local/ct-organ-comparison"
EXPECTED_DIGEST = "fcf7827f7100d1ca54be84f6bc14fb320d27ca546fd5352ac45cb40b04110ab6"
IMAGE_RECORD = ROOT / ".local/ct-organ-segmentation-astra-xhigh/image-identities.json"
CLEARANCE = BASE / "parent-launch-clearance.json"
CONDITIONS = (
    {
        "slug": "sol-xhigh",
        "experiment": "ct-organ-segmentation-sol-xhigh",
        "model": "openai/gpt-5.6-sol",
        "effort": "xhigh",
    },
    {
        "slug": "astra-medium",
        "experiment": "ct-organ-segmentation-astra-medium",
        "model": "openai/gpt-6-astra",
        "effort": "medium",
    },
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("checked_at must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("checked_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def atomic_write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=check, capture_output=True, text=True)


def docker_ids() -> dict[str, str]:
    identities = json.loads(IMAGE_RECORD.read_text())["identities"]
    for key, tag in (
        ("solver", "tb3-ct-organ-solver:v1"),
        ("transport", "tb3-ct-organ-transport:v1"),
    ):
        actual = run(["docker", "image", "inspect", "--format", "{{.Id}}", tag]).stdout.strip()
        if actual != identities[key]:
            raise RuntimeError(f"{key} image drift: expected {identities[key]}, found {actual}")
    return identities


def require_clearance() -> dict[str, object]:
    if not CLEARANCE.is_file():
        raise RuntimeError(f"parent launch clearance missing: {CLEARANCE}")
    clearance = json.loads(CLEARANCE.read_text())
    if clearance.get("approved") is not True:
        raise RuntimeError("parent launch clearance is not approved")
    if clearance.get("task_digest") != EXPECTED_DIGEST:
        raise RuntimeError("parent launch clearance names a different task digest")
    expected = [item["slug"] for item in CONDITIONS]
    if clearance.get("conditions") != expected:
        raise RuntimeError("parent launch clearance does not name the fixed conditions in order")
    current_hash = hashlib.sha256(RUNNER_PATH.read_bytes()).hexdigest()
    if clearance.get("operator_sha256") != current_hash:
        raise RuntimeError(
            "parent launch clearance does not match the current runner: "
            f"expected {current_hash}, found {clearance.get('operator_sha256')}"
        )
    return clearance


def preview(condition: dict[str, str]) -> dict[str, object]:
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
        "--preview",
    ]
    payload = json.loads(run(command).stdout)
    if payload.get("task_digest") != EXPECTED_DIGEST or payload.get("executes") is not False:
        raise RuntimeError(f"preview mismatch for {condition['slug']}: {payload}")
    return payload


def active_task_containers() -> list[str]:
    result = run(["docker", "ps", "--format", "{{.Names}}"])
    return [name for name in result.stdout.splitlines() if "task__" in name]


def require_idle_host() -> None:
    active = active_task_containers()
    if active:
        raise RuntimeError("another task container is active: " + ", ".join(active))


def wait_for_idle_host(timeout_seconds: float = 120.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while active_task_containers():
        if time.monotonic() >= deadline:
            require_idle_host()
        time.sleep(2)


def quota_receipt_path(condition: dict[str, str]) -> Path:
    return BASE / f"quota-clearance-{condition['slug']}.json"


def existing_dispatched_state(condition: dict[str, str]) -> dict[str, object] | None:
    condition_dir = BASE / condition["slug"]
    marker = condition_dir / "dispatch-once.json"
    if not marker.exists():
        return None
    state_path = condition_dir / "operator-state.json"
    if not state_path.is_file():
        raise RuntimeError(f"{condition['slug']} has a dispatch marker but no state")
    state = json.loads(state_path.read_text())
    if state.get("state") != "terminal":
        raise RuntimeError(f"{condition['slug']} was dispatched and is not durably terminal")
    return state


def check_quota_receipt(condition: dict[str, str]) -> tuple[dict[str, object] | None, str]:
    path = quota_receipt_path(condition)
    if not path.is_file():
        return None, f"waiting for {path.name}"
    try:
        receipt = json.loads(path.read_text())
        if receipt.get("approved") is not True:
            raise ValueError("approved must be true")
        if receipt.get("condition") != condition["slug"]:
            raise ValueError("condition mismatch")
        if receipt.get("task_digest") != EXPECTED_DIGEST:
            raise ValueError("task digest mismatch")
        remaining = receipt.get("remaining_percent")
        if isinstance(remaining, bool) or not isinstance(remaining, (int, float)):
            raise ValueError("remaining_percent must be numeric")
        if float(remaining) <= 25.0:
            raise ValueError("remaining_percent must be greater than 25")
        checked_at = parse_time(receipt.get("checked_at"))
        age = datetime.now(timezone.utc) - checked_at
        if age < timedelta(seconds=-60):
            raise ValueError("checked_at is in the future")
        if age > timedelta(minutes=10):
            raise ValueError("quota receipt is older than ten minutes")
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return None, f"invalid quota receipt: {exc}"
    return receipt, "ready"


def wait_for_quota_clearance(
    condition: dict[str, str], overall: dict[str, object]
) -> dict[str, object]:
    condition_dir = BASE / condition["slug"]
    condition_dir.mkdir(parents=True, exist_ok=True)
    waiting_path = condition_dir / "operator-state.json"
    while True:
        receipt, reason = check_quota_receipt(condition)
        if receipt is not None:
            return receipt
        waiting = {
            "condition": condition,
            "state": "waiting_quota_clearance",
            "reason": reason,
            "receipt_path": str(quota_receipt_path(condition)),
            "last_checked_at": now(),
            "dispatch_created": False,
        }
        atomic_write(waiting_path, waiting)
        overall.update(
            state="waiting_quota_clearance",
            current_condition=condition["slug"],
            quota_wait=waiting,
            last_updated_at=now(),
        )
        atomic_write(BASE / "operator-state.json", overall)
        time.sleep(15)


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
    *, container: str, attempt_path: Path, expected_solver: str, condition: dict[str, str]
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
        "docker_socket_absent": all(item["destination"] != "/var/run/docker.sock" for item in mounts),
        "capabilities_dropped": "ALL" in (info["HostConfig"].get("CapDrop") or []),
        "no_new_privileges": "no-new-privileges:true" in (info["HostConfig"].get("SecurityOpt") or []),
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
    condition: dict[str, str],
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
    experiment_dir = ROOT / "groups/anatomy-audit/experiments" / condition["experiment"]
    before = set((experiment_dir / "attempts").glob("*.json")) if (experiment_dir / "attempts").exists() else set()
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
    with marker.open("x") as stream:
        json.dump(
            {"created_at": now(), "operator_pid": os.getpid(), "command": command},
            stream,
            indent=2,
        )
        stream.write("\n")

    credentials = tempfile.TemporaryDirectory(prefix="tb3-ct-organ-comparison-auth-")
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


def check_only() -> None:
    clearance = require_clearance()
    identities = docker_ids()
    previews = {item["slug"]: preview(item) for item in CONDITIONS}
    require_idle_host()
    next_condition = None
    quota = None
    for condition in CONDITIONS:
        state = existing_dispatched_state(condition)
        if state is None:
            next_condition = condition
            quota, reason = check_quota_receipt(condition)
            if quota is None:
                raise RuntimeError(reason)
            break
        if state.get("condition_status") != "completed":
            raise RuntimeError(
                f"{condition['slug']} is terminal with {state.get('condition_status')}"
            )
    print(
        json.dumps(
            {
                "executes": False,
                "clearance": clearance,
                "image_identities": identities,
                "previews": previews,
                "host_idle": True,
                "next_condition": next_condition,
                "next_condition_quota": quota,
            },
            indent=2,
        )
    )


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    clearance = require_clearance()
    identities = docker_ids()
    previews = {item["slug"]: preview(item) for item in CONDITIONS}
    overall: dict[str, object] = {
        "operator_pid": os.getpid(),
        "started_at": now(),
        "state": "running",
        "task_digest": EXPECTED_DIGEST,
        "clearance": clearance,
        "image_identities": identities,
        "previews": previews,
        "order": [item["slug"] for item in CONDITIONS],
        "conditions": {},
    }
    atomic_write(BASE / "operator-state.json", overall)
    for condition in CONDITIONS:
        try:
            state = existing_dispatched_state(condition)
        except RuntimeError as exc:
            overall.update(
                state="stopped_existing_dispatch_incomplete",
                stop_condition=condition["slug"],
                stop_error=str(exc),
                finished_at=now(),
            )
            atomic_write(BASE / "operator-state.json", overall)
            return
        if state is None:
            quota_clearance = wait_for_quota_clearance(condition, overall)
            overall.update(
                state="dispatching",
                current_condition=condition["slug"],
                quota_wait=None,
                last_updated_at=now(),
            )
            atomic_write(BASE / "operator-state.json", overall)
            state = run_condition(
                condition,
                identities,
                previews[condition["slug"]],
                quota_clearance,
            )
        overall["conditions"][condition["slug"]] = state
        overall["last_updated_at"] = now()
        atomic_write(BASE / "operator-state.json", overall)
        if state.get("condition_status") != "completed":
            overall.update(
                state="stopped_after_condition_error",
                stop_condition=condition["slug"],
                stop_status=state.get("condition_status"),
                finished_at=now(),
            )
            atomic_write(BASE / "operator-state.json", overall)
            return
        try:
            wait_for_idle_host()
        except RuntimeError as exc:
            overall.update(
                state="stopped_host_not_idle",
                stop_condition=condition["slug"],
                stop_error=str(exc),
                finished_at=now(),
            )
            atomic_write(BASE / "operator-state.json", overall)
            return
    overall.update(state="terminal", finished_at=now())
    atomic_write(BASE / "operator-state.json", overall)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only:
        check_only()
    else:
        main()
