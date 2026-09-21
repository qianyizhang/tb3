"""Analyze saved artifacts only; never run inference or change frozen outputs."""

from pathlib import Path
import json
import hashlib
import re
import collections
from datetime import datetime
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi


def main():
    root = Path(__file__).resolve().parents[5]
    base = root / ".local/ct-organ-segmentation-astra-medium-litemedsam"
    task = (
        root
        / ".local/freezes/669d0880fa05c172ca1b658fce844a5c86e552d91ce2fce1e06659bb9e2808cb/task"
    )
    trial = root / ".local/attempts/attempt-bc57d5f3973843bc/job/task__WhR5ASN"
    work = trial / "artifacts/app/work"
    baseline = root / ".local/attempts/attempt-6979f136149c4e17/job/task__oAtf7Dx"
    r = json.loads((base / "independent-replay.json").read_text())
    assert r == json.loads((trial / "verifier/metrics.json").read_text())
    b = json.loads((baseline / "verifier/metrics.json").read_text())

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    batches = []
    for p in sorted(work.glob("*/provenance.json")):
        j = json.loads(p.read_text())
        rows = []
        for k, entries in j["jobs"].items():
            z = np.load(p.parent / (k + ".npz"))
            assert len(z["masks"]) == len(entries)
            assert z["ids"].tolist() == [e["id"] for e in entries]
            assert np.allclose(z["boxes"], [e["box"] for e in entries])
            rows.append(len(entries))
        log = work / (p.parent.name + ".log")
        times = [
            float(m.group(3))
            for s in log.read_text().splitlines()
            if (m := re.fullmatch(r"(\d+) (\d+) ([0-9.]+)", s))
        ]
        script = work / ("batch_crop.py" if "crop" in j else "batch.py")
        assert j["script_sha256"] == sha(script)
        assert (
            j["weights_sha256"]
            == "79d8c9dca6db4d69d3f905579e5250af05e859fff9c1f543e89a513c3028ce76"
        )
        batches.append(
            {
                "name": p.parent.name,
                "images": len(rows),
                "boxes": sum(rows),
                "logged_image_loops": len(times),
                "loop_seconds": sum(times),
                "crop": j.get("crop"),
                "provenance_sha256": sha(p),
            }
        )
    # Diagnostic boundary voxel distances on unchanged original-grid masks.
    surfaces = []
    for old, new in zip(b["per_label"], r["per_label"]):
        fn = f"{new['id']:02}.nii.gz"
        gt = np.asarray(nib.load(task / "tests/reference" / fn).dataobj) > 0
        item = {
            "id": new["id"],
            "name": new["name"],
            "baseline_dice": old["dice"],
            "tool_dice": new["dice"],
            "delta_dice": new["dice"] - old["dice"],
        }
        for label, p in [("baseline", baseline), ("tool", trial)]:
            pred = np.asarray(nib.load(p / "artifacts/app/answer/masks" / fn).dataobj) > 0
            pts = np.argwhere(gt | pred)
            lo = np.maximum(pts.min(0) - 2, 0)
            hi = np.minimum(pts.max(0) + 3, gt.shape)
            sl = tuple(slice(a, z) for a, z in zip(lo, hi))
            g = gt[sl]
            m = pred[sl]
            gs = g & ~ndi.binary_erosion(g)
            ms = m & ~ndi.binary_erosion(m)
            dg = ndi.distance_transform_edt(~gs, sampling=1.5)
            dm = ndi.distance_transform_edt(~ms, sampling=1.5)
            dist = np.concatenate([dg[ms], dm[gs]])
            item[label + "_surface_dice_3mm"] = float((dist <= 3).mean())
            item[label + "_mean_boundary_distance_mm"] = float(dist.mean())
        surfaces.append(item)
    result = json.loads((trial / "result.json").read_text())
    roll = next((trial / "agent/sessions").rglob("*.jsonl"))
    events = [json.loads(s) for s in roll.read_text().splitlines()]
    outer = [
        e["payload"]
        for e in events
        if e["type"] == "response_item" and e["payload"]["type"] == "custom_tool_call"
    ]
    counts = collections.Counter(
        n for c in outer for n in re.findall(r"tools\.([A-Za-z0-9_]+)\s*\(", c.get("input", ""))
    )
    tokens = [
        e["payload"]["info"]["total_token_usage"]
        for e in events
        if e["type"] == "event_msg" and e["payload"].get("type") == "token_count"
    ][-1]
    cmds = json.loads((base / "trace-commands.json").read_text())
    # Decode concatenated transport JSON records, retaining all bytes or raising.
    s = (base / "astra-medium-litemedsam/model-transport.log").read_text()
    decoder = json.JSONDecoder()
    transport = []
    while s.strip():
        s = s.lstrip()
        x, n = decoder.raw_decode(s)
        transport.append(x)
        s = s[n:]
    report = {
        "exact_replay_all_fields": True,
        "agent_seconds": (
            datetime.fromisoformat(result["agent_execution"]["finished_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(result["agent_execution"]["started_at"].replace("Z", "+00:00"))
        ).total_seconds(),
        "total_trial_seconds": (
            datetime.fromisoformat(result["finished_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(result["started_at"].replace("Z", "+00:00"))
        ).total_seconds(),
        "token_usage": tokens,
        "outer_exec_calls": len(outer),
        "nested_tools": dict(counts),
        "shell_failures": [
            {"index": i, "exit_code": c.get("exit_code")}
            for i, c in enumerate(cmds)
            if c["status"] == "failed"
        ],
        "batches": batches,
        "canonical_adapter_calls": 2,
        "canonical_box_masks": 8,
        "batch_images": sum(x["images"] for x in batches),
        "batch_box_masks": sum(x["boxes"] for x in batches),
        "batch_image_loop_seconds": sum(x["loop_seconds"] for x in batches),
        "loop_timing_scope": "Sum of rounded logged per-image loops including preprocessing, encode/decode and save; excludes model setup/import. May overlap wall time; not pure inference latency.",
        "per_organ": surfaces,
        "surface_metric_scope": "Post-hoc diagnostic only: unweighted 6-neighbour boundary voxel centres on native 1.5mm grid; combined bidirectional nearest-boundary distances, tolerance3mm. Frozen Dice unchanged.",
        "transport_counts": dict(
            collections.Counter(
                str(x.get("target")) + " allowed=" + str(x.get("allowed")) for x in transport
            )
        ),
    }
    xx, yy = np.meshgrid(np.arange(265), np.arange(265))
    coverage = {}
    for organ in range(1, 11):
        gt = np.asarray(nib.load(task / "tests/reference" / f"{organ:02}.nii.gz").dataobj) > 0
        boxvol = np.zeros(gt.shape, bool)
        for folder in [
            "large",
            "small",
            "adrenal",
            "gb",
            "liver_tip",
            "duo_gap",
            "duo_bridge",
            "adrenal_fix",
        ]:
            j = json.loads((work / folder / "provenance.json").read_text())
            for k, entries in j["jobs"].items():
                for e in entries:
                    if e["id"] != organ:
                        continue
                    x0, y0, x1, y1 = e["box"]
                    m = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
                    boxvol[:, :, int(k)] |= m[::-1].T
        coverage[organ] = {
            "fraction_gt_within_agent_box_union": float((gt & boxvol).sum() / gt.sum()),
            "scope": "Diagnostic union of prompts from batches used for final assembly, before terminal-slice trimming; LiteMedSAM is not hard-constrained to the rectangle.",
        }
    report["prompt_coverage_diagnostic"] = coverage
    (base / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps({k: v for k, v in report.items() if k not in ["batches", "per_organ"]}, indent=2)
    )
    print("SURFACE")
    print(json.dumps(surfaces, indent=2))


if __name__ == "__main__":
    main()
