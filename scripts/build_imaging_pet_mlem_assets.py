"""Import-safe native PET scaled-count display builder; no projection/reconstruction/evaluator."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-pet-mlem"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values):
    assert len(values) == 128 * 120
    pixels = bytes(c for v in values for c in [int(255 * min(max(v / 220, 0), 1))] * 3)

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    scan = b"".join(b"\0" + pixels[y * 360 : (y + 1) * 360] for y in range(128))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 120, 128, 8, 2, 0, 0, 0))
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
        assert len(data) == pin["bytes"] and hashlib.sha256(data).hexdigest() == pin["sha256"]
        if "git_blob" in pin:
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
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
        assert set(z.namelist()) == {"sinogram.npy", "background.npy", "theta.npy"}
        hs, ss = read_array(z, "sinogram")
        hb, bb = read_array(z, "background")
        ht, tt = read_array(z, "theta")
        for h in [hs, hb]:
            assert h["shape"] == (1, 128, 120) and h["descr"] == "<f4"
        assert ht["shape"] == (1, 120) and ht["descr"] == "<f4"

        def rows(h, data):
            values = [v[0] for v in struct.iter_unpack("<f", data)]
            if h["fortran_order"]:
                values = [values[y + x * 128] for y in range(128) for x in range(120)]
            assert len(values) == 15360
            return values

        sino = rows(hs, ss)
        background = rows(hb, bb)
        theta = [v[0] for v in struct.iter_unpack("<f", tt)]
        assert theta == [1.5 * i for i in range(120)] and len(set(background)) == 1
        (a.output / "sinogram.png").write_bytes(raster(sino))
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
        "label": "Synthetic measurements; outcome absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_profiles"] = {
        "indices": [0, 60, 119],
        "angles_deg": [theta[i] for i in [0, 60, 119]],
        "values": [[sino[y * 120 + i] for y in range(128)] for i in [0, 60, 119]],
        "background": background[0],
        "source_sha256": sha(a.raw_data),
        "shape": [1, 128, 120],
        "units": "Poisson counts divided by 1000; radial index, angle degrees",
        "PNG_formula": "floor 255*clip(float64(y)/220,0,1), grayscale",
        "PNG_pixels": [128, 120],
        "projection_or_reconstruction_executed": False,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "Poisson count scaling and additive background",
                "native observed profiles and uniform background",
                "source multiplicative MLEM/OSEM rules",
            ],
            "native_reconstruction": None,
            "fitting_or_evaluator_executed": False,
        },
    )
    put(
        "output.json",
        {
            "path": "output/reconstruction.npy",
            "domain": "One real 128x128 relative-activity array; no calibrated clinical uptake",
            "scorer_route": r["task_contract"]["scorer_route"],
            "reconstruction_npy": None,
            "actual_image": None,
            "quality_score": None,
            "task_outcome": None,
        },
    )
    (a.output / "SOURCE-LICENSE.txt").write_bytes(a.source_license.read_bytes())
    (a.output / "DATA-LICENSE.txt").write_text(
        "Imaging101 code/HF card declare MIT. Synthetic phantom projection measurements, not patient PET. Native sinogram/profile derivatives only, no activity/reference image or reconstruction. Full source license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nGray native scaled counts on fixed 0..220 scale; teal observed profile and gray background. Angles 0/90/178.5 degrees, radial indices. No projection, reconstruction, uptake or metric execution.\n"
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
            "id": "retained-imaging101-pet-mlem-source-v1",
            "frame": "PET-native-scaled-count-sinogram-plus-symbolic-update",
            "units": "radial-index, angle-degrees, counts/1000; relative activity",
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
