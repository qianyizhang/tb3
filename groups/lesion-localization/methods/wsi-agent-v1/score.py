"""Private diagnostic scorer for the four curated WSI task conditions."""

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import linear_sum_assignment


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def read_points(path: Path, *, roi: bool = False) -> list[dict]:
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
            raise ValueError("TIGER points need roi1, roi2 or roi3")
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
            if inside_polygon(point["x"], point["y"], polygon):
                distances[i, j] = 0
            else:
                distances[i, j] = boundary_distance(point["x"], point["y"], polygon)
    pairs = match(distances, tolerance)
    return {
        "reference_objects": len(polygons),
        "predicted_points": len(points),
        "matched": len(pairs),
        "unmatched_predictions": len(points) - len(pairs),
        "missed_references": len(polygons) - len(pairs),
        "recall": ratio(len(pairs), len(polygons)),
        "precision_within_reference": ratio(len(pairs), len(points)),
        "absolute_count_error": abs(len(points) - len(polygons)),
        "criterion": "one-to-one point inside polygon or within 50 um of its edge",
        "scope": "selected public training image; unmatched predictions need coverage review",
    }


def score_camelyon(points: list[dict], reference: dict) -> dict:
    tumor = reference["tumor"]
    exclusion = reference["exclusion"]
    valid = [
        point
        for point in points
        if not any(inside_polygon(point["x"], point["y"], p) for p in exclusion)
    ]
    hit = [
        i
        for i, polygon in enumerate(tumor)
        if any(inside_polygon(p["x"], p["y"], polygon) for p in valid)
    ]
    supported = sum(
        any(inside_polygon(p["x"], p["y"], polygon) for polygon in tumor) for p in valid
    )
    return {
        "tumor_polygons": len(tumor),
        "polygons_with_point": len(hit),
        "polygon_hit_fraction": ratio(len(hit), len(tumor)),
        "submitted_points": len(points),
        "reference_supported_points": supported,
        "outside_reference_points": len(valid) - supported,
        "excluded_points": len(points) - len(valid),
        "scope": "polygons are not independent lesions; one positive teaching slide only",
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
        attributed = 0
        for i, j in pairs:
            x, y = round(cells[i]["x"]), round(cells[i]["y"])
            if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
                attributed += predicted[j].get("compartment") == int(mask[y, x])
        results[roi] = {
            "reference_cells": len(cells),
            "predicted_cells": len(predicted),
            "matched": len(pairs),
            "recall": ratio(len(pairs), len(cells)),
            "precision": ratio(len(pairs), len(predicted)),
            "matched_compartment_accuracy": ratio(attributed, len(pairs)),
            "count_error": len(predicted) - len(cells),
        }
    return {"rois": results, "scope": "fixed ROIs; merged lymphocyte/plasma-cell boxes"}


def score_hiesd(answer: Path, reference: dict, root: Path) -> dict:
    true = np.asarray(Image.open(root / reference["mask"]))
    predicted = np.asarray(Image.open(answer))
    if predicted.shape != true.shape or predicted.ndim != 2:
        raise ValueError("Expected one-channel PNG on the supplied 64x grid")
    if np.any(predicted > reference["n_classes"]):
        raise ValueError("Unknown class code")
    valid = true > 0
    recognized = valid & (predicted > 0)
    correct = valid & (predicted == true)
    return {
        "annotated_pixels": int(valid.sum()),
        "predicted_annotated_pixels": int(recognized.sum()),
        "correct_annotated_pixels": int(correct.sum()),
        "coverage": ratio(int(recognized.sum()), int(valid.sum())),
        "correct_fraction": ratio(int(correct.sum()), int(valid.sum())),
        "accuracy_on_predicted": ratio(int(correct.sum()), int(recognized.sum())),
        "scope": "coarse XML regions only; unannotated pixels are not normal GT",
    }


def score(answer: Path, reference_dir: Path) -> dict:
    reference = json.loads((reference_dir / "reference.json").read_text())
    kind = reference["kind"]
    if kind == "hiesd":
        metrics = score_hiesd(answer / "map.png", reference, reference_dir)
    else:
        points = read_points(answer / "points.json", roi=kind == "tiger")
        metrics = {
            "hubmap": score_hubmap,
            "camelyon": score_camelyon,
            "tiger": lambda p, r: score_tiger(p, r, reference_dir),
        }[kind](points, reference)
    return {"kind": kind, "valid": True, "reward_meaning": "artifact contract", **metrics}


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--answer", type=Path, default=Path("/app/answer"))
    parser.add_argument("--reference", type=Path, default=Path("/tests/reference"))
    parser.add_argument("--output", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()
    try:
        result = score(args.answer, args.reference)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {"valid": False, "reason": str(exc), "reward_meaning": "artifact contract"}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "reward.txt").write_text(str(int(result["valid"])) + "\n")
    print(
        json.dumps({"passed": ["artifact_contract"] if result["valid"] else [], "result": result})
    )


if __name__ == "__main__":
    main()
