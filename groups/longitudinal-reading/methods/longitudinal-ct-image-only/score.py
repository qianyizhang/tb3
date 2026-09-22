"""Private v1 evaluator: separate detection, segmentation, association and events.

No scalar scientific pass threshold; Harbor reward is artifact-contract validity.
"""

import argparse
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

VISITS = ("baseline", "followup")
TOLERANCE_MM = 3.0


def ratio(n, d):
    return float(n / d) if d else None


def prf(tp, fp, fn):
    return dict(
        tp=int(tp),
        fp=int(fp),
        fn=int(fn),
        precision=ratio(tp, tp + fp),
        recall=ratio(tp, tp + fn),
        f1=ratio(2 * tp, 2 * tp + fp + fn),
    )


def avg(values):
    values = [x for x in values if x is not None]
    return float(np.mean(values)) if values else None


def assign(weights, valid):
    if not weights.size:
        return []
    # Maximum valid cardinality first, then the secondary bounded similarity.
    priority = min(weights.shape) + 1
    a, b = linear_sum_assignment(-(priority * valid + weights * valid))
    return [(int(i), int(j)) for i, j in zip(a, b) if valid[i, j]]


def geometry_points(mask, ids, affine, include_points=True):
    boxes = ndimage.find_objects(mask)
    centers, points = [], []
    for value in ids:
        box = boxes[value - 1]
        if include_points:
            xyz = np.argwhere(mask[box] == value) + np.array([s.start for s in box])
            world = nib.affines.apply_affine(affine, xyz)
            centers.append(world.mean(axis=0))
            points.append(world)
        else:
            # Bounded memory even for a huge incorrect prediction.
            total, moments = 0, np.zeros(3)
            for k in range(box[2].start, box[2].stop):
                x, y = np.nonzero(mask[box[0], box[1], k] == value)
                total += len(x)
                moments += [
                    x.sum() + len(x) * box[0].start,
                    y.sum() + len(y) * box[1].start,
                    len(x) * k,
                ]
            centers.append(nib.affines.apply_affine(affine, moments / total))
    return np.asarray(centers).reshape(-1, 3), points


