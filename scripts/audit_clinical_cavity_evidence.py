"""Audit BR-034 source, frozen artifacts and retained replays; never execute a solver."""

import argparse
import hashlib
import json
import tarfile
from pathlib import Path

import numcodecs
import numpy as np
import zarr
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree

BASE = Path("runs/br034-pathological-echo")
RESULT = Path("docs/evidence/br034-clinical-adaptation-results.json")
PINS = {
    str(RESULT): "252f9c3da79e7117324eaef96c6551bd4d05ea3c100cf3548c84937a110d70bc",
    "datasets/receipts/echoxflow-archives.json": "7f888b105e72eb1fe1f96d596574f09545a40f0c0bb6092ea86e72d353b22e9a",
    str(
        BASE / "source/croissant.json"
    ): "2b0e80f83f8743f5babde82a3d8ded8ec4d607a1889a1b8b8cd204342116f83d",
    str(
        BASE / "source/readme.md"
    ): "8db63d1017df2fd37e287e61ea1ee4c0628fd6081de0f2b3b6989833e2b4bc61",
    str(
        BASE / "source/LICENSE"
    ): "e66c269d4819aaab34b49ef5220c4ddab6756f21bb5180761a4eb8561f2b7bbd",
    str(
        BASE / "review/data.json"
    ): "75f617738b949a5f2f87eaef8389cb6c57e0ebc6edf22b73ea29e34b97efcf88",
}
CASES = {
    "primary": ("", "primary_preparation", "primary_validation"),
    "patient": ("curation/ef48", "hidden_patient_preparation", "hidden_patient_validation"),
    "preserved": (
        "curation/preserved-v2",
        "preserved_patient_preparation",
        "preserved_patient_validation",
    ),
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def array(path):
    return np.asarray(zarr.open_array(str(path), mode="r")[:])


def compare(actual, expected, path=""):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            compare(actual[key], expected[key], path + "/" + key)
    elif isinstance(expected, (str, bool)) or expected is None:
        assert actual == expected, (path, actual, expected)
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for i, (a, b) in enumerate(zip(actual, expected, strict=True)):
            compare(a, b, path + f"/{i}")
    else:
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-8, err_msg=path)


def signed_volumes(points, faces):
    tri = points[:, faces]
    return (
        np.einsum("tmi,tmi->tm", tri[:, :, 0], np.cross(tri[:, :, 1], tri[:, :, 2])).sum(1) / 6000
    )


def samples(points, faces):
    tri = points[faces]
    return np.concatenate(
        [
            points,
            tri.mean(1),
            (tri[:, 0] + tri[:, 1]) / 2,
            (tri[:, 1] + tri[:, 2]) / 2,
            (tri[:, 0] + tri[:, 2]) / 2,
        ]
    )


def distances(points, faces, reference, reference_faces):
    a, b = samples(points, faces), samples(reference, reference_faces)
    d = np.r_[cKDTree(b).query(a)[0], cKDTree(a).query(b)[0]]
    return float(d.mean()), float(np.percentile(d, 95))


def closed_oriented(faces):
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    _, counts = np.unique(np.sort(edges, axis=1), axis=0, return_counts=True)
    assert np.all(counts == 2) and len(np.unique(edges, axis=0)) == len(edges)


def category(ef):
    return (
        "severely_reduced"
        if ef < 30
        else "moderately_reduced"
        if ef <= 40
        else "mildly_reduced_or_borderline"
        if ef < 54
        else "preserved"
    )


