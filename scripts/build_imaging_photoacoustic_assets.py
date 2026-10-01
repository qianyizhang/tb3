"""Import-safe native acoustic display builder; no FFT/reconstruction/evaluator."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-photoacoustic-tomography"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values):
    assert len(values) == 31 * 1301
    pixels = bytearray()
    for v in values:
        q = int(255 * (1 - min(abs(v) / 0.1, 1)))
        pixels.extend((255, q, q) if v >= 0 else (q, q, 255))

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    scan = b"".join(b"\0" + pixels[y * 3903 : (y + 1) * 3903] for y in range(31))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1301, 31, 8, 2, 0, 0, 0))
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
        assert set(z.namelist()) == {
            "signals.npy",
            "detector_x.npy",
            "detector_y.npy",
            "time_vector.npy",
        }
        h, data = read_array(z, "signals")
        assert h["shape"] == (1, 1301, 31, 31) and h["descr"] == "<f8"
        values = [v[0] for v in struct.iter_unpack("<d", data)]
        assert len(values) == 1250261

        def value(t, x, y):
            return (
                values[t + x * 1301 + y * 1301 * 31]
                if h["fortran_order"]
                else values[t * 961 + x * 31 + y]
            )

        ht, td = read_array(z, "time_vector")
        assert ht["shape"] == (1, 1301) and ht["descr"] == "<f8"
        times = [v[0] for v in struct.iter_unpack("<d", td)]
        coords = []
        for name in ["detector_x", "detector_y"]:
            hc, cd = read_array(z, name)
            assert hc["shape"] == (1, 31) and hc["descr"] == "<f8"
            coords.append([v[0] for v in struct.iter_unpack("<d", cd)])
        indices = [(15, 15), (0, 15), (15, 0)]
        profiles = [[value(t, x, y) for t in range(1301)] for x, y in indices]
        (a.output / "signals.png").write_bytes(
            raster([value(t, x, 15) for x in range(31) for t in range(1301)])
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
        "label": "Synthetic acoustics; outcome absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_profiles"] = {
        "indices": indices,
        "detector_xy_mm": [[coords[0][x] * 1000, coords[1][y] * 1000] for x, y in indices],
        "values": profiles,
        "dt_seconds": times[1] - times[0],
        "time_last_seconds": times[-1],
        "source_sha256": sha(a.raw_data),
        "shape": [1, 1301, 31, 31],
        "units": "signed relative pressure; seconds and metres",
        "PNG_formula": "fixed ±.1 a.u.; positive red, negative blue, zero white; floor255*(1-min(abs(p)/.1,1)) neutral channels",
        "PNG_pixels": [31, 1301],
        "PNG_slice": "detector_y index15; x rows/time columns, no resize/decimation",
        "projection_or_reconstruction_executed": False,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "pressure geometry and time of flight",
                "native signed detector time traces",
                "signed derivative and solid-angle normalization",
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
        "Imaging101 code/HF card declare MIT. Synthetic sphere acoustic measurements only, not patient tissue or calibrated pressure. Native slice and trace derivatives, no truth or reconstructed image. Full source license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nBlue negative / red positive pressure on fixed ±.1 a.u. scale; teal native trace and gray zero. Exact center-y slice 31 x 1301, no filtering/FFT/reconstruction/evaluator.\n"
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
            "id": "retained-imaging101-photoacoustic-tomography-source-v1",
            "frame": "photoacoustic-native-time-detector-slice-plus-symbolic-backprojection",
            "units": "seconds, metres; signed relative pressure",
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
