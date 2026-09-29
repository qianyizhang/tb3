"""Scope-aware, local queue for bounded explainer completion.

The scope selects work; the ledger owns current review and dependency state. This
module never interprets a replay or a source audit as new visual acceptance.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date as Date
from pathlib import Path

from . import explanation_stories, storage, story_authoring
from .errors import MedicalError
from .types import Document, Pathish

SCOPE = "presentation/EXPLAINER-SCOPE.json"
LEDGER = "presentation/EXPLAINER-LEDGER.json"
SCOPES = frozenset(
    {
        "core",
        "candidate",
        "reference-only",
        "excluded-nonimaging",
        "excluded-nonmedical",
        "historical",
    }
)
REVIEWED = frozenset({"reviewed-scripted-planar", "reviewed-scripted-spatial"})
BLOCKED = frozenset({"blocked-source-contract", "blocked-source-input"})
STATUSES = REVIEWED | BLOCKED | {"pending-operation-review"}


def _object(value: object, label: str) -> Document:
    if not isinstance(value, dict):
        raise MedicalError(f"Expected object at {label}")
    return value


def _rows(value: object, label: str) -> list[Document]:
    if not isinstance(value, list):
        raise MedicalError(f"Expected list at {label}")
    return [_object(row, f"{label}[{index}]") for index, row in enumerate(value)]


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MedicalError(f"Missing explicit {label}")
    return value


def _index(rows: list[Document], label: str, key: str) -> dict[str, Document]:
    indexed: dict[str, Document] = {}
    for row in rows:
        identity = _text(row.get(key), f"{label}.{key}")
        if identity in indexed:
            raise MedicalError(f"Duplicate {label} {key}: {identity}")
        indexed[identity] = row
    return indexed


def _resolution(value: object, entry_id: str) -> Document | None:
    if value is None:
        return None
    resolution = _object(value, f"{entry_id}.dependency_resolution")
    state = resolution.get("state")
    if not isinstance(state, str) or state not in {"needs-resolution", "external-blocked"}:
        raise MedicalError(f"Invalid dependency resolution state: {entry_id}: {state}")
    for field in ("category", "attempt_status", "next_action"):
        _text(resolution.get(field), f"{entry_id}.dependency_resolution.{field}")
    if state == "external-blocked":
        for field in ("evidence", "reopen_condition"):
            _text(resolution.get(field), f"{entry_id}.dependency_resolution.{field}")
    return resolution


def _source_review_receipt(
    root: Path, entry_id: str, source_review: object, *, required: bool = False
) -> tuple[str, str] | None:
    if not isinstance(source_review, dict) or "receipt" not in source_review:
        if required:
            raise MedicalError(f"Missing source review receipt for {entry_id}")
        return None
    relative = _text(source_review["receipt"], f"{entry_id}.source_review.receipt")
    path = storage.inside(root, relative)
    if not path.is_file():
        raise MedicalError(f"Missing source review receipt for {entry_id}: {relative}")
    # Older source reviews pin the same receipt bytes under `sha256`.
    expected = source_review.get("receipt_sha256", source_review.get("sha256"))
    if not isinstance(expected, str) or len(expected) != 64:
        raise MedicalError(f"Missing source review receipt hash for {entry_id}")
    actual = storage.sha(path)
    if actual != expected:
        raise MedicalError(f"Changed source review receipt for {entry_id}: {relative}")
    return relative, actual


def _ready_transition(root: Path, row: Document, entry_id: str) -> None:
    """Require an attempted source resolution before a formerly blocked row is ready."""
    if not any(
        key in row
        for key in ("dependency_deferral", "dependency_resolution", "dependency_resolution_history")
    ):
        return  # Existing pending entries have no source-resolution history.
    if "dependency_resolution" in row:
        raise MedicalError(f"Active dependency resolution must be archived: {entry_id}")
    history = row.get("dependency_resolution_history")
    if not isinstance(history, list) or not history:
        raise MedicalError(f"Missing dependency resolution history for {entry_id}")
    for archived in _rows(history, f"{entry_id}.dependency_resolution_history"):
        _resolution(archived, entry_id)
    basis = row.get("illustration_basis")
    if basis not in ("source-derived", "symbolic", "mixed"):
        raise MedicalError(f"Invalid illustration basis for {entry_id}: {basis}")
    for field in ("actual_data_gap", "acquisition_route", "source_resolution_receipt"):
        _text(row.get(field), f"{entry_id}.{field}")
    if basis in ("symbolic", "mixed"):
        _text(row.get("warning_text"), f"{entry_id}.warning_text")
    pinned = _source_review_receipt(root, entry_id, row.get("source_review"), required=True)
    assert pinned is not None
    relative, _ = pinned
    if row["source_resolution_receipt"] != relative:
        raise MedicalError(f"Source resolution receipt differs from source review: {entry_id}")
    receipt = storage.read_object(storage.inside(root, relative))
    if (
        type(receipt.get("schema")) is not int
        or receipt["schema"] != 1
        or receipt.get("kind") != "explainer-source-resolution"
    ):
        raise MedicalError(f"Invalid source resolution receipt schema or kind: {entry_id}")
    if receipt.get("entry_id") != entry_id:
        raise MedicalError(f"Source resolution receipt entry differs: {entry_id}")
    attempts = _rows(receipt.get("attempts"), f"{entry_id}.source_resolution_attempts")
    if not attempts:
        raise MedicalError(f"Source resolution receipt needs attempts: {entry_id}")
    for attempt in attempts:
        for field in ("action", "source", "outcome", "attempted_at"):
            _text(attempt.get(field), f"{entry_id}.source_resolution_attempt.{field}")


def _load(root: Path) -> tuple[Document, Document, list[Document], list[Document]]:
    scope = storage.read_object(storage.inside(root, SCOPE))
    ledger = storage.read_object(storage.inside(root, LEDGER))
    if scope.get("schema") != 1 or ledger.get("schema") != 1:
        raise MedicalError("Unsupported explainer scope or ledger schema")
    scope_rows = _rows(scope.get("entries"), "scope.entries")
    ledger_rows = _rows(ledger.get("entries"), "ledger.entries")
    scope_by_id = _index(scope_rows, "scope", "entry_id")
    ledger_by_id = _index(ledger_rows, "ledger", "entry_id")
    if scope_by_id.keys() != ledger_by_id.keys():
        missing = sorted(scope_by_id.keys() - ledger_by_id.keys())
        extra = sorted(ledger_by_id.keys() - scope_by_id.keys())
        raise MedicalError(f"Scope/ledger IDs differ: missing={missing}, extra={extra}")
    return scope, ledger, scope_rows, ledger_rows


def inspect_queue(root: Pathish) -> Document:
    """Validate and join the current queue without changing either authority."""
    root_path = Path(root).resolve()
    scope, _, scope_rows, ledger_rows = _load(root_path)
    groups = _rows(scope.get("groups"), "scope.groups")
    group_by_id = _index(groups, "scope group", "group_id")
    for group in groups:
        if group.get("scope") not in SCOPES:
            raise MedicalError(f"Unclassified scope group: {group['group_id']}")
    ledger_by_id = {row["entry_id"]: row for row in ledger_rows}
    ledger_rank = {row["entry_id"]: index for index, row in enumerate(ledger_rows)}
    grouped: dict[str, list[Document]] = {group["group_id"]: [] for group in groups}
    joined: list[Document] = []
    for scope_row in scope_rows:
        entry_id = scope_row["entry_id"]
        group_id = _text(scope_row.get("group_id"), f"{entry_id}.group_id")
        if group_id not in group_by_id:
            raise MedicalError(f"Unclassified entry group: {entry_id}: {group_id}")
        automatic = scope_row.get("automatic_completion")
        if type(automatic) is not bool:
            raise MedicalError(f"Invalid automatic_completion: {entry_id}")
        scope_name = group_by_id[group_id]["scope"]
        if automatic != (scope_name == "core"):
            raise MedicalError(f"Inconsistent automatic_completion and scope: {entry_id}")
        ledger_row = ledger_by_id[entry_id]
        if scope_row.get("brief") != ledger_row.get("brief"):
            raise MedicalError(f"Scope/ledger brief differs: {entry_id}")
        status = ledger_row.get("reviewed_disposition")
        if status not in STATUSES:
            raise MedicalError(f"Unknown explainer status: {entry_id}: {status}")
        resolution = _resolution(ledger_row.get("dependency_resolution"), entry_id)
        reason: str | None = None
        next_action: str | None = None
        if status in BLOCKED:
            reason = _text(ledger_row.get("blocking_dependency"), f"{entry_id}.blocking_dependency")
            next_action = _text(ledger_row.get("remaining_work"), f"{entry_id}.remaining_work")
        elif status == "pending-operation-review":
            if ledger_row.get("blocking_dependency"):
                raise MedicalError(f"Pending entry still has a blocking dependency: {entry_id}")
            _ready_transition(root_path, ledger_row, entry_id)
        if automatic and status == "pending-operation-review":
            disposition = "ready"
        elif automatic and status in BLOCKED and resolution is not None:
            disposition = (
                "needs-resolution" if resolution["state"] == "needs-resolution" else "deferred"
            )
        elif automatic and status in BLOCKED:
            disposition = "deferred"
        elif automatic:
            disposition = "reviewed"
        else:
            disposition = "excluded"
        joined_row: Document = {
            "entry_id": entry_id,
            "title": ledger_row.get("title") or scope_row.get("title") or entry_id,
            "group_id": group_id,
            "scope": scope_name,
            "automatic_completion": automatic,
            "status": status,
            "disposition": disposition,
            "ledger_index": ledger_rank[entry_id],
            "brief": ledger_row.get("brief"),
            "catalogue": ledger_row.get("catalogue"),
            "story_id": ledger_row.get("story_id"),
            "reason": reason,
            "next_action": resolution["next_action"] if resolution is not None else next_action,
            "dependency_resolution": resolution,
        }
        grouped[group_id].append(joined_row)
        joined.append(joined_row)
    ordered = [
        row
        for group in groups
        for row in sorted(grouped[group["group_id"]], key=lambda item: item["ledger_index"])
    ]
    ready = [row["entry_id"] for row in ordered if row["disposition"] == "ready"]
    needs_resolution = [row for row in ordered if row["disposition"] == "needs-resolution"]
    deferred = [row for row in ordered if row["disposition"] == "deferred"]
    reviewed = [row for row in ordered if row["disposition"] == "reviewed"]
    excluded = [row for row in ordered if row["disposition"] == "excluded"]
    warnings: list[str] = []
    snapshot = _object(scope.get("status_snapshot"), "scope.status_snapshot")
    current_ledger_sha = storage.sha(storage.inside(root_path, LEDGER))
    if snapshot.get("sha256") != current_ledger_sha:
        warnings.append(
            "Scope audit ledger hash differs from current ledger; queue uses current ledger status."
        )
    if snapshot.get("core_reviewed") != len(reviewed) or snapshot.get("core_unfinished") != len(
        ready
    ) + len(needs_resolution) + len(deferred):
        warnings.append(
            "Scope audit counts differ from current ledger; current counts are reported below."
        )
    for scope_row in scope_rows:
        entry_id = scope_row["entry_id"]
        brief = _text(scope_row.get("brief"), f"{entry_id}.brief")
        brief_path = storage.inside(root_path, brief)
        if not brief_path.is_file():
            warnings.append(f"Scope brief missing: {entry_id}: {brief}")
        elif storage.sha(brief_path) != scope_row.get("brief_sha256"):
            warnings.append(f"Scope brief hash differs from current file: {entry_id}: {brief}")
    return {
        "schema": 1,
        "scope_sha256": storage.sha(storage.inside(root_path, SCOPE)),
        "ledger_sha256": current_ledger_sha,
        "summary": {
            "catalogue": len(joined),
            "core": len(ready) + len(needs_resolution) + len(deferred) + len(reviewed),
            "ready": len(ready),
            "needs_resolution": len(needs_resolution),
            "deferred": len(deferred),
            "reviewed_core": len(reviewed),
            "excluded": len(excluded),
        },
        "ready_ids": ready,
        "resolution_ids": [row["entry_id"] for row in needs_resolution],
        "resolution": needs_resolution,
        "deferred": deferred,
        "reviewed_ids": [row["entry_id"] for row in reviewed],
        "excluded_ids": [row["entry_id"] for row in excluded],
        "entries": ordered,
        "warnings": warnings,
    }


def prepare(root: Pathish, entry_id: str, output: Pathish, *, regression: bool = False) -> Document:
    """Publish a fresh local task packet for eligible work or explicit regression."""
    root_path = Path(root).resolve()
    queue = inspect_queue(root_path)
    selected = next((row for row in queue["entries"] if row["entry_id"] == entry_id), None)
    if selected is None:
        raise MedicalError(f"Unknown explainer entry: {entry_id}")
    expected = "reviewed" if regression else "ready"
    if selected["disposition"] != expected:
        raise MedicalError(
            f"Entry {entry_id} is {selected['disposition']}; cannot prepare {expected} packet"
        )
    scope, ledger, _, _ = _load(root_path)
    scope_row = next(row for row in scope["entries"] if row["entry_id"] == entry_id)
    ledger_row = next(row for row in ledger["entries"] if row["entry_id"] == entry_id)
    paths: Document = {}
    source_sha256: dict[str, str] = {}
    for name in ("catalogue", "brief"):
        relative = _text(ledger_row.get(name), f"{entry_id}.{name}")
        path = storage.inside(root_path, relative)
        if not path.is_file():
            raise MedicalError(f"Missing {name} for {entry_id}: {relative}")
        paths[name] = {"path": relative, "sha256": storage.sha(path)}
        source_sha256[relative] = paths[name]["sha256"]
    leaf, catalogue_entry = story_authoring.entry_owner(
        root_path, entry_id, paths["catalogue"]["path"]
    )
    if leaf.relative_to(root_path).as_posix() != paths["catalogue"]["path"]:
        raise MedicalError(f"Catalogue ownership differs from ledger for {entry_id}")
    if catalogue_entry.get("brief") != paths["brief"]["path"]:
        raise MedicalError(f"Catalogue brief differs from ledger for {entry_id}")
    illustration = catalogue_entry.get("illustration")
    story_id = illustration.get("story_id") if isinstance(illustration, dict) else None
    if regression and (story_id is None or ledger_row.get("story_id") != story_id):
        raise MedicalError(f"Reviewed story binding differs from ledger for {entry_id}")
    if story_id is not None:
        story_id = _text(story_id, f"{entry_id}.catalogue_story_id")
        plan = explanation_stories.resolve_stories(root_path, [catalogue_entry])[story_id]
        matching_sources = [
            path for path in plan["dependencies"] if path.endswith(f"/{story_id}.story.md")
        ]
        if len(matching_sources) != 1:
            raise MedicalError(f"Expected one canonical story source for {entry_id}")
        story_relative = matching_sources[0]
        story_path = storage.inside(root_path, story_relative)
        paths["story"] = {"path": story_relative, "sha256": storage.sha(story_path)}
        source_sha256[story_relative] = paths["story"]["sha256"]
        paths["catalogue"]["sha256"] = storage.sha(leaf)
        source_sha256[paths["catalogue"]["path"]] = paths["catalogue"]["sha256"]
    source_review = ledger_row.get("source_review")
    pinned_receipt = _source_review_receipt(root_path, entry_id, source_review)
    if pinned_receipt is not None:
        receipt_relative, actual = pinned_receipt
        paths["source_review_receipt"] = {"path": receipt_relative, "sha256": actual}
        source_sha256[receipt_relative] = actual
    packet: Document = {
        "schema": 1,
        "entry_id": entry_id,
        "mode": "regression" if regression else "production",
        "purpose": "regression inspection only; no new acceptance"
        if regression
        else "new explainer completion work",
        "acceptance_eligible": not regression,
        "scope": {"path": SCOPE, "sha256": queue["scope_sha256"], "group_id": selected["group_id"]},
        "ledger": {"path": LEDGER, "sha256": queue["ledger_sha256"], "status": selected["status"]},
        "sources": paths,
        "source_sha256": source_sha256,
        "story_id": story_id,
        "next_action": ledger_row.get("remaining_work"),
        "pins": {
            "scope_brief_sha256": scope_row.get("brief_sha256"),
            "ledger_source_brief_sha256": ledger_row.get("source_brief_sha256"),
            "source_review": source_review,
            "completion_review": ledger_row.get("completion_review") if regression else None,
        },
        "warnings": queue["warnings"],
    }
    output_path = Path(output)
    if output_path.is_absolute():
        try:
            relative_output = output_path.relative_to(root_path)
        except ValueError as exc:
            raise MedicalError("Packet output must be inside the workspace") from exc
    else:
        relative_output = output_path
    output_dir = storage.inside(root_path, relative_output)
    if output_dir.exists():
        raise MedicalError(f"Packet output already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    storage.write_new(output_dir / "packet.json", packet)
    return packet


def defer_blocked(root: Pathish, *, actor: str, source: str, date: str) -> Document:
    """Annotate current blocked core rows for a follow-up session, idempotently."""
    root_path = Path(root).resolve()
    actor = _text(actor, "actor")
    source = _text(source, "source")
    date = _text(date, "date")
    try:
        Date.fromisoformat(date)
    except ValueError as exc:
        raise MedicalError(f"Invalid ISO date: {date}") from exc
    queue = inspect_queue(root_path)
    ledger_path = storage.inside(root_path, LEDGER)
    original_sha256 = queue["ledger_sha256"]
    ledger = storage.read_object(ledger_path)
    deferred_by_id = {
        row["entry_id"]: row for row in queue["deferred"] if row["dependency_resolution"] is None
    }
    changed = 0
    for row in _rows(ledger.get("entries"), "ledger.entries"):
        entry_id = row["entry_id"]
        if entry_id not in deferred_by_id:
            continue
        selected = deferred_by_id[entry_id]
        annotation = {
            "actor": actor,
            "source": source,
            "date": date,
            "reason": selected["reason"],
            "next_action": selected["next_action"],
            "status": "deferred-follow-up",
        }
        existing = row.get("dependency_deferral")
        if existing == annotation:
            continue
        if existing is not None:
            raise MedicalError(f"Conflicting dependency deferral for {entry_id}")
        row["dependency_deferral"] = annotation
        changed += 1
    if changed:
        if storage.sha(ledger_path) != original_sha256:
            raise MedicalError("Explainer ledger changed during deferral; inspect again")
        # Match the ledger's Unicode-preserving JSON format. storage.atomic_write
        # currently escapes Unicode, which would churn unrelated retained prose.
        temporary = ledger_path.with_name(f".{ledger_path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(ledger, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
            )
            if storage.sha(ledger_path) != original_sha256:
                raise MedicalError("Explainer ledger changed during deferral; inspect again")
            os.replace(temporary, ledger_path)
        finally:
            temporary.unlink(missing_ok=True)
    return {
        "schema": 1,
        "annotated": changed,
        "deferred_total": len(queue["deferred"]),
        "preserved_resolution_total": len(queue["deferred"]) - len(deferred_by_id),
        "ledger_sha256": storage.sha(ledger_path),
    }


def render_dependency_register(queue: Document) -> str:
    """Render the joined queue's blocked core rows as a derived Markdown view."""
    summary = _object(queue.get("summary"), "queue.summary")
    blocked = [
        row
        for row in _rows(queue.get("entries"), "queue.entries")
        if row.get("disposition") in {"needs-resolution", "deferred"}
    ]
    lines = [
        "# Explainer dependency register",
        "",
        f"Core: **{summary['core']}** · reviewed: **{summary['reviewed_core']}** · "
        f"ready: **{summary['ready']}** · needs resolution: **{summary['needs_resolution']}** · "
        f"deferred: **{summary['deferred']}**",
        "",
        "This is a derived view of EXPLAINER-SCOPE.json and EXPLAINER-LEDGER.json. "
        "Deferral does not confer visual acceptance.",
        "",
    ]
    for row in blocked:
        resolution = row.get("dependency_resolution")
        classification = resolution["category"] if resolution is not None else "legacy-unclassified"
        attempt_status = resolution["attempt_status"] if resolution is not None else "not recorded"
        lines.extend(
            [
                f"## {row['entry_id']} — {row['title']}",
                "",
                f"- **Group:** {row['group_id']}",
                f"- **Status:** {row['status']}",
                f"- **Queue state:** {row['disposition']}",
                f"- **Classification:** {classification}",
                f"- **Attempt:** {attempt_status}",
                f"- **Current next action:** {row['next_action']}",
                f"- **Prior blocker:** {row['reason']}",
            ]
        )
        if resolution is not None and resolution["state"] == "external-blocked":
            lines.extend(
                [
                    f"- **Evidence:** {resolution['evidence']}",
                    f"- **Reopen condition:** {resolution['reopen_condition']}",
                ]
            )
        lines.append("")
    return "\n".join(lines)
