#!/usr/bin/env python3
"""Validate local links and closed code fences in maintained Markdown."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

CONFIG_PATH = Path("configs/doc-links.json")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
INLINE_LINK = re.compile(
    r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))")
HTML_LINK = re.compile(r"\b(?:href|src)\s*=\s*(['\"])(.*?)\1", re.IGNORECASE)
INLINE_CODE = re.compile(r"(`+)(.*?)\1")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
HTML_ID = re.compile(r"\bid\s*=\s*(['\"])(.*?)\1", re.IGNORECASE)
LINE_FRAGMENT = re.compile(r"L\d+(?:-L\d+)?$")


@dataclass(frozen=True)
class LinkIssue:
    source: str
    line: int
    target: str
    reason: str

    def __str__(self) -> str:
        return f"{self.source}:{self.line}: {self.target}: {self.reason}"


@dataclass(frozen=True)
class AuditResult:
    documents_checked: int
    links_checked: int
    optional_local_links: int
    issues: tuple[LinkIssue, ...]


@dataclass(frozen=True)
class Policy:
    required_files: tuple[str, ...]
    include_globs: tuple[str, ...]
    exclude_globs: tuple[str, ...]
    optional_local_roots: tuple[str, ...]
    external_schemes: frozenset[str]


def load_policy(root: Path) -> Policy:
    raw = json.loads((root / CONFIG_PATH).read_text(encoding="utf-8"))
    if raw.get("schema_version") != 1:
        raise ValueError("unsupported document-link policy version")
    return Policy(
        required_files=tuple(raw["required_files"]),
        include_globs=tuple(raw["include_globs"]),
        exclude_globs=tuple(raw["exclude_globs"]),
        optional_local_roots=tuple(raw["optional_local_roots"]),
        external_schemes=frozenset(scheme.lower() for scheme in raw["external_schemes"]),
    )


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def maintained_documents(root: Path, policy: Policy) -> tuple[tuple[Path, ...], list[LinkIssue]]:
    documents: set[Path] = set()
    issues: list[LinkIssue] = []
    for name in policy.required_files:
        path = root / name
        if path.is_file():
            documents.add(path)
        else:
            issues.append(LinkIssue(name, 1, name, "required maintained document is missing"))
    for pattern in policy.include_globs:
        documents.update(path for path in root.glob(pattern) if path.is_file())
    kept = tuple(
        sorted(
            (
                path
                for path in documents
                if not _matches(path.relative_to(root).as_posix(), policy.exclude_globs)
            ),
            key=lambda path: path.relative_to(root).as_posix(),
        )
    )
    return kept, issues


def markdown_lines(path: Path) -> tuple[list[tuple[int, str]], int | None]:
    """Return prose and any unclosed fence's line, excluding fenced examples.

    Maintained guides require explicit closing fences, even though Markdown can
    render an unfinished block through EOF. A closer must use the same marker,
    be at least as long as its opener and have no trailing prose.
    """
    lines: list[tuple[int, str]] = []
    fence: str | None = None
    fence_line: int | None = None
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fence_match = FENCE.match(raw_line)
        if fence is not None:
            if fence_match:
                marker, trailing = fence_match.groups()
                closes = marker[0] == fence[0] and len(marker) >= len(fence)
                if closes and not trailing.strip():
                    fence = None
                    fence_line = None
            continue
        if fence_match:
            marker, info = fence_match.groups()
            if marker[0] == "~" or "`" not in info:
                fence = marker
                fence_line = line_number
                continue
        lines.append((line_number, raw_line))
    return lines, fence_line


def markdown_links(path: Path) -> tuple[tuple[int, str], ...]:
    links: list[tuple[int, str]] = []
    lines, _ = markdown_lines(path)
    for line_number, raw_line in lines:
        line = INLINE_CODE.sub("", raw_line)
        reference = REFERENCE_LINK.match(line)
        if reference:
            links.append((line_number, reference.group(1) or reference.group(2)))
            continue
        links.extend(
            (line_number, match.group(1) or match.group(2)) for match in INLINE_LINK.finditer(line)
        )
        links.extend((line_number, match.group(2)) for match in HTML_LINK.finditer(line))
    return tuple(links)


def _slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = INLINE_LINK.sub(lambda match: match.group(0).split("]", 1)[0].lstrip("!["), text)
    text = INLINE_CODE.sub(lambda match: match.group(2), text)
    return re.sub(r"[^\w\s-]", "", text.lower()).replace(" ", "-")


def markdown_anchors(path: Path) -> frozenset[str]:
    anchors: set[str] = set()
    occurrences: dict[str, int] = {}
    lines, _ = markdown_lines(path)
    for _, raw_line in lines:
        heading = HEADING.match(raw_line)
        if heading:
            base = _slug(heading.group(2))
            count = occurrences.get(base, 0)
            occurrences[base] = count + 1
            anchors.add(base if count == 0 else f"{base}-{count}")
        anchors.update(match.group(2) for match in HTML_ID.finditer(raw_line))
    return frozenset(anchors)


def _inside(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
    except ValueError:
        return False
    return True


def _under_optional_root(relative: str, roots: tuple[str, ...]) -> bool:
    return any(relative == root or relative.startswith(root + "/") for root in roots)


def audit(root: Path) -> AuditResult:
    root = root.resolve()
    policy = load_policy(root)
    documents, issues = maintained_documents(root, policy)
    links_checked = 0
    optional_local_links = 0
    anchor_cache: dict[Path, frozenset[str]] = {}

    for source in documents:
        source_name = source.relative_to(root).as_posix()
        _, fence_line = markdown_lines(source)
        if fence_line is not None:
            issues.append(
                LinkIssue(source_name, fence_line, "code fence", "fenced code block is not closed")
            )
        for line_number, raw_target in markdown_links(source):
            links_checked += 1
            target = raw_target.strip()
            if not target:
                continue
            parsed = urlsplit(target)
            if parsed.scheme:
                if parsed.scheme.lower() not in policy.external_schemes:
                    issues.append(
                        LinkIssue(
                            source_name, line_number, target, "unsupported or local URI scheme"
                        )
                    )
                continue
            if target.startswith("//") or parsed.path.startswith("/"):
                issues.append(
                    LinkIssue(
                        source_name, line_number, target, "machine-absolute path is not portable"
                    )
                )
                continue

            link_path = unquote(parsed.path)
            destination = (source.parent / link_path).resolve() if link_path else source.resolve()
            if not _inside(root, destination):
                issues.append(
                    LinkIssue(source_name, line_number, target, "path escapes repository")
                )
                continue
            destination_name = destination.relative_to(root).as_posix()
            if not destination.exists():
                if _under_optional_root(destination_name, policy.optional_local_roots):
                    optional_local_links += 1
                else:
                    issues.append(
                        LinkIssue(source_name, line_number, target, "target does not exist")
                    )
                continue
            fragment = unquote(parsed.fragment)
            if fragment and destination.suffix.lower() in {".md", ".markdown"}:
                if LINE_FRAGMENT.fullmatch(fragment):
                    continue
                anchors = anchor_cache.get(destination)
                if anchors is None:
                    anchors = markdown_anchors(destination)
                    anchor_cache[destination] = anchors
                if fragment not in anchors:
                    issues.append(
                        LinkIssue(source_name, line_number, target, "heading anchor does not exist")
                    )

    return AuditResult(len(documents), links_checked, optional_local_links, tuple(issues))


def find_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / CONFIG_PATH).is_file():
            return candidate
    raise ValueError(f"cannot find {CONFIG_PATH} from {start}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root (default: discover from cwd)")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve() if args.root else find_root(Path.cwd())
        result = audit(root)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"docs-links: cannot validate documents: {exc}", file=sys.stderr)
        return 1
    if result.issues:
        print("\n".join(str(issue) for issue in result.issues), file=sys.stderr)
        print(
            f"docs-links: {len(result.issues)} issue(s) in "
            f"{result.documents_checked} maintained documents",
            file=sys.stderr,
        )
        return 1
    print(
        f"docs-links: {result.documents_checked} maintained documents and "
        f"{result.links_checked} links pass "
        f"({result.optional_local_links} optional local targets absent)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
