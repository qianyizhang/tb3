"""Strict voxel-space contract; physical errors computed only by the verifier."""

import math


def score(answer, truth):
    try:
        assert isinstance(answer, dict) and set(answer) == {"space", "landmarks"}
        assert answer["space"] == "voxel_ijk_zero_based"
        pred = answer["landmarks"]
        assert isinstance(pred, dict) and set(pred) == set(truth["points_ijk"])
        errors = {}
        for name, gt in truth["points_ijk"].items():
            p = pred[name]
            assert isinstance(p, list) and len(p) == 3
            assert all(type(x) in (int, float) and math.isfinite(x) for x in p)
            assert all(-0.5 <= p[j] <= truth["shape_ijk"][j] - 0.5 for j in range(3))
            delta = [p[j] - gt[j] for j in range(3)]
            dmm = [
                sum(truth["linear_voxel_to_mm"][i][j] * delta[j] for j in range(3))
                for i in range(3)
            ]
            errors[name] = math.sqrt(sum(x * x for x in dmm))
        accepted = {k: e <= truth["tolerance_mm"] for k, e in errors.items()}
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
    except (AssertionError, TypeError, ValueError, KeyError):
        return {
            "reward": 0,
            "contract_valid": False,
            "invalid": "Expected tagged native zero-based voxel triples for exactly all named points",
        }
