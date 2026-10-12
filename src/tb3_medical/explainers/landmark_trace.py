"""Validate a retained landmark trace's native geometry and evidence roles."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable

from ..types import Document


def _vector(value: object) -> list[int | float]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(type(v) not in (int, float) or not math.isfinite(v) for v in value)
    ):
        raise ValueError("Landmark coordinates require three finite native values")
    return value


def _points(rows: list[Document], names: set[str], shape: list[int], *, reference: bool) -> None:
    if len({p["name"] for p in rows}) != len(rows):
        raise ValueError("Duplicate named landmark")
    for row in rows:
        if row["name"] not in names or row["status"] not in {
            "observed",
            "out_of_fov",
            "absent",
            "uncertain",
        }:
            raise ValueError("Unknown landmark name or status")
        point = row["ijk"]
        if point is None:
            if row["status"] == "observed":
                raise ValueError("Observed landmark lacks its native point")
            continue
        point = _vector(point)
        inside = all(0 <= v <= n - 1 for v, n in zip(point, shape, strict=True))
        if row["status"] == "observed" and not inside:
            raise ValueError("Observed landmark is outside the supplied crop")
        if row["status"] != "observed" and not (reference and row["status"] == "out_of_fov"):
            raise ValueError("Unavailable saved landmark cannot carry a point")
        if reference and row["status"] == "out_of_fov" and inside:
            raise ValueError("Outside reference point lies inside the crop")


def project_landmark(
    data: Document, attempt: str, decode: Callable[[str, int], bytes]
) -> tuple[tuple[str, ...], Document, Document]:
    """Only declared source/input, observed and reference fields enter the reader."""
    if data["attempt"] != attempt:
        raise ValueError("Landmark attempt identity mismatch")
    shape = data["shape"]
    preview = data["preview_shape"]
    indices = data["preview_indices"]
    if len(preview) != 3 or len(indices) != 3:
        raise ValueError("Landmark preview needs three native index axes")
    for n, count, axis in zip(shape, preview, indices, strict=True):
        if type(count) is not int or not 2 <= count <= n or len(axis) != count:
            raise ValueError("Landmark preview shape/index count mismatch")
        if any(type(i) is not int or not 0 <= i < n for i in axis) or axis != sorted(set(axis)):
            raise ValueError("Landmark preview indices must be increasing native samples")
        if axis[0] != 0 or axis[-1] != n - 1:
            raise ValueError("Landmark preview must span the whole supplied crop")
    decode(data["volume"], math.prod(preview))
    spacing = _vector(data["spacing"])
    expected = [math.sqrt(sum(data["affine"][r][c] ** 2 for r in range(3))) for c in range(3)]
    if any(
        s <= 0 or not math.isclose(s, e, rel_tol=1e-8)
        for s, e in zip(spacing, expected, strict=True)
    ):
        raise ValueError("Landmark spacing differs from native affine")
    window = data["preview_window_hu"]
    if (
        len(window) != 2
        or any(type(v) not in (int, float) or not math.isfinite(v) for v in window)
        or window[0] >= window[1]
    ):
        raise ValueError("Invalid retained CT display window")
    names = {row["name"] for row in data["names"]}
    if not names or len(names) != len(data["names"]):
        raise ValueError("Duplicate or empty supplied landmark names")
    for key, reference in (("points", False), ("reference_points", True)):
        rows = data[key]
        _points(rows, names, shape, reference=reference)
        if {p["name"] for p in rows} != names:
            raise ValueError("Saved/reference landmark inventory differs from requested names")
    trace_steps = {row["step"] for row in data["trace"]}
    for state in data["states"]:
        if state["trace_step"] not in trace_steps:
            raise ValueError("Landmark state lacks a retained trace step")
        if state["axis"] is not None and (
            type(state["axis"]) is not int or state["axis"] not in range(3)
        ):
            raise ValueError("Invalid native inspection axis")
        if state["bounds"] is not None:
            if len(state["bounds"]) != 2:
                raise ValueError("Inspection needs two half-open native bounds")
            lo, hi = map(_vector, state["bounds"])
            if any(not 0 <= a < b <= n for a, b, n in zip(lo, hi, shape, strict=True)):
                raise ValueError("Inspection bounds exceed supplied crop")
        if state["center_ijk"] is not None:
            centre = _vector(state["center_ijk"])
            if any(not 0 <= v <= n - 1 for v, n in zip(centre, shape, strict=True)):
                raise ValueError("Requested inspection centre is outside the supplied crop")
        radius = state["radius_mm"]
        if radius is not None and (
            type(radius) not in (int, float) or not math.isfinite(radius) or radius < 0
        ):
            raise ValueError("Requested inspection radius must be finite and nonnegative")
        levels = state["levels"]
        if levels and (
            state["axis"] is None
            or len(set(levels)) != len(levels)
            or any(type(k) is not int or not 0 <= k < shape[state["axis"]] for k in levels)
        ):
            raise ValueError("Inspection levels exceed their native axis")
        _points(state["points"], names, shape, reference=False)
        if state["kind"] == "saved" and state["points"] != data["points"]:
            raise ValueError("Saved state differs from retained submitted points")
    frozen = {
        key: data["frozen"][key]
        for key in (
            "contract_valid",
            "reward",
            "counts",
            "hallucinated",
            "correct_rejections",
            "success_counts_mm",
            "errors_mm",
        )
    }
    reference_by_name = {p["name"]: p for p in data["reference_points"]}
    saved_by_name = {p["name"]: p for p in data["points"]}
    if dict(Counter(p["status"] for p in data["reference_points"])) != frozen["counts"]:
        raise ValueError("Frozen denominators differ from the reference inventory")
    for status in ("out_of_fov", "absent"):
        affected = [p for p in data["reference_points"] if p["status"] == status]
        if frozen["hallucinated"][status] != sum(
            saved_by_name[p["name"]]["status"] == "observed" for p in affected
        ):
            raise ValueError("Frozen false-observed count differs from saved statuses")
        if frozen["correct_rejections"][status] != sum(
            saved_by_name[p["name"]]["status"] == status for p in affected
        ):
            raise ValueError("Frozen rejection count differs from saved statuses")
    diagnosis = data["wrong_level"]
    for key, rows, name_key in (
        ("claimed_ijk", saved_by_name, "claimed_name"),
        ("matched_ijk", reference_by_name, "matched_name"),
        ("outside_ijk", reference_by_name, "outside_name"),
    ):
        if diagnosis[key] != rows[diagnosis[name_key]]["ijk"]:
            raise ValueError("Wrong-level comparison differs from pinned named points")
    delta = [a - b for a, b in zip(diagnosis["claimed_ijk"], diagnosis["matched_ijk"], strict=True)]
    distance = math.sqrt(
        sum(sum(row[c] * delta[c] for c in range(3)) ** 2 for row in data["affine"][:3])
    )
    if not math.isclose(distance, diagnosis["separation_mm"], abs_tol=1e-6):
        raise ValueError("Wrong-level separation differs from native affine")
    return (
        (
            "shape",
            "affine",
            "spacing",
            "preview_shape",
            "preview_indices",
            "preview_window_hu",
            "volume",
            "names",
            "poster",
        ),
        {
            key: data[key]
            for key in (
                "states",
                "points",
                "trace",
                "elapsed_seconds",
                "steps_in_trace",
                "evidence",
            )
        },
        {"points": data["reference_points"], "frozen": frozen, "wrong_level": diagnosis},
    )
