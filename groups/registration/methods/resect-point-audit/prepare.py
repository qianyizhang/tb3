#!/usr/bin/env python3
"""Prepare the frozen two-query RESECT task from the pinned local sample."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).resolve().parent
SOURCE = ROOT / ".local/datasets/resect-sample/e86fb37"
DESTINATION = ROOT / ".local/resect-point-audit-v1"
SELECTIONS = (("case_a", "Case1", 1), ("case_b", "Case3", 12))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tag_points(path):
    points = []
    for line in path.read_text().splitlines():
        values = re.findall(r"[-+]?\d+(?:\.\d+)?", line.split('"', 1)[0])
        if len(values) == 6:
            points.append([float(value) for value in values])
    return points


def write(path, text, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if executable:
        path.chmod(0o755)


def main():
    task = DESTINATION / "task"
    if task.exists():
        raise SystemExit(f"refusing to overwrite existing prepared task: {task}")
    data = task / "environment/data"
    reference_cases, manifest_files = [], []
    query_cases = []
    for neutral, source_case, index in SELECTIONS:
        points = tag_points(SOURCE / source_case / f"{source_case}-MRI-beforeUS.tag")
        pair = points[index]
        query_cases.append(
            {"case_id": neutral, "mri_world_mm": pair[:3], "initial_us_world_mm": pair[:3]}
        )
        reference_cases.append(
            {"case_id": neutral, "initial_us_world_mm": pair[:3], "reference_us_world_mm": pair[3:]}
        )
        for source_name, suffix in (
            (f"{source_case}-FLAIR.nii.gz", "flair.nii.gz"),
            (f"{source_case}-US-before.nii.gz", "us.nii.gz"),
        ):
            source = SOURCE / source_case / source_name
            target = data / f"{neutral}_{suffix}"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            manifest_files.append(
                {
                    "path": str(target.relative_to(DESTINATION)),
                    "bytes": target.stat().st_size,
                    "sha256": sha256(target),
                    "source_sha256": sha256(source),
                }
            )
    queries = data / "queries.json"
    queries.write_text(json.dumps({"schema_version": 1, "cases": query_cases}, indent=2) + "\n")
    manifest_files.append(
        {
            "path": str(queries.relative_to(DESTINATION)),
            "bytes": queries.stat().st_size,
            "sha256": sha256(queries),
        }
    )
    (task / "environment").mkdir(parents=True, exist_ok=True)
    (task / "tests").mkdir(parents=True, exist_ok=True)
    (task / "solution").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(METHOD / "inspect.py", task / "environment/inspect.py")
    shutil.copyfile(METHOD / "score.py", task / "tests/score.py")
    shutil.copyfile(METHOD / "instruction.md", task / "instruction.md")
    reference = task / "tests/reference.json"
    reference.parent.mkdir(parents=True, exist_ok=True)
    reference.write_text(
        json.dumps({"schema_version": 1, "cases": reference_cases}, indent=2) + "\n"
    )
    shutil.copyfile(reference, task / "solution/reference.json")
    write(task / "tests/test.sh", "#!/bin/sh\nset -eu\npython /tests/score.py\n", True)
    write(
        task / "solution/solve.sh",
        "#!/bin/sh\nset -eu\nmkdir -p /app/answer\npython - <<'PY'\nimport json\nfrom pathlib import Path\nr=json.loads(Path('/solution/reference.json').read_text())\nout={'schema_version':1,'cases':[{'case_id':x['case_id'],'us_world_mm':x['reference_us_world_mm'],'confidence':1.0,'evidence':'oracle private paired point'} for x in r['cases']]}\nPath('/app/answer/result.json').write_text(json.dumps(out,indent=2)+'\\n')\nPath('/app/answer/report.md').write_text('Oracle exact-reference control.\\n')\nPY\n",
        True,
    )
    write(
        task / "environment/Dockerfile",
        "FROM tb3-longitudinal-runtime:validated-v1\nWORKDIR /app\nCOPY data /app/data\nCOPY inspect.py /app/tools/inspect.py\nRUN mkdir -p /app/answer /app/work && chmod -R a-w /app/data /app/tools\n",
    )
    write(
        task / "environment/docker-compose.yaml",
        "services:\n  main:\n    networks: [isolated]\n    cap_drop: [ALL]\n    security_opt: [no-new-privileges:true]\n    environment:\n      HTTP_PROXY: http://transport:3128\n      HTTPS_PROXY: http://transport:3128\n      http_proxy: http://transport:3128\n      https_proxy: http://transport:3128\n      NO_PROXY: localhost,127.0.0.1\n    depends_on: [transport]\n  transport:\n    image: tb3-ct-organ-transport:v1\n    networks: [isolated, egress]\n    read_only: true\n    cap_drop: [ALL]\n    security_opt: [no-new-privileges:true]\nnetworks:\n  isolated:\n    internal: true\n  egress: {}\n",
    )
    write(task / "tests/Dockerfile", "FROM python:3.12-slim\nWORKDIR /tests\nCOPY . /tests\n")
    write(
        task / "task.toml",
        'version = "1.0"\nartifacts = ["/app/answer", "/app/work"]\n[metadata]\ncategory = "medical-imaging"\n[agent]\ntimeout_sec = 3600.0\n[verifier]\ntimeout_sec = 120.0\nenvironment_mode = "separate"\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 4\nmemory_mb = 8192\nstorage_mb = 8192\ngpus = 0\nnetwork_mode = "public"\n',
    )
    manifest = {
        "schema_version": 1,
        "upstream_revision": "e86fb37dd93f7a9c64e48952f71410af59b04b9b",
        "selection_frozen_before_inference": True,
        "selections": [
            {"case_id": neutral, "source_case": source, "landmark_index_zero_based": index}
            for neutral, source, index in SELECTIONS
        ],
        "solver_visible_files": manifest_files,
    }
    write(DESTINATION / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"task": str(task), "manifest": str(DESTINATION / "manifest.json")}, indent=2))


if __name__ == "__main__":
    main()
