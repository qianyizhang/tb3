"""Validate retained whole-slide reads without rerunning search or evaluation."""

from __future__ import annotations

import math
import struct

from ..types import Document


def _pick(value: Document, fields: str) -> Document:
    return {key: value[key] for key in fields.split()}


def _numbers(value: object, count: int) -> list[int | float]:
    if (
        not isinstance(value, list)
        or len(value) != count
        or any(type(v) not in (int, float) or not math.isfinite(v) for v in value)
    ):
        raise ValueError("WSI geometry needs finite coordinates")
    return value


def _size(value: object) -> list[int | float]:
    result = _numbers(value, 2)
    if any(type(v) is not int or v <= 0 for v in result):
        raise ValueError("WSI raster dimensions must be positive integers")
    return result


def _rect(value: object) -> list[int | float]:
    result = _numbers(value, 4)
    if min(result[:2]) < 0 or min(result[2:]) <= 0:
        raise ValueError("WSI rectangle needs nonnegative origin and positive extent")
    return result


def _inside(rect: list[int | float], size: list[int | float]) -> bool:
    return all(rect[a] + rect[a + 2] <= size[a] for a in range(2))


def project_wsi(data: Document, attempt: str) -> Document:
    """Project role-specific fields, preserving empty answers and padded pyramid reads."""
    if data["attempt"] != attempt:
        raise ValueError("WSI trace attempt differs")
    inp = _pick(
        data["input"], "size_level0 spacing_um overview overview_size overview_downsample pyramid"
    )
    obs = _pick(
        data["observed"],
        "deliveries states panels reads points answer_text trace elapsed_seconds steps_in_trace evidence",
    )
    ref = _pick(
        data["reference"],
        "source_slide polygons artifact_reward polygon_count group_count hit_groups submitted_points grouping_um limits",
    )
    inp["pyramid"] = [_pick(v, "level size downsample") for v in inp["pyramid"]]
    obs["deliveries"] = [_pick(v, "sha256 size") for v in obs["deliveries"]]
    obs["states"] = [
        _pick(v, "id label trace_step delivered_step panel_ids description") for v in obs["states"]
    ]
    obs["panels"] = [
        _pick(v, "id label delivery_sha256 raster_bounds bounds_level0 level read_step description")
        for v in obs["panels"]
    ]
    obs["reads"] = [_pick(v, "id step bounds_level0 level method") for v in obs["reads"]]
    obs["points"] = [_pick(v, "x y confidence") for v in obs["points"]]
    obs["trace"] = [_pick(v, "step timestamp calls output") for v in obs["trace"]]
    ref["polygons"] = [_pick(v, "id kind points") for v in ref["polygons"]]
    size = _size(inp["size_level0"])
    spacing = _numbers(inp["spacing_um"], 2)
    if min(spacing) <= 0:
        raise ValueError("WSI physical spacing must be positive")
    overview = _size(inp["overview_size"])
    downsample = inp["overview_downsample"]
    if (
        type(downsample) not in (int, float)
        or not math.isfinite(downsample)
        or downsample <= 0
        or any(not math.isclose(overview[a] * downsample, size[a]) for a in range(2))
    ):
        raise ValueError("WSI overview must map to the whole native slide")
    levels = {v["level"]: v for v in inp["pyramid"]}
    if len(levels) != len(inp["pyramid"]) or 0 not in levels or levels[0]["size"] != size:
        raise ValueError("WSI native pyramid identity differs")
    for level, row in levels.items():
        _size(row["size"])
        scale = row["downsample"]
        if (
            type(level) is not int
            or level < 0
            or type(scale) not in (int, float)
            or not math.isfinite(scale)
            or scale <= 0
        ):
            raise ValueError("WSI pyramid scale is invalid")
        if any(row["size"][a] * scale < size[a] for a in range(2)):
            raise ValueError("WSI padded pyramid cannot omit native extent")
    if levels[0]["downsample"] != 1:
        raise ValueError("WSI native level must have unit scale")
    deliveries = {v["sha256"]: _size(v["size"]) for v in obs["deliveries"]}
    if len(deliveries) != len(obs["deliveries"]):
        raise ValueError("WSI delivery hashes must be unique")
    steps = {v["step"] for v in obs["trace"]}
    if len(steps) != len(obs["trace"]) or any(
        type(v) is not int or v < 1 or v > obs["steps_in_trace"] for v in steps
    ):
        raise ValueError("WSI trace step identity differs")
    panels = {v["id"]: v for v in obs["panels"]}
    if len(panels) != len(obs["panels"]):
        raise ValueError("WSI panel identity repeats")
    for panel in panels.values():
        raster, native = _rect(panel["raster_bounds"]), _rect(panel["bounds_level0"])
        if panel["delivery_sha256"] not in deliveries or not _inside(
            raster, deliveries[panel["delivery_sha256"]]
        ):
            raise ValueError("WSI panel exceeds exact delivered raster")
        if panel["level"] not in levels or panel["read_step"] not in steps:
            raise ValueError("WSI panel has no retained level/read step")
        level = levels[panel["level"]]
        extent = [v * level["downsample"] for v in level["size"]]
        if not _inside(native, extent):
            raise ValueError("WSI panel exceeds source pyramid extent")
    if len({v["id"] for v in obs["reads"]}) != len(obs["reads"]):
        raise ValueError("WSI read identity repeats")
    for read in obs["reads"]:
        bounds = _rect(read["bounds_level0"])
        if (
            read["step"] not in steps
            or read["level"] not in levels
            or read["method"] not in {"helper", "pyramid"}
        ):
            raise ValueError("WSI read provenance is invalid")
        level = levels[read["level"]]
        extent = (
            size if read["method"] == "helper" else [v * level["downsample"] for v in level["size"]]
        )
        if not _inside(bounds, extent) or (read["method"] == "helper" and read["level"] != 0):
            raise ValueError(
                "WSI helper must stay inside native extent; pyramid padding is separate"
            )
    for state in obs["states"]:
        if state["trace_step"] not in steps or (
            state["delivered_step"] is not None and state["delivered_step"] not in steps
        ):
            raise ValueError("WSI state is not tied to retained trace")
        if any(
            v not in panels or panels[v]["read_step"] > state["trace_step"]
            for v in state["panel_ids"]
        ):
            raise ValueError("WSI state refers to absent or future panels")
    for point in obs["points"]:
        x, y, confidence = _numbers([point[k] for k in ("x", "y", "confidence")], 3)
        if not 0 <= x < size[0] or not 0 <= y < size[1] or not 0 <= confidence <= 1:
            raise ValueError("WSI saved point is outside the answer domain")
    for polygon in ref["polygons"]:
        if polygon["kind"] not in {"tumor", "exclusion"} or len(polygon["points"]) < 3:
            raise ValueError("WSI reference polygon is invalid")
        for point in polygon["points"]:
            x, y = _numbers(point, 2)
            if not 0 <= x <= size[0] or not 0 <= y <= size[1]:
                raise ValueError("WSI reference exceeds native slide")
    if ref["submitted_points"] != len(obs["points"]) or ref["polygon_count"] != sum(
        v["kind"] == "tumor" for v in ref["polygons"]
    ):
        raise ValueError("WSI frozen counts differ from retained artifacts")
    if not 0 <= ref["hit_groups"] <= ref["group_count"] <= ref["polygon_count"]:
        raise ValueError("WSI study group counts are inconsistent")
    return {"input": inp, "observed": obs, "reference": ref}


