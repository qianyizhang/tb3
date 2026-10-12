"""Small synthetic MRI witnesses for native-grid, phase and endpoint boundaries."""

import copy
import unittest

from test_landmark_trace import manifest as base_manifest
from test_native_trace import IDENTITY, compressed

from tb3_medical.explainers.native_trace import project_payload


def fixture():
    visits, inventory, views, measurements, citations = [], [], [], [], []
    for index, name in enumerate(("V1", "V2")):
        affine = copy.deepcopy(IDENTITY)
        spacing = index + 1
        for axis in range(3):
            affine[axis][axis] = spacing
            affine[axis][3] = index * 100
        series = [
            {"id": f"S{index}{n}", "ordinal": n, "volume": compressed(range(8))} for n in range(2)
        ]
        visits.append(
            {
                "id": name,
                "day": index * 34,
                "shape": [4] * 3,
                "affine": affine,
                "spacing": [spacing] * 3,
                "preview_shape": [2] * 3,
                "preview_indices": [[0, 3]] * 3,
                "preview_window": [0, 100],
                "series": series,
                "poster": "synthetic",
            }
        )
        inventory.extend(
            {
                "visit": name,
                "id": s["id"],
                "description": "Synthetic 3D dynamic",
                "shape": [4] * 3,
                "affine": copy.deepcopy(affine),
                "phase_count": 1,
            }
            for s in series
        )
        views.append(
            {
                "visit": name,
                "series_id": series[1]["id"],
                "axis": 2,
                "levels": [1, 2],
                "bounds": [[0, 0, 0], [4, 4, 4]],
                "center_ijk": [1, 1, 1],
            }
        )
        measurements.append(
            {
                "visit": name,
                "series_id": series[1]["id"],
                "phase": 0,
                "fraction": 0.3,
                "bbox_min": [1] * 3,
                "bbox_max": [2] * 3,
                "spans_mm": [2 * spacing] * 3,
                "diameter_mm": 2 * spacing,
                "reported_mm": 2 * spacing,
                "method": "Synthetic voxel-edge box",
            }
        )
        citations.append(
            {
                "visit": name,
                "series_id": series[1]["id"],
                "phase": 0,
                "ijk": [1.5] * 3,
                "description": "Retained claim",
            }
        )
    data = {
        "attempt": "tiny-mri",
        "visits": visits,
        "inventory": inventory,
        "registered": False,
        "states": [
            {
                "id": "saved",
                "kind": "saved",
                "label": "Saved",
                "trace_step": 1,
                "views": views,
                "delivered_step": None,
                "description": "Synthetic state",
            }
        ],
        "measurements": measurements,
        "citations": citations,
        "summary": "Retained account",
        "impression": "Not clinically adjudicated",
        "forecast": {"direction": "smaller", "confidence": 0.43, "basis": "Retained claim"},
        "evidence": "Original report",
        "trace": [{"step": 1, "timestamp": "2026-01-01", "calls": ["save"], "output": "saved"}],
        "elapsed_seconds": 1,
        "steps_in_trace": 1,
        "reference": {
            "contract_pass": True,
            "reward": 1,
            "clinical_accuracy": "Not scored",
            "ftv_cc": [3, 5],
            "diameter_raw": [2.4, 2],
            "diameter_unit": "unresolved",
            "pcr": 0,
            "audit_diameters_mm": [2, 4],
            "audit_change_percent": 100,
            "forecast_baseline": "No forecast benefit established",
        },
        "private_extra": "excluded",
    }
    manifest = base_manifest().model_copy(
        update={"adapter": "longitudinal-mri", "attempt": "tiny-mri"}
    )
    return data, manifest


class MriTraceTests(unittest.TestCase):
    def test_independent_grids_and_reference_projection(self):
        data, manifest = fixture()
        result = project_payload(data, manifest)
        self.assertFalse(result["input"]["registered"])
        self.assertNotEqual(
            result["input"]["visits"][0]["affine"], result["input"]["visits"][1]["affine"]
        )
        self.assertNotIn("citations", result["input"])
        self.assertNotIn("reference", result["input"])
        self.assertNotIn("private_extra", result["input"])
        self.assertEqual(result["reference"]["audit_change_percent"], 100)

    def test_ordinal_is_not_citation_phase(self):
        data, manifest = fixture()
        data["citations"][0]["phase"] = 1
        with self.assertRaisesRegex(ValueError, "citation phase"):
            project_payload(data, manifest)

    def test_missing_native_endpoint_rejected(self):
        data, manifest = fixture()
        data["visits"][1]["preview_indices"][0] = [0, 2]
        with self.assertRaisesRegex(ValueError, "endpoints"):
            project_payload(data, manifest)

    def test_cross_visit_affine_and_unavailable_series_rejected(self):
        for mutation in ("affine", "series"):
            data, manifest = fixture()
            if mutation == "affine":
                data["inventory"][0]["affine"][0][3] += 2
            else:
                data["states"][0]["views"][0]["series_id"] = "absent"
            with self.assertRaises(ValueError):
                project_payload(data, manifest)

    def test_box_edges_not_centre_spans(self):
        data, manifest = fixture()
        data["measurements"][0]["spans_mm"] = [1] * 3
        with self.assertRaisesRegex(ValueError, "voxel-edge"):
            project_payload(data, manifest)

    def test_relabelled_registration_and_drifted_audit_rejected(self):
        for key in ("registration", "audit"):
            data, manifest = fixture()
            if key == "registration":
                data["registered"] = True
            else:
                data["reference"]["audit_change_percent"] = -5
            with self.assertRaises(ValueError):
                project_payload(data, manifest)

    def test_native_bounds_and_points_rejected(self):
        for key in ("levels", "bounds", "center_ijk"):
            data, manifest = fixture()
            view = data["states"][0]["views"][0]
            view[key] = {"levels": [4], "bounds": [[0, 0, 0], [4, 4, 5]], "center_ijk": [4, 1, 1]}[
                key
            ]
            with self.assertRaises(ValueError):
                project_payload(data, manifest)


if __name__ == "__main__":
    unittest.main()
