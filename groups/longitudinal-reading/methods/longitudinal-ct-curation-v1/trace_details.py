"""Pin image requests and check explicit report exclusions against the native reference."""

import hashlib
import json
from pathlib import Path
import re

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-curation-v1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    state = json.loads((BASE / "astra-medium/operator-state.json").read_text())
    assert state["condition_status"] == "completed"
    trial = Path(state["trial_path"])
    task = ROOT / ".local/freezes" / state["task_digest"] / "task"
    trajectory_path = trial / "agent/trajectory.json"
    report_path = trial / "artifacts/app/answer/report.md"
    report = report_path.read_text()
    trajectory = json.loads(trajectory_path.read_text())
    requests = []
    for step in trajectory["steps"]:
        for call in step.get("tool_calls", []):
            source = call.get("arguments", {}).get("input", "")
            for path in re.findall(r"view_image\(\{\s*path\s*:\s*[\"']([^\"']+)[\"']", source):
                requests.append({"call_id": call["tool_call_id"], "path": path})
    requested = {r["path"] for r in requests}
    expected = [
        f"/app/work/sweep/{visit}_{i:03d}.jpg"
        for visit, depth in [("baseline", 615), ("followup", 743)]
        for i in range(0, depth, 75)
    ]
    exclusions = {
        "baseline": [(190, 190, 214), (350, 277, 452), (150, 250, 422)],
        "followup": [(173, 174, 378), (334, 247, 566), (125, 208, 528)],
    }
    # These points are copied from explicit report exclusions, not inferred from masks.
    for phrase in [
        "x=190,y=190",
        "x=350,y=277",
        "x=150,y=250",
        "x=173,y=174",
        "x=334,y=247",
        "slice 528, x=125,y=208",
    ]:
        assert phrase in report, phrase
    checks = []
    for visit, points in exclusions.items():
        image = nib.load(task / "tests/reference" / f"{visit}_instances.nii.gz")
        gt = np.asarray(image.dataobj)
        xyz = np.argwhere(gt > 0)
        for point in points:
            distances = np.linalg.norm((xyz - point) * image.header.get_zooms(), axis=1)
            nearest = int(distances.argmin())
            checks.append(
                {
                    "visit": visit,
                    "reported_exclusion_native_ijk": list(point),
                    "gt_label_at_point": int(gt[point]),
                    "nearest_gt_label": int(gt[tuple(xyz[nearest])]),
                    "nearest_gt_voxel_distance_mm": float(distances[nearest]),
                }
            )
    output = {
        "attempt_id": state["attempt_id"],
        "literal_view_image_requests": requests,
        "request_count": len(requests),
        "expected_sweep_views": expected,
        "all_sweep_views_requested": all(path in requested for path in expected),
        "bone_sagittal_views_requested": {
            v: f"/app/work/{p}_bone_sag.jpg" in requested
            for v, p in [("baseline", "b"), ("followup", "f")]
        },
        "coordinate_checks": checks,
        "sources": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [trajectory_path, report_path, trial / "artifacts/app/work/sweep.py"]
        },
        "limits": "Tool requests support image delivery, not attention or target visibility. Coordinate checks establish source-reference disagreement, not clinical adjudication. All exclusions other than the vascular hepatic point lie outside GT and must not be attributed to GT misses.",
    }
    path = BASE / "trace-details.json"
    assert not path.exists()
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(
        json.dumps(
            {
                "requests": len(requests),
                "all_sweep_views_requested": output["all_sweep_views_requested"],
                "exclusions_inside_gt": [r for r in checks if r["gt_label_at_point"]],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
