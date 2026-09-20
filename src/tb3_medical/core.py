"""Small file-backed records; original observations are never rewritten by reviews."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import uuid


class MedicalError(ValueError):
    pass


KINDS = {"group", "experiment", "idea", "decision", "attempt", "evaluation",
         "finding", "issue", "review", "dataset", "export", "discussion", "plan", "freeze"}
VALIDITY = {"unreviewed", "supported", "under_review", "qualified", "invalidated", "superseded"}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def identifier(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,127}", value):
        raise MedicalError("IDs use lowercase letters, digits, dot, underscore and hyphen")
    return value


def uid(prefix):
    return prefix + "-" + uuid.uuid4().hex[:16]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inside(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise MedicalError(f"Expected a repository-relative path: {relative}")
    p = root / relative
    if not p.resolve().is_relative_to(root) or any(x.is_symlink() for x in [p, *p.parents] if x != root):
        raise MedicalError(f"Path crosses a symlink or workspace boundary: {relative}")
    return p


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def atomic_write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        write_new(tmp, value)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def evidence(root, relative):
    p = inside(root, relative)
    if not p.is_file():
        raise MedicalError(f"Missing evidence: {relative}")
    return {"path": str(relative), "sha256": sha(p)}


def record_paths(root):
    for folder in ("groups", "datasets", "discussions", "exports/records"):
        base = Path(root) / folder
        for p in sorted(base.rglob("*.json")):
            # Figures and source snapshots are payloads, not catalog entries.
            if any(part in {"figures", "methods", "examples", "sources"} for part in p.relative_to(base).parts):
                continue
            value = read(p)
            if isinstance(value, dict) and value.get("kind") in KINDS:
                yield p, value


def load(root):
    result = {}
    for path, value in record_paths(root):
        key = identifier(value["id"])
        if key in result:
            raise MedicalError(f"Duplicate record ID: {key}")
        if value.get("schema_version") != 1:
            raise MedicalError(f"Unsupported record version: {path}")
        if value.get("validity", "unreviewed") not in VALIDITY:
            raise MedicalError(f"Unknown validity: {key}")
        result[key] = {**value, "record_path": str(path.relative_to(root))}
    return result


def lookup(root, key):
    records = load(root)
    if key in records:
        return records[key]
    matches = [v for v in records.values() if key in v.get("aliases", [])]
    if len(matches) != 1:
        raise MedicalError(f"Unknown or ambiguous ID/alias: {key}; use a stable ID")
    return matches[0]


def projection(root):
    records = load(root)
    digests = {}

    def evidence_state(row):
        missing, changed = [], []
        for src in row.get("evidence", []):
            p = inside(root, src["path"])
            if not p.is_file():
                missing.append(src["path"])
            else:
                if p not in digests:
                    digests[p] = sha(p)
                if not src.get("sha256") or digests[p] != src["sha256"]:
                    changed.append(src["path"])
        return missing, changed

    reviews = sorted((r for r in records.values() if r["kind"] == "review"),
                     key=lambda r: (r.get("created_at", ""), r["id"]))
    # Missing or changed review proof cannot resolve an issue or reinstate a claim.
    reviews = [r for r in reviews if r.get("evidence") and not any(evidence_state(r))]
    resolved = {(i, r["target_id"]) for r in reviews for i in r.get("resolves", [])}
    direct = {}
    for r in reviews:
        direct[r["target_id"]] = r
    issues = [r for r in records.values() if r["kind"] == "issue"]
    states = {}
    visiting = set()

    def state(key):
        if key in states:
            return states[key]
        if key in visiting:
            raise MedicalError(f"Dependency cycle at {key}")
        if key not in records:
            raise MedicalError(f"Missing dependency: {key}")
        visiting.add(key)
        r = records[key]
        verdict = direct.get(key, {}).get("validity", r.get("validity", "unreviewed"))
        blockers = []
        for issue in issues:
            if key in issue["targets"] and (issue["id"], key) not in resolved:
                blockers.append(issue["id"])
                if issue["impact"] == "confirmed":
                    verdict = "invalidated"
                elif verdict != "invalidated":
                    verdict = "under_review"
        missing, changed = evidence_state(r)
        if changed and verdict != "invalidated":
            verdict = "under_review"
        for dep in r.get("depends_on", []):
            ds = state(dep)
            blockers.extend(ds["issue_ids"])
            if ds["validity"] in {"invalidated", "under_review", "superseded"} and verdict != "invalidated":
                verdict = "under_review"
        visiting.remove(key)
        states[key] = {"validity": verdict, "issue_ids": sorted(set(blockers)),
                       "need_fix": bool(blockers or changed), "missing_evidence": missing,
                       "changed_evidence": changed,
                       "availability": "missing_local" if missing else "available"}
        if r["kind"] in {"plan", "attempt"}:
            receipt_path = r.get("source_execution")
            if not receipt_path and r["kind"] == "plan":
                receipt_path = "runs/medical/" + r["id"] + "/execution.json"
            if receipt_path and inside(root, receipt_path).is_file():
                receipt = read(inside(root, receipt_path))
                states[key]["execution"] = {k: receipt[k] for k in ("state", "started_at", "finished_at", "exit_code", "error_type", "frozen_payload_unchanged") if k in receipt}
                states[key]["completeness"] = "partial" if receipt.get("state") != "completed" else "completed"
            elif r["kind"] == "plan":
                states[key]["execution"] = {"state": r.get("planned_state", "pending")}
        return states[key]

    for key in records:
        state(key)
    decisions = sorted((r for r in records.values() if r["kind"] == "decision"),
                       key=lambda r: (r.get("created_at", ""), r["id"]))
    for decision in decisions:
        if decision["target_id"] in states:
            states[decision["target_id"]]["disposition"] = decision["disposition"]
            states[decision["target_id"]]["latest_decision"] = decision["id"]
    return {key: {**r, "current": states[key]} for key, r in records.items()}


def validate(root):
    rows = projection(root)
    errors = []
    for key, row in rows.items():
        for field in ("group_id", "experiment_id", "target_id", "attempt_id", "freeze_id", "plan_id"):
            if row.get(field) and row[field] not in rows:
                errors.append(f"{key}: missing {field} {row[field]}")
        for dep in row.get("targets", []) + row.get("resolves", []):
            if dep not in rows:
                errors.append(f"{key}: missing reference {dep}")
        for link in row.get("links", []):
            path = link["path"].split("#", 1)[0]
            if not inside(root, path).exists() and not link.get("local_only"):
                errors.append(f"{key}: missing portable link {path}")
        if row["kind"] == "issue" and row.get("impact") not in {"suspected", "confirmed"}:
            errors.append(f"{key}: invalid issue impact")
    if errors:
        raise MedicalError("\n".join(errors))
    return {"records": len(rows), "groups": sum(r["kind"] == "group" for r in rows.values()),
            "experiments": sum(r["kind"] == "experiment" for r in rows.values()),
            "missing_local_records": sum(bool(r["current"]["missing_evidence"]) for r in rows.values())}


def destination(root, row, folder):
    group = row["id"] if row["kind"] == "group" else row.get("group_id")
    if not group:
        raise MedicalError("Record must have a group owner")
    g = lookup(root, group)
    return Path(root) / Path(g["record_path"]).parent / folder


def add_idea(root, group, key, title, question, source):
    identifier(key)
    g = lookup(root, group)
    if key in load(root):
        raise MedicalError("Idea already exists; append a decision or update its concise card")
    row = {"schema_version": 1, "kind": "idea", "id": key, "group_id": g["id"],
           "title": title, "question": question, "disposition": "exploring", "created_at": now(),
           "source": source, "depends_on": [], "decisions": [], "reopen_when": "Unspecified"}
    write_new(destination(root, g, "ideas") / (key + ".json"), row)
    return row


def decide(root, idea, disposition, reason, actor, source):
    if disposition not in {"exploring", "selected", "parked", "rejected", "superseded", "promoted"}:
        raise MedicalError("Unknown idea disposition")
    r = lookup(root, idea)
    if r["kind"] != "idea":
        raise MedicalError("Decisions apply to idea records")
    row = {"schema_version": 1, "kind": "decision", "id": uid("decision"),
           "group_id": r["group_id"], "target_id": r["id"], "disposition": disposition,
           "reason": reason, "actor": actor, "source": source, "created_at": now()}
    write_new(destination(root, r, "decisions") / (row["id"] + ".json"), row)
    return row


def issue(root, targets, impact, reason, paths, actor):
    rows = [lookup(root, x) for x in targets]
    if not rows or not reason or not paths or impact not in {"suspected", "confirmed"}:
        raise MedicalError("Issue requires targets, impact, reason and existing evidence")
    row = {"schema_version": 1, "kind": "issue", "id": uid("issue"),
           "group_id": rows[0].get("group_id", rows[0]["id"]), "targets": [r["id"] for r in rows],
           "impact": impact, "reason": reason, "actor": actor, "created_at": now(),
           "evidence": [evidence(root, p) for p in paths]}
    write_new(destination(root, rows[0], "reviews") / (row["id"] + ".json"), row)
    return row


def review(root, target, verdict, reason, paths, actor, resolves=()):
    r = lookup(root, target)
    if verdict not in VALIDITY or not reason or not paths:
        raise MedicalError("Review requires validity, reason and evidence")
    for key in resolves:
        i = lookup(root, key)
        if i["kind"] != "issue" or r["id"] not in i["targets"]:
            raise MedicalError("Resolve an issue with a review of one of its affected targets")
    row = {"schema_version": 1, "kind": "review", "id": uid("review"),
           "group_id": r.get("group_id", r["id"]), "target_id": r["id"], "validity": verdict,
           "reason": reason, "actor": actor, "created_at": now(), "resolves": list(resolves),
           "evidence": [evidence(root, p) for p in paths]}
    write_new(destination(root, r, "reviews") / (row["id"] + ".json"), row)
    return row
