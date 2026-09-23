"""Explicit bounded acquisition. No model execution; existing complete files are retained."""

import concurrent.futures
import hashlib
import json
import zipfile
from pathlib import Path

import requests
from http_zip import HTTPRangeFile

ROOT = Path(".local/wsi-ground-truth")
META = ROOT / "source-metadata"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def direct(job):
    path = ROOT / job["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        tmp = path.with_suffix(path.suffix + ".part")
        with requests.get(job["url"], stream=True, timeout=(30, 120)) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for b in r.iter_content(4 * 1024 * 1024):
                    f.write(b)
        if job.get("bytes") and tmp.stat().st_size != job["bytes"]:
            raise ValueError("size mismatch")
        tmp.rename(path)
    if job.get("bytes") and path.stat().st_size != job["bytes"]:
        raise ValueError("size mismatch")
    result = {**job, "local_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}
    print("ACQUIRED", job["path"], result["bytes"], flush=True)
    return result


def main():
    jobs = json.loads((META / "selected-downloads.json").read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        receipts = list(ex.map(direct, jobs))
    (ROOT / "direct-receipt.json").write_text(json.dumps(receipts, indent=2) + "\n")


def hubmap():
    z = json.loads((META / "hubmap-zenodo.json").read_text())["files"][0]
    f = HTTPRangeFile(z["links"]["self"], z["size"])
    zf = zipfile.ZipFile(f)
    names = [
        "data/hubmap/kidney/images/train/aaa6a05cc.tiff",
        "data/hubmap/kidney/gt_masks/aaa6a05cc.json",
        "data/hubmap/kidney/gt_masks/aaa6a05cc-anatomical-structure.json",
    ]
    receipts = []
    for name in names:
        info = zf.getinfo(name)
        path = ROOT / "hubmap" / Path(name).name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            data = zf.read(name)  # zipfile verifies each extracted member CRC32
            path.write_bytes(data)
        receipts.append(
            {
                "url": f.url,
                "archive_bytes": z["size"],
                "archive_publisher_checksum": z["checksum"],
                "archive_checksum_verified": False,
                "zip_member": name,
                "zip_crc32": f"{info.CRC:08x}",
                "bytes": path.stat().st_size,
                "local_path": str(path),
                "sha256": sha(path),
            }
        )
        print("EXTRACTED", name, info.file_size, flush=True)
    (ROOT / "hubmap-receipt.json").write_text(json.dumps(receipts, indent=2) + "\n")


if __name__ == "__main__":
    import sys

    hubmap() if "--hubmap" in sys.argv else main()
