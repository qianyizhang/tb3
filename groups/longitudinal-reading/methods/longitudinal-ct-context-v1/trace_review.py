"""Saved public-trace coverage and reported-coordinate checks; never executes model code."""

import hashlib
import json
import re
import shlex
from pathlib import Path

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-context-v1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    out = BASE / "supplied/trace-review.json"
    assert not out.exists(), "Retain existing trace review"
    state = json.loads((BASE / "supplied/astra-medium/operator-state.json").read_text())
    assert state["condition_status"] == "completed"
    trial = Path(state["trial_path"])
    task = ROOT / ".local/freezes" / state["task_digest"] / "task"
    calls, messages = [], []
    for line in (trial / "agent/codex.txt").read_text().splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        item = record.get("item", {})
        if record.get("type") != "item.completed":
            continue
        if item.get("type") == "agent_message":
            messages.append({"item_id": item["id"], "text": item["text"]})
        if item.get("type") != "command_execution":
            continue
        parts = shlex.split(item["command"])
        command = parts[2] if len(parts) == 3 and parts[1] == "-lc" else item["command"]
        for part in command.splitlines():
            if re.match(r"^python /app/work/(render|views|detail|ortho|overlay)\.py ", part):
                calls.append({"item_id": item["id"], "command": part, "args": shlex.split(part)})
    axial = {"baseline": set(), "followup": set()}
    orthogonal = []
    for call in calls:
        args = call["args"]
        script, visit = Path(args[1]).name, args[2]
        if script == "render.py":
            slices = range(
                int(args[3]), min(int(args[4]), 615 if visit == "baseline" else 743), int(args[5])
            )
        elif script in {"views.py", "overlay.py"}:
            slices = [int(x) for x in args[3].split(",")]
        elif script == "detail.py":
            slices = [int(args[3])]
        else:
            orthogonal.append(call)
            continue
        axial[visit].update(slices)
    report = (trial / "artifacts/app/answer/report.md").read_text()
    assert "baseline `(190,199,406)`; follow-up `(182,165,524)`" in report
    assert "benign cyst-like or vascular focus favored over tumor" in report
    points = []
    bone = {}
    for visit, locations in [
        ("baseline", [(190, 199, 406)]),
        ("followup", [(182, 165, 524), (160, 108, 283), (190, 235, 536)]),
    ]:
        im = nib.load(task / "tests/reference" / f"{visit}_instances.nii.gz")
        gt = np.asarray(im.dataobj)
        indices = np.argwhere(gt > 0)
        for point in locations:
            distances = np.linalg.norm((indices - point) * im.header.get_zooms(), axis=1)
            nearest = np.argmin(distances)
            points.append(
                {
                    "visit": visit,
                    "native_ijk": point,
                    "reference_label": int(gt[point]),
                    "nearest_label": int(gt[tuple(indices[nearest])]),
                    "nearest_distance_mm": float(distances[nearest]),
                }
            )
        zs = set(np.argwhere(gt == 7)[:, 2].tolist())
        bone[visit] = {
            "gt_id": 7,
            "native_axial_extent": sorted(zs),
            "generated_axial_intersections": sorted(zs & axial[visit]),
        }
    prompt = (task / "instruction.md").read_text()
    result = {
        "attempt_id": state["attempt_id"],
        "task_digest": state["task_digest"],
        "public_messages": messages,
        "render_commands": calls,
        "all_generated_axial_slices": {v: sorted(s) for v, s in axial.items()},
        "orthogonal_commands": orthogonal,
        "bone_reference_coverage": bone,
        "coordinate_checks": points,
        "clinical_context_delivery": {
            "melanoma_in_prompt": "melanoma" in prompt.lower(),
            "melanoma_in_public_messages": any("melanoma" in m["text"].lower() for m in messages),
            "melanoma_in_report": "melanoma" in report.lower(),
            "interpretation": "Verified availability, not proof of how context was used internally. Absence of explicit discussion does not prove it was ignored.",
        },
        "sources": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [
                trial / "agent/codex.txt",
                trial / "agent/trajectory.json",
                task / "instruction.md",
                trial / "artifacts/app/answer/report.md",
                *[
                    trial / "artifacts/app/work" / name
                    for name in [
                        "render.py",
                        "views.py",
                        "detail.py",
                        "ortho.py",
                        "overlay.py",
                        "segment.py",
                    ]
                ],
            ]
        },
        "limits": "Coverage uses all explicit retained render/view/detail/overlay command invocations, including generated views not necessarily requested. Native plane presence does not establish attention. Orthogonal crop extents are retained for manual corroboration. Reference agreement is not clinical adjudication.",
    }
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {"bone": bone, "points": points, "context": result["clinical_context_delivery"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
