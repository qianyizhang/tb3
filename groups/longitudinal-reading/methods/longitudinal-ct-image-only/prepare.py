"""Prepare the two authorized conditions from unchanged reviewed source members."""

import csv
import hashlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).resolve().parent
BASE = ROOT / ".local/longitudinal-ct-image-only-v1"
RUNTIME = "sha256:3de5f01c3d98a0ed47c9c6ac2ef202807e2761e0ece826d0b514c994f033f107"
TRANSPORT = "sha256:a2a21e4e45448a01dd1b97b3a5017643dea882953485c99b3fb0aceab777376f"
EXPERIMENTS = ["longitudinal-ct-image-only-astra-medium", "longitudinal-ct-image-only-sol-xhigh"]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    task = BASE / "task"
    if task.exists():
        raise SystemExit("Refusing to overwrite prepared task")
    for folder in ["environment/data", "tests/reference", "solution/reference"]:
        (task / folder).mkdir(parents=True, exist_ok=False)
    # Private author selection; no source IDs or metadata enter solver files.
    pid = "0a09c8844b"
    raw = ROOT / ".local/longitudinal-ct-review/raw"
    audit = json.loads(
        (
            ROOT / "groups/longitudinal-reading/examples/longitudinal-ct-review-20260922.json"
        ).read_text()
    )
    expected = {r["member"]: r["sha256"] for r in audit["files"]}
    source_hashes, equality = {}, {}
    for visit, short in [("baseline", "BL"), ("followup", "FU")]:
        imgpath = raw / "inputsTr" / f"{pid}_{short}_img_00.nii.gz"
        maskpath = (
            raw / ("inputsTr" if short == "BL" else "targetsTr") / f"{pid}_{short}_mask_00.nii.gz"
        )
        for p in [imgpath, maskpath]:
            key = str(p.relative_to(raw))
            source_hashes[key] = sha(p)
            assert source_hashes[key] == expected[key]
        image = nib.load(imgpath)
        values = np.asarray(image.dataobj)
        header = image.header.copy()
        for key in ["descrip", "aux_file", "intent_name", "db_name"]:
            if key in header:
                header[key] = b""
        header.extensions.clear()
        clean = nib.Nifti1Image(values, image.affine, header)
        clean.set_qform(image.get_qform(), int(image.header["qform_code"]))
        clean.set_sform(image.get_sform(), int(image.header["sform_code"]))
        output = task / "environment/data" / f"{visit}.nii.gz"
        nib.save(clean, output)
        checked = nib.load(output)
        assert np.array_equal(values, np.asarray(checked.dataobj))
        assert np.array_equal(checked.affine, image.affine)
        equality[visit] = dict(
            voxels_identical=True, affine_identical=True, shape=list(checked.shape)
        )
        for folder in ["tests", "solution"]:
            shutil.copyfile(maskpath, task / folder / "reference" / f"{visit}_instances.nii.gz")
    csvpath = raw / "inputsTr" / f"{pid}.csv"
    assert sha(csvpath) == expected[str(csvpath.relative_to(raw))]
    source_hashes[str(csvpath.relative_to(raw))] = sha(csvpath)
    rows = list(csv.DictReader(csvpath.open()))
    assert all(r["linking_unclear"] == "False" for r in rows)
    groups, merges = [], {}
    for row in rows:
        label = int(row["lesion_id"])
        event = row["topology_class"]
        if event == "MERGING":
            merges.setdefault(int(float(row["merged_into"])), []).append(label)
        else:
            event_name = {
                "UNCHANGED": "persistent",
                "DISAPPEARING": "disappearing",
                "NEWLYAPPEARING": "newly_appearing",
            }[event]
            groups.append(
                dict(
                    baseline_ids=[] if event_name == "newly_appearing" else [label],
                    followup_ids=[] if event_name == "disappearing" else [label],
                    event=event_name,
                )
            )
    groups.extend(
        dict(baseline_ids=sorted(labels), followup_ids=[destination], event="merging")
        for destination, labels in sorted(merges.items())
    )
    for folder in ["tests", "solution"]:
        (task / folder / "reference/events.json").write_text(
            json.dumps(dict(schema_version=1, groups=groups), indent=2) + "\n"
        )
        (task / folder / "reference/report.md").write_text(
            "Private exact-reference oracle control.\n"
        )
    shutil.copyfile(METHOD / "instruction.md", task / "instruction.md")
    shutil.copyfile(METHOD / "score.py", task / "tests/score.py")
    (task / "tests/test.sh").write_text("#!/bin/sh\nset -eu\npython /tests/score.py\n")
    (task / "solution/solve.sh").write_text(
        "#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/reference/* /app/answer/\n"
    )
    for p in [task / "tests/test.sh", task / "solution/solve.sh"]:
        p.chmod(0o755)
    (task / "environment/Dockerfile").write_text(
        "FROM tb3-longitudinal-runtime:validated-v1\nWORKDIR /app\nCOPY data /app/data\nRUN mkdir -p /app/answer /app/work && chmod -R a-w /app/data\n"
    )
    (task / "tests/Dockerfile").write_text(
        "FROM tb3-longitudinal-runtime:validated-v1\nCOPY . /tests\nRUN mkdir -p /app/answer /logs/verifier\n"
    )
    compose = (
        ROOT / ".local/dental-f018-contract-v3-astra-medium/task/environment/docker-compose.yaml"
    ).read_text()
    assert TRANSPORT in compose
    (task / "environment/docker-compose.yaml").write_text(compose)
    (task / "task.toml").write_text("""version = "1.0"
artifacts = ["/app/answer", "/app/work"]
[metadata]
category = "medical-imaging"
[agent]
timeout_sec = 7200.0
[verifier]
timeout_sec = 600.0
environment_mode = "separate"
[verifier.environment]
docker_image = "tb3-longitudinal-image-only-evaluator:v1"
network_mode = "no-network"
cpus = 2
memory_mb = 8192
[environment]
docker_image = "tb3-longitudinal-image-only-solver:v1"
build_timeout_sec = 600.0
cpus = 4
memory_mb = 12288
storage_mb = 16384
gpus = 0
network_mode = "public"
""")
    for experiment in EXPERIMENTS:
        exp = ROOT / "groups/longitudinal-reading/experiments" / experiment
        # Preserve untouched med-new scaffold locally, rather than leave a misleading tracked task.
        if (exp / "task").exists():
            shutil.move(str(exp / "task"), str(BASE / (experiment + "-unused-scaffold")))
        config = exp / "experiment.toml"
        config.write_text(
            config.read_text().replace(
                f"groups/longitudinal-reading/experiments/{experiment}/task",
                ".local/longitudinal-ct-image-only-v1/task",
            )
        )
    receipt = dict(
        source_patient=pid,
        source_release="Longitudinal-CT v3",
        source_hashes=source_hashes,
        input_checks=equality,
        solver_data_files=["baseline.nii.gz", "followup.nii.gz"],
        shared_task=True,
        model_runs_authorized=2,
        runtime_image=RUNTIME,
        transport_image=TRANSPORT,
    )
    (BASE / "preparation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
