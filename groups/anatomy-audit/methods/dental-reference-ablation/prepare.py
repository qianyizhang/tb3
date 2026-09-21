"""Prepare the authorized two-arm study into fresh local task directories."""

import argparse
import hashlib
import json
import shutil
import tomllib
from pathlib import Path

import nibabel as nib
import numpy as np

EXPERIMENTS = ["dental-f002-contract-v2-astra-medium", "dental-f002-reference-v2-astra-medium"]
RUNTIME = "tb3-dental-runtime:v1"  # Verify pinned identity in protocol before building.


def sha(path):
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def main():
    ap = argparse.ArgumentParser(__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--reference", required=True)
    args = ap.parse_args()
    root = args.repo.resolve()
    method = Path(__file__).resolve().parent
    batch = root / ".local/dental-reference-ablation-20260921"
    old = root / ".local/dental-f002-astra-medium/task"
    common = (method / "instruction.md").read_text()
    receipt = {
        "target": "F_002",
        "reference": args.reference,
        "common_instruction_sha256": sha(method / "instruction.md"),
        "experiments": {},
    }
    for index, exp in enumerate(EXPERIMENTS):
        base = root / ".local" / exp
        task = base / "task"
        if task.exists():
            raise SystemExit(f"Refusing existing destination: {task}")
        for folder in ["environment/data", "tests", "solution"]:
            (task / folder).mkdir(parents=True, exist_ok=False)
        for name in ["ct.nii.gz", "labels.json"]:
            shutil.copyfile(old / "environment/data" / name, task / "environment/data" / name)
        for folder in ["tests", "solution"]:
            shutil.copyfile(old / "tests/reference.nii.gz", task / folder / "reference.nii.gz")
        for name in ["labels.json", "test.sh"]:
            shutil.copyfile(old / "tests" / name, task / "tests" / name)
        shutil.copyfile(old / "solution/solve.sh", task / "solution/solve.sh")
        shutil.copyfile(method / "score.py", task / "tests/score.py")
        shutil.copyfile(
            old / "environment/docker-compose.yaml", task / "environment/docker-compose.yaml"
        )
        dockerfile = f"FROM {RUNTIME}\nWORKDIR /app\nCOPY data /app/data\n"
        appendix = "\n## Available example data\n\nNo annotated example case is supplied in this condition.\n"
        if index:
            example = task / "environment/reference"
            example.mkdir()
            for suffix, dest in [("_0000", "ct.nii.gz"), ("", "segmentation.nii.gz")]:
                src = batch / "source" / f"ToothFairy3{args.reference}{suffix}.nii.gz"
                image = nib.load(src)
                data = np.asanyarray(image.dataobj)
                header = image.header.copy()
                for field in ["descrip", "aux_file", "intent_name"]:
                    header[field] = b""
                header.extensions.clear()
                new = nib.Nifti1Image(data, image.affine, header)
                new.set_qform(image.get_qform(), int(image.header["qform_code"]))
                new.set_sform(image.get_sform(), int(image.header["sform_code"]))
                nib.save(new, example / dest)
                check = nib.load(example / dest)
                assert np.array_equal(np.asanyarray(check.dataobj), data)
                assert np.array_equal(check.affine, image.affine)
            appendix = """\n## Available example data

One separate annotated example is available at `/app/reference/ct.nii.gz` and
`/app/reference/segmentation.nii.gz`, using the same label dictionary and native
axis contract. You may inspect this pair to understand the annotation convention
and use it however you judge useful. It is a different case, not a target mask;
do not assume its anatomy, label inventory or coordinates describe the target.
Only the target segmentation is requested. There are no other example cases.
"""
            dockerfile += "COPY reference /app/reference\n"
        dockerfile += "RUN mkdir -p /app/answer /app/work && chmod -R a-w /app/data"
        if index:
            dockerfile += " /app/reference"
        (task / "environment/Dockerfile").write_text(dockerfile + "\n")
        (task / "tests/Dockerfile").write_text(
            f"FROM {RUNTIME}\nCOPY . /tests\nRUN mkdir -p /app/answer /logs/verifier\n"
        )
        (task / "instruction.md").write_text(common + appendix)
        # Tags are replaced by actual image digests after offline builds, before controls/freeze.
        text = (old / "task.toml").read_text()
        old_config = tomllib.loads(text)
        text = text.replace(old_config["environment"]["docker_image"], f"tb3-{exp}:v2")
        text = text.replace(
            old_config["verifier"]["environment"]["docker_image"], "tb3-dental-f002-v2-evaluator:v2"
        )
        (task / "task.toml").write_text(text)
        for script in ["tests/test.sh", "solution/solve.sh"]:
            (task / script).chmod(0o755)
        expdir = root / "groups/anatomy-audit/experiments" / exp
        cfg = expdir / "experiment.toml"
        cfg.write_text(
            cfg.read_text().replace(
                f"groups/anatomy-audit/experiments/{exp}/task", f".local/{exp}/task"
            )
        )
        receipt["experiments"][exp] = {
            "files": {str(p.relative_to(task)): sha(p) for p in task.rglob("*") if p.is_file()},
            "reference_supplied": bool(index),
        }
    receipt["target_inputs_identical"] = all(
        sha(root / ".local" / EXPERIMENTS[0] / "task/environment/data" / f)
        == sha(root / ".local" / EXPERIMENTS[1] / "task/environment/data" / f)
        for f in ["ct.nii.gz", "labels.json"]
    )
    assert receipt["target_inputs_identical"]
    (batch / "preparation-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "experiments": EXPERIMENTS,
                "target_inputs_identical": True,
                "reference": args.reference,
            }
        )
    )


if __name__ == "__main__":
    main()
