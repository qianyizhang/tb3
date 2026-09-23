"""Local, source-linked workload report over a pinned Codex Usage Tracker index.

This adapter reads tracker facts and Harbor result summaries. It never copies
conversation bodies, tool arguments, or raw model output into its report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path
from typing import Any, cast
from zoneinfo import ZoneInfo

PURPOSES = (
    "curate_data",
    "research",
    "operations",
    "babysit",
    "experiment",
    "unclassified",
)
PURPOSE_RULES = (
    ("babysit", r"\bbabysit|\bmonitor|\bwatch (?:the |an? )?(?:run|experiment|job)"),
    ("experiment", r"\bexperiment|\btrial|\bpilot|\bbenchmark|\bmodel run|\bevaluat"),
    ("curate_data", r"\bcurat|\bdataset|\bground.truth|\bdata source|\bannotation|\bfind .* data"),
    (
        "research",
        r"\bresearch|\binvestigat|\baudit|\bsurvey|\bstudy|\banaly[sz]|\breview|\bevidence|\bcompare|\bsource screen|\bpropos|\bbrainstorm|\bdesign|\bverify|\bfind .*task|\brefinements|\bpast failures|\bchecker difficulty",
    ),
    (
        "operations",
        r"\bsetup|\bset up|\binstall|\bmaintain|\bfix|\brefactor|\bdocs|\bci\b|\bdeploy|\bfrontend|\bquality|\bbuild|\bsite|\bpresentation|\brepository|\bmigrat|\badd |\bimprove|\bpolish|\btidy|\bclean|\bguidance|\billustrat|\bi18n|\barchive|\bcommit|\bworktree|\btrace|\bresume",
    ),
)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _session_header(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as stream:
            first = json.loads(next(stream))
    except (OSError, StopIteration, json.JSONDecodeError):
        return None
    if first.get("type") != "session_meta" or not isinstance(first.get("payload"), dict):
        return None
    return cast(dict[str, Any], first["payload"])


def _tracker_source_id(path: Path) -> str:
    """Version 0.27.0's inode identity; reject a mismatched index at build time."""
    stat = path.stat()
    parts = (
        "session",
        hashlib.sha256(f"device:{stat.st_dev}".encode()).hexdigest(),
        hashlib.sha256(f"file:{stat.st_ino}".encode()).hexdigest(),
    )
    digest = hashlib.blake2b(digest_size=16, person=b"codex-kernel-v1")
    digest.update(b"src")
    for part in parts:
        encoded = part.encode()
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return "src_" + digest.hexdigest()


def _atlas_url(path: Path, base: str) -> str:
    key = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:24]
    return f"{base.rstrip('/')}/?session={key}&line=1"


def _repo_remote(root: Path) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _remote_key(value: str) -> str:
    value = value.removesuffix(".git").rstrip("/")
    if value.startswith("git@"):
        return value[4:].replace(":", "/", 1).lower()
    return re.sub(r"^https?://", "", value).lower()


def _belongs_to_repo(meta: dict[str, Any], root: Path, remote: str) -> bool:
    cwd = meta.get("cwd")
    if not isinstance(cwd, str):
        return False
    candidate = Path(cwd).resolve()
    if candidate == root or candidate.is_relative_to(root):
        return True
    git = meta.get("git")
    source_remote = git.get("repository_url") if isinstance(git, dict) else None
    return bool(
        remote
        and isinstance(source_remote, str)
        and _remote_key(source_remote) == _remote_key(remote)
        and candidate.name == root.name
    )


def _titles(codex_home: Path) -> dict[str, str]:
    index = codex_home / "session_index.jsonl"
    titles: dict[str, str] = {}
    if index.is_file():
        with index.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    title = item.get("thread_name", item.get("title"))
                    if isinstance(title, str):
                        short = _short_title(title)
                        if short:
                            titles[item["id"]] = short
    state = codex_home / "state_5.sqlite"
    if state.is_file():
        try:
            connection = sqlite3.connect(state.as_uri() + "?mode=ro", uri=True)
            try:
                for session_id, name, title in connection.execute(
                    "SELECT id,name,title FROM threads WHERE name IS NOT NULL OR title IS NOT NULL"
                ):
                    if isinstance(session_id, str):
                        candidate = name if isinstance(name, str) and name else title
                        if isinstance(candidate, str):
                            short = _short_title(candidate)
                            if short:
                                titles[session_id] = short
            finally:
                connection.close()
        except sqlite3.Error:
            pass
    return titles


