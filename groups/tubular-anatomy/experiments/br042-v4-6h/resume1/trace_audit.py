"""Post-hoc trace/output diagnostics; never execute saved solver/authoring code.

Run with .venv-br030/bin/python. Writes only a new audit receipt/local diagnostics.
Reference-assisted measurements below are not a new model attempt or adjudication.
"""
from __future__ import annotations

import collections
import copy
import hashlib
import json
from pathlib import Path
import types

import nibabel as nib
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TASK = ROOT / "runs/br042-all-vessels-v4-6h/tasks/all-vessels"
TRIAL = ROOT / "runs/br042-all-vessels-astra-xhigh-v4-6h-resume1/all-vessels__cr5kdch"
OLD = ROOT / "runs/br042-all-vessels-v4-6h-resume1/restore/answer"
ANSWER = TRIAL / "artifacts/app/answer"
WORK = TRIAL / "artifacts/app/work"
LOCAL = ROOT / "runs/br042-resume-trace-audit-20260921"
RESUME = "2026-09-20T15:47:48.895498Z"
NAMES = {1: "LM", 2: "LAD", 3: "LCx", 4: "D1", 5: "D2", 6: "OM1",
         7: "OM2", 9: "RCA", 10: "R-PDA", 11: "R-PLA", 14: "Other"}


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    LOCAL.mkdir(exist_ok=True)
    source = next((TRIAL / "agent/sessions").rglob("*.jsonl"))
    calls, messages, usage, counts, compactions = [], [], [], [], []
    for line, raw in enumerate(source.open(), 1):
        item = json.loads(raw)
        typ, p, stamp = item["type"], item.get("payload", {}), item["timestamp"]
        base = {"line": line, "timestamp": stamp, "phase": "resume" if stamp >= RESUME else "initial"}
        if typ == "response_item" and p.get("type") == "custom_tool_call":
            calls.append({**base, "call_id": p["call_id"], "input": p["input"]})
        if typ == "response_item" and p.get("type") == "message" and p.get("role") == "assistant":
            messages.append({**base, "text": "\n".join(c.get("text", "") for c in p.get("content", []))})
        if typ == "token_usage_record":
            usage.append({**base, "response_id": p.get("response_id"), "usage": p["usage"]})
        if typ == "event_msg" and p.get("type") == "token_count":
            counts.append({**base, "usage": p["info"]["total_token_usage"]})
        if typ == "compacted":
            compactions.append(base)
    # Observable actions and public messages only; no private reasoning copied.
    (LOCAL / "observable-trace.json").write_text(json.dumps({"calls": calls, "messages": messages}, indent=2) + "\n")
    token_rows = {}
    for phase in ["initial", "resume"]:
        selected = [r for r in usage if r["phase"] == phase]
        assert len({r["response_id"] for r in selected}) == len(selected)
        total = collections.Counter()
        for row in selected:
            total.update(row["usage"])
        token_rows[phase] = {"records": len(selected), "record_sum": dict(total),
                             "custom_exec_calls": sum(r["phase"] == phase for r in calls)}
    previous = [r for r in counts if r["phase"] == "initial"][-1]["usage"]
    terminal = counts[-1]["usage"]
    token_rows["terminal_cumulative"] = terminal
    token_rows["terminal_delta_resume"] = {k: terminal[k] - previous[k] for k in terminal}

    frozen = read(ROOT / "runs/br042-all-vessels-v4-6h/freeze.json")["tasks"][0]["files"]
    assert {str(p.relative_to(TASK)): sha(p) for p in TASK.rglob("*") if p.is_file()} == frozen
    scorer = types.ModuleType("frozen_score")
    exec(compile((TASK / "tests/score.py").read_text(), str(TASK / "tests/score.py"), "exec"), scorer.__dict__)
    ref, old, new = read(TASK / "tests/reference.json"), read(OLD / "centerlines.json"), read(ANSWER / "centerlines.json")
    metrics = scorer.evaluate(new, ref)
    assert metrics == read(TRIAL / "verifier/metrics.json")
    old_metrics = scorer.evaluate(old, ref)
    unchanged = all(metrics[k] == old_metrics[k] for k in ["geometry", "labeled", "per_reference_category"])
    old_specs, new_specs = [{c["id"]: c for c in read(p / "vessels.json")} for p in [OLD, ANSWER]]
    old_by, new_by = [{c["id"]: c for c in obj["centerlines"]} for obj in [old, new]]
    coronary = [c["id"] for c in new["centerlines"][:16]]
    previous_coronary = [k for k in coronary if k in old_by]
    changes = {
        "old_courses": len(old_by), "new_courses": len(new_by),
        "byte_equivalent_course_objects": [k for k in old_by if k in new_by and old_by[k] == new_by[k]],
        "previous_coronary_ids": previous_coronary,
        "unchanged_coronary_specs": [k for k in previous_coronary if old_specs[k] == new_specs[k]],
        "changed_coronary_course_objects": [k for k in previous_coronary if old_by[k] != new_by[k]],
        "old_rca_points": len(old_by["rca"]["points_ras_mm"]),
        "new_rca_points": len(new_by["rca"]["points_ras_mm"]),
        "renamed_id": {"from": "right_upper_pa_posterior", "to": "right_upper_pa_apical"},
        "net_added_courses": 4,
        "added_anatomical_courses": ["right_upper_pa_posterior", "right_upper_pa_posterior_dorsal",
                                     "right_lower_superior_segmental_pa", "rca_superior_atrial"],
    }
    r, rl, rw, ro = scorer.samples(ref)
    p, pl, pw, po = scorer.samples(new, True)
    d, nearest = scorer.nearest(r, p)
    owners = po[nearest]
    im = nib.load(TASK / "environment/data/image.nii.gz")
    inv = np.linalg.inv(im.affine)
    voxel = np.einsum("ij,nj->ni", inv[:3, :3], r) + inv[:3, 3]
    assert np.isfinite(voxel).all()
    spacing = nib.affines.voxel_sizes(im.affine)
    image = np.load(WORK / "image.npy", mmap_mode="r")
    assert np.array_equal(np.asanyarray(im.dataobj), image), "Saved HU cache differs from native CTA"
    features = np.load(WORK / "vesselness.npz")
    origin, vesselness = features["origin"], features["v"]
    fv = map_coordinates(vesselness, (voxel - origin).T, order=1, mode="nearest")
    hu = map_coordinates(image, voxel.T, order=1, mode="nearest")
    candidates = dict(np.load(WORK / "low_candidates.npz"))
    all_candidates = np.concatenate(list(candidates.values()))
    cd, _ = cKDTree(all_candidates * spacing).query(voxel * spacing)
    branches = {}
    for k, name in NAMES.items():
        sel = rl == k
        mm = float(rw[sel].sum())
        row = {
            "reference_mm": mm,
            "missed_geometry_mm": float(rw[sel & (d > 1)].sum()),
            "wrong_label_mm": float(rw[sel & (d <= 1) & (pl[nearest] != rl)].sum()),
            "candidate_point_coverage_1mm": float(np.average(cd[sel] <= 1, weights=rw[sel])),
            "center_HU_percentiles_10_50_90": np.percentile(hu[sel], [10, 50, 90]).tolist(),
            "vesselness_percentiles_10_50_90": np.percentile(fv[sel], [10, 50, 90]).tolist(),
            "reference_center_passing_low_threshold": float(np.average((fv[sel] > .018) & (hu[sel] > 80), weights=rw[sel])),
            "matched_courses": {},
        }
        for i in np.unique(owners[sel & (d <= 1)]):
            mask = sel & (d <= 1) & (owners == i)
            row["matched_courses"][new["centerlines"][int(i)]["id"]] = float(rw[mask].sum())
        if k in [5, 6, 7]:
            ranked = []
            for ident, coords in candidates.items():
                dist, _ = cKDTree(coords * spacing).query(voxel[sel] * spacing)
                ranked.append({"candidate_id": ident, "points": len(coords),
                               "coverage_1mm": float(np.average(dist <= 1, weights=rw[sel])),
                               "min_distance_mm": float(dist.min())})
            row["nearest_candidate_components"] = sorted(ranked, key=lambda q: (-q["coverage_1mm"], q["min_distance_mm"]))[:3]
        branches[name] = row

    # Same curves with post-hoc category substitutions: diagnostic only, never saved as an answer.
    counterfactuals = {}
    for title, relabel in [
        ("downstream_numbering_only", {"d2": 14, "om1": 7}),
        ("numbering_plus_disputed_inferior_rv_as_pda", {"d2": 14, "om1": 7, "rca_inferior_rv": 10}),
    ]:
        obj = copy.deepcopy(new)
        for c in obj["centerlines"]:
            if c["id"] in relabel:
                c["labels"] = [relabel[c["id"]]] * len(c["labels"])
        m = scorer.evaluate(obj, ref)
        counterfactuals[title] = {k: m[k] for k in ["geometry", "labeled", "geometry_pass", "labeled_pass"]}
    oracle_answer = copy.deepcopy(ref)
    for c in oracle_answer["centerlines"]:
        c.setdefault("vessel_name", c["id"])
    oracle = scorer.evaluate(oracle_answer, ref)
    assert oracle["format_valid"], oracle
    # Preserve fixed correspondence and exclude only disputed reference categories for sensitivity.
    sensitivity = {}
    for label, excluded in [("exclude_PDA", [10]), ("exclude_PDA_and_LM", [1, 10])]:
        selected = [v for k, v in metrics["per_reference_category"].items() if int(k) not in excluded]
        sensitivity[label] = {"geometry_macro_1mm": float(np.mean([v["geometry_recall_1mm"] for v in selected])),
                              "labeled_macro_1mm": float(np.mean([v["labeled_recall_1mm"] for v in selected])),
                              "all_remaining_geometry_at_least_80_percent": all(v["geometry_recall_1mm"] >= .8 for v in selected)}
    # How much nearest-geometry matching differs from allowing any same-label geometry.
    any_correct = np.zeros(len(r), bool)
    for k in np.unique(rl):
        if np.any(pl == k):
            any_correct[rl == k] = cKDTree(p[pl == k]).query(r[rl == k])[0] <= 1
    matching = {"official_labeled_1mm": metrics["labeled"]["length_weighted_recall_1mm"],
                "any_same_label_within_1mm_diagnostic": float(np.average(any_correct, weights=rw)),
                "length_lost_to_nearest_correspondence_mm": float(rw[any_correct & ~((d <= 1) & (pl[nearest] == rl))].sum())}

    result = {
        "schema_version": 1, "kind": "evaluation", "id": "br042-resume1-trace-gt-audit",
        "experiment_id": "br042-v4-6h", "group_id": "tubular-anatomy",
        "classification": "posthoc_trace_and_reference_sensitivity",
        "depends_on": ["br042-resume1-independent-review", "br042-v4-6h-saved-output-review"],
        "source": "codex://threads/01a0c006-0f8c-78a1-8ab1-2f5868f21ee4",
        "frozen_bytes_verified": True, "exact_verifier_agreement": True,
        "saved_image_cache_matches_native_CTA": True,
        "coronary_metrics_unchanged": unchanged, "changes": changes,
        "tokens": token_rows, "compactions": compactions,
        "branches": branches, "counterfactuals": counterfactuals,
        "fixed_geometry_label_upper_bound": metrics["geometry"],
        "reference_self_score": {k: oracle[k] for k in ["format_valid", "geometry", "labeled", "geometry_pass", "labeled_pass"]},
        "reference_exclusion_sensitivity": sensitivity, "matching_sensitivity": matching,
        "limitations": [
            "Candidate distances are to unordered retained skeleton voxels, not continuous or anatomically adjudicated vessels.",
            "Threshold rates sample the reference center, not an entire lumen or the full discovery algorithm.",
            "Relabeling and reference-exclusion counterfactuals use ground truth after the run; they are not corrected scores.",
            "Raw response-usage records and terminal cumulative usage differ; neither is a billing receipt.",
            "No model trial or clinical reference adjudication was performed.",
        ],
        "evidence": [{"path": str(q.relative_to(ROOT)), "sha256": sha(q)} for q in [
            source, OLD / "centerlines.json", OLD / "vessels.json", ANSWER / "centerlines.json",
            ANSWER / "vessels.json", ANSWER / "method.md", ANSWER / "candidate_review.py",
            WORK / "low_candidates.npz", WORK / "vesselness.npz", WORK / "paths.npz",
            WORK / "image.npy", TASK / "tests/reference.json",
            TASK / "tests/score.py", TRIAL / "verifier/metrics.json"]],
    }
    (HERE / "trace-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["changes", "tokens", "counterfactuals", "reference_self_score", "matching_sensitivity"]}, indent=2))
    print(json.dumps({k: branches[k] for k in ["D2", "OM1", "OM2"]}, indent=2))


if __name__ == "__main__":
    main()
