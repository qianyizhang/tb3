"""Small authoring records and experiment-level review state.

Inspection reads metadata only. Input verification belongs to run/replay/export.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import re
import tomllib
import uuid

import tomli_w


class MedicalError(ValueError):
    pass


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
    "discussions/*.json",
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


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,127}", value):
        raise MedicalError("IDs use lowercase letters, digits, dot, underscore and hyphen")
    return value


def uid(prefix):
    return prefix + "-" + uuid.uuid4().hex[:16]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def workspace(start=None):
    start = Path(start or Path.cwd()).resolve()
    for path in (start, *start.parents):
        if (path / "workbench.toml").is_file():
            return path
    raise MedicalError("No workbench.toml found; use --root /path/to/workspace")


def inside(root, relative):
    root, relative = Path(root).resolve(), Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise MedicalError(f"Expected a workspace-relative path: {relative}")
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise MedicalError(f"Path crosses workspace boundary: {relative}")
    if any(p.is_symlink() for p in (path, *path.parents) if p != root):
        raise MedicalError(f"Path crosses a symlink: {relative}")
    return path


def read(path):
    path = Path(path)
    text = path.read_text()
    if path.suffix == ".toml":
        return tomllib.loads(text)
    if path.suffix == ".md":
        if not text.startswith("+++\n") or "\n+++\n" not in text[4:]:
            raise MedicalError(f"Missing TOML metadata header: {path}")
        header, body = text[4:].split("\n+++\n", 1)
        return {**tomllib.loads(header), "body": body.strip()}
    return json.loads(text)


def encode(path, value):
    if Path(path).suffix == ".toml":
        return tomli_w.dumps(value)
    if Path(path).suffix == ".md":
        header = {k: v for k, v in value.items() if k != "body"}
        return "+++\n" + tomli_w.dumps(header) + "+++\n\n" + value.get("body", "") + "\n"
    return json.dumps(value, indent=2, allow_nan=False) + "\n"


def publish(path, value, *, replace=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        tmp.write_text(encode(path, value))
        if replace:
            os.replace(tmp, path)
        else:
            os.link(tmp, path)  # Atomic, exclusive publication; readers never see partial JSON.
    finally:
        tmp.unlink(missing_ok=True)


def write_new(path, value):
    publish(path, value)


def atomic_write(path, value):
    publish(path, value, replace=True)


def evidence(root, relative):
    path = inside(root, relative)
    if not path.is_file():
        raise MedicalError(f"Missing evidence: {relative}")
    return {"path": str(relative), "sha256": sha(path)}


def verify_inputs(root, entries):
    """Check only the files consumed by the requested operation."""
    for entry in entries:
        path = inside(root, entry["path"])
        if not path.is_file():
            raise MedicalError(f"Missing input: {entry['path']}")
        if sha(path) != entry["sha256"]:
            raise MedicalError(f"Changed input: {entry['path']}")


def validate_record(row, path):
    key = identifier(row.get("id"))
    kind = row.get("kind")
    if row.get("schema_version") != 2 or kind not in KINDS:
        raise MedicalError(f"Unsupported record: {path}")
    missing = [name for name in REQUIRED.get(kind, ()) if name not in row]
    if missing:
        raise MedicalError(f"{key}: missing {', '.join(missing)}")
    for axis, values in VOCABULARY["axes"].items():
        if axis in row and row[axis] not in values["values"]:
            raise MedicalError(f"{key}: unknown {axis}: {row[axis]}")
    if kind == "review" and (not row["reason"] or not row["scope"]):
        raise MedicalError(f"{key}: review needs reason and scope")


def record_paths(root):
    for pattern in RECORD_GLOBS:
        for path in sorted(Path(root).glob(pattern)):
            row = read(path)
            validate_record(row, path)
            yield path, row


def load(root):
    rows = {}
    for path, row in record_paths(root):
        if row["id"] in rows:
            raise MedicalError(f"Duplicate record ID: {row['id']}")
        rows[row["id"]] = {**row, "record_path": str(path.relative_to(root))}
    return rows


def lookup(root, key):
    try:
        return load(root)[key]
    except KeyError:
        raise MedicalError(f"Unknown ID: {key}; use med list to find its stable ID") from None


def experiment_ids(row, rows):
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
    return row.get("experiment_ids", [])


def execution_observations(rows):
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


def projection(root, *, pending_review=None):
    rows = load(root)
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
                raise MedicalError(f"{row['id']}: missing experiment {key}")
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


def validate(root):
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
                raise MedicalError(f"{row['id']}: missing {field} {key}")
            expected = {
                "group_id": "group",
                "experiment_id": "experiment",
                "attempt_id": "attempt",
                "freeze_id": "freeze",
                "issue_id": "issue",
            }.get(field)
            if expected and rows[key]["kind"] != expected:
                raise MedicalError(f"{row['id']}: {field} must reference {expected}")
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


def destination(root, row, folder):
    group = row["id"] if row["kind"] == "group" else row.get("group_id")
    group_row = lookup(root, group)
    if group_row["kind"] != "group":
        raise MedicalError("Select a group owner")
    return Path(root) / Path(group_row["record_path"]).parent / folder


def add_idea(root, group, key, title, question, source):
    identifier(key)
    if key in load(root):
        raise MedicalError("Idea already exists; edit its Markdown or record a decision")
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
    write_new(destination(root, owner, "ideas") / (key + ".md"), row)
    return row


def decide(root, idea, state, reason, actor, source, accepted=False):
    row = lookup(root, idea)
    if row["kind"] != "idea":
        raise MedicalError("Decisions apply to ideas")
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
    write_new(destination(root, row, "decisions") / (event["id"] + ".json"), event)
    return event


def issue(root, targets, reason, paths, actor):
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
    affected = sorted(affected)
    if not affected or not reason:
        raise MedicalError("Name an affected experiment or run and a concrete reason")
    owner = rows[affected[0]]
    event = {
        "schema_version": 2,
        "kind": "issue",
        "id": uid("issue"),
        "group_id": owner["group_id"],
        "experiment_ids": affected,
        "affected_records": targets,
        "reason": reason,
        "pending_action": True,
        "actor": actor,
        "created_at": now(),
        "evidence": [evidence(root, p) for p in paths],
    }
    write_new(destination(root, owner, "reviews") / (event["id"] + ".json"), event)
    return event


def review(
    root,
    experiment,
    assessment,
    reason,
    scope,
    paths,
    actor,
    resolves=(),
    eligible_attempts=(),
    *,
    qualify_attempts=(),
):
    owner = lookup(root, experiment)
    if owner["kind"] != "experiment" or not reason or not scope:
        raise MedicalError("Review an experiment's stated conclusions with reason and scope")
    if assessment == "not_assessed" and projection(root)[experiment]["current"]["assessment"] in {
        "needs_review",
        "invalidated",
    }:
        raise MedicalError(
            "An adverse assessment cannot be reset to not_assessed; record a usable scoped "
            "reassessment and resolve outstanding issues first"
        )
    for key in resolves:
        issue_row = lookup(root, key)
        if issue_row["kind"] != "issue" or experiment not in issue_row["experiment_ids"]:
            raise MedicalError("The issue must affect this experiment")
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
            raise MedicalError("Attempt qualification requires a usable scoped review")
        from .workflow import qualify_attempt

        # Check the proposed resolution before publishing any optimistic state.
        event["eligible_attempts"].extend(
            qualify_attempt(root, experiment, identity, pending_review=event)
            for identity in qualify_attempts
        )
    write_new(destination(root, owner, "reviews") / (event["id"] + ".json"), event)
    return event
