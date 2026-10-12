"""Validate a retained coronary repair and source-linked CPR without rerunning it."""

from __future__ import annotations

import math
import struct
from collections.abc import Callable
from itertools import pairwise

from ..types import Document
from .landmark_trace import _vector


def _shape(value: object) -> list[int]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(type(v) is not int or v < 1 for v in value)
    ):
        raise ValueError("Coronary array needs three positive integer dimensions")
    return value


def _finite(values: list[int | float]) -> None:
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise ValueError("Coronary coordinates or samples are not finite")


def _indices(values: list[int], size: int) -> set[int]:
    if any(type(v) is not int or not 0 <= v < size for v in values) or len(set(values)) != len(
        values
    ):
        raise ValueError("Coronary native voxel indices are invalid or repeated")
    return set(values)


def project_coronary(
    data: Document,
    attempt: str,
    decode: Callable[[str, int], bytes],
    matrix: Callable[[list[list[int | float]]], None],
) -> Document:
    """Keep supplied context, original outputs and later author correction distinct."""
    if data["attempt"] != attempt:
        raise ValueError("Coronary trace attempt differs")
    raw_input, raw_observed, raw_reference = data["input"], data["observed"], data["reference"]
    inp = {
        k: raw_input[k]
        for k in (
            "shape",
            "affine",
            "spacing",
            "preview_shape",
            "preview_indices",
            "preview_window",
            "volume",
            "detail_origin",
            "detail_shape",
            "detail_volume",
            "poster",
            "mask_indices",
            "editable_indices",
            "start_ras",
            "end_ras",
            "review_ras",
        )
    }
    obs = {
        k: raw_observed[k]
        for k in (
            "states",
            "bridge_ijk",
            "added_indices",
            "removed_indices",
            "centerline_ras",
            "cpr",
            "mesh",
            "trace",
            "elapsed_seconds",
            "steps_in_trace",
            "evidence",
        )
    }
    ref = {
        k: raw_reference[k]
        for k in (
            "reward",
            "stages",
            "metrics",
            "corrected_arc_mm",
            "correction_stages",
            "correction_only_arc",
            "limits",
        )
    }
    obs["cpr"] = {
        k: obs["cpr"][k]
        for k in ("shape", "angles_deg", "offsets_mm", "arc_mm", "hu", "source_ras_mm")
    }
    obs["mesh"] = {k: obs["mesh"][k] for k in ("vertex_count", "face_count", "vertices", "faces")}
    obs["states"] = [
        {
            k: row[k]
            for k in (
                "id",
                "label",
                "kind",
                "trace_step",
                "axis",
                "levels",
                "bounds",
                "center_ijk",
                "description",
                "delivered_step",
            )
        }
        for row in obs["states"]
    ]
    obs["trace"] = [
        {k: row[k] for k in ("step", "timestamp", "calls", "output")} for row in obs["trace"]
    ]
    shape, preview = _shape(inp["shape"]), _shape(inp["preview_shape"])
    matrix(inp["affine"])
    spacing = _vector(inp["spacing"])
    expected = [math.sqrt(sum(inp["affine"][r][c] ** 2 for r in range(3))) for c in range(3)]
    if any(
        s <= 0 or not math.isclose(s, e, rel_tol=1e-8)
        for s, e in zip(spacing, expected, strict=True)
    ):
        raise ValueError("Coronary spacing differs from native affine")
    if len(inp["preview_indices"]) != 3:
        raise ValueError("Coronary preview needs three native sample axes")
    for size, count, indices in zip(shape, preview, inp["preview_indices"], strict=True):
        _indices(indices, size)
        if (
            len(indices) != count
            or indices != sorted(indices)
            or indices[0] != 0
            or indices[-1] != size - 1
        ):
            raise ValueError("Coronary preview must span all supplied crop endpoints")
    window = inp["preview_window"]
    _finite(window)
    if len(window) != 2 or window[0] >= window[1]:
        raise ValueError("Invalid coronary CT window")
    decode(inp["volume"], math.prod(preview))
    detail_shape = _shape(inp["detail_shape"])
    origin = _vector(inp["detail_origin"])
    if any(type(v) is not int for v in origin) or any(
        not 0 <= v <= n - count for v, n, count in zip(origin, shape, detail_shape, strict=True)
    ):
        raise ValueError("Coronary native detail exceeds supplied crop")
    decode(inp["detail_volume"], math.prod(detail_shape))
    mask = _indices(inp["mask_indices"], math.prod(shape))
    editable = _indices(inp["editable_indices"], math.prod(shape))
    added = _indices(obs["added_indices"], math.prod(shape))
    removed = _indices(obs["removed_indices"], math.prod(shape))
    if added & mask or not removed <= mask or added & removed or not (added | removed) <= editable:
        raise ValueError("Coronary saved edits violate original mask or editable membership")
    for key in ("start_ras", "end_ras", "review_ras"):
        _vector(inp[key])

    def inside(point: object) -> None:
        if any(not 0 <= v <= n - 1 for v, n in zip(_vector(point), shape, strict=True)):
            raise ValueError("Coronary inspection point lies outside supplied crop")

    for point in obs["bridge_ijk"]:
        inside(point)
    trace_steps = {row["step"] for row in obs["trace"]}
    if len(trace_steps) != len(obs["trace"]):
        raise ValueError("Duplicate coronary trace step")
    for state in obs["states"]:
        if state["trace_step"] not in trace_steps:
            raise ValueError("Coronary state lacks a retained observation")
        axis = state["axis"]
        if axis is not None and (type(axis) is not int or axis not in range(3)):
            raise ValueError("Invalid coronary plane axis")
        if state["levels"]:
            if axis is None:
                raise ValueError("Coronary plane levels lack axis")
            _indices(state["levels"], shape[axis])
        if state["center_ijk"] is not None:
            inside(state["center_ijk"])
        if state["bounds"] is not None:
            if len(state["bounds"]) != 2:
                raise ValueError("Coronary bounds need two corners")
            lo, hi = map(_vector, state["bounds"])
            if any(not 0 <= a < b <= n for a, b, n in zip(lo, hi, shape, strict=True)):
                raise ValueError("Coronary bounds exceed native crop")
    route = [_vector(point) for point in obs["centerline_ras"]]
    if len(route) < 2 or any(
        math.dist(route[i], inp[key]) > 1e-4 for i, key in ((0, "start_ras"), (-1, "end_ras"))
    ):
        raise ValueError("Saved coronary route does not retain supplied endpoints")
    cumulative = [0.0]
    for previous, point in pairwise(route):
        length = math.dist(previous, point)
        if length <= 0:
            raise ValueError("Saved coronary route has duplicate consecutive points")
        cumulative.append(cumulative[-1] + length)
    cpr = obs["cpr"]
    angles, rows, columns = _shape(cpr["shape"])
    if rows != len(route) or angles != len(cpr["angles_deg"]) or columns != len(cpr["offsets_mm"]):
        raise ValueError("Coronary CPR shape differs from saved route or angle/offset axes")
    for key, size in (("angles_deg", angles), ("offsets_mm", columns), ("arc_mm", rows)):
        values = cpr[key]
        _finite(values)
        if len(values) != size or any(a >= b for a, b in pairwise(values)):
            raise ValueError("Coronary CPR axes must be strictly increasing with matching lengths")
    if cpr["arc_mm"][0] != 0 or cpr["offsets_mm"].count(0) != 1:
        raise ValueError("Coronary CPR needs zero arc origin and one central offset")
    count = angles * rows * columns
    hu = list(struct.unpack(f"<{count}f", decode(cpr["hu"], count * 4)))
    source = list(struct.unpack(f"<{count * 3}f", decode(cpr["source_ras_mm"], count * 12)))
    _finite(hu)
    _finite(source)
    # Float32 output coordinates lose small fractions of a voxel; preserve those bytes.
    for a in range(angles):
        for r, center in enumerate(route):
            for c, offset in enumerate(cpr["offsets_mm"]):
                at = ((a * rows + r) * columns + c) * 3
                distance = math.dist(source[at : at + 3], center)
                if abs(distance - abs(offset)) > 5e-4:
                    raise ValueError(
                        "CPR pixel source position differs from its saved route/offset"
                    )
    corrected = ref["corrected_arc_mm"]
    _finite(corrected)
    if len(corrected) != rows or any(
        abs(a - b) > 1e-6 for a, b in zip(corrected, cumulative, strict=True)
    ):
        raise ValueError("Separate corrected arc differs from cumulative saved-route distance")
    # Do not demand original arc == corrected arc: their preserved mismatch is this witness.
    _finite(list(ref["metrics"].values()))
    mesh = obs["mesh"]
    vertices, faces = mesh["vertex_count"], mesh["face_count"]
    if type(vertices) is not int or type(faces) is not int or vertices < 3 or faces < 1:
        raise ValueError("Invalid saved coronary mesh counts")
    positions = list(struct.unpack(f"<{vertices * 3}f", decode(mesh["vertices"], vertices * 12)))
    triangles = struct.unpack(f"<{faces * 3}I", decode(mesh["faces"], faces * 12))
    _finite(positions)
    if any(v >= vertices for v in triangles):
        raise ValueError("Saved coronary mesh face indexes an absent vertex")
    return {"input": inp, "observed": obs, "reference": ref}
