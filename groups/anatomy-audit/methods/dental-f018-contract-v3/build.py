"""Build only the fresh v3 images from the verified existing offline runtime."""

import json
import subprocess as sp
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BATCH = ROOT / ".local/dental-f018-contract-v3-20260922"
EXPS = ["dental-f018-contract-v3-astra-medium", "dental-f018-reference-v3-astra-medium"]
RUNTIME = "sha256:3de5f01c3d98a0ed47c9c6ac2ef202807e2761e0ece826d0b514c994f033f107"


def main():
    assert not json.loads((BATCH / "queue.json").read_text())["no_further_dispatch"]
    assert json.loads((BATCH / "package-audit.json").read_text())["passed"]
    image = sp.check_output(
        ["docker", "image", "inspect", "tb3-dental-runtime:v1", "--format", "{{.Id}}"],
        text=True,
    ).strip()
    assert image == RUNTIME
    entries = [(f"tb3-{exp}:v3", ROOT / ".local" / exp / "task/environment") for exp in EXPS] + [
        ("tb3-dental-f018-v3-evaluator:v3", ROOT / ".local" / EXPS[0] / "task/tests")
    ]
    for i, (tag, folder) in enumerate(entries):
        with (BATCH / f"build-{i}.log").open("x") as log:
            sp.run(
                ["docker", "build", "--network=none", "--pull=false", "-t", tag, str(folder)],
                cwd=ROOT,
                stdout=log,
                stderr=sp.STDOUT,
                check=True,
                timeout=600,
            )
        print(tag, "built", flush=True)


if __name__ == "__main__":
    main()
