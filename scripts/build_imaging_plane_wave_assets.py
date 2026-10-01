"""Import-safe native RF display builder; no FFT/reconstruction/evaluator."""

import argparse
import ast
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-plane-wave-ultrasound"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, n):
    raw = z.read(n + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    length = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + length].decode())
    return h, raw[10 + length :]


def raster(values, height):
    assert len(values) == height * 128 and all(v == int(v) and 0 <= v <= 255 for v in values)
    pixels = bytes(int(v) for v in values for _ in range(3))

    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    scan = b"".join(b"\0" + pixels[y * 384 : (y + 1) * 384] for y in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 128, height, 8, 2, 0, 0, 0))
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

    arrays = {}
    profiles = []
    with zipfile.ZipFile(a.raw_data) as z:
        assert set(z.namelist()) == {"RF_fibers.npy", "RF_cysts.npy"}
        for phantom, nt in [("fibers", 2688), ("cysts", 1536)]:
            h, data = read_array(z, "RF_" + phantom)
            assert h["shape"] == (1, nt, 128, 7) and h["descr"] == "<f4"
            values = [v[0] for v in struct.iter_unpack("<f", data)]
            assert len(values) == nt * 128 * 7

            def value(t, element, angle, values=values, nt=nt, h=h):
                return (
                    values[t + nt * element + nt * 128 * angle]
                    if h["fortran_order"]
                    else values[t * 896 + element * 7 + angle]
                )

            (a.output / ("rf-" + phantom + ".png")).write_bytes(
                raster([value(t, x, 3) for t in range(0, nt, 8) for x in range(128)], nt // 8)
            )
            arrays[phantom] = {"values": values, "mean": sum(values) / len(values)}
            for angle in [0, 3] if phantom == "fibers" else [3]:
                profiles.append(
                    {
                        "phantom": phantom,
                        "element": 63,
                        "angle_index": angle,
                        "angle_deg": [-1.5, -1, -0.5, 0, 0.5, 1, 1.5][angle],
                        "t0_seconds": 0 if phantom == "fibers" else 5e-5,
                        "values": [value(t, 63, angle) for t in range(nt)],
                        "global_mean": arrays[phantom]["mean"],
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
        "label": "Phantom RF; B-mode absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    source["native_profiles"] = {
        "profiles": profiles,
        "source_sha256": sha(a.raw_data),
        "dt_seconds": 5e-8,
        "units": "raw unsigned ADC codes, seconds",
        "PNG_formula": "every eighth time row, all elements, angle 3; RGB ADC code repeated; fixed 0..255",
        "PNG_shapes": [[336, 128], [192, 128]],
        "no_dc_filter_hilbert_migration": True,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "RF channels, time origin and steering",
                "native RF traces before DC subtraction",
                "complex compounding before envelope",
            ],
            "native_reconstruction": None,
            "fitting_or_evaluator_executed": False,
        },
    )
    put(
        "output.json",
        {
            "path": "output/reconstruction.npy",
            "domain": "Either fibers2688x128 or cysts1536x128 real display-unit B-mode; no participant image",
            "scorer_route": r["task_contract"]["scorer_route"],
            "reconstruction_npy": None,
            "actual_image": None,
            "quality_score": None,
            "task_outcome": None,
        },
    )
    (a.output / "SOURCE-LICENSE.txt").write_bytes(a.source_license.read_bytes())
    (a.output / "DATA-LICENSE.txt").write_text(
        "Imaging101 code/HF card declare MIT. Original PICMUS/Garcia physical phantom acquisition rights not independently verified. LicenseRef-Ultrasound-phantom-local-teaching is a local-use restriction, not redistribution permission. Native RF subsets/traces only, no patient/reference/B-mode image.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nGray raw ADC 0..255; angle 0 degrees, stride 8 time display subset only. Teal full RF traces, gray source global mean. No DC, FFT, Hilbert, beamforming, compounding or evaluator executed.\n"
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
            "id": "retained-imaging101-plane-wave-ultrasound-source-v1",
            "frame": "Plane-wave-native-ADC-sheet-plus-symbolic-compounding",
            "units": "ADC-code, seconds, element-index, angle-degrees",
            "license": "LicenseRef-Ultrasound-phantom-local-teaching",
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
