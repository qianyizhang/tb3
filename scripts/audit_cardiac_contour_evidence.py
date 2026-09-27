"""Audit retained BR-025 inputs and saved geometry; never refit or launch a trial."""

import argparse
import hashlib
import json
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, distance_transform_edt

PINS = {
    "docs/evidence/br025-source-audit.json": "028087eae7b14c2d31d1bf9cbe6abbbee4159ae2c79fb6a4a20173ec887c03a9",
    "docs/evidence/br025-pilot-results.json": "a7fe35162ae56cc9adc179785db0cdb3fe242397088a9582eccd9c2152f4f577",
    "datasets/receipts/feecho4d-members.json": "1af472b1aea598fdeb327ff3f063158f9c128915b5a2e7147c74e519be936025",
    "runs/br025-cardiac/source/native/extraction-manifest.json": "bfb2e2053df5c83be75bdb3a8178325bf4701b4d194118656f727720a9d68285",
    "probes/cardiac-reconstruction/authoring/pilot.py": "164d9eef2c6481ab433371b6a663c2244a3af7fa2008df4bcb6ddff28c9ade95",
    "runs/br025-cardiac/pilot-v1/results.json": "a7fe35162ae56cc9adc179785db0cdb3fe242397088a9582eccd9c2152f4f577",
    "runs/br025-cardiac/pilot-v1/curves.json": "b8a940dbde8439357b4e0f66c7b26d386a3963400bdcbc06ba070339ad4a4b7a",
    "runs/br025-cardiac/pilot-v1/one-mesh.npz": "b17a56852cec758127170cbb77cceb10819185629b03fad7252d417b1e7cdf16",
    "runs/br025-cardiac/pilot-v1/two-mesh.npz": "e4d377ea075a6a059d39cf5be6e7f6d26a8a32b5af8b3e0327f23137f91fb9ca",
    "runs/br025-cardiac/pilot-v1/four-mesh.npz": "f21da70be75c46c76f2bdd769f60330ffe5cf91720bf058af5cab4dd0bf0eb1a",
    "runs/br025-cardiac/pilot-v1/eight-mesh.npz": "bf26e310a893eb449ec75e06c446af3eacdd85117e9cf6b8e29ad8661982c840",
    "runs/br025-cardiac/pilot-v1/dense-mesh.npz": "2114deaf80047c0a70705ccf72f17ce52ed1b90323df7cf381d9152bde8371af",
}
NATIVE = Path("runs/br025-cardiac/source/native/Patient001")
PILOT = Path("runs/br025-cardiac/pilot-v1")
VIEWS = {
    "one": [0],
    "two": [0, 18],
    "four": [0, 9, 18, 27],
    "eight": [0, 4, 9, 13, 18, 22, 27, 31],
    "dense": list(range(36)),
}
HOLDOUT = [2, 7, 11, 16, 20, 25, 29, 34]
SPACING = 0.08995


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def source_file(root, kind, view, frame):
    return root / NATIVE / kind / f"Patient001_slice{view + 1:03d}time{frame + 1:03d}.png"


def section(profile, view, shape=(464, 485)):
    """Project a retained radius field into its original calibrated radial plane."""
    yy, xx = np.indices(shape)
    dx, dy = xx - 242, yy - 172
    angle = np.arctan2(np.abs(dx), dy)
    polar = np.linspace(0, np.pi, 65)
    positive = np.interp(angle, polar, profile[view % 72])
    negative = np.interp(angle, polar, profile[(view + 36) % 72])
    return np.hypot(dx, dy) <= np.where(dx >= 0, positive, negative)


def volume(vertices, faces):
    tri = vertices[:, faces]
    return (
        np.einsum("tfj,tfj->tf", tri[:, :, 0], np.cross(tri[:, :, 1], tri[:, :, 2])).sum(1) / 6000
    )


def summary(values):
    a = np.asarray(values)
    return {
        "mean": float(a.mean()),
        "min": float(a.min()),
        "p05": float(np.quantile(a, 0.05)),
        "p95": float(np.quantile(a, 0.95)),
        "max": float(a.max()),
    }


def dice(a, b):
    return float(2 * (a & b).sum() / max(1, a.sum() + b.sum()))


def compare(actual, expected, path=""):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            compare(actual[key], expected[key], path + "/" + key)
    elif isinstance(expected, list):
        assert actual == expected, path
    elif isinstance(expected, int):
        assert actual == expected, (path, actual, expected)
    else:
        assert abs(actual - expected) <= 1e-10, (path, actual, expected)


