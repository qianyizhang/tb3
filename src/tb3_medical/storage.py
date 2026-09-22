"""Workspace paths, document serialization and atomic publication.

Exclusive publication prevents replacement of retained evidence. These functions
have no knowledge of records, experiments, renderers or execution runtimes.
"""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
import uuid
from pathlib import Path
from typing import Any

import tomli_w

from .errors import MedicalError
from .types import Document, Pathish


def sha(path: Pathish) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inside(root: Pathish, relative: Pathish) -> Path:
    root, relative = Path(root).resolve(), Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise MedicalError(f"Expected a workspace-relative path: {relative}")
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise MedicalError(f"Path crosses workspace boundary: {relative}")
    if any(p.is_symlink() for p in (path, *path.parents) if p != root):
        raise MedicalError(f"Path crosses a symlink: {relative}")
    return path


def read(path: Pathish) -> Any:
    """Decode arbitrary document payloads; callers validate their own schema."""
    path = Path(path)
    text = path.read_text()
    if path.suffix == ".toml":
        return tomllib.loads(text)
    if path.suffix == ".md":
        if not text.startswith("+++\n") or "\n+++\n" not in text[4:]:
            raise MedicalError(f"Missing TOML metadata header: {path}")
        header, body = text[4:].split("\n+++\n", 1)
        return {**tomllib.loads(header), "body": body.strip()}
    return json.loads(text)


def read_object(path: Pathish) -> Document:
    """Read an object-shaped document before applying a domain validator."""
    value = read(path)
    if not isinstance(value, dict):
        raise MedicalError(f"Expected a document object: {path}")
    return value


def encode(path: Pathish, value: Document) -> str:
    if Path(path).suffix == ".toml":
        return tomli_w.dumps(value)
    if Path(path).suffix == ".md":
        header = {k: v for k, v in value.items() if k != "body"}
        body: str = value.get("body", "")
        return "+++\n" + tomli_w.dumps(header) + "+++\n\n" + body + "\n"
    return json.dumps(value, indent=2, allow_nan=False) + "\n"


def publish(path: Pathish, value: Document, *, replace: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        tmp.write_text(encode(path, value))
        if replace:
            os.replace(tmp, path)
        else:
            os.link(tmp, path)  # Atomic, exclusive publication; readers never see partial JSON.
    finally:
        tmp.unlink(missing_ok=True)


def write_new(path: Pathish, value: Document) -> None:
    publish(path, value)


def atomic_write(path: Pathish, value: Document) -> None:
    publish(path, value, replace=True)
