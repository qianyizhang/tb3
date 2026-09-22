"""Exercise candidate-judgment validation separately from mask/link scores."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import nibabel as nib
import numpy as np


def main():
    method = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix="ct-recognition-controls-") as tmp:
        root = Path(tmp)
        reference, answer = root / "reference", root / "answer"
        reference.mkdir()
        answer.mkdir()
        shutil.copyfile(method / "recognition_score.py", root / "score.py")
        shutil.copyfile(
            method.parent / "longitudinal-ct-image-only/score.py", root / "base_score.py"
        )
        gt = np.zeros((20, 20, 20), np.uint16)
        gt[8:12, 8:12, 8:12] = 1
        group = {
            "schema_version": 1,
            "groups": [{"baseline_ids": [1], "followup_ids": [1], "event": "persistent"}],
        }
        candidates = {
            "R01": {"visit": "baseline", "reference_id": 1},
            "R02": {"visit": "followup", "reference_id": 1},
        }
        (reference / "candidate_map.json").write_text(json.dumps(candidates))
        (reference / "events.json").write_text(json.dumps(group))
        for visit in ["baseline", "followup"]:
            nib.save(nib.Nifti1Image(gt, np.eye(4)), reference / f"{visit}_instances.nii.gz")
        (answer / "report.md").write_text("Synthetic control, not a model output.\n")
        cases = ["oracle", "reject", "indeterminate", "missing", "duplicate", "invalid_judgment"]
        checks = {}
        for case in cases:
            positive = case == "oracle"
            for visit in ["baseline", "followup"]:
                nib.save(
                    nib.Nifti1Image(gt if positive else np.zeros_like(gt), np.eye(4)),
                    answer / f"{visit}_instances.nii.gz",
                )
            (answer / "events.json").write_text(
                json.dumps(group if positive else {"schema_version": 1, "groups": []})
            )
            label = (
                "tumor"
                if positive
                else ("indeterminate" if case == "indeterminate" else "normal_or_benign")
            )
            rows = [
                {"candidate_id": k, "judgment": label, "reason": "Synthetic."} for k in candidates
            ]
            if case == "duplicate":
                rows[1]["candidate_id"] = "R01"
            if case == "invalid_judgment":
                rows[0]["judgment"] = "unknown_typo"
            path = answer / "candidate_judgments.json"
            path.write_text(json.dumps({"schema_version": 1, "candidates": rows}))
            if case == "missing":
                path.unlink()
            out = root / case
            subprocess.run(
                [
                    sys.executable,
                    str(root / "score.py"),
                    "--answer",
                    str(answer),
                    "--reference",
                    str(reference),
                    "--output",
                    str(out),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            metrics = json.loads((out / "metrics.json").read_text())
            assert metrics["valid"] == (case in ["oracle", "reject", "indeterminate"])
            if metrics["valid"]:
                assert metrics["recognition"]["accepted_as_tumor"] == (2 if positive else 0)
                assert metrics["detection_micro"]["tp"] == (2 if positive else 0)
                assert metrics["recognition"]["specificity"] is None
            checks[case] = "passed"
        print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
