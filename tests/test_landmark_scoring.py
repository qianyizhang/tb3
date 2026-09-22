"""Contract regressions for the maintained CT and MRI landmark scorers."""

import json
import subprocess
import sys
import unittest

from tb3_medical import score_ct, score_mri

IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


class LandmarkScoringTests(unittest.TestCase):
    def test_mri_valid_answer_returns_physical_error_metrics(self):
        truth = {
            "points_ijk": {"target": [1, 2, 3]},
            "shape_ijk": [5, 5, 5],
            "linear_voxel_to_mm": IDENTITY,
            "tolerance_mm": 0.5,
        }
        answer = {
            "space": "voxel_ijk_zero_based",
            "landmarks": {"target": [1, 2, 3]},
        }

        self.assertEqual(
            score_mri.score(answer, truth),
            {
                "reward": 1,
                "accepted": {"target": True},
                "accepted_count": 1,
                "total": 1,
                "errors_mm": {"target": 0.0},
                "mean_mm": 0.0,
                "max_mm": 0.0,
                "contract_valid": True,
            },
        )

    def test_ct_valid_answer_separates_localization_and_rejections(self):
        truth = {
            "targets": {
                "seen": {"status": "observed", "ijk": [1, 1, 1]},
                "cropped": {"status": "out_of_fov", "ijk": [-1, 1, 1]},
                "missing": {"status": "absent", "ijk": None},
            },
            "shape_ijk": [3, 3, 3],
            "linear_voxel_to_mm": IDENTITY,
        }
        answer = {
            "space": "voxel_ijk_zero_based",
            "landmarks": {
                "seen": {"status": "observed", "ijk": [1, 1, 1]},
                "cropped": {"status": "out_of_fov", "ijk": [-1, 1, 1]},
                "missing": {"status": "absent", "ijk": None},
            },
        }

        result = score_ct.score(answer, truth)

        self.assertEqual(result["reward"], 1)
        self.assertEqual(result["counts"], {"observed": 1, "out_of_fov": 1, "absent": 1})
        self.assertEqual(result["errors_mm"], {"seen": 0.0})
        self.assertEqual(result["extrapolation_errors_mm"], {"cropped": 0.0})
        self.assertEqual(result["correct_rejections"], {"out_of_fov": 1, "absent": 1})

    def test_non_finite_and_boolean_coordinates_are_invalid(self):
        truth = {
            "points_ijk": {"target": [1, 2, 3]},
            "shape_ijk": [5, 5, 5],
            "linear_voxel_to_mm": IDENTITY,
            "tolerance_mm": 0.5,
        }
        for coordinate in (True, float("nan"), float("inf")):
            with self.subTest(coordinate=coordinate):
                result = score_mri.score(
                    {
                        "space": "voxel_ijk_zero_based",
                        "landmarks": {"target": [coordinate, 2, 3]},
                    },
                    truth,
                )
                self.assertEqual(result["contract_valid"], False)
                self.assertEqual(result["reward"], 0)

    def test_contract_validation_survives_optimized_python(self):
        script = """
import json
from tb3_medical import score_ct, score_mri

identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
mri = score_mri.score(
    {"space": "wrong", "landmarks": {"target": [1, 2, 3]}},
    {
        "points_ijk": {"target": [1, 2, 3]},
        "shape_ijk": [5, 5, 5],
        "linear_voxel_to_mm": identity,
        "tolerance_mm": 0.5,
    },
)
ct = score_ct.score(
    {
        "space": "voxel_ijk_zero_based",
        "landmarks": {"target": {"status": "out_of_fov", "ijk": [1, 1, 1]}},
    },
    {
        "targets": {"target": {"status": "out_of_fov", "ijk": [-1, 1, 1]}},
        "shape_ijk": [3, 3, 3],
        "linear_voxel_to_mm": identity,
    },
)
print(json.dumps([mri["contract_valid"], ct["contract_valid"]]))
"""
        completed = subprocess.run(
            [sys.executable, "-O", "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(json.loads(completed.stdout), [False, False])


if __name__ == "__main__":
    unittest.main()
