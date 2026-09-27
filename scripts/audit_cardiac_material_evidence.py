"""Verify retained BR-029 source, public inputs and mechanics without fitting a model."""

import argparse
import json
from pathlib import Path

import meshio
import numpy as np
from audit_cardiac_contour_evidence import dump, read, sha
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates

RUN = Path("runs/br029-dynamic-heart")
PINS = {
    "docs/evidence/br029-dynamic-heart-integrity.json": "ac357b31f1ea261507f6edc4ca74c26d0926d9c1d4a1eb701b96e360e65b3524",
    "docs/evidence/br029-dynamic-heart-results.json": "cc1da908f5aa8172eedd18aabf72f6915ae398ff13ec06b71d3fe8d05f23deae",
    "docs/evidence/br029-dynamic-heart-tissue-results.json": "2401da9c2d3a637935153ccf6fe2c7f0db81c3c2c87c3f6bf8a2c0d2aa42d43b",
    "datasets/receipts/straus-patient01_healthy.json": "f57f95de623bfbeeed68743c15999f2a9668ed94c1ceff1ce194de940b401c27",
    "datasets/receipts/straus-patient04_lbbb.json": "285af282e27c948e2e7567bc37ce1ed965c464760e58be9c622b48cd85458f0a",
}


def edges(points, cells):
    return (points[cells[:, 1:]] - points[cells[:, 0], None]).swapaxes(-1, -2)


def summarize(values):
    return {
        "min": float(np.min(values)),
        "median": float(np.median(values)),
        "p05": float(np.quantile(values, 0.05)),
        "p95": float(np.quantile(values, 0.95)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
    }


def compare(actual, expected, path=""):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            compare(actual[key], expected[key], path + "/" + key)
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for index, value in enumerate(expected):
            compare(actual[index], value, path + "/" + str(index))
    elif isinstance(expected, (str, bool, int)) or expected is None:
        assert actual == expected, (path, actual, expected)
    else:
        assert abs(actual - expected) <= 1e-8, (path, actual, expected)


def analytic_checks():
    reference = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 4.0]])
    cells = np.array([[0, 1, 2, 3]])
    rotation = np.array(
        [[np.cos(0.81), -np.sin(0.81), 0], [np.sin(0.81), np.cos(0.81), 0], [0, 0, 1]]
    )
    affine = np.diag([0.8, 0.9, 1 / (0.8 * 0.9)])
    errors = {}
    for name, matrix, offset in [
        ("identity", np.eye(3), [0, 0, 0]),
        ("rigid", rotation, [13, -5, 8]),
        ("affine", affine, [0, 0, 0]),
    ]:
        transformed = reference @ matrix.T + offset
        gradient = edges(transformed, cells) @ np.linalg.inv(edges(reference, cells))
        c = gradient.swapaxes(-1, -2) @ gradient
        errors[name + "_gradient"] = float(np.max(abs(gradient - matrix)))
        errors[name + "_green"] = float(
            np.max(abs((c - np.eye(3)) / 2 - (matrix.T @ matrix - np.eye(3)) / 2))
        )
        errors[name + "_engineering"] = float(
            np.max(
                abs(np.sqrt(np.diagonal(c, axis1=-2, axis2=-1)) - np.linalg.norm(matrix, axis=0))
            )
        )
        errors[name + "_jacobian"] = float(
            np.max(abs(np.linalg.det(gradient) - np.linalg.det(matrix)))
        )
    errors["rotation_objectivity"] = float(
        np.max(abs((rotation @ affine).T @ (rotation @ affine) - affine.T @ affine))
    )
    assert max(errors.values()) < 1e-12
    return errors


