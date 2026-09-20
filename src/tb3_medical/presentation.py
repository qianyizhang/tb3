"""Portable read-only index, source-linked stories and exact figure extraction."""
import base64
import functools
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

from . import core as c


def pointer(value, path):
    for token in path.lstrip("/").split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def assets(root, write=False):
    count = 0
    for a in c.read(Path(root) / "presentation/assets.json")["assets"]:
        target = c.inside(root, a["path"]); source = c.inside(root, a["source_path"])
        if a["encoding"] == "retained-copy" and not source.exists(): source = target
        if not source.is_file() or c.sha(source) != a["source_sha256"]:
            raise c.MedicalError("Changed/missing figure source: " + a["source_path"])
        encoding = a["encoding"]
        if encoding in {"json-base64", "javascript-json-base64"}:
            raw = source.read_text()
            if encoding.startswith("javascript"): raw = raw[raw.index("{"):].strip().removesuffix(";")
            data = pointer(json.loads(raw), a["pointer"])
            blob = base64.b64decode(data.split(",", 1)[-1], validate=True)
        elif encoding == "mermaid":
            blocks = re.findall(r"```mermaid\n(.*?)\n```", source.read_text(), re.S)
            blob = (blocks[a["block"] - 1] + "\n").encode()
        else: blob = source.read_bytes()
        import hashlib
        if hashlib.sha256(blob).hexdigest() != a["sha256"]:
            raise c.MedicalError("Derived figure digest mismatch: " + a["path"])
        if write:
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(blob)
        elif not target.is_file() or target.read_bytes() != blob:
            raise c.MedicalError("Missing/stale figure: " + a["path"])
        count += 1
    return {"verified_assets": count, "written": write}


def check(root):
    stats = c.validate(root); stats.update(assets(root))
    rows = c.load(root); measurements = 0
    for group in [r for r in rows.values() if r["kind"] == "group"]:
        directory = Path(group["record_path"]).parent / "presentation"
        story = c.inside(root, str(directory / "story.md"))
        if not story.is_file(): raise c.MedicalError("Missing group story: " + group["id"])
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", story.read_text()):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path: continue
            p = (story.parent / unquote(parsed.path)).resolve()
            if not p.is_relative_to(Path(root).resolve()): raise c.MedicalError("Story link escapes repository")
            relative = p.relative_to(Path(root).resolve()).as_posix()
            if relative.startswith(("runs/", "jobs/", ".cache/", "presentation/tours/data/", "presentation/tours/web/", "presentation/tours/exports/")): continue
            if not p.exists(): raise c.MedicalError(f"Missing portable story link: {relative}")
        card_path = Path(root) / directory / "card.json"
        if card_path.is_file():
            card = c.read(card_path); sources = {}
            for path, digest in card["source_hashes"].items():
                source = c.inside(root, path)
                if c.sha(source) != digest: raise c.MedicalError("Changed measurement source: " + path)
                sources[path] = c.read(source)
            for measurement in card["measurements"]:
                if pointer(sources[measurement["source"]], measurement["pointer"]) != measurement["value"]:
                    raise c.MedicalError("Source measurement mismatch: " + measurement["label"])
                measurements += 1
    return {**stats, "source_measurements": measurements}


