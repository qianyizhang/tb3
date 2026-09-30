#!/usr/bin/env python3
"""Build an ABRA viewer teaching pack from a pinned LIDC CT ZIP, without launching a viewer."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import struct
import zlib
from pathlib import Path
from zipfile import ZipFile


ENTRY = "abra-viewer-control"
RECEIPT_KEY = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
TAGS = {
    (0x0002, 0x0010): "transfer_syntax", (0x0008, 0x0060): "modality",
    (0x0020, 0x000D): "study_uid", (0x0020, 0x000E): "series_uid",
    (0x0020, 0x0013): "instance_number", (0x0020, 0x0032): "image_position",
    (0x0028, 0x0002): "samples_per_pixel", (0x0028, 0x0004): "photometric",
    (0x0028, 0x0010): "rows", (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "spacing", (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0103): "pixel_representation", (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width", (0x0028, 0x1052): "intercept",
    (0x0028, 0x1053): "slope", (0x7FE0, 0x0010): "pixel_data",
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
        vr = raw[pos + 4:pos + 6].decode("ascii")
        long_vr = vr in LONG_VR
        head = 12 if long_vr else 8
        size = struct.unpack_from("<I" if long_vr else "<H", raw, pos + (8 if long_vr else 6))[0]
        if size == 0xFFFFFFFF or pos + head + size > len(raw):
            raise ValueError("unsupported DICOM element length")
        key = TAGS.get((group, element))
        if key:
            value = raw[pos + head:pos + head + size]
            if key == "pixel_data":
                tags[key] = value
                break
            tags[key] = (struct.unpack("<H", value)[0] if vr == "US" and size == 2
                         else value.decode("ascii").strip("\0 "))
        pos += head + size
    return tags


def png_gray8(width: int, height: int, pixels: bytes) -> bytes:
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data))
    scanlines = b"".join(b"\0" + pixels[y * width:(y + 1) * width] for y in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(scanlines, level=9)) + chunk(b"IEND", b""))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    root = next((p for p in Path(__file__).resolve().parents if (p / ".git").exists()), None)
    if root is None:
        raise RuntimeError("repository root unavailable")
    receipt = json.loads(a.receipt.read_text())
    if receipt["entry_id"] != ENTRY:
        raise ValueError("wrong source receipt")
    for pin in receipt["source_pins"]:
        raw = (root / pin.get("local_path", pin["path"])).read_bytes()
        if len(raw) != pin["bytes"] or sha(raw) != pin["sha256"]:
            raise ValueError(f"source pin mismatch: {pin['path']}")
        if pin.get("git_blob_sha"):
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != pin["git_blob_sha"]:
                raise ValueError(f"Git blob mismatch: {pin['path']}")
    out = a.output.resolve()
    if out.exists():
        raise FileExistsError(out)
    ct_path = root / "runs/task-brief-samples/abra/ct.zip"
    integrity = receipt["source_integrity"]
    with ZipFile(ct_path) as z:
        if z.testzip() is not None:
            raise ValueError("CT ZIP CRC failed")
        names = sorted(n for n in z.namelist() if n.endswith(".dcm"))
        if len(names) != 140 or len(z.namelist()) != 141:
            raise ValueError("CT archive membership changed")
        if sha(z.read("LICENSE")) != integrity["embedded_license_sha256"]:
            raise ValueError("embedded license changed")
        instances: set[int] = set()
        positions: set[str] = set()
        chosen = None
        for name in names:
            raw = z.read(name)
            info = parse_dicom(raw)
            if (info["study_uid"] != integrity["study_uid"] or
                info["series_uid"] != integrity["series_uid"] or
                info["transfer_syntax"] != "1.2.840.10008.1.2.1" or
                info["modality"] != "CT" or
                (info["rows"], info["columns"]) != (512, 512) or
                info["spacing"] != "0.820312\\0.820312" or
                (info["slope"], info["intercept"]) != ("1", "-1024") or
                (info["bits_allocated"], info["pixel_representation"],
                 info["samples_per_pixel"], info["photometric"]) != (16, 1, 1, "MONOCHROME2") or
                len(info["pixel_data"]) != 512 * 512 * 2):
                raise ValueError(f"unexpected DICOM source geometry: {name}")
            instances.add(int(str(info["instance_number"])))
            positions.add(str(info["image_position"]))
            if name == integrity["selected_member"]:
                if sha(raw) != integrity["selected_member_sha256"] or int(str(info["instance_number"])) != 80:
                    raise ValueError("selected member changed")
                chosen = info
        if len(instances) != 140 or instances != set(range(1, 141)) or len(positions) != 140 or chosen is None:
            raise ValueError("CT series identity changed")
    pixels = chosen["pixel_data"]
    center, width = float(str(chosen["window_center"])), float(str(chosen["window_width"]))
    slope, intercept = float(str(chosen["slope"])), float(str(chosen["intercept"]))
    grayscale = bytearray()
    for (stored,) in struct.iter_unpack("<h", pixels):
        hu = stored * slope + intercept
        value = ((hu - (center - 0.5)) / (width - 1.0) + 0.5) * 255.0
        grayscale.append(max(0, min(255, round(value))))
    png = png_gray8(512, 512, bytes(grayscale))
    out.mkdir(parents=True)
    (out / "source_preview.png").write_bytes(png)
    put_json(out / "source.json", {
        "role": "matched-source-DICOM-preview-plus-symbolic-viewer",
        "title": "ABRA viewer control — LIDC-IDRI-0003", "modality": "CT",
        "instance_count": 140, "initial_slice_index": 0,
        "study_uid": integrity["study_uid"], "series_uid": integrity["series_uid"],
        "preview": {"data_uri": "data:image/png;base64," + base64.b64encode(png).decode(),
                    "archive_member": integrity["selected_member"], "dicom_instance_number": 80,
                    "viewer_slice_index": None, "window_center_hu": center, "window_width_hu": width,
                    "native_rows": 512, "native_columns": 512,
                    "pixel_spacing_mm": [0.820312, 0.820312]},
        "viewer_index_mapping_verified": False, "observed_viewport": None,
        "notice": {"label": "Matched source CT; symbolic viewer state",
                   "text": receipt["top_warning"], "url": receipt["acquisition_route"],
                   "link_label": "Official LIDC-IDRI source"},
    })
    put_json(out / "operation.json", {
        "type": "viewport-state-control", "variant": "slice navigation",
        "target_formula": "num_instances // 2", "target_slice_index": 70,
        "input_action": "set_viewport_slice(slice_index=70) — hypothetical, never called",
        "state_key": "sliceIndex", "candidate_min": 0, "candidate_max": 139,
        "sample_status": "Prompt-visible target derived statically from pinned generator and matched manifest; no OHIF action.",
        "source_member_is_not_viewer_index": True,
        "other_variants": ["window-level", "slice navigation", "slice+window", "series selection"],
        "window_example": {"window_width": 2500, "window_center": 480, "tolerance": 1.0},
    })
    put_json(out / "output.json", {
        "role": "required-state-schema-only", "path": "OHIF final viewport state",
        "schema": {"sliceIndex": "requested 70; observed value absent"},
        "requested_state": {"sliceIndex": 70}, "observed_state": None,
        "prediction": None, "score": None, "reference": None,
        "comparison": "Source rule compares present fields; no scorer run or verified viewer ordering.",
    })
    (out / "NOTICE.md").write_text(receipt["top_warning"] + "\n" + receipt["acquisition_route"] + "\n")
    citation_source = root / ".local/explainers/core-20260929/abra-viewer-refined-prep-v1/official-page-evidence/collection.plain.txt"
    official_text = citation_source.read_text()
    citation_start = official_text.index("Data Citation Armato III") + len("Data Citation ")
    citation_end = official_text.index("Acknowledgement", citation_start)
    dataset_citation = official_text[citation_start:citation_end].strip()
    if not (dataset_citation.startswith("Armato III, S. G.") and
            dataset_citation.endswith("https://doi.org/10.7937/K9/TCIA.2015.LO9QL9SX")):
        raise ValueError("official dataset citation changed")
    (out / "DATA-LICENSE.txt").write_text(
        "ABRA generator/scorer text: MIT, pinned Luab/ABRA commit 688814615dc368a66276798cb864fe9a587d7e6c.\n"
        "CT dataset citation, extracted exactly from retained official TCIA collection page: " + dataset_citation + "\n"
        "Collection and full official citation: https://www.cancerimagingarchive.net/collection/lidc-idri/\n"
        "CT license: Creative Commons Attribution 3.0 Unported (CC BY 3.0), https://creativecommons.org/licenses/by/3.0/\n"
        "The collection requests acknowledgement of the National Cancer Institute and the Foundation for the National Institutes of Health in publications or grant applications, with references to relevant LIDC publications; use the exact official wording at the collection page.\n"
        "Source archive runs/task-brief-samples/abra/ct.zip contains original LICENSE. Follow TCIA Data Usage Policy and Restrictions: https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/\n"
        "Preview is a windowed derivative of archive member 00000001.dcm (DICOM InstanceNumber 80), not an OHIF viewport capture or index mapping. No annotation included.\n"
    )
    assets = []
    for path in sorted(out.iterdir()):
        raw = path.read_bytes()
        assets.append({"file": path.name, "bytes": len(raw), "sha256": sha(raw),
                       "role": "input-preview" if path.name == "source_preview.png" else "illustration",
                       "provenance": "source-derived" if path.name in {"source_preview.png", "source.json"} else "source-derived-teaching"})
    put_json(out / "manifest.json", {
        "id": "retained-abra-viewer-control-workflow-v1",
        "frame": "LIDC-IDRI-0003-DICOM-LPS-plus-symbolic-viewport",
        "units": "mm and zero-based viewer index",
        "license": "LicenseRef-ABRA-MIT-plus-LIDC-IDRI-CC-BY-3.0-TCIA",
        "label_license": None, "reference_policy": "no-reference-assets",
        "checks": {"native_input": True, "private_reference": False,
                   "model_run": False, "evaluator_run": False, "viewer_run": False},
        "sources": {RECEIPT_KEY: sha(a.receipt.read_bytes())}, "assets": assets,
    })


if __name__ == "__main__":
    main()
