"""Strict voxel-space contract; physical errors computed only by the verifier."""

from .scoring import (
    ContractError,
    finite_matrix3,
    finite_number,
    finite_point3,
    object_value,
    physical_distance_mm,
    require,
)


def score(answer: object, truth: object) -> dict[str, object]:
    try:
        answer_object = object_value(answer, keys={"space", "landmarks"})
        require(answer_object["space"] == "voxel_ijk_zero_based")
        predictions = object_value(answer_object["landmarks"])

        truth_object = object_value(truth)
        truth_points = object_value(truth_object["points_ijk"])
        require(bool(truth_points) and set(predictions) == set(truth_points))
        shape = finite_point3(truth_object["shape_ijk"])
        require(all(size > 0 for size in shape))
        linear = finite_matrix3(truth_object["linear_voxel_to_mm"])
        tolerance_mm = finite_number(truth_object["tolerance_mm"])
        require(tolerance_mm >= 0)

        errors: dict[str, float] = {}
        for name, truth_point_value in truth_points.items():
            predicted_point = finite_point3(predictions[name])
            require(all(-0.5 <= predicted_point[index] <= shape[index] - 0.5 for index in range(3)))
            truth_point = finite_point3(truth_point_value)
            errors[name] = physical_distance_mm(predicted_point, truth_point, linear)
        accepted = {name: error <= tolerance_mm for name, error in errors.items()}
        return {
            "reward": int(all(accepted.values())),
            "accepted": accepted,
            "accepted_count": sum(accepted.values()),
            "total": len(errors),
            "errors_mm": errors,
            "mean_mm": sum(errors.values()) / len(errors),
            "max_mm": max(errors.values()),
            "contract_valid": True,
        }
    except (ContractError, KeyError, TypeError, ValueError, OverflowError):
        return {
            "reward": 0,
            "contract_valid": False,
            "invalid": "Expected tagged native zero-based voxel triples for exactly all named points",
        }
