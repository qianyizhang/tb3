"""Portable read-only index, source-linked stories and exact figure extraction."""

import base64
import functools
import html
import json
import os
import re
import shutil
from collections.abc import Callable
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from . import core as c
from . import frontend
from .presentation_contracts import validate_payload
from .types import Document, Pathish


def pointer(value: Any, path: str) -> Any:
    for token in path.lstrip("/").split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def assets(root: Pathish, write: bool = False) -> Document:
    count = 0
    for a in c.read(Path(root) / "presentation/assets.json")["assets"]:
        target = c.inside(root, a["path"])
        source = c.inside(root, a["source_path"])
        if not source.is_file() or c.sha(source) != a["source_sha256"]:
            raise c.MedicalError("Changed/missing figure source: " + a["source_path"])
        encoding = a["encoding"]
        if encoding in {"json-base64", "javascript-json-base64"}:
            raw = source.read_text()
            if encoding.startswith("javascript"):
                raw = raw[raw.index("{") :].strip().removesuffix(";")
            data = pointer(json.loads(raw), a["pointer"])
            blob = base64.b64decode(data.split(",", 1)[-1], validate=True)
        elif encoding == "mermaid":
            blocks = re.findall(r"```mermaid\n(.*?)\n```", source.read_text(), re.S)
            blob = (blocks[a["block"] - 1] + "\n").encode()
        else:
            blob = source.read_bytes()
        import hashlib

        if hashlib.sha256(blob).hexdigest() != a["sha256"]:
            raise c.MedicalError("Derived figure digest mismatch: " + a["path"])
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
        elif not target.is_file() or target.read_bytes() != blob:
            raise c.MedicalError("Missing/stale figure: " + a["path"])
        count += 1
    return {"verified_assets": count, "written": write}


def check_links(root: Pathish, source: Path) -> None:
    """Check maintained prose links; retained runtime locators may be unavailable."""
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", source.read_text()):
        parsed = urlsplit(target)
        if parsed.scheme or not parsed.path:
            continue
        path = (source.parent / unquote(parsed.path)).resolve()
        if not path.is_relative_to(Path(root).resolve()):
            raise c.MedicalError(f"Prose link escapes repository: {source}: {target}")
        relative = path.relative_to(Path(root).resolve()).as_posix()
        if relative.startswith(
            (
                "runs/",
                "jobs/",
                ".cache/",
                ".local/",
                "presentation/tours/data/",
                "presentation/tours/web/",
                "presentation/tours/exports/",
            )
        ):
            continue
        if not path.exists():
            raise c.MedicalError(f"Missing portable prose link: {source}: {relative}")


def check(root: Pathish) -> Document:
    stats = c.validate(root)
    rows = c.load(root)
    measurements = 0
    for group in [r for r in rows.values() if r["kind"] == "group"]:
        directory = Path(group["record_path"]).parent / "presentation"
        story = c.inside(root, str(directory / "story.md"))
        if not story.is_file():
            raise c.MedicalError("Missing group story: " + group["id"])
        check_links(root, story)
        card_path = Path(root) / directory / "card.json"
        if card_path.is_file():
            card = c.read(card_path)
            sources = {}
            for path, digest in card["source_hashes"].items():
                source = c.inside(root, path)
                if c.sha(source) != digest:
                    raise c.MedicalError("Source digest mismatch: " + path)
                # Narrative checks compare the small authored measurements, not raw runs.
                sources[path] = c.read(source)
            for measurement in card["measurements"]:
                if (
                    pointer(sources[measurement["source"]], measurement["pointer"])
                    != measurement["value"]
                ):
                    raise c.MedicalError("Source measurement mismatch: " + measurement["label"])
                measurements += 1
    protocols = list(Path(root).glob("groups/*/experiments/*/protocol.md"))
    for protocol in protocols:
        check_links(root, protocol)
    return {**stats, "source_measurements": measurements, "protocols_checked": len(protocols)}


