"""Small Markdown task briefs and an offline, read-only explorer."""

import base64
import hashlib
import json
import mimetypes
import re
from collections.abc import Sequence
from fnmatch import fnmatch
from pathlib import Path
from urllib.parse import unquote, urlsplit

from . import core as c
from . import dataset_previews, datasets, frontend, task_catalog
from .presentation import markdown
from .presentation_contracts import validate_payload
from .types import Document, Pathish, Records

DEFAULT_CATALOG = task_catalog.DEFAULT_CATALOG
MARKER = "<!-- tb3-task-explorer: generated -->"
SOURCE_MAX_BYTES = 64 * 1024
SOURCE_TOTAL_BYTES = 256 * 1024
FIELDS = {
    "value": "Value",
    "raw": "Given/Original data",
    "helpers": "Given/Supplied helpers",
    "tools": "Given/Callable tools",
    "reference": "Given/Reference-only material",
    "spec": "Task specification",
    "output": "Expected output",
    "score": "Evaluation",
    "challenge": "Difficulty",
    "families": "Coverage",
    "gap": "Gaps",
    "case_note": "Cases",
}


def sections(text: str) -> dict[str, str]:
    """Read template headings while leaving ordinary Markdown bodies editable."""
    result: dict[str, str] = {}
    lines: list[str] = []
    key, major, fenced = "intro", "", False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"^(#{1,3}) (.+)$", line)
        if heading:
            result[key] = "\n".join(lines).strip()
            lines = []
            level, label = len(heading[1]), heading[2]
            if level == 1:
                result["title"] = label
                key = "goal"
            elif level == 2:
                key = major = label
            else:
                key = major + "/" + label
        else:
            lines.append(line)
    result[key] = "\n".join(lines).strip()
    return result


def conditions(body: str) -> list[dict[str, str]]:
    rows = []
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        cells = [
            s.strip().replace("\\|", "|") for s in re.split(r"(?<!\\)\|", line.strip().strip("|"))
        ]
        if len(cells) != 3 or cells[0] == "Condition" or re.fullmatch(r":?-+:?", cells[0]):
            continue
        rows.append(dict(zip(("name", "helper", "remaining"), cells, strict=True)))
    return rows


def local_path(root: Path, source: Path, target: str) -> Path:
    path = (source.parent / unquote(urlsplit(target).path)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise c.MedicalError("Brief link escapes repository: " + target)
    return path


def render_text(root: Path, source: Path, body: str, missing: list[str]) -> str:
    """Embed local images; never fetch remote media or expose raw runtime folders."""
    embedded: dict[str, str] = {}

    def image(match: re.Match[str]) -> str:
        alt, target = match.groups()
        if urlsplit(target).scheme:
            missing.append(target)
            return f"{alt} (external image not embedded; follow the source link)"
        path = local_path(root, source, target)
        if not path.is_file():
            missing.append(str(path.relative_to(root)))
            return f"{alt} (local image unavailable)"
        mime = mimetypes.guess_type(path.name)[0]
        if mime not in {"image/png", "image/jpeg", "image/webp", "image/svg+xml"}:
            raise c.MedicalError("Unsupported brief image: " + str(path))
        token = "brief-image-" + str(len(embedded))
        embedded[token] = "data:" + mime + ";base64," + base64.b64encode(path.read_bytes()).decode()
        return f"![{alt}]({token})"

    body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image, body)

    def link(target: str) -> str | None:
        if target in embedded:
            return embedded[target]
        return target if urlsplit(target).scheme in {"http", "https", "codex"} else None

    return markdown(body, link)


def source_bundle(root: Pathish, entries: Sequence[Document]) -> Records:
    """Package only directly cited small text files, never their dependencies."""
    root = Path(root).resolve()
    policy_path = root / "configs/artifact-policy.json"
    policy = c.read(policy_path) if policy_path.is_file() else {}
    local_roots = {"runs", "jobs", ".local", ".cache", "node_modules", "archive/legacy"}
    local_roots.update(policy.get("local_roots", []))
    blocked = [".venv*", ".env", ".env.*", *policy.get("blocked_components", [])]
    sources: Records = {}
    total = 0
    for entry in entries:
        for _, target in entry["sources"]:
            if urlsplit(target).scheme or target in sources:
                continue
            path = c.inside(root, target)
            reason = ""
            if any(path.is_relative_to(root / p) for p in local_roots) or any(
                fnmatch(part, pattern)
                for part in path.relative_to(root).parts
                for pattern in blocked
            ):
                reason = "Local runtime material is not included."
            elif not path.is_file():
                reason = "Directories are not included."
            elif path.suffix.lower() not in {".md", ".json", ".txt"}:
                reason = "Only Markdown, JSON and plain-text sources are included."
            elif path.stat().st_size > SOURCE_MAX_BYTES:
                reason = "Source exceeds the 64 KiB per-file limit."
            elif total + path.stat().st_size > SOURCE_TOTAL_BYTES:
                raise c.MedicalError(
                    "Task Explorer sources exceed the 256 KiB combined limit at "
                    + target
                    + "; reduce the explicitly cited source scope."
                )
            if reason:
                sources[target] = {"unavailable": reason}
                continue
            raw = path.read_bytes()
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                sources[target] = {"unavailable": "Source is not UTF-8 text."}
                continue
            total += len(raw)
            sources[target] = {
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "content": content,
                "base64": base64.b64encode(raw).decode(),
            }
    return sources


