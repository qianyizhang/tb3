"""Read saved CT outputs and statically parse authoring evidence; no solver execution."""

from __future__ import annotations
import argparse
import ast
import collections
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import nibabel as nib
from scipy.ndimage import distance_transform_edt
from skimage.draw import polygon

ATTEMPTS = {
    "astra-xhigh": "2668797075454e54",
    "astra-medium": "6979f136149c4e17",
    "sol-xhigh": "7b643e5d3c7e4994",
    "astra-medium-litemedsam": "bc57d5f3973843bc",
}
BATCHES = ["large", "small", "adrenal", "gb", "liver_tip", "duo_gap", "duo_bridge", "adrenal_fix"]
SOL_NAMES = {"ADRENAL_LEFT": "adrenal_gland_left", "ADRENAL_RIGHT": "adrenal_gland_right"}


def literal(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id == "range":
            return list(range(*(literal(a) for a in node.args)))
        if node.func.id == "list":
            return list(literal(node.args[0]))
    return ast.literal_eval(node)


def constants(source):
    vals = {}
    for node in ast.parse(source).body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            try:
                vals[node.targets[0].id] = literal(node.value)
            except (ValueError, TypeError):
                pass
    return vals


def events(trajectory):
    result = []
    for step in trajectory["steps"]:
        for call in step.get("tool_calls", []):
            code = call["arguments"].get("input", "")
            images = "input_image" in str(step.get("observation", {}))
            for m in re.finditer(
                r'(?:cmd|path)["\']?\s*:\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', code
            ):
                result.append(
                    {
                        "step": step["step_id"],
                        "type": "view" if m[0].startswith("path") else "command",
                        "text": ast.literal_eval(m[1]).replace("\\n", "\n"),
                        "image_observed_in_step": images,
                    }
                )
            m = re.search(r'const patch\s*=\s*("(?:[^"\\]|\\.)*")', code)
            if m:
                result.append(
                    {
                        "step": step["step_id"],
                        "type": "patch",
                        "text": ast.literal_eval(m[1]).replace("\\n", "\n"),
                    }
                )
    return result


def raster(pts, shape):
    out = np.zeros(shape, bool)
    if pts:
        for poly in pts if isinstance(pts[0][0], (list, tuple)) else [pts]:
            p = np.asarray(poly)
            rr, cc = polygon(p[:, 0], p[:, 1], shape)
            out[rr, cc] = True
    return out


def loft(parts, shape, empty=False, inclusive=False):
    out = np.zeros(shape, bool)
    for data in parts:
        prev = None
        for z, pts in sorted((int(z), pts) for z, pts in data.items()):
            m = raster(pts, shape[:2])
            d = (
                distance_transform_edt(m) - distance_transform_edt(~m)
                if m.any() or not empty
                else np.full(m.shape, -3.0)
            )
            if prev is not None:
                a, da = prev
                for k in range(a, z + 1):
                    t = (k - a) / (z - a)
                    field = da * (1 - t) + d * t if empty else da * (z - k) + d * (k - a)
                    out[:, :, k] |= field >= 0 if inclusive else field > 0
            prev = (z, d)
    return out


def summ(rows, field="final"):
    if not rows:
        return {"n": 0, "dice": None, "mean_slice_dice": None, "gt_voxels": 0, "pred_voxels": 0}
    g = sum(r["gt"] for r in rows)
    p = sum(r[field + "_pred"] for r in rows)
    tp = sum(r[field + "_tp"] for r in rows)
    scores = [
        2 * r[field + "_tp"] / (r["gt"] + r[field + "_pred"])
        for r in rows
        if r["gt"] + r[field + "_pred"]
    ]
    return {
        "n": len(rows),
        "dice": 2 * tp / (g + p) if g + p else None,
        "mean_slice_dice": float(np.mean(scores)) if scores else None,
        "gt_voxels": g,
        "pred_voxels": p,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    root = a.root.resolve()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    hashes = {}

    def read(p):
        p = Path(p)
        b = p.read_bytes()
        hashes[str(p.relative_to(root))] = hashlib.sha256(b).hexdigest()
        return b

    def js(p):
        return json.loads(read(p))

    task = root / ".local/ct-organ-segmentation-astra-xhigh/task"
    labels = js(task / "tests/labels.json")["labels"]
    shape = (265, 265, 401)
    results = {}
    allrows = []
    for condition, aid in ATTEMPTS.items():
        trial = next((root / ".local/attempts" / ("attempt-" + aid) / "job").glob("task__*"))
        work = trial / "artifacts/app/work"
        ev = events(js(trial / "agent/trajectory.json"))
        (out / (condition + "-events.json")).write_text(json.dumps(ev, indent=2) + "\n")
        parts = {item["name"]: [] for item in labels}
        anchors = collections.defaultdict(set)
        spans = collections.defaultdict(set)
        empty_anchors = collections.defaultdict(set)
        revised = collections.defaultdict(set)
        batches = {}
        sam = condition.endswith("litemedsam")
        if condition == "astra-xhigh":
            for item in labels:
                parts[item["name"]] = [js(work / "contours" / (item["name"] + ".json"))]
            # Initial authored polygons versus final saved data: net revision, not every visit.
            initial = {}
            for p in work.glob("draw_*.py"):
                for n in ast.walk(ast.parse(read(p).decode())):
                    if (
                        isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Name)
                        and n.func.id == "save_contours"
                    ):
                        initial[literal(n.args[0])] = literal(n.args[1])
            for name, data in initial.items():
                final = {int(k): v for k, v in parts[name][0].items()}
                for z in data.keys() & final.keys():
                    if json.dumps(data.get(z)) != json.dumps(final.get(z)):
                        revised[name].add(z)
        elif condition == "astra-medium":
            data = js(work / "contours.json")
            for n, d in data.items():
                main = {
                    "liver_left_inferior": "liver",
                    "spleen_tip": "spleen",
                    "duodenum_ascending": "duodenum",
                }.get(n, n)
                parts[main].append(d)
            # Trace contains no contour rewrite after initial per-organ authoring; later changes affect build.py.
        elif condition == "sol-xhigh":
            data = constants(read(work / "segment.py").decode())
            initial = {}
            for e in ev:
                if e["type"] == "patch" and "*** Add File: /app/work/segment.py" in e["text"]:
                    src = "\n".join(
                        line[1:] for line in e["text"].splitlines() if line.startswith("+")
                    )
                    initial = constants(src)
                elif e["type"] == "patch" and "*** Update File: /app/work/segment.py" in e["text"]:
                    added = "\n".join(
                        line[1:] for line in e["text"].splitlines() if line.startswith("+")
                    )
                    for match in re.finditer(r"^([A-Z_]+) = (\{.*?^\})", added, re.M | re.S):
                        initial.setdefault(match[1], ast.literal_eval(match[2]))
            for key, d in data.items():
                name = SOL_NAMES.get(key, key.lower())
                if name in parts and isinstance(d, dict):
                    parts[name] = [d]
                    first = initial.get(key, {})
                    assert first, key
                    for z in first.keys() & d.keys():
                        if first.get(z) != d.get(z):
                            revised[name].add(z)
        else:
            for f in ["anchors.json", "small_anchors.json", "adrenal_anchors.json"]:
                for ident, data in js(work / f).items():
                    idx = 10 if ident.startswith("10") else int(ident)
                    name = labels[idx - 1]["name"]
                    anchors[name] |= set(map(int, data))
            for e in ev:
                if e["type"] == "command" and "pts={" in e["text"] and "_jobs.json" in e["text"]:
                    line = next(item for item in e["text"].splitlines() if item.startswith("pts="))
                    tree = ast.parse(line)
                    pts = literal(tree.body[0].value)
                    ident = int(re.search(r"'id':(\d+)", line)[1])
                    anchors[labels[ident - 1]["name"]] |= set(pts)
            for p in sorted(work.glob("*/provenance.json")):
                batches[p.parent.name] = js(p)["jobs"]
        for name, group in parts.items():
            for data in group:
                anchors[name] |= {int(z) for z, p in data.items() if p}
                empty_anchors[name] |= {int(z) for z, p in data.items() if not p}
                zs = sorted(map(int, data))
                spans[name] |= set(range(zs[0], zs[-1] + 1))
        ops = []
        if sam:
            for folder, jobs in batches.items():
                for z, boxes in jobs.items():
                    for box in boxes:
                        ops.append(
                            {
                                "batch": folder,
                                "z": int(z),
                                "id": box["id"],
                                "selected": folder in BATCHES,
                            }
                        )
        organs = []
        for item in labels:
            name = item["name"]
            idx = item["id"]
            gtpath = task / "tests/reference" / item["file"]
            pp = trial / "artifacts/app/answer/masks" / item["file"]
            read(gtpath)
            read(pp)
            gt = np.asarray(nib.load(gtpath).dataobj) > 0
            pred = np.asarray(nib.load(pp).dataobj) > 0
            raw = None
            if sam:
                raw = np.zeros(shape, bool)
                for folder in BATCHES:
                    jobs = batches[folder]
                    for z, boxes in jobs.items():
                        if not any(b["id"] == idx for b in boxes):
                            continue
                        path = work / folder / (z + ".npz")
                        read(path)
                        with np.load(path) as f:
                            for m, id in zip(f["masks"], f["ids"], strict=True):
                                if id == idx:
                                    raw[:, :, int(z)] |= m[::-1].T
                        spans[name].add(int(z))
            elif parts[name]:
                raw = loft(parts[name], shape, condition == "astra-xhigh", condition == "sol-xhigh")
            else:
                raw = (
                    pred.copy()
                )  # Sol parametric duodenum: final raw geometry is the ellipsoid union.
            g = gt.sum((0, 1))
            p = pred.sum((0, 1))
            tp = (gt & pred).sum((0, 1))
            r = raw.sum((0, 1))
            rt = (gt & raw).sum((0, 1))
            changed = (raw != pred).sum((0, 1))
            active = set(np.where(g + p > 0)[0])
            roi = set(np.where(g > 0)[0])
            maxarea = g.max()
            rows = []
            for z in sorted(active):
                category = (
                    ("explicit_box" if sam else "authored_polygon")
                    if z in anchors[name]
                    else ("interpolated_box" if sam else "interpolated_shape")
                    if z in spans[name]
                    else "outside_authored_extent"
                )
                if z in empty_anchors[name]:
                    category = "explicit_empty_anchor"
                if condition == "sol-xhigh" and name == "duodenum":
                    category = "parametric_ellipsoids"
                rr = {
                    "condition": condition,
                    "id": idx,
                    "organ": name,
                    "z": int(z),
                    "category": category,
                    "gt": int(g[z]),
                    "final_pred": int(p[z]),
                    "final_tp": int(tp[z]),
                    "raw_pred": int(r[z]),
                    "raw_tp": int(rt[z]),
                    "postprocess_changed": int(changed[z]),
                    "central_gt": bool(g[z] >= 0.25 * maxarea),
                    "gt_present": bool(g[z]),
                    "anchor_distance_mm": float(min(abs(z - k) for k in anchors[name]) * 1.5)
                    if anchors[name]
                    else None,
                    "net_revised_anchor": z in revised[name],
                    "tool_batch_count": len(
                        {op["batch"] for op in ops if op["id"] == idx and op["z"] == z}
                    ),
                    "tool_final_batch_count": len(
                        {
                            op["batch"]
                            for op in ops
                            if op["id"] == idx and op["z"] == z and op["selected"]
                        }
                    ),
                }
                rows.append(rr)
            org = {
                "id": idx,
                "name": name,
                "anchors": sorted(anchors[name]),
                "empty_anchors": sorted(empty_anchors[name]),
                "empty_anchor_active": len(empty_anchors[name] & active),
                "construction_slices": sorted(spans[name]),
                "net_revised_anchor_slices": sorted(revised[name]),
                "gt_slices": len(roi),
                "active_slices": len(active),
                "anchor_active": len(anchors[name] & active),
                "gt_outside_construction": len(roi - spans[name]) if parts[name] or sam else None,
                "final": summ(rows),
                "raw": {
                    "dice": float(2 * rt.sum() / (g.sum() + r.sum())),
                    "gt_voxels": int(g.sum()),
                    "pred_voxels": int(r.sum()),
                },
                "categories": {
                    c: {
                        "final": summ([r for r in rows if r["category"] == c]),
                        "raw": summ([r for r in rows if r["category"] == c], "raw"),
                    }
                    for c in sorted({r["category"] for r in rows})
                },
                "postprocess_changed_voxels": int(changed.sum()),
                "raw_voxels": int(raw.sum()),
                "final_voxels": int(pred.sum()),
            }
            organs.append(org)
            allrows.extend(rows)
            metrics = js(trial / "verifier/metrics.json")
            original = next(x["dice"] for x in metrics["per_label"] if x["id"] == idx)
            assert abs(original - org["final"]["dice"]) < 1e-12
        cr = [r for r in allrows if r["condition"] == condition]
        cats = {}
        for category in sorted({r["category"] for r in cr}):
            sub = [r for r in cr if r["category"] == category]
            orgscores = [summ([r for r in sub if r["id"] == i])["dice"] for i in range(1, 11)]
            cats[category] = {
                "pooled": summ(sub),
                "macro_organ_dice": float(np.mean([v for v in orgscores if v is not None])),
                "raw": summ(sub, "raw"),
                "central_gt": summ([r for r in sub if r["central_gt"]]),
            }
        results[condition] = {
            "organs": organs,
            "categories": cats,
            "active_organ_slices": len(cr),
            "whole_macro_dice": float(np.mean([o["final"]["dice"] for o in organs])),
            "raw_macro_dice": float(np.mean([o["raw"]["dice"] for o in organs])),
            "tool_batch_masks": len(ops),
            "tool_unique_pairs": len({(o["id"], o["z"]) for o in ops}),
            "tool_repeat_batch_pairs": sum(
                len({o["batch"] for o in ops if o["id"] == i and o["z"] == z}) > 1
                for i, z in {(o["id"], o["z"]) for o in ops}
            ),
            "tool_final_masks": sum(o["selected"] for o in ops),
            "tool_final_unique_pairs": len({(o["id"], o["z"]) for o in ops if o["selected"]}),
            "tool_final_repeat_pairs": sum(
                len({o["batch"] for o in ops if o["id"] == i and o["z"] == z and o["selected"]}) > 1
                for i, z in {(o["id"], o["z"]) for o in ops if o["selected"]}
            ),
        }
    # Matched planes remove condition-dependent slice selection from the tool comparison.
    medium = {(r["id"], r["z"]): r for r in allrows if r["condition"] == "astra-medium"}
    samrows = {(r["id"], r["z"]): r for r in allrows if r["condition"] == "astra-medium-litemedsam"}
    paired = {}
    for category in ["authored_polygon", "interpolated_shape", "outside_authored_extent"]:
        keys = [k for k, r in medium.items() if r["category"] == category and r["gt_present"]]
        m = [medium[k] for k in keys]
        s = [samrows[k] for k in keys]
        paired[category] = {"baseline": summ(m), "tool_same_planes": summ(s)}
    # Endpoint / gap controls: descriptive, no attempt at causal adjustment.
    distances = {}
    for c in ATTEMPTS:
        rows = [
            r
            for r in allrows
            if r["condition"] == c
            and r["gt_present"]
            and r["anchor_distance_mm"] is not None
            and r["category"] != "outside_authored_extent"
        ]
        distances[c] = {}
        for lo, hi in [(0, 0), (1.5, 3), (4.5, 1000)]:
            s = [r for r in rows if lo <= r["anchor_distance_mm"] <= hi]
            distances[c][f"{lo}-{hi}mm"] = {
                "all": summ(s),
                "central_gt": summ([r for r in s if r["central_gt"]]),
            }
    previous = js(
        root / "groups/anatomy-audit/findings/evidence/ct-organ-methodology-astra-xhigh.json"
    )
    for new, old in zip(results["astra-xhigh"]["organs"], previous["per_organ"], strict=True):
        assert new["name"] == old["name"]
        assert abs(new["raw"]["dice"] - old["raw_dice"]) < 1e-12
    result = {
        "schema_version": 1,
        "scope": "posthoc one-case organ-slice diagnostic; original metrics unchanged",
        "conditions": results,
        "same_baseline_strata": paired,
        "anchor_distance": distances,
        "input_hashes": hashes,
    }
    (out / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    (out / "slices.json").write_text(json.dumps(allrows, indent=2) + "\n")
    for name, h in hashes.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == h, name
    print(
        json.dumps(
            {
                c: {
                    "active": x["active_organ_slices"],
                    "macro": x["whole_macro_dice"],
                    "raw_macro": x["raw_macro_dice"],
                    "categories": x["categories"],
                    "tool_pairs": x["tool_unique_pairs"],
                    "tool_repeat": x["tool_repeat_batch_pairs"],
                }
                for c, x in results.items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
