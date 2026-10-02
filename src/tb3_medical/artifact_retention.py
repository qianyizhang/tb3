"""Bounded artifact inventories and exact-byte, deduplicated recovery stores.

Occurrences keep their paths and provenance; SHA-256 objects share only bytes.
No command deletes sources, rewrites evidence, or infers retirement permission.
"""

from __future__ import annotations

import gzip
import hashlib
import os
import stat
import subprocess
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from . import storage
from .errors import MedicalError
from .types import Document

Text = Annotated[str, Field(strict=True, min_length=1)]
Digest = Annotated[str, Field(strict=True, pattern=r"^[a-f0-9]{64}$")]
Count = Annotated[int, Field(strict=True, ge=0)]


def relative_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or path.as_posix() != value:
        raise ValueError(f"Expected a normalized relative file path: {value}")
    return value


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Scope(Model):
    path: Text
    state: Literal["active", "closed"] = "active"
    role: Literal[
        "source", "accepted-evidence", "attempt-evidence", "derived", "scratch", "unknown"
    ] = "unknown"
    retention: Literal["keep", "archive", "rebuild", "unknown"] = "unknown"
    reason: str = ""
    references: list[str] = Field(default_factory=list)
    rebuild_recipe: str = ""

    _path = field_validator("path")(relative_path)


class Job(Model):
    schema_version: Literal[1] = 1
    kind: Literal["artifact-retention-job"] = "artifact-retention-job"
    id: Text
    owner: Text
    source_task: Text
    provenance: list[str] = Field(default_factory=list)
    scopes: Annotated[list[Scope], Field(min_length=1)]
    max_files: Annotated[int, Field(strict=True, gt=0)] = 20000
    max_bytes: Annotated[int, Field(strict=True, gt=0)] = 10_000_000_000

    @model_validator(mode="after")
    def disjoint(self) -> Job:
        paths = [Path(scope.path) for scope in self.scopes]
        for i, path in enumerate(paths):
            if any(path.is_relative_to(other) or other.is_relative_to(path) for other in paths[:i]):
                raise ValueError("Artifact scopes must be disjoint")
        return self


class Occurrence(Model):
    path: Text
    scope: Count
    sha256: Digest
    bytes: Count
    mode: Annotated[int, Field(strict=True, ge=0, le=0o777)]
    mtime_ns: Count

    _path = field_validator("path")(relative_path)


class Plan(Model):
    schema_version: Literal[1] = 1
    kind: Literal["artifact-retention-plan"] = "artifact-retention-plan"
    created_at: Text
    job_sha256: Digest
    job: Job
    git_commit: str | None
    files: list[Occurrence]

    @model_validator(mode="after")
    def valid_occurrences(self) -> Plan:
        paths: set[str] = set()
        sizes: dict[str, int] = {}
        for item in self.files:
            if item.path in paths or item.scope >= len(self.job.scopes):
                raise ValueError("Duplicate path or invalid scope")
            if not Path(item.path).is_relative_to(self.job.scopes[item.scope].path):
                raise ValueError("File falls outside its scope")
            paths.add(item.path)
            if item.sha256 in sizes and sizes[item.sha256] != item.bytes:
                raise ValueError("Conflicting lengths for one object")
            sizes[item.sha256] = item.bytes
        if any(str(parent) in paths for name in paths for parent in Path(name).parents):
            raise ValueError("File paths conflict with parent directories")
        if (
            len(self.files) > self.job.max_files
            or sum(f.bytes for f in self.files) > self.job.max_bytes
        ):
            raise ValueError("Plan exceeds its job limits")
        return self


def _location(path: Path) -> Path:
    # Allow a caller-selected external store/recovery destination. Never follow a
    # symlink into it. Source paths always use the stricter workspace boundary.
    path = path.absolute()
    if ".." in path.parts or any(p.is_symlink() for p in (path, *path.parents)):
        raise MedicalError(f"Unsafe artifact location: {path}")
    return path


def _signature(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
        info.st_mode,
    )


def _files(root: Path, job: Job) -> Iterator[tuple[int, Path]]:
    for index, scope in enumerate(job.scopes):
        target = storage.inside(root, scope.path)
        pending = [target]
        while pending:
            path = pending.pop()
            info = path.lstat()
            if stat.S_ISDIR(info.st_mode):
                pending.extend(sorted(path.iterdir(), reverse=True))
            elif stat.S_ISREG(info.st_mode):
                yield index, path
            else:
                raise MedicalError(f"Only regular files/directories are supported: {path}")


def _read_source(path: Path) -> tuple[str, os.stat_result]:
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise MedicalError(f"Source is not a regular file: {path}")
    with path.open("rb") as stream:
        if _signature(before) != _signature(os.fstat(stream.fileno())):
            raise MedicalError(f"Source changed while opening: {path}")
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
        after = os.fstat(stream.fileno())
    if _signature(before) != _signature(after) or _signature(after) != _signature(path.lstat()):
        raise MedicalError(f"Source changed while hashing: {path}")
    return digest, after


