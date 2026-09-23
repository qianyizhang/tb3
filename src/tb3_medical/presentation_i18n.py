"""Audit authored translations and explicitly declared English source fallbacks."""

import re
from pathlib import Path

from . import core as c
from .types import Document, Pathish

MANIFEST = "presentation/i18n-coverage.json"
DATASET_FIELDS = (
    "title",
    "summary",
    "modality",
    "sample_unit",
    "image_description",
    "annotation_description",
    "reference_note",
    "version_note",
    "terms_note",
)


def _fallbacks(manifest: Document, kind: str) -> set[str]:
    rows = manifest.get("source_fallback", {}).get(kind)
    if not isinstance(rows, list) or any(not isinstance(value, str) for value in rows):
        raise c.MedicalError(f"Invalid {kind} translation fallback list")
    if len(rows) != len(set(rows)):
        raise c.MedicalError(f"Duplicate {kind} translation fallback")
    return set(rows)


def check(root: Pathish, briefs: list[Document], datasets: Document) -> Document:
    """Require each reader-facing item to be translated or opted into labeled fallback.

    Called by the composed production catalogue; missing or stale entries fail.
    """
    root = Path(root)
    path = root / MANIFEST
    if not path.is_file():
        raise c.MedicalError("Missing translation coverage manifest")
    manifest = c.read(path)
    if (
        manifest.get("schema_version") != 1
        or manifest.get("source_language") != "en"
        or manifest.get("target_language") != "zh-CN"
    ):
        raise c.MedicalError("Invalid translation coverage contract")
    stories = {
        group["id"]: group for path in root.glob("groups/*/group.json") for group in [c.read(path)]
    }
    source_sets = {
        "briefs": {row["id"] for row in briefs if "zh-CN" not in row.get("locales", {})},
        "datasets": {
            row["id"] for row in datasets["records"] if "zh-CN" not in row.get("locales", {})
        },
        "stories": {
            key
            for key in stories
            if not (root / "groups" / key / "presentation/story.zh-CN.md").is_file()
        },
    }
    for kind, expected in source_sets.items():
        declared = _fallbacks(manifest, kind)
        if expected != declared:
            missing = sorted(expected - declared)
            stale = sorted(declared - expected)
            raise c.MedicalError(
                f"{kind} translation coverage differs; undeclared fallback={missing}, "
                f"stale fallback={stale}"
            )
    for row in datasets["records"]:
        translated = row.get("locales", {}).get("zh-CN")
        if not translated:
            continue
        missing = [field for field in DATASET_FIELDS if not translated.get(field)]
        if missing:
            raise c.MedicalError(f"{row['id']}: incomplete zh-CN fields: {missing}")
        if len(translated.get("sample_set_notes", [])) != len(row["sample_sets"]):
            raise c.MedicalError(f"{row['id']}: incomplete zh-CN sample notes")
        if len(translated.get("sample_set_labels", [])) != len(row["sample_sets"]):
            raise c.MedicalError(f"{row['id']}: incomplete zh-CN sample labels")
        if len(translated.get("documentation_gaps", [])) != len(row.get("documentation_gaps", [])):
            raise c.MedicalError(f"{row['id']}: incomplete zh-CN documentation gaps")
        if row.get("access_note") and not translated.get("access_note"):
            raise c.MedicalError(f"{row['id']}: missing zh-CN access note")
        snapshot = datasets.get("previews", {}).get(row["id"])
        if snapshot and (
            not translated.get("snapshot_summary")
            or not translated.get("snapshot_reference_note")
            or len(translated.get("snapshot_captions", [])) != len(snapshot["panels"])
        ):
            raise c.MedicalError(f"{row['id']}: incomplete zh-CN snapshot")
    for row in briefs:
        translated = row.get("locales", {}).get("zh-CN")
        if not translated:
            continue
        for field in (
            "title",
            "goal",
            "value",
            "raw",
            "helpers",
            "reference",
            "spec",
            "output",
            "score",
            "challenge",
        ):
            if not re.search(r"[\u3400-\u9fff]", translated.get(field, "")):
                raise c.MedicalError(f"{row['id']}: missing authored zh-CN {field}")
        if len(translated["variants"]) != len(row["variants"]):
            raise c.MedicalError(f"{row['id']}: zh-CN condition count differs")
    return {
        kind: {
            "translated": len(all_ids) - len(source_sets[kind]),
            "source_fallback": len(source_sets[kind]),
        }
        for kind, all_ids in (
            ("briefs", briefs),
            ("datasets", datasets["records"]),
            ("stories", stories),
        )
    }
