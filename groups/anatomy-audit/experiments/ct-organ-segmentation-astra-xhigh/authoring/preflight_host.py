"""Exercise solver visibility and network isolation using the pinned images."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / ".local/ct-organ-segmentation-astra-xhigh"
TASK = BASE / "task"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=BASE / "runtime",
        check=check,
        text=True,
        capture_output=True,
    )


def main() -> None:
    identities = json.loads((BASE / "image-identities.json").read_text())["identities"]
    solver_tag = "tb3-ct-organ-solver:v1"
    local_solver = run(
        ["docker", "image", "inspect", "--format", "{{.Id}}", solver_tag]
    ).stdout.strip()
    if local_solver != identities["solver"]:
        raise RuntimeError(
            f"solver tag drift: expected {identities['solver']}, found {local_solver}"
        )
    dockerfile = BASE / "runtime/Preflight.Dockerfile"
    # Docker can run a local content ID directly, but BuildKit parses a bare
    # sha256 ID in FROM as a registry name. Verify the tag above, then derive
    # the preflight image from that exact local image.
    dockerfile.write_text(f"FROM {solver_tag}\nCOPY preflight.py /preflight.py\n")
    run(
        [
            "docker",
            "build",
            "--pull=false",
            "-t",
            "tb3-ct-organ-preflight:v1",
            "-f",
            dockerfile.name,
            ".",
        ]
    )
    compose = BASE / "runtime/preflight.yaml"
    compose.write_text(
        f"""services:
  main:
    image: tb3-ct-organ-preflight:v1
    networks: [isolated]
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
    environment:
      HTTP_PROXY: http://transport:3128
      HTTPS_PROXY: http://transport:3128
      http_proxy: http://transport:3128
      https_proxy: http://transport:3128
      NO_PROXY: localhost,127.0.0.1
    depends_on: [transport]
  transport:
    image: {identities["transport"]}
    networks: [isolated, egress]
    read_only: true
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
networks:
  isolated:
    internal: true
  egress: {{}}
"""
    )
    command = [
        "docker",
        "compose",
        "-p",
        "ct-organ-preflight",
        "-f",
        str(compose),
        "run",
        "--rm",
        "main",
        "python",
        "/preflight.py",
    ]
    result = run(command, check=False)
    logs = run(
        [
            "docker",
            "compose",
            "-p",
            "ct-organ-preflight",
            "-f",
            str(compose),
            "logs",
            "transport",
        ],
        check=False,
    )
    run(
        [
            "docker",
            "compose",
            "-p",
            "ct-organ-preflight",
            "-f",
            str(compose),
            "down",
            "--remove-orphans",
        ],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"preflight failed ({result.returncode})\n{result.stdout}\n{result.stderr}"
        )
    payload = json.loads(result.stdout[result.stdout.index("{") :])
    receipt = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "solver_image": identities["solver"],
        "transport_image": identities["transport"],
        "checks": payload,
        "transport_log": logs.stdout,
        "limitations": (
            "Allowlisted model-service transport is not proof of complete external "
            "isolation or absence from model pretraining."
        ),
    }
    (BASE / "isolation-preflight.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