def visit_score(prediction, reference):
    ref = nib.load(reference)
    g = np.asarray(ref.dataobj).astype(np.uint16)
    gids = [int(x) for x in np.unique(g) if x]
    if not Path(prediction).is_file():
        return dict(valid=False, reason="missing_mask", gt_count=len(gids))
    try:
        im = nib.load(prediction)
        if im.shape != ref.shape or not np.allclose(im.affine, ref.affine, rtol=0, atol=1e-5):
            raise ValueError("shape_or_affine_mismatch")
        p = np.asarray(im.dataobj)
        if (
            not np.isfinite(p).all()
            or not np.equal(p, np.rint(p)).all()
            or p.min() < 0
            or p.max() > 65535
        ):
            raise ValueError("labels_must_be_integers_0_to_65535")
        p = p.astype(np.uint16)
        pids = [int(x) for x in np.unique(p) if x]
        if len(pids) > 4096:
            raise ValueError("too_many_instances")
    except Exception as exc:
        return dict(valid=False, reason=str(exc), gt_count=len(gids))
    allg, allp = np.array([0] + gids), np.array([0] + pids)
    counts = np.zeros((len(allg), len(allp)), dtype=np.int64)
    for z in range(g.shape[2]):
        gi, pi = np.searchsorted(allg, g[:, :, z]), np.searchsorted(allp, p[:, :, z])
        counts += np.bincount((gi * len(allp) + pi).ravel(), minlength=counts.size).reshape(
            counts.shape
        )
    gc, pc = counts.sum(axis=1)[1:], counts.sum(axis=0)[1:]
    intersection = counts[1:, 1:]
    den = gc[:, None] + pc[None, :]
    dice = np.divide(
        2 * intersection, den, out=np.zeros_like(intersection, dtype=float), where=den > 0
    )
    union = den - intersection
    iou = np.divide(
        intersection, union, out=np.zeros_like(intersection, dtype=float), where=union > 0
    )
    gcenters, gpoints = geometry_points(g, gids, ref.affine)
    pcenters, _ = geometry_points(p, pids, ref.affine, include_points=False)
    distances = np.zeros((len(gids), len(pids)))
    centerdist = np.zeros_like(distances)
    for i, points in enumerate(gpoints):
        if pids:
            distances[i] = cKDTree(points).query(pcenters)[0]
            centerdist[i] = np.linalg.norm(pcenters - gcenters[i], axis=1)
            # A point inside the reference is accepted even with thick/oblique voxels.
            ijk = np.rint(nib.affines.apply_affine(np.linalg.inv(ref.affine), pcenters)).astype(int)
            inside = np.all((ijk >= 0) & (ijk < np.array(g.shape)), axis=1)
            for j in np.flatnonzero(inside):
                if g[tuple(ijk[j])] == gids[i]:
                    distances[i, j] = 0.0
    similarity = 1 / (1 + centerdist)
    pairs = assign(similarity, distances <= TOLERANCE_MM)
    detection = prf(len(pairs), len(pids) - len(pairs), len(gids) - len(pairs))
    detection.update(
        gt_count=len(gids),
        prediction_count=len(pids),
        criterion="prediction centroid in reference mask or within 3 mm of a labeled voxel center; one-to-one assignment",
        mean_centroid_distance_mm=avg([centerdist[i, j] for i, j in pairs]),
        mean_centroid_to_reference_mm=avg([distances[i, j] for i, j in pairs]),
    )
    matchmap = {pids[j]: gids[i] for i, j in pairs}
    best = linear_sum_assignment(-dice) if dice.size else ([], [])
    best_dice = {int(i): float(dice[i, j]) for i, j in zip(*best)}
    assigned = {i: j for i, j in pairs}
    per_gt = [
        dict(
            gt_id=gids[i],
            voxels=int(gc[i]),
            detection_prediction_id=pids[assigned[i]] if i in assigned else None,
            detected_dice=float(dice[i, assigned[i]]) if i in assigned else 0.0,
            best_one_to_one_dice=best_dice.get(i, 0.0),
        )
        for i in range(len(gids))
    ]
    segmentation = dict(
        foreground_dice=ratio(2 * intersection.sum(), gc.sum() + pc.sum()),
        foreground_precision=ratio(intersection.sum(), pc.sum()),
        foreground_recall=ratio(intersection.sum(), gc.sum()),
        gt_macro_dice=avg([r["best_one_to_one_dice"] for r in per_gt]),
        detected_only_macro_dice=avg([float(dice[i, j]) for i, j in pairs]),
        detection_anchored_gt_macro_dice=avg([r["detected_dice"] for r in per_gt]),
    )
    overlap_detection = {}
    for threshold in (0.1, 0.25, 0.5):
        matching = assign(iou, iou >= threshold)
        overlap_detection[str(threshold)] = prf(
            len(matching), len(pids) - len(matching), len(gids) - len(matching)
        )
    return dict(
        valid=True,
        ids=pids,
        gt_ids=gids,
        mapping=matchmap,
        detection=detection,
        segmentation=segmentation,
        overlap_detection_sensitivity=overlap_detection,
        per_gt=per_gt,
        matched_pairs=[
            dict(
                gt_id=gids[i],
                prediction_id=pids[j],
                dice=float(dice[i, j]),
                iou=float(iou[i, j]),
                centroid_mm=pcenters[j].tolist(),
                centroid_distance_mm=float(centerdist[i, j]),
            )
            for i, j in pairs
        ],
    )


def validate_events(document, ids):
    if (
        not isinstance(document, dict)
        or document.get("schema_version") != 1
        or not isinstance(document.get("groups"), list)
    ):
        raise ValueError("invalid_events_document")
    seen = {v: [] for v in VISITS}
    groups = []
    for group in document["groups"]:
        if not isinstance(group, dict):
            raise ValueError("invalid_event_group")
        b, f = group.get("baseline_ids"), group.get("followup_ids")
        if not isinstance(b, list) or not isinstance(f, list):
            raise ValueError("ids_must_be_lists")
        for value in b + f:
            if type(value) is not int or value <= 0:
                raise ValueError("event_id_must_be_positive_integer")
        sizes = len(b), len(f)
        event = group.get("event")
        allowed = (
            event == "persistent"
            and sizes == (1, 1)
            or event == "merging"
            and sizes[0] >= 2
            and sizes[1] == 1
            or event == "disappearing"
            and sizes == (1, 0)
            or event == "newly_appearing"
            and sizes == (0, 1)
            or event == "unresolved"
            and sum(sizes) > 0
        )
        if not allowed:
            raise ValueError("event_cardinality_mismatch")
        seen["baseline"].extend(b)
        seen["followup"].extend(f)
        groups.append(dict(baseline_ids=sorted(b), followup_ids=sorted(f), event=event))
    for v in VISITS:
        if len(seen[v]) != len(set(seen[v])) or set(seen[v]) != set(ids[v]):
            raise ValueError("each_mask_instance_must_occur_exactly_once_" + v)
    return groups


def event_key(group):
    return (
        group["event"],
        tuple(sorted(group["baseline_ids"], key=str)),
        tuple(sorted(group["followup_ids"], key=str)),
    )


def edges(groups):
    return {
        (b, f)
        for g in groups
        if g["event"] in ("persistent", "merging")
        for b in g["baseline_ids"]
        for f in g["followup_ids"]
    }


