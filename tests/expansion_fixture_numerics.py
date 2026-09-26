"""Retained operation fixtures; run with the existing NumPy/trimesh environment."""

import json
import unittest
from itertools import pairwise
from pathlib import Path

import numpy as np
import trimesh

ASSETS = Path(__file__).resolve().parents[1] / "presentation/assets/teaching-fixtures"


def fixture(name):
    return json.loads((ASSETS / name / "fixture.json").read_text())


class OperationNumerics(unittest.TestCase):
    def test_topology_connectivity_and_lengths(self):
        data = fixture("topology-v1")
        self.assertEqual((len(data["edges"]), len(data["nodes"])), (7, 8))
        by_id = {edge["id"]: edge for edge in data["edges"]}
        route = [by_id[id] for id in data["selected_edges"]]
        for a, b in pairwise(route):
            self.assertEqual(a["target"], b["source"])
        for edge in data["edges"]:
            np.testing.assert_allclose(edge["points"][0], data["nodes"][edge["source"]])
            np.testing.assert_allclose(edge["points"][-1], data["nodes"][edge["target"]])
            self.assertAlmostEqual(
                edge["length_m"], np.linalg.norm(np.diff(edge["points"], axis=0), axis=1).sum()
            )

    def test_rigid_fit_is_checked_on_held_out_points(self):
        d = fixture("correspondence-v1")
        p = np.array(d["moving_points"])
        q = np.array(d["fixed_points"])
        a = p[:3] - p[:3].mean(0)
        b = q[:3] - q[:3].mean(0)
        u, _, vt = np.linalg.svd(a.T @ b)
        rotation = vt.T @ u.T
        if np.linalg.det(rotation) < 0:
            vt[-1] *= -1
            rotation = vt.T @ u.T
        translation = q[:3].mean(0) - p[:3].mean(0) @ rotation.T
        np.testing.assert_allclose(p[3:] @ rotation.T + translation, q[3:], atol=1e-12)
        np.testing.assert_allclose(
            np.array(d["fixed_from_moving"]) @ np.array(d["moving_from_fixed"]),
            np.eye(4),
            atol=1e-12,
        )
        self.assertGreater(np.max(abs(np.array(d["deformed_points"]) - q)), 1e-5)
        self.assertNotIn(d["target_absent_id"], d["point_ids"])

    def test_edit_domain_and_unchanged_control(self):
        d = np.load(ASSETS / "local-edit-v1/masks.npz")
        changed = d["supplied"] != d["repaired"]
        self.assertEqual(int(changed.sum()), 20)
        self.assertFalse(np.any(changed & ~d["editable"]))
        np.testing.assert_array_equal(d["unchanged_input"], d["unchanged_output"])

    def test_material_points_stay_on_same_surface(self):
        d = fixture("shape-material-v1")
        uv = np.array(d["marker_uv"])
        for frame in d["frames"]:
            for name in ["A", "B"]:
                points = np.array(frame[name])
                y = points[:, 1]
                x = (points[:, 0] - 0.12 * y) / (0.0385 * frame["phase"])
                z = points[:, 2] / (0.0315 * frame["phase"])
                np.testing.assert_allclose(
                    x * x + z * z, np.sin(0.55 + uv[:, 1] * (np.pi - 0.55)) ** 2, atol=1e-12
                )
        self.assertGreater(
            np.linalg.norm(np.array(d["frames"][-1]["A"]) - np.array(d["frames"][-1]["B"])), 0.015
        )

    def test_patch_cardinality_codes_and_coordinate_transfer(self):
        d = fixture("multiscale-v1")
        self.assertEqual(len({p["id"] for p in d["patches"]}), 12)
        self.assertTrue(all(p["class_code"] is None for p in d["patches"]))
        self.assertEqual(len(set(d["teaching_classes"])), 6)
        np.testing.assert_array_equal(
            np.array(d["tile_origin_level0"])
            + d["tile_downsample"] * np.array(d["example_local_point"]),
            d["example_level0_point"],
        )

    def test_longitudinal_outside_coverage_not_disappeared(self):
        d = fixture("longitudinal-v1")
        link = next(x for x in d["links"] if x["source"] == "c0")
        self.assertIsNone(link["target"])
        self.assertEqual(link["relation"], "outside-followup-coverage")
        self.assertEqual(len([x for x in d["links"] if x["source"] and x["target"]]), 2)

    def test_inverse_complex_data_consistency(self):
        a = np.load(ASSETS / "inverse-problems-v1/arrays.npz")
        d = fixture("inverse-problems-v1")
        self.assertEqual(a["sinogram"].shape[1], 90)
        self.assertLess(d["mri"]["sampled_complex_coefficient_max_error"], 1e-12)
        self.assertGreater(np.linalg.norm(np.abs(a["mri_zero_filled"]) - a["truth"]), 0.1)
        self.assertGreater(d["ct"]["relative_reprojection_l2"], 0)

    def test_glbs_are_finite_closed_meshes(self):
        files = list(ASSETS.glob("*/*.glb"))
        self.assertEqual(len(files), 4)
        for path in files:
            scene = trimesh.load(path, force="scene")
            for mesh in scene.geometry.values():
                self.assertTrue(np.isfinite(mesh.vertices).all())
                self.assertTrue(mesh.is_watertight)


if __name__ == "__main__":
    unittest.main()