def markdown(text, link):
    """Small escaped renderer for authored research prose; no raw HTML execution."""
    def inline(value):
        value = html.escape(value)
        def image(m):
            url = link(html.unescape(m[2]))
            return f'<img loading="lazy" alt="{m[1]}" src="{html.escape(url, quote=True)}">' if url else f'<span class="unavailable">{m[1]} (local artifact unavailable)</span>'
        value = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image, value)
        def anchor(m):
            url = link(html.unescape(m[2]))
            return f'<a href="{html.escape(url, quote=True)}">{m[1]}</a>' if url else f'<span class="unavailable">{m[1]} (local artifact)</span>'
        value = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", anchor, value)
        value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
        value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
        return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    lines = text.splitlines(); out = []; i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            language = line[3:]; block = []; i += 1
            while i < len(lines) and not lines[i].startswith("```"): block.append(lines[i]); i += 1
            out.append('<details><summary>Workflow diagram source</summary>' if language == "mermaid" else "")
            out.append("<pre><code>" + html.escape("\n".join(block)) + "</code></pre>")
            if language == "mermaid": out.append("</details>")
        elif re.match(r"^#{1,6} ", line):
            level = len(line) - len(line.lstrip("#")); out.append(f'<h{level}>' + inline(line[level+1:]) + f'</h{level}>')
        elif line.startswith("|"):
            table = []
            while i < len(lines) and lines[i].startswith("|"):
                parts = [x.strip() for x in lines[i].strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", x) for x in parts): table.append(parts)
                i += 1
            out.append('<div class="table"><table>')
            for n, row in enumerate(table):
                tag = "th" if n == 0 else "td"; out.append("<tr>" + "".join(f'<{tag}>{inline(x)}</{tag}>' for x in row) + "</tr>")
            out.append("</table></div>"); continue
        elif line.startswith(("- ", "* ")):
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith(("- ", "* ")):
                out.append("<li>" + inline(lines[i][2:]) + "</li>"); i += 1
            out.append("</ul>"); continue
        elif line.strip():
            paragraph = [line]; i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", "|", "- ")):
                paragraph.append(lines[i]); i += 1
            out.append("<p>" + inline(" ".join(paragraph)) + "</p>"); continue
        i += 1
    return "\n".join(out)


def present(root, output, local_media=False):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or root.is_relative_to(output): raise c.MedicalError("Output cannot contain the source checkout")
    marker = output / ".tb3-medical-site"
    if output.exists() and not marker.exists() and any(output.iterdir()): raise c.MedicalError("Refusing a nonempty unowned output directory")
    output.mkdir(parents=True, exist_ok=True); marker.write_text("Generated read-only medical presentation\n")
    rows = c.projection(root); groups = [r for r in rows.values() if r["kind"] == "group"]
    for name in ("index.html", "app.js", "style.css"):
        shutil.copy2(root / "presentation" / name, output / name)
    copied = set()
    def copy_link(relative, page_output):
        parsed = urlsplit(relative)
        if parsed.scheme: return relative if parsed.scheme in {"https", "http", "codex"} else None
        if not parsed.path: return relative
        src = (root / unquote(parsed.path)).resolve()
        if not src.is_relative_to(root) or not src.is_file(): return None
        rel = src.relative_to(root).as_posix()
        local = rel.startswith(("runs/", "jobs/", ".cache/", "presentation/tours/data/", "presentation/tours/web/", "presentation/tours/exports/"))
        # Only explicitly authored links are exposed. Never serve the checkout or raw runtime config.
        if local: return None
        target = output / rel
        if rel not in copied:
            copied.add(rel); target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, target)
        return os.path.relpath(target, page_output.parent) + ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
    for group in groups:
        source = root / Path(group["record_path"]).parent / "presentation/story.md"
        page = output / "stories" / (group["id"] + ".html"); page.parent.mkdir(exist_ok=True)
        def story_link(target):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path: return copy_link(target, page)
            absolute = (source.parent / unquote(parsed.path)).resolve()
            if not absolute.is_relative_to(root): return None
            rel = absolute.relative_to(root).as_posix()
            if rel.startswith("presentation/tours/"):
                if not absolute.is_file(): return None
                if local_media:
                    return "../" + rel + ("?" + parsed.query if parsed.query else "")
                if absolute.suffix != ".md": return None
            return copy_link(rel + ("#" + parsed.fragment if parsed.fragment else ""), page)
        body = markdown(source.read_text(), story_link)
        validity = group["current"]["validity"]
        notice = f'<aside>Current evidence status: <strong>{html.escape(validity)}</strong>. See the index for review dependencies and evidence availability.</aside>'
        page.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(group["title"])+'</title><link rel="stylesheet" href="../style.css"><main class="story"><a href="../index.html">← Medical workbench</a>'+notice+body+'</main></html>')
        group["story_url"] = "stories/" + group["id"] + ".html"
    for row in rows.values():
        row["portable_links"] = [{"label": x["label"], "url": copy_link(x["path"], output / "index.html")} for x in row.get("links", [])]
    if local_media:
        tours = root / "presentation/tours"
        shutil.copytree(tours, output / "presentation/tours", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "validation.json", "compression-report.json", "*.zip"))
    c.atomic_write(output / "records.json", {"records": list(rows.values()), "local_media": local_media})
    return {"output": str(output), "groups": len(groups), "records": len(rows), "local_media": local_media}


def serve(output, port):
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(output))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        try: server.serve_forever()
        except KeyboardInterrupt: pass
