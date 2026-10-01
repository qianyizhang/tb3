"""Build representative input display and empty BM3D contract without running tool."""

import argparse
import hashlib
import io
import json
from pathlib import Path

ENTRY = "bcer-short-denoise"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    from PIL import Image

    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--preview", type=Path, required=True)
    ap.add_argument("--license", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    rpath = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bpath = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rpath.read_text())
    assert sha(bpath) == r["brief_sha256"]
    assert sha(a.preview) == r["representative_input"]["display_slice_png_sha256"]
    assert sha(a.license) == r["representative_input"]["data_license_sha256"]
    if a.output.exists():
        raise FileExistsError(a.output)
    a.output.mkdir(parents=True)
    image = Image.open(a.preview)
    assert image.size == (640, 640)
    image = image.resize((320, 320), Image.Resampling.BILINEAR)
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=70, optimize=False, progressive=False)
    raw = buf.getvalue()
    assert len(raw) < 65536

    def put(n, v):
        (a.output / n).write_text(json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n")

    source = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
            "representative_input",
        ]
    }
    source["display_derivative"] = {
        "from": "retained640x640PNG",
        "to": [320, 320],
        "resize": "bilinear",
        "encoding": "JPEGquality70",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "tool_output": False,
    }
    source["notice"] = {
        "label": "Representative helper; matched BM3D input/output absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official PI-CAI acquisition",
    }
    put("source.json", source)
    (a.output / "source-preview.jpeg").write_bytes(raw)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "stages": ["wholevolume normalization", "sigma units", "slice filter/geometry"],
            "sigma_default": 0.08,
            "actual_tool_run": False,
        },
    )
    put(
        "output.json",
        {
            "denoised_nifti": None,
            "actual_image": None,
            "elapsed_seconds": None,
            "quality_score": None,
        },
    )
    (a.output / "DATA-LICENSE.txt").write_bytes(a.license.read_bytes())
    (a.output / "NOTICE.md").write_text(
        "PI-CAI public training/development release, Zenodo 6624726, PI-CAI dataset authors, CC BY-NC 4.0. Representative 10001_1000001 T2w helper; not a matched BCER short case or clean target. Native k=10 (zero-based) display window 15-829; 320-square bilinear JPEG quality 70 display derivative. BCER tool code MIT is separate from the image license. No actual filter, clean reference, clinical finding or publication. "
        + r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\n"
    )
    assets = [
        {
            "file": x.name,
            "bytes": x.stat().st_size,
            "sha256": sha(x),
            "role": "reader-reference-reveal"
            if x.name == "reference.json"
            else "input-preview"
            if x.name == "source-preview.jpeg"
            else "illustration",
            "provenance": "symbolic-protocol"
            if x.name == "fixture.json"
            else "source-derived-teaching",
        }
        for x in sorted(a.output.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-bcer-denoise-source-v1",
            "frame": "native-k10-display-and-symbolic-contract",
            "units": "arbitrary-MRI-intensity-and-normalized-sigma",
            "license": "CC-BY-NC-4.0",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(rpath.relative_to(a.root)): sha(rpath),
                str(bpath.relative_to(a.root)): sha(bpath),
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
