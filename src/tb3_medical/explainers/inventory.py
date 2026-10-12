"""Read-only local availability audit for the core explainer enhancement pass.

Presence is not trace interpretation, scientific acceptance, or condition coverage.
Only attempt-owned result pointers identify executions; teaching assets do not.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .. import storage
from ..errors import MedicalError
from ..explainer_queue import LEDGER, SCOPE, _index, _load
from ..types import Document, Pathish

HASH_LIMIT = 1024 * 1024


def artifact(root: Path, value: object, *, expected: object = None) -> Document:
    """Check an explicit workspace path; never follow paths outside the workspace."""
    root = root.resolve()
    if not isinstance(value, str) or not value:
        return {"path": None, "status": "not-declared"}
    try:
        path = storage.inside(root, value)
    except MedicalError:
        return {"path": value, "status": "outside-workspace"}
    row: Document = {"path": path.relative_to(root).as_posix()}
    if not path.exists():
        return {**row, "status": "not-retained"}
    row["status"] = "present"
    row["type"] = "directory" if path.is_dir() else "file"
    if path.is_file():
        row["bytes"] = path.stat().st_size
        if path.stat().st_size <= HASH_LIMIT:
            row["sha256"] = storage.sha(path)
            if isinstance(expected, str):
                row["declared_sha256"] = expected
                row["hash_matches"] = row["sha256"] == expected
        else:
            row["hash_status"] = "skipped-size-limit"
            if isinstance(expected, str):
                row["declared_sha256"] = expected
    return row


def _read_present(root: Path, row: Document) -> Document:
    if row["status"] == "present" and row.get("type") == "file":
        return storage.read_object(root / row["path"])
    return {}


def _story(root: Path, story_id: object) -> Document:
    if not isinstance(story_id, str) or not story_id:
        return artifact(root, None)
    # Mirror the canonical resolver's explicit locations without compiling assets.
    if any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in story_id):
        raise MedicalError(f"Invalid story ID: {story_id}")
    paths = sorted(root.glob(f"groups/*/presentation/stories/{story_id}.story.md"))
    paths += sorted(root.glob(f"presentation/external-tasks/stories/{story_id}.story.md"))
    if len(paths) > 1:
        raise MedicalError(f"Ambiguous story ID: {story_id}")
    return (
        {**artifact(root, paths[0].relative_to(root).as_posix()), "story_id": story_id}
        if paths
        else {"path": None, "story_id": story_id, "status": "not-retained"}
    )


def _attempt(root: Path, path: Path) -> Document:
    record = storage.read_object(path)
    result = artifact(root, record.get("source_result"))
    raw = _read_present(root, result)
    config = raw.get("config", {})
    agent = config.get("agent", {}) if isinstance(config, dict) else {}
    name = agent.get("name") if isinstance(agent, dict) else None
    model = agent.get("model_name") if isinstance(agent, dict) else None
    task = config.get("task", {}) if isinstance(config, dict) else {}
    task_path = task.get("path") if isinstance(task, dict) else None
    task_artifact = artifact(root, task_path)
    trajectories: list[Document] = []
    outputs: list[Document] = []
    verifier: Document = artifact(root, None)
    if result["status"] == "present":
        trial = (root / result["path"]).parent
        trajectory = trial / "agent/trajectory.json"
        # These are Harbor's retained trace layouts, not guessed neighbouring runs.
        trajectories.append(artifact(root, trajectory.relative_to(root).as_posix()))
        sessions = trial / "agent/sessions"
        if sessions.is_dir():
            trajectories.extend(
                artifact(root, item.relative_to(root).as_posix())
                for item in sorted(sessions.rglob("*.jsonl"))
            )
        submitted = trial / "artifacts/app"
        if submitted.is_dir():
            outputs.extend(
                artifact(root, item.relative_to(root).as_posix())
                for item in sorted(submitted.rglob("*"))
                if item.is_file()
            )
        verifier = artifact(root, (trial / "verifier/test-stdout.txt").relative_to(root).as_posix())
    model_attempt = bool(model) and name not in {"oracle", "nop", "none"}
    trace_present = model_attempt and any(row["status"] == "present" for row in trajectories)
    return {
        "attempt_id": record.get("id"),
        "record": artifact(root, path.relative_to(root).as_posix()),
        "source_result": result,
        "agent_name": name,
        "model_name": model,
        "model_attempt": model_attempt,
        "trace_artifacts_present": trace_present,
        "trace_interpretation": "unreviewed" if trace_present else "unavailable",
        "task": task_artifact,
        "task_roles": {
            role: artifact(root, str(Path(task_path) / relative) if task_path else None)
            for role, relative in {
                "instruction": "instruction.md",
                "solver_inputs": "environment",
                "evaluator_reference": "tests",
                "oracle": "solution",
            }.items()
        },
        "trajectories": trajectories,
        "submitted_outputs": outputs,
        "verifier": verifier,
        "exception_present": raw.get("exception_info") is not None if raw else None,
    }


def build_inventory(root: Pathish) -> Document:
    """Join core membership, live review history, leaf bindings and retained runs."""
    root = Path(root).resolve()
    scope, _, scope_rows, ledger_rows = _load(root)
    ledger = _index(ledger_rows, "ledger", "entry_id")
    groups = _index(scope["groups"], "scope group", "group_id")
    experiments: dict[str, tuple[Path, Document]] = {}
    for path in sorted(root.glob("groups/*/experiments/*/experiment.toml")):
        record = storage.read_object(path)
        identity = record["id"]
        if identity in experiments:
            raise MedicalError(f"Duplicate experiment: {identity}")
        experiments[identity] = (path, record)
    catalogs: dict[str, Document] = {}
    rows: list[Document] = []
    for selected in scope_rows:
        if not selected.get("automatic_completion"):
            continue
        entry_id = selected["entry_id"]
        old = ledger[entry_id]
        catalog = artifact(root, old.get("catalogue"))
        catalog_key = str(old.get("catalogue"))
        if catalog_key not in catalogs:
            catalogs[catalog_key] = _read_present(root, catalog)
        matches = [
            item for item in catalogs[catalog_key].get("entries", []) if item["id"] == entry_id
        ]
        if len(matches) > 1:
            raise MedicalError(f"Duplicate leaf entry: {entry_id}")
        entry = matches[0] if matches else {}
        review = old.get("source_review") or {}
        audit = artifact(
            root, review.get("receipt"), expected=review.get("receipt_sha256", review.get("sha256"))
        )
        audit_record = _read_present(root, audit)
        pins = audit_record.get("source_pins", {})
        sources = (
            [artifact(root, source, expected=expected) for source, expected in sorted(pins.items())]
            if isinstance(pins, dict)
            else []
        )
        studies: list[Document] = []
        for link in entry.get("experiments", []):
            experiment_id = link["id"]
            found = experiments.get(experiment_id)
            if found is None:
                studies.append(
                    {
                        "experiment_id": experiment_id,
                        "scope": link.get("scope"),
                        "status": "not-retained",
                        "attempts": [],
                    }
                )
                continue
            path, record = found
            studies.append(
                {
                    "experiment_id": experiment_id,
                    "scope": link.get("scope"),
                    "status": "present",
                    "record": artifact(root, path.relative_to(root).as_posix()),
                    "protocol": artifact(
                        root, (path.parent / record["protocol"]).relative_to(root).as_posix()
                    )
                    if record.get("protocol")
                    else artifact(root, None),
                    "evidence": [
                        artifact(root, item.get("path"), expected=item.get("sha256"))
                        for item in record.get("evidence", [])
                    ],
                    "attempts": [
                        _attempt(root, attempt)
                        for attempt in sorted((path.parent / "attempts").glob("*.json"))
                    ],
                }
            )
        attempts = [attempt for study in studies for attempt in study["attempts"]]
        model_attempts = [attempt for attempt in attempts if attempt["model_attempt"]]
        traces = [attempt for attempt in model_attempts if attempt["trace_artifacts_present"]]
        illustration = entry.get("illustration") or {}
        group = groups[selected["group_id"]]
        rows.append(
            {
                "entry_id": entry_id,
                "title": old.get("title"),
                "group_id": selected["group_id"],
                "priority": group.get("priority"),
                "owner_group": entry.get("owner_group"),
                "previous_review_status": old.get("reviewed_disposition"),
                "illustration_basis": old.get("illustration_basis"),
                "asset_readiness_claim": old.get("source_asset_readiness"),
                "catalogue": catalog,
                "leaf_binding_status": "present" if entry else "not-retained",
                "brief": artifact(root, entry.get("brief", old.get("brief"))),
                "story": _story(root, illustration.get("story_id")),
                "source_audit": audit,
                "audit_source_pins": sources,
                "experiments": studies,
                "coverage": {
                    "linked_experiments": len(studies),
                    "attempt_records": len(attempts),
                    "model_attempts_identified": len(model_attempts),
                    "model_attempts_with_trace_artifacts": len(traces),
                    "model_attempts_with_submitted_outputs": sum(
                        bool(item["submitted_outputs"]) for item in model_attempts
                    ),
                },
                "enhancement_status": "not-assessed",
                "candidate_basis": "retained-model-trace-artifacts"
                if traces
                else "retained-model-result"
                if model_attempts
                else "source-resolution-or-task-mechanism",
            }
        )
    candidates = sorted(
        rows,
        key=lambda row: (
            {"P0": 0, "P1": 1, "P2": 2}.get(row["priority"], 3),
            {
                "retained-model-trace-artifacts": 0,
                "retained-model-result": 1,
                "source-resolution-or-task-mechanism": 2,
            }[row["candidate_basis"]],
            row["entry_id"],
        ),
    )
    return {
        "schema": 1,
        "kind": "core-explainer-evidence-inventory",
        "authority": {"scope": artifact(root, SCOPE), "ledger": artifact(root, LEDGER)},
        "limits": [
            "Filesystem presence is an availability observation, not semantic trace validation or scientific acceptance.",
            "Only explicit leaf experiment links and their attempt source_result pointers are joined; unlinked historical runs remain outside this audit.",
            "Input/reference directory presence does not establish individual file completeness or solver visibility; source_audit.source_pins are checked without inferring roles. Other audit formats are retained by path, not recursively interpreted.",
            "No trial, source download, medical runtime, renderer or historical authoring module is executed.",
            f"Files larger than {HASH_LIMIT} bytes are not hashed; retained declared hashes are not newly verified.",
            "Entry counts do not establish full condition coverage or native-context enhancement completion.",
        ],
        "summary": {
            "core_entries": len(rows),
            "stories_present": sum(row["story"]["status"] == "present" for row in rows),
            "source_audits_present": sum(
                row["source_audit"]["status"] == "present" for row in rows
            ),
            "entries_with_linked_experiments": sum(bool(row["experiments"]) for row in rows),
            "entries_with_model_results": sum(
                row["coverage"]["model_attempts_identified"] > 0 for row in rows
            ),
            "entries_with_model_trace_artifacts": sum(
                row["coverage"]["model_attempts_with_trace_artifacts"] > 0 for row in rows
            ),
            "candidate_basis": dict(Counter(row["candidate_basis"] for row in rows)),
        },
        "candidates": [
            {
                "entry_id": row["entry_id"],
                "priority": row["priority"],
                "basis": row["candidate_basis"],
                "coverage": row["coverage"],
            }
            for row in candidates
        ],
        "entries": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_inventory(args.root)
    output = storage.inside(args.root.resolve(), args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
