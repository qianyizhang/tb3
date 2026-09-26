"""Draft canonical stories without binding or accepting unfinished explanations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from . import explanation_stories as stories
from . import storage, task_briefs, task_catalog
from .errors import MedicalError
from .types import Document


@dataclass(frozen=True)
class Recipe:
    id: str
    asset_pack: str
    channels: tuple[str, ...]
    acquisitions: tuple[str, ...]


def recipes() -> tuple[Recipe, ...]:
    """Read channel structure from the compiler's canonical Pydantic schema."""
    schema = stories.ADAPTER.json_schema()
    definitions = schema["$defs"]
    result = []
    for variant in schema["oneOf"]:
        fields = definitions[variant["$ref"].split("/")[-1]]["properties"]
        recipe = fields["recipe"]["const"]
        beat = definitions[fields["beats"]["items"]["$ref"].split("/")[-1]]
        channels = definitions[beat["properties"]["channels"]["$ref"].split("/")[-1]]
        result.append(
            Recipe(
                recipe,
                stories.RECIPE_PACKS[recipe],
                tuple(channels["properties"]),
                tuple(fields.get("acquisition", {}).get("enum", ())),
            )
        )
    return tuple(result)


def entry_owner(
    root: Path, entry_id: str, catalog: str = task_catalog.DEFAULT_CATALOG
) -> tuple[Path, Document]:
    """Retain leaf ownership when resolving nested catalogue collections."""
    matches: list[tuple[Path, Document]] = []

    def visit(name: str, parents: tuple[Path, ...]) -> None:
        path = storage.inside(root, name)
        if path in parents:
            raise MedicalError(f"Task collection cycle: {name}")
        data = storage.read_object(path)
        matches.extend((path, row) for row in data.get("entries", []) if row["id"] == entry_id)
        for child in data.get("collections", []):
            visit(child, (*parents, path))

    visit(catalog, ())
    if len(matches) != 1:
        raise MedicalError(f"Expected one catalogue entry for {entry_id}; found {len(matches)}")
    return matches[0]


def new(
    root: Path,
    entry_id: str,
    story_id: str,
    *,
    recipe: str,
    acquisition: str | None = None,
    catalog: str = task_catalog.DEFAULT_CATALOG,
    preview: bool = False,
) -> Document:
    root = root.resolve()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", story_id):
        raise MedicalError("Use a lowercase hyphenated story ID")
    specs = {spec.id: spec for spec in recipes()}
    if recipe not in specs:
        raise MedicalError("Unknown draft recipe; inspect med story recipes")
    spec = specs[recipe]
    if (spec.acquisitions and acquisition not in spec.acquisitions) or (
        not spec.acquisitions and acquisition is not None
    ):
        raise MedicalError(f"Recipe acquisition must be one of {spec.acquisitions or (None,)}")
    leaf, entry = entry_owner(root, entry_id, catalog)
    brief = storage.inside(root, entry["brief"])
    if not brief.is_file():
        raise MedicalError(f"Missing source brief: {entry['brief']}")
    title = task_briefs.sections(brief.read_text()).get("title")
    if not title:
        raise MedicalError("Source brief needs its canonical title")
    owner = leaf.parent / "stories"
    destination = storage.inside(root, owner.relative_to(root) / "drafts" / f"{story_id}.story.md")
    existing = [
        *root.glob(f"groups/*/presentation/stories/**/{story_id}.story.md"),
        *root.glob(f"presentation/external-tasks/stories/**/{story_id}.story.md"),
    ]
    if existing or destination.exists():
        raise MedicalError(f"Story ID or draft already exists: {story_id}")
    header: Document = {
        "schema": 2,
        "id": story_id,
        "title": title,
        "locale": "en",
        "purpose": "[[AUTHOR: one operation this condition asks the solver to perform]]",
        "scope": "[[AUTHOR: actual inputs, assistance, output and teaching/reference limits]]",
        "recipe": recipe,
        "asset_pack": spec.asset_pack,
        "source_class": (
            "source-derived-teaching" if recipe == "anatomy-audit-v1" else "procedural-teaching"
        ),
        "reference_policy": "no-reference-assets",
        "fps": 24,
        "source_locators": [brief.relative_to(root).as_posix()],
    }
    if acquisition is not None:
        header["acquisition"] = acquisition
    content = "---\n" + yaml.safe_dump(header, sort_keys=False, allow_unicode=True) + "---\n"
    content += "\n# Draft explanation\n\nNot bound or visually reviewed.\n"
    for name in ("input", "operation", "output-and-limit"):
        beat = {
            "id": name,
            "frames": 120,
            "caption": f"[[AUTHOR: {name} caption]]",
            "narration": f"[[AUTHOR: {name} source-backed explanation]]",
            "visual": f"[[AUTHOR: {name} visible operation and witness]]",
            "channels": {channel: [0.0, 0.0] for channel in spec.channels},
        }
        content += f"\n## {name}\n\n```beat\n" + yaml.safe_dump(beat, sort_keys=False) + "```\n"
    if not preview:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("x") as file:
            file.write(content)
    return {
        "entry": entry_id,
        "catalogue": leaf.relative_to(root).as_posix(),
        "destination": destination.relative_to(root).as_posix(),
        "preview": preview,
        "bound": False,
        "visual_review": "pending",
        "content": content,
    }


def check(root: Path, source: str) -> Document:
    path = storage.inside(root, source)
    if path.is_file():
        plan = stories.compile_story(root, path)
    else:
        plan = stories.resolve_stories(root, [{"illustration": {"story_id": source}}])[source]
    return {
        "id": plan["id"],
        "recipe": plan["recipe"],
        "frames": plan["durationFrames"],
        "source_sha256": plan["source_sha256"],
        "dependencies": plan["dependencies"],
        "visual_review": "not_assessed",
    }
