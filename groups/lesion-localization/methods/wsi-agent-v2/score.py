"""Private diagnostic measures for the revised WSI tasks.

Harbor reward checks the answer contract. The returned measures are separate
diagnostics on selected public source examples, not clinical performance scores.
"""

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from scipy.optimize import linear_sum_assignment


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def points_from(path: Path, *, roi: bool = False, confidence: bool = False) -> list[dict]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("points"), list):
        raise ValueError("Expected a JSON object with a points array")
    points = payload["points"]
    if len(points) > 5000:
        raise ValueError("Too many points")
    for point in points:
        if not isinstance(point, dict) or not all(k in point for k in ("x", "y")):
            raise ValueError("Every point needs x and y")
        if not all(
            isinstance(point[k], (int, float)) and math.isfinite(point[k]) for k in ("x", "y")
        ):
            raise ValueError("Point coordinates must be finite numbers")
        if roi and point.get("roi") not in {"roi1", "roi2", "roi3"}:
            raise ValueError("Unknown ROI")
        if confidence and (
            not isinstance(point.get("confidence"), (int, float))
            or not math.isfinite(point["confidence"])
            or not 0 <= point["confidence"] <= 1
        ):
            raise ValueError("Every CAMELYON point needs confidence from 0 to 1")
    return points


def inside_polygon(x: float, y: float, polygon: list[list[float]]) -> bool:
    hit = False
    for (ax, ay), (bx, by) in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            hit = not hit
    return hit


def boundary_distance(x: float, y: float, polygon: list[list[float]]) -> float:
    best = float("inf")
    for (ax, ay), (bx, by) in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        fraction = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / length_sq)) if length_sq else 0
        best = min(best, math.hypot(x - ax - fraction * dx, y - ay - fraction * dy))
    return best


def match(cost: np.ndarray, threshold: float) -> list[tuple[int, int]]:
    if not cost.size:
        return []
    valid = cost <= threshold
    penalty = min(cost.shape) + 1
    row, col = linear_sum_assignment(np.where(valid, cost / max(threshold, 1), penalty))
    return [(int(i), int(j)) for i, j in zip(row, col, strict=True) if valid[i, j]]


def score_hubmap(points: list[dict], reference: dict) -> dict:
    polygons = reference["polygons"]
    tolerance = 50 / reference["mpp"]
    distances = np.full((len(polygons), len(points)), np.inf)
    for i, polygon in enumerate(polygons):
        for j, point in enumerate(points):
            distances[i, j] = (
                0
                if inside_polygon(point["x"], point["y"], polygon)
                else boundary_distance(point["x"], point["y"], polygon)
            )
    pairs = match(distances, tolerance)
    return {
        "reference_objects": len(polygons),
        "submitted_points": len(points),
        "matched_reference_objects": len(pairs),
        "reference_recall": ratio(len(pairs), len(polygons)),
        "unmatched_points_pending_review": len(points) - len(pairs),
        "criterion": "one-to-one point in source polygon or within 50 micrometers of edge",
        "scope": "reference recall only; unmatched points have no adjudicated false-positive status",
    }


def score_tiger(points: list[dict], reference: dict, root: Path) -> dict:
    results = {}
    for roi in ("roi1", "roi2", "roi3"):
        truth = reference["rois"][roi]
        predicted = [p for p in points if p["roi"] == roi]
        cells = truth["cells"]
        cost = np.array(
            [[math.hypot(a["x"] - b["x"], a["y"] - b["y"]) for b in predicted] for a in cells]
        ).reshape(len(cells), len(predicted))
        pairs = match(cost, 20)
        mask = np.asarray(Image.open(root / truth["mask"]))
        boundary_maps = {
            int(code): distance_transform_edt(mask == code) for code in np.unique(mask)
        }
        correct_reference = correct_predicted = boundary_pairs = interior_correct = 0
        interior_pairs = 0
        for i, j in pairs:
            rx, ry = round(cells[i]["x"]), round(cells[i]["y"])
            px, py = round(predicted[j]["x"]), round(predicted[j]["y"])
            if not (0 <= ry < mask.shape[0] and 0 <= rx < mask.shape[1]):
                raise ValueError("Reference cell outside tissue mask")
            if not (0 <= py < mask.shape[0] and 0 <= px < mask.shape[1]):
                raise ValueError("Submitted matched point outside tissue mask")
            reference_code = int(mask[ry, rx])
            predicted_code = int(mask[py, px])
            reported_code = predicted[j].get("compartment")
            if reported_code not in range(8):
                raise ValueError("TIGER compartment must be an integer code 0..7")
            correct_reference += reported_code == reference_code
            correct_predicted += reported_code == predicted_code
            on_boundary = boundary_maps[reference_code][ry, rx] <= 20
            boundary_pairs += on_boundary
            if not on_boundary:
                interior_pairs += 1
                interior_correct += reported_code == reference_code
        results[roi] = {
            "reference_cells": len(cells),
            "submitted_cells": len(predicted),
            "matched_cells": len(pairs),
            "cell_recall": ratio(len(pairs), len(cells)),
            "cell_precision_within_reference": ratio(len(pairs), len(predicted)),
            "compartment_accuracy_reference_center": ratio(correct_reference, len(pairs)),
            "compartment_accuracy_submitted_center": ratio(correct_predicted, len(pairs)),
            "boundary_band_pairs": int(boundary_pairs),
            "interior_pairs": interior_pairs,
            "interior_compartment_accuracy_reference_center": ratio(
                interior_correct, interior_pairs
            ),
        }
    return {
        "rois": results,
        "matching": "one-to-one within 20 ROI pixels",
        "boundary_band": "reference center within 20 pixels of another mask code",
        "scope": "three fixed ROIs from one slide; 0 is unknown/unannotated",
    }


