"""Import-safe native mask/public-source display builder; no FFT/reconstruction/evaluator."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-pnp-mri-reconstruction"


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
    ap.add_argument("--mask", type=Path, required=True)
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

    assert sha(a.mask) == next(
        v["sha256"] for v in r["source_files"] if v["path"].endswith("sampling_mask.npy")
    )
    with zipfile.ZipFile(a.raw_data) as z:
        assert set(z.namelist()) == {"img.npy"}
        h, data = read_array(z, "img")
        assert h["shape"] == (1, 320, 320) and h["descr"] == "<f4"
        values = [v[0] for v in struct.iter_unpack("<f", data)]
        if h["fortran_order"]:
            values = [values[y + x * 320] for y in range(320) for x in range(320)]
        assert len(values) == 102400
        low, high = min(values), max(values)
        span = f32(high - low)
        assert span > 0
        preview = [
            int(255 * f32(f32(values[y * 320 + x] - low) / span))
            for y in range(0, 320, 2)
            for x in range(0, 320, 2)
        ]
        (a.output / "source-image.png").write_bytes(raster(preview, 160, 160))
    mh, md = parse_npy(a.mask.read_bytes())
    assert mh["shape"] == (320, 320) and mh["descr"] == "|b1"
    mask = list(md)
    if mh["fortran_order"]:
        mask = [mask[y + x * 320] for y in range(320) for x in range(320)]
    assert len(mask) == 102400 and set(mask) == {0, 1} and sum(mask) == 11766
    (a.output / "mask.png").write_bytes(raster([v * 255 for v in mask], 320, 320))
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
        "label": "Visible image; k-space / result absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_display"] = {
        "raw_sha256": sha(a.raw_data),
        "mask_sha256": sha(a.mask),
        "raw_min": low,
        "raw_max": high,
        "mask_count": 11766,
        "mask_pixels": [320, 320],
        "reference_preview_pixels": [160, 160],
        "reference_preview_stride": 2,
        "reference_formula": "float32 minmax then floor255*float64(norm), select every second native row/column",
        "source_image_is_visible_truth": True,
        "no_fourier_or_model_executed": True,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "source-visible image and generated-measurement boundary",
                "retained saved mask and unitary scaling",
                "PGM clipping then unknown denoiser",
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
        "Imaging101 code/HF card MIT. Upstream fastMRI image and MSSN/BSD500 checkpoint reuse rights not independently verified. LicenseRef-fastMRI-MSSN-local-teaching is local restriction, not redistribution permission. Source image equals visible truth, displayed late only; no reconstruction.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nWhite/black source-saved mask cells, no new generation. Public source image minmax/stride2 derivative later only, no acquired k-space, FFT, denoising or metric.\n"
    )
    assets = [
        {
            "file": q.name,
            "bytes": q.stat().st_size,
            "sha256": sha(q),
            "role": "reader-reference-reveal"
            if q.name == "source-image.png"
            else "input-preview"
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
            "id": "retained-imaging101-pnp-mri-reconstruction-source-v1",
            "frame": "PnP-MRI-native-mask-plus-reader-source-image-and-symbolic-PGM",
            "units": "native-image-index, normalized-intensity, mask-bit; physical calibration absent",
            "license": "LicenseRef-fastMRI-MSSN-local-teaching",
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