def markdown(text: str, link: Callable[[str], str | None]) -> str:
    """Small escaped renderer for authored research prose; no raw HTML execution."""

    def inline(value: str) -> str:
        value = html.escape(value)

        def image(m: re.Match[str]) -> str:
            url = link(html.unescape(m[2]))
            return (
                f'<img loading="lazy" alt="{m[1]}" src="{html.escape(url, quote=True)}">'
                if url
                else f'<span class="unavailable">{m[1]} (local artifact unavailable)</span>'
            )

        value = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image, value)

        def anchor(m: re.Match[str]) -> str:
            url = link(html.unescape(m[2]))
            return (
                f'<a href="{html.escape(url, quote=True)}">{m[1]}</a>'
                if url
                else f'<span class="unavailable">{m[1]} (local artifact)</span>'
            )

        value = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", anchor, value)
        value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
        value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
        return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)

    lines = text.splitlines()
    out = []
    i = 0
    heading_ids = set()
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            language = line[3:]
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            out.append(
                "<details><summary>Workflow diagram source</summary>"
                if language == "mermaid"
                else ""
            )
            out.append("<pre><code>" + html.escape("\n".join(block)) + "</code></pre>")
            if language == "mermaid":
                out.append("</details>")
        elif re.match(r"^#{1,6} ", line):
            level = len(line) - len(line.lstrip("#"))
            title = line[level + 1 :]
            slug = re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-") or "section"
            identifier, suffix = slug, 0
            while identifier in heading_ids:
                suffix += 1
                identifier = f"{slug}-{suffix}"
            heading_ids.add(identifier)
            out.append(f'<h{level} id="{identifier}">' + inline(title) + f"</h{level}>")
        elif line.startswith("|"):
            table = []
            while i < len(lines) and lines[i].startswith("|"):
                parts = [x.strip() for x in lines[i].strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", x) for x in parts):
                    table.append(parts)
                i += 1
            out.append('<div class="table"><table>')
            for n, row in enumerate(table):
                tag = "th" if n == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(x)}</{tag}>" for x in row) + "</tr>")
            out.append("</table></div>")
            continue
        elif line.startswith(("- ", "* ")):
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith(("- ", "* ")):
                out.append("<li>" + inline(lines[i][2:]) + "</li>")
                i += 1
            out.append("</ul>")
            continue
        elif line.strip():
            paragraph = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not lines[i].startswith(("#", "```", "|", "- "))
            ):
                paragraph.append(lines[i])
                i += 1
            out.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            continue
        i += 1
    return "\n".join(out)


