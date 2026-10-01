"""Import-safe native echo display builder; no fitting, operator or evaluator execution."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-mri-t2-mapping"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values):
    assert len(values) == 65536
    pixels = bytes(c for v in values for c in [int(255 * min(max(v, 0), 1))] * 3)

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
        data = (a.source_root / pin["path"]).read_bytes()
        assert len(data) == pin["bytes"]
        assert hashlib.sha256(data).hexdigest() == pin["sha256"]
        if "git_blob" in pin:
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == pin["git_blob"]
            )
    transport = r["source_transport"]
    assert sha(a.source_root / transport["path"]) == transport["sha256"]
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
        assert set(z.namelist()) == {"multi_echo_signal.npy"}
        h, data = read_array(z, "multi_echo_signal")
        assert h["shape"] == (1, 256, 256, 10) and h["descr"] == "<f4"
        values = [v[0] for v in struct.iter_unpack("<f", data)]
        assert len(values) == 655360
        for index, TE in [(0, 10), (4, 50), (9, 100)]:
            selected = (
                [values[y + x * 256 + index * 65536] for y in range(256) for x in range(256)]
                if h["fortran_order"]
                else [values[i * 10 + index] for i in range(65536)]
            )
            (a.output / f"echo-{TE}.png").write_bytes(raster(selected))
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
        "label": "Synthetic echoes; target ambiguity",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["echo_display"] = {
        "indices": [0, 4, 9],
        "TE_ms": [10, 50, 100],
        "shape": [1, 256, 256, 10],
        "member": "multi_echo_signal.npy",
        "source_sha256": sha(a.raw_data),
        "pixels": [256, 256],
        "formula": "floor255*clip(float64(signal),0,1), grayscale; same scale all echoes",
        "units": "signal a.u.; TE ms; image stored row/column",
        "per_echo_normalization": False,
        "fitting_or_model_executed": False,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "mono-exponential expectation and magnitude noise",
                "native selected echoes with shared display scale",
                "log-linear and unweighted LM contracts",
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
        "Imaging101 code/HF card declare MIT. Synthetic modified Shepp-Logan echo source, no patient scan. Direct echo-intensity derivatives only; no fitted T2 or truth map. Full source license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nGray magnitude signal a.u. fixed0..1;10/50/100ms echo times. No per-echo normalization/log/fitting. Native256x256 cells; above1 clipped only for display.\n"
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
            "id": "retained-imaging101-t2-mapping-source-v1",
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
