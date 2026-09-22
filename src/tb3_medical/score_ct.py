"""Separate invented detections, visibility classification, localization, extrapolation."""

from .scoring import (
    ContractError,
    finite_matrix3,
    finite_point3,
    object_value,
    physical_distance_mm,
    require,
    string_choice,
)


def score(answer: object, truth: object) -> dict[str, object]:
    try:
        answer_object = object_value(answer, keys={"space", "landmarks"})
        require(answer_object["space"] == "voxel_ijk_zero_based")
        predictions = object_value(answer_object["landmarks"])

        truth_object = object_value(truth)
        targets = object_value(truth_object["targets"])
        require(set(predictions) == set(targets))
        shape = finite_point3(truth_object["shape_ijk"])
        require(all(size > 0 for size in shape))
        linear = finite_matrix3(truth_object["linear_voxel_to_mm"])

        rows: dict[str, object] = {}
        counts = {status: 0 for status in ["observed", "out_of_fov", "absent"]}
        hallucinated = {status: 0 for status in ["out_of_fov", "absent"]}
        correct = dict(hallucinated)
        uncertain = dict(hallucinated)
        errors: dict[str, float] = {}
        extrapolation_errors: dict[str, float] = {}
        missed = 0
        confusion: dict[str, int] = {}
        for key, truth_target_value in targets.items():
            prediction = object_value(predictions[key], keys={"status", "ijk"})
            status = string_choice(
                prediction["status"], ("observed", "out_of_fov", "absent", "uncertain")
            )
            raw_point = prediction["ijk"]
            point = None if raw_point is None else finite_point3(raw_point)
            if status == "observed":
                if point is None:
                    raise ContractError
                require(all(-0.5 <= point[index] <= shape[index] - 0.5 for index in range(3)))
            if status in ("uncertain", "absent"):
                require(point is None)
            if status == "out_of_fov" and point is not None:
                require(
                    any(
                        point[index] < -0.5 or point[index] > shape[index] - 0.5
                        for index in range(3)
                    )
                )

            truth_target = object_value(truth_target_value)
            expected = string_choice(truth_target["status"], ("observed", "out_of_fov", "absent"))
            counts[expected] += 1
            ck = f"{expected}->{status}"
            confusion[ck] = confusion.get(ck, 0) + 1
            row: dict[str, object] = {
                "truth_status": expected,
                "predicted_status": status,
                "predicted_ijk": raw_point,
            }
            if expected == "observed":
                if status == "observed":
                    if point is None:
                        raise ContractError
                    truth_point = finite_point3(truth_target["ijk"])
                    errors[key] = physical_distance_mm(point, truth_point, linear)
                    row["error_mm"] = errors[key]
                else:
                    missed += 1
            else:
                hallucinated[expected] += int(status == "observed")
                correct[expected] += int(status == expected)
                uncertain[expected] += int(status == "uncertain")
                if expected == "out_of_fov" and status == "out_of_fov" and point is not None:
                    truth_point = finite_point3(truth_target["ijk"])
                    extrapolation_errors[key] = physical_distance_mm(point, truth_point, linear)
            rows[key] = row
        sdr = {str(t): sum(e <= t for e in errors.values()) for t in (5, 10, 20)}
        neg = counts["out_of_fov"] + counts["absent"]
        return {
            "contract_valid": True,
            "reward": int(sdr["5"] == counts["observed"] and sum(correct.values()) == neg),
            "requested": len(rows),
            "counts": counts,
            "hallucinated": hallucinated,
            "hallucination_rate": sum(hallucinated.values()) / neg if neg else None,
            "correct_rejections": correct,
            "uncertain_rejections": uncertain,
            "confusion": confusion,
            "missed_visible": missed,
            "localized_visible": len(errors),
            "success_counts_mm": sdr,
            "errors_mm": errors,
            "mean_localized_error_mm": sum(errors.values()) / len(errors) if errors else None,
            "extrapolation_errors_mm": extrapolation_errors,
            "rows": rows,
        }
    except (ContractError, TypeError, KeyError, ValueError, OverflowError):
        return {
            "reward": 0,
            "contract_valid": False,
            "invalid": "Require all keys with status and native ijk; observed inside, extrapolation outside, absent/uncertain null.",
        }
