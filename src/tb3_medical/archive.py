"""Verified recovery of explicitly retired files from a local copy or Git history."""
from pathlib import Path
import subprocess

from . import core as c


def restore(root, prefix, destination):
    manifest = c.read(Path(root) / "archive/manifest.json")
    prefix = prefix.rstrip("/")
    c.inside(root, prefix)
    entries = [e for e in manifest["entries"] if e["original_path"] == prefix or e["original_path"].startswith(prefix + "/")]
    if not entries: raise c.MedicalError("No archived files match this original path prefix")
    dest = Path(destination).absolute()
    if dest.exists(): raise c.MedicalError("Recovery destination must be a new directory")
    payloads = []
    import hashlib
    for entry in entries:
        cached = c.inside(root, entry["local_copy"])
        if cached.is_file() and c.sha(cached) == entry["sha256"]:
            blob = cached.read_bytes()
        else:
            try:
                blob = subprocess.check_output(["git", "show", entry["source_commit"] + ":" + entry["original_path"]], cwd=root, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as exc:
                raise c.MedicalError("Recovery source unavailable. Fetch the pre-migration history/tag or restore the verified Git bundle, then retry.") from exc
        if hashlib.sha256(blob).hexdigest() != entry["sha256"]:
            raise c.MedicalError("Archive digest mismatch: " + entry["original_path"])
        payloads.append((entry, blob))
    dest.mkdir(parents=True, exist_ok=False)
    for entry, blob in payloads:
        path = c.inside(dest, entry["original_path"])
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(blob)
        path.chmod(int(entry.get("mode", "100644"), 8) & 0o777)
    return {"restored_files": len(entries), "destination": str(dest), "prefix": prefix,
            "verified_sha256": True, "executed": False}
