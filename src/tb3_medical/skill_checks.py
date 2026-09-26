"""Check portable skill resources and optional installation mirrors; never install."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field

from . import doc_links, storage


class Version(BaseModel):
    model_config = ConfigDict(extra="allow")
    version: str = Field(strict=True, pattern=r"^\d+\.\d+\.\d+$")


class SkillHeader(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(strict=True, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str = Field(strict=True, min_length=1)
    metadata: Version


@dataclass(frozen=True)
class SkillCheck:
    name: str
    version: str | None
    files: dict[str, str]
    issues: tuple[str, ...]


def file_hashes(folder: Path) -> dict[str, str]:
    """Include authored resources; exclude interpreter and desktop caches."""
    return {
        path.relative_to(folder).as_posix(): storage.sha(path)
        for path in sorted(folder.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path.name != ".DS_Store"
    }


def check_skill(folder: Path, installed_root: Path | None = None) -> SkillCheck:
    folder = folder.resolve()
    issues: list[str] = []
    version = None
    files = file_hashes(folder)
    try:
        raw = (folder / "SKILL.md").read_text()
        match = re.match(r"\A---\n(.*?)\n---\n", raw, re.S)
        if not match:
            raise ValueError("Missing YAML frontmatter")
        header = SkillHeader.model_validate(yaml.safe_load(match[1]))
        version = header.metadata.version
        if header.name != folder.name:
            issues.append("Skill name differs from its directory")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        issues.append(f"SKILL.md: {exc}")
    if "references/feedback-ledger.md" not in files:
        issues.append("Missing canonical feedback ledger")
    for name in files:
        source = folder / name
        if source.is_symlink():
            issues.append(f"Nonportable symlink: {name}")
        if source.suffix != ".md":
            continue
        _, unclosed = doc_links.markdown_lines(source)
        if unclosed:
            issues.append(f"{name}:{unclosed}: unclosed code fence")
        for line, target in doc_links.markdown_links(source):
            parsed = urlsplit(target)
            if parsed.scheme in {"https", "http", "codex", "mailto"}:
                continue
            destination = (
                (source.parent / unquote(parsed.path)).resolve()
                if parsed.path
                else source.resolve()
            )
            if parsed.scheme or parsed.netloc or not destination.is_relative_to(folder):
                issues.append(f"{name}:{line}: link escapes the installed skill: {target}")
            elif not destination.exists():
                issues.append(f"{name}:{line}: missing resource: {target}")
            elif (
                parsed.fragment
                and destination.suffix == ".md"
                and not doc_links.LINE_FRAGMENT.fullmatch(parsed.fragment)
                and unquote(parsed.fragment) not in doc_links.markdown_anchors(destination)
            ):
                issues.append(f"{name}:{line}: missing anchor: {target}")
    if installed_root is not None:
        mirror = file_hashes(installed_root / folder.name)
        for name in sorted(files.keys() | mirror.keys()):
            if files.get(name) != mirror.get(name):
                issues.append(f"Installed mirror differs: {name}")
    return SkillCheck(folder.name, version, files, tuple(issues))


def check(
    root: Path, *, installed_root: Path | None = None, names: Sequence[str] = ()
) -> tuple[SkillCheck, ...]:
    folders = sorted(
        path.parent
        for base in (root / "skills", root / "src/tb3_medical/skills")
        for path in base.glob("*/SKILL.md")
    )
    available = {folder.name for folder in folders}
    if len(available) != len(folders):
        raise ValueError("Duplicate canonical skill name")
    if not folders or set(names) - available:
        raise ValueError("No canonical skills or unknown selected skill")
    return tuple(
        check_skill(folder, installed_root)
        for folder in folders
        if not names or folder.name in names
    )


def main(argv: Sequence[str] | None = None) -> int:
    from .core import workspace

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--json", action="store_true", help="Include resource fingerprints")
    args = parser.parse_args(argv)
    try:
        results = check(workspace(args.root), installed_root=args.installed_root, names=args.skill)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"skill-check: {exc}\n")
    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        for result in results:
            state = "FAIL" if result.issues else "PASS"
            print(f"{state} {result.name} {result.version}: {len(result.files)} files")
            for issue in result.issues:
                print(f"  {issue}")
    return int(any(result.issues for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
