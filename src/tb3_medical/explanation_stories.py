"""Compile group-owned explanation scripts; no model calls or validator I/O."""

from __future__ import annotations

import hashlib
import json
import re
from html import escape
from pathlib import Path
from typing import Literal, Self, cast

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, model_validator

from .errors import MedicalError
from .presentation_contracts import StoryBeat, StoryPlan
from .types import Document

CHANNELS = ("context", "route", "ribbon", "cursor", "unfold", "output")
SCOPE = (
    "Synthetic teaching fixture · one sampling ribbon only. Does not demonstrate local mask "
    "repair, eight CT planes, closed mesh production or full BR030 verification. "
    "Fixture coordinates: m; real task outputs: mm."
)


class UniqueLoader(yaml.SafeLoader):  # type: ignore[misc]
    # PyYAML is confined to the untyped parse boundary; Pydantic checks its output.
    """Reject duplicate keys instead of silently keeping the last occurrence."""


def _mapping(loader: UniqueLoader, node: yaml.MappingNode) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"Duplicate or non-string YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


class Closed(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class AssetPack(Closed):
    manifest: str = Field(min_length=1, strict=True)
    retained_files: tuple[str, ...]
    runtime_geometry: Literal["geometry.json"]

    @model_validator(mode="after")
    def complete(self) -> Self:
        required = {
            "geometry.json",
            "route.json",
            "cpr-sampled.png",
            "phantom-projection.png",
            "branching-phantom-volume.npz",
        }
        if not required.issubset(self.retained_files):
            raise ValueError("Route pack is missing required fixture dependencies")
        if len(self.retained_files) != len(set(self.retained_files)):
            raise ValueError("Duplicate retained asset")
        return self


class PrefabIndex(Closed):
    schema_version: StrictInt = Field(alias="schema", ge=1, le=1)
    packs: dict[str, AssetPack]


class Header(Closed):
    schema_version: StrictInt = Field(alias="schema", ge=1, le=1)
    id: str = Field(pattern=r"^[a-z0-9-]+$", strict=True)
    title: str = Field(min_length=1, strict=True)
    locale: Literal["en"]
    purpose: str = Field(min_length=1, strict=True)
    recipe: Literal["route-unfold-v1"]
    asset_pack: Literal["tb3-route-kit-v1"]
    fps: StrictInt = Field(ge=12, le=60)
    reference_policy: Literal["no-reference-assets"]
    source_class: Literal["procedural-teaching"]


class Beat(Closed):
    id: str = Field(pattern=r"^[a-z0-9-]+$", strict=True)
    duration: StrictFloat = Field(gt=0, le=60)
    caption: str = Field(min_length=1, strict=True)
    narration: str = Field(min_length=1, strict=True)
    visual: str = Field(min_length=1, strict=True)
    context: tuple[StrictFloat, StrictFloat]
    route: tuple[StrictFloat, StrictFloat]
    ribbon: tuple[StrictFloat, StrictFloat]
    cursor: tuple[StrictFloat, StrictFloat]
    unfold: tuple[StrictFloat, StrictFloat]
    output: tuple[StrictFloat, StrictFloat]

    @model_validator(mode="after")
    def bounded(self) -> Self:
        for name in CHANNELS:
            if not all(0 <= value <= 1 for value in getattr(self, name)):
                raise ValueError(f"{name} must stay in [0,1]")
        return self


def parse_story(raw: str) -> tuple[Header, tuple[Beat, ...]]:
    match = re.match(r"\A---\n(.*?)\n---\n", raw, re.S)
    if not match:
        raise ValueError("Expected YAML frontmatter")
    header = Header.model_validate(yaml.load(match[1], Loader=UniqueLoader))
    blocks = re.findall(r"^```beat\n(.*?)^```\s*$", raw, re.M | re.S)
    if len(blocks) != len(re.findall(r"^```beat\s*$", raw, re.M)):
        raise ValueError("Unclosed or malformed beat block")
    beats = tuple(Beat.model_validate(yaml.load(block, Loader=UniqueLoader)) for block in blocks)
    if not beats or len({beat.id for beat in beats}) != len(beats):
        raise ValueError("Missing beats or duplicate beat IDs")
    for beat in beats:
        frames = beat.duration * header.fps
        if round(frames) < 1 or abs(frames - round(frames)) > 1e-8:
            raise ValueError(f"{beat.id}: duration must align with fps")
    return header, beats


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Asset escaped owner: {name}")
    return path


def resolve_assets(root: Path, pack_id: str) -> tuple[str, dict[str, str]]:
    index_path = root / "presentation/assets/teaching-prefabs.json"
    index = PrefabIndex.model_validate_json(index_path.read_text())
    if pack_id not in index.packs:
        raise ValueError(f"Unknown asset pack: {pack_id}")
    pack = index.packs[pack_id]
    manifest_path = inside(root, pack.manifest)
    manifest = json.loads(manifest_path.read_text())
    if manifest["id"] != pack_id:
        raise ValueError("Asset pack mismatch")
    dependencies = {str(p.relative_to(root)): digest(p) for p in (index_path, manifest_path)}
    assets = {asset["file"]: asset for asset in manifest["assets"]}
    if len(assets) != len(manifest["assets"]):
        raise ValueError("Duplicate manifest asset")
    for name in pack.retained_files:
        asset = assets[name]
        if asset["provenance"] != "procedural-teaching" or asset["role"] != "illustration":
            raise ValueError("Pilot prohibits reference or non-teaching assets")
        path = inside(manifest_path.parent, name)
        if digest(path) != asset["sha256"] or path.stat().st_size != asset["bytes"]:
            raise ValueError(f"Stale asset: {name}")
        dependencies[str(path.relative_to(root))] = digest(path)
    return digest(manifest_path), dependencies


def compile_story(root: Path, path: Path) -> StoryPlan:
    root, path = root.resolve(), path.resolve()
    raw = path.read_text()
    header, beats = parse_story(raw)
    manifest_hash, dependencies = resolve_assets(root, header.asset_pack)
    dependencies[str(path.relative_to(root))] = digest(path)
    at = 0
    projected: list[StoryBeat] = []
    for beat in beats:
        end = at + round(beat.duration * header.fps)
        projected.append(cast(StoryBeat, {**beat.model_dump(), "startFrame": at, "endFrame": end}))
        at = end
    return cast(
        StoryPlan,
        {
            **header.model_dump(by_alias=True),
            "durationFrames": at,
            "beats": projected,
            "source_sha256": digest(path),
            "asset_manifest_sha256": manifest_hash,
            "dependencies": dependencies,
            "scope": SCOPE,
        },
    )


def resolve_stories(root: Path, entries: list[Document]) -> dict[str, StoryPlan]:
    plans: dict[str, StoryPlan] = {}
    for entry in entries:
        illustration = entry.get("illustration")
        if not isinstance(illustration, dict):
            continue
        story_id = illustration.get("story_id")
        if story_id is None:
            continue
        if not isinstance(story_id, str) or not re.fullmatch(r"[a-z0-9-]+", story_id):
            raise MedicalError("Invalid explanation story ID")
        matches = list(root.glob(f"groups/*/presentation/stories/{story_id}.story.md"))
        if len(matches) != 1:
            raise MedicalError(f"Unknown or ambiguous explanation story: {story_id}")
        plan = compile_story(root, matches[0])
        if plan["id"] != story_id:
            raise MedicalError("Story binding and script ID differ")
        plans[story_id] = plan
    return plans


def write_projections(plan: StoryPlan, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")

    def stamp(frame: int, sep: str) -> str:
        ms = round(frame / plan["fps"] * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}{sep}{ms % 1000:03}"

    for ext, sep in (("vtt", "."), ("srt", ",")):
        text = "WEBVTT\n\n" if ext == "vtt" else ""
        for i, beat in enumerate(plan["beats"]):
            text += (
                f"{i + 1}\n{stamp(beat['startFrame'], sep)} --> "
                f"{stamp(beat['endFrame'], sep)}\n{beat['caption']}\n\n"
            )
        (output / f"captions.{ext}").write_text(text)
    (output / "transcript.md").write_text(
        "# "
        + plan["title"]
        + "\n\n"
        + plan["scope"]
        + "\n\n"
        + "\n\n".join(
            f"## {beat['id']} · {beat['caption']}\n\n{beat['narration']}" for beat in plan["beats"]
        )
        + "\n"
    )


def build_export(root: Path, story_id: str, output: Path) -> StoryPlan:
    """Assemble a standalone composed view from the same plan and checked frontend."""
    plans = resolve_stories(root, [{"illustration": {"story_id": story_id}}])
    plan = plans[story_id]
    write_export(root, plan, output)
    return plan


def write_export(root: Path, plan: StoryPlan, output: Path) -> None:
    """Project an explicitly compiled plan to the shared standalone view."""
    from . import frontend

    root = root.resolve()
    for name, expected in plan["dependencies"].items():
        if digest(inside(root, name)) != expected:
            raise ValueError(f"Compiled story dependency changed: {name}")
    script, css = frontend.assets(root, "explainer-export")
    write_projections(plan, output)
    source = next(name for name in plan["dependencies"] if name.endswith(".story.md"))
    (output / "canonical.story.md").write_bytes((root / source).read_bytes())
    common = (root / "presentation/ui.css").read_text()
    payload = json.dumps(plan).replace("<", "\\u003c").replace("&", "\\u0026")
    script = re.sub(r"</script", r"<\\/script", script, flags=re.I)
    (output / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(plan['title'])}</title>"
        f'<style>{common}\n{css}\nbody{{margin:0}}</style><div id="root"></div>'
        f'<script id="story-plan" type="application/json">{payload}</script>'
        f"<script>{script}</script></html>"
    )