def model_stats(data):
    points, cells, labels, directions = [
        data[k] for k in ["points", "tetra", "cell_labels", "directions"]
    ]
    d0 = edges(points[0], cells)
    inv = np.linalg.inv(d0)
    weights = np.linalg.det(d0) / 6
    assert np.all(weights > 0)
    valid = (labels > 0) & np.all(np.linalg.norm(directions, axis=-1) > 0.99, axis=0)
    engineering, green, jacobian, regional, regional_green, global_, tissue = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for frame in points:
        gradient = np.einsum("nij,njk->nik", edges(frame, cells), inv)
        c = np.einsum("nji,njk->nik", gradient, gradient)
        e = 0.5 * (c - np.eye(3))
        eng = np.stack(
            [
                np.sqrt(np.maximum(np.einsum("ni,nij,nj->n", axis, c, axis), 0)) - 1
                for axis in directions
            ],
            axis=-1,
        )
        gl = np.stack([np.einsum("ni,nij,nj->n", axis, e, axis) for axis in directions], axis=-1)
        j = np.linalg.det(gradient)
        assert np.isfinite(gradient).all() and np.isfinite(eng).all() and np.isfinite(j).all()
        eng[~valid], gl[~valid] = np.nan, np.nan
        engineering.append(eng)
        green.append(gl)
        jacobian.append(j)
        global_.append(np.average(eng[valid], axis=0, weights=weights[valid]))
        regional.append(
            [
                np.average(
                    eng[(labels == region) & valid],
                    axis=0,
                    weights=weights[(labels == region) & valid],
                )
                for region in range(1, 18)
            ]
        )
        regional_green.append(
            [
                np.average(
                    gl[(labels == region) & valid],
                    axis=0,
                    weights=weights[(labels == region) & valid],
                )
                for region in range(1, 18)
            ]
        )
        tissue.append(float(np.sum(weights * j) / 1000))
    engineering, green, jacobian, regional = map(
        np.asarray, [engineering, green, jacobian, regional]
    )
    assert np.nanmax(abs(engineering[0])) < 1e-10
    array_errors = {}
    for key, values in [
        ("engineering", engineering),
        ("green_lagrange_directional", green),
        ("jacobian", jacobian),
    ]:
        np.testing.assert_array_equal(np.isnan(values), np.isnan(data[key]))
        np.testing.assert_allclose(values.astype("float32"), data[key], atol=1e-7, rtol=1e-7)
        array_errors[key] = float(np.nanmax(abs(values.astype("float32") - data[key])))
    nodal = []
    for t in range(len(points)):
        fields = np.c_[np.nan_to_num(engineering[t]), np.nan_to_num(green[t]), jacobian[t]]
        field_weights = (
            weights[:, None] * np.c_[np.repeat(valid[:, None], 6, axis=1), np.ones(len(valid))]
        )
        numerator = np.zeros((len(points[0]), 7))
        denominator = np.zeros_like(numerator)
        for corner in range(4):
            np.add.at(numerator, cells[:, corner], fields * field_weights)
            np.add.at(denominator, cells[:, corner], field_weights)
        nodal.append(numerator / np.maximum(denominator, 1e-15))
    nodal = np.asarray(nodal).astype("float32")
    np.testing.assert_allclose(nodal, data["nodal_fields"], atol=1e-7, rtol=1e-7)
    array_errors["nodal_fields"] = float(np.max(abs(nodal - data["nodal_fields"])))
    peaks = np.stack(
        [regional[:, :, 0].min(0), regional[:, :, 1].min(0), regional[:, :, 2].max(0)], axis=1
    )
    peak_frames = (
        np.stack(
            [regional[:, :, 0].argmin(0), regional[:, :, 1].argmin(0), regional[:, :, 2].argmax(0)],
            axis=1,
        )
        + 1
    )
    stats = {
        "tissue_volume_ml": tissue,
        "tissue_volume_change_percent": (100 * (np.array(tissue) / tissue[0] - 1)).tolist(),
        "jacobian": summarize(jacobian),
        "inverted_tetrahedron_frames": int((jacobian <= 0).sum()),
        "reference_frame_strain_max_abs": float(np.nanmax(abs(engineering[0]))),
        "positive_label_cells_without_directional_basis": int(((labels > 0) & ~valid).sum()),
        "lv_volume_with_complete_directional_basis_fraction": float(
            weights[valid].sum() / weights[labels > 0].sum()
        ),
        "global_engineering_percent": (100 * np.asarray(global_)).tolist(),
        "regional_engineering_percent": (100 * regional).tolist(),
        "regional_green_lagrange_percent": (100 * np.asarray(regional_green)).tolist(),
        "regional_peak_percent": (100 * peaks).tolist(),
        "regional_peak_frames_1based": peak_frames.tolist(),
        "strain_directional_distributions_percent": [
            summarize(100 * engineering[:, valid, i]) for i in range(3)
        ],
        "cycle_endpoint_material_displacement_mm": summarize(
            np.linalg.norm(points[-1] - points[0], axis=1)
        ),
    }
    return stats, engineering, weights, array_errors