def grade(answer, reference):
    data = dict(np.load(answer / "prediction.npz", allow_pickle=False))
    p, f, gp, gf = (
        data["points"].astype(float),
        data["faces"],
        reference["points"],
        reference["faces"],
    )
    assert p.ndim == 3 and p.shape[0] == len(gp) and p.shape[2] == 3 and p.shape[1] <= 10000
    assert (
        f.ndim == 2 and f.shape[1] == 3 and len(f) <= 20000 and np.issubdtype(f.dtype, np.integer)
    )
    assert np.isfinite(p).all() and f.min() >= 0 and f.max() < p.shape[1]
    closed_oriented(f)
    v, gv = abs(signed_volumes(p, f)), abs(signed_volumes(gp, gf))
    assert min(v) > 1
    ef, gef = (float(100 * (1 - a.min() / a.max())) for a in [v, gv])
    summary = read(answer / "summary.json")
    np.testing.assert_allclose(summary["volume_ml"], v, atol=0.01)
    assert abs(summary["ef_pct"] - ef) < 0.05
    assert (answer / "solve.py").is_file() and (answer / "method.md").is_file()
    ds = np.array([distances(a, f, b, gf) for a, b in zip(p, gp, strict=True)])
    declared = summary.get("diagnosis", {}).get("functional_class")
    result = {
        "format_valid": True,
        "surface_mean_mm": float(ds[:, 0].mean()),
        "surface_p95_mm": float(ds[:, 1].max()),
        "per_frame_surface_mean_mm": ds[:, 0].tolist(),
        "per_frame_surface_p95_mm": ds[:, 1].tolist(),
        "volume_ml": v.tolist(),
        "reference_volume_ml": gv.tolist(),
        "ef_pct": ef,
        "reference_ef_pct": gef,
        "ef_error_pp": abs(ef - gef),
        "mean_volume_error_pct": float(np.mean(abs(v - gv) / gv * 100)),
        "edv_error_pct": float(abs(v.max() - gv.max()) / gv.max() * 100),
        "esv_error_pct": float(abs(v.min() - gv.min()) / gv.min() * 100),
        "declared_functional_class": declared,
        "reference_functional_class": category(gef),
        "diagnostic_class_matches": declared == category(gef),
        "diagnosis_consistent_with_own_ef": declared == category(ef),
    }
    gates = {
        "surface_mean": result["surface_mean_mm"] <= 3,
        "surface_p95": result["surface_p95_mm"] <= 6,
        "ef": result["ef_error_pp"] <= 8,
        "edv": result["edv_error_pct"] <= 15,
        "esv": result["esv_error_pct"] <= 15,
    }
    result.update(
        gates=gates, reward=int(all(gates.values()) and result["diagnostic_class_matches"])
    )
    return data, result


def sector_indices(points_mm, geometry, native_shape):
    x, y, z = np.moveaxis(points_mm / 1000, -1, 0)
    radius = np.sqrt(x**2 + y**2 + z**2)
    azimuth = np.arctan2(x, np.sqrt(y**2 + z**2))
    elevation = np.arctan2(y, z)
    return np.array(
        [
            (elevation / geometry["ElevationWidth"] + 0.5) * (native_shape[1] - 1),
            (azimuth / geometry["Width"] + 0.5) * (native_shape[2] - 1),
            (radius - geometry["DepthStart"])
            / (geometry["DepthEnd"] - geometry["DepthStart"])
            * (native_shape[3] - 1),
        ]
    )


def sections(points, faces, axis, value, origin, axes):
    tri = points[faces]
    d = tri[:, :, axis] - value
    keep = (d.min(1) < 0) & (d.max(1) > 0)
    tri, d = tri[keep], d[keep]
    out = np.zeros((len(tri), 2, 3))
    count = np.zeros(len(tri), dtype=int)
    for a, b in [(0, 1), (1, 2), (2, 0)]:
        ids = np.flatnonzero((d[:, a] < 0) != (d[:, b] < 0))
        alpha = d[ids, a] / (d[ids, a] - d[ids, b])
        out[ids, count[ids]] = tri[ids, a] + alpha[:, None] * (tri[ids, b] - tri[ids, a])
        count[ids] += 1
    return (out[count == 2] - origin)[:, :, axes]