def _short_title(value: str) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) > 500:
        return ""
    return compact[:177] + "..." if len(compact) > 180 else compact


def _purpose(title: str, override: str | None) -> tuple[str, str]:
    if override is not None:
        if override not in PURPOSES:
            raise ValueError(f"unknown purpose override: {override}")
        return override, "manual"
    for purpose, pattern in PURPOSE_RULES:
        if re.search(pattern, title, flags=re.IGNORECASE):
            return purpose, "title rule"
    return "unclassified", "no title rule"


def _date(value: str | None, zone: ZoneInfo) -> str:
    if not value:
        return "unknown"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(zone).date().isoformat()


def _number(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _price(
    rates: dict[str, Any], model: str, usage: dict[str, int], *, coarse: bool = False
) -> tuple[float | None, str]:
    model_rates = rates.get("models", {}).get(model)
    if not isinstance(model_rates, dict):
        return None, "unpriced model"
    input_tokens = usage["input_tokens"]
    cached = usage["cached_input_tokens"]
    writes = usage["cache_write_input_tokens"]
    if cached + writes > input_tokens:
        return None, "inconsistent input buckets"
    long = not coarse and input_tokens > rates["long_context_threshold_input_tokens"]
    prefix = "long_" if long else ""
    cost = (
        (input_tokens - cached - writes) * model_rates[prefix + "input"]
        + cached * model_rates[prefix + "cached_input"]
        + writes * model_rates[prefix + "cache_write"]
        + usage["output_tokens"] * model_rates[prefix + "output"]
    ) / 1_000_000
    return round(cost, 8), "coarse estimate" if coarse else "API Standard estimate"


def _usage_from_offset(stream: Any, offset: int) -> dict[str, Any]:
    stream.seek(offset)
    try:
        record = json.loads(stream.readline())
    except (json.JSONDecodeError, ValueError):
        return {}
    payload = record.get("payload", {})
    if record.get("type") == "token_usage_record":
        usage = payload.get("usage", {})
    elif record.get("type") == "event_msg" and payload.get("type") == "token_count":
        usage = payload.get("info", {}).get("last_token_usage", {})
    else:
        usage = {}
    return usage if isinstance(usage, dict) else {}


def _empty_row(**values: Any) -> dict[str, Any]:
    return {
        **values,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "priced_tokens": 0,
        "cost_usd": 0.0,
        "calls": 0,
        "tools": 0,
        "tool_names": {},
        "models": {},
        "slices": {},
        "days": set(),
        "unpriced_models": [],
    }


def _add_usage(target: dict[str, Any], usage: dict[str, int], cost: float | None) -> None:
    for field in ("input_tokens", "cached_input_tokens", "output_tokens"):
        target[field] += usage[field]
    target["total_tokens"] += usage["input_tokens"] + usage["output_tokens"]
    if cost is not None:
        target["cost_usd"] += cost
        target["priced_tokens"] += usage["input_tokens"] + usage["output_tokens"]


def _add_slice(
    session: dict[str, Any], day: str, model: str, usage: dict[str, int], cost: float | None
) -> None:
    key = f"{day}||{model}"
    item = session["slices"].setdefault(
        key,
        {
            "day": day,
            "model": model,
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "priced_tokens": 0,
            "cost_usd": 0.0,
            "calls": 0,
        },
    )
    _add_usage(item, usage, cost)
    item["calls"] += 1


def _load_codex_sessions(
    root: Path, codex_home: Path, atlas_base: str, overrides: dict[str, str]
) -> dict[str, dict[str, Any]]:
    titles = _titles(codex_home)
    remote = _repo_remote(root)
    found: dict[str, dict[str, Any]] = {}
    for subdir in ("sessions", "archived_sessions"):
        directory = codex_home / subdir
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.jsonl"):
            meta = _session_header(path)
            if meta is None or not _belongs_to_repo(meta, root, remote):
                continue
            session_id = str(meta.get("id", path.stem))
            title = titles.get(session_id) or (
                f"Delegated session {session_id[:8]}"
                if meta.get("parent_thread_id")
                else f"Session {session_id[:8]}"
            )
            purpose, basis = _purpose(title, overrides.get(session_id))
            source_id = _tracker_source_id(path)
            found[source_id] = _empty_row(
                key=source_id,
                source="codex",
                session_id=session_id,
                title=title,
                purpose=purpose,
                purpose_basis=basis,
                path=str(path),
                trace_url=_atlas_url(path, atlas_base),
                started=str(meta.get("timestamp", "")),
                archive_state=subdir,
                parent=str(meta.get("parent_thread_id", "")),
                model="",
                effort="",
                tracker_present=False,
                token_coverage="indexed",
            )
    by_session_id = {row["session_id"]: row for row in found.values() if not row["parent"]}
    for row in found.values():
        by_session_id.setdefault(row["session_id"], row)
    for _ in range(8):
        changed = False
        for row in found.values():
            if row["purpose"] != "unclassified" or row["purpose_basis"] == "manual":
                continue
            parent = by_session_id.get(row["parent"])
            if parent and parent["purpose"] != "unclassified":
                row["purpose"] = parent["purpose"]
                row["purpose_basis"] = f"inherited from {parent['session_id']}"
                changed = True
        if not changed:
            break
    return found


def _tracker_facts(
    database: Path,
    sessions: dict[str, dict[str, Any]],
    rates: dict[str, Any],
    zone: ZoneInfo,
    daily: dict[str, dict[str, Any]],
    models: dict[str, dict[str, Any]],
    tools: dict[str, dict[str, Any]],
) -> dict[str, int]:
    if not database.is_file():
        raise ValueError(f"tracker database missing: {database}; run tracker refresh first")
    connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        required = {"sources", "model_calls", "tool_calls", "threads", "generations"}
        available = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
        if not required <= available:
            raise ValueError(
                "tracker index schema is unsupported; expected codex-usage-tracking 0.27.0"
            )
        indexed = {row[0] for row in connection.execute("SELECT source_id FROM sources")}
        for source_id, session in sessions.items():
            session["tracker_present"] = source_id in indexed
            if source_id not in indexed:
                session["token_coverage"] = "tracker missing"
        selected = set(sessions)
        counts = {
            "canonical_calls": 0,
            "excluded_duplicate_calls": 0,
            "tracker_missing": len(selected - indexed),
        }
        query = (
            "SELECT source_id,event_at,model,effort,input_tokens,cached_input_tokens,"
            "output_tokens,source_offset,duplicate_state FROM model_calls"
        )
        by_source: dict[str, list[sqlite3.Row]] = defaultdict(list)
        for row in connection.execute(query):
            if row["source_id"] in selected:
                by_source[row["source_id"]].append(row)
        for source_id, rows in by_source.items():
            session = sessions[source_id]
            with Path(session["path"]).open("rb") as stream:
                for row in rows:
                    if row["duplicate_state"] != "canonical":
                        counts["excluded_duplicate_calls"] += 1
                        continue
                    counts["canonical_calls"] += 1
                    raw_usage = _usage_from_offset(stream, int(row["source_offset"]))
                    usage = {
                        "input_tokens": int(row["input_tokens"]),
                        "cached_input_tokens": int(row["cached_input_tokens"]),
                        "cache_write_input_tokens": _number(
                            raw_usage.get("cache_write_input_tokens")
                        )
                        or 0,
                        "output_tokens": int(row["output_tokens"]),
                    }
                    model = str(row["model"] or "unknown")
                    effort = str(row["effort"] or "unknown")
                    cost, status = _price(rates, model, usage)
                    if cost is None and model not in session["unpriced_models"]:
                        session["unpriced_models"].append(model)
                    _add_usage(session, usage, cost)
                    session["calls"] += 1
                    session["models"][f"{model} / {effort}"] = (
                        session["models"].get(f"{model} / {effort}", 0) + 1
                    )
                    day = _date(row["event_at"], zone)
                    session["days"].add(day)
                    _add_slice(session, day, f"{model} / {effort}", usage, cost)
                    daily_row = daily.setdefault(day, _empty_row(day=day))
                    _add_usage(daily_row, usage, cost)
                    daily_row["calls"] += 1
                    key = f"{model} / {effort}"
                    model_row = models.setdefault(
                        key, _empty_row(key=key, model=model, effort=effort, status=status)
                    )
                    _add_usage(model_row, usage, cost)
                    model_row["calls"] += 1
                    model_row.setdefault("sessions", set()).add(source_id)
            if session["models"]:
                session["model"] = max(session["models"], key=session["models"].get)
        tool_query = "SELECT source_id,tool_name,tool_category FROM tool_calls"
        for row in connection.execute(tool_query):
            source_id = row["source_id"]
            if source_id not in selected:
                continue
            session = sessions[source_id]
            name = str(row["tool_name"] or "unknown")
            category = str(row["tool_category"] or "unknown")
            session["tools"] += 1
            session["tool_names"][name] = session["tool_names"].get(name, 0) + 1
            item = tools.setdefault(
                name, {"name": name, "category": category, "calls": 0, "sessions": set()}
            )
            item["calls"] += 1
            item["sessions"].add(source_id)
        return counts
    finally:
        connection.close()


def _med_tools(traces: list[Path]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in traces:
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = item.get("payload", {})
                if item.get("type") == "response_item" and payload.get("type") in {
                    "function_call",
                    "custom_tool_call",
                }:
                    counts[str(payload.get("name") or "unknown")] += 1
    return counts


def _med_facts(
    root: Path,
    atlas_base: str,
    overrides: dict[str, str],
    rates: dict[str, Any],
    zone: ZoneInfo,
    daily: dict[str, dict[str, Any]],
    models: dict[str, dict[str, Any]],
    tools: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    local_results = (root / ".local" / "attempts").glob("*/job/task__*/result.json")
    historical_results = (root / "runs").glob("*/*/result.json")
    for path in [*local_results, *historical_results]:
        result = _read_json(path)
        attempt_id = (
            path.parents[2].name
            if (root / ".local" / "attempts") in path.parents
            else f"{path.parents[1].name}:{path.parent.name}"
        )
        config = result.get("config") or {}
        agent = config.get("agent") or {}
        agent_result = result.get("agent_result") or {}
        model_info = (result.get("agent_info") or {}).get("model_info") or {}
        model = str(model_info.get("name") or agent.get("model_name") or "unknown").removeprefix(
            "openai/"
        )
        effort = str((agent.get("kwargs") or {}).get("reasoning_effort") or "unknown")
        purpose, basis = _purpose("", overrides.get(attempt_id, "experiment"))
        trace_paths = sorted((path.parent / "agent" / "sessions").rglob("*.jsonl"))
        tokens = {
            "input_tokens": _number(agent_result.get("n_input_tokens")),
            "cached_input_tokens": _number(agent_result.get("n_cache_tokens")),
            "output_tokens": _number(agent_result.get("n_output_tokens")),
        }
        complete = all(value is not None for value in tokens.values())
        usage = {
            "input_tokens": tokens["input_tokens"] or 0,
            "cached_input_tokens": tokens["cached_input_tokens"] or 0,
            "cache_write_input_tokens": 0,
            "output_tokens": tokens["output_tokens"] or 0,
        }
        cost, status = (
            _price(rates, model, usage, coarse=True) if complete else (None, "missing usage")
        )
        date = _date(result.get("finished_at") or result.get("started_at"), zone)
        row = _empty_row(
            key=attempt_id,
            source="med run",
            session_id=attempt_id,
            title=str(result.get("task_name") or attempt_id),
            purpose=purpose,
            purpose_basis=basis if basis == "manual" and attempt_id in overrides else "med attempt",
            path=str(path),
            trace_url=_atlas_url(trace_paths[0], atlas_base) if trace_paths else "",
            started=str(result.get("started_at") or ""),
            archive_state="local result",
            parent="",
            model=f"{model} / {effort}",
            effort=effort,
            tracker_present=True,
            token_coverage=status,
        )
        row["days"].add(date)
        if complete:
            _add_usage(row, usage, cost)
            row["calls"] = 1
            row["models"][f"{model} / {effort}"] = 1
            _add_slice(row, date, f"{model} / {effort}", usage, cost)
            day_row = daily.setdefault(date, _empty_row(day=date))
            _add_usage(day_row, usage, cost)
            day_row["calls"] += 1
            key = f"{model} / {effort}"
            model_row = models.setdefault(
                key, _empty_row(key=key, model=model, effort=effort, status=status)
            )
            _add_usage(model_row, usage, cost)
            model_row["calls"] += 1
            model_row.setdefault("sessions", set()).add(attempt_id)
        elif model not in row["unpriced_models"]:
            row["unpriced_models"].append(model)
        for name, count in _med_tools(trace_paths).items():
            row["tools"] += count
            row["tool_names"][name] = count
            item = tools.setdefault(
                name, {"name": name, "category": "med run", "calls": 0, "sessions": set()}
            )
            item["calls"] += count
            item["sessions"].add(attempt_id)
        rows.append(row)
    return rows


def build_report(
    root: Path,
    codex_home: Path,
    tracker_database: Path,
    rates_path: Path,
    labels_path: Path | None,
    output: Path,
    timezone_name: str,
    atlas_base: str,
) -> dict[str, Any]:
    root = root.resolve()
    codex_home = codex_home.expanduser().resolve()
    rates = _read_json(rates_path)
    if rates.get("schema") != "tb3-workload-rates-v1":
        raise ValueError("unsupported workload rate card")
    labels = _read_json(labels_path) if labels_path and labels_path.is_file() else {}
    session_overrides = labels.get("sessions", {})
    attempt_overrides = labels.get("attempts", {})
    if not isinstance(session_overrides, dict) or not isinstance(attempt_overrides, dict):
        raise ValueError("purpose labels must contain sessions and attempts objects")
    zone = ZoneInfo(timezone_name)
    sessions = _load_codex_sessions(root, codex_home, atlas_base, session_overrides)
    daily: dict[str, dict[str, Any]] = {}
    models: dict[str, dict[str, Any]] = {}
    tools: dict[str, dict[str, Any]] = {}
    coverage = _tracker_facts(tracker_database, sessions, rates, zone, daily, models, tools)
    med_rows = _med_facts(root, atlas_base, attempt_overrides, rates, zone, daily, models, tools)
    all_rows = list(sessions.values()) + med_rows
    totals = _empty_row()
    for row in all_rows:
        _add_usage(
            totals,
            {
                "input_tokens": row["input_tokens"],
                "cached_input_tokens": row["cached_input_tokens"],
                "cache_write_input_tokens": 0,
                "output_tokens": row["output_tokens"],
            },
            row["cost_usd"] if row["priced_tokens"] else None,
        )
        totals["calls"] += row["calls"]
        totals["tools"] += row["tools"]
    totals["priced_tokens"] = sum(row["priced_tokens"] for row in all_rows)
    for row in models.values():
        row["sessions"] = sorted(row.get("sessions", set()))
    for row in tools.values():
        row["sessions"] = sorted(row["sessions"])
    for row in all_rows:
        row["days"] = sorted(row["days"])
    for row in daily.values():
        row["days"] = []
    for row in models.values():
        row["days"] = []
    totals["days"] = []
    report = {
        "schema": "tb3-workload-report-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "root": str(root),
        "timezone": timezone_name,
        "cost_basis": rates["basis"],
        "price_source": rates["source"],
        "price_checked_at": rates["checked_at"],
        "tracker_database": str(tracker_database),
        "coverage": {
            **coverage,
            "codex_trace_files": len(sessions),
            "med_results": len(med_rows),
            "med_without_trace": sum(not row["trace_url"] for row in med_rows),
            "unclassified_sessions": sum(row["purpose"] == "unclassified" for row in all_rows),
            "classified_token_percent": round(
                100
                * sum(row["total_tokens"] for row in all_rows if row["purpose"] != "unclassified")
                / totals["total_tokens"],
                2,
            )
            if totals["total_tokens"]
            else 100,
            "priced_token_percent": round(100 * totals["priced_tokens"] / totals["total_tokens"], 2)
            if totals["total_tokens"]
            else 100,
        },
        "totals": totals,
        "sessions": sorted(all_rows, key=lambda row: row["total_tokens"], reverse=True),
        "daily": sorted(daily.values(), key=lambda row: row["day"]),
        "models": sorted(models.values(), key=lambda row: row["total_tokens"], reverse=True),
        "tools": sorted(tools.values(), key=lambda row: row["calls"], reverse=True),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    template = (
        resources.files("tb3_medical").joinpath("workload_report.html").read_text(encoding="utf-8")
    )
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    (output / "index.html").write_text(
        template.replace("__WORKLOAD_DATA__", payload), encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a local, trace-linked tb3 workload report")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--tracker-db", type=Path, required=True)
    parser.add_argument("--rates", type=Path)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--atlas-base", default="http://127.0.0.1:8765")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    rates = args.rates or root / "configs" / "workload-rates.json"
    output = args.output or root / ".local" / "workload"
    labels = args.labels or root / ".local" / "workload" / "purpose-labels.json"
    try:
        report = build_report(
            root,
            args.codex_home,
            args.tracker_db,
            rates,
            labels,
            output,
            args.timezone,
            args.atlas_base,
        )
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.exit(2, f"tb3-workload: {exc}\n")
    print(
        json.dumps({"report": str(output / "index.html"), "coverage": report["coverage"]}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
