#!/usr/bin/env python3
"""Reconstruct a case-specific dynamic LV blood-pool surface.

The input contains no contours or reference model.  This script therefore uses a
small, explicitly documented set of image measurements made on the supplied
calibrated views.  The numbers below are millimetre measurements of the inner
blood/tissue transition, not a learned or imported cardiac shape.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


# Per-frame observations after inspecting all four synchronized views.  r1/r2
# are cavity semi-diameters at the well-seen z=+15 mm transverse plane.  z_base
# is the inferred mitral annular closure and z_apex the deepest endocardial tip.
# c1/c2 are the cavity centre at z=+15 mm.  Coordinates use geometry.json's
# (transverse_1, transverse_2, depth) orthonormal basis.
OBSERVED = {
    "r1": np.array([25.0, 22.5, 29.5, 31.5, 24.5, 24.0,
                    25.5, 22.5, 30.0, 32.0, 24.0, 23.5,
                    27.0, 22.0, 30.5, 31.0, 24.0, 23.0]),
    "r2": np.array([31.0, 26.0, 35.0, 37.0, 28.0, 27.0,
                    31.5, 26.5, 35.5, 38.0, 27.5, 27.0,
                    33.0, 25.5, 36.5, 37.0, 27.5, 26.0]),
    "z_base": np.array([-2.6, -0.6, -9.4, -11.6, -1.1, -1.9,
                        -2.8, -0.4, -9.0, -12.0, -0.8, -1.5,
                        -3.4, 0.0, -9.8, -11.2, -1.0, -1.3]),
    "z_apex": np.array([46.9, 43.5, 48.8, 49.5, 45.0, 45.8,
                        47.2, 43.2, 48.5, 50.0, 45.2, 45.5,
                        47.8, 43.0, 49.0, 49.4, 45.6, 45.2]),
    "c1": np.array([11.0, 9.0, 12.0, 15.0, 11.0, 12.0,
                    11.5, 9.5, 12.0, 15.5, 11.0, 11.5,
                    12.0, 9.0, 12.5, 14.5, 11.0, 11.0]),
    "c2": np.array([19.0, 14.0, 18.0, 20.0, 18.0, 20.0,
                    19.5, 14.5, 18.5, 20.5, 18.0, 19.5,
                    20.0, 13.5, 19.0, 20.0, 18.0, 19.0]),
}


def interp_profile(s: np.ndarray, basal_variant: bool = False) -> np.ndarray:
    """Smooth dimensionless LV radius profile from annulus (0) to apex (1)."""
    knots = np.array([0.00, 0.10, 0.30, 0.48, 0.66, 0.82, 0.93, 0.975, 1.00])
    if basal_variant:
        vals = np.array([1.00, 1.02, 1.01, 0.94, 0.80, 0.58, 0.34, 0.16, 0.00])
    else:
        vals = np.array([0.86, 0.95, 1.00, 0.95, 0.82, 0.61, 0.36, 0.17, 0.00])
    # Linear interpolation on a dense longitudinal sampling is preferable here
    # to a high-order polynomial, which can overshoot and create necks.
    return np.interp(s, knots, vals)


def make_faces(n_rings: int, n_theta: int) -> np.ndarray:
    """Closed genus-zero topology: planar basal fan, rings, apical fan."""
    faces: list[list[int]] = []
    cap = 0
    first = 1
    # Outward cap normal points toward decreasing depth.
    for j in range(n_theta):
        faces.append([cap, first + (j + 1) % n_theta, first + j])
    for i in range(n_rings - 1):
        a0 = first + i * n_theta
        b0 = first + (i + 1) * n_theta
        for j in range(n_theta):
            jn = (j + 1) % n_theta
            faces.append([a0 + j, a0 + jn, b0 + j])
            faces.append([a0 + jn, b0 + jn, b0 + j])
    apex = first + n_rings * n_theta
    last = first + (n_rings - 1) * n_theta
    for j in range(n_theta):
        faces.append([last + j, last + (j + 1) % n_theta, apex])
    return np.asarray(faces, dtype=np.int32)


def make_frame_points(
    frame: int,
    origin: np.ndarray,
    e1: np.ndarray,
    e2: np.ndarray,
    depth: np.ndarray,
    n_rings: int,
    n_theta: int,
    radial_scale: float = 1.0,
    base_shift: float = 0.0,
    apex_shift: float = 0.0,
    basal_variant: bool = False,
) -> np.ndarray:
    z0 = float(OBSERVED["z_base"][frame] + base_shift)
    za = float(OBSERVED["z_apex"][frame] + apex_shift)
    s_rings = np.linspace(0.0, 0.975, n_rings)
    z = z0 + (za - z0) * s_rings
    s15 = np.clip((15.0 - z0) / (za - z0), 0.05, 0.90)
    prof = interp_profile(s_rings, basal_variant)
    p15 = float(interp_profile(np.array([s15]), basal_variant)[0])
    # Preserve the directly observed +15 mm radii for the basal-plane variant.
    amp1 = radial_scale * float(OBSERVED["r1"][frame]) / p15
    amp2 = radial_scale * float(OBSERVED["r2"][frame]) / p15

    # A shallow bowed centreline matches the centroids in both long axes while
    # avoiding an unsupported rigid translation of the whole cavity.
    c1_15 = float(OBSERVED["c1"][frame])
    c2_15 = float(OBSERVED["c2"][frame])
    bow = 1.0 - ((s_rings - s15) / max(s15, 1.0 - s15)) ** 2
    bow = np.clip(bow, -0.45, 1.0)
    c1 = c1_15 - 3.0 + 3.0 * bow
    c2 = c2_15 - 3.5 + 3.5 * bow

    theta = np.linspace(0.0, 2.0 * np.pi, n_theta, endpoint=False)
    # Slight second-harmonic modulation expresses the observed non-elliptical
    # inner boundary without reproducing individual speckle or papillary echoes.
    shape = 1.0 + 0.035 * np.cos(2.0 * theta - 0.45)
    rows = []
    for i, ss in enumerate(s_rings):
        rr1 = amp1 * prof[i]
        rr2 = amp2 * prof[i]
        ring = (
            origin[None, :]
            + (c1[i] + rr1 * shape * np.cos(theta))[:, None] * e1[None, :]
            + (c2[i] + rr2 * shape * np.sin(theta))[:, None] * e2[None, :]
            + z[i] * depth[None, :]
        )
        rows.append(ring)

    base_center = origin + c1[0] * e1 + c2[0] * e2 + z0 * depth
    apex_c1 = c1_15 - 3.0
    apex_c2 = c2_15 - 3.5
    apex = origin + apex_c1 * e1 + apex_c2 * e2 + za * depth
    return np.vstack([base_center[None, :], np.vstack(rows), apex[None, :]])


def signed_volume_mm3(points: np.ndarray, faces: np.ndarray) -> float:
    tri = points[faces]
    return float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0)


def triangle_plane_segments(points: np.ndarray, faces: np.ndarray, plane_o: np.ndarray,
                            plane_n: np.ndarray, tol: float = 1e-7):
    """Return (face index, p0, p1) segments cut by a plane."""
    dist = (points - plane_o) @ plane_n
    out = []
    for fi, face in enumerate(faces):
        ids = face.tolist()
        vals = dist[ids]
        hits = []
        for k in range(3):
            ia, ib = ids[k], ids[(k + 1) % 3]
            da, db = dist[ia], dist[ib]
            pa, pb = points[ia], points[ib]
            if abs(da) <= tol:
                hits.append(pa)
            if da * db < -(tol * tol):
                hits.append(pa + (pb - pa) * (da / (da - db)))
        unique = []
        for p in hits:
            if not any(np.linalg.norm(p - q) < 1e-5 for q in unique):
                unique.append(p)
        if len(unique) >= 2:
            out.append((fi, unique[0], unique[1]))
    return out


def save_overlays(input_dir: Path, output_dir: Path, points: np.ndarray,
                  faces: np.ndarray, geometry: dict, n_theta: int) -> None:
    root = output_dir / "overlays"
    root.mkdir(parents=True, exist_ok=True)
    for vi, plane in enumerate(geometry["planes"]):
        view_out = root / plane["name"]
        view_out.mkdir(exist_ok=True)
        po = np.asarray(plane["origin"], float)
        pu = np.asarray(plane["u"], float)
        pv = np.asarray(plane["v"], float)
        pn = np.cross(pu, pv)
        frames_for_sheet = []
        for f in range(points.shape[0]):
            src = input_dir / plane["name"] / f"frame_{f + 1:02d}.png"
            gray = cv2.imread(str(src), cv2.IMREAD_GRAYSCALE)
            if gray is None:
                raise FileNotFoundError(src)
            canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            segs = triangle_plane_segments(points[f], faces, po, pn)
            for fi, p, q in segs:
                pix = []
                for xyz in (p, q):
                    col = geometry["pixel_center"] + np.dot(xyz - po, pu) / geometry["spacing_mm"]
                    row = geometry["pixel_center"] + np.dot(xyz - po, pv) / geometry["spacing_mm"]
                    pix.append((int(round(col)), int(round(row))))
                color = (255, 255, 0) if fi < n_theta else (40, 40, 255)
                cv2.line(canvas, pix[0], pix[1], color, 1, cv2.LINE_AA)
            label = f"F{f + 1:02d} red=LV section cyan=basal cap"
            cv2.rectangle(canvas, (0, 0), (230, 16), (0, 0, 0), -1)
            cv2.putText(canvas, label, (3, 12), cv2.FONT_HERSHEY_SIMPLEX,
                        0.32, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imwrite(str(view_out / f"frame_{f + 1:02d}.png"), canvas)
            frames_for_sheet.append(canvas)
        sheet = np.zeros((3 * 256, 6 * 256, 3), np.uint8)
        for k, im in enumerate(frames_for_sheet):
            sheet[(k // 6) * 256:(k // 6 + 1) * 256,
                  (k % 6) * 256:(k % 6 + 1) * 256] = im
        cv2.imwrite(str(root / f"contact_{plane['name']}.jpg"), sheet,
                    [cv2.IMWRITE_JPEG_QUALITY, 94])


def validate(points: np.ndarray, faces: np.ndarray) -> dict:
    if not np.isfinite(points).all():
        raise ValueError("non-finite coordinates")
    if faces.min() < 0 or faces.max() >= points.shape[1]:
        raise ValueError("face index out of range")
    edges = Counter()
    for tri in faces:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edges[tuple(sorted((int(a), int(b))))] += 1
    bad_edges = sum(v != 2 for v in edges.values())
    signed = np.array([signed_volume_mm3(p, faces) for p in points])
    if bad_edges:
        raise ValueError(f"mesh is not edge-closed: {bad_edges} bad edges")
    if np.any(signed <= 0):
        raise ValueError("mesh orientation is not consistently outward")
    return {
        "vertices": int(points.shape[1]),
        "triangles": int(faces.shape[0]),
        "nonmanifold_or_boundary_edges": int(bad_edges),
        "signed_volume_positive_all_frames": True,
    }


def write_method(path: Path, volumes: np.ndarray, alt_volumes: np.ndarray) -> None:
    frac = (volumes.max() - volumes.min()) / volumes.max()
    text = f"""# Dynamic LV blood-pool reconstruction

