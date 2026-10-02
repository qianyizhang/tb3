"""Import-safe MRCT source/role/display builder; no FFT/reconstruction/evaluator."""

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

ENTRY = "automedbench-full-synthrad2025-mrct-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def native_display(raw):
    assert (
        hashlib.sha256(raw).hexdigest()
        == "79ebf8c0caa3d7f26a4501550bc2eb1975f153e67500f1cada504bce43c99a71"
    )
    mark = b"ElementDataFile = LOCAL\n"
    off = raw.index(mark) + len(mark)
    assert b"DimSize = 303 302 41\n" in raw[:off] and b"ElementType = MET_SHORT\n" in raw[:off]
    cells = zlib.decompress(raw[off:])
    assert len(cells) == 303 * 302 * 41 * 2
    plane = struct.unpack_from("<91506h", cells, 20 * 303 * 302 * 2)
    lo, hi = min(plane), max(plane)
    pixels = bytes(
        255 * (plane[j * 303 + i] - lo) // (hi - lo)
        for j in range(0, 302, 3)
        for i in range(0, 303, 3)
    )

    def chunk(kind, body):
        return (
            struct.pack(">I", len(body))
            + kind
            + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
        )

    rows = b"".join(b"\0" + pixels[j * 101 : (j + 1) * 101] for j in range(101))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">2I5B", 101, 101, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )
    return png, hashlib.sha256(pixels).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--native-volume", type=Path, required=True)
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    for pin in r["source_files"]:
        raw = (a.source_root / pin["path"]).read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Stale source bytes: " + pin["path"])
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
        "label": "Matching MR/mask/CT pair missing",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official SynthRAD MRCT acquisition",
    }
    source["symbolic_display"] = {
        "native_image": None,
        "pixel_parity": "not applicable: no native MR/CT pixels",
        "no_resizing_or_model": True,
    }
    png, pixel_sha = native_display(a.native_volume.read_bytes())
    assert pixel_sha == r["native_source_example"]["display"]["pixel_sha256"]
    (a.output / "upstream-mr-slice.png").write_bytes(png)
    source["upstream_example"] = r["native_source_example"]
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "MR and mask",
                "Same grid, new domain",
                "Tier and format",
                "Metric denominators",
            ],
            "native_synthesis": None,
            "evaluator_executed": False,
        },
    )
    put(
        "output.json",
        {"sct_volume": None, "actual_image": None, "quality_score": None, "task_outcome": None},
    )
    (a.output / "SOURCE-LICENSE.txt").write_text(
        "Official SynthRAD2025 training metadata: CC BY-NC4.0, Thummerer, van der Bijl, Galapon Jr., Kamp and Maspero, DOI10.5281/zenodo.15373853. https://creativecommons.org/licenses/by-nc/4.0/ . Upstream MR PNG CC BY-NC4.0, exact native k20 stride3 plane-local normalization; no model rights conveyed. Full release harness source pinned separately.\n"
    )
    (a.output / "DATA-LICENSE.txt").write_text(
        "LicenseRef-AutoMedBench-SynthRAD-MRCT-symbolic-teaching: authored unknown role cells and source-contract explanations. Separate upstream MR PNG CC BY-NC4.0, exact k20 stride3 display. No Full MRI/CT pair, private target or model result.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nTeal public MR role (arbitrary units), outlined synthetic CT socket (HU), gray private CT role (HU); no actual voxels or synthesis.\n"
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
            "id": "retained-automedbench-full-synthrad2025-mrct-task-source-v1",
            "frame": "upstream-MR-native-index-slice-plus-symbolic-Full-MRCT-roles",
            "units": "upstream MR arbitrary intensity; declared CT HU, no acquired CT",
            "license": "LicenseRef-AutoMedBench-SynthRAD-MRCT-symbolic-teaching",
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
