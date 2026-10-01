# ruff: noqa: RUF001 -- literal scientific display typography
"""Build representative input display and empty resampling contract without running tool."""

import argparse
import base64
import hashlib
import io
import json
import math
from pathlib import Path

ENTRY = "bcer-short-superres"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def derive_grid(size, spacing, target):
    """Authored pure illustration of the pinned ceil rule, never invokes BCER."""
    if not (len(size) == len(spacing) == len(target) == 3):
        raise ValueError("Three-axis illustration required")
    if any(not math.isfinite(x) or x <= 0 for x in [*size, *spacing, *target]):
        raise ValueError("Positive finite illustration grid required")
    return [math.ceil(n * s / t) for n, s, t in zip(size, spacing, target, strict=True)]


def verify_pins(root, receipt):
    for pin in (
        receipt["source_files"]
        + receipt["source_inputs"]
        + receipt["source_transport"]
        + receipt["retained_evidence"]
    ):
        path = Path(pin["path"])
        if not path.is_absolute():
            path = root / path
        raw = path.read_bytes()
        if sha(path) != pin["sha256"] or len(raw) != pin["bytes"]:
            raise ValueError(f"Stale source pin: {pin['path']}")
        if "git_blob" in pin:
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != pin["git_blob"]:
                raise ValueError(f"Stale Git blob: {pin['path']}")


def main():
    from PIL import Image

    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--preview", type=Path, required=True)
    ap.add_argument("--license", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    rpath = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bpath = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rpath.read_text())
    assert sha(bpath) == r["brief_sha256"]
    verify_pins(a.source_root, r)
    fixture = r["fixture"]
    assert fixture["derived_size"] == [
        derive_grid(fixture["input_size"], fixture["input_spacing"], target)
        for target in fixture["target_spacing"]
    ]
    assert fixture["rounded_spacing_example"]["derived_size"] == derive_grid(
        fixture["input_size"],
        fixture["input_spacing"],
        fixture["rounded_spacing_example"]["target"],
    )
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
    source["preview_data_uri"] = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
    source["display_derivative"] = {
        "from": "retained640x640PNG",
        "to": [320, 320],
        "resize": "bilinear",
        "encoding": "JPEGquality70",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "tool_output": False,
    }
    source["notice"] = {
        "label": "Representative input; no matched resampled output",
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
            "stages": ["source geometry", "target grid", "interpolation"],
            "identity_transform": True,
            "actual_tool_run": False,
        },
    )
    put(
        "output.json",
        {
            "resampled_nifti": None,
            "actual_image": None,
            "elapsed_seconds": None,
            "quality_score": None,
        },
    )
    (a.output / "DATA-LICENSE.txt").write_bytes(a.license.read_bytes())
    (a.output / "NOTICE.md").write_text(
        "PI-CAI dataset authors, public training/development release Zenodo 6624726, CC BY-NC 4.0. Representative 10001_1000001 T2w helper, not a matched BCER short case or HR/LR pair. Native k10 display window 15–829; 320-square bilinear JPEG quality-70 preview derivative. BCER code MIT is separate from image rights. No actual resampling, clean reference, clinical finding or publication. "
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
            "id": "retained-bcer-superres-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
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
