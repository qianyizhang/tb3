"""Source-backed dataset navigation and explicit, read-only sample auditing.

Ordinary builds verify small receipts, never scan native data. ``audit`` is the
explicit operation that hashes declared local files; absent files remain gaps.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from . import core as c

ROLES = {
    "used",
    "curated",
    "screened",
    "metadata-only",
    "illustration",
    "helper",
    "synthetic",
    "not-acquired",
}
FIELDS = (
    "summary",
    "modality",
    "sample_unit",
    "image_description",
    "annotation_description",
    "reference_note",
    "version_note",
    "terms_note",
)


def pointer(value, location):
    """Resolve a JSON Pointer; never evaluate a path expression or import a probe."""
    if location and not location.startswith("/"):
        raise c.MedicalError("Invalid dataset receipt pointer: " + location)
    try:
        for part in location.split("/")[1:]:
            part = part.replace("~1", "/").replace("~0", "~")
            value = value[int(part)] if isinstance(value, list) else value[part]
    except (KeyError, IndexError, ValueError, TypeError) as error:
        raise c.MedicalError("Missing dataset receipt pointer: " + location) from error
    return value


def checked_receipt(root, ref, cache):
    path = c.inside(root, ref["path"])
    if not path.is_file():
        raise c.MedicalError("Missing dataset receipt: " + ref["path"])
    if ref["path"] not in cache:
        cache[ref["path"]] = (
            c.sha(path),
            c.read(path) if path.suffix == ".json" else path.read_text(),
        )
    digest, value = cache[ref["path"]]
    if ref.get("sha256") != digest:
        raise c.MedicalError("Dataset receipt changed; review provenance: " + ref["path"])
    return pointer(value, ref.get("pointer", ""))


def file_items(root, spec, cache):
    values = checked_receipt(root, spec["receipt"], cache)
    if not isinstance(values, list) or not values:
        raise c.MedicalError("Dataset file set must select a nonempty list")
    indices = spec.get("indices", list(range(len(values))))
    if (
        not indices
        or len(indices) != len(set(indices))
        or any(type(i) is not int or not 0 <= i < len(values) for i in indices)
    ):
        raise c.MedicalError("Invalid dataset file selection indices")
    return [values[i] for i in indices]


def load(root, entries=(), *, require_coverage=False):
    """Resolve stable dataset/sample/use relationships without reading native files."""
    root = Path(root).resolve()
    experiments = {
        row["id"]: row
        for path in sorted(root.glob("groups/*/experiments/*/experiment.toml"))
        for row in [c.read(path)]
    }
    entry_ids = {e["id"] for e in entries}
    cache, records, ids, covered = {}, [], set(), set()
    for path in sorted(root.glob("datasets/*.json")):
        row = c.read(path)
        key = c.identifier(row["id"])
        if key in ids:
            raise c.MedicalError("Duplicate dataset ID: " + key)
        ids.add(key)
        if row.get("record_type") == "overview":
            continue
        for field in FIELDS:
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise c.MedicalError(f"{key}: missing dataset {field}")
        if not row.get("sample_sets"):
            raise c.MedicalError(key + ": document selected samples or an explicit acquisition gap")
        for sample in row["sample_sets"]:
            if (
                sample.get("role") not in ROLES
                or not sample.get("sample_ids")
                or len(sample["sample_ids"]) != len(set(sample["sample_ids"]))
                or not sample.get("note")
            ):
                raise c.MedicalError(key + ": incomplete sample selection")
            checked_receipt(root, sample["receipt"], cache)
        for payload in row.get("unverified_payloads", []):
            if not all(payload.get(k) for k in ("sample_id", "original_runtime_path", "note")):
                raise c.MedicalError(key + ": incomplete unrecovered payload documentation")
            checked_receipt(root, payload["receipt"], cache)
        if (
            require_coverage
            and row.get("native_payload_expected", True)
            and not row.get("file_sets")
        ):
            raise c.MedicalError(key + ": missing local file inventory")
        for files in row.get("file_sets", []):
            values = file_items(root, files, cache)
            for item in values:
                relative = str(Path(files.get("local_root", "")) / item[files["path_field"]])
                c.inside(root, relative)
                if not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", "")):
                    raise c.MedicalError(key + ": file lacks a SHA-256: " + relative)
        uses = row.get("experiment_ids", [])
        if len(uses) != len(set(uses)) or set(uses) - experiments.keys():
            raise c.MedicalError(key + ": duplicate or unknown experiment use")
        explicit = row.get("brief_ids", [])
        if require_coverage and set(explicit) - entry_ids:
            raise c.MedicalError(key + ": unknown task brief")
        example = row.get("example_brief")
        if require_coverage and example and example not in entry_ids:
            raise c.MedicalError(key + ": unknown example brief")
        covered.update(uses)
        briefs = [e["id"] for e in entries if e["id"] in explicit]
        records.append(
            {
                **row,
                "record_path": str(path.relative_to(root)),
                "task_ids": briefs,
                "experiments": [{"id": x, "title": experiments[x]["title"]} for x in uses],
            }
        )
    missing = sorted(experiments.keys() - covered)
    if require_coverage and missing:
        raise c.MedicalError("Experiments missing dataset documentation: " + ", ".join(missing))
    # Every acquired external example file must resolve once to a source dataset.
    external = root / "presentation/external-tasks/samples.json"
    if require_coverage and external.is_file():
        expected = {
            item["path"]
            for field in ("downloads", "reused_sources")
            for item in c.read(external).get(field, [])
        }
        actual = Counter(
            item[files["path_field"]]
            for row in records
            for files in row.get("file_sets", [])
            if files["receipt"]["path"] == "presentation/external-tasks/samples.json"
            for item in file_items(root, files, cache)
        )
        if set(actual) != expected or any(n != 1 for n in actual.values()):
            raise c.MedicalError("External sample files need exactly one dataset owner")
    return {
        "records": records,
        "coverage": {
            "datasets": len(records),
            "experiments": len(covered),
            "sample_sets": sum(len(d["sample_sets"]) for d in records),
            "receipts": len(cache),
            "unmapped_experiments": missing,
            "scope": "Registered medical experiments, retained source screens and acquired external Task Explorer examples. Survey-only benchmark definitions are not acquired samples.",
        },
    }


def audit(root, data):
    """Hash exact declared local paths. No acquisition, basename search or repair."""
    root = Path(root).resolve()
    cache, seen, files = {}, {}, []
    for row in data["records"]:
        for file_set in row.get("file_sets", []):
            for item in file_items(root, file_set, cache):
                relative = str(Path(file_set.get("local_root", "")) / item[file_set["path_field"]])
                expected = item["sha256"]
                if relative in seen:
                    if seen[relative] != expected:
                        raise c.MedicalError("Conflicting source digests: " + relative)
                    continue
                seen[relative] = expected
                path = c.inside(root, relative)
                actual = c.sha(path) if path.is_file() else None
                files.append(
                    {
                        "dataset_id": row["id"],
                        "path": relative,
                        "expected_sha256": expected,
                        "actual_sha256": actual,
                        "status": "missing"
                        if actual is None
                        else "verified"
                        if actual == expected
                        else "mismatch",
                    }
                )
    no_inventory = [
        d["id"]
        for d in data["records"]
        if d.get("native_payload_expected", True) and not d.get("file_sets")
    ]
    return {
        "schema_version": 1,
        "checked_at": c.now(),
        "coverage": data["coverage"],
        "local_file_counts": dict(Counter(x["status"] for x in files)),
        "datasets_without_local_file_inventory": no_inventory,
        "metadata_only_sources": [
            d["id"] for d in data["records"] if not d.get("native_payload_expected", True)
        ],
        "unverified_payloads": [
            {"dataset_id": d["id"], **payload}
            for d in data["records"]
            for payload in d.get("unverified_payloads", [])
        ],
        "limitations": [
            "Receipt integrity and local byte identity do not certify clinical reference correctness.",
            "Only declared paths are hashed. Missing files and datasets without file inventories remain explicit gaps.",
            "No scans were downloaded, changed or regenerated; no model or authoring module was run.",
        ],
        "files": files,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--verify-local", action="store_true", help="Explicitly hash declared native files"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    from . import task_briefs

    data = task_briefs.load(args.root)["datasets"]
    result = audit(args.root, data) if args.verify_local else data["coverage"]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 1 if result.get("local_file_counts", {}).get("mismatch") else 0


if __name__ == "__main__":
    raise SystemExit(main())