def score_camelyon(points: list[dict], reference: dict) -> dict:
    polygons = reference["tumor"]
    exclusions = reference["exclusion"]
    groups = reference["lesion_groups"]
    polygon_group = {index: g for g, indices in enumerate(groups) for index in indices}
    if set(polygon_group) != set(range(len(polygons))):
        raise ValueError("Every tumor polygon must belong to exactly one lesion group")
    hit_groups: set[int] = set()
    first_hits = false_positives = excluded = duplicates = 0
    for point in sorted(points, key=lambda p: p["confidence"], reverse=True):
        x, y = point["x"], point["y"]
        if any(inside_polygon(x, y, polygon) for polygon in exclusions):
            excluded += 1
            false_positives += 1
            continue
        candidate_groups = {
            polygon_group[i] for i, polygon in enumerate(polygons) if inside_polygon(x, y, polygon)
        }
        if not candidate_groups:
            false_positives += 1
        elif candidate_groups - hit_groups:
            hit_groups.update(candidate_groups)
            first_hits += 1
        else:
            duplicates += 1
            false_positives += 1
    return {
        "source_slide": reference["slide"],
        "reference_tumor_polygons": len(polygons),
        "reference_lesion_groups": len(groups),
        "hit_lesion_groups": len(hit_groups),
        "lesion_group_recall": ratio(len(hit_groups), len(groups)),
        "submitted_points": len(points),
        "first_hit_points": first_hits,
        "false_positive_points": false_positives,
        "duplicate_points_within_hit_groups": duplicates,
        "excluded_points": excluded,
        "scope": "selected fully annotated public slide; 50 micrometer polygon grouping is a study rule",
    }


def score_hiesd(answer: Path, reference: dict) -> dict:
    payload = json.loads(answer.read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("labels"), list):
        raise ValueError("Expected a JSON object with a labels array")
    labels = payload["labels"]
    expected = reference["labels"]
    if len(labels) != len(expected) or {item.get("id") for item in labels} != set(expected):
        raise ValueError("Supply exactly one label for every patch ID")
    if any(item.get("class") not in range(7) for item in labels):
        raise ValueError("Patch class must be an integer code 0..6")
    predictions = {item["id"]: item["class"] for item in labels}
    if len(predictions) != len(labels):
        raise ValueError("Duplicate patch ID")
    per_class = {}
    for code in range(1, 7):
        ids = [patch_id for patch_id, truth in expected.items() if truth == code]
        covered = sum(predictions[patch_id] > 0 for patch_id in ids)
        correct = sum(predictions[patch_id] == code for patch_id in ids)
        per_class[str(code)] = {
            "patches": len(ids),
            "covered": covered,
            "correct": correct,
            "accuracy": ratio(correct, len(ids)),
        }
    correct_total = sum(item["correct"] for item in per_class.values())
    covered_total = sum(item["covered"] for item in per_class.values())
    return {
        "patches": len(expected),
        "covered": covered_total,
        "correct": correct_total,
        "coverage": ratio(covered_total, len(expected)),
        "accuracy": ratio(correct_total, len(expected)),
        "accuracy_on_covered": ratio(correct_total, covered_total),
        "per_class": per_class,
        "scope": "GT-selected annotated patches from one slide; correlated regions, no WSI search score",
    }


def score(answer: Path, reference_dir: Path) -> dict:
    reference = json.loads((reference_dir / "reference.json").read_text())
    kind = reference["kind"]
    if kind == "hiesd_patches":
        metrics = score_hiesd(answer / "labels.json", reference)
    elif kind == "hubmap":
        metrics = score_hubmap(points_from(answer / "points.json"), reference)
    elif kind == "tiger":
        metrics = score_tiger(
            points_from(answer / "points.json", roi=True), reference, reference_dir
        )
    elif kind == "camelyon_lesions":
        metrics = score_camelyon(points_from(answer / "points.json", confidence=True), reference)
    else:
        raise ValueError(f"Unsupported WSI task kind: {kind}")
    return {"kind": kind, "valid": True, "reward_meaning": "answer contract", **metrics}


def main() -> None:
    import os

    answer = Path(os.environ.get("TB3_ANSWER_DIR", "/app/answer"))
    reference_dir = Path(os.environ.get("TB3_REFERENCE_DIR", "/tests/reference"))
    try:
        result = score(answer, reference_dir)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        result = {"valid": False, "reason": str(exc), "reward_meaning": "answer contract"}
    Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
    Path("/logs/verifier/metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    Path("/logs/verifier/reward.txt").write_text(f"{int(result['valid'])}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
