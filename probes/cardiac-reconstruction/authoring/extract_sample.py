"""Extract the bounded native FeEcho4D Patient001 prefix; never fetch all 11 GB.

Download inputs (HTTP 206 required):
  URL: https://zenodo.org/api/records/21322299/files/FeEcho4D.zip/content
  central directory range: 11278711717-11282906020
  patient prefix range: 0-59126599
Archive metadata: https://zenodo.org/api/records/21322299
This script performs no network operations. It validates each extracted member's
size and CRC32, and records SHA-256. These are partial-archive checks; the complete
archive MD5 has NOT been independently verified. Do not redistribute the data.
"""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib


def central_entries(data):
    pos = 0
    while pos + 46 <= len(data) and data[pos:pos + 4] == b"PK\x01\x02":
        fields = struct.unpack_from("<4s6H3L5H2L", data, pos)
        name_len, extra_len, comment_len = fields[10:13]
        end = pos + 46 + name_len + extra_len + comment_len
        if end > len(data):
            return
        yield {
            "name": data[pos + 46:pos + 46 + name_len].decode(),
            "size": fields[9], "compressed": fields[8],
            "offset": fields[16], "crc32": fields[7], "method": fields[4],
        }
        pos = end


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prefix = args.prefix.read_bytes()
    records = []
    root = "FeEcho4D/FeEcho4D_Annotated/Patient001/"
    for entry in central_entries(args.index.read_bytes()):
        name = entry["name"]
        if not name.startswith(root) or name.endswith("/") or "/scribble/" in name:
            continue
        if name.endswith(".mp4") or name.endswith(".csv"):
            continue
        offset = entry["offset"]
        header = struct.unpack_from("<4s5H3L2H", prefix, offset)
        assert header[0] == b"PK\x03\x04"
        start = offset + 30 + header[-2] + header[-1]
        compressed = prefix[start:start + entry["compressed"]]
        assert len(compressed) == entry["compressed"], name
        assert entry["method"] in (0, 8)
        data = zlib.decompress(compressed, -15) if entry["method"] == 8 else compressed
        assert len(data) == entry["size"] and zlib.crc32(data) == entry["crc32"], name
        relative = Path(name.removeprefix(root))
        assert not relative.is_absolute() and ".." not in relative.parts
        path = args.output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        records.append({**entry, "sha256": hashlib.sha256(data).hexdigest()})
    assert len([r for r in records if "/image/" in r["name"]]) == 1110
    assert len([r for r in records if "/mask/" in r["name"]]) == 1110
    assert len([r for r in records if "/mesh/" in r["name"]]) == 30
    manifest = {
        "source": "https://zenodo.org/records/21322299",
        "archive_size": 11423073355,
        "publisher_archive_md5_unverified": "b9c07a261849b224a743c0ec2037db6c",
        "prefix_sha256": hashlib.sha256(prefix).hexdigest(),
        "index_sha256": hashlib.sha256(args.index.read_bytes()).hexdigest(),
        "members": records,
    }
    (args.output.parent / "extraction-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"members": len(records), "output": str(args.output), "prefix_sha256": manifest["prefix_sha256"]}))


if __name__ == "__main__":
    main()
