"""Compile selected native-trace stories without executing a medical recipe or trial.

The source manuscript owns chapters and timing. A pinned manifest owns local asset
availability; input/observation/reference projections remain separate for readers.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import struct
import zlib
from pathlib import Path
from typing import Literal, Self, cast

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from .. import storage
from ..presentation_contracts import (
    NativeTracePlan,
    NativeTraceView,
    StoryPlan,
    validate_native_trace_view,
)
from ..types import Document
from .assets import check_dependencies
from .landmark_trace import project_landmark


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Asset(ClosedModel):
    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    bytes: StrictInt = Field(ge=1)
    role: Literal[
        "derived-display",
        "delivered-image",
        "provenance",
        "license",
        "task-input",
        "saved-output",
        "private-reference",
        "trace",
    ]
    step: StrictInt | None = Field(default=None, ge=1)


class Manifest(ClosedModel):
    schema_version: Literal[1] = Field(alias="schema")
    id: str = Field(min_length=1)
    entry_id: str = Field(min_length=1)
    attempt: str = Field(min_length=1)
    saved_state: str = Field(min_length=1)
    adapter: Literal["ct-pose", "mra-repair", "ct-landmarks"]
    coordinates: Literal["LPS-mm", "RAS-mm"]
    notice: str = Field(min_length=1)
    recovery: str = Field(min_length=1)
    assets: list[Asset] = Field(min_length=3)

    @model_validator(mode="after")
    def closure(self) -> Self:
        if len({item.path for item in self.assets}) != len(self.assets):
            raise ValueError("Duplicate asset path")
        if sum(a.role == "derived-display" for a in self.assets) != 1:
            raise ValueError("Exactly one derived display payload is required")
        if not {"provenance", "license"} <= {a.role for a in self.assets}:
            raise ValueError("Native data needs provenance and license assets")
        expected = "LPS-mm" if self.adapter == "ct-pose" else "RAS-mm"
        if self.coordinates != expected:
            raise ValueError("Native adapter coordinate frame mismatch")
        if any((a.role == "delivered-image") != (a.step is not None) for a in self.assets):
            raise ValueError("Only delivered images require a trace step")
        return self


class Chapter(ClosedModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    scene: Literal[
        "input",
        "search",
        "bounds",
        "coarse",
        "threshold",
        "contacts",
        "output",
        "reference",
        "projection",
        "levels",
        "centres",
    ]
    frames: StrictInt = Field(ge=1)
    caption: str = Field(min_length=1)
    narration: str = Field(min_length=1)
    visual: str = Field(min_length=1)
    state: str | None
    trace_steps: list[StrictInt] = Field(min_length=1)
    reference: bool = False


class Manuscript(ClosedModel):
    schema_version: Literal[2] = Field(alias="schema")
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    locale: Literal["en"]
    purpose: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    recipe: Literal["native-trace-v1"]
    manifest: str = Field(min_length=1)
    fps: StrictInt = Field(ge=1, le=60)
    reference_policy: Literal["reader-reference-reveal"]
    source_class: Literal["source-derived-teaching"]
    source_locators: list[str] = Field(min_length=1)
    beats: list[Chapter] = Field(min_length=2)

    @model_validator(mode="after")
    def timeline(self) -> Self:
        if len({beat.id for beat in self.beats}) != len(self.beats):
            raise ValueError("Duplicate chapter ID")
        if [i for i, beat in enumerate(self.beats) if beat.reference] != [len(self.beats) - 1]:
            raise ValueError("The final chapter alone must declare the reference reveal")
        for beat in self.beats:
            if len(set(beat.trace_steps)) != len(beat.trace_steps) or min(beat.trace_steps) < 1:
                raise ValueError("Invalid or duplicate trace step")
        return self


def _matrix(value: object) -> None:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError("Expected a finite 4 by 4 native affine")
    if any(
        not isinstance(row, list)
        or len(row) != 4
        or any(type(x) not in (int, float) or not math.isfinite(x) for x in row)
        for row in value
    ):
        raise ValueError("Expected a finite 4 by 4 native affine")
    if value[3] != [0, 0, 0, 1]:
        raise ValueError("Invalid homogeneous affine row")
    a, b, c = value[:3]
    determinant = (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )
    if abs(determinant) < 1e-12:
        raise ValueError("Native affine is singular")


def _array(encoded: str, size: int) -> bytes:
    if size > 64 * 1024 * 1024:
        raise ValueError("Display array exceeds the native-reader limit")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    raw = decoder.decompress(base64.b64decode(encoded, validate=True), size + 1)
    if len(raw) != size or not decoder.eof or decoder.unused_data:
        raise ValueError("Compressed native array shape/length mismatch")
    return raw


def _indices(values: list[int], size: int) -> None:
    if any(type(i) is not int or not 0 <= i < size for i in values):
        raise ValueError("Voxel index outside the supplied grid")
    if len(set(values)) != len(values):
        raise ValueError("Duplicate voxel index")


def project_payload(data: Document, manifest: Manifest) -> Document:
    """Explicit field allowlists prevent reference diagnostics leaking into input data."""
    shape = data["shape"]
    if (
        not isinstance(shape, list)
        or len(shape) != 3
        or any(type(n) is not int or n < 1 for n in shape)
    ):
        raise ValueError("Invalid native volume shape")
    _matrix(data["affine"])
    size = math.prod(shape)
    trace = data["trace"]
    if len({item["step"] for item in trace}) != len(trace):
        raise ValueError("Duplicate retained trace step")
    if manifest.adapter == "ct-pose":
        if data["attempt"] != manifest.attempt:
            raise ValueError("CT attempt identity mismatch")
        preview = data["preview_size"]
        if type(preview) is not int or preview < 1 or shape != [preview * 2] * 3:
            raise ValueError("CT preview shape must match the retained half-resolution grid")
        _array(data["preview_base64_gzip"], preview**3)
        _matrix(data["reference_pose"])
        states, diagnostics = [], {}
        for state in data["states"]:
            _matrix(state["pose"])
            states.append(
                {
                    key: state[key]
                    for key in (
                        "id",
                        "trace_step",
                        "pose",
                        "image",
                        "silhouette",
                        "difference",
                        "role",
                    )
                }
            )
            diagnostics[state["id"]] = state["diagnostic"]
        input_keys: tuple[str, ...] = (
            "shape",
            "affine",
            "spacing_mm",
            "preview_size",
            "preview_window_hu",
            "preview_base64_gzip",
            "target",
            "target_silhouette",
            "slice_previews",
        )
        observed = {
            "states": states,
            "trace": trace,
            "elapsed_seconds": data["elapsed_seconds"],
            "steps_in_trace": data["steps_in_trace"],
        }
        reference = {
            "pose": data["reference_pose"],
            "frozen_metrics": data["frozen_metrics"],
            "state_diagnostics": diagnostics,
        }
    elif manifest.adapter == "ct-landmarks":
        input_keys, observed, reference = project_landmark(data, manifest.attempt, _array)
    else:
        volume = _array(data["volume"], size)
        mask = _array(data["mask"], size)
        editable = _array(data["editable"], size)
        if max(mask) > 1 or max(editable) > 1:
            raise ValueError("Supplied masks must be binary")
        if not volume:
            raise ValueError("Empty image array")
        vertices = data["surface_vertices"]
        if type(vertices) is not int or vertices < 1:
            raise ValueError("Invalid surface vertex count")
        surface = _array(data["surface"], vertices * 3 * 4)
        if any(not math.isfinite(value[0]) for value in struct.iter_unpack("<f", surface)):
            raise ValueError("Surface contains nonfinite coordinates")
        seed, roi = data["seed"], data["roi"]
        if len(seed) != 3 or any(
            type(x) is not int or not 0 <= x < n for x, n in zip(seed, shape, strict=True)
        ):
            raise ValueError("Seed lies outside the supplied grid")
        if (
            len(roi) != 2
            or any(len(bound) != 3 for bound in roi)
            or any(
                type(lo) is not int or type(hi) is not int or not 0 <= lo < hi <= n
                for lo, hi, n in zip(*roi, shape, strict=True)
            )
        ):
            raise ValueError("Invalid half-open native crop")
        thresholds = [state["threshold"] for state in data["states"]]
        if any(type(t) not in (int, float) or not math.isfinite(t) for t in thresholds) or len(
            set(thresholds)
        ) != len(thresholds):
            raise ValueError("Threshold states must have unique finite values")
        for state in data["states"]:
            _indices(state["indices"], size)
            if any(mask[i] or not editable[i] for i in state["indices"]):
                raise ValueError("Candidate lies outside the editable unmasked domain")
            if state["count"] != len(state["indices"]):
                raise ValueError("Threshold count differs from retained voxel set")
            for patch in state["contacts"]:
                _indices(patch, size)
                if not set(patch) <= set(state["indices"]):
                    raise ValueError("Contact patch lies outside its candidate")
            contacts = [i for patch in state["contacts"] for i in patch]
            if len(set(contacts)) != len(contacts):
                raise ValueError("Contact patches overlap")
        _indices(data["added"], size)
        _indices(data["residual"], size)
        if any(mask[i] or not editable[i] for i in data["added"]):
            raise ValueError("Saved additions must be new foreground inside the editable mask")
        selected = [s for s in data["states"] if str(s["threshold"]) == manifest.saved_state]
        if len(selected) != 1 or set(data["added"]) != set(selected[0]["indices"]):
            raise ValueError("Saved additions differ from the declared selected component")
        input_keys = (
            "shape",
            "affine",
            "spacing",
            "volume",
            "mask",
            "editable",
            "surface",
            "surface_vertices",
            "mip",
            "source_voxels",
            "global_components",
        )
        observed = {key: data[key] for key in ("states", "seed", "roi", "added", "trace")}
        reference = {key: data[key] for key in ("residual", "frozen", "initial")}
    return {
        "input": {key: data[key] for key in input_keys},
        "observed": {
            **observed,
            "trace": [
                {
                    "step": item["step"],
                    "timestamp": item.get("timestamp", item.get("time")),
                    "calls": item.get("calls", [item.get("call", "")]),
                    "output": item["output"],
                }
                for item in trace
            ],
        },
        "reference": reference,
    }


def compile_trace(root: Path, path: Path, *, allow_missing: bool = False) -> Document:
    from .. import explanation_stories

    root = root.resolve()
    path = storage.inside(root, path)
    story_bytes = path.read_bytes()
    raw = story_bytes.decode()
    if "[[AUTHOR:" in raw:
        raise ValueError("Unfinished native-trace manuscript")
    document = explanation_stories.parse_document(raw)
    story = Manuscript.model_validate({**document.header, "beats": list(document.beats)})
    manifest_path = storage.inside(root, story.manifest)
    manifest_bytes = manifest_path.read_bytes()
    manifest = Manifest.model_validate_json(manifest_bytes)
    if manifest.id != story.id:
        raise ValueError("Story and native manifest identity differ")
    dependencies = {
        path.relative_to(root).as_posix(): hashlib.sha256(story_bytes).hexdigest(),
        story.manifest: hashlib.sha256(manifest_bytes).hexdigest(),
    }
    for locator in story.source_locators:
        source = storage.inside(root, locator)
        dependencies[locator] = storage.sha(source)
    missing = []
    for asset in manifest.assets:
        source = storage.inside(root, asset.path)
        if not source.is_file():
            missing.append(asset.path)
            continue
        if source.stat().st_size != asset.bytes or storage.sha(source) != asset.sha256:
            raise ValueError(f"Changed native asset: {asset.path}")
        dependencies[asset.path] = asset.sha256
    if missing and not allow_missing:
        raise ValueError(f"Missing native assets: {', '.join(missing)}; {manifest.recovery}")
    at = 0
    beats = []
    for beat in story.beats:
        beats.append({**beat.model_dump(), "startFrame": at, "endFrame": at + beat.frames})
        at += beat.frames
    payload = None
    if not missing:
        asset = next(a for a in manifest.assets if a.role == "derived-display")
        payload = project_payload(storage.read_object(storage.inside(root, asset.path)), manifest)
        states = payload["observed"]["states"]
        state_ids = {
            str(s["threshold"] if manifest.adapter == "mra-repair" else s["id"]) for s in states
        }
        if len(state_ids) != len(states):
            raise ValueError("Duplicate native state identity")
        if manifest.saved_state not in state_ids:
            raise ValueError("Saved state is not retained")
        steps = {item["step"] for item in payload["observed"]["trace"]}
        if manifest.adapter == "ct-landmarks":
            deliveries = {a.step for a in manifest.assets if a.role == "delivered-image"}
            if any(
                s["delivered_step"] is not None and s["delivered_step"] not in deliveries
                for s in states
            ):
                raise ValueError("Landmark inspection is missing its exact delivered image")
        for beat in story.beats:
            if not set(beat.trace_steps) <= steps or (
                beat.state is not None and beat.state not in state_ids
            ):
                raise ValueError(f"Chapter {beat.id} is not bound to retained trace/state evidence")
        payload["delivered_images"] = [
            {
                "step": a.step,
                "path": a.path,
                "src": "data:image/png;base64,"
                + base64.b64encode(storage.inside(root, a.path).read_bytes()).decode(),
            }
            for a in manifest.assets
            if a.role == "delivered-image"
        ]
        payload["licenses"] = [
            storage.inside(root, a.path).read_text() for a in manifest.assets if a.role == "license"
        ]
    check_dependencies(root, dependencies)
    return {
        "schema": 1,
        "family": "native-trace",
        "status": "compiled-native-trace",
        "availability": "missing-local-assets" if missing else "available",
        "missing": missing,
        "manifest": manifest.model_dump(mode="json", by_alias=True),
        "plan": {
            **story.model_dump(mode="json", by_alias=True),
            "beats": beats,
            "durationFrames": at,
        },
        "payload": payload,
        "dependencies": dependencies,
        "compiler": {
            "native_trace.py": storage.sha(Path(__file__)),
            "explanation_stories.py": storage.sha(Path(explanation_stories.__file__)),
            **(
                {"landmark_trace.py": storage.sha(Path(__file__).with_name("landmark_trace.py"))}
                if manifest.adapter == "ct-landmarks"
                else {}
            ),
        },
        "reference_boundary": "Reader reveal only; this local package contains reference bytes and is not solver staging.",
    }


def compile_components(root: Path, path: Path) -> tuple[NativeTracePlan, NativeTraceView]:
    """Canonical projection; absent local arrays remain an explicit missing-data view."""
    from ..explanation_stories import compiler_hashes

    root = root.resolve()
    relative = path.relative_to(root) if path.is_absolute() else path
    compiled = compile_trace(root, relative, allow_missing=True)
    manifest = compiled["manifest"]
    dependencies = {**compiled["dependencies"], **compiler_hashes(root)}
    dependencies["src/tb3_medical/explainers/native_trace.py"] = storage.sha(
        root / "src/tb3_medical/explainers/native_trace.py"
    )
    if manifest["adapter"] == "ct-landmarks":
        dependencies["src/tb3_medical/explainers/landmark_trace.py"] = storage.sha(
            root / "src/tb3_medical/explainers/landmark_trace.py"
        )
    plan = cast(
        NativeTracePlan,
        {
            **compiled["plan"],
            "asset_pack": manifest["id"],
            "source_sha256": dependencies[relative.as_posix()],
            "asset_manifest_sha256": dependencies[compiled["plan"]["manifest"]],
            "dependencies": dependencies,
        },
    )
    available = compiled["availability"] == "available"
    view = validate_native_trace_view(
        {
            "family": "native-trace",
            "version": 1,
            "adapter": manifest["adapter"],
            "label": "Retained task-solving trace",
            "availability": compiled["availability"],
            "missing": compiled["missing"],
            "coordinates": manifest["coordinates"],
            "attempt": manifest["attempt"],
            "saved_state": manifest["saved_state"],
            "source": {
                "notice": {
                    "label": "Native source / one retained condition"
                    if available
                    else "Native assets unavailable here",
                    "text": manifest["notice"] if available else manifest["recovery"],
                    "url": "https://zenodo.org/records/10047263"
                    if manifest["adapter"] == "ct-pose"
                    else "https://github.com/anjany/verse"
                    if manifest["adapter"] == "ct-landmarks"
                    else "https://zenodo.org/records/15692630",
                    "link_label": "Original dataset",
                }
            },
            "bundle": {"id": manifest["id"], "assets": manifest["assets"]},
            "payload": compiled["payload"],
            "dependencies": dependencies,
            "reference_boundary": compiled["reference_boundary"],
        }
    )
    check_dependencies(root, dependencies)
    return plan, view


def compile_view(root: Path, plan: StoryPlan) -> NativeTraceView | None:
    if plan["recipe"] != "native-trace-v1":
        return None
    sources = [p for p in plan["dependencies"] if p.endswith(".story.md")]
    if len(sources) != 1:
        raise ValueError("A native trace needs one canonical manuscript")
    current, view = compile_components(root, Path(sources[0]))
    if current != plan:
        raise ValueError("Native trace source or asset availability changed; recompile the story")
    return view


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("story", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()
    result = compile_trace(args.root, args.story, allow_missing=args.allow_missing)
    storage.write_new(args.output, result)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "availability": result["availability"],
                "chapters": len(result["plan"]["beats"]),
                "status": result["status"],
            }
        )
    )


if __name__ == "__main__":
    main()
