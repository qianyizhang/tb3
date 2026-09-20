"""Deterministic explicit-file packages; never overwrite a handed-off repository."""
import json
import re
from pathlib import Path
import shutil
import subprocess

from . import core as c


def export(root, recipe_path, destination):
    recipe = c.read(c.inside(root, recipe_path))
    if recipe.get("schema_version") != 1 or recipe.get("mode") not in {"exact", "adapted"}:
        raise c.MedicalError("Expected a v1 exact/adapted export recipe")
    commit = recipe["source_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise c.MedicalError("Pin source_commit to a full immutable Git commit SHA")
    subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"], cwd=root, check=True, capture_output=True)
    if recipe.get("qualification") != "draft":
        raise c.MedicalError("This exporter emits drafts; current submission gates need a separate review")
    rows = c.projection(root)
    selected = [rows[key] for key in recipe["depends_on"]]
    flagged = [r["id"] for r in selected if r["current"]["validity"] in {"invalidated", "under_review", "superseded"}]
    if flagged and not recipe.get("include_flagged_research"):
        raise c.MedicalError("Source evidence needs review: " + ", ".join(flagged))
    dest = Path(destination).absolute()
    if dest.exists():
        raise c.MedicalError("Destination exists; build into a new directory, never over independent edits")
    seen, entries, gaps = set(), [], []
    for entry in recipe["files"]:
        name = entry["destination"]
        c.inside(dest, name)
        if name in seen or name in {"manifest.json", "recipe.json"} or Path(name).parts[0] == ".git":
            raise c.MedicalError("Duplicate/reserved package destination: " + name)
        seen.add(name)
        source = c.inside(root, entry["source"])
        if not source.is_file():
            gaps.append(entry["source"])
            continue
        if c.sha(source) != entry["sha256"]:
            raise c.MedicalError("Changed package input: " + entry["source"])
        if entry.get("role") not in {"task", "license", "evidence", "reproduction", "provenance"}:
            raise c.MedicalError("Declare an allowed role for every package input")
        if recipe["mode"] == "adapted" and not recipe.get("changes"):
            raise c.MedicalError("Adapted exports require an explicit source-to-package changes list")
        entries.append(entry)
    if gaps:
        raise c.MedicalError("Restore required artifacts (see recipe digests): " + ", ".join(gaps))
    manifest = {"schema_version": 1, "source_commit": commit, "recipe_sha256": c.sha(c.inside(root, recipe_path)),
                "mode": recipe["mode"], "files": entries, "depends_on": recipe["depends_on"],
                "qualification": "draft", "remaining_gates": recipe["remaining_gates"],
                "source_validity": {r["id"]: r["current"] for r in selected},
                "changes": recipe.get("changes", []), "target_profile": recipe["target_profile"],
                "ownership": "Generated during preparation; independent after explicit handoff.",
                "omitted": "Raw configs, credentials, trajectories and unselected runtime artifacts."}
    dest.mkdir(parents=True, exist_ok=False)
    try:
        for entry in entries:
            target = c.inside(dest, entry["destination"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(c.inside(root, entry["source"]), target)
            if c.sha(target) != entry["sha256"]:
                raise c.MedicalError("Source changed during export")
        c.write_new(dest / "manifest.json", manifest)
        c.write_new(dest / "recipe.json", recipe)
        verify(dest)
    except BaseException:
        # Keep the failed package inspectable; never pretend it is complete.
        (dest / "INCOMPLETE").write_text("Export interrupted or verification failed. Build again into a new destination.\n")
        raise
    record = {"schema_version": 1, "kind": "export", "id": "export-" + c.sha(dest / "manifest.json")[:24],
              "depends_on": recipe["depends_on"], "recipe": recipe_path,
              "manifest_sha256": c.sha(dest / "manifest.json"), "qualification": "draft",
              "evidence": [c.evidence(root, recipe_path)], "remaining_gates": recipe["remaining_gates"]}
    path = Path(root) / "exports/records" / (record["id"] + ".json")
    if not path.exists():
        c.write_new(path, record)
    return {"destination": str(dest), "files": len(entries), "record": record["id"], "qualification": "draft"}


def verify(destination):
    dest = Path(destination).resolve()
    manifest = c.read(dest / "manifest.json")
    if (dest / "INCOMPLETE").exists():
        raise c.MedicalError("Package is marked INCOMPLETE")
    if c.sha(c.inside(dest, "recipe.json")) != manifest["recipe_sha256"]:
        raise c.MedicalError("Package recipe changed")
    recipe = c.read(dest / "recipe.json")
    pinned = ("files", "source_commit", "qualification", "remaining_gates", "mode", "target_profile", "depends_on")
    if any(recipe[key] != manifest[key] for key in pinned) or recipe.get("changes", []) != manifest["changes"]:
        raise c.MedicalError("Package manifest differs from the pinned recipe")
    expected = {"recipe.json", "manifest.json", *(e["destination"] for e in manifest["files"])}
    actual = set()
    for p in dest.rglob("*"):
        rel = p.relative_to(dest)
        if rel.parts[0] == ".git": continue
        if p.is_symlink(): raise c.MedicalError("Package contains a symlink: " + str(rel))
        if p.is_file(): actual.add(rel.as_posix())
    if actual != expected:
        raise c.MedicalError("Package inventory differs: " + ", ".join(sorted(actual ^ expected)))
    for entry in manifest["files"]:
        p = c.inside(dest, entry["destination"])
        if not p.is_file() or c.sha(p) != entry["sha256"]:
            raise c.MedicalError("Package input missing/changed: " + entry["destination"])
    return {"verified_files": len(manifest["files"]), "qualification": manifest["qualification"]}