def load(root: Pathish, catalog: Pathish = DEFAULT_CATALOG) -> Document:
    root = Path(root).resolve()
    data = task_catalog.collection(root, catalog)
    experiment_count = task_catalog.classify(root, data)
    out = []
    ids = set()
    for meta in data["entries"]:
        if meta["id"] in ids:
            raise c.MedicalError("Duplicate task brief ID: " + meta["id"])
        ids.add(meta["id"])
        source = c.inside(root, meta["brief"])
        content = sections(source.read_text())
        for field in (
            "title",
            "goal",
            "Given/Original data",
            "Task specification",
            "Expected output",
            "Evaluation",
            "Sources",
        ):
            if not content.get(field):
                raise c.MedicalError(f"{meta['brief']}: missing {field}")
        row = dict(meta, title=content["title"], goal=content["goal"])
        row.update({field: content.get(key, "Not yet specified.") for field, key in FIELDS.items()})
        row["stages"] = [
            line[2:]
            for line in content.get("Visual explanation/Workflow", "").splitlines()
            if line.startswith("- ")
        ]
        if len(row["stages"]) != 3:
            row["stages"] = ["Supplied inputs", "Requested action", "Expected deliverable"]
        row["variants"] = conditions(content.get("Conditions", "")) or [
            {"name": "Specified condition", "helper": row["helpers"], "remaining": row["spec"]}
        ]
        row["sources"] = []
        for label, target in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", content["Sources"]):
            if not urlsplit(target).scheme:
                p = local_path(root, source, target)
                if not p.exists():
                    raise c.MedicalError(f"{meta['brief']}: missing source {target}")
                target = p.relative_to(root).as_posix()
            row["sources"].append([label, target])
        for study in row["studies"]:
            if study["protocol"] not in [target for _, target in row["sources"]]:
                row["sources"].append([study["title"], study["protocol"]])
        missing: list[str] = []
        row["html"] = {
            key: render_text(root, source, row[key], missing) for key in ("goal", *FIELDS)
        }
        row["visuals"] = {
            key: render_text(
                root,
                source,
                content.get("Visual explanation/" + heading, "No source-derived view curated yet."),
                missing,
            )
            for key, heading in (
                ("input", "Input"),
                ("helpers", "Supplied helpers"),
                ("answer", "Reference or output"),
            )
        }
        row["missing_media"] = sorted(set(missing))
        illustration = row.get("illustration")
        if illustration is not None and (
            not isinstance(illustration, dict)
            or not all(
                isinstance(illustration.get(key), str) and illustration[key].strip()
                for key in ("kind", "input", "output", "caption")
            )
        ):
            raise c.MedicalError(f"{row['id']}: incomplete overview illustration")
        if data.get("require_overview_visuals") and not (
            illustration or "<img " in row["visuals"]["input"]
        ):
            raise c.MedicalError(f"{row['id']}: missing overview visual")
        out.append(row)
    inventory = data["inventory"]
    by_id = {entry["id"]: entry for entry in out}
    for repo in inventory.get("repositories", []):
        item_ids = [r["id"] for r in repo["items"]]
        if len(item_ids) != len(set(item_ids)):
            raise c.MedicalError("Duplicate inventory ID: " + repo["id"])
        for item in repo["items"]:
            if repo.get("require_brief_coverage") and not item.get("brief_id"):
                raise c.MedicalError("Inventory entry lacks a task brief: " + item["id"])
            if item.get("brief_id") and item["brief_id"] not in ids:
                raise c.MedicalError("Unknown inventory brief: " + item["brief_id"])
            if item.get("brief_id"):
                entry = by_id[item["brief_id"]]
                if entry.get("repository_id", entry["id"]) != repo["id"]:
                    raise c.MedicalError(
                        "Inventory brief belongs to another repository: " + item["id"]
                    )
                index = item.get("condition_index", 0)
                if type(index) is not int or not 0 <= index < len(entry["variants"]):
                    raise c.MedicalError("Invalid inventory condition: " + item["id"])
    dataset_data = datasets.load(
        root, out, require_coverage=data.get("require_dataset_coverage", False)
    )
    dataset_data["previews"] = dataset_previews.load(
        root,
        {row["id"] for row in dataset_data["records"]},
        required=data.get("require_dataset_previews", False),
    )
    return validate_payload(
        {
            **data,
            "schema_version": 1,
            "entries": out,
            "inventory": inventory,
            "local_sources": source_bundle(root, out),
            "datasets": dataset_data,
            "experiment_count": experiment_count,
        },
        "explorer",
    )