## Image evidence and chamber choice

The reconstruction uses only the 72 supplied PNG reslices and `geometry.json`.
The two views sharing the depth direction were read as long-axis views.  Their
deeper chamber, bounded by a bright, relatively thick apical wall, changes in
concert with the dark lumen in `view_3` (the +15 mm transverse plane).  That
coherent chamber was identified as the LV blood pool.  The large shallower dark
region was excluded as atrial-side blood pool rather than being allowed to make
the reconstruction into the whole heart.  `view_2`, at -25 mm, has no stable
LV-like anechoic lumen and was used primarily as a negative constraint on the
basal extent.

Across all views the observed sequence repeats approximately every six sampled
volumes: minimum lumen near frames 2/8/14, rapid opening by 3/9/15, maximum near
4/10/16, then contraction through the following samples.  The reconstruction
uses separate measurements for all 18 frames; it does not evaluate a decorative
sine wave.

## Segmentation, geometry, and deformation

For each frame, inner blood/tissue transitions were inspected in both long axes
and in the +15 mm transverse slice.  The transverse semi-diameters and centroid,
and the long-axis basal and apical depths, are the case-specific observations
listed explicitly in `solve.py`.  Papillary/trabecular echoes inside the lumen
were not treated as an outer myocardial boundary; the mesh follows the enclosing
endocardial blood-pool envelope.  A smooth stack of mildly non-elliptical rings
interpolates those observations from annulus to apex.  Ring vertex number and
azimuth are held fixed through time, giving geometric correspondence only.