def audit(root, out):
    assert not out.exists(), "Use a fresh local destination"
    out.mkdir(parents=True)
    pins = dict(PINS)
    for name, digest in pins.items():
        assert sha(root / name) == digest, name
    integrity = read(root / "docs/evidence/br029-dynamic-heart-integrity.json")
    original = read(root / "docs/evidence/br029-dynamic-heart-results.json")
    tissue_original = read(root / "docs/evidence/br029-dynamic-heart-tissue-results.json")

    def pin(path, expected=None):
        value = sha(root / path)
        if expected is not None:
            assert value == expected, path
        pins[str(path)] = value

    for name, digest in integrity["code_sha256"].items():
        pin(Path(name), digest)
    for name, digest in integrity["final_results_sha256"].items():
        pin(RUN / name, digest)
    source_counts = {}
    for case in integrity["source_cases"]:
        folder = RUN / "source" / case["case"]
        pin(folder / "download-manifest.json", case["manifest_sha256"])
        manifest = read(root / folder / "download-manifest.json")
        assert manifest == read(root / f"datasets/receipts/straus-{case['case']}.json")["receipt"]
        for f in manifest["files"]:
            path = folder / f["path"]
            assert (root / path).stat().st_size == f["bytes"]
            pin(path, f["sha256"])
        assert len(manifest["files"]) == case["files"]
        assert sum(f["bytes"] for f in manifest["files"]) == case["bytes"]
        source_counts[case["case"]] = {"files": case["files"], "bytes": case["bytes"]}
    pin(RUN / "source/RefMeshP1.vtk", integrity["reference_mesh_sha256"])
    canonical = meshio.read(root / RUN / "source/RefMeshP1.vtk")
    public = RUN / "public-video"
    pin(public / "manifest.json", integrity["public_input"]["manifest_sha256"])
    manifest = read(root / public / "manifest.json")
    expected_files = {"initial_mesh.npz", "TASK.md", "geometry.json"} | {
        f"view_{v}/frame_{t:02d}.png" for v in range(4) for t in range(1, 31)
    }
    assert set(manifest) == expected_files and len(manifest) == 123
    assert {
        str(p.relative_to(root / public)) for p in (root / public).rglob("*") if p.is_file()
    } == expected_files | {"manifest.json"}
    for name, digest in manifest.items():
        pin(public / name, digest)
    initial = dict(np.load(root / public / "initial_mesh.npz", allow_pickle=False))
    geo = read(root / public / "geometry.json")
    cells, point_labels = initial["tetra"], initial["point_labels"]
    np.testing.assert_array_equal(cells, canonical.cells_dict["tetra"])
    np.testing.assert_array_equal(initial["labels"], canonical.cell_data["AHA"][0])
    np.testing.assert_array_equal(point_labels, canonical.point_data["AHA"])

    def normalize(a):
        return a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), 1e-12)

    radial = normalize(canonical.point_data["rads"][cells].mean(1))
    longitudinal = canonical.point_data["longs"][cells].mean(1)
    longitudinal -= np.einsum("ni,ni->n", longitudinal, radial)[:, None] * radial
    longitudinal = normalize(longitudinal)
    directions = np.array([longitudinal, normalize(np.cross(longitudinal, radial)), radial])
    np.testing.assert_array_equal(directions, initial["directions"])
    rotation, offset = (
        np.array(geo["canonical_to_native_rotation_rows"]),
        np.array(geo["canonical_to_native_offset"]),
    )
    assert abs(np.linalg.det(rotation) - 1) < 1e-12
    np.testing.assert_allclose(rotation @ rotation.T, np.eye(3), atol=1e-12, rtol=0)
    models = {name: RUN / "analysis-v2" / f"{name}.npz" for name in original["models"]}
    models["tissue_fit"] = RUN / "tissue-analysis-v3/tissue_fit.npz"
    raw_reference = {}
    for case, name in [
        ("patient01_healthy", "healthy_reference"),
        ("patient04_lbbb", "lbbb_reference"),
    ]:
        seq = []
        for t in range(30):
            m = meshio.read(root / RUN / "source" / case / "mesh" / f"usmesh{t:02d}.vtk")
            np.testing.assert_array_equal(m.cells_dict["tetra"], cells)
            seq.append(np.einsum("nj,kj->nk", m.points.astype(float) - offset, rotation))
        seq = np.asarray(seq)
        with np.load(root / models[name], allow_pickle=False) as data:
            np.testing.assert_allclose(seq, data["points"], atol=1e-9, rtol=0)
        raw_reference[name] = seq
    np.testing.assert_allclose(
        initial["points"], raw_reference["healthy_reference"][0], atol=1e-9, rtol=0
    )
    pose_error = np.linalg.norm(
        np.einsum("nj,jk->nk", canonical.points.astype(float), rotation)
        + offset
        - meshio.read(root / RUN / "source/patient01_healthy/mesh/usmesh00.vtk").points,
        axis=1,
    )
    assert abs(pose_error.max() - geo["pose_fit_max_error_mm"]) < 1e-10
    np.testing.assert_allclose(
        initial["points"][point_labels > 0].mean(0), geo["initial_center"], atol=1e-12, rtol=0
    )
    assert geo["image_size"] == 192 and geo["spacing_mm"] == 0.75 and geo["pixel_center"] == 95.5
    assert geo["physical_frame_duration_seconds"] is None
    seed_counts = []
    for plane in geo["planes"]:
        u, v, origin = [np.array(plane[k]) for k in ["u", "v", "origin"]]
        eligible = abs(np.einsum("nj,j->n", initial["points"] - origin, np.cross(u, v))) < 1.5
        pts = initial["points"][eligible]
        pixels = np.stack(
            [np.einsum("nj,j->n", pts - origin, axis) / 0.75 + 95.5 for axis in [u, v]], axis=1
        )
        seed_counts.append(int(np.all((pixels > 5) & (pixels < 186), axis=1).sum()))
    assert seed_counts == original["video_receipt"]["sample_points_per_plane"]
    # Reproduce only the retained source-to-input sampling; no motion estimation.
    grid = (np.arange(192) - 95.5) * 0.75
    vv, uu = np.meshgrid(grid, grid, indexing="ij")
    samples = []
    for plane in geo["planes"]:
        coordinates = (
            np.array(plane["origin"]) + uu[..., None] * plane["u"] + vv[..., None] * plane["v"]
        )
        native = (np.einsum("...j,jk->...k", coordinates, rotation) + offset) / geo[
            "source_spacing_mm"
        ]
        samples.append(np.moveaxis(native[..., ::-1], -1, 0))
    for t in range(30):
        header = root / RUN / "source/patient01_healthy/image" / f"usfrm{t:02d}.mhd"
        fields = dict(
            line.split(" = ", 1) for line in header.read_text().splitlines() if " = " in line
        )
        assert fields["ElementType"] == "MET_SHORT" and fields["BinaryDataByteOrderMSB"] == "False"
        assert fields["TransformMatrix"] == "1 0 0 0 1 0 0 0 1" and fields["Offset"] == "0 0 0"
        np.testing.assert_array_equal(
            np.array(fields["ElementSpacing"].split(), float), geo["source_spacing_mm"]
        )
        volume = np.fromfile(header.with_name(fields["ElementDataFile"]), dtype="<i2").reshape(
            tuple(np.array(fields["DimSize"].split(), int)[::-1])
        )
        if t == 0:
            assert (
                float(np.percentile(volume[volume > 0], 99.5))
                == geo["intensity_high_from_initial_volume"]
            )
        for view, coordinates in enumerate(samples):
            values = map_coordinates(
                volume.astype("float32"), coordinates, order=1, mode="constant", cval=0
            )
            pixels = np.clip(
                values / geo["intensity_high_from_initial_volume"] * 255, 0, 255
            ).astype("uint8")
            np.testing.assert_array_equal(
                pixels, np.asarray(Image.open(root / public / f"view_{view}/frame_{t + 1:02d}.png"))
            )
    receipts = {}
    for folder in ["video-fit-v1", "tissue-fit-v1", "tissue-fit-v2"]:
        path = RUN / folder
        pin(path / "receipt.json")
        receipt = read(root / path / "receipt.json")
        pin(path / "prediction.npz", receipt["prediction_sha256"])
        assert receipt["public_manifest_sha256"] == integrity["public_input"]["manifest_sha256"]
        receipts[folder] = receipt
    assert receipts["video-fit-v1"] == original["video_receipt"]
    assert receipts["tissue-fit-v2"] == tissue_original["receipt"]
    for folder, name in [("video-fit-v1", "video_affine"), ("tissue-fit-v2", "tissue_fit")]:
        with (
            np.load(root / RUN / folder / "prediction.npz", allow_pickle=False) as pred,
            np.load(root / models[name], allow_pickle=False) as analyzed,
        ):
            np.testing.assert_array_equal(pred["points"], analyzed["points"])
    first, repaired = receipts["tissue-fit-v1"], receipts["tissue-fit-v2"]
    assert (
        first["scales"] == repaired["scales"]
        and first["nonlinear_steps"] == repaired["nonlinear_steps"] == 3
    )
    assert (
        first["affine_prediction_sha256"]
        == repaired["affine_prediction_sha256"]
        == receipts["video-fit-v1"]["prediction_sha256"]
    )
    assert not first["all_cg_converged"] and repaired["all_cg_converged"]
    logs = [s for frame in repaired["iterations"] for s in frame]
    assert len(logs) == 87 and all(s["cg_info"] == 0 for s in logs)
    pin(RUN / "tissue-fit-v1/fit_tissue.executed.py", first["script_sha256"])
    replayed, field_errors, refstrain, refweights = {}, {}, None, None
    valid = (initial["labels"] > 0) & np.all(np.linalg.norm(directions, axis=-1) > 0.99, axis=0)
    for name, path in models.items():
        pin(path)
        data = dict(np.load(root / path, allow_pickle=False))
        np.testing.assert_array_equal(data["tetra"], cells)
        np.testing.assert_array_equal(data["directions"], directions)
        np.testing.assert_array_equal(data["cell_labels"], initial["labels"])
        s, eng, weights, errors = model_stats(data)
        old = tissue_original["model"] if name == "tissue_fit" else original["models"][name]
        if name == "healthy_reference":
            refstrain, refweights = eng, weights
        elif name != "lbbb_reference":
            comparison_reference = (
                refstrain.astype("float32") if name == "tissue_fit" else refstrain
            )
            strain_weights = weights if name == "tissue_fit" else refweights
            error = 100 * np.average(
                abs(eng[:, valid] - comparison_reference[:, valid]),
                axis=1,
                weights=strain_weights[valid],
            ).mean(0)
            source = replayed["healthy_reference"]
            peak = np.mean(
                abs(
                    np.array(s["regional_peak_percent"]) - np.array(source["regional_peak_percent"])
                ),
                axis=0,
            )
            timing = np.mean(
                abs(
                    np.array(s["regional_peak_frames_1based"])
                    - np.array(source["regional_peak_frames_1based"])
                ),
                axis=0,
            )
            motion = np.linalg.norm(data["points"] - raw_reference["healthy_reference"], axis=-1)
            s["comparison"] = {
                "material_point_rmse_mm": float(np.sqrt(np.mean(motion**2))),
                "material_displacement_error_mm": summarize(motion),
                "directional_engineering_mae_pp": error.tolist(),
                "regional_peak_mae_pp": peak.tolist(),
                "regional_peak_timing_mae_frames": timing.tolist(),
                "tissue_volume_curve_relative_error_percent": float(
                    100
                    * np.mean(abs(np.array(s["tissue_volume_ml"]) / source["tissue_volume_ml"] - 1))
                ),
            }
            s["gates"] = {
                "motion": s["comparison"]["material_point_rmse_mm"] <= 2,
                "strain": bool(np.all(error <= 5)),
                "regional_peak": bool(np.all(peak <= 5)),
                "inversions": s["inverted_tetrahedron_frames"] == 0,
            }
            s["pass"] = all(s["gates"].values())
        s["description"] = old["description"]
        compare(s, old, name)
        replayed[name], field_errors[name] = s, errors
        print(name + ": original mechanics and comparison fields reproduced", flush=True)
    export_path = RUN / "deliverables/tissue-model.npz"
    pin(export_path, integrity["exported_model"]["sha256"])
    pin(export_path.with_suffix(".json"))
    assert read(root / export_path.with_suffix(".json")) == integrity["exported_model"]
    exported = dict(np.load(root / export_path, allow_pickle=False))
    saved_tissue = dict(np.load(root / models["tissue_fit"], allow_pickle=False))
    assert json.loads(str(exported["metadata_json"])) == integrity["exported_model"]["metadata"]
    np.testing.assert_array_equal(exported["points_mm"], saved_tissue["points"].astype("float32"))
    np.testing.assert_array_equal(exported["tetra"], cells)
    np.testing.assert_array_equal(exported["cell_labels"], initial["labels"])
    np.testing.assert_array_equal(exported["reference_directions"], directions.astype("float32"))
    faces = np.concatenate(
        [cells[:, indices] for indices in [[1, 2, 3], [0, 3, 2], [0, 1, 3], [0, 2, 1]]]
    )
    _, indices, counts = np.unique(
        np.sort(faces, axis=1), axis=0, return_index=True, return_counts=True
    )
    np.testing.assert_array_equal(exported["boundary_triangles"], faces[indices[counts == 1]])
    np.testing.assert_array_equal(exported["engineering_strain"], saved_tissue["engineering"])
    np.testing.assert_array_equal(exported["J"], saved_tissue["jacobian"])
    inv = np.linalg.inv(edges(saved_tissue["points"][0], cells))
    export_errors = {"F": 0.0, "E_green_lagrange": 0.0}
    for t, points in enumerate(saved_tissue["points"]):
        gradient = np.einsum("nij,njk->nik", edges(points, cells), inv)
        green = 0.5 * (np.einsum("nji,njk->nik", gradient, gradient) - np.eye(3))
        for key, computed in [("F", gradient), ("E_green_lagrange", green)]:
            np.testing.assert_allclose(
                exported[key][t], computed.astype("float32"), atol=1e-7, rtol=1e-7
            )
            export_errors[key] = max(
                export_errors[key],
                float(np.max(abs(exported[key][t] - computed.astype("float32")))),
            )
    del exported, saved_tissue
    regional_motion = {}
    for name in ["video_affine", "tissue_fit"]:
        with np.load(root / models[name], allow_pickle=False) as data:
            squared_error = (
                np.linalg.norm(data["points"] - raw_reference["healthy_reference"], axis=-1) ** 2
            )
            regional_motion[name] = {
                "lv_labelled_vertices": float(np.sqrt(np.mean(squared_error[:, point_labels > 0]))),
                "rv_or_unassigned_vertices": float(
                    np.sqrt(np.mean(squared_error[:, point_labels == 0]))
                ),
            }
    compare(regional_motion, integrity["regional_material_point_rmse_mm"], "regional_motion")
    invalid = (initial["labels"] > 0) & ~valid
    assert np.where(invalid)[0].tolist() == [7722, 9345, 45413]
    for name in original["models"]:
        oldpath = RUN / "analysis-v1" / f"{name}.npz"
        pin(oldpath)
        with (
            np.load(root / oldpath, allow_pickle=False) as old,
            np.load(root / models[name], allow_pickle=False) as new,
        ):
            np.testing.assert_array_equal(old["points"], new["points"])
            np.testing.assert_array_equal(old["engineering"][0, invalid], -np.ones((3, 3)))
            assert np.isnan(new["engineering"][0, invalid]).all()
    oldpath = RUN / "tissue-analysis-v2/tissue_fit.npz"
    pin(oldpath)
    with (
        np.load(root / oldpath, allow_pickle=False) as old,
        np.load(root / models["tissue_fit"], allow_pickle=False) as new,
    ):
        np.testing.assert_array_equal(old["points"], new["points"])
        np.testing.assert_array_equal(old["engineering"][0, invalid], -np.ones((3, 3)))
        assert np.isnan(new["engineering"][0, invalid]).all()
    for t in [1, 17]:
        sheet = Image.new("RGB", (768, 232), "white")
        draw = ImageDraw.Draw(sheet)
        for view in range(4):
            sheet.paste(
                Image.open(root / public / f"view_{view}/frame_{t:02d}.png").convert("RGB"),
                (192 * view, 24),
            )
            draw.text((192 * view + 4, 6), geo["planes"][view]["name"], fill="black")
        draw.text(
            (4, 218),
            f"Actual public input, frame {t}; 0.75 mm/px; no contours or later reference meshes supplied",
            fill="black",
        )
        sheet.save(out / f"public-frame-{t}.png")
    dump(out / "replayed-results.json", replayed)
    result = {
        "schema": 1,
        "scope": "BR-029 source/input and saved-mechanics audit; no fitting, model trial or clinical adjudication",
        "source_pins": pins,
        "source_cases": source_counts,
        "reference_mesh_verified": True,
        "public_input": {
            "manifest_members": 123,
            "files_with_manifest": 124,
            "images": 120,
            "shape_hw": [192, 192],
            "spacing_mm": 0.75,
            "all_resampled_pixels_equal": True,
            "later_meshes_present": False,
            "material_seed_counts_per_plane": seed_counts,
        },
        "raw_reference_to_saved_coordinate_match_atol_mm": 1e-9,
        "initial_pose_max_error_mm": float(pose_error.max()),
        "frames": 30,
        "vertices": 11370,
        "tetrahedra": 47186,
        "directional_cells": {
            "aha_zero": int((initial["labels"] == 0).sum()),
            "aha_positive": int((initial["labels"] > 0).sum()),
            "valid": int(valid.sum()),
            "invalid_positive_zero_based_ids": np.where(invalid)[0].tolist(),
            "lv_volume_fraction_supported": replayed["healthy_reference"][
                "lv_volume_with_complete_directional_basis_fraction"
            ],
        },
        "analytic_checks": analytic_checks(),
        "replayed_conditions": list(replayed),
        "score_absolute_tolerance": 1e-8,
        "saved_float32_field_max_absolute_differences": field_errors,
        "retained_export": {
            "path": str(export_path),
            "sha256": pins[str(export_path)],
            "full_tensor_max_absolute_differences": export_errors,
            "interpretation": "Existing source-pinned material export checked; no new fitting or portable source distribution.",
        },
        "regional_motion_rmse_mm": regional_motion,
        "regional_point_counts": {
            "lv_labelled": int((point_labels > 0).sum()),
            "rv_or_unassigned": int((point_labels == 0).sum()),
        },
        "summary": {
            name: {
                k: v
                for k, v in s.items()
                if k
                in [
                    "comparison",
                    "jacobian",
                    "inverted_tetrahedron_frames",
                    "reference_frame_strain_max_abs",
                    "positive_label_cells_without_directional_basis",
                    "lv_volume_with_complete_directional_basis_fraction",
                    "gates",
                    "pass",
                ]
            }
            for name, s in replayed.items()
        },
        "numerical_recovery": {
            "initial_nonconverged_solves": sum(
                s["cg_info"] != 0 for frame in first["iterations"] for s in frame
            ),
            "solves_per_attempt": 87,
            "final_all_cg_converged": True,
            "max_recorded_relative_residual": max(
                s["normal_equation_relative_residual"] for s in logs
            ),
            "same_input_affine_initialization_and_regularization": True,
            "nonlinear_steps": 3,
            "limit": "Linear convergence does not prove full nonlinear stationarity.",
        },
        "superseded_axis_correction": "All seven analyzed point arrays are unchanged. Three positive-AHA cells had -100 percent reference-frame engineering strain in superseded outputs from undefined axes; corrected outputs mark them NaN and exclude them only from directional statistics.",
        "limits": [
            "One healthy simulation reconstructed; LBBB is reference playback only. No independent agent trial or observed patient strain.",
            "Healthy controls are endpoint-only comparisons: privileged known-correspondence fits and video fits have different information. Tissue method is development-informed.",
            "Source separation was reviewed in code, not enforced by an isolated provider runtime.",
            "Directional mechanics covers 31241 of 31244 positive-AHA tetrahedra; all 47186 remain in geometry/Jacobian checks.",
            "Physical frame duration is unknown. Tissue volume is not cavity volume or EF; this audit does not establish strain rate, flow, force balance or diagnosis.",
            "Source redistribution terms remain unresolved. Native and derived image/mesh assets stay local.",
        ],
    }
    dump(out / "audit.json", result)
    print(
        json.dumps(
            {
                "output": str(out),
                "source_files": 121,
                "public_images_reproduced": 120,
                "conditions_replayed": 7,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output)