def audit(root, out):
    out.mkdir(parents=True, exist_ok=False)
    b = root / BASE
    pins, verified = {}, set()

    def pin(path, expected=None):
        relative = path.relative_to(root) if path.is_absolute() else path
        key = relative.as_posix()
        actual = sha(root / relative)
        assert expected is None or actual == expected, key
        assert key not in pins or pins[key] == actual, key
        pins[key] = actual
        if expected is not None:
            verified.add(key)

    for name, digest in PINS.items():
        pin(Path(name), digest)
    old = read(root / RESULT)
    for name, digest in old["code_sha256"].items():
        pin(Path(name), digest)
    freeze = read(b / "freeze.json")
    pin(b / "freeze.json", old["freeze_sha256"])
    for name, digest in freeze["files"].items():
        pin(root / freeze["task_path"] / name, digest)
    for name, digest in {
        "evaluation-freeze.json": old["evaluation_freeze_sha256"],
        **old["preserved_control_freezes"],
    }.items():
        pin(b / name, digest)
        for f, h in read(b / name)["files"].items():
            pin(b / f, h)
    catalog = read(b / "source/croissant.json")
    rows = next(rs["data"] for rs in catalog["recordSet"] if rs["@id"] == "arrays")
    assert catalog["license"]["name"] == "CC-BY-NC-SA-4.0"
    cases, references, inputs, calendars = {}, {}, {}, {}
    for key, (subdir, preparation_key, validation_key) in CASES.items():
        base = b / subdir
        prep, validation = read(base / "preparation.json"), read(base / "validation.json")
        compare(prep, old[preparation_key])
        compare(validation, old[validation_key])
        source = b / "source" / prep["exam"]
        folder = source / "exams" / prep["exam"] / (prep["recording"] + ".zarr")
        archive = read(source / "archive-receipt.json")
        expected = prep["source_archive_sha256"]
        assert archive["sha256"] == archive["source"]["lfs"]["oid"] == expected
        archive_path = source.with_suffix(".tar")
        pin(archive_path, expected)
        assert archive_path.stat().st_size == archive["bytes"]
        matched = set()
        with tarfile.open(archive_path) as tar:
            for member in tar:
                if member.isfile() and prep["recording"] + ".zarr" in Path(member.name).parts:
                    assert (
                        not Path(member.name).is_absolute() and ".." not in Path(member.name).parts
                    )
                    stream = tar.extractfile(member)
                    assert stream is not None
                    digest = hashlib.file_digest(stream, "sha256").hexdigest()
                    path = source / member.name
                    pin(path, digest)
                    assert path.stat().st_size == member.size
                    matched.add(path)
        assert matched == {p for p in folder.rglob("*") if p.is_file()}
        manifest = read(folder / ".zattrs")["recording_manifest"]
        geometry = manifest["sectors"][0]["geometry"]
        compare(geometry, prep["source_geometry"])
        native_path = folder / "data/3d_brightness_mode"
        native = array(native_path)
        za = read(native_path / ".zarray")
        assert za["shape"] == za["chunks"]
        decoded = numcodecs.get_codec(za["compressor"]).decode(
            (native_path / "0.0.0.0").read_bytes()
        )
        direct = np.frombuffer(decoded, dtype=za["dtype"]).reshape(za["shape"], order=za["order"])
        np.testing.assert_array_equal(native, direct)
        native_hash = hashlib.sha256(native.tobytes()).hexdigest()
        assert native_hash == prep["native_array_sha256"]
        row = next(
            r
            for r in rows
            if r["arrays/recording_id"] == prep["recording"]
            and r["arrays/array_path"] == "data/3d_brightness_mode"
        )
        assert row["arrays/shape"] == list(native.shape) == prep["native_shape"]
        assert row["arrays/data_sha256"] == validation["publisher_array_digest"]
        assert native_hash == validation["decoded_c_order_digest"] != row["arrays/data_sha256"]
        raw_times = array(folder / "timestamps/3d_brightness_mode")
        times = raw_times.copy()
        origin = manifest["metadata"]["time_reference"]["origin_s"]
        if times.min() >= origin - 1e-6:
            times -= origin
        reference_times = array(folder / "timestamps/3d_left_ventricle_mesh")
        ids = abs(times[:, None] - reference_times[None, :]).argmin(0)
        assert (
            np.all(np.diff(ids) == 1)
            and ids.tolist() == prep["selected_native_frame_indices_zero_based"]
        )
        compare(raw_times[ids], prep["native_timestamps_s"])
        compare(times[ids], prep["relative_native_timestamps_s"])
        compare(reference_times, prep["reference_timestamps_s"])
        timestamp_error = float(abs(times[ids] - reference_times).max())
        compare(timestamp_error, prep["maximum_time_alignment_error_s"])
        assert timestamp_error < 0.005
        mesh = folder / "data/3d_left_ventricle_mesh"
        points = array(mesh / "point_values").astype(float) * 1000
        faces = array(mesh / "face_values")
        po, fo = array(mesh / "point_frame_offsets"), array(mesh / "face_frame_offsets")
        pp = np.stack([points[po[i] : po[i + 1]] for i in range(len(po) - 1)])
        ff = [faces[fo[i] : fo[i + 1]] for i in range(len(fo) - 1)]
        assert all(np.array_equal(ff[0], f) for f in ff)
        transformed = pp[:, :, [0, 2, 1]] * [-1.0, 1.0, 1.0]
        center = transformed[0].mean(0)
        eigenvectors = np.linalg.eigh(np.cov((transformed[0] - center).T))[1]
        depth = eigenvectors[:, -1]
        if depth[2] < 0:
            depth = -depth
        transverse = eigenvectors[:, -2]
        basis = np.stack([transverse, np.cross(depth, transverse), depth], axis=1)
        np.testing.assert_allclose(basis, prep["local_to_source_basis"], rtol=0, atol=1e-12)
        np.testing.assert_allclose(center, prep["local_to_source_center_mm"], rtol=0, atol=1e-12)
        local_points = np.einsum("tni,ij->tnj", transformed - center, basis)
        local_faces = ff[0]
        if signed_volumes(local_points[:1], local_faces)[0] < 0:
            local_faces = local_faces[:, [0, 2, 1]]
        reference = dict(np.load(base / "reference.npz", allow_pickle=False))
        np.testing.assert_allclose(reference["points"], local_points, rtol=0, atol=1e-11)
        np.testing.assert_array_equal(reference["faces"], local_faces)
        closed_oriented(local_faces)
        volume = abs(signed_volumes(local_points, local_faces))
        compare(volume, prep["reference_volume_ml"])
        assert volume.argmax() == 0
        initial = np.load(base / "input/initial_mesh.npz", allow_pickle=False)
        np.testing.assert_array_equal(initial["points"], reference["points"][0])
        np.testing.assert_array_equal(initial["faces"], reference["faces"])
        lo = np.floor(local_points[0].min(0) - 18)
        hi = np.ceil(local_points[0].max(0) + 18)
        shape = (hi - lo).astype(int) + 1
        cal = read(base / "input/geometry.json")
        np.testing.assert_array_equal(cal["origin_xyz_mm"], lo)
        np.testing.assert_array_equal(cal["spacing_xyz_mm"], [1, 1, 1])
        compare(cal["timestamps_s"], times[ids] - times[ids[0]])
        assert cal["initial_mesh_frame"] == 0
        grid = np.load(base / "input/volumes.npy", mmap_mode="r", allow_pickle=False)
        assert list(grid.shape) == cal["shape_tzyx"] == prep["input_shape"]
        assert tuple(grid.shape[1:]) == tuple(shape[::-1])
        zz, yy, xx = np.meshgrid(*(np.arange(shape[i]) + lo[i] for i in [2, 1, 0]), indexing="ij")
        world = np.einsum("...j,ij->...i", np.stack([xx, yy, zz], -1), basis) + center
        indices = sector_indices(world, geometry, native.shape)
        ci = np.rint(-lo).astype(int)
        for t, index in enumerate(ids):
            sample = map_coordinates(
                native[index], indices, order=1, mode="constant", cval=0
            ).astype("uint8")
            np.testing.assert_array_equal(sample, grid[t])
            for k, im in enumerate(
                [grid[t, :, ci[1], :], grid[t, :, :, ci[0]], grid[t, ci[2], :, :]]
            ):
                preview = base / "input/previews" / f"plane{k + 1}_{t:03d}.png"
                np.testing.assert_array_equal(np.asarray(Image.open(preview).convert("L")), im)
        actual_inputs = {
            str(p.relative_to(base / "input")): sha(p)
            for p in (base / "input").rglob("*")
            if p.is_file()
        }
        assert len(actual_inputs) == 3 * len(ids) + 3 + (key == "primary")
        if key == "primary":
            assert actual_inputs == {
                p.removeprefix("environment/data/"): h
                for p, h in freeze["files"].items()
                if p.startswith("environment/data/")
            }
        ref_indices = sector_indices(transformed, geometry, native.shape)
        outside = (
            (ref_indices < 0) | (ref_indices > (np.array(native.shape[1:]) - 1)[:, None, None])
        ).any(0)
        sector = next(
            r
            for r in old["screen_sector_coverage"]
            if r["recording"] == prep["recording"] + ".zarr"
        )
        compare(float(outside.mean()), sector["outside"])
        compare(float(outside[0].mean()), sector["initial_outside"])
        cases[key] = {
            "source_archive_sha256": expected,
            "source_members_equal_archive": len(matched),
            "native_shape": list(native.shape),
            "input_shape": list(grid.shape),
            "selected_frame_indices_zero_based": ids.tolist(),
            "public_file_count": len(actual_inputs),
            "all_prepared_voxels_and_previews_equal": True,
            "maximum_timestamp_error_s": timestamp_error,
            "reference_vertices": local_points.shape[1],
            "reference_faces": len(local_faces),
            "reference_volume_ml": volume.tolist(),
            "reference_ef_pct": float(100 * (1 - volume.min() / volume.max())),
            "initial_reference_exactly_supplied": True,
            "outside_sector_overall_fraction": float(outside.mean()),
            "outside_sector_initial_fraction": float(outside[0].mean()),
            "publisher_array_digest": row["arrays/data_sha256"],
            "decoded_c_order_digest": native_hash,
            "array_hash_convention_unresolved": True,
        }
        references[key], inputs[key], calendars[key] = reference, base / "input", cal
        print(
            f"{key}: native/archive, {len(ids)} resampled frames and initial/private references verified",
            flush=True,
        )
        del native, decoded, direct, world, indices, grid

    grades, predictions = {}, {}
    trial = next(t for t in old["trials"] if t["phase"] == "sol-xhigh")
    answer = (root / trial["result_path"]).parent / "artifacts/app/answer"
    for t in old["trials"]:
        pin(root / t["result_path"], t["result_sha256"])
        a = (root / t["result_path"]).parent / "artifacts/app/answer"
        for name, digest in t["artifacts"].items():
            pin(a / name, digest)
        assert (
            t["task_checksum"] == "157ec8c44a64edbbe84ac0c10597d9291af6e11a7826147a3fd8457c657c2a0d"
        )
        if t["phase"] == "nop":
            assert t["grade"]["reward"] == 0 and not (a / "prediction.npz").exists()
        else:
            data, value = grade(a, references["primary"])
            compare(value, t["grade"])
            predictions[t["phase"]], grades[t["phase"]] = data, value
        for s in t.get("session_files", []):
            pin(root / s["path"], s["sha256"])
    static_data, static_grade = grade(b / "static-control", references["primary"])
    np.testing.assert_array_equal(
        static_data["points"],
        np.repeat(
            references["primary"]["points"][:1], len(references["primary"]["points"]), axis=0
        ),
    )
    np.testing.assert_array_equal(static_data["faces"], references["primary"]["faces"])
    for path in (b / "static-control").rglob("*"):
        if path.is_file():
            pin(path)
    compare(static_grade, old["controls"]["static_initialization"])
    compare(grades["oracle"], old["controls"]["reference"])
    grades["static_initialization"] = static_grade
    predictions["primary"] = predictions["sol-xhigh"]
    for key in ["points", "faces"]:
        np.testing.assert_array_equal(
            predictions["primary"][key][0] if key == "points" else predictions["primary"][key],
            references["primary"][key][0] if key == "points" else references["primary"][key],
        )
    replay_results = {}
    original = predictions["primary"]
    for kind, r in old["replays"].items():
        replay = b / "replays" / ("original-v2" if kind == "original" else kind)
        compare(read(replay / "receipt.json"), r)
        inp = (
            inputs[kind]
            if kind in ["patient", "preserved"]
            else replay / "input"
            if kind in ["static", "shift"]
            else inputs["primary"]
        )
        for name, digest in r["submitted_files_sha256"].items():
            pin(answer / name, digest)
        for name, digest in r["input_files_sha256"].items():
            pin(inp / name, digest)
        for name, digest in r["output_files_sha256"].items():
            pin(replay / "output" / name, digest)
        assert r["exit_code"] == 0 and r["timeout"] is False and r["seconds"] <= 300
        data = dict(np.load(replay / "output/prediction.npz", allow_pickle=False))
        v = abs(signed_volumes(data["points"], data["faces"]))
        compare(v, r["volume_ml"])
        motion = float(
            np.sqrt(np.mean(np.sum((data["points"] - data["points"][:1]) ** 2, axis=-1)))
        )
        compare(motion, r["motion_rms_mm"])
        if kind in ["original", "patient", "preserved"]:
            for name in ["prediction.npz", "summary.json", "solve.py", "method.md"]:
                expected = (
                    sha(replay / "output" / name)
                    if (replay / "output" / name).exists()
                    else sha(answer / name)
                )
                pin(replay / "grading" / name, expected)
            _, value = grade(
                replay / "grading", references[kind if kind != "original" else "primary"]
            )
            compare(value, r["grade"])
            grades[kind] = value
        if kind in ["original", "shift"]:
            points = data["points"] if kind == "original" else np.roll(data["points"], -5, axis=0)
            np.testing.assert_array_equal(points, original["points"])
            np.testing.assert_array_equal(data["faces"], original["faces"])
            assert (
                r["original_coordinate_max_abs_mm"]
                == r["original_volume_mae_ml"]
                == r["original_surface_mean_mm"]
                == 0
            )
        if kind in ["static", "shift"]:
            grid = np.load(inp / "volumes.npy", mmap_mode="r")
            baseline = np.load(inputs["primary"] / "volumes.npy", mmap_mode="r")
            expected = (
                np.repeat(baseline[:1], len(baseline), axis=0)
                if kind == "static"
                else np.roll(baseline, 5, axis=0)
            )
            np.testing.assert_array_equal(grid, expected)
            assert read(inp / "geometry.json")["initial_mesh_frame"] == (
                0 if kind == "static" else 5
            )
            if kind == "static":
                np.testing.assert_array_equal(
                    data["points"],
                    np.repeat(original["points"][:1], len(original["points"]), axis=0),
                )
                assert r["ef_pct"] == r["motion_rms_mm"] == 0
            assert r["input_response_pass"] is True
        predictions[kind] = data
        replay_results[kind] = {k: v for k, v in r.items() if not isinstance(v, (dict, list))}
    infrastructure = read(b / "replays/original/receipt.json")
    compare(infrastructure, old["earlier_replay_infrastructure"])
    assert infrastructure["exit_code"] == 125 and not infrastructure["output_files_sha256"]
    trajectory_path = (root / trial["result_path"]).parent / "agent/trajectory.json"
    pin(trajectory_path, "c28a1195b9a1386073dcabe1816e24c247b84ce469853092612072c87f0cb8a2")
    trace = read(trajectory_path)
    assert trace["agent"]["model_name"] == "gpt-5.6-sol"
    assert trial["runtime_contexts"] == [{"model": "gpt-5.6-sol", "effort": "xhigh"}]
    compare(
        read(answer / "pre_model_assessment.json"), old["author_review"]["pre_model_assessment"]
    )

    review = read(b / "review/data.json")
    sections_checked = 0
    for case in review["cases"]:
        key = case["key"]
        reference = references[key if key in references else "primary"].copy()
        if key == "static":
            reference["points"] = np.repeat(
                reference["points"][:1], len(reference["points"]), axis=0
            )
        elif key == "shift":
            reference["points"] = np.roll(reference["points"], 5, axis=0)
        cal = calendars[key if key in calendars else "primary"]
        lo = np.array(cal["origin_xyz_mm"])
        index = np.rint(-lo).astype(int)
        for model, data in zip(case["models"], [predictions[key], reference], strict=True):
            np.testing.assert_array_equal(np.round(data["points"], 4), model["points"])
            np.testing.assert_array_equal(data["faces"], model["faces"])
            compare(abs(signed_volumes(data["points"], data["faces"])), model["volumes"])
            for j, (axis, axes) in enumerate([(1, [0, 2]), (0, [1, 2]), (2, [0, 1])]):
                for t, points in enumerate(data["points"]):
                    lines = sections(points, data["faces"], axis, lo[axis] + index[axis], lo, axes)
                    assert np.round(lines, 3).tolist() == model["sections"][j][t]
                    sections_checked += 1
        if key not in CASES:
            continue
        t = int(np.argmin(case["models"][1]["volumes"]))
        sheet = Image.new("RGB", (900, 992), "#101820")
        draw = ImageDraw.Draw(sheet)
        draw.text(
            (8, 8),
            f"BR-034 {key} | reference ES frame {t} (zero based) | 1 mm source grid",
            fill="white",
        )
        draw.text(
            (8, 25),
            "Cyan solid: saved solver | gold dashed: private clinical reference | no material truth",
            fill="white",
        )
        for j in range(3):
            path = inputs[key] / "previews" / f"plane{j + 1}_{t:03d}.png"
            original_image = Image.open(path).convert("RGB")
            for column in range(3):
                panel = original_image.copy()
                pd = ImageDraw.Draw(panel)
                if column > 0:
                    lines = case["models"][column - 1]["sections"][j][t]
                    for a, c in lines:
                        a, c = np.asarray(a), np.asarray(c)
                        if column == 1:
                            pd.line([tuple(a), tuple(c)], fill="#3de9d6", width=1)
                        else:
                            count = max(1, int(np.ceil(np.linalg.norm(c - a) / 2)))
                            for n in range(0, count, 2):
                                pd.line(
                                    [
                                        tuple(a + (c - a) * n / count),
                                        tuple(a + (c - a) * min(n + 1, count) / count),
                                    ],
                                    fill="#ffcc66",
                                    width=1,
                                )
                panel = panel.resize((panel.width * 2, panel.height * 2), Image.Resampling.NEAREST)
                sheet.paste(panel, (column * 300 + (300 - panel.width) // 2, 52 + j * 310))
                draw.text(
                    (column * 300 + 8, 52 + j * 310 + 280),
                    f"Plane {j + 1}: "
                    + ["source only", "solver section", "reference reveal"][column],
                    fill="white",
                )
        sheet.save(out / f"{key}-reference-es.png")

    report = {
        "schema": 1,
        "scope": "Source and saved-output BR-034 audit; no source authoring, flow fitting, solver/model run, clinical adjudication or score replacement",
        "source_pins": pins,
        "hash_coverage": {
            "checked_against_existing_pins_or_verified_archive_members": len(verified),
            "additional_current_fingerprints": len(pins) - len(verified),
        },
        "cases": cases,
        "recomputed_grades": grades,
        "retained_replays": replay_results,
        "native_crops_verified": 3,
        "native_frames_resampled_and_verified": sum(v["input_shape"][0] for v in cases.values()),
        "preview_images_verified": sum(v["input_shape"][0] * 3 for v in cases.values()),
        "review_section_sets_verified": sections_checked,
        "model_execution": {
            "model": "gpt-5.6-sol",
            "effort": "xhigh",
            "seconds": trial["agent_seconds"],
            "trajectory_steps": len(trace["steps"]),
            "initial_impression_artifact_matches_original_review": True,
        },
        "scorer_limits": [
            "Pilot thresholds, not clinical certification",
            "Sampled symmetric nearest-neighbor distances use vertices, centroids and edge midpoints, not exact continuous Hausdorff distance",
            "Absolute signed volume in original score does not by itself verify positive global winding",
            "No general self-intersection or myocardial material test",
            "Initial reference is supplied; separate recovered later frames",
        ],
        "source_terms": {
            "catalog_name": catalog["name"],
            "catalog_creator": catalog["creator"],
            "catalog_cite_as": catalog["citeAs"],
            "license": catalog["license"]["name"],
            "url": catalog["url"],
            "raw_and_derived_assets_local": True,
        },
        "visual_artifacts": {p.name: sha(p) for p in sorted(out.glob("*.png"))},
        "numeric_absolute_tolerance": 1e-8,
        "limits": old["limitations"],
    }
    dump(out / "audit.json", report)
    print(
        f"Verified {len(pins)} file hashes, all clinical grades and {sections_checked} retained sections",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
