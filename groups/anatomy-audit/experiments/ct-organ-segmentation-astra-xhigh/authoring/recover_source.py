"""Extract and verify the eleven selected source files from the pinned archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = EXPERIMENT / "source/selected-source-manifest.json"


def digest(path: Path, algorithm: str) -> str:
    result = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    archive = args.archive.resolve()
    output = args.output.resolve()
    manifest = json.loads(args.manifest.resolve().read_text())
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"destination is not empty: {output}")
    if digest(archive, "md5") != manifest["archive"]["md5"]:
        raise RuntimeError("archive MD5 does not match the pinned Zenodo record")

    extracted: list[dict[str, object]] = []
    with zipfile.ZipFile(archive) as source:
        for item in manifest["files"]:
            relative = Path(item["path"])
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"unsafe manifest path: {relative}")
            info = source.getinfo(item["archive_member"])
            if info.file_size != item["bytes"]:
                raise RuntimeError(f"archive member size mismatch: {info.filename}")
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source.open(info) as input_stream, destination.open("xb") as output_stream:
                shutil.copyfileobj(input_stream, output_stream)
            actual = digest(destination, "sha256")
            if actual != item["sha256"]:
                raise RuntimeError(f"archive member hash mismatch: {info.filename}")
            extracted.append(
                {
                    "path": relative.as_posix(),
                    "bytes": destination.stat().st_size,
                    "sha256": actual,
                }
            )

    receipt = {
        "schema_version": 1,
        "source_record": manifest["record"],
        "source_version": manifest["version"],
        "archive": str(archive),
        "archive_md5": manifest["archive"]["md5"],
        "output": str(output),
        "files": extracted,
    }
    receipt_path = output.parent / f"{output.name}-extraction-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
