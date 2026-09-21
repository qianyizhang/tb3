"""Build, audit and pin the same-machine runtime images without model execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
DEFAULT_BASE = ROOT / ".local/ct-organ-segmentation-astra-xhigh"
RUNTIME_MANIFEST = Path(__file__).resolve().parent.parent / "source/runtime-manifest.json"


def run(command: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd or ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def image_id(tag: str) -> str:
    return run(["docker", "image", "inspect", "--format", "{{.Id}}", tag])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--source-runtime", default="tb3-dental-runtime:v1")
    args = parser.parse_args()
    base = args.base.resolve()
    task = base / "task"
    manifest = json.loads(RUNTIME_MANIFEST.read_text())

    # The retained dental runtime was independently inspected by the parent task.
    # It contains Codex plus copied scientific site-packages, not dental inputs.
    # A receiver can load the image under the portable tag declared in the
    # tracked manifest and pass that tag explicitly.
    source_runtime = args.source_runtime
    run(["docker", "image", "inspect", source_runtime])
    source_identity = image_id(source_runtime)
    expected_identity = manifest["source_runtime"]["identity"]
    if source_identity != expected_identity:
        raise RuntimeError(
            f"source runtime mismatch: expected {expected_identity}, found {source_identity}"
        )
    run(["docker", "tag", source_runtime, "tb3-ct-organ-runtime:v1"])

    runtime_audit = run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "tb3-ct-organ-runtime:v1",
            "python",
            "-c",
            (
                "import importlib.util,json;"
                "mods={n:importlib.util.find_spec(n) is None "
                "for n in ['totalsegmentator','nnunet','nnunetv2']};"
                "assert all(mods.values());"
                "import numpy,scipy,nibabel,skimage,PIL;"
                "print(json.dumps({'forbidden_modules_absent':mods,"
                "'scientific_versions':{'numpy':numpy.__version__,"
                "'scipy':scipy.__version__,'nibabel':nibabel.__version__,"
                "'skimage':skimage.__version__,'Pillow':PIL.__version__}}))"
            ),
        ]
    )

    run(
        [
            "docker",
            "build",
            "--pull=false",
            "-t",
            "tb3-ct-organ-transport:v1",
            "-f",
            "Proxy.Dockerfile",
            ".",
        ],
        cwd=base / "runtime",
    )
    run(
        [
            "docker",
            "build",
            "--pull=false",
            "-t",
            "tb3-ct-organ-solver:v1",
            ".",
        ],
        cwd=task / "environment",
    )
    run(
        [
            "docker",
            "build",
            "--pull=false",
            "-t",
            "tb3-ct-organ-evaluator:v1",
            ".",
        ],
        cwd=task / "tests",
    )

    identities = {
        "runtime": image_id("tb3-ct-organ-runtime:v1"),
        "transport": image_id("tb3-ct-organ-transport:v1"),
        "solver": image_id("tb3-ct-organ-solver:v1"),
        "evaluator": image_id("tb3-ct-organ-evaluator:v1"),
    }
    task_toml = (task / "task.toml").read_text()
    task_toml = task_toml.replace("tb3-ct-organ-solver:v1", identities["solver"])
    task_toml = task_toml.replace("tb3-ct-organ-evaluator:v1", identities["evaluator"])
    (task / "task.toml").write_text(task_toml)
    compose = (task / "environment/docker-compose.yaml").read_text()
    compose = compose.replace("tb3-ct-organ-transport:v1", identities["transport"])
    (task / "environment/docker-compose.yaml").write_text(compose)

    receipt = json.loads((base / "preparation-receipt.json").read_text())
    receipt["task_files"]["task.toml"] = sha256(task / "task.toml")
    receipt["task_files"]["environment/docker-compose.yaml"] = sha256(
        task / "environment/docker-compose.yaml"
    )
    receipt["runtime"] = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_runtime_tag": source_runtime,
        "source_runtime_identity": source_identity,
        "runtime_manifest_sha256": sha256(RUNTIME_MANIFEST),
        "identities": identities,
        "audit": json.loads(runtime_audit),
        "same_machine_preparation": True,
    }
    (base / "preparation-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (base / "image-identities.json").write_text(json.dumps(receipt["runtime"], indent=2) + "\n")
    print(json.dumps(receipt["runtime"], indent=2))


if __name__ == "__main__":
    main()
