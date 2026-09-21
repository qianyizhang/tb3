"""Private scoring for independent binary organ masks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np


def _zero_result(reason: str) -> dict[str, object]:
    return {
        "valid": False,
        "reason": reason,
        "semantic_macro_dice": 0.0,
        "matched_macro_dice": 0.0,
        "identity_accuracy": None,
        "identity_assessable_matches": 0,
        "foreground_dice": 0.0,
        "foreground_precision": 0.0,
        "foreground_recall": 0.0,
        "per_label": [],
        "matched_pairs": [],
    }


def _maximum_assignment(weights: np.ndarray) -> list[int]:
    """Return an exact maximum-weight one-to-one assignment for small matrices."""
    n = int(weights.shape[0])
    if weights.shape != (n, n):
        raise ValueError("assignment matrix must be square")
    scores = {0: 0.0}
    parents: list[dict[int, tuple[int, int]]] = []
    for row in range(n):
        next_scores: dict[int, float] = {}
        row_parent: dict[int, tuple[int, int]] = {}
        for used, score in scores.items():
            for col in range(n):
                bit = 1 << col
                if used & bit:
                    continue
                new_used = used | bit
                candidate = score + float(weights[row, col])
                old = next_scores.get(new_used)
                if old is None or candidate > old + 1e-15:
                    next_scores[new_used] = candidate
                    row_parent[new_used] = (used, col)
        scores = next_scores
        parents.append(row_parent)
    used = (1 << n) - 1
    assignment = [-1] * n
    for row in range(n - 1, -1, -1):
        previous, col = parents[row][used]
        assignment[row] = col
        used = previous
    return assignment


def _load_binary(path: Path, reference: nib.Nifti1Image) -> np.ndarray:
    image = nib.load(path)
    if image.shape != reference.shape:
        raise ValueError(f"geometry mismatch for {path.name}: shape")
    if not np.allclose(image.affine, reference.affine, atol=1e-5, rtol=0):
        raise ValueError(f"geometry mismatch for {path.name}: affine")
    values = np.asanyarray(image.dataobj)
    if not np.isfinite(values).all():
        raise ValueError(f"nonfinite values in {path.name}")
    unique = set(np.unique(values).tolist())
    if not unique.issubset({0, 1}):
        raise ValueError(f"nonbinary values in {path.name}")
    return values.astype(bool)


def score(answer: Path, reference: Path, label_file: Path) -> dict[str, object]:
    config = json.loads(label_file.read_text())
    labels = config["labels"]
    filenames = [item["file"] for item in labels]
    if not answer.is_dir():
        return _zero_result("missing_output_directory")
    submitted = {path.name for path in answer.glob("*.nii.gz")}
    unexpected = sorted(submitted - set(filenames))
    missing = sorted(set(filenames) - submitted)
    if unexpected:
        return _zero_result("unknown_mask_files: " + ", ".join(unexpected))
    if missing:
        return _zero_result("missing_mask_files: " + ", ".join(missing))

    first_reference = nib.load(reference / filenames[0])
    try:
        gt = [_load_binary(reference / name, first_reference) for name in filenames]
        prediction = [_load_binary(answer / name, first_reference) for name in filenames]
    except Exception as exc:
        return _zero_result(str(exc))

    n = len(labels)
    intersections = np.zeros((n, n), dtype=np.int64)
    dice = np.zeros((n, n), dtype=np.float64)
    gt_counts = np.array([int(mask.sum()) for mask in gt], dtype=np.int64)
    pred_counts = np.array([int(mask.sum()) for mask in prediction], dtype=np.int64)
    for i, gt_mask in enumerate(gt):
        for j, predicted_mask in enumerate(prediction):
            # Index only the sparse GT foreground instead of allocating and
            # scanning a full-volume boolean conjunction for every pair.
            overlap = int(np.count_nonzero(predicted_mask[gt_mask]))
            intersections[i, j] = overlap
            denominator = int(gt_counts[i] + pred_counts[j])
            dice[i, j] = 2.0 * overlap / denominator if denominator else 1.0

    semantic = np.diag(dice)
    assignment = _maximum_assignment(dice)
    matched = np.array([dice[i, assignment[i]] for i in range(n)])
    pairs = []
    assessable = 0
    correct = 0
    for i, j in enumerate(assignment):
        overlap = int(intersections[i, j])
        if overlap > 0:
            assessable += 1
            correct += int(i == j)
        pairs.append(
            {
                "gt_id": int(labels[i]["id"]),
                "gt_name": labels[i]["name"],
                "prediction_id": int(labels[j]["id"]),
                "prediction_name": labels[j]["name"],
                "intersection": overlap,
                "dice": float(dice[i, j]),
                "identity_correct": bool(i == j and overlap > 0),
            }
        )

    gt_union = np.logical_or.reduce(gt)
    prediction_union = np.logical_or.reduce(prediction)
    foreground_intersection = int(np.count_nonzero(gt_union & prediction_union))
    gt_foreground = int(gt_union.sum())
    predicted_foreground = int(prediction_union.sum())
    foreground_denominator = gt_foreground + predicted_foreground
    per_label = []
    for i, item in enumerate(labels):
        per_label.append(
            {
                "id": int(item["id"]),
                "name": item["name"],
                "gt_voxels": int(gt_counts[i]),
                "prediction_voxels": int(pred_counts[i]),
                "intersection": int(intersections[i, i]),
                "dice": float(semantic[i]),
            }
        )

    return {
        "valid": True,
        "reason": None,
        "semantic_macro_dice": float(semantic.mean()),
        "matched_macro_dice": float(matched.mean()),
        "semantic_geometry_gap": float(matched.mean() - semantic.mean()),
        "identity_accuracy": (correct / assessable if assessable else None),
        "identity_correct_matches": correct,
        "identity_assessable_matches": assessable,
        "foreground_dice": (
            2.0 * foreground_intersection / foreground_denominator
            if foreground_denominator
            else 1.0
        ),
        "foreground_precision": (
            foreground_intersection / predicted_foreground if predicted_foreground else 0.0
        ),
        "foreground_recall": (foreground_intersection / gt_foreground if gt_foreground else 1.0),
        "foreground_gt_voxels": gt_foreground,
        "foreground_prediction_voxels": predicted_foreground,
        "foreground_false_positive_voxels": predicted_foreground - foreground_intersection,
        "foreground_false_negative_voxels": gt_foreground - foreground_intersection,
        "per_label": per_label,
        "matched_pairs": pairs,
    }


def main() -> None:
    answer = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/answer/masks")
    reference = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tests/reference")
    label_file = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("/tests/labels.json")
    result = score(answer, reference, label_file)
    output = Path("/logs/verifier")
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    reward = float(result["semantic_macro_dice"])
    (output / "reward.txt").write_text(f"{reward}\n")
    print(
        json.dumps(
            {
                "valid": result["valid"],
                "semantic_macro_dice": reward,
                "matched_macro_dice": result["matched_macro_dice"],
            }
        )
    )


if __name__ == "__main__":
    main()
