"""Bind the reviewed single-dispatch runner to this one new tool condition.

Import is passive. No completed experiment file or runtime state is modified.
All mutable runner destinations are rebound before check-only or execution.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / ".local/ct-organ-segmentation-astra-medium-litemedsam"
NAME = "ct-organ-segmentation-astra-medium-litemedsam"
SLUG = "astra-medium-litemedsam"
HELPER = ROOT / "groups/anatomy-audit/methods/ct-organ-three-condition-comparison/run_comparison.py"


def bound_runner():
    plan = json.loads((BASE / "operation-plan.json").read_text())
    if hashlib.sha256(HELPER.read_bytes()).hexdigest() != plan["runner_helper_sha256"]:
        raise RuntimeError("Reviewed runner helper changed")
    controls = json.loads((BASE / "controls-review.json").read_text())
    if controls.get("task_digest") != plan["task_digest"] or controls.get("passed") is not True:
        raise RuntimeError("Exact-task controls not approved")
    for item in controls["evidence_files"]:
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise RuntimeError(f"Control or preflight evidence changed: {path}")
    spec = importlib.util.spec_from_file_location("ct_litemedsam_runner_helper", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import reviewed runner")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.ROOT = ROOT
    runner.RUNNER_PATH = Path(__file__).resolve()
    runner.BASE = BASE
    runner.EXPECTED_DIGEST = plan["task_digest"]
    runner.IMAGE_RECORD = BASE / "image-identities.json"
    runner.CLEARANCE = BASE / "parent-launch-clearance.json"
    runner.CONDITIONS = ({
        "slug": SLUG, "experiment": NAME, "model": "openai/gpt-6-astra", "effort": "medium"
    },)

    def image_ids():
        identities = json.loads(runner.IMAGE_RECORD.read_text())["identities"]
        for key, tag in (
            ("solver", "tb3-ct-organ-litemedsam-solver:v1"),
            ("transport", "tb3-ct-organ-transport:v1"),
            ("evaluator", "tb3-ct-organ-evaluator:v1"),
        ):
            actual = runner.run(["docker", "image", "inspect", "--format", "{{.Id}}", tag]).stdout.strip()
            if actual != identities[key]:
                raise RuntimeError(f"{key} image drift")
        return identities

    runner.docker_ids = image_ids
    return runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    runner = bound_runner()
    if args.check_only:
        runner.check_only()
    else:
        runner.main()


if __name__ == "__main__":
    main()
