"""Import-safe native k-space sample display builder; no Fourier, model or scorer execution."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-mri-varnet"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values):
    assert len(values) == 160 * 92
    ceiling = math.log1p(0.006 / 1e-5)
    pixels = bytes(
        c for v in values for c in [int(255 * min(math.log1p(v / 1e-5) / ceiling, 1))] * 3
    )

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    scan = b"".join(b"\0" + pixels[y * 92 * 3 : (y + 1) * 92 * 3] for y in range(160))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 92, 160, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scan, 9))
        + chunk(b"IEND", b"")
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--raw-data", type=Path, required=True)
    ap.add_argument("--source-license", type=Path, required=True)
    ap.add_argument("--saved-mask", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    for pin in r["source_files"]:
        data = (a.source_root / pin["path"]).read_bytes()
        assert len(data) == pin["bytes"]
        assert hashlib.sha256(data).hexdigest() == pin["sha256"]
        if "git_blob" in pin:
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == pin["git_blob"]
            )
    t = r["source_transport"]
    assert sha(a.source_root / t["path"]) == t["sha256"]
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
        assert set(z.namelist()) == {"kspace_real.npy", "kspace_imag.npy"}
        hr, real = read_array(z, "kspace_real")
        hi, imag = read_array(z, "kspace_imag")
        for h in [hr, hi]:
            assert h["shape"] == (1, 15, 640, 368) and h["descr"] == "<f4"
        assert len(real) == len(imag) == 3532800 * 4

        def scalar(data, h, c, y, x):
            index = c + 15 * y + 15 * 640 * x if h["fortran_order"] else (c * 640 + y) * 368 + x
            return struct.unpack_from("<f", data, index * 4)[0]

        for c in [0, 7, 14]:
            values = [
                math.hypot(scalar(real, hr, c, y, x), scalar(imag, hi, c, y, x))
                for y in range(0, 640, 4)
                for x in range(0, 368, 4)
            ]
            (a.output / f"kspace-{c}.png").write_bytes(raster(values))
    assert sha(a.saved_mask) == next(
        v["sha256"] for v in r["source_files"] if v["path"].endswith("/mask.npy")
    )
    raw = a.saved_mask.read_bytes()
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    assert h["shape"] == (1, 368, 1) and h["descr"] == "<f4"
    mask = [int(v[0]) for v in struct.iter_unpack("<f", raw[10 + length :])]
    assert mask == [int(i % 4 == 2 or 170 <= i < 199) for i in range(368)] and sum(mask) == 113
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
        "label": "Checkpoint absent; input preview only",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_mask"] = mask
    source["kspace_display"] = {
        "coils": [0, 7, 14],
        "source_sha256": sha(a.raw_data),
        "members": ["kspace_real.npy", "kspace_imag.npy"],
        "stride": 4,
        "pixels": [160, 92],
        "frame": "native frequency-array row/column indices, no spatial image",
        "units": "relative source k-space amplitude; no physical calibration",
        "formula": "floor255*min(log1p(hypot(real,imag)/1e-5)/log1p(.006/1e-5),1)",
        "phase_preserved": False,
        "FFT_or_model_executed": False,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "complex encoding and orthonormal FFT convention",
                "native k-space samples and saved equispaced mask",
                "missing checkpoint and external learned model contract",
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
        "Code MIT; source fastMRI-derived data retained for local research/education. No publication or redistribution authorized by this packet. K-space magnitude subsamples only, no image reconstruction or patient/clinical claims. Preserve applicable upstream rights review before sharing.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nGray log-display k-space samples, fixed ceiling .006; phase lost. Every fourth native row/column, no averaging. Teal saved sampled columns, dark missing; no model, FFT or fresh task tensor.\n"
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
            "id": "retained-imaging101-varnet-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "LicenseRef-fastMRI-internal-research",
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
