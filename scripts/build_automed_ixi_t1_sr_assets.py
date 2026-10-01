"""Import-safe symbolic IXI geometry/contract builder; no FFT/reconstruction/evaluator."""

import argparse
import gzip
import hashlib
import json
import struct
import zlib
from pathlib import Path

ENTRY = "automedbench-full-ixi-t1-sr-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def native_display(raw):
    n = gzip.decompress(raw)
    assert len(n) == 19661152 and struct.unpack_from("<i", n)[0] == 348
    assert struct.unpack_from("<8h", n, 40) == (3, 256, 256, 150, 1, 1, 1, 1)
    assert struct.unpack_from("<2h", n, 70) == (4, 16)
    assert struct.unpack_from("<3f", n, 108) == (352.0, 1.0, 0.0)
    plane = struct.unpack_from("<65536h", n, 352 + 75 * 65536 * 2)
    lo, hi = min(plane), max(plane)
    pixels = bytes(
        255 * (plane[j * 256 + i] - lo) // (hi - lo)
        for j in range(0, 256, 2)
        for i in range(0, 256, 2)
    )

    def chunk(kind, body):
        return (
            struct.pack(">I", len(body))
            + kind
            + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
        )

    rows = b"".join(b"\x00" + pixels[j * 128 : (j + 1) * 128] for j in range(128))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">2I5B", 128, 128, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )
    return png, {
        "plane_min": lo,
        "plane_max": hi,
        "native_k": 75,
        "sampled_cells": 16384,
        "source_plane_cells": 65536,
        "pixel_sha256": hashlib.sha256(pixels).hexdigest(),
        "display_sha256": hashlib.sha256(png).hexdigest(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, default=None)
    ap.add_argument("--native-volume", type=Path, required=True)
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
    raw = a.native_volume.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == r["native_source_example"]["member_sha256"]
    png, display = native_display(raw)
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
        "label": "Matching MRI / target missing",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official IXI acquisition",
    }
    source["symbolic_display"] = {
        "native_image": None,
        "low_cells": 4,
        "high_cells": 16,
        "native_pixel_parity": "default symbolic; separately late upstream source-example display exactly verified",
        "no_resizing_or_model": True,
    }
    source["upstream_example"] = {**r["native_source_example"], "verified_display": display}
    (a.output / "upstream-t1-slice.png").write_bytes(png)
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "128→256 shape and information boundary",
                "Full Lite / Standard help and format checker",
                "unknown high-resolution output values",
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
    (a.output / "SOURCE-LICENSE.txt").write_text(
        "Release-owned Full harness source pinned by archive/member SHA; no original clinical data or model license is conveyed. Upstream IXI CC BY-SA3.0: IXI - Information eXtraction from Images (EPSRC GR/S21533/02), https://brain-development.org/ixi-dataset/. Derived native k75 stride2 grayscale display only, no registration or reconstruction. https://creativecommons.org/licenses/by-sa/3.0/\n"
    )
    (a.output / "DATA-LICENSE.txt").write_text(
        "LicenseRef-AutoMedBench-IXI-symbolic-teaching: authored illustrative pixel values and geometry only; no patient image, private target, model or metric. Upstream example PNG CC BY-SA3.0, task targets separate.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nTeal authored low-resolution cells; outlined high-resolution cells unknown. Not MRI, resized result, private reference or clinical outcome.\n"
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
            "id": "retained-automedbench-full-ixi-t1-sr-task-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "LicenseRef-AutoMedBench-IXI-symbolic-teaching",
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
