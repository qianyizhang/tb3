"""Retrieve only the selected public ZIP members; verify size/CRC and retain hashes."""

import concurrent.futures
import hashlib
import json
import struct
import time
import zlib
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-case02"
URL = "https://fdat.uni-tuebingen.de/api/records/qe950-g4h94/files/Longitudinal_CT_v3.zip/content"
SIZE = 51047900775


def byte_range(start, size):
    assert 0 <= start < SIZE and 0 < size <= 200_000_000
    for attempt in range(3):
        try:
            with requests.get(
                URL,
                headers={"Range": f"bytes={start}-{start + size - 1}"},
                timeout=(20, 90),
                stream=True,
            ) as response:
                response.raise_for_status()
                assert response.status_code == 206, "Refusing whole archive download"
                assert (
                    response.headers["Content-Range"] == f"bytes {start}-{start + size - 1}/{SIZE}"
                )
                data = bytearray()
                for part in response.iter_content(1024 * 1024):
                    data.extend(part)
                    assert len(data) <= size
                assert len(data) == size
                return bytes(data)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def extract(entry):
    target = BASE / "raw" / entry["name"]
    assert target.resolve().is_relative_to((BASE / "raw").resolve())
    if target.exists():
        data = target.read_bytes()
        assert len(data) == entry["size"] and zlib.crc32(data) == entry["crc32"]
    else:
        header = byte_range(entry["offset"], 30)
        h = struct.unpack_from("<4s5H3I2H", header)
        assert h[0] == b"PK\x03\x04" and entry["method"] in (0, 8)
        packed = byte_range(entry["offset"] + 30 + h[-2] + h[-1], entry["compressed"])
        data = zlib.decompress(packed, -15) if entry["method"] == 8 else packed
        assert len(data) == entry["size"] and zlib.crc32(data) == entry["crc32"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    result = {
        "member": entry["name"],
        "bytes": len(data),
        "crc32": entry["crc32"],
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    print(result["member"], flush=True)
    return result


def main():
    selection = json.loads((BASE / "source/selection.json").read_text())
    index_path = ROOT / ".local/longitudinal-ct-review/source/zip-index.json"
    assert hashlib.sha256(index_path.read_bytes()).hexdigest() == selection["index_sha256"]
    response = requests.get("https://fdat.uni-tuebingen.de/api/records/qe950-g4h94", timeout=30)
    response.raise_for_status()
    record = response.json()
    source = BASE / "source/record-v3-current.json"
    source.write_text(json.dumps(record, indent=2) + "\n")
    entry = record["files"]["entries"]["Longitudinal_CT_v3.zip"]
    assert entry["size"] == SIZE and entry["checksum"] == "md5:cde33aed3ed708065f5a1970b5079098"
    patient = selection["selected"]["patient"]
    members = [
        x
        for x in json.loads(index_path.read_text())
        if Path(x["name"]).name.startswith(patient) and not x["name"].endswith("/")
    ]
    assert len(members) == 7 and sum(x["compressed"] for x in members) < 400_000_000
    print(
        f"Retrieving {len(members)} members, {sum(x['compressed'] for x in members):,} compressed bytes",
        flush=True,
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        receipts = list(pool.map(extract, members))
    (BASE / "source/acquisition.json").write_text(
        json.dumps(
            {
                "patient": patient,
                "files": receipts,
                "source_url": URL,
                "compressed_bytes": sum(x["compressed"] for x in members),
                "archive_bytes": SIZE,
                "full_archive_md5_verified": False,
                "checks": "Exact HTTP 206 range, decompressed size, per-member ZIP CRC32, SHA256 receipt",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
