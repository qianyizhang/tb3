"""Audit retained BR-032 source and outputs without running a historical solver."""

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

BASE = Path("runs/br032-real-echo")
PINS = {
    "docs/evidence/br032-real-echo-results.json": "48973ce75ce6105b1ec8396142f4afdfd16225aac41890495af1e3e8ec040a93",
    "datasets/receipts/echoslicer-files.json": "56bd504d244a777a6c46f8a8011c0e19c1b0fe93d93159ad60595c2929f368fb",
    "runs/br032-real-echo/freeze.json": "2f5ed47d92fe2b6f9715a844e42f85a6cba868689dd9a41a506485d48368f1c6",
    "runs/br032-real-echo/source/source-receipt.json": "0a753395e6e61401d4612874659458dba75b13580874b12ef23c0da55216be55",
    "runs/br032-real-echo/source/selected.dcm": "cfe78d709e89e9127e5ece5089c0824e677eab3eb90950876df23ff3cdbb3fc1",
    "runs/br032-real-echo/input-validation.json": "3b8b9195c8ece224c67f23ad56c516ee9745b07755ee7ff7281bed6e14842209",
    "runs/br032-real-echo/native.npz": "c2aaadd2f51b762f00829811e5fe30d97a1b6729fe46dcf681de41b7be289769",
    "runs/br032-real-echo/decode.json": "689cc19b47882b296fc7b4de05f26ea5f4ae2fb36b5b31b2f50818bfa1cd179c",
    "runs/br032-real-echo/private-review.json": "b0cae6f0abc8292b8588462769261c189573afe92e2a94d406caa7d62f0ee46f",
    "runs/br032-real-echo/private-review.npz": "a541bfe3618c196e8d42c8bf9ae33a0e08d3cd536d714f9a93b6c23f2876e6c4",
    "runs/br032-real-echo/review-slices.npz": "516f0720b4342c591c5f13fe980cbe26ea615479ff9ba9d2a71ee0f722a1ce42",
    "runs/br032-real-echo/sol-xhigh-receipt.json": "1693d1d06c0defe0ecbf70fafc7b841c6c08751bd76887571b8bc883938a4803",
    "runs/br032-real-echo/oracle-receipt.json": "b1c92ccac0f346239ec0c7e5eac09b3ca9d0a463b0c341ae1700acdeab703196",
    "runs/br032-real-echo/nop-receipt.json": "a5dae445e9a4c941e200f98c6c897ef7c4bcede6adca936c68d2003b1153318c",
    "runs/br032-real-echo/review/data.json": "7c46e0c68ff3631d2ecb4d38338e45dbb0a7a9a4fb3db0e3ed45424ef6259d08",
    "runs/br032-real-echo/review-metrics.json": "1338e3b11bcc9a65dcfc5f25b8b13974d1e9025be9aaa6fb6ae2ab3d113c77d9",
    "runs/br032-real-echo/author-review.json": "31aab7179269ce23a5302d375d57cba791e4a51c05c2b8b5a1992410975b63e3",
    "runs/br032-real-echo/replay-assessment.json": "716295c8578135f58944c530b6bf3713a91871aaea11ac44f666c24a889a3a47",
    "runs/br032-real-echo/replays/pose/receipt.json": "989d3e33da201baf49fe281bdd34b75107a7ee84045da888b5e32a716eeed69d",
    "runs/br032-real-echo/replays/pose-v2/receipt.json": "1dbeb91532316e7b5b4f9384182cf0b428813474ace8327112bab37e93b9dec4",
    "runs/br032-real-echo/replays/static/receipt.json": "03f00e5a8683e1f5e461413ecf8f0296e1189f047889a2fce0ce14faed13e174",
    "runs/br032-real-echo/replays/static-v2/receipt.json": "c70263eb236f4221a0b93599fca91d4b695208aae50b69496589d2841e2e095e",
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def decode(root, out):
    """Use only the required private image tags; never export patient metadata."""
    import pydicom

    out.mkdir(parents=True, exist_ok=False)
    source = root / BASE / "source/selected.dcm"
    native_path = root / BASE / "native.npz"
    assert sha(source) == PINS[str(BASE / "source/selected.dcm")]
    assert sha(native_path) == PINS[str(BASE / "native.npz")]
    d = pydicom.dcmread(source)
    shape_code = np.asarray(d[0x200D, 0x3315].value, dtype=int)
    stride_code = np.asarray(d[0x200D, 0x3316].value, dtype=int)
    shape = (shape_code ^ shape_code[-1])[2::-1]
    stride = (stride_code ^ stride_code[-1])[2::-1]
    fragment = d[0x200D, 0x3CF5][1][0x200D, 0x3CF1][0]
    assert fragment[0x200D, 0x3CFA].value == "ZLib"
    raw, headers = fragment[0x200D, 0x3CF3].value, fragment[0x200D, 0x3CFB].value
    _, frames = struct.unpack("<II", raw[:8])
    starts = struct.unpack("<" + "I" * frames, raw[8 : 8 + 4 * frames])
    native = np.load(native_path, allow_pickle=False)
    assert frames == 18 and native["images"].shape == (18, 404, 76, 62)
    for i, start in enumerate(starts):
        assert raw[start : start + 32] == headers[i * 32 : (i + 1) * 32]
        buffer = np.frombuffer(zlib.decompress(raw[start + 32 :]), dtype=np.uint8)
        volume = buffer[: np.prod(stride)].reshape(stride)
        decoded = volume[: shape[0], : shape[1], : shape[2]].transpose(2, 1, 0)
        np.testing.assert_array_equal(decoded, native["images"][i])
    bounds = np.array(
        [float(d[0x200D, tag].value) for tag in [0x3102, 0x3103, 0x3104, 0x3105, 0x3203, 0x3204]]
    ).reshape(3, 2)
    np.testing.assert_array_equal(bounds, native["bounds"])
    assert float(d.FrameTime) == 161.15 and int(d.NumberOfFrames) == frames
    result = {
        "source_sha256": sha(source),
        "native_sha256": sha(native_path),
        "script_sha256": sha(Path(__file__)),
        "python": sys.version.split()[0],
        "pydicom": pydicom.__version__,
        "numpy": np.__version__,
        "all_native_frames_equal": True,
        "shape_T_rho_phi_theta": list(native["images"].shape),
        "stride_theta_phi_rho": stride.tolist(),
        "bounds_rho_mm_phi_rad_theta_rad": bounds.tolist(),
        "frame_time_ms": float(d.FrameTime),
        "dicom_identifiers_exported": False,
    }
    dump(out / "decode.json", result)
    print("Native DICOM decode: all 18 frames and bounds equal retained arrays", flush=True)


def volumes(points, faces):
    centered = points - points.mean(axis=1, keepdims=True)
    a, b, c = (centered[:, faces[:, i]] for i in range(3))
    return (a * np.cross(b, c)).sum(axis=(1, 2)) / 6000


def geometry_audit(answer, original):
    z = dict(np.load(answer / "prediction.npz", allow_pickle=False))
    p, f, alternatives = (z[k] for k in ["points", "faces", "alternative_points"])
    assert p.ndim == 3 and p.shape[0] == 18 and p.shape[2] == 3
    assert 4 <= p.shape[1] <= 10000 and 4 <= len(f) <= 20000 and f.shape[1] == 3
    assert np.issubdtype(f.dtype, np.integer) and f.min() >= 0 and f.max() < p.shape[1]
    assert 2 <= len(alternatives) <= 5 and alternatives.shape[1:] == p.shape
    assert np.isfinite(p).all() and np.isfinite(alternatives).all()
    directed = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    _, inverse, counts = np.unique(
        np.sort(directed, axis=1), axis=0, return_counts=True, return_inverse=True
    )
    orientation = np.bincount(inverse, weights=np.where(directed[:, 0] < directed[:, 1], 1, -1))
    assert np.all(counts == 2) and np.all(orientation == 0)
    area = (
        np.linalg.norm(
            np.cross(p[:, f[:, 1]] - p[:, f[:, 0]], p[:, f[:, 2]] - p[:, f[:, 0]]), axis=-1
        )
        / 2
    )
    v = volumes(p, f)
    av = np.stack([volumes(a, f) for a in alternatives])
    assert area.min() > 1e-8 and np.all(v > 0) and np.all(av > 0)
    assert all((answer / name).is_file() for name in ["solve.py", "summary.json", "method.md"])
    summary = read(answer / "summary.json")
    assert summary["frame_ids"] == list(range(1, 19))
    np.testing.assert_allclose(summary["volume_ml"], v, rtol=0.001, atol=0.01)
    numbers = {
        "vertices": p.shape[1],
        "triangles": len(f),
        "volume_ml": v.tolist(),
        "alternative_volume_ml": av.tolist(),
        "displacement_from_first_rms_mm": float(np.sqrt(np.mean(np.sum((p - p[0]) ** 2, axis=-1)))),
        "temporal_step_rms_mm": float(np.sqrt(np.mean(np.sum(np.diff(p, axis=0) ** 2, axis=-1)))),
        "first_last_point_gap_rms_mm": float(
            np.sqrt(np.mean(np.sum((p[-1] - p[0]) ** 2, axis=-1)))
        ),
        "min_face_area_mm2": float(area.min()),
    }
    for key, value in numbers.items():
        np.testing.assert_allclose(value, original[key], rtol=0, atol=1e-9, err_msg=key)
    assert original["reward"] == 1 and original["self_intersection_checked"] is False
    assert original["ground_truth_available"] is False
    return z, {
        **numbers,
        "original_reward": 1,
        "scope": "artifact validity; no anatomy truth or general self-intersection check",
    }


def sections(points, faces, plane):
    o, u, v = (np.asarray(plane[k]) for k in ["origin", "u", "v"])
    triangles = points[faces]
    distances = np.einsum("fvi,i->fv", triangles - o, np.cross(u, v))
    cut = (distances.min(1) < 0) & (distances.max(1) > 0)
    triangles, distances = triangles[cut], distances[cut]
    lines = np.zeros((len(triangles), 2, 3))
    counts = np.zeros(len(triangles), dtype=int)
    for a, b in [(0, 1), (1, 2), (2, 0)]:
        ids = np.flatnonzero((distances[:, a] < 0) != (distances[:, b] < 0))
        t = distances[ids, a] / (distances[ids, a] - distances[ids, b])
        lines[ids, counts[ids]] = triangles[ids, a] + t[:, None] * (
            triangles[ids, b] - triangles[ids, a]
        )
        counts[ids] += 1
    lines = lines[counts == 2] - o
    return (
        np.stack([np.einsum("svi,i->sv", lines, u), np.einsum("svi,i->sv", lines, v)], axis=-1)
        / 0.75
        + 127.5
    )


def image_proxy(image, segments):
    import cv2

    mask = np.zeros((256, 256), dtype=np.uint8)
    if len(segments):
        x0, y0 = segments[:, 0].T
        x1, y1 = segments[:, 1].T
        for y in range(256):
            hit = (y0 > y) != (y1 > y)
            xs = np.sort(x0[hit] + (y - y0[hit]) * (x1[hit] - x0[hit]) / (y1[hit] - y0[hit]))
            for a, b in zip(xs[::2], xs[1::2], strict=True):
                lo, hi = max(0, int(np.ceil(a))), min(256, int(np.ceil(b)))
                if hi > lo:
                    mask[y, lo:hi] = 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    border = (mask > 0) & (cv2.erode(mask, kernel) == 0)
    inner = border & (image > 0)
    outer = (cv2.dilate(mask, kernel) > 0) & (mask == 0) & (image > 0)
    if inner.sum() < 20 or outer.sum() < 20:
        return None
    return {
        "outer_minus_inner": float(image[outer].mean() - image[inner].mean()),
        "inside_mean": float(image[(mask > 0) & (image > 0)].mean()),
        "mask_area_px": int(mask.sum()),
        "boundary_support_fraction": float(inner.sum() / max(1, border.sum())),
    }


def audit(root, out, dicom_python):
    from scipy.ndimage import map_coordinates
    from scipy.spatial.transform import Rotation

    out.mkdir(parents=True, exist_ok=False)
    pins = {}
    verified_existing_pins = set()

    def pin(path, expected=None):
        key = str(path)
        actual = sha(root / path)
        assert expected is None or actual == expected, key
        assert key not in pins or pins[key] == actual, key
        pins[key] = actual
        if expected is not None:
            verified_existing_pins.add(key)

    for p, digest in PINS.items():
        pin(Path(p), digest)
    b = root / BASE
    result = read(root / "docs/evidence/br032-real-echo-results.json")
    for p, digest in result["code_sha256"].items():
        pin(Path(p), digest)
    source = read(b / "source/source-receipt.json")
    for name, digest in source["author_source_files"].items():
        pin(BASE / "source" / Path(name).name, digest)
    freeze = read(b / "freeze.json")
    for name, digest in freeze["files"].items():
        pin(Path(freeze["task_path"]) / name, digest)
    assert len(freeze["files"]) == 84
    validation = read(b / "input-validation.json")
    for name, digest in validation["input_files"].items():
        pin(BASE / "input" / name, digest)
        assert freeze["files"]["environment/data/" + name] == digest
    assert len(validation["input_files"]) == 73
    for directory in [b / "input", root / freeze["task_path"] / "environment/data"]:
        assert {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()} == set(
            validation["input_files"]
        )
    assert source["selected_member"] == "dataset/A_0.dcm"
    assert (b / "source/selected.dcm").stat().st_size == source["source_bytes"] == 37488946
    subprocess.run(
        [
            str(dicom_python),
            str(Path(__file__).resolve()),
            "--root",
            str(root),
            "--out",
            str(out / "native-decode"),
            "--decode-only",
        ],
        check=True,
    )
    native = np.load(b / "native.npz", allow_pickle=False)
    image_stack = np.load(b / "private-review.npz", allow_pickle=False)
    images = image_stack["images"]
    np.testing.assert_array_equal(
        images, np.load(b / "review-slices.npz", allow_pickle=False)["images"]
    )
    spec, public = read(b / "private-review.json"), read(b / "input/geometry.json")
    observed, withheld = [0, 1, 5, 7], [2, 3, 4, 6]
    assert spec["observed"] == observed and spec["withheld"] == withheld
    np.testing.assert_array_equal(image_stack["observed"], observed)
    np.testing.assert_array_equal(image_stack["withheld"], withheld)
    rotation = Rotation.from_euler("zyx", [17, -23, 31], degrees=True).as_matrix()
    offset = np.array([13.4, -27.8, 6.2])
    np.testing.assert_allclose(spec["source_to_task_R"], rotation, rtol=0, atol=1e-14)
    np.testing.assert_array_equal(spec["source_to_task_translation"], offset)
    native_planes = []
    for angle in [0, 90, 45, 135]:
        a = np.deg2rad(angle)
        native_planes.append(([90, 0, 0], [0, np.sin(a), np.cos(a)], [1, 0, 0]))
    native_planes.extend(([depth, 0, 0], [0, 0, 1], [0, 1, 0]) for depth in [45, 65, 85, 105])
    rows, cols = np.mgrid[:256, :256]
    uv = np.stack([(cols - 127.5) * 0.75, (rows - 127.5) * 0.75], axis=-1).reshape(-1, 2)
    bounds = native["bounds"]
    for j, (o, u, v) in enumerate(native_planes):
        points = np.asarray(o) + uv[:, :1] * u + uv[:, 1:] * v
        x, y, z = points.T
        rho = np.linalg.norm(points, axis=1)
        spherical = np.stack(
            [
                rho,
                np.arctan2(z, x),
                np.arcsin(np.divide(y, rho, out=np.zeros_like(y), where=rho > 1e-8)),
            ]
        )
        indices = (
            (spherical - bounds[:, :1])
            / np.diff(bounds, axis=1)
            * (np.array(native["images"].shape[1:])[:, None] - 1)
        )
        for key, value in zip(
            ["origin", "u", "v"],
            [
                np.asarray(o) @ rotation.T + offset,
                np.asarray(u) @ rotation.T,
                np.asarray(v) @ rotation.T,
            ],
            strict=True,
        ):
            np.testing.assert_allclose(spec["planes"][j][key], value, rtol=0, atol=1e-13)
            if j in observed:
                np.testing.assert_array_equal(
                    public["planes"][observed.index(j)][key], spec["planes"][j][key]
                )
        for frame in range(18):
            reslice = map_coordinates(
                native["images"][frame], indices, order=1, mode="constant"
            ).reshape(256, 256)
            np.testing.assert_array_equal(reslice, images[j, frame])
            stored = b / "review/images" / f"p{j}_f{frame}.png"
            np.testing.assert_array_equal(np.asarray(Image.open(stored)), reslice)
            pin(stored.relative_to(root))
            if j in observed:
                public_png = (
                    b / "input" / f"view_{observed.index(j)}" / f"frame_{frame + 1:02d}.png"
                )
                np.testing.assert_array_equal(np.asarray(Image.open(public_png)), reslice)
    np.testing.assert_array_equal(public["times_seconds"], np.arange(18) * 0.16115)
    print("All 144 reslices match native data; 72 public images match frozen task", flush=True)

    trials, meshes = {}, {}
    for phase in ["sol-xhigh", "oracle", "nop"]:
        receipt = read(b / f"{phase}-receipt.json")
        pin(Path(receipt["result_path"]), receipt["result_sha256"])
        assert (
            receipt["task_checksum"]
            == "07e614e9bb09cf8dd02278e021636dd1b24ebdc15544684d26f30d6816f80a4f"
        )
        answer = (root / receipt["result_path"]).parent / "artifacts/app/answer"
        for name, digest in receipt["artifacts"].items():
            pin(answer.relative_to(root) / name, digest)
        if phase == "nop":
            assert receipt["grade"]["reward"] == 0 and not (answer / "prediction.npz").exists()
            trials[phase] = {
                "original_reward": 0,
                "original_error": receipt["grade"]["error"],
                "scope": "missing artifact control",
            }
        else:
            meshes[phase], trials[phase] = geometry_audit(answer, receipt["grade"])
        for session in receipt.get("session_files", []):
            pin(Path(session["path"]), session["sha256"])
    receipt = read(b / "sol-xhigh-receipt.json")
    trial_dir = Path(receipt["result_path"]).parent
    trajectory_path = trial_dir / "agent/trajectory.json"
    pin(trajectory_path, "0d60ac85483c9065002ceb7f77619b82ff86757ac51847ce84777ada386551af")
    trajectory = read(root / trajectory_path)
    image_steps = []
    for step in trajectory["steps"]:
        calls = str(step.get("tool_calls") or [])
        if "tools.view_image" in calls:
            image_steps.append(step["step_id"])
    assert image_steps == [11, 15, 17, 18, 22, 24, 26, 29, 33, 34]
    assert trajectory["agent"]["model_name"] == "gpt-5.6-sol"
    assert receipt["runtime_contexts"] == [{"model": "gpt-5.6-sol", "effort": "xhigh"}]
    original = meshes["sol-xhigh"]
    replay_results = {}
    for kind in ["pose", "static"]:
        for suffix in ["", "-v2"]:
            replay = b / "replays" / (kind + suffix)
            record = read(replay / "receipt.json")
            for name, digest in record["input_hashes"].items():
                pin(replay.relative_to(root) / "input" / name, digest)
            assert set(record["input_hashes"]) == set(validation["input_files"])
            assert record["network"] == "none" and record["timeout"] is False
            assert record["submitted_solver_sha256"] == receipt["artifacts"]["solve.py"]
            if not suffix:
                assert record["exit_code"] == 125
                pin(replay.relative_to(root) / "stdout.txt")
                assert "Unable to find image" in (replay / "stdout.txt").read_text()
                continue
            assert (
                record["exit_code"] == 0
                and record["contract"]["error"] == "AssertionError: solve.py"
            )
            assert not (replay / "output/solve.py").exists()
            for p in (replay / "output").rglob("*"):
                if p.is_file():
                    pin(p.relative_to(root))
            z = np.load(replay / "output/prediction.npz", allow_pickle=False)
            np.testing.assert_array_equal(z["faces"], original["faces"])
            changed_pngs = 0
            for name, digest in record["input_hashes"].items():
                if name.endswith(".png"):
                    changed_pngs += digest != validation["input_files"][name]
                    expected_file = (
                        b / "input" / name
                        if kind == "pose"
                        else b / "input" / Path(name).parent / "frame_01.png"
                    )
                    assert sha(replay / "input" / name) == sha(expected_file)
            if kind == "static":
                assert changed_pngs == 68
                assert (
                    record["input_hashes"]["geometry.json"]
                    == validation["input_files"]["geometry.json"]
                )
                for key in ["points", "alternative_points"]:
                    np.testing.assert_array_equal(z[key], original[key])
                replay_results[kind] = {
                    "changed_pngs": changed_pngs,
                    "total_pngs": 72,
                    "primary_and_alternatives_exactly_unchanged": True,
                    "retained_motion_rms_mm": trials["sol-xhigh"]["displacement_from_first_rms_mm"],
                }
            else:
                assert changed_pngs == 0
                q = Rotation.from_euler("xyz", [-21, 13, 37], degrees=True).as_matrix()
                shift = np.array([-18.2, 11.1, 24.6])
                altered = read(replay / "input/geometry.json")
                for a, p in zip(altered["planes"], public["planes"], strict=True):
                    np.testing.assert_allclose(
                        a["origin"], np.asarray(p["origin"]) @ q.T + shift, rtol=0, atol=1e-13
                    )
                    for key in ["u", "v"]:
                        np.testing.assert_allclose(
                            a[key], np.asarray(p[key]) @ q.T, rtol=0, atol=1e-13
                        )
                errors = {}
                for key in ["points", "alternative_points"]:
                    delta = z[key] - (np.einsum("...i,ji->...j", original[key], q) + shift)
                    errors[key + "_rmse_mm"] = float(np.sqrt(np.mean(np.sum(delta**2, axis=-1))))
                    assert errors[key + "_rmse_mm"] < 1e-10
                replay_results[kind] = {"changed_pngs": 0, **errors}

    review = read(b / "review/data.json")
    metrics = read(b / "review-metrics.json")
    all_points = [original["points"], *original["alternative_points"]]
    intersections = {}
    all_sections = []
    for model, points in zip(review["models"], all_points, strict=True):
        np.testing.assert_array_equal(np.round(points, 4), model["points"])
        np.testing.assert_allclose(
            volumes(points, original["faces"]), model["volumes"], rtol=0, atol=1e-9
        )
        model_sections = []
        for j, plane in enumerate(spec["planes"]):
            sequence = []
            frames_with_sections = []
            for t in range(18):
                lines = sections(points[t], original["faces"], plane)
                assert np.round(lines, 3).tolist() == model["sections"][j][t]
                proxy = image_proxy(images[j, t], lines)
                assert proxy == model["image_proxies"][j][t]
                assert proxy == metrics["image_proxies"][model["name"]][j][t]
                sequence.append(lines)
                if len(lines):
                    frames_with_sections.append(t + 1)
            model_sections.append(sequence)
            intersections.setdefault(model["name"], {})[plane["name"]] = frames_with_sections
        all_sections.append(model_sections)
    for j in range(8):
        for t in range(18):
            assert (
                image_proxy(images[j, t], all_sections[0][j][0])
                == metrics["static_initial_mesh_proxies"][j][t]
            )
    assert intersections["Agent reconstruction"]["short_65"] == []
    assert intersections["Agent reconstruction"]["short_85"] == [3, 4, 9, 10, 15, 16]
    for frame in [1, 3, 9, 13]:
        sheet = Image.new("RGB", (3 * 256, 4 * 286 + 44), "#101820")
        draw = ImageDraw.Draw(sheet)
        draw.text(
            (8, 7),
            f"BR-032 source frame {frame + 1} | native pixels; no independent contours",
            fill="white",
        )
        draw.text(
            (8, 23),
            "Cyan solid: primary | gold dashed: basal alternative | no contour GT",
            fill="white",
        )
        for row, j in enumerate([0, 7, 2, 6]):
            for column in range(3):
                panel = Image.fromarray(images[j, frame]).convert("RGB")
                pd = ImageDraw.Draw(panel)
                if column > 0:
                    lines = all_sections[0 if column == 1 else 3][j][frame]
                    for a, b_ in lines:
                        if column == 1:
                            pd.line([tuple(a), tuple(b_)], fill="#3de9d6", width=2)
                        else:
                            count = max(1, int(np.ceil(np.linalg.norm(b_ - a) / 3)))
                            for i in range(0, count, 2):
                                pd.line(
                                    [
                                        tuple(a + (b_ - a) * i / count),
                                        tuple(a + (b_ - a) * min(i + 1, count) / count),
                                    ],
                                    fill="#ffcc66",
                                    width=2,
                                )
                sheet.paste(panel, (column * 256, 44 + row * 286))
                role = "Given" if j in observed else "Review only"
                label = ["Source only", "Primary section", "Basal alternative"][column]
                draw.text(
                    (column * 256 + 5, 44 + row * 286 + 259),
                    f"{role} {spec['planes'][j]['name']} | {label}",
                    fill="white",
                )
        sheet.save(out / f"sections-frame-{frame + 1:02d}.png")
    report = {
        "schema": 1,
        "scope": "BR-032 saved-source/output audit; no solver execution, new trial, clinical adjudication or historical score change",
        "source_pins": pins,
        "hash_coverage": {
            "checked_against_existing_receipts": len(verified_existing_pins),
            "additional_current_fingerprints": len(pins) - len(verified_existing_pins),
            "distinction": "Additional fingerprints cover retained review images and replay outputs checked against source pixels, arrays or geometry; they are not pre-existing hash attestations.",
        },
        "native_decode": read(out / "native-decode/decode.json"),
        "frozen_files": 84,
        "public_files": 73,
        "public_pngs": 72,
        "review_only_pngs": 72,
        "all_reslices_equal_native_sampling": True,
        "observed_plane_indices_zero_based": observed,
        "withheld_plane_indices_zero_based": withheld,
        "trials": trials,
        "model_trace": {
            "model": "gpt-5.6-sol",
            "effort": "xhigh",
            "seconds": receipt["agent_seconds"],
            "trajectory_steps": len(trajectory["steps"]),
            "image_view_tool_steps": image_steps,
        },
        "retained_replays": replay_results,
        "replay_limits": "v1 exit 125 before execution: missing image. v2 completed network-none; whole-artifact reward 0 records missing copied solve.py, not anatomy failure. Array comparisons here are new checks of retained outputs, not fresh replays.",
        "all_576_section_sets_and_proxies_match_retained_review": True,
        "all_144_static_mesh_proxies_match": True,
        "intersection_frames": intersections,
        "numeric_absolute_tolerance": 1e-9,
        "visual_artifacts": {p.name: sha(p) for p in sorted(out.glob("*.png"))},
        "limits": [
            "No independent segmentation, geometry or material truth",
            "Chamber and basal assignment unadjudicated",
            "Brightness proxies exclude empty or poorly supported boundaries and are not accuracy",
            "Alternative spread is not a calibrated confidence interval",
            "Source exposure unknown; original prompt retrieval prohibition is not network isolation",
            "Selected stills do not establish integrated story or motion acceptance",
        ],
    }
    dump(out / "audit.json", report)
    print(
        f"Recorded {len(pins)} file hashes ({len(verified_existing_pins)} checked against existing receipts); "
        "all retained mesh metrics and review sections/proxies match",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dicom-python", type=Path)
    parser.add_argument("--decode-only", action="store_true")
    args = parser.parse_args()
    if args.decode_only:
        decode(args.root.resolve(), args.out.resolve())
    else:
        if args.dicom_python is None:
            parser.error("--dicom-python must name an existing runtime with pydicom and NumPy")
        # Preserve the venv executable path; resolving its symlink loses that environment.
        audit(args.root.resolve(), args.out.resolve(), args.dicom_python.absolute())


if __name__ == "__main__":
    main()
