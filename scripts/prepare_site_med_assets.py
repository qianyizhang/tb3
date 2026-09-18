#!/usr/bin/env python3
"""Export exact retained figures and Mermaid sources for the medical articles.

No model calls, image editing, source downloads, or frozen-artifact writes.
Run from any directory. --check verifies exports without writing.
"""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MED = ROOT / "site_med"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads((ROOT / path).read_text())


def prepare():
    exports = {}
    records = []

    def add(name, source, selector, data, attribution, terms, description, provenance):
        encoded = data.split(",", 1)[1] if data.startswith("data:image/png;base64,") else data
        blob = base64.b64decode(encoded, validate=True)
        if not blob.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(f"Not a PNG: {name}")
        path = f"assets/{name}.png"
        exports[path] = blob
        records.append({
            "id": name, "path": path, "kind": "retained scientific figure",
            "source_path": source, "source_selector": selector,
            "source_sha256": sha256((ROOT / source).read_bytes()),
            "sha256": sha256(blob), "bytes": len(blob),
            "derivation": "Exact base64 decoding; no image edits or resampling.",
            "attribution": attribution, "terms": terms,
            "caption": description, "alt": description,
            "model_exposure": "Author-created review material; not asserted to be an exact model input.",
            "provenance_path": provenance,
        })

    source = "site_med/data/segmentation_assets.js"
    raw = (ROOT / source).read_text()
    seg = json.loads(raw[raw.index("{"):].strip().removesuffix(";"))
    for state in ("before", "after"):
        add(f"segmentation-{state}", source, f"axial-{state}", seg[f"axial-{state}"],
            "TotalSegmentator contributors; TB3 author review", "CC BY 4.0",
            f"Axial CT with {state}-reassignment organ labels; CT is unchanged. One plane through a 3D transfer.",
            "probes/revisions/br017/authoring/README.md")

    source = "site/aneurysm-figures.json"
    case = read_json(source)["cases"]["n02"]
    plane = next(p for p in case["planes"] if p["axis"] == 2)
    add("aneurysm-n02", source, "cases.n02.planes[axis=2].image", plane["image"],
        "OpenNeuro ds003949 contributors; TB3 guided review", "CC0 source",
        "N02 reference-centered seven-slice brightness projection; overlapping vessels can obscure 3D shape.",
        "site/provenance.json")
    records[-1]["geometry"] = {k: v for k, v in plane.items() if k != "image"}

    source = "site/registration-figures.json"
    reg = read_json(source)
    index = reg["ids"].index("q04")
    for name, images, selector in (
        ("source", reg["source"], "source"),
        ("reference", reg["manual"], "manual"),
        ("agent", reg["methods"]["Sol / full 3D source"]["images"], "methods.Sol / full 3D source.images"),
    ):
        add(f"registration-q04-{name}", source, f"{selector}.Dataset XY[{index}]",
            images["Dataset XY"][index], "Learn2Reg LungCT contributors; TB3 review", "CC BY 4.0",
            f"q04 {name} neighborhood, centered on its own coordinate in the dataset XY plane. Not a shared-center displacement view.",
            "site/registration-provenance.json")

    source = "site/vessel-figures.json"
    add("airway-controls", source, "figures.airway", read_json(source)["figures"]["airway"],
        "AeroPath / Raidionics contributors; TB3 output review",
        "Downloaded source license.md: CC BY 4.0; mirror card: MIT. Preserve the recorded attribution and discrepancy.",
        "Terra airway outputs: A01 repaired; A02/A03 preserve internally connected fragments that remain detached from parent trees.",
        "site/vessel-provenance.json")

    source = "runs/br030-vessel-geometry/viewer-terra-arc-correction/cpr-preview.png"
    target = "assets/coronary-cpr.png"
    # The retained preview is local runtime material. A migrated publication can
    # verify the exported hash without acquiring or regenerating the full scan.
    if (ROOT / source).exists():
        blob = (ROOT / source).read_bytes()
    else:
        blob = (MED / target).read_bytes()
    expected = "f7017e754b0365d8dbe91e0a78614c050ab9d7b4a7820a7861111e8f570a2bb3"
    if sha256(blob) != expected:
        raise ValueError("Retained coronary preview differs from the reviewed source")
    exports[target] = blob
    records.append({"id": "coronary-cpr", "path": target,
        "kind": "retained scientific figure", "source_path": source,
        "source_sha256": expected, "sha256": expected, "bytes": len(blob),
        "derivation": "Exact copy of the author-corrected Terra viewer preview; display enlargement retained.",
        "attribution": "ImageCAS / ImageCAS-X contributors; Terra output; TB3 viewer",
        "terms": "Source declarations: ImageCAS Apache 2.0; ImageCAS-X CC BY 4.0. See source receipt.",
        "provenance_path": "docs/evidence/br030-sources.json",
        "caption": "Coronary CPR preview from the corrected package. Underlying sampled CT values are unchanged by the arc_mm correction; preview is not a uniform physical-scale display.",
        "alt": "A curved coronary CT plane displayed as a horizontal strip with a bright vessel interior.",
        "model_exposure": "Author-created preview of the submitted geometry after metadata correction."})

    source = "site/cardiac-figures.json"
    add("cardiac-comparison", source, "figure", read_json(source)["figure"],
        "STRAUS source contributors; TB3 independently scored scientific plot",
        "Authored plot of aggregate measurements; no ultrasound or source mesh redistribution. See source provenance.",
        "Left: synthetic wall volume; middle: separate clinical cavity transfer; right: synthetic engineering-strain error. Nearly overlapping curves reflect explicit volume matching.",
        "site/cardiac-provenance.json")

    source = "site/landmark-figures.json"
    case = next(c for c in read_json(source) if c["case"] == "ct-partial")
    for level in ("T4", "T5"):
        filename = f"ct-partial-{level}.png"
        add(f"landmark-{level.lower()}", source, f"ct-partial.images.{filename}", case["images"][filename],
            "VerSe contributors; TB3 per-landmark review", "CC BY-SA 4.0; derived illustration retains these terms",
            f"Cropped CT {level} comparison. T4 is outside the scan; T5 is visible and missed by Sol. Markers are projected; scores use 3D distances.",
            "site/landmark-provenance.json")

    for page in sorted(MED.glob("0[1-6]-*.md")):
        for number, match in enumerate(re.finditer(r"```mermaid\n(.*?)\n```", page.read_text(), re.S), 1):
            blob = (match.group(1) + "\n").encode()
            path = f"assets/diagrams/{page.stem}-{number}.mmd"
            exports[path] = blob
            records.append({"id": f"{page.stem}-{number}", "path": path,
                "kind": "conceptual workflow diagram", "source_path": f"site_med/{page.name}",
                "sha256": sha256(blob), "bytes": len(blob),
                "derivation": "Extracted from the authoritative Markdown Mermaid block.",
                "caption": "Conceptual task workflow, not patient anatomy or a recovered private reasoning trace.",
                "model_exposure": "Editorial illustration created after the experiments."})

    exports["assets/manifest.json"] = (json.dumps({
        "schema_version": 1, "path_base": "site_med", "source_path_base": "repository root",
        "rebuild": "python3 scripts/prepare_site_med_assets.py",
        "scope": "Portable content exports; original source bytes and freezes remain unchanged.",
        "assets": records,
    }, indent=2) + "\n").encode()
    return exports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare without writing")
    args = parser.parse_args()
    exports = prepare()
    stale = []
    for relative, blob in exports.items():
        target = MED / relative
        if args.check:
            if not target.exists() or target.read_bytes() != blob:
                stale.append(relative)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
    if stale:
        parser.exit(1, "Missing or stale: " + ", ".join(stale) + "\n")
    print(f"{'Verified' if args.check else 'Exported'} {len(exports) - 1} assets and their manifest.")


if __name__ == "__main__":
    main()
