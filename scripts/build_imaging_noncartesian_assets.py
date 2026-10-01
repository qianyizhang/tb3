"""Import-safe native trajectory display builder; no NUFFT/reconstruction/evaluator."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-mri-noncartesian-cs"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    assert not h["fortran_order"]
    return h, raw[10 + length :]


def raster(points):
    pixels = bytearray([18, 41, 57] * 256 * 256)
    for i in range(8, 249):
        for y, x in [(128, i), (i, 128)]:
            pixels[(y * 256 + x) * 3 : (y * 256 + x) * 3 + 3] = bytes([82, 99, 115])
    for c0, c1 in points:
        x = int(8 + (c1 + 64) * 240 / 128)
        y = int(8 + (64 - c0) * 240 / 128)
        assert 0 <= x < 256 and 0 <= y < 256
        pixels[(y * 256 + x) * 3 : (y * 256 + x) * 3 + 3] = bytes([87, 209, 204])

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 256, 256, 8, 2, 0, 0, 0))
        + chunk(
            b"IDAT",
            zlib.compress(
                b"".join(b"\0" + pixels[y * 256 * 3 : (y + 1) * 256 * 3] for y in range(256)), 9
            ),
        )
        + chunk(b"IEND", b"")
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--raw-data", type=Path, required=True)
    ap.add_argument("--source-license", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    for pin in r["source_files"]:
        raw = (a.source_root / pin["path"]).read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Stale source bytes: " + pin["path"])
        if "git_blob" in pin:
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != pin["git_blob"]:
                raise ValueError("Stale source Git blob: " + pin["path"])
    for transport in r["source_transport"]:
        raw = (a.source_root / transport["path"]).read_bytes()
        if len(raw) != transport["bytes"] or hashlib.sha256(raw).hexdigest() != transport["sha256"]:
            raise ValueError("Stale official transport")
    assert sha(a.raw_data) == next(
        v["sha256"] for v in r["source_files"] if v["path"].endswith("raw_data.npz")
    )
    assert sha(a.source_license) == next(
        v["sha256"] for v in r["source_files"] if v["path"].endswith("/LICENSE")
    )
    if a.output.exists():
        raise FileExistsError(a.output)
    a.output.mkdir(parents=True)

    def put(n, v):
        (a.output / n).write_text(json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n")

    with zipfile.ZipFile(a.raw_data) as z:
        h, data = read_array(z, "coord")
        assert h["shape"] == (1, 8192, 2) and h["descr"] == "<f4"
        pairs = list(struct.iter_unpack("<ff", data))
        assert len(pairs) == 8192
    points = [list(pairs[i]) for i in range(0, 8192, 16)]
    (a.output / "trajectory.png").write_bytes(raster(points))
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
        "label": "Synthetic phantom; outcome/calibration absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["trajectory"] = {
        "source_sha256": sha(a.raw_data),
        "member": "coord.npy",
        "native_shape": [1, 8192, 2],
        "stride": 16,
        "points": points,
        "frame": "coord0/coord1 NUFFT image-grid scaling",
        "units": "grid-sample indices; cycles/pixel requires division by 128",
        "plot_map": "x=8+(coord1+64)*240/128; y=8+(64-coord0)*240/128; uint floor",
        "pixels": [256, 256],
        "raster_role": "source-coordinate diagram, not patient image/reconstruction",
        "time_units": None,
        "full_points_per_spoke": 128,
        "display_points_per_spoke": 8,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "trajectory/frame/coils",
                "NUFFT and density compensation",
                "unweighted complex data consistency plus wavelet prior",
            ],
            "DCF": None,
            "native_NUFFT_executed": False,
        },
    )
    put(
        "output.json",
        {
            "reconstruction_npy": None,
            "actual_image": None,
            "quality_score": None,
            "task_outcome": None,
        },
    )
    (a.output / "SOURCE-LICENSE.txt").write_bytes(a.source_license.read_bytes())
    (a.output / "DATA-LICENSE.txt").write_text(
        "AI4ImagingLab Imaging101 source and HF dataset card declare MIT. Native coordinate data are synthetic Shepp-Logan/birdcage source, not patient MRI. Direct coordinate-diagram derivative plus original mathematical controls; no reconstruction/GT image/performance. Full code license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nCoordinates are 1-in-16 actual source samples, no interpolation. Gray axes guide only; teal actual display points. Views of 1/16/64 spokes change display, not acquisition or solver.\n"
    )
    assets = [
        {
            "file": q.name,
            "bytes": q.stat().st_size,
            "sha256": sha(q),
            "role": "input-preview"
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
            "id": "retained-imaging101-noncartesian-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "MIT",
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
