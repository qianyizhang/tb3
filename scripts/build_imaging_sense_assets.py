"""Import-safe native sensitivity display builder; no Fourier, CG or scorer."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-mri-sense"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values):
    assert len(values) == 16384
    pixels = bytes(c for v in values for c in [int(255 * min(v / 0.16, 1))] * 3)

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    scan = b"".join(b"\0" + pixels[y * 384 : (y + 1) * 384] for y in range(128))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 128, 128, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scan, 9))
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
    transport = r["source_transport"]
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
        assert set(z.namelist()) == {
            n + ".npy"
            for n in [
                "masked_kspace_real",
                "masked_kspace_imag",
                "sensitivity_maps_real",
                "sensitivity_maps_imag",
                "undersampling_mask",
            ]
        }
        arrays = []
        for name in ["sensitivity_maps_real", "sensitivity_maps_imag"]:
            h, data = read_array(z, name)
            assert h["shape"] == (1, 128, 128, 8) and h["descr"] == "<f4"
            values = [v[0] for v in struct.iter_unpack("<f", data)]
            if h["fortran_order"]:
                values = [
                    values[y + x * 128 + c * 16384]
                    for y in range(128)
                    for x in range(128)
                    for c in range(8)
                ]
            arrays.append(values)
        for c in [0, 3, 7]:
            mag = [math.hypot(arrays[0][i * 8 + c], arrays[1][i * 8 + c]) for i in range(16384)]
            (a.output / f"sensitivity-{c}.png").write_bytes(raster(mag))
        h, data = read_array(z, "undersampling_mask")
        assert h["shape"] == (128,) and h["descr"] == "|u1"
        mask = list(data)
        assert set(mask) == {0, 1} and sum(mask) == 54
        assert mask == [int(i % 3 == 0 or 56 <= i < 72) for i in range(128)]
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
        "label": "Synthetic maps; loader/R mismatch",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_mask"] = mask
    source["sensitivity_display"] = {
        "coils": [0, 3, 7],
        "shape": [1, 128, 128, 8],
        "source_sha256": sha(a.raw_data),
        "members": ["sensitivity_maps_real.npy", "sensitivity_maps_imag.npy"],
        "pixels": [128, 128],
        "formula": "floor255*min(hypot(float64(real),float64(imag))/.16,1), grayscale",
        "units": "relative source sensitivity amplitude, no physical calibration",
        "phase_preserved": False,
        "reconstruction": False,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "complex coil encoding",
                "native supplied maps and R3 sampling",
                "CG normal equations and scaled inverse helper",
            ],
            "native_reconstruction": None,
            "model_or_FFT_executed": False,
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
        "Imaging101 code/HF card declare MIT. Synthetic Shepp-Logan/Gaussian-map source. Native map-magnitude derivatives only; no patient image, reconstruction or inference. Full source license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nGray native map magnitude, fixed .16 ceiling; phase lost. Teal sampled rows; dark missing. Native indices not physical geometry. No FFT or CG.\n"
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
            "id": "retained-imaging101-sense-source-v1",
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
