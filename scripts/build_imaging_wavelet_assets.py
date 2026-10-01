"""Import-safe MRI mask/k-space display builder; no FFT, reconstruction or evaluator."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
import zlib
from pathlib import Path

ENTRY = "imaging101-mri-l1-wavelet"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_array(z, name):
    raw = z.read(name + ".npy")
    assert raw[:8] == b"\x93NUMPY\x01\x00"
    n = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + n].decode())
    assert not h["fortran_order"]
    return h, raw[10 + n :]


def png(pixels):
    def chunk(n, b):
        return struct.pack(">I", len(b)) + n + b + struct.pack(">I", zlib.crc32(n + b))

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 320, 320, 8, 0, 0, 0, 0))
        + chunk(
            b"IDAT",
            zlib.compress(b"".join(b"\0" + pixels[y * 320 : (y + 1) * 320] for y in range(320)), 9),
        )
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
        raise ValueError("Stale official transport receipt")
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
        h, data = read_array(z, "masked_kspace")
        assert h["shape"] == (1, 15, 320, 320) and h["descr"] == "<c8"
        assert len(data) == 15 * 320 * 320 * 8
        mh, mb = read_array(z, "undersampling_mask")
        assert mh["shape"] == (320,) and mh["descr"] == "<f4"
        mask = list(struct.unpack("<320f", mb))
        assert set(mask) == {0.0, 1.0} and sum(mask) == 80
    derivatives = []
    for coil in [0, 7, 14]:
        values = list(
            struct.iter_unpack("<ff", data[coil * 320 * 320 * 8 : (coil + 1) * 320 * 320 * 8])
        )
        logs = [math.log1p(math.hypot(re, im)) for re, im in values]
        maximum = max(logs)
        pixels = bytes(int(v / maximum * 255) for v in logs)
        name = f"coil-{coil}.png"
        (a.output / name).write_bytes(png(pixels))
        derivatives.append(
            {
                "file": name,
                "coil_index": coil,
                "native_shape": [320, 320],
                "frame": "k-space row/last-axis phase-encode column indices; not patient image coordinates",
                "units": "arbitrary complex signal",
                "display": "uint8 truncation of 255*log1p(hypot(real,imag))/per-coil maximumlog",
                "maximumlog": maximum,
                "no_resize": True,
                "phase_shown": False,
                "FFT_or_reconstruction_executed": False,
                "source_sha256": sha(a.raw_data),
                "member": "masked_kspace.npy",
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
        "label": "README/assets/loader differ",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 MRI acquisition",
    }
    source["derivatives"] = derivatives
    source["native_mask"] = [int(v) for v in mask]
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "mask/coils/complex samples",
                "M F S forward model",
                "wavelet L1 complex shrinkage",
            ],
            "actual_reconstruction": None,
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
        "AI4ImagingLab source code and HF dataset card declare MIT. Released arrays metadata cites fastMRI knee; upstream fastMRI source rights/terms not independently established. Local noncommercial inspection only; no public redistribution permission asserted. K-space log-magnitude derivative is not a reconstruction/image/GT; full code license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nSource k-space coil displays preserve native 320-square frequency frame, separate grayscale display scale per coil. Metadata fastMRI file1000000.h5 slice 21; no patient-image orientation or physical spacing established. No outcome/GT image.\n"
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
            "id": "retained-imaging101-wavelet-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "LicenseRef-MIT-distribution-fastMRI-rights-unresolved",
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
