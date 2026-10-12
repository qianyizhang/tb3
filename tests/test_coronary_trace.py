"""Small witnesses for native coronary editing and CPR source/distance boundaries."""

import struct
import unittest

from test_landmark_trace import manifest as base_manifest
from test_native_trace import compressed

from tb3_medical.explainers.native_trace import project_payload


def floats(values):
    return compressed(struct.pack(f"<{len(values)}f", *values))


def fixture():
    route = [[2, 1, k] for k in (1, 2, 3)]
    cpr_sources = [
        v
        for point in route
        for offset in (-1, 0, 1)
        for v in (point[0], point[1] + offset, point[2])
    ]
    data = {
        "attempt": "tiny-coronary",
        "input": {
            "shape": [4, 4, 4],
            "affine": [[-1, 0, 0, 3], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            "spacing": [1, 1, 1],
            "preview_shape": [2, 2, 2],
            "preview_indices": [[0, 3]] * 3,
            "preview_window": [-200, 500],
            "volume": compressed(range(8)),
            "detail_origin": [1, 1, 1],
            "detail_shape": [2, 2, 2],
            "detail_volume": compressed(range(8)),
            "poster": "synthetic",
            "mask_indices": [21],
            "editable_indices": [21, 22],
            "start_ras": route[0],
            "end_ras": route[-1],
            "review_ras": [2, 1, 2],
            "private_extra": "not an input",
        },
        "observed": {
            "states": [
                {
                    "id": "saved",
                    "label": "Original saved output",
                    "kind": "saved",
                    "trace_step": 1,
                    "axis": 2,
                    "levels": [1, 2],
                    "bounds": [[0, 0, 0], [4, 4, 4]],
                    "center_ijk": [1, 1, 2],
                    "description": "Synthetic native witness",
                    "delivered_step": None,
                }
            ],
            "bridge_ijk": [[1, 1, 1], [1, 1, 2]],
            "added_indices": [22],
            "removed_indices": [],
            "centerline_ras": route,
            "cpr": {
                "shape": [1, 3, 3],
                "angles_deg": [0],
                "offsets_mm": [-1, 0, 1],
                "arc_mm": [0, 1.2, 2.4],
                "hu": floats(range(9)),
                "source_ras_mm": floats(cpr_sources),
            },
            "mesh": {
                "vertex_count": 3,
                "face_count": 1,
                "vertices": floats([2, 1, 1, 2, 2, 1, 1, 1, 1]),
                "faces": compressed(struct.pack("<3I", 0, 1, 2)),
            },
            "trace": [{"step": 1, "timestamp": None, "calls": ["save"], "output": "saved"}],
            "elapsed_seconds": 1,
            "steps_in_trace": 1,
            "evidence": "Original output",
        },
        "reference": {
            "reward": 0,
            "stages": {"repair": True, "cpr": False},
            "metrics": {"distance_error_mm": 0.4},
            "corrected_arc_mm": [0, 1, 2],
            "correction_stages": {"cpr": True},
            "correction_only_arc": True,
            "limits": "No anatomical adjudication",
        },
    }
    return data, base_manifest().model_copy(
        update={"adapter": "coronary-cpr", "attempt": "tiny-coronary"}
    )


class CoronaryTraceTests(unittest.TestCase):
    def test_original_wrong_arc_and_later_correction_remain_separate(self):
        data, manifest = fixture()
        data["observed"]["cpr"]["corrected_arc_mm"] = [0, 1, 2]
        result = project_payload(data, manifest)
        self.assertEqual(result["observed"]["cpr"]["arc_mm"], [0, 1.2, 2.4])
        self.assertEqual(result["reference"]["corrected_arc_mm"], [0, 1, 2])
        self.assertNotIn("private_extra", result["input"])
        self.assertNotIn("corrected_arc_mm", result["observed"]["cpr"])
        self.assertNotIn("corrected_arc_mm", result["observed"])

    def test_source_pixel_must_link_to_saved_route_and_offset(self):
        data, manifest = fixture()
        data["observed"]["cpr"]["source_ras_mm"] = floats([0] * 27)
        with self.assertRaisesRegex(ValueError, "pixel source"):
            project_payload(data, manifest)

    def test_edits_require_binary_region_membership_and_original_state(self):
        for added in ([23], [21], [22, 22]):
            data, manifest = fixture()
            data["observed"]["added_indices"] = added
            with self.assertRaises(ValueError):
                project_payload(data, manifest)

    def test_later_distance_axis_must_match_saved_polyline(self):
        data, manifest = fixture()
        data["reference"]["corrected_arc_mm"] = [0, 1.2, 2.4]
        with self.assertRaisesRegex(ValueError, "corrected arc"):
            project_payload(data, manifest)

    def test_cpr_buffer_shape_and_finite_values(self):
        for value in (floats([0] * 8), floats([float("nan")] * 9)):
            data, manifest = fixture()
            data["observed"]["cpr"]["hu"] = value
            with self.assertRaises(ValueError):
                project_payload(data, manifest)

    def test_saved_mesh_face_must_refer_to_existing_vertex(self):
        data, manifest = fixture()
        data["observed"]["mesh"]["faces"] = compressed(struct.pack("<3I", 0, 1, 3))
        with self.assertRaisesRegex(ValueError, "absent vertex"):
            project_payload(data, manifest)

    def test_native_crop_endpoints_and_logged_levels(self):
        for target in ("preview", "level", "route", "detail"):
            data, manifest = fixture()
            if target == "preview":
                data["input"]["preview_indices"][0] = [0, 2]
            elif target == "level":
                data["observed"]["states"][0]["levels"] = [4]
            elif target == "detail":
                data["input"]["detail_origin"] = [3, 1, 1]
            else:
                data["input"]["start_ras"] = [0, 0, 0]
            with self.assertRaises(ValueError):
                project_payload(data, manifest)
