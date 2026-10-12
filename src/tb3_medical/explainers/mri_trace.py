"""Validate two independent native MRI grids and a retained longitudinal trace."""

from __future__ import annotations

import math
from collections.abc import Callable

from ..types import Document
from .landmark_trace import _vector


def _shape(value: object) -> list[int]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(type(n) is not int or n < 1 for n in value)
    ):
        raise ValueError("MRI series requires a three-dimensional native shape")
    return value


def _inside(point: object, shape: list[int]) -> None:
    if any(not 0 <= p <= n - 1 for p, n in zip(_vector(point), shape, strict=True)):
        raise ValueError("MRI point outside its own native visit grid")


def project_mri(
    data: Document,
    attempt: str,
    decode: Callable[[str, int], bytes],
    matrix: Callable[[list[list[int | float]]], None],
) -> Document:
    """Project separate input, retained observations, and reader-only references."""
    if data["attempt"] != attempt or data["registered"] is not False:
        raise ValueError("MRI attempt differs or unregistered visits relabelled registered")
    visits = data["visits"]
    by_visit: dict[str, Document] = {v["id"]: v for v in visits}
    if len(visits) != 2 or set(by_visit) != {"V1", "V2"}:
        raise ValueError("Longitudinal trace requires distinct V1 and V2 native grids")
    inventory = {(r["visit"], r["id"]): r for r in data["inventory"]}
    if not inventory or len(inventory) != len(data["inventory"]):
        raise ValueError("MRI inventory has duplicate or missing series")
    for (visit, _), row in inventory.items():
        if visit not in by_visit or type(row["phase_count"]) is not int or row["phase_count"] < 1:
            raise ValueError("MRI inventory refers to an unknown visit or phase count")
        _shape(row["shape"])
        matrix(row["affine"])
    for visit in visits:
        shape = _shape(visit["shape"])
        matrix(visit["affine"])
        spacing = _vector(visit["spacing"])
        expected = [math.sqrt(sum(visit["affine"][r][c] ** 2 for r in range(3))) for c in range(3)]
        if any(
            s <= 0 or not math.isclose(s, e, rel_tol=1e-8)
            for s, e in zip(spacing, expected, strict=True)
        ):
            raise ValueError("MRI spacing differs from its native affine")
        preview = _shape(visit["preview_shape"])
        if len(visit["preview_indices"]) != 3:
            raise ValueError("MRI preview needs three explicit native axes")
        for size, count, axis in zip(shape, preview, visit["preview_indices"], strict=True):
            if len(axis) != count or count > size or any(type(i) is not int for i in axis):
                raise ValueError("MRI preview sample count differs")
            if axis != sorted(set(axis)) or axis[0] != 0 or axis[-1] != size - 1:
                raise ValueError("MRI preview must cover whole native grid endpoints")
        window = visit["preview_window"]
        if (
            len(window) != 2
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in window)
            or window[0] >= window[1]
        ):
            raise ValueError("MRI preview window must be finite and increasing")
        series = visit["series"]
        if len(series) < 2 or [s["ordinal"] for s in series] != list(range(len(series))):
            raise ValueError("MRI dynamic ordinals must be an ordered baseline/post sequence")
        if len({s["id"] for s in series}) != len(series):
            raise ValueError("Duplicate selected MRI series")
        for series_row in series:
            original = inventory.get((visit["id"], series_row["id"]))
            if original is None or original["shape"] != shape or original["phase_count"] != 1:
                raise ValueError("Selected MRI series differs from supplied native inventory")
            # Supplied metadata rounds affines; retain NIfTI precision in the preview.
            if any(
                abs(a - b) > 1e-3
                for x, y in zip(original["affine"], visit["affine"], strict=True)
                for a, b in zip(x, y, strict=True)
            ):
                raise ValueError("Selected MRI series belongs to a different physical grid")
            decode(series_row["volume"], math.prod(preview))
    trace_steps = {r["step"] for r in data["trace"]}
    if len(trace_steps) != len(data["trace"]):
        raise ValueError("Duplicate MRI trace step")

    def selected(visit: str, series: str) -> Document:
        if visit not in by_visit or series not in {s["id"] for s in by_visit[visit]["series"]}:
            raise ValueError("MRI state refers to an unavailable visit/series")
        return by_visit[visit]

    for state in data["states"]:
        if state["trace_step"] not in trace_steps:
            raise ValueError("MRI state lacks its retained trace observation")
        if not state["views"]:
            raise ValueError("MRI state has no native inspection view")
        for view in state["views"]:
            visit = selected(view["visit"], view["series_id"])
            axis = view["axis"]
            if axis is not None and (type(axis) is not int or axis not in range(3)):
                raise ValueError("Invalid MRI inspection axis")
            if view["levels"] and (
                axis is None
                or any(
                    type(k) is not int or not 0 <= k < visit["shape"][axis] for k in view["levels"]
                )
            ):
                raise ValueError("MRI inspection level lies outside its native axis")
            if view["center_ijk"] is not None:
                _inside(view["center_ijk"], visit["shape"])
            bounds = view["bounds"]
            if bounds is not None:
                if len(bounds) != 2:
                    raise ValueError("MRI bounds need two half-open native corners")
                lo, hi = map(_vector, bounds)
                if any(not 0 <= a < b <= n for a, b, n in zip(lo, hi, visit["shape"], strict=True)):
                    raise ValueError("MRI inspection bounds exceed supplied grid")
    for citation in data["citations"]:
        visit = selected(citation["visit"], citation["series_id"])
        if type(citation["phase"]) is not int or citation["phase"] != 0:
            raise ValueError("MRI dynamic ordinal is not a 3D file's citation phase")
        _inside(citation["ijk"], visit["shape"])
    measured = {}
    for row in data["measurements"]:
        visit = selected(row["visit"], row["series_id"])
        if row["visit"] in measured or row["phase"] != 0 or not 0 < row["fraction"] <= 1:
            raise ValueError("Invalid or duplicate saved MRI measurement")
        lo, hi = _vector(row["bbox_min"]), _vector(row["bbox_max"])
        _inside(lo, visit["shape"])
        _inside(hi, visit["shape"])
        if any(type(v) is not int for v in lo + hi) or any(
            a > b for a, b in zip(lo, hi, strict=True)
        ):
            raise ValueError("MRI component box needs ordered inclusive voxel extrema")
        spans = [(b - a + 1) * s for a, b, s in zip(lo, hi, visit["spacing"], strict=True)]
        if (
            any(abs(a - b) > 0.00051 for a, b in zip(_vector(row["spans_mm"]), spans, strict=True))
            or abs(row["diameter_mm"] - max(spans)) > 0.00051
        ):
            raise ValueError("MRI component span differs from native voxel-edge box")
        if abs(row["reported_mm"] - max(spans)) > 0.051:
            raise ValueError("MRI reported rounded span differs from saved component")
        measured[row["visit"]] = max(spans)
    if set(measured) != set(by_visit):
        raise ValueError("MRI saved extent requires both visits")
    forecast = data["forecast"]
    if not 0 <= forecast["confidence"] <= 1:
        raise ValueError("MRI saved forecast confidence outside [0,1]")
    reference = data["reference"]
    for key in ("ftv_cc", "diameter_raw"):
        values = reference[key]
        if len(values) < 2 or any(
            type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values
        ):
            raise ValueError("MRI reference endpoint needs finite nonnegative visit values")
    expected_diameters = [measured[v] for v in ("V1", "V2")]
    if len(reference["audit_diameters_mm"]) != 2 or any(
        abs(a - b) > 1e-6
        for a, b in zip(reference["audit_diameters_mm"], expected_diameters, strict=True)
    ):
        raise ValueError("MRI prior audit differs from saved native box geometry")
    change = 100 * (expected_diameters[1] / expected_diameters[0] - 1)
    if abs(reference["audit_change_percent"] - change) > 1e-6:
        raise ValueError("MRI audit percentage differs from its defined endpoint")
    return {
        "input": {k: data[k] for k in ("visits", "inventory", "registered")},
        "observed": {
            k: data[k]
            for k in (
                "states",
                "measurements",
                "citations",
                "summary",
                "impression",
                "forecast",
                "evidence",
                "trace",
                "elapsed_seconds",
                "steps_in_trace",
            )
        },
        "reference": {
            k: reference[k]
            for k in (
                "contract_pass",
                "reward",
                "clinical_accuracy",
                "ftv_cc",
                "diameter_raw",
                "diameter_unit",
                "pcr",
                "audit_diameters_mm",
                "audit_change_percent",
                "forecast_baseline",
            )
        },
    }
