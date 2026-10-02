"""Selected offline documents and relative, content-addressed served assets."""

import base64
import gzip
import hashlib
import json
import re
from html import escape
from pathlib import Path

from .. import frontend
from ..presentation_contracts import StoryPlan
from ..types import Document
from .assets import check_dependencies
from .families.restoration import compile_view


def json_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")


def write_export(root: Path, plan: StoryPlan, output: Path) -> None:
    from ..explanation_stories import write_projections

    root = root.resolve()
    check_dependencies(root, plan["dependencies"])
    view = compile_view(root, plan)
    entry = "restoration-export" if view else "explainer-export"
    script, css = frontend.assets(root, entry)
    write_projections(plan, output)
    source = next(name for name in plan["dependencies"] if name.endswith(".story.md"))
    (output / "canonical.story.md").write_bytes((root / source).read_bytes())
    common = (root / "presentation/ui.css").read_text()
    script = re.sub(r"</script", r"<\\/script", script, flags=re.I)
    document = (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(plan['title'])}</title>"
        f'<style>{common}\n{css}\nbody{{margin:0}}</style><div id="root"></div>'
        f'<script id="story-plan" type="application/json">{json_script(plan)}</script>'
        f'<script id="explainer-view" type="application/json">{json_script(view)}</script>'
        f"<script>{script}</script></html>"
    )
    (output / "index.html").write_text(document)
    raw = document.encode()
    receipt = json.loads((root / frontend.BUILD_DIR / "manifest.json").read_text())
    (output / "package.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "story": plan["id"],
                "entry": entry,
                "delivery": "selected-offline" if view else "legacy-offline",
                "html_bytes": len(raw),
                "gzip_bytes": len(gzip.compress(raw, mtime=0)),
                "html_sha256": hashlib.sha256(raw).hexdigest(),
                "assets": view["bundle"]["assets"] if view else [],
                "dependencies": view["dependencies"] if view else plan["dependencies"],
                "modules": receipt.get("modules", {}).get(entry, []),
            },
            indent=2,
        )
        + "\n"
    )
    check_dependencies(root, view["dependencies"] if view else plan["dependencies"])
    frontend.assets(root, entry)


def prepare_served(root: Path, output: Path, data: Document) -> tuple[Document, str]:
    """Write only the served JS closure and deduplicated browser images/selected plans."""
    frontend.assets(root, "explorer-served")
    build = root / frontend.BUILD_DIR
    receipt = json.loads((build / "manifest.json").read_text())
    assets = output.parent / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in receipt["servedOutputs"]:
        raw = (build / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != receipt["outputs"][name]:
            raise ValueError(f"Changed served frontend asset: {name}")
        (assets / name).write_bytes(raw)

    def write(raw: bytes, extension: str) -> str:
        name = hashlib.sha256(raw).hexdigest() + extension
        (assets / name).write_bytes(raw)
        return "./assets/" + name

    def image(match: re.Match[str]) -> str:
        extension = {"png": ".png", "jpeg": ".jpg", "webp": ".webp", "gif": ".gif"}[match[1]]
        return write(base64.b64decode(match[2], validate=True), extension)

    def externalize(value: object) -> object:
        if isinstance(value, str):
            return re.sub(r"data:image/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=]+)", image, value)
        if isinstance(value, list):
            return [externalize(item) for item in value]
        if isinstance(value, dict):
            # Exact source downloads and source snapshots retain their original bytes.
            return {
                key: item
                if key in {"local_sources", "source_record", "source_snapshot"}
                else externalize(item)
                for key, item in value.items()
            }
        return value

    result = dict(data)
    plans = result.pop("explanation_stories", {})
    views = result.pop("explainer_views", {})
    result["explainer_resources"] = {
        key: write(json.dumps({"plan": plan, "view": views.get(key)}).encode(), ".json")
        for key, plan in plans.items()
    }
    result["explanation_stories"] = {}
    result["explainer_views"] = {}
    projected = externalize(result)
    assert isinstance(projected, dict)
    return projected, '<script type="module" src="./assets/explorer-served.js"></script>'