No image resizing or guessed voxel size enters the 3-D result.  Each mesh point
is composed in the orthonormal `transverse_1`, `transverse_2`, and `depth` axes
from `geometry.json`, in millimetres.  The given origins and 0.75 mm pixel spacing
are used again when projecting mesh/plane intersections into the saved overlays.

## Basal convention and closure

The basal boundary is an inferred mitral-annular closure, approximately
perpendicular to the supplied depth axis and moving longitudinally frame by
frame.  In the primary interpretation its depth coordinate ranges from
{OBSERVED['z_base'].min():.1f} to {OBSERVED['z_base'].max():.1f} mm, whereas the
apical tip ranges from {OBSERVED['z_apex'].min():.1f} to
{OBSERVED['z_apex'].max():.1f} mm.  Thus the -25 mm transverse view remains on
the atrial side of the cap and the +15 mm view crosses the LV.  The first 48 rim
vertices are closed by a planar triangle fan to a
dedicated cap-centre vertex.  This synthetic cap is a measurement convention,
not imaged endocardium or an anatomic valve surface.  The opposite end converges
to one inferred apical vertex.  Triangle winding was constructed outward and
checked using positive signed volume; every undirected edge has exactly two
incident triangles.

## Weakly observed regions and alternatives

Only four planes constrain a 3-D surface.  The largest uncertainty is between
planes, followed by the blood/tissue edge around internal papillary echoes and
the location of the basal closure when the valve region is open.  The alternatives
retain identical connectivity and observed timing:

