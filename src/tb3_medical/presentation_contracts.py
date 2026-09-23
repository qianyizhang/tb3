"""Versioned browser payloads: Python authority, validation and generated TS types.

These are presentation projections, not replacements for scientific record schemas.
Additional source fields survive projection; only declared browser fields are required.
"""

from __future__ import annotations

import argparse
import json
import types
from pathlib import Path
from typing import (
    Literal,
    NotRequired,
    TypedDict,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)

from .errors import MedicalError
from .types import Document

VisualRole = Literal["input", "helpers", "answer"]
TaskTab = Literal["overview", "requirements", "examples", "sources"]
BrowseView = Literal["capability", "repository"]
ResearchLane = Literal["tasks", "supporting", "all"]
BriefField = Literal[
    "goal",
    "value",
    "raw",
    "helpers",
    "output",
    "challenge",
    "spec",
    "tools",
    "score",
    "reference",
    "families",
    "gap",
    "case_note",
]


class Illustration(TypedDict):
    kind: str
    input: str
    output: str
    caption: str
    subject: NotRequired[str]
    target: NotRequired[str]
    scene_variant: NotRequired[str]
    labels: NotRequired[list[str]]


class Study(TypedDict):
    id: str
    title: str
    scope: str
    tasks: list[str]
    protocol: str
    record_path: str


class Condition(TypedDict):
    name: str
    helper: str
    remaining: str


class Visuals(TypedDict):
    input: str
    helpers: str
    answer: str


class LocalizedBrief(TypedDict):
    title: str
    goal: str
    value: str
    raw: str
    helpers: str
    output: str
    challenge: str
    spec: str
    tools: str
    score: str
    reference: str
    families: str
    gap: str
    case_note: str
    variants: list[Condition]
    sources: list[tuple[str, str]]
    visuals: Visuals
    html: dict[BriefField, str]
    stages: list[str]
    missing_media: list[str]


class TaskEntry(TypedDict):
    id: str
    title: str
    repo: str
    repository_id: NotRequired[str]
    category: str
    role: NotRequired[str]
    agent_work: str
    modalities: list[str]
    owner_group: NotRequired[str]
    operations: NotRequired[list[str]]
    task_family: NotRequired[str]
    nav_group: NotRequired[str]
    nav_label: NotRequired[str]
    proposed: NotRequired[bool]
    goal: str
    value: str
    raw: str
    helpers: str
    output: str
    challenge: str
    spec: str
    tools: str
    score: str
    reference: str
    families: str
    gap: str
    case_note: str
    variants: list[Condition]
    sources: list[tuple[str, str]]
    visuals: Visuals
    html: NotRequired[dict[BriefField, str]]
    illustration: NotRequired[Illustration]
    missing_media: NotRequired[list[str]]
    example_case_id: NotRequired[str]
    studies: NotRequired[list[Study]]
    stages: NotRequired[list[str]]
    locales: NotRequired[dict[str, LocalizedBrief]]


class CaseFact(TypedDict):
    value: str | int | float
    label: str


class CaseContext(TypedDict):
    label: NotRequired[str]
    facts: NotRequired[list[CaseFact]]
    source: NotRequired[str]


class InventoryItem(TypedDict):
    id: str
    title: str
    brief_id: NotRequired[str]
    kind: str
    definition: str
    condition: str
    condition_index: NotRequired[int]
    family: NotRequired[str]
    url: str
    brief_scope_note: NotRequired[str]
    case_context: NotRequired[CaseContext]


class RepositoryInventory(TypedDict):
    id: str
    items: list[InventoryItem]
    coverage: str
    observed_on: str
    commit: str


class LocalSource(TypedDict, total=False):
    sha256: str
    bytes: int
    base64: str
    content: str
    unavailable: str


class SourceDigest(TypedDict):
    path: str
    sha256: str


class SnapshotPanel(TypedDict):
    role: Literal["input", "reference", "metadata"]
    caption: str
    image_url: NotRequired[str]
    text: NotRequired[str]
    path: NotRequired[str]


