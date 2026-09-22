"""Inspect saved public actions and geometric coverage; never execute solver scripts."""

import hashlib
import json
from pathlib import Path
import re
import shlex

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-curation-v1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def render_call(line, item):
    args = shlex.split(line)
    script, visit, plane = Path(args[1]).name, args[2], args[3]
    if visit not in {"baseline", "followup"} or plane not in {"ax", "cor", "sag"}:
        return None
    if script == "view.py":
        indices = list(range(int(args[4]), int(args[5]), int(args[6])))
        crop = (
            list(map(int, args[args.index("--crop") + 1].split(","))) if "--crop" in args else None
        )
        output = args[args.index("--out") + 1] if "--out" in args else "/app/work/view.jpg"
        # view.py reverses z for non-axial views; no cropped non-axial calls assumed.
        supported = crop is None or plane == "ax"
    else:
        indices = list(map(int, args[4].split(",")))
        crop = list(map(int, args[5].split(",")))
        output = args[-1]
        supported = True
    return {
        "item_id": item["id"],
        "script": script,
        "visit": visit,
        "plane": plane,
        "indices": indices,
        "crop": crop,
        "output": output,
        "geometry_supported": supported,
        "command": line,
    }


def main():
    state = json.loads((BASE / "astra-medium/operator-state.json").read_text())
    assert state["condition_status"] == "completed"
    trial = Path(state["trial_path"])
    task = ROOT / ".local/freezes" / state["task_digest"] / "task"
    source = trial / "agent/codex.txt"
    renders, messages, commands = [], [], []
    for line in source.read_text().splitlines():
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
        commands.append(
            {"item_id": item["id"], "command": item["command"], "exit_code": item.get("exit_code")}
        )
        if item.get("exit_code") != 0:
            continue
        parts = shlex.split(item["command"])
        shell = parts[2] if len(parts) == 3 and parts[1] == "-lc" else item["command"]
        for part in shell.splitlines():
            if re.match(r"^python /app/work/(view|detail|mpr)\.py ", part):
                parsed = render_call(part, item)
                if parsed:
                    renders.append(parsed)
    coverage = []
    for visit in ["baseline", "followup"]:
        gt_path = task / "tests/reference" / f"{visit}_instances.nii.gz"
        gt = np.asarray(nib.load(gt_path).dataobj)
        for ident in sorted(int(v) for v in np.unique(gt) if v):
            xyz = np.argwhere(gt == ident)
            hits = []
            for call in renders:
                if call["visit"] != visit or not call["geometry_supported"]:
                    continue
                axis, horizontal, vertical = {"ax": (2, 0, 1), "cor": (1, 0, 2), "sag": (0, 1, 2)}[
                    call["plane"]
                ]
                included = np.isin(xyz[:, axis], call["indices"])
                if call["crop"]:
                    a, b, c, d = call["crop"]
                    included &= (xyz[:, horizontal] >= a) & (xyz[:, horizontal] < c)
                    included &= (xyz[:, vertical] >= b) & (xyz[:, vertical] < d)
                if included.any():
                    hits.append(
                        {
                            "item_id": call["item_id"],
                            "plane": call["plane"],
                            "output": call["output"],
                            "native_indices_intersecting_gt": sorted(
                                set(xyz[included, axis].tolist())
                            ),
                            "reference_voxels_on_generated_planes": int(included.sum()),
                        }
                    )
            coverage.append(
                {
                    "visit": visit,
                    "gt_id": ident,
                    "native_k_extent": [int(xyz[:, 2].min()), int(xyz[:, 2].max())],
                    "generated_view_intersections": hits,
                }
            )
        del gt
    paths = [source, trial / "agent/trajectory.json", trial / "artifacts/app/answer/report.md"]
    paths.extend(sorted((trial / "artifacts/app/work").glob("*.py")))
    result = {
        "attempt_id": state["attempt_id"],
        "task_digest": state["task_digest"],
        "public_messages": messages,
        "commands": commands,
        "render_commands": renders,
        "per_reference_generated_coverage": coverage,
        "limits": "Geometric intersections of explicit successful view/detail/mpr calls only. Generated views are not necessarily requested; intersection does not prove attention or recognizability after windowing/downsampling. Additional rendering scripts/inline code require manual review. No clinical adjudication.",
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths if p.is_file()},
    }
    out = BASE / "trace-review.json"
    assert not out.exists()
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "render_commands": len(renders),
                "unsupported_render_geometry": [r for r in renders if not r["geometry_supported"]],
                "references_without_generated_intersection": [
                    {"visit": r["visit"], "gt_id": r["gt_id"]}
                    for r in coverage
                    if not r["generated_view_intersections"]
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
