"""Synthetic witnesses for crop coverage, named points and retained result boundaries."""

import copy
import unittest

from test_native_trace import IDENTITY, compressed

from tb3_medical.explainers.native_trace import Manifest, project_payload


def payload():
    points = [
        {"name": "A", "status": "observed", "ijk": [1, 1, 1]},
        {"name": "B", "status": "observed", "ijk": [1, 1, 1.2]},
        {"name": "C", "status": "absent", "ijk": None},
    ]
    return {
        "shape": [4, 4, 4],
        "affine": copy.deepcopy(IDENTITY),
        "spacing": [1, 1, 1],
        "preview_shape": [2, 2, 2],
        "preview_indices": [[0, 3], [0, 3], [0, 3]],
        "preview_window_hu": [-200, 1400],
        "volume": compressed(range(8)),
        "names": [{"name": n, "definition": "Synthetic landmark"} for n in "ABC"],
        "poster": "synthetic",
        "attempt": "tiny-landmark",
        "points": points,
        "states": [
            {
                "id": "saved",
                "trace_step": 1,
                "label": "Submitted",
                "kind": "saved",
                "bounds": None,
                "center_ijk": None,
                "radius_mm": None,
                "axis": None,
                "levels": [],
                "points": copy.deepcopy(points),
                "delivered_step": None,
                "description": "Synthetic saved points",
            }
        ],
        "trace": [{"step": 1, "calls": ["write answer"], "output": "saved"}],
        "elapsed_seconds": 1,
        "steps_in_trace": 1,
        "evidence": "Retained account",
        "reference_points": [
            points[0],
            {"name": "B", "status": "out_of_fov", "ijk": [1, 1, 4]},
            points[2],
        ],
        "frozen": {
            "contract_valid": True,
            "reward": 0,
            "counts": {"observed": 1, "out_of_fov": 1, "absent": 1},
            "hallucinated": {"out_of_fov": 1, "absent": 0},
            "correct_rejections": {"out_of_fov": 0, "absent": 1},
            "success_counts_mm": {"5": 1, "10": 1, "20": 1},
            "errors_mm": {"A": 0},
        },
        "wrong_level": {
            "claimed_name": "B",
            "matched_name": "A",
            "claimed_ijk": [1, 1, 1.2],
            "matched_ijk": [1, 1, 1],
            "separation_mm": 0.2,
            "outside_name": "B",
            "outside_ijk": [1, 1, 4],
        },
        "private_extra": "never enters input",
    }


def manifest():
    return Manifest.model_validate(
        {
            "schema": 1,
            "id": "tiny",
            "entry_id": "tiny",
            "attempt": "tiny-landmark",
            "saved_state": "saved",
            "adapter": "ct-landmarks",
            "coordinates": "RAS-mm",
            "notice": "Synthetic witness",
            "recovery": "Synthetic fixture",
            "assets": [
                {"path": role, "sha256": "0" * 64, "bytes": 1, "role": role}
                for role in ("derived-display", "provenance", "license")
            ],
        }
    )


class LandmarkTraceTests(unittest.TestCase):
    def test_project_keeps_wrong_level_and_outside_truth_separate(self):
        source = payload()
        result = project_payload(source, manifest())
        self.assertNotIn("points", result["input"])
        self.assertNotIn("frozen", result["observed"])
        self.assertNotIn("private_extra", str(result))
        self.assertEqual(result["observed"]["points"][1]["status"], "observed")
        self.assertEqual(result["reference"]["points"][1]["status"], "out_of_fov")
        self.assertEqual(result["reference"]["frozen"]["reward"], 0)

    def test_preview_requires_endpoint_coverage_and_correct_byte_count(self):
        for update in (
            {"preview_indices": [[0, 2], [0, 3], [0, 3]]},
            {"volume": compressed(range(7))},
            {"preview_indices": [[3, 0], [0, 3], [0, 3]]},
        ):
            data = payload()
            data.update(update)
            with self.subTest(update=update), self.assertRaises(ValueError):
                project_payload(data, manifest())

    def test_saved_and_reference_point_roles_cannot_be_swapped(self):
        for key, index, change in (
            ("points", 1, {"ijk": [1, 1, 4]}),
            ("reference_points", 1, {"ijk": [1, 1, 2]}),
            ("points", 2, {"ijk": [1, 1, 1]}),
        ):
            data = payload()
            data[key][index].update(change)
            with self.subTest(key=key, change=change), self.assertRaises(ValueError):
                project_payload(data, manifest())

    def test_geometry_and_frozen_counts_cannot_drift(self):
        for key, value in (("spacing", [2, 1, 1]), ("attempt", "another-run")):
            data = payload()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                project_payload(data, manifest())
        data = payload()
        data["wrong_level"]["separation_mm"] = 2
        with self.assertRaisesRegex(ValueError, "separation"):
            project_payload(data, manifest())
        data = payload()
        data["frozen"]["counts"]["observed"] = 2
        with self.assertRaisesRegex(ValueError, "denominators"):
            project_payload(data, manifest())
        data = payload()
        data["frozen"]["hallucinated"]["out_of_fov"] = 0
        with self.assertRaisesRegex(ValueError, "false-observed"):
            project_payload(data, manifest())

    def test_inspection_bounds_and_saved_state_are_evidence_bound(self):
        for change in (
            {"bounds": [[0, 0, 0], [4, 4, 5]]},
            {"axis": 2, "levels": [0, 4]},
            {"trace_step": 2},
            {"center_ijk": [1, 1, 5]},
            {"radius_mm": -1},
            {"points": []},
        ):
            data = payload()
            data["states"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                project_payload(data, manifest())