class DatasetSnapshot(TypedDict):
    sample_id: str
    status: Literal["paired", "input-only", "reference-only", "unavailable"]
    summary: str
    panels: list[SnapshotPanel]
    reference_note: str
    sources: list[SourceDigest]


class SampleReceipt(SourceDigest):
    pointer: NotRequired[str]


class SampleSet(TypedDict):
    label: str
    role: str
    sample_ids: list[str]
    note: str
    receipt: SampleReceipt


class DatasetExperiment(TypedDict):
    id: str
    title: str


class SourceLink(TypedDict):
    path: str
    label: str


class DatasetLocalized(TypedDict):
    title: str
    summary: str
    modality: str
    sample_unit: str
    image_description: str
    annotation_description: str
    reference_note: str
    version_note: str
    terms_note: str
    access_note: str
    documentation_gaps: list[str]
    sample_set_notes: list[str]
    snapshot_summary: str
    snapshot_reference_note: str
    snapshot_captions: list[str]


class DatasetRecord(TypedDict):
    id: str
    title: str
    modality: str
    summary: str
    image_description: str
    annotation_description: str
    sample_unit: str
    reference_note: str
    sample_sets: list[SampleSet]
    task_ids: list[str]
    experiments: list[DatasetExperiment]
    links: NotRequired[list[SourceLink]]
    version_note: str
    terms_note: str
    access_note: NotRequired[str]
    documentation_gaps: NotRequired[list[str]]
    record_path: str
    locales: NotRequired[dict[str, DatasetLocalized]]


class CategoryInfo(TypedDict):
    title: str
    description: str


class Taxonomy(TypedDict, total=False):
    categories: dict[str, CategoryInfo]
    roles: dict[str, str]
    agent_work: dict[str, str]
    modalities: dict[str, str]


class TaskFamily(TypedDict):
    title: str
    selector: str


class PresentationContext(TypedDict, total=False):
    home_url: str
    home_label: str
    story_urls: dict[str, str]


class DatasetCoverage(TypedDict, total=False):
    experiments: int
    scope: str


class DatasetCollection(TypedDict):
    records: list[DatasetRecord]
    previews: NotRequired[dict[str, DatasetSnapshot]]
    coverage: DatasetCoverage


class Inventory(TypedDict, total=False):
    repositories: list[RepositoryInventory]


class ExplorerData(TypedDict):
    schema_version: Literal[1]
    title: NotRequired[str]
    entries: list[TaskEntry]
    inventory: Inventory
    taxonomy: Taxonomy
    task_families: NotRequired[dict[str, TaskFamily]]
    repository_contexts: NotRequired[dict[str, str]]
    local_sources: dict[str, LocalSource]
    presentation_context: NotRequired[PresentationContext]
    datasets: NotRequired[DatasetCollection]


class VocabularyTerm(TypedDict):
    label: str
    definition: str


class VocabularyAxis(TypedDict):
    values: dict[str, VocabularyTerm]


class OverviewVocabulary(TypedDict):
    axes: dict[str, VocabularyAxis]
    context_badges: dict[str, VocabularyTerm]
    display_rules: dict[str, str | list[str]]


class ReviewFlag(TypedDict):
    experiment_id: str
    assessment: str
    reason: str


class RecordCurrent(TypedDict, total=False):
    review_flags: list[ReviewFlag]


class PortableLink(TypedDict):
    label: str
    url: NotRequired[str | None]


class ResearchRecord(TypedDict):
    id: str
    kind: str
    current: RecordCurrent
    portable_links: NotRequired[list[PortableLink]]
    experiment_ids: NotRequired[list[str]]


class OverviewData(TypedDict):
    schema_version: Literal[1]
    records: list[ResearchRecord]
    vocabulary: OverviewVocabulary
    task_explorer_url: NotRequired[str | None]
    local_media: bool