def set_score(predicted, truth):
    return prf(len(predicted & truth), len(predicted - truth), len(truth - predicted))


def association_score(groups, reference, mappings):
    maps = [{int(k): v for k, v in mappings[visit].items()} for visit in VISITS]
    remapped = []
    detectable = []
    for number, group in enumerate(groups):
        g = dict(event=group["event"])
        complete = True
        for side, key in enumerate(("baseline_ids", "followup_ids")):
            mapped = []
            for value in group[key]:
                if value not in maps[side]:
                    complete = False
                mapped.append(maps[side].get(value, f"unmatched_{side}_{value}"))
            g[key] = sorted(mapped, key=str)
        remapped.append(g)
        if complete:
            detectable.append(g)
    gt_edges, predicted_edges = edges(reference), edges(remapped)
    detected = [set(m.values()) for m in maps]
    eligible_edges = {(b, f) for b, f in gt_edges if b in detected[0] and f in detected[1]}
    eligible_groups = [
        g
        for g in reference
        if set(g["baseline_ids"]) <= detected[0] and set(g["followup_ids"]) <= detected[1]
    ]
    conditional_pred_edges = {
        (b, f) for b, f in predicted_edges if b in detected[0] and f in detected[1]
    }
    gt_events, predicted_events = set(map(event_key, reference)), set(map(event_key, remapped))
    event_metrics = set_score(predicted_events, gt_events)
    per_class = {}
    for event in ("persistent", "merging", "disappearing", "newly_appearing"):
        p = {e for e in predicted_events if e[0] == event}
        g = {e for e in gt_events if e[0] == event}
        per_class[event] = dict(
            reference_groups=len(g), prediction_groups=len(p), **set_score(p, g)
        )
    return dict(
        links_end_to_end=set_score(predicted_edges, gt_edges),
        links_conditional_on_detection=dict(
            eligible_gt_edges=len(eligible_edges),
            total_gt_edges=len(gt_edges),
            **set_score(conditional_pred_edges, eligible_edges),
        ),
        events_end_to_end=event_metrics,
        events_conditional_on_detection=dict(
            eligible_gt_groups=len(eligible_groups),
            total_gt_groups=len(reference),
            **set_score(set(map(event_key, detectable)), set(map(event_key, eligible_groups))),
        ),
        event_classes=per_class,
        unresolved_groups=sum(g["event"] == "unresolved" for g in groups),
        mapped_predictions=remapped,
    )


def score(answer, reference):
    answer, reference = Path(answer), Path(reference)
    result = dict(
        schema_version=1,
        reward_meaning="output_contract_only_not_scientific_success",
        matching_tolerance_mm=TOLERANCE_MM,
        visits={},
    )
    for v in VISITS:
        result["visits"][v] = visit_score(
            answer / f"{v}_instances.nii.gz", reference / f"{v}_instances.nii.gz"
        )
    masks_valid = all(r["valid"] for r in result["visits"].values())
    graph_valid = False
    try:
        if not masks_valid:
            raise ValueError("mask_contract_invalid; valid visit metrics retained separately")
        groups = validate_events(
            json.loads((answer / "events.json").read_text()),
            {v: result["visits"][v]["ids"] for v in VISITS},
        )
        graph_valid = True
        truth = json.loads((reference / "events.json").read_text())["groups"]
        result["association"] = association_score(
            groups, truth, {v: result["visits"][v]["mapping"] for v in VISITS}
        )
    except Exception as exc:
        result["association"] = dict(valid=False, reason=str(exc))
    valid_visits = [r for r in result["visits"].values() if r["valid"]]
    result["valid_visit_count"] = len(valid_visits)
    result["detection_micro"] = (
        prf(*(sum(r["detection"][k] for r in valid_visits) for k in ("tp", "fp", "fn")))
        if valid_visits
        else None
    )
    result["segmentation_gt_macro_dice"] = avg(
        [x["best_one_to_one_dice"] for r in valid_visits for x in r["per_gt"]]
    )
    result["report_present"] = (answer / "report.md").is_file() and (
        answer / "report.md"
    ).stat().st_size > 0
    result["valid"] = masks_valid and graph_valid and result["report_present"]
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--answer", type=Path, default=Path("/app/answer"))
    parser.add_argument("--reference", type=Path, default=Path("/tests/reference"))
    parser.add_argument("--output", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = score(args.answer, args.reference)
    (args.output / "metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "reward.txt").write_text(str(int(result["valid"])) + "\n")
    print(
        json.dumps(
            {
                "passed": ["artifact_contract"] if result["valid"] else [],
                "failures": [] if result["valid"] else ["artifact_contract"],
                "reward_meaning": result["reward_meaning"],
            }
        )
    )


if __name__ == "__main__":
    main()