def check(root: Pathish, catalog: Pathish = DEFAULT_CATALOG) -> Document:
    data = load(root, catalog)
    return {
        "briefs": len(data["entries"]),
        "experiments": data["experiment_count"],
        "supporting_research": sum(e.get("role", "task") != "task" for e in data["entries"]),
        "conditions": sum(len(x["variants"]) for x in data["entries"]),
        "catalogue_entries": sum(
            len(x["items"]) for x in data["inventory"].get("repositories", [])
        ),
        "linked_entries": sum(
            bool(i.get("brief_id"))
            for r in data["inventory"].get("repositories", [])
            for i in r["items"]
        ),
        "native_visual_briefs": sum(
            any("<img " in body for body in e["visuals"].values()) for e in data["entries"]
        ),
        "illustrated_overviews": sum(
            bool(e.get("illustration")) or "<img " in e["visuals"]["input"] for e in data["entries"]
        ),
        "missing_media": sorted({p for x in data["entries"] for p in x["missing_media"]}),
        "dataset_snapshots": {
            "documented": len(data["datasets"]["previews"]),
            "paired": sum(
                row["status"] == "paired" for row in data["datasets"]["previews"].values()
            ),
            "missing_media": sorted(
                panel["path"]
                for row in data["datasets"]["previews"].values()
                for panel in row["panels"]
                if not panel["available"]
            ),
        },
    }


def build(
    root: Pathish,
    output: Pathish,
    catalog: Pathish = DEFAULT_CATALOG,
    *,
    presentation_context: Document | None = None,
) -> Document:
    root = Path(root).resolve()
    output = Path(output).resolve()
    data = load(root, catalog)
    if presentation_context:
        data["presentation_context"] = presentation_context
    base = root / "presentation/task-explorer"
    app_js, app_css = frontend.assets(root, "explorer")
    if output.exists() and MARKER not in output.read_text()[:200]:
        raise c.MedicalError("Refusing to overwrite an unowned file: " + str(output))
    document = (base / "index.html").read_text()
    payload = (
        json.dumps(data, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    document = (
        document.replace(
            "__STYLE__",
            "\n".join(
                path.read_text()
                for path in (
                    base.parent / "ui.css",
                    base / "style.css",
                    base / "datasets.css",
                    base / "scene-explanation.css",
                )
            )
            + "\n"
            + app_css,
        )
        .replace("__APP__", re.sub(r"</script", r"<\\/script", app_js, flags=re.I))
        .replace("__DATA__", payload)
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(MARKER + "\n" + document)
    temporary.replace(output)
    return {
        "output": str(output),
        "briefs": len(data["entries"]),
        "standalone": True,
        "integrated": bool(presentation_context),
        "embedded_sources": sum("sha256" in s for s in data["local_sources"].values()),
    }


def new(
    root: Pathish,
    key: str,
    title: str,
    repository: str,
    family: str,
    destination: Pathish,
    catalog: Pathish = DEFAULT_CATALOG,
    repository_id: str | None = None,
) -> Document:
    root = Path(root).resolve()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
        raise c.MedicalError("Use a lowercase hyphenated brief ID")
    path = c.inside(root, str(catalog))
    target = c.inside(root, str(destination))
    data: Document = c.read(path) if path.exists() else {"title": "Task Explorer", "entries": []}
    if data.get("collections"):
        raise c.MedicalError("Choose a group-owned leaf collection with --catalog for a new brief")
    if data.get("taxonomy"):
        taxonomy = c.read(c.inside(root, data["taxonomy"]))
        if family not in taxonomy["categories"]:
            raise c.MedicalError("Use a category ID from the collection taxonomy for --family")
    if target.exists() or any(
        e["id"] == key or e["brief"] == str(destination) for e in data["entries"]
    ):
        raise c.MedicalError("Brief ID or destination already exists")
    template = (root / "presentation/task-explorer/brief-template.md").read_text()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template.replace("{{title}}", title.replace("\n", " ")))
    entry = {
        "id": key,
        "repo": repository,
        "category": family,
        "tag": "Proposed task",
        "brief": target.relative_to(root).as_posix(),
        "proposed": True,
        "role": "task",
        "agent_work": "direct",
    }
    if repository_id:
        entry["repository_id"] = repository_id
    data["entries"].append(entry)
    c.atomic_write(path, data)
    return {
        "brief": str(target),
        "catalog": str(path),
        "proposed": True,
        "experiment_created": False,
    }