ALIASES = {
    name: globals()[name]
    for name in ("VisualRole", "TaskTab", "BrowseView", "ResearchLane", "BriefField")
}
MODELS = {name: model for name, model in list(globals().items()) if is_typeddict(model)}
EXTENSIBLE = {"ResearchRecord", "RecordCurrent", "DatasetRecord"}
GENERATED = Path("presentation/frontend/contracts.generated.ts")


def _fields(model: object) -> list[tuple[str, object, bool]]:
    fields = []
    for name, kind in get_type_hints(model, include_extras=True).items():
        optional = get_origin(kind) is NotRequired or not getattr(model, "__total__", True)
        fields.append(
            (name, get_args(kind)[0] if get_origin(kind) is NotRequired else kind, optional)
        )
    return fields


def _validate(value: object, kind: object, path: str) -> None:
    origin, args = get_origin(kind), get_args(kind)
    if is_typeddict(kind):
        if not isinstance(value, dict):
            raise MedicalError(f"{path}: expected object")
        for name, field_type, optional in _fields(kind):
            if name not in value:
                if optional:
                    continue
                raise MedicalError(f"{path}.{name}: required field is missing")
            _validate(value[name], field_type, path + "." + name)
    elif origin is Literal:
        if not any(type(value) is type(item) and value == item for item in args):
            raise MedicalError(f"{path}: unsupported value {value!r}")
    elif origin is types.UnionType:
        for candidate in args:
            try:
                _validate(value, candidate, path)
                return
            except MedicalError:
                pass
        raise MedicalError(f"{path}: incompatible value type")
    elif origin in (list, tuple):
        if not isinstance(value, (list, tuple)) or (origin is tuple and len(value) != len(args)):
            raise MedicalError(f"{path}: expected {'array' if origin is list else 'fixed tuple'}")
        for index, item in enumerate(value):
            _validate(item, args[0] if origin is list else args[index], f"{path}[{index}]")
    elif origin is dict:
        if not isinstance(value, dict):
            raise MedicalError(f"{path}: expected mapping")
        for key, item in value.items():
            _validate(key, args[0], path + ".<key>")
            _validate(item, args[1], path + "." + str(key))
    elif kind is not object and type(value) is not kind:
        raise MedicalError(f"{path}: expected {getattr(kind, '__name__', kind)}")


def validate_payload(data: Document, surface: Literal["explorer", "overview"]) -> Document:
    """Validate the emitted boundary, retaining additional scientific source fields."""
    _validate(data, ExplorerData if surface == "explorer" else OverviewData, surface)
    return data


def _ts(kind: object) -> str:
    origin, args = get_origin(kind), get_args(kind)
    if is_typeddict(kind):
        return cast(type, kind).__name__
    if origin is Literal:
        return " | ".join(json.dumps(item) for item in args)
    if origin is types.UnionType:
        return " | ".join(dict.fromkeys(_ts(item) for item in args))
    if origin is list:
        return f"Array<{_ts(args[0])}>"
    if origin is tuple:
        return "[" + ", ".join(_ts(item) for item in args) + "]"
    if origin is dict:
        key = _ts(args[0])
        # Authored HTML fields may be absent and fall back to escaped text.
        mapping = f"Record<{key}, {_ts(args[1])}>"
        return f"Partial<{mapping}>" if args[0] == BriefField else mapping
    return {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        type(None): "null",
        object: "unknown",
    }[cast(type, kind)]


def typescript() -> str:
    lines = ["// Generated by python -m tb3_medical.presentation_contracts. Do not edit."]
    for name, kind in ALIASES.items():
        lines.append(f"export type {name} = {_ts(kind)};")
    for name, model in MODELS.items():
        lines.append(f"export interface {name} {{")
        for field, kind, optional in _fields(model):
            lines.append(f"  {field}{'?' if optional else ''}: {_ts(kind)};")
        if name in EXTENSIBLE:
            lines.append("  [key: string]: unknown;")
        lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = Path.cwd() / GENERATED
    expected = typescript()
    if args.check:
        if not target.is_file() or target.read_text() != expected:
            print("Frontend types are stale; run python -m tb3_medical.presentation_contracts")
            return 1
        print("Python and TypeScript presentation contracts match")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
