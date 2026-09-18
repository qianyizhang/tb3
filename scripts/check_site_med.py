#!/usr/bin/env python3
"""Check rewritten medical content, relative links, assets and source values.

Checks portable files by default; --local also requires runtime-only links.
Does not validate the legacy HTML presentation or run experiments.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from prepare_site_med_assets import prepare

ROOT = Path(__file__).resolve().parents[1]
MED = ROOT / "site_med"


def resolve_pointer(value, pointer):
    for part in pointer.lstrip("/").split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true", help="Also require local media and raw-evidence links")
    args = parser.parse_args()
    errors = []
    deferred_links = 0
    chapters = sorted(MED.glob("0[1-6]-*.md"))
    if len(chapters) != 6:
        errors.append("Expected six chapters")
    for page in chapters + [MED / "references.md", MED / "README.md"]:
        content = page.read_text()
        if "file:///" in content:
            errors.append(f"{page.name}: machine-local URL")
        if any(ord(c) < 32 and c not in "\n\t\r" for c in content):
            errors.append(f"{page.name}: unexpected control character")
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            resolved = (page.parent / unquote(parsed.path)).resolve()
            relative = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else ""
            local_only = relative.startswith(("runs/", "jobs/", ".cache/", "site_med/tours/data/",
                                               "site_med/tours/web/", "site_med/tours/exports/"))
            if local_only and not args.local:
                deferred_links += 1
                continue
            if not resolved.exists():
                errors.append(f"{page.name}: missing target {target}")
        if page in chapters:
            for section in ("## See the task", "## Why this work matters",
                            "## What the agent received and returned",
                            "## What worked, and what it cost", "## Inspect or reproduce"):
                if section not in content:
                    errors.append(f"{page.name}: missing {section}")
            # A reading estimate, not a semantic or scientific correctness test.
            prose = re.sub(r"```.*?```", "", content, flags=re.S)
            prose = re.sub(r"\]\([^)]*\)", "]", prose)
            print(f"{page.name}: approximately {len(prose.split())} words excluding code/diagrams")

    values = 0
    cards = sorted((MED / "task_cards").glob("*.json"))
    if len(cards) != 6:
        errors.append("Expected six task cards")
    for path in cards:
        card = json.loads(path.read_text())
        if card.get("schema_version") != 2:
            errors.append(f"{path.name}: expected source-linked editorial schema")
        for key in ("protocol", "reproduction"):
            if not (ROOT / card[key]).is_file():
                errors.append(f"{path.name}: missing {key}")
        if not (MED / card["chapter"]).is_file():
            errors.append(f"{path.name}: missing chapter")
        sources = {}
        for source, digest in card["source_hashes"].items():
            blob = (ROOT / source).read_bytes()
            if hashlib.sha256(blob).hexdigest() != digest:
                errors.append(f"{path.name}: changed source {source}")
            sources[source] = json.loads(blob)
        for metric in card["measurements"]:
            value = resolve_pointer(sources[metric["source"]], metric["pointer"])
            if value != metric["value"]:
                errors.append(f"{path.name}: source mismatch for {metric['label']}")
            values += 1

    exports = prepare()
    for relative, expected in exports.items():
        path = MED / relative
        if not path.exists() or path.read_bytes() != expected:
            errors.append(f"Missing/stale export: {relative}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Checked six chapters, references, {values} source values, and {len(exports)-1} assets.")
    if deferred_links:
        print(f"Deferred {deferred_links} local media/evidence links; use --local to require them.")
    print("Legacy HTML is excluded. Clinical validity and external URL availability are not certified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
