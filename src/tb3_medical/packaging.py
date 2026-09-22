"""Selected research exports with explicit Git or artifact origins."""

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from . import core as c
from .types import Document, Pathish


def source_bytes(root: Pathish, commit: str, entry: Document) -> bytes:
    if entry["origin"] == "git":
        content = subprocess.check_output(["git", "show", commit + ":" + entry["source"]], cwd=root)
    elif entry["origin"] == "artifact":
        content = c.inside(root, entry["source"]).read_bytes()
    else:
        raise c.MedicalError("Declare git or artifact origin for " + entry["source"])
    if hashlib.sha256(content).hexdigest() != entry["sha256"]:
        raise c.MedicalError("Changed export input: " + entry["source"])
    return content


def export(
    root: Pathish, recipe_path: str, destination: Pathish, *, include_flagged: bool = False
) -> Document:
    source_recipe = c.inside(root, recipe_path)
    recipe_bytes = source_recipe.read_bytes()
    recipe = json.loads(recipe_bytes)
    if recipe.get("schema_version") != 2 or recipe.get("mode") not in {"exact", "adapted"}:
        raise c.MedicalError("Expected a canonical exact/adapted export recipe")
    commit = recipe["source_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise c.MedicalError("Pin source_commit to an immutable Git commit SHA")
    subprocess.run(
        ["git", "cat-file", "-e", commit + "^{commit}"], cwd=root, check=True, capture_output=True
    )
    if recipe.get("submission_status") != "draft":
        raise c.MedicalError(
            "Exports begin as drafts; submission readiness needs a separate assessment"
        )
    rows = c.projection(root)
    states = {key: rows[key]["current"] for key in recipe["experiment_ids"]}
    flags = {
        key: state
        for key, state in states.items()
        if state.get("assessment") in {"needs_review", "invalidated"}
    }
    if flags and not include_flagged:
        raise c.MedicalError(
            "Selected conclusions need review; use --include-flagged for a labeled research draft"
        )
    dest = Path(destination).absolute()
    if dest.exists():
        raise c.MedicalError(
            "Build into a fresh destination; existing packages are independently owned"
        )
    if recipe["mode"] == "adapted" and not recipe.get("changes"):
        raise c.MedicalError("Record the adaptations in changes")
    seen = set()
    for entry in recipe["files"]:
        name = entry["destination"]
        c.inside(dest, name)
        if (
            name in seen
            or name in {"manifest.json", "recipe.json"}
            or Path(name).parts[0] == ".git"
        ):
            raise c.MedicalError("Duplicate/reserved export destination: " + name)
        seen.add(name)
        source_bytes(root, commit, entry)
    manifest = {
        key: recipe[key]
        for key in (
            "schema_version",
            "mode",
            "source_commit",
            "files",
            "experiment_ids",
            "submission_status",
            "target_profile",
            "remaining_gates",
        )
    }
    manifest.update(
        recipe_sha256=hashlib.sha256(recipe_bytes).hexdigest(),
        source_assessments=states,
        review_flags=flags,
        changes=recipe.get("changes", []),
    )
    dest.mkdir(parents=True, exist_ok=False)
    try:
        for entry in recipe["files"]:
            target = c.inside(dest, entry["destination"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source_bytes(root, commit, entry))
            target.chmod(entry.get("mode", 0o644))
        (dest / "recipe.json").write_bytes(recipe_bytes)
        c.write_new(dest / "manifest.json", manifest)
        verify(dest)
    except BaseException:
        (dest / "INCOMPLETE").write_text(
            "Export did not finish. Build again into a fresh destination.\n"
        )
        raise
    row = {
        "schema_version": 2,
        "kind": "export",
        "id": "export-" + c.sha(dest / "manifest.json")[:24],
        "experiment_ids": recipe["experiment_ids"],
        "recipe": recipe_path,
        "manifest_sha256": c.sha(dest / "manifest.json"),
        "submission_status": "draft",
        "review_flags_at_export": flags,
        "evidence": [c.evidence(root, recipe_path)],
    }
    path = Path(root) / "exports/records" / (row["id"] + ".json")
    if not path.exists():
        c.write_new(path, row)
    return {
        "destination": str(dest),
        "files": len(recipe["files"]),
        "record": row["id"],
        "submission_status": "draft",
        "review_flags": flags,
    }


def verify(destination: Pathish) -> Document:
    dest = Path(destination).resolve()
    if (dest / "INCOMPLETE").exists():
        raise c.MedicalError("Package is marked INCOMPLETE")
    manifest = c.read(dest / "manifest.json")
    if c.sha(dest / "recipe.json") != manifest["recipe_sha256"]:
        raise c.MedicalError("Package recipe changed")
    recipe = c.read(dest / "recipe.json")
    pinned = (
        "schema_version",
        "files",
        "source_commit",
        "submission_status",
        "remaining_gates",
        "mode",
        "target_profile",
        "experiment_ids",
    )
    if (
        any(recipe[k] != manifest[k] for k in pinned)
        or recipe.get("changes", []) != manifest["changes"]
    ):
        raise c.MedicalError("Package manifest differs from the pinned recipe")
    expected = {"recipe.json", "manifest.json", *(e["destination"] for e in manifest["files"])}
    actual = set()
    for path in dest.rglob("*"):
        relative = path.relative_to(dest)
        if relative.parts[0] == ".git":
            continue
        if path.is_symlink():
            raise c.MedicalError("Unexpected package symlink: " + str(relative))
        if path.is_file():
            actual.add(relative.as_posix())
    if actual != expected:
        raise c.MedicalError("Package inventory differs: " + ", ".join(sorted(actual ^ expected)))
    for entry in manifest["files"]:
        target = c.inside(dest, entry["destination"])
        if c.sha(target) != entry["sha256"]:
            raise c.MedicalError("Package input changed: " + entry["destination"])
        # POSIX execute bits carry the declared runnable-file contract. Windows
        # chmod does not preserve these bits, so never claim to verify them there.
        if os.name == "posix" and target.stat().st_mode & 0o111 != entry.get("mode", 0o644) & 0o111:
            raise c.MedicalError("Package executable mode changed: " + entry["destination"])
    return {
        "verified_files": len(manifest["files"]),
        "submission_status": manifest["submission_status"],
        "executable_modes": "verified (POSIX)" if os.name == "posix" else "not checked (non-POSIX)",
    }
