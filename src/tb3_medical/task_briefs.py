"""Small Markdown task briefs and an offline, read-only explorer."""

import base64
import json
import mimetypes
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from . import core as c
from .presentation import markdown

DEFAULT_CATALOG = "discussions/medical-agent-repository-survey/catalog.json"
MARKER = "<!-- tb3-task-explorer: generated -->"
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


def sections(text):
    """Read template headings while leaving ordinary Markdown bodies editable."""
    result, key, major, lines, fenced = {}, "intro", "", [], False
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


def conditions(body):
    rows = []
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        cells = [
            s.strip().replace("\\|", "|") for s in re.split(r"(?<!\\)\|", line.strip().strip("|"))
        ]
        if len(cells) != 3 or cells[0] == "Condition" or re.fullmatch(r":?-+:?", cells[0]):
            continue
        rows.append(dict(zip(("name", "helper", "remaining"), cells)))
    return rows


def local_path(root, source, target):
    path = (source.parent / unquote(urlsplit(target).path)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise c.MedicalError("Brief link escapes repository: " + target)
    return path


def render_text(root, source, body, missing):
    """Embed local images; never fetch remote media or expose raw runtime folders."""
    embedded = {}

    def image(match):
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

    def link(target):
        if target in embedded:
            return embedded[target]
        return target if urlsplit(target).scheme in {"http", "https", "codex"} else None

    return markdown(body, link)


def load(root, catalog=DEFAULT_CATALOG):
    root = Path(root).resolve()
    path = c.inside(root, str(catalog))
    data = c.read(path)
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
        missing = []
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
        out.append(row)
    inventory = (
        c.read(c.inside(root, data["inventory"])) if data.get("inventory") else {"repositories": []}
    )
    by_id = {entry["id"]: entry for entry in out}
    for repo in inventory.get("repositories", []):
        item_ids = [r["id"] for r in repo["items"]]
        if len(item_ids) != len(set(item_ids)):
            raise c.MedicalError("Duplicate inventory ID: " + repo["id"])
        for item in repo["items"]:
            if data.get("require_brief_coverage") and not item.get("brief_id"):
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
    return {**data, "entries": out, "inventory": inventory}


def check(root, catalog=DEFAULT_CATALOG):
    data = load(root, catalog)
    return {
        "briefs": len(data["entries"]),
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
        "missing_media": sorted({p for x in data["entries"] for p in x["missing_media"]}),
    }


def build(root, output, catalog=DEFAULT_CATALOG):
    root = Path(root).resolve()
    output = Path(output).resolve()
    data = load(root, catalog)
    base = root / "presentation/task-explorer"
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
        document.replace("__STYLE__", (base / "style.css").read_text())
        .replace(
            "__APP__",
            "\n".join((base / name).read_text() for name in ("illustrations.js", "app.js")),
        )
        .replace("__DATA__", payload)
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(MARKER + "\n" + document)
    temporary.replace(output)
    return {"output": str(output), "briefs": len(data["entries"]), "standalone": True}


def new(
    root, key, title, repository, family, destination, catalog=DEFAULT_CATALOG, repository_id=None
):
    root = Path(root).resolve()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
        raise c.MedicalError("Use a lowercase hyphenated brief ID")
    path = c.inside(root, str(catalog))
    target = c.inside(root, str(destination))
    data = c.read(path) if path.exists() else {"title": "Task Explorer", "entries": []}
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
