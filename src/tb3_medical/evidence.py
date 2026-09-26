"""Model-free evidence inventories for agent-authored medical explanations."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from . import core as c
from . import storage
from .errors import MedicalError
from .types import Document, Pathish, Records

SCHEMA_VERSION = 1
INDEX_MARKER = "<!-- tb3-evidence-index: generated -->"
HIGH_SIGNAL_TERMS = {
    "metric",
    "report",
    "result",
    "reward",
    "score",
    "trace",
    "trajectory",
    "verifier",
}
INTERPRETATION_BOUNDARIES = [
    "Decide whether differing task, instruction, scorer, reference or input digests are comparable.",
    "Interpret metric meaning and clinical or anatomical significance.",
    "Attribute failures across data, reference, instruction, tool, reasoning and infrastructure.",
    "Question ground truth without relabeling or rewriting frozen scores.",
    "Choose source-derived views and distinguish them from conceptual drawings.",
]


def _role(path: str) -> str:
    path = path.lower()
    if path.endswith("instruction.md") or "prompt" in path:
        return "instruction"
    if "reference" in path or "/solution/" in "/" + path:
        return "reference"
    if "/tests/" in "/" + path or "score" in path or "verifier" in path:
        return "evaluator"
    if "/data/" in "/" + path or path.startswith("data/"):
        return "input"
    return "environment"


def _record_ref(root: Pathish, row: Document) -> dict[str, str]:
    path = storage.inside(root, row["record_path"])
    return {
        "id": row["id"],
        "kind": row["kind"],
        "path": row["record_path"],
        "sha256": storage.sha(path),
    }


def _experiment_ids(rows: Records, targets: Sequence[str]) -> list[str]:
    return sorted(
        {experiment_id for key in targets for experiment_id in c.experiment_ids(rows[key], rows)}
    )


def _related(row: Document, scope_ids: set[str], experiment_ids: set[str]) -> bool:
    if row["id"] in scope_ids:
        return True
    if row["kind"] == "finding":
        return False
    if row.get("experiment_id") in experiment_ids:
        return True
    if set(row.get("experiment_ids", [])) & experiment_ids:
        return True
    return False


def _artifact_pointer(root: Pathish, source: Document, entry: Document) -> Document | None:
    relative = entry.get("path")
    if not relative:
        return None
    try:
        path = storage.inside(root, relative)
    except MedicalError:
        return {
            "source_record": source["id"],
            "label": entry.get("label", "Evidence"),
            "path": relative,
            "expected_sha256": entry.get("sha256"),
            "availability": "outside_workspace",
        }
    present = path.is_file()
    actual = storage.sha(path) if present else None
    expected = entry.get("sha256")
    return {
        "source_record": source["id"],
        "label": entry.get("label", "Evidence"),
        "path": relative,
        "expected_sha256": expected,
        "availability": "present" if present else "missing_local",
        "digest_matches": None if not present or not expected else actual == expected,
    }


def _selected_artifacts(root: Pathish, related: Sequence[Document]) -> Document:
    counts: Counter[str] = Counter()
    pointers: list[Document] = []
    seen: set[str] = set()
    for row in related:
        entries = row.get("evidence", [])
        counts[row["kind"]] += len(entries)
        for entry in entries:
            path = entry.get("path", "")
            text = (entry.get("label", "") + " " + entry.get("path", "")).lower()
            high_signal = row["kind"] in {"finding", "review", "issue"} or any(
                term in text for term in HIGH_SIGNAL_TERMS
            )
            if row["kind"] in {"attempt", "evaluation"}:
                if row.get("agent") in {"oracle", "nop"} or Path(path).suffix in {".py", ".pyc"}:
                    high_signal = False
            if not high_signal or entry.get("path") in seen:
                continue
            seen.add(entry.get("path"))
            pointer = _artifact_pointer(root, row, entry)
            if pointer:
                pointers.append(pointer)
    return {
        "declared_by_record_kind": dict(sorted(counts.items())),
        "selected_pointers": sorted(pointers, key=lambda p: (p["path"], p["source_record"])),
        "selection_note": (
            "All finding/review/issue evidence plus high-signal model result, score, report and "
            "trace pointers are listed. Control and full submitted-artifact declarations remain "
            "available through pinned record references."
        ),
    }


def _contracts(rows: Records, experiment_id: str) -> list[Document]:
    freezes = sorted(
        (
            row
            for row in rows.values()
            if row["kind"] == "freeze" and row["experiment_id"] == experiment_id
        ),
        key=lambda row: (row.get("created_at", ""), row["id"]),
    )
    contracts = []
    for freeze in freezes:
        roles: dict[str, list[dict[str, str]]] = {}
        for path, digest in sorted(freeze["files"].items()):
            roles.setdefault(_role(path), []).append({"path": path, "sha256": digest})
        contracts.append(
            {
                "freeze_id": freeze["id"],
                "case": freeze.get("case"),
                "created_at": freeze.get("created_at"),
                "task_digest": freeze["task_digest"],
                "snapshot_path": freeze.get("snapshot_path"),
                "roles": roles,
            }
        )
    return contracts


def _observations(rows: Records, executions: Records, experiment_id: str) -> list[Document]:
    attempts = {
        row["id"]: row
        for row in rows.values()
        if row["kind"] == "attempt" and row["experiment_id"] == experiment_id
    }
    latest = sorted(
        (row for row in executions.values() if row["experiment_id"] == experiment_id),
        key=lambda item: (item.get("collected_at", ""), item["id"]),
    )
    result = []
    for row in latest:
        attempt = attempts.get(row.get("attempt_id"), {})
        result.append(
            {
                "evaluation_id": row["id"],
                "attempt_id": row.get("attempt_id"),
                "evaluation_kind": row.get("evaluation_kind", "legacy"),
                "agent": row.get("agent", attempt.get("agent")),
                "model": row.get("model", attempt.get("model")),
                "reasoning_effort": row.get("reasoning_effort", attempt.get("reasoning_effort")),
                "execution_state": row.get("execution_state"),
                "outcome": row.get("outcome"),
                "reward": row.get("reward"),
                "partial": row.get("partial", False),
                "source_classification": row.get("source_classification"),
                "task_digest": row.get("task_digest"),
                "collected_at": row.get("collected_at"),
                "timing": row.get("timing"),
                "usage": row.get("usage"),
            }
        )
    return result


def collect(root: Pathish, targets: Sequence[str]) -> Document:
    """Collect exact identities and evidence pointers without interpreting them."""
    root = Path(root).resolve()
    rows = c.load(root)
    missing = [key for key in targets if key not in rows]
    if missing:
        raise MedicalError("Unknown evidence target: " + ", ".join(missing))
    target_rows = {key: rows[key] for key in targets}
    experiment_ids = set(_experiment_ids(rows, targets))
    scope_ids = (
        set(targets)
        | experiment_ids
        | {row["group_id"] for row in target_rows.values() if row.get("group_id")}
    )
    related = [row for row in rows.values() if _related(row, scope_ids, experiment_ids)]
    projection = c.projection(root)
    executions = c.execution_observations(rows)
    experiments = []
    task_digests: set[str] = set()
    for experiment_id in sorted(experiment_ids):
        experiment = rows[experiment_id]
        contracts = _contracts(rows, experiment_id)
        observations = _observations(rows, executions, experiment_id)
        task_digests.update(
            item["task_digest"] for item in [*contracts, *observations] if item.get("task_digest")
        )
        experiments.append(
            {
                "id": experiment_id,
                "group_id": experiment["group_id"],
                "title": experiment.get("title"),
                "method": experiment.get("method"),
                "current": projection[experiment_id]["current"],
                "contracts": contracts,
                "observations": observations,
            }
        )
    findings = [
        {
            "id": row["id"],
            "analysis_kind": row.get("analysis_kind", "unclassified_legacy"),
            "claim": row.get("claim"),
            "limitations": row.get("limitations", []),
            "review_flags": projection[row["id"]]["current"].get("review_flags", []),
        }
        for row in related
        if row["kind"] == "finding"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "evidence_manifest",
        "targets": list(dict.fromkeys(targets)),
        "record_refs": [
            _record_ref(root, row)
            for row in sorted(related, key=lambda item: (item["kind"], item["id"]))
        ],
        "findings": findings,
        "experiments": experiments,
        "comparability": {
            "status": "agent_decision_required",
            "observed_task_digests": sorted(task_digests),
            "same_observed_task_digest": len(task_digests) == 1 if task_digests else None,
            "note": (
                "Digest equality supports byte-level task identity only. The explaining agent must "
                "still assess endpoints, conditions and scientific comparability."
            ),
        },
        "artifacts": _selected_artifacts(root, related),
        "interpretation_boundaries": INTERPRETATION_BOUNDARIES,
    }


def validate_manifest(data: Document) -> Document:
    if data.get("schema_version") != SCHEMA_VERSION or data.get("kind") != "evidence_manifest":
        raise MedicalError("Unsupported evidence manifest")
    for field in ("targets", "record_refs", "experiments", "artifacts"):
        if field not in data:
            raise MedicalError("Evidence manifest missing " + field)
    paths = [row["path"] for row in data["record_refs"]]
    if len(paths) != len(set(paths)):
        raise MedicalError("Evidence manifest has duplicate record paths")
    return data


def write_manifest(path: Pathish, data: Document) -> None:
    validate_manifest(data)
    storage.write_new(path, data)


def summary(data: Document) -> Document:
    return {
        "targets": len(data["targets"]),
        "records": len(data["record_refs"]),
        "experiments": len(data["experiments"]),
        "selected_artifacts": len(data["artifacts"]["selected_pointers"]),
        "agent_interpretation_required": True,
    }


def check(root: Pathish, manifest: Pathish) -> Document:
    root = Path(root).resolve()
    data = validate_manifest(storage.read(manifest))
    changed, missing = [], []
    for ref in data["record_refs"]:
        path = storage.inside(root, ref["path"])
        if not path.is_file():
            missing.append(ref["path"])
        elif storage.sha(path) != ref["sha256"]:
            changed.append(ref["path"])
    if missing or changed:
        parts = []
        if missing:
            parts.append("missing records: " + ", ".join(missing))
        if changed:
            parts.append("changed records: " + ", ".join(changed))
        raise MedicalError("Evidence manifest is stale; " + "; ".join(parts))
    artifact_states: Counter[str] = Counter()
    artifact_drift: list[str] = []
    for pointer in data["artifacts"]["selected_pointers"]:
        if pointer["availability"] == "outside_workspace":
            artifact_states["outside_workspace"] += 1
            continue
        path = storage.inside(root, pointer["path"])
        if not path.is_file():
            state = "missing_local"
        elif pointer.get("expected_sha256") and storage.sha(path) != pointer["expected_sha256"]:
            state = "digest_mismatch"
        elif pointer["availability"] == "missing_local":
            state = "newly_available"
        else:
            state = "present"
        artifact_states[state] += 1
        if state == "digest_mismatch" or (
            pointer["availability"] == "present" and state != "present"
        ):
            artifact_drift.append(pointer["path"])
    if artifact_drift:
        raise MedicalError("Evidence manifest artifact drift: " + ", ".join(sorted(artifact_drift)))
    return {**summary(data), "record_hashes": "match", "artifact_states": dict(artifact_states)}


def _cell(value: object) -> str:
    return str(value if value is not None else "—").replace("|", "\\|")


def _markdown_row(*values: object) -> str:
    return "| " + " | ".join(_cell(value) for value in values) + " |"


def build(root: Pathish, manifest: Pathish, output: Pathish) -> Document:
    data = validate_manifest(storage.read(manifest))
    check(root, manifest)
    lines = [
        INDEX_MARKER,
        "# Evidence inventory",
        "",
        "> Machine-built identity and availability index. It contains no clinical or causal interpretation.",
        "",
        "## Targets",
        "",
        *[f"- `{target}`" for target in data["targets"]],
        "",
        "## Conditions and observations",
        "",
        "| Experiment | Evaluation | Agent / model | State | Outcome | Task digest |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for experiment in data["experiments"]:
        if not experiment["observations"]:
            lines.append(f"| `{experiment['id']}` | — | — | — | — | — |")
        for observation in experiment["observations"]:
            identity = " / ".join(
                str(value)
                for value in (observation.get("agent"), observation.get("model"))
                if value
            )
            lines.append(
                _markdown_row(
                    f"`{experiment['id']}`",
                    f"`{observation['evaluation_id']}`",
                    identity or "—",
                    observation.get("execution_state"),
                    observation.get("outcome"),
                    observation.get("task_digest"),
                )
            )
    lines += [
        "",
        "## Contract identities",
        "",
        "| Experiment | Freeze | Case | Task digest | Input | Reference | Evaluator |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for experiment in data["experiments"]:
        for contract in experiment["contracts"]:
            roles = contract["roles"]
            lines.append(
                _markdown_row(
                    f"`{experiment['id']}`",
                    f"`{contract['freeze_id']}`",
                    contract.get("case"),
                    contract["task_digest"],
                    len(roles.get("input", [])),
                    len(roles.get("reference", [])),
                    len(roles.get("evaluator", [])),
                )
            )
    lines += [
        "",
        "## Selected evidence pointers",
        "",
        "| Source record | Evidence | Availability |",
        "| --- | --- | --- |",
    ]
    for pointer in data["artifacts"]["selected_pointers"]:
        lines.append(
            _markdown_row(
                f"`{pointer['source_record']}`",
                f"`{pointer['path']}`",
                pointer["availability"],
            )
        )
    lines += ["", "## Interpretation still required", ""]
    lines += [f"- {item}" for item in data["interpretation_boundaries"]]
    output = Path(output)
    if output.exists() and INDEX_MARKER not in output.read_text()[:100]:
        raise MedicalError("Refusing to overwrite an unowned file: " + str(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text("\n".join(lines) + "\n")
    temporary.replace(output)
    return {"output": str(output), **summary(data)}


def new(
    root: Pathish, group: str, key: str, title: str, analysis_kind: str, targets: Sequence[str]
) -> Document:
    root = Path(root).resolve()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
        raise MedicalError("Use a lowercase hyphenated analysis ID")
    if analysis_kind not in c.ANALYSIS_KINDS:
        raise MedicalError("Unknown analysis kind: " + analysis_kind)
    owner = c.lookup(root, group)
    if owner["kind"] != "group":
        raise MedicalError("Analysis owner must be a group")
    manifest = collect(root, targets)
    experiment_ids = sorted(e["id"] for e in manifest["experiments"])
    base = c.destination(root, owner, "findings")
    report_path = base / (key + ".md")
    record_path = base / (key + ".json")
    evidence_path = base / "evidence" / (key + ".json")
    for path in (report_path, record_path, evidence_path):
        if path.exists():
            raise MedicalError("Refusing to overwrite existing analysis file: " + str(path))
    write_manifest(evidence_path, manifest)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("x") as report:
        report.write(
            f"# {title}\n\n"
            "> Draft agent-authored interpretation. Frozen scores and source records remain authoritative.\n\n"
            "## At a glance\n\n"
            "| Question | Evidence | Interpretation | Confidence |\n"
            "| --- | --- | --- | --- |\n"
            "| What happened? | Add the exact measure. | Explain what it means. | Draft |\n\n"
            "## Task, data and reference\n\n"
            "Explain the actual condition, solver-visible inputs, expected output and reference limits.\n\n"
            "## Measured result\n\n"
            "Report frozen measures before interpretation.\n\n"
            "## Result and reference inspection\n\n"
            "Use source-derived views with exact legends, coordinates and concise captions.\n\n"
            "## Trace and intermediate artifacts\n\n"
            "Connect consequential actions to retained evidence; omit routine trace chronology.\n\n"
            "## Failure attribution and alternatives\n\n"
            "Separate observation from hypothesis across data, GT, instruction, tool, reasoning and infrastructure.\n\n"
            "## Comparison and limits\n\n"
            "Declare comparability, confounders, unresolved questions and what this evidence cannot establish.\n\n"
            "## Provenance\n\n"
            f"- Evidence manifest: `{evidence_path.relative_to(root)}`\n"
        )
    record = {
        "schema_version": 2,
        "kind": "finding",
        "analysis_kind": analysis_kind,
        "id": key,
        "group_id": group,
        "title": title,
        "claim": "Draft analysis; no conclusion has been accepted.",
        "experiment_ids": experiment_ids,
        "evidence": [
            {
                "path": evidence_path.relative_to(root).as_posix(),
                "sha256": storage.sha(evidence_path),
            }
        ],
        "limitations": ["Interpretation and visual inspection are not complete."],
        "links": [{"label": "Analysis report", "path": report_path.relative_to(root).as_posix()}],
    }
    storage.write_new(record_path, record)
    return {
        "record": record_path.relative_to(root).as_posix(),
        "report": report_path.relative_to(root).as_posix(),
        "evidence": evidence_path.relative_to(root).as_posix(),
        "analysis_kind": analysis_kind,
        "experiments": experiment_ids,
    }
