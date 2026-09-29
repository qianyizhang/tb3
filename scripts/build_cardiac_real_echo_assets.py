"""Build a local, source-derived BR-032 teaching pack from retained bytes only.

No historical preparation, solver, model, or author module is imported or run.
"""

import argparse
import base64
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = next(
    parent for parent in Path(__file__).resolve().parents if (parent / "workbench.toml").is_file()
)
AUDIT = Path("groups/cardiac-motion/presentation/sources/real-echo-audit.json")
GEOMETRY = Path("runs/br032-real-echo/task/cardiac-real/environment/data/geometry.json")
PUBLIC = Path("runs/br032-real-echo/task/cardiac-real/environment/data")
REVIEW = Path("runs/br032-real-echo/private-review.npz")
PREDICTION = Path(
    "runs/br032-real-echo-sol-xhigh-v1-20260916/cardiac-real__f4ubmjE/artifacts/app/answer/prediction.npz"
)
STATIC = Path("runs/br032-real-echo/task/cardiac-real/solution/prediction.npz")
RING_IDS = list(range(0, 25, 2))
AZIMUTH_IDS = list(range(0, 48, 3))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def compact_float(value, digits=3):
    return round(float(value), digits)


def image_data(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def section_path(points, faces, plane):
    """Intersect the retained triangular surface with its calibrated image plane."""
    origin = np.asarray(plane["origin"], dtype=float)
    u = np.asarray(plane["u"], dtype=float)
    v = np.asarray(plane["v"], dtype=float)
    normal = np.cross(u, v)
    assert np.isfinite(points).all() and np.isfinite(origin).all()
    assert np.isfinite(normal).all() and np.isclose(np.linalg.norm(normal), 1.0)
    signed = np.einsum("ij,j->i", points - origin, normal)
    assert np.isfinite(signed).all()
    tri = points[faces]
    distance = signed[faces]
    paths = []
    for vertices, d in zip(tri, distance, strict=True):
        crossings = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if (d[a] < 0 <= d[b]) or (d[b] < 0 <= d[a]):
                ratio = float(d[a] / (d[a] - d[b]))
                crossings.append(vertices[a] + ratio * (vertices[b] - vertices[a]))
        if len(crossings) == 2:
            pixels = []
            for point in crossings:
                offset = point - origin
                pixels.append((127.5 + (offset @ u) / 0.75, 127.5 + (offset @ v) / 0.75))
            (x1, y1), (x2, y2) = pixels
            paths.append(
                f"M{compact_float(x1, 1)} {compact_float(y1, 1)}L{compact_float(x2, 1)} {compact_float(y2, 1)}"
            )
    return "".join(paths)


def sampled_rings(points):
    assert points.shape == (18, 1202, 3)
    samples = points[:, [ring * 48 + az for ring in RING_IDS for az in AZIMUTH_IDS], :]
    return np.round(samples.reshape(18, len(RING_IDS), len(AZIMUTH_IDS), 3), 3).tolist()


def build(out):
    assert not out.exists(), "Use a fresh output directory"
    audit = json.loads((ROOT / AUDIT).read_text())
    assert sha(ROOT / AUDIT) == "cac57a80d5e037adc23e5a3024951663e6e926642cab23db029af1be85d4c770"
    pinned = audit["source_pins"]
    used = {str(AUDIT): sha(ROOT / AUDIT)}

    def verify(path):
        digest = sha(ROOT / path)
        assert pinned[str(path)] == digest, str(path)
        used[str(path)] = digest

    for path in (GEOMETRY, REVIEW, PREDICTION, STATIC):
        verify(path)
    geometry = json.loads((ROOT / GEOMETRY).read_text())
    assert geometry["frames"] == 18 and geometry["image_size"] == [256, 256]
    assert geometry["spacing_mm"] == 0.75 and geometry["pixel_center"] == 127.5
    source_views = []
    for view in range(4):
        frames = []
        for frame in range(1, 19):
            path = PUBLIC / f"view_{view}/frame_{frame:02}.png"
            verify(path)
            frames.append(image_data(ROOT / path))
        source_views.append(
            {"name": f"view_{view}", "frames": frames, "plane": geometry["planes"][view]}
        )
    with np.load(ROOT / REVIEW, allow_pickle=False) as pack:
        assert pack["images"].shape == (8, 18, 256, 256)
        assert pack["withheld"].tolist() == [2, 3, 4, 6]
        assert pack["images"].dtype == np.uint8
    private_geometry_path = Path("runs/br032-real-echo/private-review.json")
    verify(private_geometry_path)
    private_geometry = json.loads((ROOT / private_geometry_path).read_text())
    # Identical private-review pixels were already exported to pinned PNGs.
    review_names = ["long_45", "long_135", "short_45", "short_85"]
    review_views = []
    for j, name in enumerate(review_names):
        frames = []
        for frame in range(1, 19):
            path = Path(f"runs/br032-real-echo/review/images/p{[2, 3, 4, 6][j]}_f{frame - 1}.png")
            # The audit pins the review-plane PNG bytes where present; if a
            # different export layout was retained, fail rather than synthesize.
            assert (ROOT / path).exists(), str(path)
            verify(path)
            frames.append(image_data(ROOT / path))
        review_views.append(
            {"name": name, "frames": frames, "plane": private_geometry["planes"][[2, 3, 4, 6][j]]}
        )
    # The withheld planes are calibrated in private-review.json, not in the
    # public four-plane geometry file.
    with np.load(ROOT / PREDICTION, allow_pickle=False) as pack:
        points = np.asarray(pack["points"])
        faces = np.asarray(pack["faces"])
        alternatives = np.asarray(pack["alternative_points"])
    assert points.shape == (18, 1202, 3) and faces.shape == (2400, 3)
    assert alternatives.shape == (3, 18, 1202, 3)
    volume_ml = (
        np.einsum(
            "tij,tij->t",
            points[:, faces[:, 0]],
            np.cross(points[:, faces[:, 1]], points[:, faces[:, 2]]),
        )
        / 6000.0
    )
    assert np.allclose(volume_ml, audit["trials"]["sol-xhigh"]["volume_ml"], atol=1e-8)
    with np.load(ROOT / STATIC, allow_pickle=False) as pack:
        assert pack["points"].shape == (18, 300, 3)
    output = {
        "frame": "BR032-task-mm",
        "ring_sample_rule": "original vertex index ring*48+azimuth, rings 0,2,...,24; azimuths 0,3,...,45; display only",
        "primary_rings_mm": sampled_rings(points),
        "basal_alternative_rings_mm": sampled_rings(alternatives[2]),
        "primary_sections_px": [
            [section_path(points[t], faces, geometry["planes"][j]) for t in range(18)]
            for j in range(4)
        ],
        "basal_alternative_plane0_sections_px": [
            section_path(alternatives[2, t], faces, geometry["planes"][0]) for t in range(18)
        ],
        "volume_ml": [compact_float(v, 5) for v in audit["trials"]["sol-xhigh"]["volume_ml"]],
        "alternative_volume_ml": [
            [compact_float(v, 5) for v in row]
            for row in audit["trials"]["sol-xhigh"]["alternative_volume_ml"]
        ],
        "static_control_volume_ml": [
            compact_float(v, 5) for v in audit["trials"]["oracle"]["volume_ml"]
        ],
        "artifact_reward": {"primary": 1, "static_format_control": 1, "no_output": 0},
        "replay": audit["retained_replays"],
    }
    source = {
        "frame": "BR032-task-mm",
        "source_shape_T_rho_phi_theta": [18, 404, 76, 62],
        "image_shape_hw": [256, 256],
        "spacing_mm": 0.75,
        "pixel_center": 127.5,
        "times_seconds": geometry["times_seconds"],
        "task_axes": geometry["task_axes"],
        "views": source_views,
        "roles": "four solver-visible reslices of one real 3D acquisition; geometry is supplied; no contour/mesh supplied",
    }
    review = {
        "role": "reader-only withheld ultrasound images; no contour or 3D ground truth",
        "views": review_views,
        "primary_sections_px": [
            [section_path(points[t], faces, private_geometry["planes"][j]) for t in range(18)]
            for j in (2, 3, 4, 6)
        ],
        "intersection_frames": audit["intersection_frames"]["Agent reconstruction"],
    }
    for j, name in enumerate(review_names):
        observed = [t + 1 for t, section in enumerate(review["primary_sections_px"][j]) if section]
        assert observed == review["intersection_frames"][name]
    out.mkdir(parents=True)
    payloads = {"source.json": source, "output.json": output, "review.json": review}
    for name, payload in payloads.items():
        (out / name).write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    notice = (
        "# Local BR-032 teaching pack\n\nEchoSlicer v1.0 A_0.dcm, retained BR-032 reslices and "
        "saved original attempt. Local noncommercial interpretation only. Visible upstream records "
        "do not establish an onward redistribution license; keep raw and derived pixels local. "
        "Review planes are image-only and hidden until explicit reader reveal. "
        "No anatomy ground truth, clinical EF or disease truth is present.\n"
    )
    (out / "NOTICE.md").write_text(notice)
    assets = [
        {
            "file": name,
            "sha256": sha(out / name),
            "bytes": (out / name).stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if name == "review.json" else "illustration",
        }
        for name in (*payloads, "NOTICE.md")
    ]
    manifest = {
        "schema": 1,
        "id": "retained-real-echo-v1",
        "frame": "BR032-task-mm",
        "units": "mm",
        "license": "LicenseRef-EchoSlicer-research-local-terms-unresolved",
        "label_license": "LicenseRef-EchoSlicer-research-local-terms-unresolved",
        "reference_policy": "reader-reference-reveal",
        "source_class": "source-derived-teaching",
        "sources": used,
        "checks": {
            "native_frames": 18,
            "public_images": 72,
            "withheld_images": 72,
            "primary_vertices_per_frame": 1202,
            "primary_faces": 2400,
            "model_execution": False,
        },
        "assets": assets,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(out), "assets": assets}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output)
