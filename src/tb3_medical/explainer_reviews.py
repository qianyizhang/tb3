"""Validate a scoped reviewer sign-off; regression never changes acceptance."""

from __future__ import annotations

import json
import os
import uuid
from collections import Counter
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt

from . import explainer_queue, storage, story_batches, task_briefs
from .errors import MedicalError
from .types import Document

Text = Annotated[str, Field(strict=True, min_length=1)]
Digest = Annotated[str, Field(strict=True, pattern=r"^[a-f0-9]{64}$")]


class Witness(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: Text
    sha256: Digest


class Inspection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Annotated[StrictInt, Field(alias="schema", ge=1, le=1)]
    entry_id: Text
    reviewer: Text
    reviewed_at: Text
    scope: Text
    observations: Annotated[list[Text], Field(min_length=1)]
    limits: Annotated[list[Text], Field(min_length=1)]
    checks: dict[str, StrictBool]
    inspected_images: Annotated[dict[str, Digest], Field(min_length=1)]
    collection: Witness
    browser_matrix: Witness
    rendered_mode: Literal["planar", "spatial"]


CHECKS = {"visual", "motion", "explorer", "mobile", "no_gpu", "reference_boundaries"}


def _path(root: Path, path: Path | str) -> Path:
    relative = Path(path)
    if relative.is_absolute():
        try:
            relative = relative.relative_to(root)
        except ValueError as exc:
            raise MedicalError("Review paths must be inside the workspace") from exc
    return storage.inside(root, relative)


def _witness(root: Path, witness: Witness) -> Path:
    path = _path(root, witness.path)
    if storage.sha(path) != witness.sha256:
        raise MedicalError(f"Changed review witness: {witness.path}")
    return path


def record(
    root: Path,
    packet_path: Path,
    batch_path: Path,
    inspection_path: Path,
    output: Path,
    *,
    accept: bool = False,
) -> Document:
    """Require current pins, decoded video and explicit inspection before recording."""
    root = root.resolve()
    packet_path = _path(root, packet_path)
    if packet_path.is_dir():
        packet_path /= "packet.json"
    batch_path = _path(root, batch_path)
    inspection_path = _path(root, inspection_path)
    output = _path(root, output)
    if output.exists():
        raise MedicalError("Review record needs a fresh output file")
    packet = storage.read_object(packet_path)
    inspection = Inspection.model_validate_json(inspection_path.read_bytes())
    entry_id = inspection.entry_id
    if packet.get("entry_id") != entry_id:
        raise MedicalError("Packet and inspection entry differ")
    mode = packet.get("mode")
    if mode not in {"production", "regression"}:
        raise MedicalError("Packet must explicitly identify production or regression")
    if accept and mode != "production":
        raise MedicalError("Regression cannot change acceptance")
    sources = packet.get("source_sha256")
    if not isinstance(sources, dict) or not sources:
        raise MedicalError("Packet source pins are missing")
    for name, digest in sources.items():
        if storage.sha(_path(root, name)) != digest:
            raise MedicalError(f"Packet source changed: {name}; prepare a fresh packet")
    for authority in ("scope", "ledger"):
        pin = packet.get(authority, {})
        if not pin.get("path") or storage.sha(_path(root, pin["path"])) != pin.get("sha256"):
            raise MedicalError(f"Packet {authority} changed; prepare a fresh packet")
    queue = explainer_queue.inspect_queue(root)
    # Eligibility is checked again at sign-off; historical active_entry is irrelevant.
    scope = storage.read_object(root / "presentation/EXPLAINER-SCOPE.json")
    member = next((e for e in scope["entries"] if e["entry_id"] == entry_id), None)
    ledger_path = root / "presentation/EXPLAINER-LEDGER.json"
    ledger_sha = storage.sha(ledger_path)
    ledger = storage.read_object(ledger_path)
    row = next((r for r in ledger["entries"] if r["entry_id"] == entry_id), None)
    if member is None or not member["automatic_completion"] or row is None:
        raise MedicalError("Review entry is outside automatic core scope")
    status = row["reviewed_disposition"]
    if mode == "regression" and not status.startswith("reviewed-"):
        raise MedicalError("Regression requires an already reviewed core entry")
    if mode == "production" and status != "pending-operation-review":
        raise MedicalError("Production requires an unblocked pending operation review")
    if set(inspection.checks) != CHECKS or not all(inspection.checks.values()):
        raise MedicalError("Explicit positive inspection of every required surface is missing")
    for name, digest in inspection.inspected_images.items():
        if storage.sha(_path(root, name)) != digest:
            raise MedicalError(f"Changed inspected image: {name}")
    collection_path = _witness(root, inspection.collection)
    collection = storage.read_object(collection_path)
    if collection.get("schema") != 1 or collection.get("errors") != []:
        raise MedicalError("Review collection is malformed or failed")
    matrix_path = _witness(root, inspection.browser_matrix)
    browser_witness = storage.read_object(matrix_path)
    if (
        browser_witness.get("schema") != 1
        or browser_witness.get("kind") != "explainer-browser-witness"
    ):
        raise MedicalError("Browser evidence needs a current batch-bound witness")
    matrix = storage.read_object(
        _witness(root, Witness.model_validate(browser_witness.get("matrix")))
    )
    pins = browser_witness.get("sources", {})
    required_pins = {
        str((batch_path / "batch.json").relative_to(root)),
        "tests/explanation_expansion_browser.cjs",
        "presentation/tooling/browser.mts",
        "scripts/review_explainer_browser.mts",
        browser_witness.get("explorer"),
    }
    if not isinstance(pins, dict) or not required_pins.issubset(pins):
        raise MedicalError("Browser witness source pins are incomplete")
    for name, digest in pins.items():
        if storage.sha(_path(root, name)) != digest:
            raise MedicalError(f"Browser witness source changed: {name}")
    batch = story_batches.load(batch_path)
    selected = next((e for e in batch.entries if e.entry_id == entry_id), None)
    if selected is None or batch.stills_only:
        raise MedicalError("Review requires this entry in a full-video batch")
    export = batch_path / selected.story_id
    for name in ("plan.json", "receipt.json", "index.html"):
        if str((export / name).relative_to(root)) not in pins:
            raise MedicalError("Browser witness does not pin this export")
    if (
        Path(collection.get("export", "")).resolve() != export.resolve()
        or collection.get("sourceReceiptSha256") != storage.sha(export / "receipt.json")
        or collection.get("planSha256") != storage.sha(export / "plan.json")
        or collection.get("videoSha256") != storage.sha(export / selected.video_name)
        or collection.get("storyId") != selected.story_id
        or collection.get("status") != "pending-human-review"
    ):
        raise MedicalError("Review collection does not match the selected export")
    playback = collection.get("playback", {})
    if (
        playback.get("completion", {}).get("ended") is not True
        or playback.get("completion", {}).get("rate") != 1
        or playback.get("metadata", {}).get("rate") != 1
        or playback.get("pageErrors") != []
        or playback.get("remoteRequests") != []
        or len(playback.get("seeks", [])) != 3
    ):
        raise MedicalError("Completed normal-speed playback and three seeks are required")
    for sample in [
        *collection.get("canonicalStills", []),
        *collection.get("samples", []),
        *playback["seeks"],
    ]:
        if storage.sha(storage.inside(collection_path.parent, sample["file"])) != sample["sha256"]:
            raise MedicalError("A collected review image changed")
    if (
        matrix.get("errors") != []
        or matrix.get("remote_requests") != []
        or not any(r.get("id") == selected.story_id for r in matrix.get("stories", []))
    ):
        raise MedicalError("A passing browser matrix covering this story is required")
    browser_row = next(r for r in matrix["stories"] if r.get("id") == selected.story_id)
    if browser_row.get("fallback") is not True or set(browser_row.get("locales", [])) != {
        "en",
        "zh-CN",
    }:
        raise MedicalError("Browser coverage is missing locales or no-GPU fallback")
    frames = browser_row.get("frames", [])
    for locale in ("en", "zh-CN"):
        captured = {f["frame"] for f in frames if f.get("locale") == locale}
        if not {0, selected.frames - 1}.issubset(captured):
            raise MedicalError("Browser coverage is missing endpoint frames")
    for frame in frames:
        if storage.sha(storage.inside(export, frame["file"])) != frame["sha256"]:
            raise MedicalError("Browser capture changed")
    verification = story_batches.check(root, batch_path, decode=True)
    if not verification["ok"]:
        raise MedicalError("Batch verification failed: " + "; ".join(verification["issues"]))
    report: Document = {
        "schema": 1,
        "entry_id": entry_id,
        "story_id": selected.story_id,
        "mode": mode,
        "acceptance_requested": accept,
        "inspection": inspection.model_dump(mode="json", by_alias=True),
        "packet": {"path": str(packet_path.relative_to(root)), "sha256": storage.sha(packet_path)},
        "batch": {
            "path": str(batch_path.relative_to(root)),
            "sha256": storage.sha(batch_path / "batch.json"),
        },
        "export_receipt_sha256": storage.sha(export / "receipt.json"),
        "verification": verification,
        "queue_summary": queue["summary"],
        "review_ledger_sha256_before": ledger_sha,
    }
    if storage.sha(ledger_path) != ledger_sha:
        raise MedicalError("Review ledger changed during verification; prepare a fresh sign-off")
    storage.write_new(output, report)
    if accept:
        row.update(
            reviewed_disposition=f"reviewed-scripted-{inspection.rendered_mode}",
            observed_binding_state="bound-story-reviewed",
            story_id=selected.story_id,
            rendered_mode=inspection.rendered_mode,
            acceptance_receipt=str(output.relative_to(root)),
            acceptance_scope=inspection.scope,
            blocking_dependency=None,
            remaining_work="No outstanding explainer work within the recorded acceptance scope.",
            completion_review={
                "date": inspection.reviewed_at,
                "reviewer": inspection.reviewer,
                "acceptance_receipt_sha256": storage.sha(output),
            },
            reviewed_contract_projection=task_briefs._brief_projection(root, root / row["brief"]),
        )
        ledger["counts"] = dict(Counter(r["reviewed_disposition"] for r in ledger["entries"]))
        temporary = ledger_path.with_name(f".{ledger_path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(ledger, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
            )
            if storage.sha(ledger_path) != ledger_sha:
                raise MedicalError(
                    "Review ledger changed before acceptance; validated report retained"
                )
            os.replace(temporary, ledger_path)
        finally:
            temporary.unlink(missing_ok=True)
    return {"ok": True, "record": str(output), "mode": mode, "accepted": accept}
