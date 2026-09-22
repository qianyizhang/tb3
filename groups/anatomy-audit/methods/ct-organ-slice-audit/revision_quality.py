"""Compare initial/final polygons on identically indexed, explicitly revised anchors."""

import argparse
import ast
import json
import re
from pathlib import Path
import nibabel as nib
import numpy as np
from analyze import ATTEMPTS, SOL_NAMES, constants, raster, summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--analysis", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads((args.analysis / "metrics.json").read_text())
    result = {}
    for condition in ["astra-xhigh", "sol-xhigh"]:
        trial = next(
            (args.root / ".local/attempts" / ("attempt-" + ATTEMPTS[condition]) / "job").glob(
                "task__*"
            )
        )
        work = trial / "artifacts/app/work"
        initial = {}
        final = {}
        if condition == "astra-xhigh":
            for p in work.glob("draw_*.py"):
                for n in ast.walk(ast.parse(p.read_text())):
                    if (
                        isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Name)
                        and n.func.id == "save_contours"
                    ):
                        initial[ast.literal_eval(n.args[0])] = ast.literal_eval(n.args[1])
            final = {
                p.stem: {int(k): v for k, v in json.loads(p.read_text()).items()}
                for p in (work / "contours").glob("*.json")
            }
        else:
            ev = json.loads((args.analysis / (condition + "-events.json")).read_text())
            first = {}
            for e in ev:
                if e["type"] == "patch" and "segment.py" in e["text"]:
                    added = "\n".join(
                        line[1:] for line in e["text"].splitlines() if line.startswith("+")
                    )
                    if "*** Add File: /app/work/segment.py" in e["text"]:
                        first = constants(added)
                    else:
                        for m in re.finditer(r"^([A-Z_]+) = (\{.*?^\})", added, re.M | re.S):
                            first.setdefault(m[1], ast.literal_eval(m[2]))
            initial = {
                SOL_NAMES.get(k, k.lower()): v for k, v in first.items() if isinstance(v, dict)
            }
            final = {
                SOL_NAMES.get(k, k.lower()): v
                for k, v in constants((work / "segment.py").read_text()).items()
                if isinstance(v, dict)
            }
        organs = []
        allrows = []
        for organ in data["conditions"][condition]["organs"]:
            name = organ["name"]
            if name not in initial:
                continue
            before = initial[name]
            after = final[name]
            changed = [
                z
                for z in before.keys() & after.keys()
                if json.dumps(before[z]) != json.dumps(after[z])
            ]
            added = sorted(after.keys() - before.keys())
            removed = sorted(before.keys() - after.keys())
            assert sorted(changed) == organ["net_revised_anchor_slices"]
            if not (changed or added or removed):
                continue
            gt = (
                np.asarray(
                    nib.load(
                        args.root
                        / ".local/ct-organ-segmentation-astra-xhigh/task/tests/reference"
                        / f"{organ['id']:02}.nii.gz"
                    ).dataobj
                )
                > 0
            )
            rows = []
            for z in sorted(changed):
                b = raster(before[z], gt.shape[:2])
                a = raster(after[z], gt.shape[:2])
                g = gt[:, :, z]
                rows.append(
                    {
                        "organ": name,
                        "z": z,
                        "gt": int(g.sum()),
                        "raw_pred": int(b.sum()),
                        "raw_tp": int((b & g).sum()),
                        "final_pred": int(a.sum()),
                        "final_tp": int((a & g).sum()),
                    }
                )
            allrows.extend(rows)
            organs.append(
                {
                    "name": name,
                    "changed_existing": sorted(changed),
                    "added": added,
                    "removed": removed,
                    "before": summ(rows, "raw"),
                    "after": summ(rows),
                    "planes": rows,
                }
            )
        result[condition] = {
            "organs": organs,
            "changed_existing_total": len(allrows),
            "before_pooled": summ(allrows, "raw"),
            "after_pooled": summ(allrows),
        }
    (args.analysis / "revision-quality.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
