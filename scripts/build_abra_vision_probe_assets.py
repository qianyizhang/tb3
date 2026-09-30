#!/usr/bin/env python3
"""Derive native matched-source CT examples; no viewer/task/runtime execution."""

from __future__ import annotations

import argparse
import base64
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


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def put_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


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


def f32(v: float) -> float:
    return struct.unpack("<f", struct.pack("<f", v))[0]


def window_bytes(pixels: bytes, center: float, width: float) -> bytes:
    low = center - width / 2
    high = center + width / 2
    return bytes(
        int(f32(f32(f32(max(low, min(high, stored - 1024)) - low) / width) * 255))
        for (stored,) in struct.iter_unpack("<h", pixels)
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--fixture", type=Path, required=True)
    ap.add_argument("--license", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    rp = a.root / "presentation/external-tasks/sources/abra-vision-probe-resolution.json"
    r = json.loads(rp.read_text())
    brief = a.root / "presentation/external-tasks/briefs/abra-vision-probe.md"
    assert sha(brief.read_bytes()) == r["brief_sha256"]
    ex = r["source_example"]
    assert sha(a.archive.read_bytes()) == ex["archive_sha256"]
    assert sha(a.license.read_bytes()) == ex["licence_file_sha256"]
    integrity = ex["viewer_integrity"]
    records = []
    pixels_by_name = {}
    with ZipFile(a.archive) as z:
        assert z.testzip() is None
        names = sorted(n for n in z.namelist() if n.endswith(".dcm"))
        assert len(names) == 140 and len(z.namelist()) == 141
        assert sha(z.read("LICENSE")) == integrity["embedded_license_sha256"]
        for name in names:
            raw = z.read(name)
            d = parse_dicom(raw)
            pixels = d.pop("pixel_data")
            assert (
                d["study_uid"] == integrity["study_uid"]
                and d["series_uid"] == integrity["series_uid"]
            )
            assert d["transfer_syntax"] == "1.2.840.10008.1.2.1"
            assert (
                d["rows"],
                d["columns"],
                d["bits_allocated"],
                d["pixel_representation"],
                d["samples_per_pixel"],
                d["photometric"],
            ) == (512, 512, 16, 1, 1, "MONOCHROME2")
            assert (d["slope"], d["intercept"]) == ("1", "-1024")
            assert len(pixels) == 512 * 512 * 2
            ipp = list(map(float, str(d["image_position"]).split("\\")))
            iop = list(map(float, str(d["orientation"]).split("\\")))
            row = iop[:3]
            col = iop[3:]
            normal = [
                row[1] * col[2] - row[2] * col[1],
                row[2] * col[0] - row[0] * col[2],
                row[0] * col[1] - row[1] * col[0],
            ]
            key = sum(x * y for x, y in zip(ipp, normal, strict=True))
            records.append(
                {
                    "member": name,
                    "member_sha256": sha(raw),
                    "header_sha256": sha(raw[: -len(pixels)]),
                    "pixel_data_sha256": sha(pixels),
                    "CRC32": z.getinfo(name).CRC,
                    "tags": d,
                    "position_projection": key,
                }
            )
            pixels_by_name[name] = pixels
    records.sort(key=lambda x: x["position_projection"])
    assert len({x["position_projection"] for x in records}) == 140
    assert {int(x["tags"]["instance_number"]) for x in records} == set(range(1, 141))
    out = a.output
    out.mkdir(parents=True)
    previews = []
    for i in ex["indices"]:
        rec = records[i]
        entry = {
            "index": i,
            "member": rec["member"],
            "instance_number": int(rec["tags"]["instance_number"]),
            "sop_uid": rec["tags"]["sop_uid"],
            "image_position_lps_mm": list(
                map(float, str(rec["tags"]["image_position"]).split("\\"))
            ),
            "native_size": [512, 512],
            "pixel_spacing_mm": list(map(float, str(rec["tags"]["spacing"]).split("\\"))),
        }
        for name, c, width in [("lung", -600, 1500), ("soft", 40, 400)]:
            pix = window_bytes(pixels_by_name[rec["member"]], c, width)
            png = png_gray8(512, 512, pix)
            file = f"{name}-{i}.png"
            (out / file).write_bytes(png)
            entry[name] = {
                "file": file,
                "sha256": sha(png),
                "display_pixels_sha256": sha(pix),
                "center_HU": c,
                "width_HU": width,
                "data_uri": "data:image/png;base64," + base64.b64encode(png).decode(),
            }
        previews.append(entry)
    put_json(
        out / "previews.json",
        {
            "role": "source-example derivatives; not recovered generated task/control PNGs or reference",
            "instances": previews,
        },
    )
    put_json(
        out / "geometry.json",
        {
            "archive_sha256": ex["archive_sha256"],
            "native_size": [512, 512],
            "resampling": False,
            "source_roles_unchanged": r["source_roles"],
            "series_count": 1,
            "instance_count": 140,
            "study_uid": integrity["study_uid"],
            "series_uid": integrity["series_uid"],
            "sort": ex["sort"],
            "all_sorted_member_headers": records,
        },
    )
    source = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "illustration_basis",
            "source_roles",
            "task_contract",
            "source_commit",
        ]
    }
    source["notice"] = {
        "label": "Source CT examples; task PNG absent",
        "text": r["warning_text"],
        "url": "https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/README.md#2-download-datasets",
        "link_label": "Official ABRA setup",
    }
    put_json(out / "source.json", source)
    put_json(out / "fixture.json", json.loads(a.fixture.read_text()))
    put_json(
        out / "output.json",
        {
            "role": "Participant output absent",
            "participant_answer": None,
            "score": None,
            "actual_reference": None,
            "required_output": "submit_answer.arguments.answer string: A/B/C/D",
        },
    )
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n"
        + r["actual_data_gap"]
        + "\nNative CT source-example derivatives: no task identity, recovered sidecar, actual control/reference or clinical findings. Authored grid/control remains nonclinical.\n"
    )
    licence = a.license.read_text()
    licence = licence[: licence.index("Preview is a windowed derivative")]
    (out / "DATA-LICENSE.txt").write_text(
        licence
        + "Previews are independently derived selected-index CT examples using pinned ABRA window formula, not recovered sidecar or viewer captures. No annotation included.\n"
    )
    assets = [
        {
            "file": x.name,
            "bytes": x.stat().st_size,
            "sha256": sha(x.read_bytes()),
            "role": "input-preview"
            if x.suffix == ".png" or x.name == "previews.json"
            else "illustration",
            "provenance": "symbolic-protocol"
            if x.name == "fixture.json"
            else "source-derived-teaching",
        }
        for x in sorted(out.iterdir())
    ]
    put_json(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-abra-vision-probe-source-example-v3",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "CC-BY-3.0",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "no-reference-assets",
            "sources": {
                "presentation/external-tasks/sources/abra-vision-probe-resolution.json": sha(
                    rp.read_bytes()
                ),
                "presentation/external-tasks/briefs/abra-vision-probe.md": sha(brief.read_bytes()),
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
