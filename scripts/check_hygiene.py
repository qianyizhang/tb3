#!/usr/bin/env python3
"""Read-only artifact gate over the Git index, independent of local run data."""
from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tomllib

POLICY = "configs/artifact-policy.json"


def git(root: Path, *args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], input=data,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True).stdout


def index_files(root: Path) -> dict[str, bytes]:
    entries = []
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, oid, stage = metadata.split()
        path = name.decode("utf-8")
        if stage != b"0":
            raise ValueError(f"unresolved merge: {path}")
        if mode not in (b"100644", b"100755"):
            raise ValueError(f"unsupported index mode {mode.decode()}: {path}")
        entries.append((path, oid))
    raw = git(root, "cat-file", "--batch", data=b"".join(oid + b"\n" for _, oid in entries))
    files = {}
    cursor = 0
    for path, _ in entries:
        end = raw.index(b"\n", cursor)
        _, kind, length = raw[cursor:end].split()
        if kind != b"blob":
            raise ValueError(f"not a regular blob: {path}")
        cursor = end + 1
        size = int(length)
        files[path] = raw[cursor:cursor + size]
        cursor += size + 1
    return files


def problems(files: dict[str, bytes]) -> list[str]:
    policy = json.loads(files[POLICY])
    if policy["schema_version"] != 1:
        raise ValueError("unsupported artifact policy version")
    errors = []
    for name, data in files.items():
        path = PurePosixPath(name)
        components = path.parts
        if any(fnmatch.fnmatchcase(part, pattern)
               for part in components if part != ".env.example"
               for pattern in policy["blocked_components"]):
            errors.append(f"{name}: local/generated artifact must stay untracked")
        if components[0] in policy["local_roots"]:
            errors.append(f"{name}: local runtime directory must stay untracked")
        special = len(data) > policy["max_file_bytes"] or b"\0" in data[:8192]
        exception = policy["retained_artifacts"].get(name)
        if exception:
            if not exception.get("reason") or hashlib.sha256(data).hexdigest() != exception["sha256"]:
                errors.append(f"{name}: retained artifact changed; review provenance and update its digest")
        elif special:
            errors.append(f"{name}: binary or over {policy['max_file_bytes']} bytes; explicit digest/reason required")
        vendor = any(name.startswith(prefix) for prefix in policy["vendor_roots"])
        if not vendor and path.suffix in (".json", ".toml"):
            try:
                text = data.decode("utf-8")
                json.loads(text) if path.suffix == ".json" else tomllib.loads(text)
            except (ValueError, UnicodeError) as exc:
                errors.append(f"{name}: invalid {path.suffix[1:]} ({exc})")
    return errors


def main() -> int:
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip())
        files = index_files(root)
        errors = problems(files)
    except (subprocess.CalledProcessError, ValueError, KeyError, TypeError) as exc:
        print(f"hygiene: cannot validate index: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"hygiene: {len(files)} staged/tracked files pass (Git index only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