def _image_size(raw: bytes) -> tuple[int, int]:
    if raw.startswith(b"\x89PNG\r\n\x1a\n") and len(raw) >= 24:
        return struct.unpack(">II", raw[16:24])
    if not raw.startswith(b"\xff\xd8"):
        raise ValueError("WSI exact delivery must be PNG or JPEG")
    at = 2
    while at + 4 <= len(raw):
        if raw[at] != 255:
            break
        marker = raw[at + 1]
        if marker == 255:
            at += 1
            continue
        length = int.from_bytes(raw[at + 2 : at + 4], "big")
        if length < 2 or at + 2 + length > len(raw):
            break
        if marker in {0xC0, 0xC1, 0xC2} and length >= 7:
            h, w = struct.unpack(">HH", raw[at + 5 : at + 9])
            return w, h
        at += length + 2
    raise ValueError("WSI delivery dimensions are unavailable")


def validate_wsi_deliveries(payload: Document, assets: list[tuple[str, int | None, bytes]]) -> None:
    """Bind panel rasters to actual image headers and recorded delivery steps."""
    actual = {sha: (step, list(_image_size(raw))) for sha, step, raw in assets}
    declared = payload["observed"]["deliveries"]
    if {v["sha256"] for v in declared} != set(actual) or any(
        actual[v["sha256"]][1] != v["size"] for v in declared
    ):
        raise ValueError("WSI delivered image identity or dimensions differ")
    panels = {v["id"]: v for v in payload["observed"]["panels"]}
    for state in payload["observed"]["states"]:
        for identity in state["panel_ids"]:
            panel = panels[identity]
            delivered = actual[panel["delivery_sha256"]][0]
            if (
                delivered is None
                or delivered > state["trace_step"]
                or panel["read_step"] > delivered
            ):
                raise ValueError("WSI delivery chronology differs from retained state")
