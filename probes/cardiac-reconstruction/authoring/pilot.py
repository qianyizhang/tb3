"""CPU author feasibility pilot: native FeEcho4D radial masks to an LV mesh.

This is contour-conditioned reconstruction, not an independent model trial or
video segmentation. Held-out masks are read only by evaluation. A dense-view
reconstruction is a derived comparator, never independent 3D ground truth.
Run with numpy, scipy and pillow; tested versions are recorded in results.json.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import scipy
from scipy.ndimage import map_coordinates, binary_erosion, distance_transform_edt
from PIL import Image

VIEWS = {"one": [0], "two": [0, 18], "four": [0, 9, 18, 27],
         "eight": [0, 4, 9, 13, 18, 22, 27, 31], "dense": list(range(36))}
HOLDOUT = [2, 7, 11, 16, 20, 25, 29, 34]
NPOLAR, NAZIMUTH = 65, 72


def mask_file(root, view, frame):
    return root / "mask" / f"Patient001_slice{view + 1:03d}time{frame + 1:03d}.png"


def read_mask(root, view, frame):
    return np.asarray(Image.open(mask_file(root, view, frame))) == 127


def ray_profile(mask, cx, cy, positive):
    phi = np.linspace(0, np.pi, NPOLAR)
    radii = np.arange(0, max(mask.shape), 0.5)
    xx = cx + (1 if positive else -1) * np.sin(phi)[:, None] * radii
    yy = cy + np.cos(phi)[:, None] * radii
    inside = map_coordinates(mask.astype(float), [yy, xx], order=0,
                             mode="constant", cval=0) > 0.5
    # A star-shaped prior: fill concavities along rays. Its errors are scored.
    return np.max(np.where(inside, radii[None, :] + 0.25, 0), axis=1)


def reconstruct(root, frames, views, cx, cy):
    query_theta = np.arange(NAZIMUTH) * 2 * np.pi / NAZIMUTH
    out = []
    for frame in range(frames):
        observed, angles = [], []
        for view in views:
            mask = read_mask(root, view, frame)
            for positive, shift in [(True, 0), (False, np.pi)]:
                observed.append(ray_profile(mask, cx, cy, positive))
                angles.append(view * np.pi / 36 + shift)
        profiles = np.array(observed)
        order = np.argsort(angles)
        angles = np.array(angles)[order]
        profiles = profiles[order]
        full = np.stack([np.interp(query_theta, angles, profiles[:, j], period=2 * np.pi)
                         for j in range(NPOLAR)], axis=1)
        # A single pole at each end of the long axis; no duplicated pole vertices.
        full[:, 0] = np.mean(profiles[:, 0])
        full[:, -1] = np.mean(profiles[:, -1])
        out.append(full)
    return np.asarray(out)


def render_mask(profile, view, shape, cx, cy):
    yy, xx = np.indices(shape)
    dx, dy = xx - cx, yy - cy
    phi = np.arctan2(np.abs(dx), dy)
    theta = view * np.pi / 36
    positive = np.interp(np.arange(NPOLAR), np.arange(NPOLAR), profile[int(round(theta / (2 * np.pi) * NAZIMUTH)) % NAZIMUTH])
    negative = profile[(int(round(theta / (2 * np.pi) * NAZIMUTH)) + NAZIMUTH // 2) % NAZIMUTH]
    rpos = np.interp(phi, np.linspace(0, np.pi, NPOLAR), positive)
    rneg = np.interp(phi, np.linspace(0, np.pi, NPOLAR), negative)
    return np.hypot(dx, dy) <= np.where(dx >= 0, rpos, rneg)


def mesh(profile, spacing):
    phi = np.linspace(0, np.pi, NPOLAR)[1:-1]
    theta = np.arange(NAZIMUTH) * 2 * np.pi / NAZIMUTH
    r = profile[:, 1:-1].T
    xx = r * np.sin(phi)[:, None] * np.cos(theta)
    zz = r * np.sin(phi)[:, None] * np.sin(theta)
    yy = r * np.cos(phi)[:, None] * np.ones_like(theta)
    vertices = np.concatenate([[[0, profile[0, 0], 0]],
                               np.stack([xx, yy, zz], axis=-1).reshape(-1, 3),
                               [[0, -profile[0, -1], 0]]]) * spacing
    faces = []
    rings = NPOLAR - 2
    bottom = len(vertices) - 1
    for a in range(NAZIMUTH):
        b = (a + 1) % NAZIMUTH
        faces.append([0, 1 + a, 1 + b])
        for ring in range(rings - 1):
            u, v = 1 + ring * NAZIMUTH, 1 + (ring + 1) * NAZIMUTH
            faces.extend([[u + a, v + a, v + b], [u + a, v + b, u + b]])
        u = 1 + (rings - 1) * NAZIMUTH
        faces.append([u + b, u + a, bottom])
    faces = np.array(faces)
    if signed_volume(vertices, faces) < 0:
        faces = faces[:, ::-1]
    return vertices, faces


def signed_volume(vertices, faces):
    tri = vertices[faces]
    return np.sum(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2]))) / 6


def dice(a, b):
    return float(2 * np.sum(a & b) / max(1, np.sum(a) + np.sum(b)))


def summary(values):
    return {"mean": float(np.mean(values)), "min": float(np.min(values)),
            "p05": float(np.quantile(values, 0.05)), "p95": float(np.quantile(values, 0.95)),
            "max": float(np.max(values))}


def ef(volumes, ed, es):
    return float(100 * (1 - volumes[es] / volumes[ed]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    shape = read_mask(args.source, 0, 0).shape
    frames, spacing, ed, es = 30, 0.089950, 1, 16
    # Origin determined from the first provided plane only, across its frames.
    # Supplied radial geometry establishes the image midpoint as the rotation axis.
    cx = (shape[1] - 1) / 2
    ranges = [np.where(read_mask(args.source, 0, t)[:, int(cx)])[0] for t in range(frames)]
    cy = (max(x.min() for x in ranges) + min(x.max() for x in ranges)) / 2
    assert all(read_mask(args.source, 0, t)[int(cy), int(cx)] for t in range(frames))
    assert all(not set(v) & set(HOLDOUT) for k, v in VIEWS.items() if k != "dense")
    profiles, meshes, curves, stats = {}, {}, {}, {}
    # Freeze each sparse prediction first; dense comparator and evaluation follow.
    for name, views in VIEWS.items():
        profiles[name] = reconstruct(args.source, frames, views, cx, cy)
        ms = [mesh(p, spacing) for p in profiles[name]]
        meshes[name] = np.array([m[0] for m in ms])
        faces = ms[0][1]
        curves[name] = np.array([signed_volume(v, faces) / 1000 for v in meshes[name]])
        np.savez_compressed(args.output / f"{name}-mesh.npz", vertices=meshes[name], faces=faces,
                            radius_px=profiles[name], volume_ml=curves[name])
    # Static negative control copies the first frame of the four-view prediction.
    profiles["static"] = np.repeat(profiles["four"][:1], frames, axis=0)
    meshes["static"] = np.repeat(meshes["four"][:1], frames, axis=0)
    curves["static"] = np.repeat(curves["four"][:1], frames)
    for name, ps in profiles.items():
        held_dice, held_hd95, observed_dice = [], [], []
        for frame in range(frames):
            for view in HOLDOUT:
                truth = read_mask(args.source, view, frame)
                pred = render_mask(ps[frame], view, shape, cx, cy)
                held_dice.append(dice(truth, pred))
                ta = truth ^ binary_erosion(truth)
                pa = pred ^ binary_erosion(pred)
                distances = np.r_[distance_transform_edt(~ta)[pa], distance_transform_edt(~pa)[ta]] * spacing
                held_hd95.append(float(np.quantile(distances, 0.95)))
            for view in VIEWS.get(name, [0]):
                observed_dice.append(dice(read_mask(args.source, view, frame), render_mask(ps[frame], view, shape, cx, cy)))
        vertices = meshes[name]
        edge_pairs = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
        _, edge_counts = np.unique(edge_pairs, axis=0, return_counts=True)
        areas = np.linalg.norm(np.cross(vertices[:, faces[:, 1]] - vertices[:, faces[:, 0]],
                                       vertices[:, faces[:, 2]] - vertices[:, faces[:, 0]]), axis=-1) / 2
        stats[name] = {
            "input_planes_1based": [v + 1 for v in VIEWS.get(name, VIEWS['four'])],
            "heldout_dice": summary(held_dice), "heldout_hd95_mm": summary(held_hd95),
            "observed_dice": summary(observed_dice),
            "ef_at_source_phases_percent": ef(curves[name], ed, es),
            "ef_error_vs_dense_reference_pp": abs(ef(curves[name], ed, es) - ef(curves['dense'], ed, es)),
            "volume_curve_mape_vs_dense_percent": float(100 * np.mean(np.abs(curves[name] / curves['dense'] - 1))),
            "max_volume_frame_1based": int(np.argmax(curves[name])) + 1,
            "min_volume_frame_1based": int(np.argmin(curves[name])) + 1,
            "volume_at_source_ed_ml": float(curves[name][ed]),
            "volume_at_source_es_ml": float(curves[name][es]),
            "mesh_boundary_edges": int(sum(edge_counts == 1)),
            "mesh_nonmanifold_edges": int(sum(edge_counts > 2)),
            "degenerate_triangle_count": int((areas < 1e-10).sum()),
            "min_signed_volume_ml": float(curves[name].min()),
            "framewise_displacement_p95_mm": float(np.quantile(np.linalg.norm(np.diff(vertices, axis=0), axis=-1), .95)),
        }
    # Exact missing-depth control: scale the unobserved z dimension; the z=0
    # section is unchanged. Smooth phase variation changes volume and EF.
    scale = 1 + 0.25 * np.cos(2 * np.pi * (np.arange(frames) - ed) / frames)
    modified = meshes['one'].copy()
    modified[:, :, 2] *= scale[:, None]
    amb_curve = np.array([signed_volume(v, faces) / 1000 for v in modified])
    assert np.allclose(amb_curve, curves['one'] * scale)
    on_plane = np.isclose(meshes['one'][:, :, 2], 0, atol=1e-10)
    assert np.allclose(modified[on_plane], meshes['one'][on_plane], rtol=0, atol=1e-12)
    # A separate closed-form sphere checks mesh orientation and volume integration.
    sph, sf = mesh(np.full((NAZIMUTH, NPOLAR), 10.0), 1.0)
    sphere_error = abs(signed_volume(sph, sf) / (4 / 3 * np.pi * 1000) - 1)
    assert sphere_error < 0.005
    result = {
        "kind": "author_feasibility_not_model_trial", "source_patient": "Patient001",
        "source_record": "https://zenodo.org/records/21322299",
        "frames": frames, "native_planes": 37, "unique_planes_used": 36,
        "excluded_plane_37": "180-degree duplicate direction; annotations not identical after mirroring",
        "input_geometry": {"axis_x_px": cx, "origin_y_px_from_plane1_only": cy,
                           "in_plane_spacing_mm": spacing, "angular_step_deg": 5,
                           "angular_step_basis": "37 source planes span 0..180 degrees; source radial slicing convention"},
        "source_ed_1based": ed + 1, "source_es_1based": es + 1,
        "source_phases_used_by_reconstruction": False,
        "heldout_planes_1based": [v + 1 for v in HOLDOUT],
        "heldout_frame_plane_pairs": frames * len(HOLDOUT),
        "dense_comparator_is_independent_3d_truth": False,
        "vertex_correspondence_is_material_tracking": False,
        "absolute_volume_status": "Derived from documented pixel spacing and assumed radial pose; not independently validated",
        "blood_flow_or_disease_evaluated": False,
        "stats": stats,
        "missing_depth_control": {"scale_range": [float(scale.min()), float(scale.max())],
                                  "same_observed_plane_exactly": True,
                                  "original_ef_percent": ef(curves['one'], ed, es),
                                  "modified_ef_percent": ef(amb_curve, ed, es),
                                  "difference_pp": abs(ef(curves['one'], ed, es) - ef(amb_curve, ed, es))},
        "independent_sphere_relative_volume_error": float(sphere_error),
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
    }
    (args.output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.output / 'curves.json').write_text(json.dumps({k: v.tolist() for k, v in curves.items()}) + '\n')
    for k, s in stats.items():
        print(k, json.dumps({z: s[z] for z in ['heldout_dice', 'ef_at_source_phases_percent', 'ef_error_vs_dense_reference_pp', 'volume_curve_mape_vs_dense_percent', 'degenerate_triangle_count']}), flush=True)
    print('missing_depth', result['missing_depth_control'], 'elapsed_s', result['elapsed_seconds'])


if __name__ == '__main__':
    main()
