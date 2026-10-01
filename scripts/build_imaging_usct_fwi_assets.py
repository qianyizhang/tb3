"""Import-safe native complex observation display builder; no FFT/reconstruction/evaluator."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-usct-fwi"


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
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
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

    profiles = []
    ranges = []
    with zipfile.ZipFile(a.raw_data) as z:
        for key, name in [
            ("dobs_0.3", "observations-03.png"),
            ("dobs_0.8", "observations-08.png"),
            ("dobs_1.25", "observations-125.png"),
        ]:
            h, data = read_array(z, key)
            assert h["shape"] == (1, 256, 256) and h["descr"] == "<c8"
            values = list(struct.iter_unpack("<ff", data))
            assert len(values) == 65536
            if h["fortran_order"]:
                values = [values[y + x * 256] for y in range(256) for x in range(256)]
            scale = max(abs(v[0]) for v in values)
            assert scale > 0
            preview = [
                int(255 * (values[y * 256 + x][0] / scale + 1) / 2)
                for y in range(0, 256, 2)
                for x in range(0, 256, 2)
            ]
            (a.output / name).write_bytes(raster(preview, 128, 128))
            ranges.append(scale)
            profiles.append(
                {
                    "key": key,
                    "source_index": 0,
                    "receiver_indices": list(range(256)),
                    "real": [values[y * 256][0] for y in range(256)],
                    "imag": [values[y * 256][1] for y in range(256)],
                }
            )
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
        "label": "Phantom signals; truth / output absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_display"] = {
        "raw_sha256": sha(a.raw_data),
        "ranges": ranges,
        "preview_pixels": [128, 128],
        "stride": 2,
        "formula": "floor255*(native real/max_abs+1)/2 float64, every second receiver/source",
        "units": "uncalibrated complex observation amplitude",
        "no_wave_simulation_or_inversion": True,
        "profiles": profiles,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "source / receiver grid and complex frequency units",
                "native selected frequencies without a wave solve",
                "authored complex amplitude fit and NCG rules",
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
        "Imaging101 source code/HF card MIT. Source README identifies numerical breast phantom, not patient data. LicenseRef-Imaging101-USCT-local-teaching preserves local display restriction; no expanded rights.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nNative complex observation real component: black negative / midgray zero / white positive, separate per-frequency max-absolute scales; receiver/source stride2. No wave simulation, inversion, speed map or metric.\n"
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
            "id": "retained-imaging101-usct-fwi-source-v1",
            "frame": "USCT-native-complex-observation-cells-plus-symbolic-FWI",
            "units": "receiver-index, source-index, uncalibrated-complex-amplitude, MHz; speed m/s rule only",
            "license": "LicenseRef-Imaging101-USCT-local-teaching",
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
