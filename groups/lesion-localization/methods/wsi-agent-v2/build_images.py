"""Build and pin the seven local WSI solver/evaluator image pairs once."""

import json
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PREPARATION = ROOT / ".local/wsi-agent-v2/preparation.json"
RESULT = ROOT / ".local/wsi-agent-v2/runtime-images.json"


def run(*command: str) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout: {result.stdout[-3000:]}\nstderr: {result.stderr[-3000:]}"
        )
    return result.stdout.strip()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError(f"Refusing to replace pinned image receipt: {RESULT}")
    tasks = json.loads(PREPARATION.read_text())["tasks"]
    pinned = {}
    for case, relative in tasks.items():
        task = ROOT / relative
        task_toml = task / "task.toml"
        source = task_toml.read_text()
        config = tomllib.loads(source)
        kind, variant = task.parts[-3], task.parts[-2]
        stem = f"tb3-wsi-v2-{kind}-{variant}"
        pairs = (
            (
                "evaluator",
                f"{stem}-evaluator:v1",
                config["verifier"]["environment"]["docker_image"],
                task / "tests",
            ),
            (
                "solver",
                f"{stem}-solver:v1",
                config["environment"]["docker_image"],
                task / "environment",
            ),
        )
        case_images = {}
        for role, tag, current, context in pairs:
            if current == tag:
                run("docker", "build", "--quiet", "-t", tag, str(context))
            elif not current.startswith("sha256:"):
                raise ValueError(f"Unexpected task image reference: {case} {role} {current}")
            image_id = run("docker", "image", "inspect", tag, "--format", "{{.Id}}")
            if not image_id.startswith("sha256:"):
                raise ValueError(f"Unexpected image ID for {tag}: {image_id}")
            if current.startswith("sha256:") and current != image_id:
                raise ValueError(f"Pinned digest no longer matches {tag}: {current}")
            if current == tag:
                original = f'docker_image = "{tag}"'
                if source.count(original) != 1:
                    raise ValueError(f"Expected one task image reference: {original}")
                source = source.replace(original, f'docker_image = "{image_id}"')
            case_images[role] = {"tag": tag, "digest": image_id}
            print(f"{case} {role} {image_id}", flush=True)
        task_toml.write_text(source)
        pinned[case] = case_images
    RESULT.write_text(json.dumps({"schema_version": 1, "images": pinned}, indent=2) + "\n")


if __name__ == "__main__":
    main()
