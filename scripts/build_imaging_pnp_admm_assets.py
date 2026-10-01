"""Import-safe native binary-mask display builder; no Fourier, denoiser or scorer."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-mri-pnp-admm"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values):
    assert len(values) == 65536 and all(v in (0, 1) for v in values)
    pixels = bytes(c for v in values for c in ([87, 209, 204] if v else [18, 41, 57]))

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    scan = b"".join(b"\0" + pixels[y * 768 : (y + 1) * 768] for y in range(256))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 256, 256, 8, 2, 0, 0, 0))
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

    counts = []
    with zipfile.ZipFile(a.raw_data) as z:
        assert set(z.namelist()) == {
            n + ".npy"
            for n in ["mask_random", "mask_radial", "mask_cartesian", "noises_real", "noises_imag"]
        }
        for name in ["random", "radial", "cartesian"]:
            h, data = read_array(z, "mask_" + name)
            assert h["shape"] == (1, 256, 256) and h["descr"] == "<f4"
            values = [v[0] for v in struct.iter_unpack("<f", data)]
            if h["fortran_order"]:
                values = [values[y + x * 256] for y in range(256) for x in range(256)]
            counts.append(sum(values))
            (a.output / ("mask-" + name + ".png")).write_bytes(raster(values))
    assert counts == [19674, 19249, 19456]
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
        "label": "No measured k-space; metadata scale missing",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["masks"] = {
        "names": ["random", "radial", "cartesian"],
        "counts": counts,
        "source_sha256": sha(a.raw_data),
        "shape": [1, 256, 256],
        "dtype": "float32",
        "pixels": [256, 256],
        "frame": "stored unshifted Fourier array indices",
        "units": "index, no physical calibration",
        "palette": {"sampled": [87, 209, 204], "unsampled": [18, 41, 57]},
        "transform": "direct binary-cell mapping, no shift/resize/FFT",
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "synthesized observation and real initialization",
                "Fourier consistency and source masks",
                "residual denoiser and dual update",
            ],
            "learned_residual": None,
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
        "Imaging101 code/HF card declare MIT. Actual mask-only derivatives, no upstream Brain.jpg display. Brain image rights not separately verified. No reconstruction or inference. Full source license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nTeal sampled cells, dark unsampled. Native 256x256 stored indices; mask controls alter display only. No Fourier transform, noise synthesis or learned result.\n"
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
            "id": "retained-imaging101-pnp-admm-source-v1",
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
