#!/usr/bin/env python3
"""Small, evidence-first local runner for the pinned Terminal-Bench 3 checkout.

This intentionally plans commands but never runs models.  The upstream checkout
is a pinned input, rather than a vendored or reimplemented set of TB3 rules.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit


UPSTREAM_COMMIT = "e2995b93b0a46edee7bc9942ea5622411a6d5bb9"
REQUIRED_TASK_FILES = (
    "task.toml",
    "instruction.md",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/Dockerfile",
    "tests/test.sh",
)
STATIC_CHECKS = (
    ("Canary strings", "check-canary.sh"),
    ("Dockerfile refs", "check-dockerfile-references.sh"),
    ("Dockerfile sanity", "check-dockerfile-sanity.sh"),
    ("Dockerfile platform", "check-dockerfile-platform.sh"),
    ("Absolute paths", "check-task-absolute-path.sh"),
    ("Test refs", "check-test-file-references.sh"),
    ("test.sh sanity", "check-test-sh-sanity.sh"),
    ("Task fields", "check-task-fields.sh"),
    ("Task timeout cap", "check-task-timeout.sh"),
    ("Instruction suffix", "check-instruction-suffix.sh"),
    ("GPU types", "check-gpu-types.sh"),
    ("Allow internet", "check-allow-internet.sh"),
    ("No internet opt-in", "check-no-allow-internet-true.sh"),
    ("Task slug length", "check-task-slug.sh"),
    ("Task package name", "check-task-package-name.sh"),
    ("Separate verifier", "check-separate-verifier.sh"),
    ("Verifier tooling baked", "check-verifier-tooling-baked.sh"),
    ("Trial network fetch", "check-trial-network-fetch.sh"),
    ("Pip pinning", "check-pip-pinning.sh"),
    ("Pytest version pin", "check-pytest-version.sh"),
    ("Nproc usage", "check-nproc.sh"),
    ("Compose host binds", "check-compose-host-binds.sh"),
)


class RunnerError(RuntimeError):
    """A preflight error which must never silently become a passing result."""


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_upstream() -> Path:
    return _root() / ".cache" / "terminal-bench"


def _default_harbor() -> Path:
    local = _root() / ".venv" / "bin" / "harbor"
    return local if local.exists() else Path("harbor")


def _default_upstream_lock() -> Path:
    return _root() / "configs" / "upstream-lock.json"


def _quote(value: str | Path) -> str:
    """POSIX shell quote without invoking a shell."""
    return "'" + str(value).replace("'", "'\"'\"'") + "'"


def _agent_proxy_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError("agent proxy must be an absolute http(s) URL")
    if parsed.username is not None or parsed.password is not None:
        raise argparse.ArgumentTypeError("agent proxy URL must not contain credentials")
    return value


def _agent_proxy_flags(agent_proxy: str | None) -> str:
    if agent_proxy is None:
        return ""
    variables = (
        f"http_proxy={agent_proxy}",
        f"https_proxy={agent_proxy}",
        f"HTTP_PROXY={agent_proxy}",
        f"HTTPS_PROXY={agent_proxy}",
        "NO_PROXY=localhost,127.0.0.1",
    )
    return "".join(f" --ae {_quote(variable)}" for variable in variables)


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _static_runtime() -> dict[str, str]:
    """Describe the interpreter deliberately placed first for upstream scripts."""
    python_bin = Path(sys.executable).parent
    return {
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "path_prefix": str(python_bin),
        "python3_command": str(python_bin / "python3"),
    }


def _static_environment() -> dict[str, str]:
    environment = os.environ.copy()
    python_bin = _static_runtime()["path_prefix"]
    environment["PATH"] = python_bin + os.pathsep + environment.get("PATH", "")
    return environment


def task_hash(task: Path) -> str:
    """Hash task paths and bytes, making captured check results reproducible."""
    digest = hashlib.sha256()
    for path in sorted(task.rglob("*"), key=lambda item: item.relative_to(task).as_posix()):
        relative = path.relative_to(task).as_posix().encode()
        if path.is_symlink():
            digest.update(b"L\0" + relative + b"\0" + os.readlink(path).encode())
        elif path.is_file():
            digest.update(b"F\0" + relative + b"\0")
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        elif path.is_dir():
            digest.update(b"D\0" + relative + b"\0")
    return digest.hexdigest()


def _pinned_commit(upstream: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(upstream), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_upstream_lock(lock_path: Path) -> dict[str, Any]:
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RunnerError(f"cannot read upstream lock {lock_path}: {exc}") from exc
    if not isinstance(lock, dict):
        raise RunnerError(f"upstream lock {lock_path} is not an object")
    hashes = lock.get("sha256")
    if lock.get("commit") != UPSTREAM_COMMIT or not isinstance(hashes, dict) or not hashes:
        raise RunnerError(f"upstream lock {lock_path} does not pin {UPSTREAM_COMMIT}")
    if any(not isinstance(path, str) or not isinstance(value, str) for path, value in hashes.items()):
        raise RunnerError(f"upstream lock {lock_path} has invalid sha256 entries")
    return lock


def _validate_upstream(upstream: Path, lock_path: Path) -> dict[str, Any]:
    lock = _load_upstream_lock(lock_path)
    upstream_head = _pinned_commit(upstream)
    if upstream_head is None:
        raise RunnerError(f"cannot resolve git HEAD for pinned upstream: {upstream}")
    if upstream_head != UPSTREAM_COMMIT:
        raise RunnerError(f"upstream checkout is {upstream_head}, expected pinned {UPSTREAM_COMMIT}")
    for relative, expected_hash in lock["sha256"].items():
        source = upstream / relative
        if not source.is_file():
            raise RunnerError(f"pinned upstream file is missing: {source}")
        actual_hash = _sha256_file(source)
        if actual_hash != expected_hash:
            raise RunnerError(f"pinned upstream file hash differs: {relative}")
    return lock


def _assert_task_inputs(task: Path) -> None:
    if not task.is_dir():
        raise RunnerError(f"task directory is missing: {task}")
    missing = [str(task / relative) for relative in REQUIRED_TASK_FILES if not (task / relative).is_file()]
    if missing:
        raise RunnerError("required task files are missing: " + ", ".join(missing))


def _assert_static_inputs(task: Path, upstream: Path, lock_path: Path) -> tuple[Path, ...]:
    _assert_task_inputs(task)
    _validate_upstream(upstream, lock_path)
    checks_dir = upstream / "scripts" / "checks"
    missing = [str(checks_dir / script) for _, script in STATIC_CHECKS if not (checks_dir / script).is_file()]
    if missing:
        raise RunnerError("pinned static check scripts are missing: " + ", ".join(missing))
    return tuple(checks_dir / script for _, script in STATIC_CHECKS)


def run_static(task: Path, upstream: Path, runs_dir: Path, upstream_lock: Path | None = None) -> tuple[int, Path]:
    """Run every named upstream static check and save all output separately."""
    task = task.resolve()
    upstream = upstream.resolve()
    upstream_lock = (upstream_lock or _default_upstream_lock()).resolve()
    scripts = _assert_static_inputs(task, upstream, upstream_lock)
    run_dir = runs_dir / f"static-{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%S%fZ')}"
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, Any] = {
        "kind": "static-checks",
        "started_at": _now(),
        "task": str(task),
        "task_sha256": task_hash(task),
        "static_runtime": _static_runtime(),
        "upstream": str(upstream),
        "upstream_head": _pinned_commit(upstream),
        "expected_upstream_head": UPSTREAM_COMMIT,
        "upstream_lock": str(upstream_lock),
        "upstream_lock_sha256": _sha256_file(upstream_lock),
        "checks": [],
    }
    failures = 0
    for index, ((name, script_name), script) in enumerate(zip(STATIC_CHECKS, scripts), start=1):
        started = _now()
        started_clock = time.monotonic()
        completed = subprocess.run(
            ["bash", str(script), str(task)],
            capture_output=True,
            text=True,
            check=False,
            env=_static_environment(),
        )
        finished = _now()
        stem = f"{index:02d}-{script_name.removesuffix('.sh')}"
        stdout_path = run_dir / f"{stem}.stdout.txt"
        stderr_path = run_dir / f"{stem}.stderr.txt"
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        manifest["checks"].append(
            {
                "name": name,
                "script": str(script),
                "exit_code": completed.returncode,
                "started_at": started,
                "finished_at": finished,
                "duration_seconds": round(time.monotonic() - started_clock, 6),
                "stdout": stdout_path.name,
                "stderr": stderr_path.name,
            }
        )
        failures += completed.returncode != 0
    manifest["finished_at"] = _now()
    manifest["passed"] = failures == 0
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return (0 if failures == 0 else 1), manifest_path


def _probe(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "detail": type(exc).__name__}
    # Version commands are intentionally the only captured output we display.
    detail = (completed.stdout or completed.stderr).strip().splitlines()
    return {"available": completed.returncode == 0, "exit_code": completed.returncode, "detail": detail[0] if detail else ""}


def doctor(harbor: Path, backend: str) -> tuple[int, dict[str, Any]]:
    """Read-only availability/authentication readiness checks with no secret values."""
    report: dict[str, Any] = {
        "platform": platform.platform(),
        "harbor": _probe([str(harbor), "--version"]),
        "backend": backend,
        "static_runtime": _static_runtime(),
    }
    if backend == "docker":
        report["docker"] = _probe(["docker", "version", "--format", "{{.Server.Version}}"])
        report["docker_compose"] = _probe(["docker", "compose", "version", "--short"])
        report["docker_buildx"] = _probe(["docker", "buildx", "version"])
        ready = (
            report["harbor"]["available"]
            and report["docker"]["available"]
            and report["docker_compose"]["available"]
            and report["docker_buildx"]["available"]
        )
    else:
        modal_module = subprocess.run(
            [sys.executable, "-c", "import importlib.util; raise SystemExit(not bool(importlib.util.find_spec('modal')))"],
            capture_output=True,
            text=True,
            check=False,
        )
        # Boolean presence is sufficient for a diagnostic and never exposes credentials.
        report["modal"] = {
            "package_available": modal_module.returncode == 0,
            "token_environment_configured": bool(os.environ.get("MODAL_TOKEN_ID") and os.environ.get("MODAL_TOKEN_SECRET")),
            "config_file_present": (Path.home() / ".modal.toml").is_file(),
        }
        ready = report["harbor"]["available"] and report["modal"]["package_available"] and (
            report["modal"]["token_environment_configured"] or report["modal"]["config_file_present"]
        )
    if sys.platform == "darwin":
        report["static_check_compatibility"] = (
            "Upstream scripts are executed unchanged. Some use GNU-only command options; "
            "a macOS/BSD-tool failure is captured as local evidence, not patched."
        )
    return (0 if ready else 1), report


def stage_cheat(task: Path, destination: Path, upstream: Path, upstream_lock: Path) -> None:
    """Copy a task once and append the exact pinned red-team prompt without BSD sed."""
    task = task.resolve()
    upstream = upstream.resolve()
    if destination.exists():
        raise RunnerError(f"cheat staging destination already exists: {destination}")
    _assert_task_inputs(task)
    _validate_upstream(upstream, upstream_lock.resolve())
    if not destination.parent.is_dir():
        raise RunnerError(f"cheat staging parent is missing: {destination.parent}")
    shutil.copytree(task, destination, symlinks=True)
    instruction = destination / "instruction.md"
    original = instruction.read_text(encoding="utf-8")
    # The upstream sed expression runs one physical line at a time. Keep that
    # behavior while avoiding macOS BSD sed's incompatible `-i` syntax.
    import re

    stripped = "".join(
        re.sub(r"[ \t\r\f\v]*[Dd]o not cheat[^.]*\.", "", line)
        for line in original.splitlines(keepends=True)
    )
    prompt = (upstream / "docs" / "prompts" / "hack-trial-prompt.md").read_text(encoding="utf-8")
    instruction.write_text(stripped + "\n\n" + prompt, encoding="utf-8")


def plan_commands(
    task: Path,
    backend: str,
    upstream: Path,
    harbor: Path,
    runs_dir: Path,
    subscription: bool = True,
    agent_proxy: str | None = None,
) -> list[str]:
    """Return commands only; a proxy applies to agents, not Harbor analyze 0.14."""
    task = task.resolve()
    upstream = upstream.resolve()
    runs_dir = runs_dir.resolve()
    task_q, runs_q, upstream_q, harbor_q = map(_quote, (task, runs_dir, upstream, harbor))
    runner_q = _quote(_root() / "scripts" / "tb3.py")
    run_stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%fZ")
    rubric_stage_q = _quote(runs_dir / f"rubric-stage-{run_stamp}")
    stage_q = _quote(runs_dir / f"cheat-stage-{run_stamp}")
    validation_harbor_q = _quote(_root() / ".venv-validation" / "bin" / "harbor")
    base = f"{harbor_q} run -p {task_q} --env {backend} -o {runs_q}"
    validation_base = f"{validation_harbor_q} run -p {task_q} --env {backend} -o {runs_q}"
    analysis = f"{harbor_q} analyze -m sonnet --n-concurrent 5 -r {upstream_q}/docs/prompts/trial-analysis.toml --job-prompt {upstream_q}/docs/prompts/trial-analysis-job.txt"
    codex_subscription = " --ae CODEX_FORCE_AUTH_JSON=1" if subscription else ""
    agent_proxy_flags = _agent_proxy_flags(agent_proxy)
    commands = [
        f"mkdir -p {runs_q}",
        f"{_quote(sys.executable)} {runner_q} static {task_q}",
        f"{base} --agent codex -m openai/gpt-5.6-terra{codex_subscription}{agent_proxy_flags} --ak reasoning_effort=high --n-attempts 1 --job-name tb3-terra-smoke",
    ]
    if backend == "docker":
        commands.append(f"docker build -t tb3-task-env {task_q}/environment")
    commands.extend(
        [
            f"{validation_base} --agent oracle{agent_proxy_flags} --n-attempts 1 --job-name tb3-oracle",
            f"{validation_base} --agent nop{agent_proxy_flags} --n-attempts 1 --job-name tb3-nop",
            # The current official review workflow is Harbor 0.18.0's `exec`, not
            # `harbor check`; it stages the task/rubric under these exact names.
            f"mkdir {rubric_stage_q} && mkdir {rubric_stage_q}/task-under-review",
            f"cp -R {task_q} {rubric_stage_q}/task-under-review/ && cp {upstream_q}/docs/prompts/task-implementation.toml {rubric_stage_q}/rubric.toml",
            f"{validation_harbor_q} exec -p {rubric_stage_q}/task-under-review -p {rubric_stage_q}/rubric.toml --instruction-path {upstream_q}/scripts/rubric-regression/templates/instruction.md -f /app/verdicts.json --image ubuntu:24.04 -a claude-code -m sonnet{agent_proxy_flags} --job-name tb3-rubric",
            f"{base} --agent codex -m openai/gpt-5.6-sol{codex_subscription}{agent_proxy_flags} --ak reasoning_effort=xhigh --n-attempts 3 --job-name tb3-sol",
            f"CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000 {base} --agent claude-code -m anthropic/claude-opus-5{agent_proxy_flags} --ak reasoning_effort=max --n-attempts 3 --job-name tb3-opus",
            f"{_quote(sys.executable)} {runner_q} stage-cheat {task_q} {stage_q}",
            f"{harbor_q} run -p {stage_q} --env {backend} -o {runs_q} --agent codex -m openai/gpt-5.6-sol{codex_subscription}{agent_proxy_flags} --ak reasoning_effort=xhigh --n-attempts 1 --job-name tb3-cheat-sol",
            f"CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000 {harbor_q} run -p {stage_q} --env {backend} -o {runs_q} --agent claude-code -m anthropic/claude-opus-5{agent_proxy_flags} --ak reasoning_effort=max --n-attempts 1 --job-name tb3-cheat-opus",
            f"{analysis} -o {runs_q}/tb3-sol.analysis.json {runs_q}/tb3-sol",
            f"{analysis} -o {runs_q}/tb3-opus.analysis.json {runs_q}/tb3-opus",
            f"{analysis} -o {runs_q}/tb3-cheat-sol.analysis.json {runs_q}/tb3-cheat-sol",
            f"{analysis} -o {runs_q}/tb3-cheat-opus.analysis.json {runs_q}/tb3-cheat-opus",
        ]
    )
    return commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, default=_default_upstream())
    parser.add_argument("--upstream-lock", type=Path, default=_default_upstream_lock())
    parser.add_argument("--runs-dir", type=Path, default=_root() / "runs")
    parser.add_argument("--harbor", type=Path, default=_default_harbor())
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor_parser = subparsers.add_parser("doctor", help="read-only local readiness check")
    doctor_parser.add_argument("--backend", choices=("docker", "modal"), default="modal")
    static_parser = subparsers.add_parser("static", help="run all 22 pinned upstream static checks")
    static_parser.add_argument("task", type=Path)
    stage_parser = subparsers.add_parser("stage-cheat", help="copy a task and append the pinned cheat prompt")
    stage_parser.add_argument("task", type=Path)
    stage_parser.add_argument("destination", type=Path)
    plan_parser = subparsers.add_parser("plan", help="print, but do not execute, the TB3 evaluation commands")
    plan_parser.add_argument("task", type=Path)
    plan_parser.add_argument("--backend", choices=("docker", "modal"), default="modal")
    auth_mode = plan_parser.add_mutually_exclusive_group()
    auth_mode.add_argument("--subscription", dest="subscription", action="store_true", default=True,
                           help="use the Codex subscription adapter (default)")
    auth_mode.add_argument("--api-key", dest="subscription", action="store_false",
                           help="omit subscription-only Codex authentication")
    plan_parser.add_argument(
        "--agent-proxy",
        type=_agent_proxy_url,
        help="http(s) proxy passed only as Harbor agent env; analyze has no --ae support",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "doctor":
            status, report = doctor(args.harbor, args.backend)
            print(json.dumps(report, indent=2, sort_keys=True))
            return status
        if args.command == "static":
            status, manifest = run_static(args.task, args.upstream, args.runs_dir, args.upstream_lock)
            print(manifest)
            return status
        if args.command == "stage-cheat":
            stage_cheat(args.task, args.destination, args.upstream, args.upstream_lock)
            print(args.destination)
            return 0
        for command in plan_commands(
            args.task, args.backend, args.upstream, args.harbor, args.runs_dir, args.subscription, args.agent_proxy
        ):
            print(command)
        return 0
    except RunnerError as exc:
        print(f"tb3: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
