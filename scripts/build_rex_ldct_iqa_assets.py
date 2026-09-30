"""Rebuild preserved LDCT teaching bytes after native-source/pixel/hash checks."""

import argparse
import hashlib
import json
import shutil
import struct
import zlib
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--frozen-pack", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    ROOT = a.source_root.resolve()
    PACK = a.frozen_pack.resolve()
    RECEIPT = a.receipt.resolve()
    if a.output.exists():
        raise FileExistsError(a.output)
    receipt = json.loads(RECEIPT.read_text())
    for pin in receipt["source_pins"]:
        assert sha((ROOT / pin["path"]).read_bytes()) == pin["sha256"], pin["path"]
    source = ROOT / ".local/explainers/core-20260929/interpretation-d-source/rexmle-ldct-iqa"
    tree = json.loads((source / "tree.json").read_text())
    by_path = {x["path"]: x for x in tree["tree"]}
    for file in (source / "pinned-source").iterdir():
        raw = file.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert blob == by_path["rex-mle/rexmle/challenges/ldct-iqa/" + file.name]["sha"]
    raw = (source / "0559.tif").read_bytes()
    endian = "<" if raw[:2] == b"II" else ">"
    offset = struct.unpack_from(endian + "I", raw, 4)[0]
    count = struct.unpack_from(endian + "H", raw, offset)[0]
    tags = {
        t: v
        for t, _, _, v in (
            struct.unpack_from(endian + "HHII", raw, offset + 2 + 12 * i) for i in range(count)
        )
    }
    assert (tags[256], tags[257], tags[258], tags[259], tags[339]) == (512, 512, 32, 1, 3)
    data = struct.unpack_from(endian + str(512 * 512) + "f", raw, tags[273])
    assert min(data) == 0 and max(data) == 1
    gray = bytes(max(0, min(255, round(v * 255))) for v in data)
    png = (PACK / "image.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    compressed = bytearray()
    pos = 8
    while pos < len(png):
        length = struct.unpack_from(">I", png, pos)[0]
        kind, content = png[pos + 4 : pos + 8], png[pos + 8 : pos + 8 + length]
        if kind == b"IHDR":
            assert struct.unpack(">IIBBBBB", content) == (512, 512, 8, 0, 0, 0, 0)
        if kind == b"IDAT":
            compressed.extend(content)
        pos += length + 12
    filtered = zlib.decompress(compressed)
    decoded = bytearray()
    previous = bytes(512)
    for y in range(512):
        method = filtered[y * 513]
        row = bytearray(filtered[y * 513 + 1 : (y + 1) * 513])
        for x in range(512):
            left = row[x - 1] if x else 0
            above = previous[x]
            corner = previous[x - 1] if x else 0
            if method == 4:
                candidate = left + above - corner
                distances = [abs(candidate - v) for v in (left, above, corner)]
                predictor = (left, above, corner)[distances.index(min(distances))]
            else:
                predictor = (0, left, above, (left + above) // 2)[method]
            row[x] = (row[x] + predictor) % 256
        decoded.extend(row)
        previous = row
    assert bytes(decoded) == gray
    assert json.loads((source / "train.json").read_text())["0559.tif"] == 3.8
    manifest = json.loads((PACK / "manifest.json").read_text())
    for asset in manifest["assets"]:
        raw = (PACK / asset["file"]).read_bytes()
        assert sha(raw) == asset["sha256"] and len(raw) == asset["bytes"]
    assert manifest["sources"][
        "presentation/external-tasks/sources/rexmle-ldct-iqa-resolution.json"
    ] == sha(RECEIPT.read_bytes())
    a.output.mkdir(parents=True)
    for name in [asset["file"] for asset in manifest["assets"]] + ["manifest.json"]:
        shutil.copyfile(PACK / name, a.output / name)
    print("Verified source pins, native pixels and eight deterministic frozen pack files")


if __name__ == "__main__":
    main()
