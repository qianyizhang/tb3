"""Pin corrected evaluator images after the first no-op control exposed a bug."""

import json
import shutil
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEST = ROOT / ".local/wsi-agent-v2"
METHOD = Path(__file__).resolve().parent
RESULT = DEST / "runtime-images-verifier-fix.json"


def run(*command: str) -> str:
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(
            f"Command failed ({process.returncode}): {' '.join(command)}\n"
            f"stdout: {process.stdout[-3000:]}\nstderr: {process.stderr[-3000:]}"
        )
    return process.stdout.strip()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError(f"Refusing to replace repair receipt: {RESULT}")
    tasks = json.loads((DEST / "preparation.json").read_text())["tasks"]
    original = json.loads((DEST / "runtime-images.json").read_text())["images"]
    corrected = {}
    for case, relative in tasks.items():
        task = ROOT / relative
        scorer = task / "tests/score.py"
        if scorer.read_bytes() != (METHOD / "score.py").read_bytes():
            shutil.copyfile(METHOD / "score.py", scorer)
        toml_path = task / "task.toml"
        source = toml_path.read_text()
        current = tomllib.loads(source)["verifier"]["environment"]["docker_image"]
        old_id = original[case]["evaluator"]["digest"]
        kind, variant = task.parts[-3], task.parts[-2]
        tag = f"tb3-wsi-v2-{kind}-{variant}-evaluator:verifier-fix-1"
        if current == old_id:
            run("docker", "build", "--quiet", "-t", tag, str(task / "tests"))
        elif not current.startswith("sha256:"):
            raise ValueError(f"Unexpected evaluator image reference: {case} {current}")
        new_id = run("docker", "image", "inspect", tag, "--format", "{{.Id}}")
        if current != old_id and current != new_id:
            raise ValueError(f"Pinned digest differs from repaired image: {case} {current}")
        if current == old_id:
            old_field = f'docker_image = "{old_id}"'
            if source.count(old_field) != 1:
                raise ValueError(f"Expected one evaluator digest in {case}")
            toml_path.write_text(source.replace(old_field, f'docker_image = "{new_id}"'))
        corrected[case] = {"old_evaluator": old_id, "new_evaluator": new_id, "tag": tag}
        print(f"{case} {new_id}", flush=True)
    RESULT.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "reason": "A missing no-op answer raised before reward.txt was written; corrected scorer records valid=false and reward=0.",
                "cases": corrected,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