def audit(root, out):
    assert not out.exists(), "Use a fresh local destination"
    out.mkdir(parents=True)
    for p, digest in PINS.items():
        assert sha(root / p) == digest, p
    acquisition = read(root / "runs/br025-cardiac/source/native/extraction-manifest.json")
    retained = read(root / "datasets/receipts/feecho4d-members.json")
    by_name = {m["name"]: m for m in retained["members"]}
    assert len(acquisition["members"]) == len(by_name) == 2251
    counts = {"image": 0, "mask": 0, "mesh": 0, "config": 0}
    for m in acquisition["members"]:
        relative = Path(m["name"]).relative_to("FeEcho4D/FeEcho4D_Annotated/Patient001")
        p = root / NATIVE / relative
        data = p.read_bytes()
        assert len(data) == m["size"] == by_name[m["name"]]["size"]
        assert hashlib.sha256(data).hexdigest() == m["sha256"] == by_name[m["name"]]["sha256"]
        assert zlib.crc32(data) == m["crc32"]
        counts[relative.parts[0] if len(relative.parts) > 1 else "config"] += 1
    assert counts == {"image": 1110, "mask": 1110, "mesh": 30, "config": 1}
    original = read(root / "docs/evidence/br025-pilot-results.json")
    masks = {}
    for view in range(37):
        for frame in range(30):
            mask = np.asarray(Image.open(source_file(root, "mask", view, frame)))
            assert mask.shape == (464, 485) and set(np.unique(mask)) <= {0, 127, 255}
            assert Image.open(source_file(root, "image", view, frame)).size == (485, 464)
            masks[view, frame] = mask == 127
    assert all(not set(v) & set(HOLDOUT) for name, v in VIEWS.items() if name != "dense")
    ranges = [np.where(masks[0, t][:, 242])[0] for t in range(30)]
    assert (max(r.min() for r in ranges) + min(r.max() for r in ranges)) / 2 == 172
    mirror = [dice(masks[0, t][:, ::-1], masks[36, t]) for t in range(30)]
    old_source = read(root / "docs/evidence/br025-source-audit.json")
    compare(
        {"mean": float(np.mean(mirror)), "min": min(mirror), "max": max(mirror)},
        old_source["duplicate_direction_mirror_dice"],
    )
    saved = {name: dict(np.load(root / PILOT / f"{name}-mesh.npz")) for name in VIEWS}
    faces = saved["one"]["faces"]
    for data in saved.values():
        assert data["vertices"].shape == (30, 4538, 3)
        assert data["radius_px"].shape == (30, 72, 65)
        assert np.array_equal(data["faces"], faces)
        np.testing.assert_allclose(
            volume(data["vertices"], faces), data["volume_ml"], atol=1e-12, rtol=0
        )
    assert faces.shape == (9072, 3)
    saved["static"] = {
        k: np.repeat(v[:1], 30, axis=0) for k, v in saved["four"].items() if k != "faces"
    }
    curves = read(root / PILOT / "curves.json")
    for name, data in saved.items():
        np.testing.assert_allclose(data["volume_ml"], curves[name], atol=1e-12, rtol=0)
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, edge_counts = np.unique(edges, axis=0, return_counts=True)
    stats = {}

    def ef(v):
        return float(100 * (1 - v[16] / v[1]))

    for name, data in saved.items():
        held, hd, observed = [], [], []
        for t in range(30):
            for view in HOLDOUT:
                truth, pred = masks[view, t], section(data["radius_px"][t], view)
                held.append(dice(truth, pred))
                a, b = truth ^ binary_erosion(truth), pred ^ binary_erosion(pred)
                distances = (
                    np.r_[distance_transform_edt(~a)[b], distance_transform_edt(~b)[a]] * SPACING
                )
                hd.append(float(np.quantile(distances, 0.95)))
            # Preserve the historical static observed-dice implementation (plane 1 only).
            for view in VIEWS.get(name, [0]):
                observed.append(dice(masks[view, t], section(data["radius_px"][t], view)))
        v, curve = data["vertices"], data["volume_ml"]
        area = (
            np.linalg.norm(
                np.cross(
                    v[:, faces[:, 1]] - v[:, faces[:, 0]], v[:, faces[:, 2]] - v[:, faces[:, 0]]
                ),
                axis=-1,
            )
            / 2
        )
        stats[name] = {
            "input_planes_1based": [i + 1 for i in VIEWS.get(name, VIEWS["four"])],
            "heldout_dice": summary(held),
            "heldout_hd95_mm": summary(hd),
            "observed_dice": summary(observed),
            "ef_at_source_phases_percent": ef(curve),
            "ef_error_vs_dense_reference_pp": abs(ef(curve) - ef(saved["dense"]["volume_ml"])),
            "volume_curve_mape_vs_dense_percent": float(
                100 * np.mean(np.abs(curve / saved["dense"]["volume_ml"] - 1))
            ),
            "max_volume_frame_1based": int(np.argmax(curve)) + 1,
            "min_volume_frame_1based": int(np.argmin(curve)) + 1,
            "volume_at_source_ed_ml": float(curve[1]),
            "volume_at_source_es_ml": float(curve[16]),
            "mesh_boundary_edges": int((edge_counts == 1).sum()),
            "mesh_nonmanifold_edges": int((edge_counts > 2).sum()),
            "degenerate_triangle_count": int((area < 1e-10).sum()),
            "min_signed_volume_ml": float(curve.min()),
            "framewise_displacement_p95_mm": float(
                np.quantile(np.linalg.norm(np.diff(v, axis=0), axis=-1), 0.95)
            ),
        }
        compare(stats[name], original["stats"][name], name)
        print(f"{name}: original score fields reproduced", flush=True)
    scale = 1 + 0.25 * np.cos(2 * np.pi * (np.arange(30) - 1) / 30)
    changed = saved["one"]["vertices"].copy()
    changed[:, :, 2] *= scale[:, None]
    on_plane = np.isclose(saved["one"]["vertices"][:, :, 2], 0, atol=1e-10)
    np.testing.assert_allclose(
        changed[on_plane], saved["one"]["vertices"][on_plane], atol=1e-12, rtol=0
    )
    modified_curve = volume(changed, faces)
    np.testing.assert_allclose(
        modified_curve, saved["one"]["volume_ml"] * scale, atol=1e-12, rtol=0
    )
    control = {
        "scale_range": [float(scale.min()), float(scale.max())],
        "same_observed_plane_exactly": True,
        "original_ef_percent": ef(saved["one"]["volume_ml"]),
        "modified_ef_percent": ef(modified_curve),
        "difference_pp": abs(ef(saved["one"]["volume_ml"]) - ef(modified_curve)),
    }
    compare(control, original["missing_depth_control"])
    # Native-size selected reader images; labels are separate source/evaluation roles.
    for t in [1, 16]:
        canvas = Image.new("RGB", (485 * 3, 514), "white")
        draw = ImageDraw.Draw(canvas)
        for i, name in enumerate(["one", "four", "eight"]):
            im = np.array(Image.open(source_file(root, "image", 7, t)).convert("RGB"))
            truth, pred = masks[7, t], section(saved[name]["radius_px"][t], 7)
            im[truth ^ binary_erosion(truth)] = [237, 194, 61]
            im[pred ^ binary_erosion(pred)] = [33, 206, 220]
            canvas.paste(Image.fromarray(im), (i * 485, 30))
            draw.text(
                (i * 485 + 12, 8),
                f"{name} supplied views | held-out plane 8 | frame {t + 1}",
                fill="black",
            )
        draw.text(
            (10, 500),
            "Gold: source LV boundary | Cyan: projected saved contour reconstruction | Native 0.08995 mm/px",
            fill="black",
        )
        canvas.save(out / f"heldout-frame-{t + 1}.png")
    result = {
        "schema": 1,
        "scope": "BR-025 source and saved-output audit only; no reconstruction, model trial or clinical adjudication",
        "source_pins": PINS,
        "members_verified": 2251,
        "member_counts": counts,
        "member_manifest_sha256": PINS["datasets/receipts/feecho4d-members.json"],
        "member_sha256_crc32_and_size_match": True,
        "native_shape_hw": [464, 485],
        "radial_pose_status": "Assumed 5 degree steps, x=242 px axis, y=172 px origin from supplied plane 1 only; no independently audited per-plane pose",
        "phase_status": "Config ED_time=2 and ES_time=17 interpreted as one-based; config index base remains unspecified",
        "duplicate_direction_mirror_dice": old_source["duplicate_direction_mirror_dice"],
        "sparse_heldout_disjoint": True,
        "heldout_pairs_per_condition": 240,
        "mesh_frames": 30,
        "mesh_vertices": 4538,
        "mesh_faces": 9072,
        "recomputed_stats": stats,
        "numeric_tolerance": 1e-10,
        "missing_depth_control": control,
        "static_observed_dice_scope": "Historical observed Dice is evaluated on plane 1, although static mesh was copied from the four-view reconstruction; held-out comparisons still use the same eight directions.",
        "dense_scope": "Dense includes evaluation planes; values named heldout in original JSON are source fit only, not held-out accuracy.",
        "limits": [
            "One selected source patient and propagated/refined source masks; not 240 independent cases.",
            "Dense comparator and fixed vertex IDs do not establish independent 3D truth or material motion.",
            "Native source OBJ physical transform and cavity partition were not established; never use its whole-shell volume as an EF oracle.",
            "Original scores and source artifacts remain unchanged. No publication or redistribution is performed by this audit.",
        ],
    }
    dump(out / "audit.json", result)
    dump(out / "curves.json", dict(curves, ambiguity=modified_curve.tolist()))
    print(json.dumps({"output": str(out), "members_verified": 2251, "conditions_replayed": 6}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output)
