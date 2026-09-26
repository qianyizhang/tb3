"""Portable, fingerprinted sample/reference snapshots for dataset pages."""

import base64
import re
from pathlib import Path

from . import storage
from .errors import MedicalError
from .types import Pathish, Records

CATALOG = "datasets/previews/catalog.json"
STATES = {"paired", "input-only", "reference-only", "unavailable"}


def load(root: Pathish, dataset_ids: set[str], *, required: bool = False) -> Records:
    root = Path(root).resolve()
    path = root / CATALOG
    if not path.is_file():
        if required:
            raise MedicalError("Missing dataset snapshot catalog")
        return {}
    output = {}
    for row in storage.read(path)["entries"]:
        key = row["dataset_id"]
        if key in output or key not in dataset_ids:
            raise MedicalError("Duplicate or unknown dataset snapshot: " + key)
        if row.get("status") not in STATES or not all(
            row.get(field) for field in ("sample_id", "summary", "reference_note", "sources")
        ):
            raise MedicalError("Incomplete dataset snapshot: " + key)
        for source in row["sources"]:
            storage.inside(root, source["path"])
            if not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", "")):
                raise MedicalError("Snapshot source lacks a fingerprint: " + key)
        panels = []
        for panel in row.get("panels", []):
            if panel.get("role") not in {"input", "reference", "metadata"} or not panel.get(
                "caption"
            ):
                raise MedicalError("Incomplete snapshot panel: " + key)
            resolved = dict(panel)
            if panel.get("path"):
                image = storage.inside(root, panel["path"])
                if image.suffix != ".png" or not re.fullmatch(
                    r"[0-9a-f]{64}", panel.get("sha256", "")
                ):
                    raise MedicalError("Snapshot requires a pinned PNG: " + key)
                resolved["available"] = image.is_file()
                if image.is_file():
                    if storage.sha(image) != panel["sha256"]:
                        raise MedicalError("Dataset snapshot changed: " + panel["path"])
                    resolved["image_url"] = (
                        "data:image/png;base64," + base64.b64encode(image.read_bytes()).decode()
                    )
            elif isinstance(panel.get("text"), str) and panel["text"].strip():
                resolved["available"] = True
            else:
                raise MedicalError("Empty snapshot panel: " + key)
            panels.append(resolved)
        roles = {p["role"] for p in panels}
        expected = {
            "paired": {"input", "reference"},
            "input-only": {"input"},
            "reference-only": {"reference"},
            "unavailable": {"metadata"},
        }[row["status"]]
        if roles != expected:
            raise MedicalError("Snapshot availability contradicts its panels: " + key)
        output[key] = {**row, "panels": panels}
    if required and output.keys() != dataset_ids:
        raise MedicalError("Every dataset needs a snapshot or explicit acquisition gap")
    return output
