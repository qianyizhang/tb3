"""Prepare and verify selected story exports without assigning visual acceptance."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Sequence
from html import escape
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool

from . import explanation_stories as stories
from . import frontend, storage, story_authoring, task_catalog
from .errors import MedicalError
from .types import Document

EXPORT_SOURCES = (
    "scripts/export_med_tours.mts",
    "presentation/tooling/media/cli.mts",
    "presentation/tooling/media/stories.mts",
    "presentation/tooling/media/capture.mts",
    "presentation/tooling/media/encoder.mts",
    "presentation/tooling/media/tours.mts",
    "presentation/tooling/media/tour-plan.mts",
    "presentation/tooling/browser.mts",
    "presentation/tooling/python.mts",
    "src/tb3_medical/cli.py",
    "tsconfig.tooling.json",
    "presentation/ui.css",
)
REQUIRED_OUTPUTS = {
    "index.html",
    "plan.json",
    "canonical.story.md",
    "captions.srt",
    "captions.vtt",
    "transcript.md",
    "stills.json",
    "first.png",
    "poster.png",
}


class BatchEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    entry_id: str
    story_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    recipe: str
    frames: int = Field(gt=0)
    fps: int = Field(gt=0)
    dependencies: dict[str, str]

    @property
    def video_name(self) -> str:
        return "route-unfold.mp4" if self.recipe == "route-unfold-v1" else f"{self.story_id}.mp4"


class Batch(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1] = 1
    entries: tuple[BatchEntry, ...] = Field(min_length=1)
    stills_only: StrictBool
    frontend_inputs: dict[str, str]
    frontend_manifest_sha256: str
    dependencies: dict[str, str]


def _output_path(root: Path, output: Path) -> Path:
    if output.is_absolute():
        try:
            output = output.resolve().relative_to(root.resolve())
        except ValueError as exc:
            raise MedicalError("Batch output must be inside the workspace") from exc
    return storage.inside(root, output)


def new(
    root: Path,
    entry_ids: Sequence[str],
    output: Path,
    *,
    stills_only: bool = False,
    catalog: str = task_catalog.DEFAULT_CATALOG,
) -> Document:
    root = root.resolve()
    output = _output_path(root, output)
    if output.exists():
        raise MedicalError("Batch needs a fresh output directory")
    if not entry_ids or len(set(entry_ids)) != len(entry_ids):
        raise MedicalError("Select distinct catalogue entries")
    frontend.assets(root, "explainer-export")
    dependencies = {name: storage.sha(root / name) for name in EXPORT_SOURCES}
    entries = []
    selected_stories: set[str] = set()
    for entry_id in entry_ids:
        leaf, entry = story_authoring.entry_owner(root, entry_id, catalog)
        story_id = entry.get("illustration", {}).get("story_id")
        if not story_id:
            raise MedicalError(f"Entry has no canonical story: {entry_id}")
        if story_id in selected_stories:
            raise MedicalError(
                "Select one representative per story; shared bindings need own review"
            )
        selected_stories.add(story_id)
        plan = stories.resolve_stories(root, [entry])[story_id]
        dependencies[leaf.relative_to(root).as_posix()] = storage.sha(leaf)
        dependencies.update(plan["dependencies"])
        entries.append(
            BatchEntry(
                entry_id=entry_id,
                story_id=story_id,
                recipe=plan["recipe"],
                frames=plan["durationFrames"],
                fps=plan["fps"],
                dependencies=plan["dependencies"],
            )
        )
    batch = Batch(
        entries=tuple(entries),
        stills_only=stills_only,
        frontend_inputs=frontend.input_hashes(root),
        frontend_manifest_sha256=storage.sha(root / frontend.BUILD_DIR / "manifest.json"),
        dependencies=dependencies,
    )
    output.mkdir(parents=True, exist_ok=False)
    storage.write_new(output / "batch.json", batch.model_dump(mode="json"))
    _gallery(output, batch)
    return {"batch": str(output), "entries": len(entries), "visual_review": "pending"}


def load(output: Path) -> Batch:
    batch = Batch.model_validate_json((output / "batch.json").read_text())
    if len({entry.story_id for entry in batch.entries}) != len(batch.entries):
        raise MedicalError("Duplicate batch story")
    return batch


def snapshot_issues(root: Path, batch: Batch) -> list[str]:
    issues = []
    for name, expected in batch.dependencies.items():
        path = storage.inside(root, name)
        if not path.is_file() or storage.sha(path) != expected:
            issues.append(f"Source changed or missing: {name}")
    if frontend.input_hashes(root) != batch.frontend_inputs:
        issues.append("Frontend source snapshot changed")
    manifest = root / frontend.BUILD_DIR / "manifest.json"
    if not manifest.is_file() or storage.sha(manifest) != batch.frontend_manifest_sha256:
        issues.append("Frontend build snapshot changed or missing")
    return issues


def run(root: Path, output: Path) -> Document:
    """Invoke the existing exporter once per story; stop on the first failure."""
    output = _output_path(root, output)
    batch = load(output)
    issues = snapshot_issues(root, batch)
    if issues:
        raise MedicalError("; ".join(issues))
    if (output / "execution.json").exists() or any(
        (output / entry.story_id).exists() for entry in batch.entries
    ):
        raise MedicalError("Batch already attempted; retain it and create a fresh batch")
    result: Document = {"ok": False, "exports": [], "visual_review": "pending"}
    storage.write_new(output / "execution.json", result)
    for entry in batch.entries:
        command = [
            "node",
            str(root / "scripts/export_med_tours.mts"),
            f"--story={entry.story_id}",
            f"--output={output / entry.story_id}",
        ]
        if batch.stills_only:
            command.append("--stills-only")
        row: Document = {"entry": entry.entry_id, "story": entry.story_id, "command": command}
        result["exports"].append(row)
        try:
            with (output / f"{entry.story_id}.log").open("x") as log:
                process = subprocess.run(
                    command,
                    cwd=root,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env={**os.environ, "TB3_PYTHON": sys.executable},
                )
            row["exit_code"] = process.returncode
            row["status"] = "exported" if process.returncode == 0 else "execution_failed"
            if process.returncode:
                text = (output / f"{entry.story_id}.log").read_text()
                if any(
                    token in text
                    for token in ("browserType.launch", "LaunchServices", "spawn EPERM")
                ):
                    row["status"] = "browser_startup_failed"
                raise MedicalError(f"{entry.story_id}: {row['status']}; inspect its retained log")
            changed = snapshot_issues(root, batch)
            if changed:
                raise MedicalError("Source changed during batch: " + "; ".join(changed))
        except (OSError, MedicalError) as exc:
            row["error"] = str(exc)
            raise
        finally:
            storage.atomic_write(output / "execution.json", result)
    verification = check(root, output, decode=not batch.stills_only)
    result["ok"] = verification["ok"]
    result["verification"] = verification
    storage.atomic_write(output / "execution.json", result)
    return result


def check(root: Path, output: Path, *, decode: bool = False) -> Document:
    output = _output_path(root, output)
    batch = load(output)
    issues = snapshot_issues(root, batch)
    checked = []
    for entry in batch.entries:
        folder = output / entry.story_id
        try:
            receipt = storage.read_object(folder / "receipt.json")
            plan = storage.read_object(folder / "plan.json")
            if receipt["story"] != entry.story_id or plan["id"] != entry.story_id:
                raise ValueError("story identity differs")
            if (
                receipt["dependencies"] != entry.dependencies
                or plan["dependencies"] != entry.dependencies
            ):
                raise ValueError("story dependencies differ")
            if receipt["frontend_manifest_sha256"] != batch.frontend_manifest_sha256:
                raise ValueError("frontend fingerprint differs")
            if receipt["errors"]:
                raise ValueError("exporter reported page/network errors")
            outputs = receipt["outputs"]
            required = REQUIRED_OUTPUTS | (set() if batch.stills_only else {entry.video_name})
            if not required.issubset(outputs):
                raise ValueError("required export artifacts are missing from receipt")
            for name, expected in outputs.items():
                if Path(name).name != name:
                    raise ValueError("unsafe output name")
                path = folder / name
                if (
                    path.is_symlink()
                    or path.stat().st_size != expected["bytes"]
                    or storage.sha(path) != expected["sha256"]
                ):
                    raise ValueError(f"output fingerprint differs: {name}")
            if decode and not batch.stills_only:
                _decode(folder / entry.video_name, entry)
            checked.append(
                {
                    "entry": entry.entry_id,
                    "story": entry.story_id,
                    "receipt_sha256": storage.sha(folder / "receipt.json"),
                }
            )
        except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
            issues.append(f"{entry.story_id}: {exc}")
    return {"ok": not issues, "exports": checked, "issues": issues, "visual_review": "pending"}


def _decode(path: Path, entry: BatchEntry) -> None:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    streams = json.loads(probe.stdout)["streams"]
    if len(streams) != 1:
        raise ValueError("Expected one silent video stream")
    stream = streams[0]
    if (stream["codec_name"], stream["width"], stream["height"], int(stream["nb_read_frames"])) != (
        "h264",
        1280,
        720,
        entry.frames,
    ):
        raise ValueError("Video codec, dimensions or frame count differs")
    numerator, denominator = (int(n) for n in stream["r_frame_rate"].split("/"))
    if numerator != entry.fps * denominator:
        raise ValueError("Video frame rate differs")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"],
        check=True,
        capture_output=True,
    )


def _gallery(output: Path, batch: Batch) -> None:
    cards = []
    for entry in batch.entries:
        key = entry.story_id
        links = {
            "Interactive story": "index.html",
            "Transcript": "transcript.md",
            "Receipt": "receipt.json",
        }
        if not batch.stills_only:
            links["Video"] = entry.video_name
        navigation = " · ".join(
            f'<a href="{key}/{name}">{label}</a>' for label, name in links.items()
        )
        cards.append(
            f"<article><h2>{escape(entry.entry_id)}</h2><nav>{navigation}</nav>"
            f'<div><img src="{key}/first.png" alt="First frame"><img src="{key}/poster.png" alt="Ending poster"></div></article>'
        )
    (output / "review.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        "<title>Story batch review</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:16px}article{margin:32px 0}img{width:48%;height:auto}a{color:#245b8b}</style>"
        "<h1>Story batch review</h1><p>Visual review pending for all entries. Export verification does not establish visual or scientific acceptance. "
        "Record the reviewer, source snapshot, inspected views and remaining limits separately.</p>"
        + "".join(cards)
        + "</html>"
    )
