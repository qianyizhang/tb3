"""Create a fresh curation condition from an explicitly verified historical freeze."""

import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).parent
BASE = ROOT / ".local/longitudinal-ct-curation-v1"
OLD = ROOT / ".local/longitudinal-ct-context-v1/supplied"
SOURCE_DIGEST = "ffdf321ba2637b46484309d8ec2c39fdffd5234b99e3152842c245a25a149215"
EXPERIMENT = "longitudinal-ct-curation-astra-medium"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    assert not BASE.exists(), "Never overwrite an existing curation study"
    source = ROOT / ".local/freezes" / SOURCE_DIGEST / "task"
    manifest = json.loads((OLD / "task-files.json").read_text())
    for name, digest in manifest.items():
        assert sha(source / name) == digest, name
    task = BASE / "task"
    shutil.copytree(source, task)
    shutil.copyfile(METHOD / "instruction.md", task / "instruction.md")
    context = (METHOD.parent / "longitudinal-ct-context-v1/context-block.md").read_text().strip()
    assert context in (task / "instruction.md").read_text()
    shutil.copyfile(METHOD / "evaluate.py", task / "tests/evaluate.py")
    test_sh = task / "tests/test.sh"
    test_sh.write_text("#!/bin/sh\nset -eu\npython /tests/evaluate.py\n")
    oracle = {"schema_version": 1, "visits": {"baseline": [], "followup": []}}
    graph = json.loads((task / "solution/reference/events.json").read_text())
    for visit in oracle["visits"]:
        ids = sorted({i for group in graph["groups"] for i in group[visit + "_ids"]})
        oracle["visits"][visit] = [
            {"id": i, "p_tumor": 1.0, "reason": "Private mechanical oracle control."} for i in ids
        ]
    (task / "solution/reference/candidates.json").write_text(json.dumps(oracle, indent=2) + "\n")
    images = json.loads((OLD / "image-identities.json").read_text())
    config = task / "task.toml"
    config.write_text(
        config.read_text().replace(images["evaluator"], "tb3-longitudinal-curation-evaluator:v1")
    )
    images["evaluator"] = "tb3-longitudinal-curation-evaluator:v1"
    (BASE / "image-identities.json").write_text(json.dumps(images, indent=2) + "\n")
    (BASE / "review").mkdir()
    shutil.copyfile(
        ROOT / ".local/longitudinal-ct-case02/review/geometry.json", BASE / "review/geometry.json"
    )
    exp = ROOT / "groups/longitudinal-reading/experiments" / EXPERIMENT
    shutil.move(str(exp / "task"), str(BASE / "unused-scaffold"))
    config = exp / "experiment.toml"
    config.write_text(
        config.read_text().replace(
            f"groups/longitudinal-reading/experiments/{EXPERIMENT}/task",
            ".local/longitudinal-ct-curation-v1/task",
        )
    )
    (exp / "protocol.md").write_text(
        "# Comprehensive longitudinal tumor-candidate curation\n\n"
        "[Predeclared design](../../methods/longitudinal-ct-curation-v1/protocol.md).\n\n"
        "One fresh Astra-medium attempt; same case02 CTs and verified broad context.\n"
    )
    preparation = {
        "experiment_id": EXPERIMENT,
        "decision_id": "decision-4d11c9538adb4521",
        "source_task_digest": SOURCE_DIGEST,
        "source_manifest_verified": True,
        "instruction_sha256": sha(task / "instruction.md"),
        "context_block_sha256": sha(METHOD.parent / "longitudinal-ct-context-v1/context-block.md"),
        "scientific_scorer_sha256": sha(task / "tests/score.py"),
        "candidate_wrapper_sha256": sha(task / "tests/evaluate.py"),
        "input_hashes": {p: sha(task / p) for p in manifest if p.startswith("environment/data/")},
        "same_solver_image": images["solver"],
        "comparison_classification": "endpoint_only",
        "sources": [
            "https://www.nature.com/articles/s41597-026-07466-y",
            "https://fdat.uni-tuebingen.de/records/qe950-g4h94",
        ],
    }
    assert preparation["scientific_scorer_sha256"] == manifest["tests/score.py"]
    (BASE / "preparation.json").write_text(json.dumps(preparation, indent=2) + "\n")
    print(json.dumps(preparation, indent=2))


if __name__ == "__main__":
    main()
