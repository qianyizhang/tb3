"""Compile group-owned explanation scripts; no model calls or validator I/O."""

from __future__ import annotations

import hashlib
import json
import re
from html import escape
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml  # type: ignore[import-untyped]
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    TypeAdapter,
    model_validator,
)

from .errors import MedicalError
from .presentation_contracts import StoryBeat, StoryPlan
from .types import Document

CHANNELS = ("context", "route", "ribbon", "cursor", "unfold", "output")
RECIPE_PACKS = {
    "topology-v1": "topology-v1",
    "correspondence-v1": "correspondence-v1",
    "multiscale-v1": "multiscale-v1",
    "shape-material-v1": "shape-material-v1",
    "local-edit-v1": "local-edit-v1",
    "longitudinal-v1": "longitudinal-v1",
    "inverse-v1": "inverse-problems-v1",
    "anatomy-audit-v1": "retained-anatomy-v1",
}
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


Unit = Annotated[StrictFloat, Field(ge=0, le=1)]
Pair = tuple[Unit, Unit]
Text = Annotated[str, Field(strict=True, min_length=1)]


class TopologyChannels(Closed):
    focus: Pair
    trace: Pair
    inventory: Pair


class CorrespondenceChannels(Closed):
    transform: Pair
    query: Pair
    residual: Pair


class MaterialChannels(Closed):
    phase: Pair
    markers: Pair
    alternative: Pair


class LongitudinalChannels(Closed):
    visits: Pair
    links: Pair
    coverage: Pair


class MultiscaleChannels(Closed):
    viewport: Pair
    selections: Pair
    coverage: Pair
    outputs: Pair


class InverseChannels(Closed):
    observations: Pair
    reconstruction: Pair
    residual: Pair


class AnatomyChannels(Closed):
    focus: Pair
    evidence: Pair
    output: Pair


class EditChannels(Closed):
    domain: Pair
    correction: Pair
    control: Pair


class ExpansionBeat[Channels: Closed](Closed):
    id: Annotated[str, Field(strict=True, pattern=r"^[a-z0-9-]+$")]
    frames: Annotated[StrictInt, Field(ge=2, le=3600)]
    caption: Text
    narration: Text
    visual: Text
    channels: Channels
    cut: Literal["continuous", "intentional-cut"] = "continuous"


class Story[Channels: Closed](Closed):
    schema_version: Annotated[StrictInt, Field(alias="schema", ge=2, le=2)]
    id: Annotated[str, Field(strict=True, pattern=r"^[a-z0-9-]+$")]
    title: Text
    locale: Literal["en"]
    purpose: Text
    scope: Text
    asset_pack: Text
    source_class: Literal["procedural-teaching", "source-derived-teaching"]
    reference_policy: Literal["no-reference-assets"]
    fps: Annotated[StrictInt, Field(ge=12, le=60)]
    source_locators: Annotated[tuple[Text, ...], Field(min_length=1)]
    beats: tuple[ExpansionBeat[Channels], ...]

    @model_validator(mode="after")
    def timeline(self) -> Self:
        if not self.beats or len({b.id for b in self.beats}) != len(self.beats):
            raise ValueError("Missing or duplicate beats")
        for prev, cur in zip(self.beats, self.beats[1:], strict=False):
            if cur.cut == "continuous":
                a, b = prev.channels.model_dump(), cur.channels.model_dump()
                if any(abs(a[k][1] - b[k][0]) > 1e-9 for k in a):
                    raise ValueError(f"Unmarked channel discontinuity at {cur.id}")
        return self


class TopologyStory(Story[TopologyChannels]):
    recipe: Literal["topology-v1"]


class CorrespondenceStory(Story[CorrespondenceChannels]):
    recipe: Literal["correspondence-v1"]


class MaterialStory(Story[MaterialChannels]):
    recipe: Literal["shape-material-v1"]


class LongitudinalStory(Story[LongitudinalChannels]):
    recipe: Literal["longitudinal-v1"]


class MultiscaleStory(Story[MultiscaleChannels]):
    recipe: Literal["multiscale-v1"]


class InverseStory(Story[InverseChannels]):
    recipe: Literal["inverse-v1"]
    acquisition: Literal["ct-parallel", "mri-cartesian"]


class AnatomyStory(Story[AnatomyChannels]):
    recipe: Literal["anatomy-audit-v1"]


class EditStory(Story[EditChannels]):
    recipe: Literal["local-edit-v1"]


AnyStory = Annotated[
    TopologyStory
    | CorrespondenceStory
    | MaterialStory
    | LongitudinalStory
    | MultiscaleStory
    | InverseStory
    | EditStory
    | AnatomyStory,
    Field(discriminator="recipe"),
]
ADAPTER: TypeAdapter[
    TopologyStory
    | CorrespondenceStory
    | MaterialStory
    | LongitudinalStory
    | MultiscaleStory
    | InverseStory
    | EditStory
    | AnatomyStory
] = TypeAdapter(AnyStory)


class FixturePack(Closed):
    manifest: str = Field(min_length=1, strict=True)
    retained_files: tuple[str, ...]
    runtime_geometry: Literal["fixture.json"]

    @model_validator(mode="after")
    def complete(self) -> Self:
        if "fixture.json" not in self.retained_files or len(set(self.retained_files)) != len(
            self.retained_files
        ):
            raise ValueError("Missing fixture or duplicate dependency")
        return self


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


