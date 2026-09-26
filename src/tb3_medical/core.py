"""Small authoring records and experiment-level review state.

Inspection reads metadata only. Input verification belongs to run/replay/export.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import uuid
from collections.abc import Iterable, Iterator, Mapping, Sequence
from importlib.resources import files
from pathlib import Path
from typing import Any

from . import errors, storage
from .types import Document, Pathish, Records

KINDS = {
    "group",
    "experiment",
    "idea",
    "decision",
    "attempt",
    "evaluation",
    "finding",
    "issue",
    "review",
    "dataset",
    "export",
    "discussion",
    "plan",
    "freeze",
}
ANALYSIS_KINDS = {
    "result",
    "comparison",
    "trace_analysis",
    "audit",
    "synthesis",
}
VOCABULARY = json.loads(files("tb3_medical").joinpath("vocabulary.json").read_text())
RECORD_GLOBS = (
    "groups/*/group.json",
    "groups/*/ideas/*.md",
    "groups/*/decisions/*.json",
    "groups/*/findings/*.json",
    "groups/*/reviews/*.json",
    "groups/*/experiments/*/experiment.toml",
    "groups/*/experiments/*/attempts/*.json",
    "groups/*/experiments/*/evaluations/*.json",
    "groups/*/experiments/*/freezes/*.json",
    "groups/*/experiments/*/plans/*.json",
    "groups/*/experiments/*/reviews/*.json",
    "datasets/*.json",
    "discussions/records/*.json",
    "exports/records/*.json",
)
REQUIRED = {
    "group": ("title",),
    "experiment": ("group_id", "title"),
    "idea": ("group_id", "title", "idea_state"),
    "attempt": ("group_id", "experiment_id"),
    "evaluation": ("experiment_id", "attempt_id", "outcome", "execution_state"),
    "finding": ("group_id", "claim", "experiment_ids"),
    "issue": ("experiment_ids", "reason", "pending_action"),
    "review": ("experiment_id", "assessment", "reason", "actor", "scope"),
    "decision": ("target_id", "idea_state", "actor", "accepted", "reason", "source"),
    "freeze": ("experiment_id", "files", "task_digest", "snapshot_path"),
    "plan": ("experiment_id", "execution_state"),
    "export": ("experiment_ids", "submission_status"),
}


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def identifier(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,127}", value):
        raise errors.MedicalError("IDs use lowercase letters, digits, dot, underscore and hyphen")
    return value


def uid(prefix: str) -> str:
    return prefix + "-" + uuid.uuid4().hex[:16]


def workspace(start: Pathish | None = None) -> Path:
    start = Path(start or Path.cwd()).resolve()
    for path in (start, *start.parents):
        if (path / "workbench.toml").is_file():
            return path
    raise errors.MedicalError("No workbench.toml found; use --root /path/to/workspace")


def evidence(root: Pathish, relative: Pathish) -> dict[str, str]:
    path = storage.inside(root, relative)
    if not path.is_file():
        raise errors.MedicalError(f"Missing evidence: {relative}")
    return {"path": str(relative), "sha256": storage.sha(path)}


def verify_inputs(root: Pathish, entries: Iterable[Mapping[str, Any]]) -> None:
    """Check only the files consumed by the requested operation."""
    for entry in entries:
        path = storage.inside(root, entry["path"])
        if not path.is_file():
            raise errors.MedicalError(f"Missing input: {entry['path']}")
        if storage.sha(path) != entry["sha256"]:
            raise errors.MedicalError(f"Changed input: {entry['path']}")


def validate_record(row: Document, path: Pathish) -> None:
    key = identifier(row.get("id"))
    kind = row.get("kind")
    if row.get("schema_version") != 2 or kind not in KINDS:
        raise errors.MedicalError(f"Unsupported record: {path}")
    missing = [name for name in REQUIRED.get(kind, ()) if name not in row]
    if missing:
        raise errors.MedicalError(f"{key}: missing {', '.join(missing)}")
    for axis, values in VOCABULARY["axes"].items():
        if axis in row and row[axis] not in values["values"]:
            raise errors.MedicalError(f"{key}: unknown {axis}: {row[axis]}")
    if kind == "review" and (not row["reason"] or not row["scope"]):
        raise errors.MedicalError(f"{key}: review needs reason and scope")
    if kind == "finding" and row.get("analysis_kind") not in {None, *ANALYSIS_KINDS}:
        raise errors.MedicalError(f"{key}: unknown analysis_kind: {row['analysis_kind']}")


def record_paths(root: Pathish) -> Iterator[tuple[Path, Document]]:
    for pattern in RECORD_GLOBS:
        for path in sorted(Path(root).glob(pattern)):
            row = storage.read_object(path)
            validate_record(row, path)
            yield path, row


def load(root: Pathish) -> Records:
    rows = {}
    for path, row in record_paths(root):
        if row["id"] in rows:
            raise errors.MedicalError(f"Duplicate record ID: {row['id']}")
        rows[row["id"]] = {**row, "record_path": str(path.relative_to(root))}
    return rows


def lookup(root: Pathish, key: str) -> Document:
    try:
        return load(root)[key]
    except KeyError:
        raise errors.MedicalError(
            f"Unknown ID: {key}; use med list to find its stable ID"
        ) from None


def experiment_ids(row: Document, rows: Records) -> list[str]:
    if row["kind"] == "group":
        return sorted(
            r["id"]
            for r in rows.values()
            if r["kind"] == "experiment" and r["group_id"] == row["id"]
        )
    if row["kind"] == "experiment":
        return [row["id"]]
    if row.get("experiment_id"):
        return [row["experiment_id"]]
    identities: list[str] = row.get("experiment_ids", [])
    return identities


def execution_observations(rows: Records) -> Records:
    """Latest execution/result per attempt, before any eligibility filtering.

    Untyped imported Harbor observations remain supported. Evaluations owned by
    another experiment and explicit replay/trace kinds do not describe execution.
    """
    latest = {}
    for row in sorted(rows.values(), key=lambda r: (r.get("collected_at", ""), r["id"])):
        if row["kind"] != "evaluation" or row.get("evaluation_kind") not in {
            None,
            "execution",
            "result",
        }:
            continue
        attempt = rows.get(row["attempt_id"], {})
        if row.get("evaluation_kind") is None:
            imported_result = all(
                row.get(field)
                for field in ("source_result", "source_classification", "evidence_sha256")
            )
            launcher_receipt = attempt.get("execution_path") and any(
                entry.get("path") == attempt["execution_path"] for entry in row.get("evidence", [])
            )
            if not (imported_result or launcher_receipt):
                continue
        if row["experiment_id"] == attempt.get("experiment_id"):
            latest[row["attempt_id"]] = row
    return latest


def projection(root: Pathish, *, pending_review: Document | None = None) -> Records:
    return project_records(load(root), pending_review=pending_review)


def project_records(
    loaded: Mapping[str, Document], *, pending_review: Document | None = None
) -> Records:
    """Derive current state from already-loaded records without changing the input."""
    rows = dict(loaded)
    if pending_review is not None:
        rows[pending_review["id"]] = pending_review
    latest_observations = execution_observations(rows)
    reviews = sorted(
        (r for r in rows.values() if r["kind"] == "review"),
        key=lambda r: (r.get("created_at", ""), r["id"]),
    )
    decisions = sorted(
        (r for r in rows.values() if r["kind"] == "decision"),
        key=lambda r: (r.get("created_at", ""), r["id"]),
    )
    resolved = {(r["experiment_id"], issue) for r in reviews for issue in r.get("resolves", [])}
    issues = [r for r in rows.values() if r["kind"] == "issue"]
    states = {}
    for row in rows.values():
        state = {axis: row[axis] for axis in VOCABULARY["axes"] if axis in row}
        state["attention"] = False
        state["review_flags"] = []
        if row["kind"] == "experiment":
            state.setdefault("assessment", "not_assessed")
            for review in reviews:
                if review["experiment_id"] == row["id"]:
                    state.update(
                        assessment=review["assessment"],
                        assessment_reason=review["reason"],
                        assessment_scope=review["scope"],
                        latest_review=review["id"],
                    )
            pending = [
                i
                for i in issues
                if row["id"] in i["experiment_ids"]
                and i["pending_action"]
                and (row["id"], i["id"]) not in resolved
            ]
            if pending:
                state["attention"] = True
                state["issue_ids"] = [i["id"] for i in pending]
                state["assessment"] = "needs_review"
                state["assessment_reason"] = "; ".join(i["reason"] for i in pending)
            if state["assessment"] == "needs_review":
                state["attention"] = True
        elif row["kind"] == "idea":
            for decision in decisions:
                if decision["target_id"] == row["id"] and decision["accepted"]:
                    state.update(idea_state=decision["idea_state"], latest_decision=decision["id"])
        elif row["kind"] == "attempt":
            last = latest_observations.get(row["id"])
            if last:
                state.update(
                    execution_state=last["execution_state"],
                    outcome=last["outcome"],
                    observed_at=last.get("collected_at"),
                    partial=last.get("partial", False),
                )
        states[row["id"]] = state
    for row in rows.values():
        if row["kind"] not in {"group", "finding", "export"}:
            continue
        for key in experiment_ids(row, rows):
            if key not in states:
                raise errors.MedicalError(f"{row['id']}: missing experiment {key}")
            state = states[key]
            if state.get("assessment") in {"needs_review", "invalidated"}:
                states[row["id"]]["review_flags"].append(
                    {
                        "experiment_id": key,
                        "assessment": state["assessment"],
                        "reason": state.get("assessment_reason", ""),
                        "attention": state["attention"],
                    }
                )
        states[row["id"]]["attention"] = any(
            f["attention"] for f in states[row["id"]]["review_flags"]
        )
    return {
        key: {
            **row,
            **({"experiment_ids": experiment_ids(row, rows)} if row["kind"] == "group" else {}),
            "current": states[key],
        }
        for key, row in rows.items()
    }


def validate(root: Pathish) -> Document:
    rows = load(root)
    reproduction_cases = 0
    for row in rows.values():
        refs = [
            (field, row[field])
            for field in ("group_id", "experiment_id", "attempt_id", "target_id", "freeze_id")
            if row.get(field)
        ]
        refs += [("experiment_id", key) for key in experiment_ids(row, rows)]
        refs += [("issue_id", key) for key in row.get("resolves", [])]
        for field, key in refs:
            if key not in rows:
                raise errors.MedicalError(f"{row['id']}: missing {field} {key}")
            expected = {
                "group_id": "group",
                "experiment_id": "experiment",
                "attempt_id": "attempt",
                "freeze_id": "freeze",
                "issue_id": "issue",
            }.get(field)
            if expected and rows[key]["kind"] != expected:
                raise errors.MedicalError(f"{row['id']}: {field} must reference {expected}")
        if row["kind"] == "experiment" and row.get("reproduction_manifest"):
            from .task_package import validate_metadata

            reproduction_cases += validate_metadata(root, row, rows)
    return {
        "records": len(rows),
        "groups": sum(r["kind"] == "group" for r in rows.values()),
        "experiments": sum(r["kind"] == "experiment" for r in rows.values()),
        "reproduction_cases": reproduction_cases,
        "artifact_checks": "not performed; verify selected inputs when running, replaying or exporting",
    }


def destination(root: Pathish, row: Document, folder: str) -> Path:
    group = row["id"] if row["kind"] == "group" else row.get("group_id")
    if not isinstance(group, str):
        raise errors.MedicalError("Select a group owner")
    group_row = lookup(root, group)
    if group_row["kind"] != "group":
        raise errors.MedicalError("Select a group owner")
    return Path(root) / Path(group_row["record_path"]).parent / folder


def add_idea(
    root: Pathish, group: str, key: str, title: str, question: str, source: str
) -> Document:
    identifier(key)
    if key in load(root):
        raise errors.MedicalError("Idea already exists; edit its Markdown or record a decision")
    owner = lookup(root, group)
    row = {
        "schema_version": 2,
        "kind": "idea",
        "id": key,
        "group_id": owner["id"],
        "title": title,
        "idea_state": "exploring",
        "source": source,
        "body": f"# {title}\n\n{question}\n\n## Prior findings\n\n## Reopen when",
    }
    storage.write_new(destination(root, owner, "ideas") / (key + ".md"), row)
    return row


def decide(
    root: Pathish,
    idea: str,
    state: str,
    reason: str,
    actor: str,
    source: str,
    accepted: bool = False,
) -> Document:
    row = lookup(root, idea)
    if row["kind"] != "idea":
        raise errors.MedicalError("Decisions apply to ideas")
    event = {
        "schema_version": 2,
        "kind": "decision",
        "id": uid("decision"),
        "group_id": row["group_id"],
        "target_id": row["id"],
        "idea_state": state,
        "reason": reason,
        "actor": actor,
        "source": source,
        "created_at": now(),
        "accepted": actor == "user" or accepted,
    }
    validate_record(event, idea)
    storage.write_new(destination(root, row, "decisions") / (event["id"] + ".json"), event)
    return event


def issue(
    root: Pathish, targets: Sequence[str], reason: str, paths: Sequence[str], actor: str
) -> Document:
    rows = load(root)
    affected = {key for target in targets for key in experiment_ids(rows[target], rows)}
    attempts = {
        rows[target]["attempt_id"] for target in targets if rows[target]["kind"] == "evaluation"
    }
    attempts.update(target for target in targets if rows[target]["kind"] == "attempt")
    entire_experiments = {target for target in targets if rows[target]["kind"] == "experiment"}
    attempts.update(
        r["id"]
        for r in rows.values()
        if r["kind"] == "attempt" and r["experiment_id"] in entire_experiments
    )
    # A comparison may reuse an earlier round's attempt. Include experiments that
    # explicitly evaluate that same execution, without a general dependency graph.
    affected.update(
        r["experiment_id"]
        for r in rows.values()
        if r["kind"] == "evaluation" and r["attempt_id"] in attempts
    )
    affected_ids = sorted(affected)
    if not affected_ids or not reason:
        raise errors.MedicalError("Name an affected experiment or run and a concrete reason")
    owner = rows[affected_ids[0]]
    event = {
        "schema_version": 2,
        "kind": "issue",
        "id": uid("issue"),
        "group_id": owner["group_id"],
        "experiment_ids": affected_ids,
        "affected_records": targets,
        "reason": reason,
        "pending_action": True,
        "actor": actor,
        "created_at": now(),
        "evidence": [evidence(root, p) for p in paths],
    }
    storage.write_new(destination(root, owner, "reviews") / (event["id"] + ".json"), event)
    return event


def review(
    root: Pathish,
    experiment: str,
    assessment: str,
    reason: str,
    scope: str,
    paths: Sequence[str],
    actor: str,
    resolves: Sequence[str] = (),
    eligible_attempts: Sequence[str] = (),
    *,
    qualify_attempts: Sequence[str] = (),
) -> Document:
    owner = lookup(root, experiment)
    if owner["kind"] != "experiment" or not reason or not scope:
        raise errors.MedicalError("Review an experiment's stated conclusions with reason and scope")
    if assessment == "not_assessed" and projection(root)[experiment]["current"]["assessment"] in {
        "needs_review",
        "invalidated",
    }:
        raise errors.MedicalError(
            "An adverse assessment cannot be reset to not_assessed; record a usable scoped "
            "reassessment and resolve outstanding issues first"
        )
    for key in resolves:
        issue_row = lookup(root, key)
        if issue_row["kind"] != "issue" or experiment not in issue_row["experiment_ids"]:
            raise errors.MedicalError("The issue must affect this experiment")
    event = {
        "schema_version": 2,
        "kind": "review",
        "id": uid("review"),
        "group_id": owner["group_id"],
        "experiment_id": experiment,
        "assessment": assessment,
        "reason": reason,
        "scope": scope,
        "actor": actor,
        "created_at": now(),
        "resolves": list(resolves),
        "eligible_attempts": list(eligible_attempts),
        "evidence": [evidence(root, p) for p in paths],
    }
    validate_record(event, experiment)
    if qualify_attempts:
        if assessment != "usable":
            raise errors.MedicalError("Attempt qualification requires a usable scoped review")
        from .workflow import qualify_attempt

        # Check the proposed resolution before publishing any optimistic state.
        event["eligible_attempts"].extend(
            qualify_attempt(root, experiment, identity, pending_review=event)
            for identity in qualify_attempts
        )
    storage.write_new(destination(root, owner, "reviews") / (event["id"] + ".json"), event)
    return event