def init_job(paths: list[str], *, id: str, owner: str, source_task: str, output: Path) -> Document:
    job = Job(id=id, owner=owner, source_task=source_task, scopes=[Scope(path=p) for p in paths])
    storage.write_new(_location(output), job.model_dump())
    return {"job": str(output), "status": "classify scopes before packing"}


def summary(plan: Plan) -> Document:
    unique = {f.sha256: f.bytes for f in plan.files}
    total = sum(f.bytes for f in plan.files)
    return {
        "id": plan.job.id,
        "files": len(plan.files),
        "objects": len(unique),
        "logical_bytes": total,
        "unique_bytes": sum(unique.values()),
        "duplicate_logical_bytes": total - sum(unique.values()),
        "retirement_authorized": False,
    }


def plan(root: Path, job_path: Path, output: Path) -> Document:
    root = root.resolve()
    raw = job_path.read_bytes()
    job = Job.model_validate_json(raw)
    destination = _location(output)
    if destination.exists():
        raise MedicalError("Plan needs a fresh output path")
    selected: list[tuple[int, Path]] = []
    total = 0
    for index, path in _files(root, job):
        selected.append((index, path))
        total += path.stat().st_size
        if len(selected) > job.max_files or total > job.max_bytes:
            raise MedicalError(
                "Inventory exceeds job limits; split the scope or set deliberate limits"
            )
    if any(destination.is_relative_to(storage.inside(root, s.path)) for s in job.scopes):
        raise MedicalError("Plan output must be outside the selected scopes")
    rows = []
    for index, path in selected:
        digest, info = _read_source(path)
        if info.st_mode & 0o7000:
            raise MedicalError(f"Special file permissions are unsupported: {path}")
        rows.append(
            Occurrence(
                path=path.relative_to(root).as_posix(),
                scope=index,
                sha256=digest,
                bytes=info.st_size,
                mode=stat.S_IMODE(info.st_mode),
                mtime_ns=info.st_mtime_ns,
            )
        )
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    result = Plan(
        created_at=datetime.now(UTC).isoformat(),
        job_sha256=hashlib.sha256(raw).hexdigest(),
        job=job,
        git_commit=commit.stdout.strip() if commit.returncode == 0 else None,
        files=rows,
    )
    storage.write_new(destination, result.model_dump())
    return {**summary(result), "plan": str(destination), "plan_sha256": storage.sha(destination)}


def _load(path: Path) -> tuple[Plan, str]:
    raw = path.read_bytes()
    return Plan.model_validate_json(raw), hashlib.sha256(raw).hexdigest()


def _object(store: Path, digest: str) -> Path:
    return storage.inside(store, f"objects/{digest[:2]}/{digest}.gz")


def _check_object(path: Path, digest: str, size: int, output: Path | None = None) -> None:
    hasher = hashlib.sha256()
    total = 0
    destination = output.open("xb") if output else None
    try:
        with gzip.open(path, "rb") as stream:
            while chunk := stream.read(1024 * 1024):
                total += len(chunk)
                if total > size:
                    raise MedicalError(f"Object length exceeds manifest: {path}")
                hasher.update(chunk)
                if destination:
                    destination.write(chunk)
        if total != size or hasher.hexdigest() != digest:
            raise MedicalError(f"Object fingerprint differs: {path}")
    except EOFError as exc:
        raise MedicalError(f"Truncated compressed object: {path}") from exc
    finally:
        if destination:
            destination.close()


def _check_sources(root: Path, manifest: Plan) -> dict[str, tuple[int, ...]]:
    current = {p.relative_to(root).as_posix() for _, p in _files(root, manifest.job)}
    if current != {f.path for f in manifest.files}:
        raise MedicalError("Selected file membership changed; prepare a fresh plan")
    signatures = {}
    for item in manifest.files:
        path = storage.inside(root, item.path)
        digest, info = _read_source(path)
        if (digest, info.st_size, stat.S_IMODE(info.st_mode), info.st_mtime_ns) != (
            item.sha256,
            item.bytes,
            item.mode,
            item.mtime_ns,
        ):
            raise MedicalError(f"Source differs from plan: {item.path}")
        signatures[item.path] = _signature(info)
    return signatures


def _store(store: Path, *, create: bool = False) -> Path:
    store = _location(store)
    marker = storage.inside(store, "store.json")
    if not marker.exists() and create:
        store.mkdir(parents=True, exist_ok=True)
        if any(store.iterdir()):
            raise MedicalError("Refusing an unmarked nonempty object store")
        storage.write_new(
            marker, {"schema_version": 1, "kind": "artifact-object-store", "codec": "gzip"}
        )
    if storage.read_object(marker) != {
        "schema_version": 1,
        "kind": "artifact-object-store",
        "codec": "gzip",
    }:
        raise MedicalError("Unrecognized artifact object store")
    return store