class AnatomyPack(Closed):
    manifest: str
    retained_files: tuple[str, ...]
    runtime_geometry: Literal["anatomy-assembly"]


class PrefabIndex(Closed):
    schema_version: StrictInt = Field(alias="schema", ge=1, le=1)
    packs: dict[str, AssetPack | FixturePack | AnatomyPack]


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


def parse_expansion(
    raw: str,
) -> (
    TopologyStory
    | CorrespondenceStory
    | MaterialStory
    | LongitudinalStory
    | MultiscaleStory
    | InverseStory
    | EditStory
    | AnatomyStory
):
    match = re.match(r"\A---\n(.*?)\n---\n", raw, re.S)
    if not match:
        raise ValueError("Expected YAML frontmatter")
    obj = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(obj, dict) or "beats" in obj:
        raise ValueError("Beats belong in fenced blocks")
    blocks = re.findall(r"^```beat\n(.*?)^```\s*$", raw, re.M | re.S)
    if len(blocks) != len(re.findall(r"^```beat\s*$", raw, re.M)):
        raise ValueError("Unclosed or malformed beat block")
    obj["beats"] = [yaml.load(block, Loader=UniqueLoader) for block in blocks]
    return ADAPTER.validate_python(obj)


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
    if isinstance(pack, AnatomyPack):
        if pack_id != "retained-anatomy-v1" or not manifest.get("terms"):
            raise ValueError("Invalid anatomy owner or missing terms")
        required_parts = {
            "liver",
            "stomach",
            "spleen",
            "pancreas",
            "kidney_left",
            "kidney_right",
            "gallbladder",
        }
        required_files = {name + ".json" for name in required_parts} | {
            "NOTICE.md",
            "CC-BY-4.0.txt",
        }
        if set(pack.retained_files) != required_files or len(pack.retained_files) != len(
            required_files
        ):
            raise ValueError("Anatomy assembly requires its exact parts and notices")
        frames = {json.dumps(manifest["assets"][name]["affine"]) for name in required_parts}
        cases = {
            manifest["assets"][name]["source"].split("/segmentations/")[0]
            for name in required_parts
        }
        if len(frames) != 1 or len(cases) != 1:
            raise ValueError("Anatomy parts must share a source case and physical frame")
        dependencies = {str(p.relative_to(root)): digest(p) for p in (index_path, manifest_path)}
        for name in pack.retained_files:
            path = inside(manifest_path.parent, name)
            if name.endswith(".json"):
                asset = manifest["assets"][path.stem]
                if digest(path) != asset["asset_sha256"] or path.stat().st_size != asset["bytes"]:
                    raise ValueError(f"Stale anatomy asset: {name}")
            dependencies[str(path.relative_to(root))] = digest(path)
        return digest(manifest_path), dependencies
    if isinstance(pack, FixturePack):
        if (
            manifest.get("license") != "CC0-1.0"
            or not manifest.get("frame")
            or not manifest.get("units")
        ):
            raise ValueError("Fixture terms or coordinate frame missing")
        required = {
            "local-edit-v1": {
                "fixture.json",
                "masks.npz",
                "supplied-mask.png",
                "corrected-mask.png",
                "editable-domain.png",
                "unchanged-control.png",
            },
            "inverse-problems-v1": {
                "fixture.json",
                "arrays.npz",
                "ct-sinogram.png",
                "ct-reconstruction.png",
                "mri-kspace.png",
                "mri-sampled.png",
                "mri-zero-filled.png",
                "object.png",
            },
        }.get(pack_id, {"fixture.json"})
        if not required.issubset(pack.retained_files):
            raise ValueError("Recipe pack missing required dependencies")
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
    if "[[AUTHOR:" in raw:
        raise ValueError("Unfinished story draft: replace every [[AUTHOR:...]] field")
    if re.search(r"^schema: 2$", raw, re.M):
        story = parse_expansion(raw)
        expected_pack = RECIPE_PACKS[story.recipe]
        if story.asset_pack != expected_pack:
            raise ValueError("Recipe asset pack mismatch")
        if (story.recipe == "anatomy-audit-v1") != (
            story.source_class == "source-derived-teaching"
        ):
            raise ValueError("Recipe provenance mismatch")
        manifest_hash, dependencies = resolve_assets(root, story.asset_pack)
        if story.recipe == "topology-v1":
            _, route_dependencies = resolve_assets(root, "tb3-route-kit-v1")
            dependencies.update(route_dependencies)
        dependencies[str(path.relative_to(root))] = digest(path)
        for locator in story.source_locators:
            source = inside(root, locator)
            if not source.is_file():
                raise ValueError(f"Missing story source: {locator}")
            dependencies[locator] = digest(source)
        result = story.model_dump(mode="json", by_alias=True)
        at = 0
        for beat in result["beats"]:
            beat["startFrame"] = at
            at += beat["frames"]
            beat["endFrame"] = at
        result.update(
            durationFrames=at,
            source_sha256=digest(path),
            asset_manifest_sha256=manifest_hash,
            dependencies=dependencies,
        )
        return cast(StoryPlan, result)
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
        matches = list(root.glob(f"groups/*/presentation/stories/{story_id}.story.md")) + list(
            root.glob(f"presentation/external-tasks/stories/{story_id}.story.md")
        )
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
