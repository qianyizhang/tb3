"""Import-safe native tooth raw-count display builder; no FFT/reconstruction/evaluator."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-xray-tooth-gridrec"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values, width, height):
    assert len(values) == width * height
    pixels = bytes(int(v) for v in values for _ in range(3))

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    scan = b"".join(b"\0" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scan, 9))
        + chunk(b"IEND", b"")
    )


def parse_npy(raw):
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    return ast.literal_eval(raw[10 : 10 + length].decode()), raw[10 + length :]


def f32(v):
    return struct.unpack("<f", struct.pack("<f", v))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--raw-data", type=Path, required=True)
    ap.add_argument("--source-license", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, default=Path.cwd())
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    for pin in r["source_files"]:
        raw = (a.source_root / pin["path"]).read_bytes()
        assert len(raw) == pin["bytes"] and hashlib.sha256(raw).hexdigest() == pin["sha256"]
        if "git_blob" in pin:
            assert (
                hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                == pin["git_blob"]
            )
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
        h, data = read_array(z, "projections")
        assert h["shape"] == (1, 181, 2, 640) and h["descr"] == "<f4" and not h["fortran_order"]
        values = [v[0] for v in struct.iter_unpack("<f", data)]
        assert len(values) == 231680
        low, high = min(values), max(values)
        span = high - low
        assert span > 0
        for row in range(2):
            preview = [
                int(255 * (values[(angle * 2 + row) * 640 + det] - low) / span)
                for angle in range(0, 181, 2)
                for det in range(0, 640, 4)
            ]
            (a.output / f"counts-row{row}.png").write_bytes(raster(preview, 160, 91))
        profiles = []
        for key in ["flat_field", "dark_field"]:
            h, data = read_array(z, key)
            assert h["shape"] == (1, 10, 2, 640) and h["descr"] == "<f4" and not h["fortran_order"]
            native = [v[0] for v in struct.iter_unpack("<f", data)]
            profiles.append({"key": key, "frame": 0, "row": 0, "values": native[:640]})
        h, data = read_array(z, "theta")
        assert h["shape"] == (1, 181) and h["descr"] == "<f8"
        angles = [v[0] for v in struct.iter_unpack("<d", data)]
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
        "label": "Tooth counts; calibration / output gaps",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_display"] = {
        "raw_sha256": sha(a.raw_data),
        "raw_min": low,
        "raw_max": high,
        "preview_pixels": [91, 160],
        "angle_stride": 2,
        "detector_stride": 4,
        "formula": "floor255*(native raw count-min)/(max-min), float64; common full input range",
        "units": "native raw detector counts, physical photon calibration unknown",
        "no_native_log_filter_inverse_or_reconstruction": True,
        "calibration_profiles": profiles,
        "angles_rad": angles,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "raw counts, flat/dark and log boundaries",
                "native two row displays and first calibration frames",
                "symbolic centre/filter and source FBP geometry",
            ],
            "native_reconstruction": None,
            "fitting_or_evaluator_executed": False,
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
        "Imaging101 source code MIT. Source README identifies APS beamline2-BM/32-ID tooth specimen, not patient identity. Original specimen acquisition/reuse rights/calibration unverified. LicenseRef-Imaging101-tooth-local-teaching is local restriction, not redistribution permission.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nGray=raw projection counts common minmax; angle/detector stride2/4. Teal/gray=first flat/dark frame counts, not stack means. No native log, centre fit, ramp FFT, backprojection, reconstruction or metric.\n"
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
            "id": "retained-imaging101-xray-tooth-gridrec-source-v1",
            "frame": "Tooth-native-detector-counts-plus-symbolic-correction-and-FBP",
            "units": "angle-radians, detector-index, raw-counts; dimensionless transmission rule only",
            "license": "LicenseRef-Imaging101-tooth-local-teaching",
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