def present(root: Pathish, output: Pathish, local_media: bool = False) -> Document:
    root, output = Path(root).resolve(), Path(output).resolve()
    app_js, app_css = frontend.assets(root, "overview")
    if output == root or root.is_relative_to(output):
        raise c.MedicalError("Output cannot contain the source checkout")
    marker = output / ".tb3-medical-site"
    if output.exists() and not marker.exists() and any(output.iterdir()):
        raise c.MedicalError("Refusing a nonempty unowned output directory")
    if marker.exists():
        # This is an explicitly marked disposable build. Rebuild the whole inventory
        # so a portable build cannot retain media from a prior local build.
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    marker.write_text("Generated read-only medical presentation\n")
    rows = c.projection(root)
    groups = [r for r in rows.values() if r["kind"] == "group"]
    story_pages = {
        str(Path(group["record_path"]).parent / "presentation/story.md"): "stories/"
        + group["id"]
        + ".html"
        for group in groups
    }
    for name in ("index.html", "style.css", "ui.css"):
        shutil.copy2(root / "presentation" / name, output / name)
    (output / "overview.js").write_text(app_js)
    (output / "style.css").write_text((output / "style.css").read_text() + "\n" + app_css)
    copied = set()

    def copy_link(relative: str, page_output: Path) -> str | None:
        parsed = urlsplit(relative)
        if parsed.scheme:
            return relative if parsed.scheme in {"https", "http", "codex"} else None
        if not parsed.path:
            return relative
        src = (root / unquote(parsed.path)).resolve()
        if not src.is_relative_to(root) or not src.is_file():
            return None
        rel = src.relative_to(root).as_posix()
        if rel in story_pages:
            return (
                os.path.relpath(output / story_pages[rel], page_output.parent)
                + ("?" + parsed.query if parsed.query else "")
                + ("#" + parsed.fragment if parsed.fragment else "")
            )
        local = rel.startswith(
            (
                "runs/",
                "jobs/",
                ".cache/",
                ".local/",
                "presentation/tours/data/",
                "presentation/tours/web/",
                "presentation/tours/exports/",
            )
        )
        # Only explicitly authored links are exposed. Never serve the checkout or raw runtime config.
        if local:
            return None
        target = output / rel
        if rel not in copied:
            copied.add(rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        return (
            os.path.relpath(target, page_output.parent)
            + ("?" + parsed.query if parsed.query else "")
            + ("#" + parsed.fragment if parsed.fragment else "")
        )

    for group in groups:
        source = root / Path(group["record_path"]).parent / "presentation/story.md"
        page = output / "stories" / (group["id"] + ".html")
        page.parent.mkdir(exist_ok=True)

        def story_link(
            target: str, *, page_output: Path = page, story_source: Path = source
        ) -> str | None:
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                return copy_link(target, page_output)
            absolute = (story_source.parent / unquote(parsed.path)).resolve()
            if not absolute.is_relative_to(root):
                return None
            rel = absolute.relative_to(root).as_posix()
            if rel.startswith("presentation/tours/"):
                if not absolute.is_file():
                    return None
                if local_media:
                    return "../" + rel + ("?" + parsed.query if parsed.query else "")
                if absolute.suffix != ".md":
                    return None
            return copy_link(rel + ("#" + parsed.fragment if parsed.fragment else ""), page_output)

        body = markdown(source.read_text(), story_link)
        flags = group["current"]["review_flags"]
        validity = (
            "; ".join(
                c.VOCABULARY["axes"]["assessment"]["values"][f["assessment"]]["label"]
                + ": "
                + f["experiment_id"]
                + (" — " + f["reason"] if f.get("reason") else "")
                for f in flags
            )
            if flags
            else "No unresolved review flags recorded for the cited experiments"
        )
        notice = f"<aside>Current evidence status: <strong>{html.escape(validity)}</strong>. See the index for review dependencies and evidence availability.</aside>"
        explorer_navigation = (
            '<a href="../task-explorer/index.html">Tasks</a>'
            '<a href="../task-explorer/index.html#datasets">Datasets</a>'
            if (root / "presentation/task-explorer/catalog.json").is_file()
            else ""
        )
        title = html.escape(group["title"])
        page.write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>'
            + title
            + ' · TB3 Medical</title><link rel="stylesheet" href="../ui.css">'
            '<link rel="stylesheet" href="../style.css"></head><body>'
            '<a class="skip-link" href="#story-content">Skip to story</a>'
            '<header class="site-header story-header">'
            '<a class="site-brand" href="../index.html">TB3 / MEDICAL'
            '<span class="site-brand-caption">Research workbench</span></a>'
            '<nav class="site-nav" aria-label="Primary navigation">'
            '<a href="../index.html" aria-current="page">Overview</a>'
            + explorer_navigation
            + '</nav></header><main class="story" id="story-content" tabindex="-1">'
            '<p class="story-breadcrumb"><a href="../index.html#research-areas">Research areas</a>'
            '<span aria-hidden="true">/</span>'
            + title
            + "</p>"
            + notice
            + body
            + '<footer class="story-footer"><a href="../index.html#research-areas">'
            '← All research areas</a><a href="../index.html?group='
            + html.escape(group["id"], quote=True)
            + '#research-record">Browse evidence for this area →</a></footer></main></body></html>'
        )
        group["story_url"] = "stories/" + group["id"] + ".html"
    for row in rows.values():
        row["portable_links"] = [
            {"label": x["label"], "url": copy_link(x["path"], output / "index.html")}
            for x in row.get("links", [])
        ]
    if local_media:
        tours = root / "presentation/tours"
        shutil.copytree(
            tours,
            output / "presentation/tours",
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                "__pycache__", "validation.json", "compression-report.json", "*.zip"
            ),
        )
    # Imported locally because the brief renderer reuses this module's Markdown renderer.
    from . import task_briefs

    explorer = None
    if (root / task_briefs.DEFAULT_CATALOG).is_file():
        explorer = task_briefs.build(
            root,
            output / "task-explorer/index.html",
            presentation_context={
                "home_url": "../index.html",
                "home_label": "Medical workbench",
                "story_urls": {path: "../" + url for path, url in story_pages.items()},
            },
        )
    c.atomic_write(
        output / "records.json",
        validate_payload(
            {
                "schema_version": 1,
                "records": list(rows.values()),
                "local_media": local_media,
                "vocabulary": c.VOCABULARY,
                "task_explorer_url": "task-explorer/index.html" if explorer else None,
            },
            "overview",
        ),
    )
    return {
        "output": str(output),
        "groups": len(groups),
        "records": len(rows),
        "local_media": local_media,
        "task_explorer": explorer,
    }


def serve(output: Pathish, port: int) -> None:
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(output))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
