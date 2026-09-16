"""Admit A01 and two intact controls; validate and freeze before any trial."""
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import nibabel as nib
from score import score

ROOT = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
B = ROOT / "runs/br033-airway-routing"
G = B / "benchmark"
IDS = ["A01", "A02", "A03"]
PIP = "numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 scikit-image==0.25.2 trimesh==4.11.3"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    selected = G / "admitted-truth"
    assert not selected.exists(), "Never overwrite admission"
    selected.mkdir()
    for case in IDS:
        (selected / case).mkdir()
        shutil.copy2(G / "truth" / case / "reference.npz", selected / case / "reference.npz")
    results = {}
    for name in ["oracle", "image-baseline-v2", "mask-only-baseline"]:
        results[name] = score(G / name, selected)
    assert results["oracle"]["reward"] == 1
    assert results["image-baseline-v2"]["reward"] == 1
    assert results["mask-only-baseline"]["reward"] == 0
    for name in ["unchanged_mask", "edit_intact", "fabricated_HU", "wrong_arc", "wrong_route", "outside_edit"]:
        target = G / "controls" / name
        for case in IDS:
            shutil.copytree(G / "oracle" / case, target / case)
        if name == "unchanged_mask":
            for case in IDS:
                shutil.copy2(G / "input" / case / "proposed_mask.nii.gz", target / case / "corrected_mask.nii.gz")
        elif name in ["edit_intact", "outside_edit"]:
            case = "A02" if name == "edit_intact" else "A01"
            f = target / case / "corrected_mask.nii.gz"
            ni = nib.load(f)
            a = np.asarray(ni.dataobj).copy()
            if name == "edit_intact":
                edit = np.asarray(nib.load(G / "input" / case / "editable_region.nii.gz").dataobj) > 0
                point = np.argwhere(edit & (a == 0))[0]
            else:
                point = (0, 0, 0)
            a[tuple(point)] = 1 - a[tuple(point)]
            nib.save(nib.Nifti1Image(a, ni.affine), f)
        elif name == "wrong_route":
            f = target / "A01/centerline.npy"
            np.save(f, np.load(f)[::-1])
        else:
            f = target / "A01/cpr.npz"
            c = dict(np.load(f))
            if name == "fabricated_HU":
                c["hu"] += 10
            else:
                c["arc_mm"] *= 1.2
            np.savez_compressed(f, **c)
        results[name] = score(target, selected)
        assert results[name]["reward"] == 0, name
    validation = {"cases": IDS, "excluded": {"A04": "Input-legal repair contrast is boundary-sensitive; not admitted to a coding-agent trial"},
                  "controls": results,
                  "baseline_development": "v2 thickens to 2 mm and uses -400 HU after v1 underfilled the lumen. Author reference-assisted development; no blinded or generalization claim. v3/v4 and excluded A04 retained."}
    (G / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    task = B / "tasks/airway-route-cpr"
    assert not task.exists()
    env, tests, sol = (task / x for x in ["environment", "tests", "solution"])
    for p in [env, tests, sol]:
        p.mkdir(parents=True)
    for case in IDS:
        shutil.copytree(G / "input" / case, env / "data" / case)
        shutil.copytree(G / "oracle" / case, sol / "answer" / case)
    shutil.copy2(H / "instruction.md", task / "instruction.md")
    source = ROOT / "runs/br033-brain-routing/airway-access"
    shutil.copy2(source / "license.md", env / "DATA-LICENSE.txt")
    (env / "SOURCE_NOTICE.md").write_text("AeroPath: Stoverud et al., PLOS ONE 2024, doi:10.1371/journal.pone.0311416. Dataset https://github.com/raidionics/AeroPath ; author mirror https://huggingface.co/datasets/andreped/AeroPath at revision 6d0f831ca22bf57918aba3980ae475c94d45b997. Included data license is CC BY 4.0; mirror card separately declares MIT. Local research development fixture; publication rights need a separate review. Predictions are unmodified spatial crops of released Raidionics CT Airways ONNX v1.2.0, with predicted lung cropping, no injected errors. Public images and reference-derived curation create possible training exposure. No clinical or held-out coding-agent benchmark claim.\n")
    (env / "Dockerfile").write_text(f"FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nWORKDIR /app\nCOPY data /app/data\nCOPY SOURCE_NOTICE.md DATA-LICENSE.txt /app/\nRUN mkdir -p /app/answer\n")
    shutil.copy2(H / "score.py", tests / "score.py")
    shutil.copytree(selected, tests / "truth")
    (tests / "test.sh").write_text("#!/bin/sh\nset -eu\npython /verifier/score.py\n")
    (tests / "Dockerfile").write_text(f"FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD [\"/tests/test.sh\"]\n")
    (sol / "solve.sh").write_text("#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp -r /solution/answer/* /app/answer/\n")
    (task / "task.toml").write_text('''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/airway-route-cpr"
description = "Repair a natural airway break, preserve intact routes, and produce rotated source-mapped CPR."
authors = [{name = "Research pilot"}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["ct", "airway", "segmentation", "cpr"]
[verifier]
timeout_sec = 180.0
environment_mode = "separate"
[agent]
timeout_sec = 1800.0
[environment]
build_timeout_sec = 600.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
gpus = 0
network_mode = "public"
''')
    files = {str(p.relative_to(task)): sha(p) for p in sorted(task.rglob("*")) if p.is_file()}
    freeze = {"round": "BR-033", "pretrial": True, "model": "openai/gpt-5.6-terra", "reasoning_effort": "high",
              "agent_timeout_sec": 1800, "tasks": [{"task": "airway-route-cpr", "task_path": str(task.relative_to(ROOT)), "files": files}],
              "validation_sha256": sha(G / "validation.json"), "case_manifest_sha256": sha(G / "build.json"),
              "scope": "One real gap and two intact route controls across two patients; separate anatomy and CPR scores. No genuine absent-branch control or clinical adjudication."}
    (B / "freeze.json").write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps({"cases": IDS, "controls": {k: v["reward"] for k, v in results.items()}, "frozen_files": len(files)}, indent=2))


if __name__ == "__main__":
    main()
