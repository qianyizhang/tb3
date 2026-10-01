"""Import-safe symbolic LIDC-IDRI noise/contract builder; no FFT/reconstruction/evaluator."""

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from zipfile import ZipFile

TAGS = {
    (0x0020, 0x0037): "orientation",
    (0x0008, 0x0018): "sop_uid",
    (0x0002, 0x0010): "transfer_syntax",
    (0x0008, 0x0060): "modality",
    (0x0020, 0x000D): "study_uid",
    (0x0020, 0x000E): "series_uid",
    (0x0020, 0x0013): "instance_number",
    (0x0020, 0x0032): "image_position",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "spacing",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "intercept",
    (0x0028, 0x1053): "slope",
    (0x7FE0, 0x0010): "pixel_data",
}
LONG_VR = {"OB", "OW", "OF", "SQ", "UT", "UN", "OD", "OL", "UC", "UR", "OV"}


def parse_dicom(raw: bytes) -> dict[str, object]:
    if raw[128:132] != b"DICM":
        raise ValueError("not a Part 10 DICOM")
    pos = 132
    tags: dict[str, object] = {}
    while pos + 8 <= len(raw):
        group, element = struct.unpack_from("<HH", raw, pos)
        vr = raw[pos + 4 : pos + 6].decode("ascii")
        long_vr = vr in LONG_VR
        head = 12 if long_vr else 8
        size = struct.unpack_from("<I" if long_vr else "<H", raw, pos + (8 if long_vr else 6))[0]
        if size == 0xFFFFFFFF or pos + head + size > len(raw):
            raise ValueError("unsupported DICOM element length")
        key = TAGS.get((group, element))
        if key:
            value = raw[pos + head : pos + head + size]
            if key == "pixel_data":
                tags[key] = value
                break
            tags[key] = (
                struct.unpack("<H", value)[0]
                if vr == "US" and size == 2
                else value.decode("ascii").strip("\0 ")
            )
        pos += head + size
    return tags


def png_gray8(width: int, height: int, pixels: bytes) -> bytes:
    def chunk(name: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data))
        )

    scanlines = b"".join(b"\0" + pixels[y * width : (y + 1) * width] for y in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scanlines, level=9))
        + chunk(b"IEND", b"")
    )


ENTRY = "automedbench-full-lidc-idri-denoising-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, default=None)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--attribution", type=Path, required=True)
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    source_root = a.source_root or a.root
    for pin in r["source_pins"]:
        raw_pin = (source_root / pin["path"]).read_bytes()
        if len(raw_pin) != pin["bytes"] or hashlib.sha256(raw_pin).hexdigest() != pin["sha256"]:
            raise ValueError("Stale source pin: " + pin["path"])
    assert sha(bp) == r["brief_sha256"]
    ex = r["native_source_example"]
    assert sha(a.archive) == ex["archive_sha256"]
    assert sha(a.attribution) == ex["full_attribution_sha256"]
    with ZipFile(a.archive) as z:
        raw = z.read(ex["member"])
        assert hashlib.sha256(raw).hexdigest() == ex["raw"]["raw_member_sha256"]
        assert hashlib.sha256(z.read("LICENSE")).hexdigest() == ex["embedded_license_sha256"]
        tags = parse_dicom(raw)
    assert tags["rows"] == 512 and tags["columns"] == 512 and tags["pixel_representation"] == 1
    assert tags["slope"] == "1" and tags["intercept"] == "-1024"
    stored = struct.unpack("<262144h", tags["pixel_data"])
    display = bytes(
        255 * (max(-160, min(240, stored[j * 512 + i] - 1024)) + 160) // 400
        for j in range(0, 512, 4)
        for i in range(0, 512, 4)
    )
    native_png = png_gray8(128, 128, display)
    if a.output.exists():
        raise FileExistsError(a.output)
    a.output.mkdir(parents=True)

    def put(n, v):
        (a.output / n).write_text(json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n")

    source = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
            "source_condition",
        ]
    }
    source["notice"] = {
        "label": "Matching noisy CT / target missing",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official LIDC-IDRI acquisition",
    }
    source["symbolic_display"] = {
        "native_image": None,
        "low_cells": 4,
        "high_cells": 4,
        "native_pixel_parity": "default symbolic; separate late upstream display has exact parity",
        "no_denoising_or_model": True,
    }
    source["upstream_example"] = ex
    source["upstream_display_pixel_sha256"] = hashlib.sha256(display).hexdigest()
    (a.output / "upstream-ct.png").write_bytes(native_png)
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "normalized sigma and unknown clean/noise boundary",
                "Full Lite / Standard help and format checker",
                "same geometry with unknown clean/output values",
            ],
            "native_reconstruction": None,
            "fitting_or_evaluator_executed": False,
        },
    )
    put(
        "output.json",
        {
            "enhanced_npy": None,
            "actual_image": None,
            "quality_score": None,
            "task_outcome": None,
        },
    )
    (a.output / "SOURCE-LICENSE.txt").write_bytes(a.attribution.read_bytes())
    (a.output / "DATA-LICENSE.txt").write_text(
        "LicenseRef-AutoMedBench-LIDC-IDRI-symbolic-teaching: authored illustrative pixel values and geometry only; no matching Full patient image, private target, model or metric. Reader-only upstream CT PNG is separately CC BY3.0 under SOURCE-LICENSE attribution; dataset rights do not establish Full pair or target permission.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nTeal authored noisy cells; outlined clean/output cells unknown, same geometry. Not CT, Gaussian random realization, denoised result, private reference or clinical outcome.\n"
    )
    assets = [
        {
            "file": q.name,
            "bytes": q.stat().st_size,
            "sha256": sha(q),
            "role": "reader-reference-reveal"
            if q.suffix == ".png"
            else "reader-reference-reveal"
            if q.name == "reference.json"
            else "illustration",
            "provenance": "symbolic-protocol"
            if q.name == "fixture.json"
            else "source-derived-teaching",
        }
        for q in sorted(a.output.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-automedbench-full-lidc-idri-denoising-task-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "LicenseRef-AutoMedBench-LIDC-IDRI-symbolic-teaching",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "reader-reference-reveal",
            "sources": {str(rp.relative_to(a.root)): sha(rp), str(bp.relative_to(a.root)): sha(bp)},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
