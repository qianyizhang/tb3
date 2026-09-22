"""Prepare a new image-only pair with unchanged v2 instructions and v1 scientific scorer."""

import csv
import hashlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-case02"
TASK = BASE / "task"
RUNTIME = "sha256:3de5f01c3d98a0ed47c9c6ac2ef202807e2761e0ece826d0b514c994f033f107"
EXPERIMENT = "longitudinal-ct-case02-astra-medium"


def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    assert not TASK.exists(), "Never overwrite a task"
    acquisition = json.loads((BASE / "source/acquisition.json").read_text())
    expected = {r["member"]: r["sha256"] for r in acquisition["files"]}
    pid = acquisition["patient"]
    raw = BASE / "raw"
    for name, digest in expected.items():
        assert sha(raw / name) == digest
    geometry = json.loads((BASE / "review/geometry.json").read_text())
    assert all(v["image_mask_geometry_equal"] for v in geometry["visits"].values())
    assert json.loads((BASE / "review/acceptance.json").read_text())["accepted_for_diagnostic"]
    source = (
        ROOT
        / ".local/freezes/110a8ffd31c0991525ff33800c7a91023bb7cb24cddda518fecd3395f34d75f1/task"
    )
    manifest = json.loads(
        (ROOT / ".local/longitudinal-ct-image-only-v2/whole-volume/task-files.json").read_text()
    )
    copied = [
        "instruction.md",
        "tests/score.py",
        "tests/test.sh",
        "solution/solve.sh",
        "environment/docker-compose.yaml",
        "task.toml",
    ]
    for name in copied:
        assert sha(source / name) == manifest[name]
        target = TASK / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    input_checks = {}
    for visit, short in [("baseline", "BL"), ("followup", "FU")]:
        image = nib.load(raw / "inputsTr" / f"{pid}_{short}_img_00.nii.gz")
        data = np.asarray(image.dataobj)
        header = image.header.copy()
        for key in ["descrip", "aux_file", "intent_name", "db_name"]:
            if key in header:
                header[key] = b""
        header.extensions.clear()
        clean = nib.Nifti1Image(data, image.affine, header)
        clean.set_qform(image.get_qform(), int(image.header["qform_code"]))
        clean.set_sform(image.get_sform(), int(image.header["sform_code"]))
        output = TASK / "environment/data" / f"{visit}.nii.gz"
        output.parent.mkdir(parents=True, exist_ok=True)
        nib.save(clean, output)
        checked = nib.load(output)
        assert np.array_equal(data, np.asarray(checked.dataobj)) and np.array_equal(
            image.affine, checked.affine
        )
        input_checks[visit] = {
            "voxels_identical": True,
            "affine_identical": True,
            "shape": image.shape,
        }
        mask = (
            raw / ("inputsTr" if short == "BL" else "targetsTr") / f"{pid}_{short}_mask_00.nii.gz"
        )
        for folder in ["tests", "solution"]:
            target = TASK / folder / "reference" / f"{visit}_instances.nii.gz"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(mask, target)
    rows = list(csv.DictReader((raw / "inputsTr" / f"{pid}.csv").open()))
    assert all(
        r["linking_unclear"] == "False" and r["topology_class"] in ["UNCHANGED", "NEWLYAPPEARING"]
        for r in rows
    )
    groups = [
        {
            "baseline_ids": [int(r["lesion_id"])] if r["topology_class"] == "UNCHANGED" else [],
            "followup_ids": [int(r["lesion_id"])],
            "event": "persistent" if r["topology_class"] == "UNCHANGED" else "newly_appearing",
        }
        for r in rows
    ]
    for folder in ["tests", "solution"]:
        (TASK / folder / "reference/events.json").write_text(
            json.dumps({"schema_version": 1, "groups": groups}, indent=2) + "\n"
        )
        (TASK / folder / "reference/report.md").write_text(
            "Private exact-reference oracle control.\n"
        )
    for name in ["tests/test.sh", "solution/solve.sh"]:
        (TASK / name).chmod(0o755)
    (TASK / "environment/Dockerfile").write_text(
        "FROM tb3-longitudinal-runtime:validated-v1\nWORKDIR /app\nCOPY data /app/data\nRUN mkdir -p /app/answer /app/work && chmod -R a-w /app/data\n"
    )
    (TASK / "tests/Dockerfile").write_text(
        "FROM tb3-longitudinal-runtime:validated-v1\nCOPY . /tests\nRUN mkdir -p /app/answer /logs/verifier\n"
    )
    config = (
        (TASK / "task.toml")
        .read_text()
        .replace(
            "sha256:7b2b9c1dcf3964b6a6955c64f28000af79d0b0b70eee7922bef4419ce3d04189",
            "tb3-longitudinal-case02-evaluator:v1",
        )
        .replace(
            "sha256:cb998b7609d41429fc5d00d60439c1ff389ad2fdf3c580a834c827e6352280e9",
            "tb3-longitudinal-case02-solver:v1",
        )
    )
    (TASK / "task.toml").write_text(config)
    exp = ROOT / "groups/longitudinal-reading/experiments" / EXPERIMENT
    if (exp / "task").exists():
        shutil.move(str(exp / "task"), str(BASE / "unused-scaffold"))
    path = exp / "experiment.toml"
    path.write_text(
        path.read_text().replace(
            f"groups/longitudinal-reading/experiments/{EXPERIMENT}/task",
            ".local/longitudinal-ct-case02/task",
        )
    )
    receipt = {
        "patient": pid,
        "source_release": "Longitudinal-CT v3",
        "source_hashes": expected,
        "input_checks": input_checks,
        "prompt_sha256": sha(TASK / "instruction.md"),
        "prompt_unchanged_from_v2": True,
        "scorer_sha256": sha(TASK / "tests/score.py"),
        "scorer_unchanged_from_v1": True,
        "event_counts": {"persistent": 7, "newly_appearing": 8},
        "solver_allowlist": ["baseline.nii.gz", "followup.nii.gz"],
        "model_attempts_authorized": 1,
        "runtime": RUNTIME,
        "clinical_context": "Source annotators had clinical reports; solver CT only, deliberate retained limitation.",
    }
    (BASE / "preparation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
