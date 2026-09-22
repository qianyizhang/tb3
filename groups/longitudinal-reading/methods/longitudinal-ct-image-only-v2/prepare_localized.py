"""Prepare one conditional localized probe from the completed v2 coverage audit."""

import hashlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).resolve().parent
BASE = ROOT / ".local/longitudinal-ct-image-only-v2"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    prior = BASE / "whole-volume"
    audit = json.loads((prior / "analysis/evidence.json").read_text())
    assert audit["localized_trigger"]["triggered"]
    group = audit["localized_trigger"]["selected_reference_group"]
    destination = BASE / "localized"
    task = destination / "task"
    if task.exists():
        raise SystemExit("Refusing to overwrite localized task")
    shutil.copytree(prior / "task", task)
    table, mapping, judgments = [], {}, []
    for visit in ["baseline", "followup"]:
        image = nib.load(task / "tests/reference" / f"{visit}_instances.nii.gz")
        values = np.asanyarray(image.dataobj)
        selected = group[visit + "_ids"]
        for label in selected:
            center = np.argwhere(values == label).mean(axis=0)
            # Ensure the supplied center lies on the selected structure, even
            # for a nonconvex reference; nearest labeled voxel to its centroid.
            points = np.argwhere(values == label)
            point = points[np.argmin(((points - center) ** 2).sum(axis=1))]
            candidate = f"R{len(mapping) + 1:02d}"
            mapping[candidate] = {
                "visit": visit,
                "reference_id": label,
                "native_ijk": point.tolist(),
            }
            table.append(
                f"| {candidate} | `/app/data/{visit}.nii.gz` | {int(point[0])}, {int(point[1])}, {int(point[2])} |"
            )
            judgments.append(
                {
                    "candidate_id": candidate,
                    "judgment": "tumor",
                    "reason": "Private reference oracle.",
                }
            )
        scoped = np.where(np.isin(values, selected), values, 0).astype(np.uint16)
        for folder in ["tests", "solution"]:
            out = task / folder / "reference" / f"{visit}_instances.nii.gz"
            nib.save(nib.Nifti1Image(scoped, image.affine, image.header.copy()), out)
    for folder in ["tests", "solution"]:
        (task / folder / "reference/events.json").write_text(
            json.dumps({"schema_version": 1, "groups": [group]}, indent=2) + "\n"
        )
    (task / "tests/reference/candidate_map.json").write_text(json.dumps(mapping, indent=2) + "\n")
    (task / "solution/reference/candidate_judgments.json").write_text(
        json.dumps({"schema_version": 1, "candidates": judgments}, indent=2) + "\n"
    )
    (task / "tests/score.py").rename(task / "tests/base_score.py")
    shutil.copyfile(METHOD / "recognition_score.py", task / "tests/score.py")
    original = (METHOD / "instruction.md").read_text()
    old_intro = "earlier and later CT examinations of the same patient. Examine both full volumes,\nsegment all visible tumor lesions, and determine their correspondence and events\nacross visits. No masks, lesion locations or annotated examples are supplied."
    replacement = (
        "earlier and later CT examinations of the same patient. Review only the structures\nat the candidate centers below, using adjacent slices and surrounding anatomy.\nThese coordinates specify what to review, not its diagnosis. No masks or\nannotated examples are supplied. Other findings are outside this task's scope.\n\n| Candidate | Input | Zero-based native voxel center (i, j, k) |\n|---|---|---|\n"
        + "\n".join(table)
    )
    assert old_intro in original
    instruction = original.replace(old_intro, replacement)
    instruction = instruction.replace(
        "segment all visible tumor lesions", "segment candidate structures judged tumor"
    )
    instruction = instruction.replace(
        "Write these files under `/app/answer/`:",
        "First record a judgment for each listed candidate: `tumor`, `normal_or_benign`,\nor `indeterminate`, with an image-based reason. Segment only candidates judged\n`tumor`; do not assign tumor masks to rejected or indeterminate candidates.\nUse the event rules below for the candidates you segmented.\n\nWrite these files under `/app/answer/`:",
    )
    insertion = """4. `candidate_judgments.json`: one entry per listed candidate, using this format.
   The following entry is a format example, not a judgment about your scans:

```json
{"schema_version": 1, "candidates": [{"candidate_id": "R00", "judgment": "indeterminate", "reason": "Explain the image evidence."}]}
```

"""
    instruction = instruction.replace(
        "Detection/localization, mask agreement, correspondence and events will be measured",
        insertion
        + "Candidate judgment, mask agreement, correspondence and events will be measured",
    )
    (task / "instruction.md").write_text(instruction)
    (destination / "instruction.md").write_text(instruction)
    shutil.copyfile(prior / "image-identities.json", destination / "image-identities.json")
    receipt = {
        "source_attempt": audit["attempt_id"],
        "source_evidence_sha256": sha(prior / "analysis/evidence.json"),
        "selected_reference_group": group,
        "private_candidate_map": mapping,
        "relaxed_information": "Exact candidate-center native coordinates; diagnosis, masks, source identity and previous result withheld.",
        "outside_scope": "Nonselected lesions are zeroed only in this new diagnostic reference; originals unchanged.",
        "requires_new_evaluator_image": True,
    }
    (destination / "preparation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
