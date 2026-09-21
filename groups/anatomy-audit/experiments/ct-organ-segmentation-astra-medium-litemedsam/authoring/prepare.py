"""Prepare a fresh tool-enabled task, without building images or dispatching runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASELINE_DIGEST = "fcf7827f7100d1ca54be84f6bc14fb320d27ca546fd5352ac45cb40b04110ab6"
WEIGHTS_SHA = "79d8c9dca6db4d69d3f905579e5250af05e859fff9c1f543e89a513c3028ce76"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--runtime-source", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--solver-image", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Output must be fresh; never rewrite a frozen task")
    files = {str(p.relative_to(args.baseline)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(args.baseline.rglob("*"))
             if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if digest != BASELINE_DIGEST:
        raise ValueError("Baseline task digest differs")
    weights = args.runtime_source / "weights/lite_medsam.pth"
    if hashlib.sha256(weights.read_bytes()).hexdigest() != WEIGHTS_SHA:
        raise ValueError("Pinned checkpoint mismatch")
    shutil.copytree(args.baseline, args.output)
    context = args.output / "environment"
    shutil.copytree(args.wheelhouse, context / "wheelhouse")
    runtime = context / "litemedsam"
    vendor = runtime / "vendor/LiteMedSAM"
    vendor.mkdir(parents=True)
    source = args.runtime_source / "vendor/LiteMedSAM"
    shutil.copytree(source / "segment_anything", vendor / "segment_anything",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for filename in ("tiny_vit_sam.py", "LICENSE"):
        shutil.copyfile(source / filename, vendor / filename)
    (runtime / "weights").mkdir()
    shutil.copyfile(weights, runtime / "weights/lite_medsam.pth")
    shutil.copyfile(HERE / "requirements.txt", runtime / "requirements.txt")
    shutil.copyfile(HERE / "Dockerfile", context / "Dockerfile")
    shutil.copytree(ROOT / "src/tb3_medical/skills/litemedsam", context / "skills/litemedsam",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    instruction = args.output / "instruction.md"
    old = "External data, websites, pretrained segmentation weights, reference masks and\nscoring feedback are unavailable."
    new = (
        "LiteMedSAM is available on CPU through the skill at\n"
        "`/skills/litemedsam/SKILL.md`; its runtime is `/opt/litemedsam`. You may use it\n"
        "to create or refine masks, choosing prompts from the supplied CT yourself.\n"
        "External data, websites, other pretrained segmentation weights, reference masks\n"
        "and scoring feedback are unavailable."
    )
    text = instruction.read_text()
    if text.count(old) != 1:
        raise ValueError("Baseline instruction differs; retain partial output for review")
    instruction.write_text(text.replace(old, new))
    config = args.output / "task.toml"
    text = config.read_text()
    old_image = "sha256:e7f0c11c5c8991896e1f9058fc6f5a6943808dea5c3077e471a946d3f6cce52d"
    if text.count(old_image) != 1:
        raise ValueError("Baseline solver binding differs")
    config.write_text(text.replace(old_image, args.solver_image).replace(
        "[environment]\n", '[environment]\nskills_dir = "/skills"\n'))
    manifest = {str(p.relative_to(runtime)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(runtime.rglob("*")) if p.is_file()}
    (args.output.parent / "runtime-input-manifest.json").write_text(json.dumps({
        "upstream_commit": "b0fab476e54e631dd412b25e0db9fdf2a2b0f54c",
        "files": manifest,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