1. **Conservative inner envelope:** radii 8% smaller, base 2 mm apical, apex 1 mm
   basalward.
2. **Generous outer envelope:** radii 8% larger, base 2 mm atrialward, apex 1.5 mm
   deeper.
3. **Basal-inclusion variant:** the base is 6 mm farther atrialward and the basal
   profile is fuller while preserving the measured +15 mm transverse diameters.

Primary mesh volumes range from {volumes.min():.2f} to {volumes.max():.2f} mL.
The resulting fractional cavity-volume change is {frac:.3f}; this is only this
model's geometric estimate, not a validated clinical ejection fraction.  Across
all alternative/frame combinations the volume range is
{alt_volumes.min():.2f}-{alt_volumes.max():.2f} mL.

## What cannot be concluded

The sparse reslices cannot establish unique out-of-plane anatomy, material point
identity, myocardial strain, clinical EF, hemodynamics, active-force equilibrium,
diagnosis, or outcome.  In particular, persistent mesh indices are geometric
correspondence and must not be interpreted as tracked myocardial tissue.
"""
    path.write_text(text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path, help="directory containing geometry.json and view_* folders")
    ap.add_argument("--output", required=True, type=Path, help="output directory")
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    geometry = json.loads((args.input / "geometry.json").read_text())
    if int(geometry["frames"]) != 18:
        raise ValueError("This case-specific solver expects the supplied 18-frame acquisition")

    origin = np.asarray(geometry["planes"][0]["origin"], float)
    e1 = np.asarray(geometry["task_axes"]["transverse_1"], float)
    e2 = np.asarray(geometry["task_axes"]["transverse_2"], float)
    depth = np.asarray(geometry["task_axes"]["depth"], float)
    basis = np.column_stack([e1, e2, depth])
    if not np.allclose(basis.T @ basis, np.eye(3), atol=1e-6):
        raise ValueError("task axes are not orthonormal")

    n_rings, n_theta = 25, 48
    faces = make_faces(n_rings, n_theta)
    primary = np.stack([
        make_frame_points(f, origin, e1, e2, depth, n_rings, n_theta)
        for f in range(18)
    ]).astype(np.float64)
    alternatives = np.stack([
        np.stack([make_frame_points(f, origin, e1, e2, depth, n_rings, n_theta,
                                    radial_scale=0.92, base_shift=2.0, apex_shift=-1.0)
                  for f in range(18)]),
        np.stack([make_frame_points(f, origin, e1, e2, depth, n_rings, n_theta,
                                    radial_scale=1.08, base_shift=-2.0, apex_shift=1.5)
                  for f in range(18)]),
        np.stack([make_frame_points(f, origin, e1, e2, depth, n_rings, n_theta,
                                    radial_scale=1.0, base_shift=-6.0,
                                    basal_variant=True)
                  for f in range(18)]),
    ]).astype(np.float64)

    checks = validate(primary, faces)
    for alt in alternatives:
        validate(alt, faces)
    np.savez_compressed(args.output / "prediction.npz", points=primary,
                        faces=faces, alternative_points=alternatives)

    volumes = np.array([signed_volume_mm3(p, faces) / 1000.0 for p in primary])
    alt_volumes = np.array([[signed_volume_mm3(p, faces) / 1000.0 for p in alt]
                            for alt in alternatives])
    local_max = [4, 10, 16]
    local_min = [2, 8, 14]
    summary = {
        "frame_ids": list(range(1, 19)),
        "times_seconds": geometry["times_seconds"],
        "volume_ml": [round(float(v), 6) for v in volumes],
        "inferred_extrema": {
            "largest_cavity": {
                "global_frame_id": int(np.argmax(volumes) + 1),
                "global_time_seconds": float(geometry["times_seconds"][int(np.argmax(volumes))]),
                "global_volume_ml": round(float(volumes.max()), 6),
                "recurrent_local_frame_ids": local_max,
                "basis": "largest observed long-axis extent and +15 mm transverse lumen"
            },
            "smallest_cavity": {
                "global_frame_id": int(np.argmin(volumes) + 1),
                "global_time_seconds": float(geometry["times_seconds"][int(np.argmin(volumes))]),
                "global_volume_ml": round(float(volumes.min()), 6),
                "recurrent_local_frame_ids": local_min,
                "basis": "smallest coherent deeper LV lumen across synchronized views"
            }
        },
        "model_geometric_fractional_cavity_volume_change": round(float((volumes.max() - volumes.min()) / volumes.max()), 6),
        "model_geometric_fractional_cavity_volume_change_warning": "Model-derived geometric estimate only; not a validated clinical EF.",
        "basal_cap": {
            "declared": True,
            "type": "planar triangle fan at the inferred mitral-annular closure",
            "cap_center_vertex_index": 0,
            "rim_vertex_indices_zero_based": list(range(1, n_theta + 1)),
            "cap_face_indices_zero_based": list(range(0, n_theta)),
            "normal_direction": "approximately negative task depth (atrialward)"
        },
        "alternatives": [
            {"index": 0, "meaning": "conservative inner blood-pool envelope and shorter long axis",
             "volume_ml": [round(float(v), 6) for v in alt_volumes[0]]},
            {"index": 1, "meaning": "generous outer blood-pool envelope and longer long axis",
             "volume_ml": [round(float(v), 6) for v in alt_volumes[1]]},
            {"index": 2, "meaning": "more atrial basal closure with fuller basal interpolation",
             "volume_ml": [round(float(v), 6) for v in alt_volumes[2]]}
        ],
        "assumptions": [
            "The deeper thick-walled chamber coherent with view_3 is the LV; the shallower chamber is excluded.",
            "The mitral closure is approximated by a plane normal to the supplied depth axis.",
            "Between-plane sections are smooth mildly non-elliptical rings; four planes do not determine a unique surface.",
            "Internal papillary/trabecular echoes do not redefine the enclosing blood-pool boundary.",
            "Persistent vertex indices indicate geometric correspondence, not established material identity."
        ],
        "uncertainty": {
            "dominant_sources": ["between-plane shape", "blood/tissue contour placement", "basal closure"],
            "quantified_by": "three same-connectivity alternative_points variants",
            "alternative_volume_range_ml_all_frames": [round(float(alt_volumes.min()), 6), round(float(alt_volumes.max()), 6)]
        },
        "mesh_validation": checks,
        "alternatives_validated_closed_outward_and_same_topology": True,
        "units": {"points": "mm", "volume_ml": "mL"}
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_method(args.output / "method.md", volumes, alt_volumes)
    save_overlays(args.input, args.output, primary, faces, geometry, n_theta)


if __name__ == "__main__":
    main()
