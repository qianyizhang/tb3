"""Verify explicitly built frontend assets before assembling portable publications."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .errors import MedicalError

BUILD_DIR = Path(".local/frontend")
BUILD_INPUTS = (
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "scripts/build_frontend.mjs",
    "src/tb3_medical/presentation_contracts.py",
    "src/tb3_medical/explanation_stories.py",
    "presentation/assets/teaching-prefabs.json",
    "presentation/task-explorer/assets/Apache-2.0.txt",
)


def input_hashes(root: Path) -> dict[str, str]:
    paths = [root / name for name in BUILD_INPUTS]
    paths.extend(
        path
        for folder in ("presentation/frontend", "presentation/assets/teaching")
        for path in (root / folder).rglob("*")
        if path.is_file() and path.suffix in {".ts", ".tsx", ".css", ".js"}
    )
    paths.extend(
        path for path in (root / "presentation/task-explorer/anatomy").glob("*") if path.is_file()
    )
    paths.extend(
        path
        for path in (root / "presentation/assets/teaching-fixtures").rglob("*")
        if path.is_file()
    )
    paths.extend(root.glob("groups/*/presentation/stories/*.story.md"))
    paths.extend(root.glob("presentation/external-tasks/stories/*.story.md"))
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths)
    }


def assets(root: Path, entry: str) -> tuple[str, str]:
    """Return JS/CSS only when source inputs and compiled output match the receipt."""
    if entry not in {"explorer", "overview", "explainer-export"}:
        raise MedicalError("Unknown frontend entry: " + entry)
    folder = root / BUILD_DIR
    try:
        manifest = json.loads((folder / "manifest.json").read_text())
        if manifest.get("schema_version") != 1 or manifest.get("inputs") != input_hashes(root):
            raise ValueError("source fingerprint differs")
        outputs = manifest["outputs"]
        js_name, css_name = entry + ".js", entry + ".css"
        if js_name not in outputs:
            raise ValueError("entry bundle is absent")
        result = []
        for name in (js_name, css_name):
            if name not in outputs:
                result.append("")
                continue
            raw = (folder / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != outputs[name]:
                raise ValueError("compiled asset fingerprint differs")
            result.append(raw.decode("utf-8"))
        return result[0], result[1]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise MedicalError(
            "Frontend assets are missing or stale; run npm ci, then npm run frontend:build "
            "from the workbench root before building a presentation."
        ) from exc