def pack(root: Path, plan_path: Path, store: Path, output: Path) -> Document:
    root = root.resolve()
    manifest, plan_digest = _load(plan_path)
    for scope in manifest.job.scopes:
        if (
            scope.state != "closed"
            or scope.role == "unknown"
            or scope.retention == "unknown"
            or not scope.reason
        ):
            raise MedicalError("Packing requires closed, classified scopes with retention reasons")
        if scope.retention == "rebuild" and not scope.rebuild_recipe:
            raise MedicalError("Rebuild retention requires an explicit recipe")
    store, output = _location(store), _location(output)
    if output.exists():
        raise MedicalError("Pack receipt needs a fresh path")
    for scope in manifest.job.scopes:
        source = storage.inside(root, scope.path)
        if (
            store.is_relative_to(source)
            or output.is_relative_to(source)
            or source.is_relative_to(store)
        ):
            raise MedicalError("Store/receipt and source scopes must be separate")
    source_signatures = _check_sources(root, manifest)
    store = _store(store, create=True)
    objects: dict[str, Occurrence] = {f.sha256: f for f in manifest.files}
    added = 0
    for digest, item in objects.items():
        target = _object(store, digest)
        if target.exists():
            _check_object(target, digest, item.bytes)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name("." + uuid.uuid4().hex + ".tmp")
        try:
            with temporary.open("xb") as raw:
                with gzip.GzipFile(
                    filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=6
                ) as compressed:
                    source = storage.inside(root, item.path)
                    with source.open("rb") as stream:
                        while chunk := stream.read(1024 * 1024):
                            compressed.write(chunk)
                raw.flush()
                os.fsync(raw.fileno())
            _check_object(temporary, digest, item.bytes)
            temporary.chmod(0o444)
            try:
                os.link(temporary, target)
                added += target.stat().st_size
            except FileExistsError:
                _check_object(target, digest, item.bytes)
        finally:
            temporary.unlink(missing_ok=True)
    current_signatures = {
        p.relative_to(root).as_posix(): _signature(p.lstat()) for _, p in _files(root, manifest.job)
    }
    if source_signatures != current_signatures:
        raise MedicalError("Sources changed during packing; no receipt published")
    # The original plan is the portable manifest. Pin the exact serialized bytes.
    target_manifest = storage.inside(store, f"manifests/{plan_digest}.json")
    target_manifest.parent.mkdir(parents=True, exist_ok=True)
    raw_plan = plan_path.read_bytes()
    if (
        hashlib.sha256(raw_plan).hexdigest() != plan_digest
        or Plan.model_validate_json(raw_plan) != manifest
    ):
        raise MedicalError("Plan changed during packing")
    temporary = target_manifest.with_name("." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(raw_plan)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o444)
        try:
            os.link(temporary, target_manifest)
        except FileExistsError:
            if target_manifest.read_bytes() != raw_plan:
                raise MedicalError("Stored manifest differs") from None
    finally:
        temporary.unlink(missing_ok=True)
    result = {
        **summary(manifest),
        "kind": "artifact-pack-receipt",
        "manifest_sha256": plan_digest,
        "manifest": str(target_manifest),
        "store": str(store),
        "added_stored_bytes": added,
        "referenced_stored_bytes": sum(_object(store, d).stat().st_size for d in objects),
        "source_files_retained": True,
        "independent_backup_verified": False,
    }
    storage.write_new(output, result)
    return result


def verify(plan_path: Path, store: Path) -> Document:
    manifest, plan_digest = _load(plan_path)
    store = _store(store)
    for digest, size in {f.sha256: f.bytes for f in manifest.files}.items():
        _check_object(_object(store, digest), digest, size)
    return {**summary(manifest), "verified": True, "manifest_sha256": plan_digest}


def restore(plan_path: Path, store: Path, output: Path) -> Document:
    manifest, plan_digest = _load(plan_path)
    output = _location(output)
    if output.exists():
        raise MedicalError("Restore needs a fresh destination")
    store = _store(store)
    if output.is_relative_to(store) or store.is_relative_to(output):
        raise MedicalError("Restore destination must be separate from the object store")
    for digest, size in {f.sha256: f.bytes for f in manifest.files}.items():
        _check_object(_object(store, digest), digest, size)
    output.mkdir(parents=True, exist_ok=False)
    marker = output / ".artifact-restore-incomplete"
    marker.write_text(plan_digest + "\n")
    for item in manifest.files:
        destination = storage.inside(output, item.path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _check_object(_object(store, item.sha256), item.sha256, item.bytes, destination)
        destination.chmod(item.mode)
        os.utime(destination, ns=(item.mtime_ns, item.mtime_ns))
    marker.unlink()
    return {**summary(manifest), "restored": str(output), "manifest_sha256": plan_digest}
