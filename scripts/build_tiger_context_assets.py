"""Audit retained TIGER data and prepare source teaching views; no model execution."""

import argparse
import base64
import hashlib
import io
import json
import math
import shutil
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

PACK = "retained-tiger-context-v1"
MPP = 20000 / 43793
COLORS = ["#697582", "#d54579", "#20a49a", "#f19144", "#8970c6", "#916441", "#3476c9", "#aaa54a"]
LABELS = [
    "Unknown / unannotated",
    "Invasive tumor",
    "Tumor-associated stroma",
    "In-situ tumor",
    "Healthy glands",
    "Non-in-situ necrosis",
    "Inflamed tumor-associated stroma",
    "Other / rest tissue",
]
PINS = {
    "datasets/receipts/wsi-teaching-samples.json": "2e1c2bdf985d7e6531dbb28883010e08568519d46a3985c0c7053609c3a35c81",
    ".local/wsi-ground-truth/source-metadata/tiger-license.txt": "622e76a7dc5597d4c79d9320bbe105d5c213388869fea025b033dd4377251b5b",
    "groups/lesion-localization/experiments/wsi-tiger-context-astra-medium/freezes/freeze-51b2cc974a33b276b54171e8.json": "ee60224ca604c41c52b2c9482dd9bd8c88839aeedd3979623e97da2c0e3f5b36",
    "groups/lesion-localization/experiments/wsi-tiger-context-astra-medium/freezes/freeze-feace41bfb792b616200d535.json": "afe705ca365fc27e7d895b9cc429490136d3775dca76d6fa904daa9df9384588",
    "groups/lesion-localization/experiments/wsi-tiger-context-v2-sol6-xhigh/freezes/freeze-17a4512e7e1be7f646843acb.json": "786f6c47882459001276b0e017ece46b8f6d09c0f3a259ee415bad4b72105552",
    "groups/lesion-localization/experiments/wsi-tiger-context-v2-sol6-xhigh/freezes/freeze-cc71d25cfbfc03edd452a48a.json": "ddc737607a9a82e18a0711c62823c50ea7e6a5505a3e8932a29cf167e54b7b1c",
}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def encoded(image, lossless=False):
    stream = io.BytesIO()
    image.save(
        stream, format="PNG" if lossless else "JPEG", **({} if lossless else {"quality": 78})
    )
    return (
        "data:image/"
        + ("png" if lossless else "jpeg")
        + ";base64,"
        + base64.b64encode(stream.getvalue()).decode()
    )


def native_region(tiff, bounds):
    """Read only intersecting level-0 TIFF tiles; do not load the whole slide."""
    x, y, w, h = bounds
    p = tiff.pages[0]
    out = np.empty((h, w, 3), np.uint8)
    tw, th = p.tilewidth, p.tilelength
    cols = math.ceil(p.imagewidth / tw)
    offsets, counts, decode, tables = p.dataoffsets, p.databytecounts, p.decode, p.jpegtables
    for ty in range(y // th, math.ceil((y + h) / th)):
        for tx in range(x // tw, math.ceil((x + w) / tw)):
            i = ty * cols + tx
            tiff.filehandle.seek(offsets[i])
            decoded, _, _ = decode(tiff.filehandle.read(counts[i]), i, jpegtables=tables)
            gx, gy = tx * tw, ty * th
            xa, ya, xb, yb = max(x, gx), max(y, gy), min(x + w, gx + tw), min(y + h, gy + th)
            out[ya - y : yb - y, xa - x : xb - x] = decoded[
                0, ya - gy : yb - gy, xa - gx : xb - gx, :3
            ]
    return out


def build(root, output, audit_path):
    if output.exists() or audit_path.exists():
        raise FileExistsError("Use fresh output and audit destinations")
    sources = dict(PINS)
    for path, digest in PINS.items():
        assert sha(root / path) == digest, path
    receipt = read(root / "datasets/receipts/wsi-teaching-samples.json")["samples"]["tiger"]
    for item in receipt["files"]:
        path = root / item["local_path"]
        assert path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], path
        sources[item["local_path"]] = item["sha256"]
    snapshots, frozen = [], []
    for name in PINS:
        if "/freezes/" not in name:
            continue
        record = read(root / name)
        task = root / record["snapshot_path"]
        for path, digest in record["files"].items():
            assert sha(task / path) == digest, path
            sources[(task / path).relative_to(root).as_posix()] = digest
        frozen.append(
            {"record": name, "task_digest": record["task_digest"], "files": len(record["files"])}
        )
        snapshots.append(task)
    data = root / ".local/wsi-ground-truth/tiger"
    coco = read(data / "tiger-coco.json")
    selected = {item["id"]: item for item in coco["images"] if item["id"] in [940, 941, 942]}
    results, images, masks, stats = [], {}, {}, []
    with tifffile.TiffFile(data / "114S.tif") as tiff:
        page = tiff.pages[0]
        assert page.shape == (43392, 61504, 3)
        assert page.tags["ResolutionUnit"].value == 3
        for axis in "XY":
            assert page.tags[f"{axis}Resolution"].value == (43793, 2)
        overview = Image.fromarray(tiff.pages[6].asarray())
        for pilot, coco_id in enumerate([942, 940, 941], start=1):
            item = selected[coco_id]
            name = Path(item["file_name"]).name
            bounds = [int(n) for n in name.split("[")[1].split("]")[0].split(",")]
            x, y, x2, y2 = bounds
            bounds = [x, y, x2 - x, y2 - y]
            image = Image.open(data / "rois" / name).convert("RGB")
            mask = np.asarray(Image.open(data / "masks" / name))
            assert image.size == (bounds[2], bounds[3]) == (item["width"], item["height"])
            assert mask.shape == (bounds[3], bounds[2]) and set(np.unique(mask)) <= set(range(8))
            assert np.array_equal(native_region(tiff, bounds), np.asarray(image))
            cells = []
            for ann in coco["annotations"]:
                if ann["image_id"] != coco_id:
                    continue
                assert ann["category_id"] == 1
                bx, by, bw, bh = ann["bbox"]
                cx, cy = bx + bw / 2, by + bh / 2
                assert 0 <= cx < image.width and 0 <= cy < image.height
                cells.append(
                    {
                        "id": ann["id"],
                        "bbox": ann["bbox"],
                        "center": [cx, cy],
                        "compartment": int(mask[round(cy), round(cx)]),
                    }
                )
            assert len(cells) == [20, 175, 323][pilot - 1]
            for task in snapshots:
                truth = read(task / "tests/reference/reference.json")["rois"][f"roi{pilot}"]
                assert truth["cells"] == [{"x": c["center"][0], "y": c["center"][1]} for c in cells]
                assert np.array_equal(
                    np.asarray(Image.open(task / "tests/reference" / truth["mask"])), mask
                )
                assert np.array_equal(
                    np.asarray(Image.open(task / "environment/data" / f"roi{pilot}.png")),
                    np.asarray(image),
                )
                supplied = task / "environment/data" / f"roi{pilot}-tissue.png"
                if supplied.exists():
                    assert np.array_equal(np.asarray(Image.open(supplied)), mask)
            counts = [sum(c["compartment"] == k for c in cells) for k in range(8)]
            floor_counts = [
                sum(int(mask[int(c["center"][1]), int(c["center"][0])]) == k for c in cells)
                for k in range(8)
            ]
            pixels = [int((mask == k).sum()) for k in range(8)]
            rows = [
                {
                    "code": k,
                    "cells": counts[k],
                    "pixels": pixels[k],
                    "area_mm2": pixels[k] * MPP**2 / 1e6,
                    "density_per_mm2": counts[k] / (pixels[k] * MPP**2 / 1e6)
                    if k and pixels[k]
                    else None,
                }
                for k in range(8)
            ]
            merged = {"cells": counts[2] + counts[6], "pixels": pixels[2] + pixels[6]}
            merged["area_mm2"] = merged["pixels"] * MPP**2 / 1e6
            merged["density_per_mm2"] = (
                merged["cells"] / merged["area_mm2"] if merged["pixels"] else None
            )
            rgba = np.empty((*mask.shape, 4), np.uint8)
            for k, color in enumerate(COLORS):
                rgb = [int(color[i : i + 2], 16) for i in [1, 3, 5]]
                rgba[mask == k] = [*rgb, 125 if k else 185]
            result = {
                "pilot_id": f"roi{pilot}",
                "coco_id": coco_id,
                "bounds_level0": bounds,
                "cells": cells,
                "rows": rows,
                "merged_stroma": merged,
                "mask_overlay": encoded(Image.fromarray(rgba), True),
            }
            results.append(result)
            images[f"roi{pilot}"] = image
            masks[f"roi{pilot}"] = mask
            stats.append(
                {
                    "pilot_id": f"roi{pilot}",
                    "coco_id": coco_id,
                    "bounds_level0": bounds,
                    "native_rgb_mae": 0,
                    "cells": len(cells),
                    "rounded_assignment": counts,
                    "historical_floor_assignment": floor_counts,
                    "rows": rows,
                    "merged_stroma": merged,
                }
            )
    # Explicitly constructed point displacement, not a stored agent prediction.
    point, shifted = [465, 870], [467, 873]
    assert any(c["center"] == point for c in results[2]["cells"])
    assert masks["roi3"][point[1], point[0]] == 1 and masks["roi3"][shifted[1], shifted[0]] == 2
    example = {
        "kind": "constructed displacement from one source center; not agent output",
        "pilot_id": "roi3",
        "center": point,
        "shifted": shifted,
        "distance_px": math.dist(point, shifted),
        "source_code": 1,
        "shifted_code": 2,
        "crop_bounds_roi": [405, 810, 120, 120],
    }
    selected_roi = results[1]
    detail_bounds = [640, 420, 480, 480]

    def crop(im, b):
        return im.crop((b[0], b[1], b[0] + b[2], b[1] + b[3]))

    output.mkdir(parents=True)
    for result in results:
        pilot_id = result["pilot_id"]
        write(
            output / f"{pilot_id}.json",
            {
                "pilot_id": pilot_id,
                "coco_id": result["coco_id"],
                "bounds_level0": result["bounds_level0"],
                "image": encoded(images[pilot_id]),
            },
        )
    write(
        output / "source.json",
        {
            "sample": "114S",
            "size_level0": [61504, 43392],
            "mpp": MPP,
            "frame": "level-0-image",
            "axes": "x right, y down, upper-left origin",
            "overview": encoded(overview),
            "detail": {
                "pilot_id": "roi2",
                "bounds_roi": detail_bounds,
                "image": encoded(crop(images["roi2"], detail_bounds)),
                "selection": "Source-reference-selected dense cell teaching crop; not agent navigation",
            },
            "boundary": {
                "bounds_roi": example["crop_bounds_roi"],
                "image": encoded(crop(images["roi3"], example["crop_bounds_roi"])),
            },
            "encoding": "JPEG quality 78; unchanged source RGB, no stain normalization; masks lossless PNG; overview native pyramid level 6",
        },
    )
    write(
        output / "reference.json",
        {
            "role": "reader-reference-reveal",
            "rois": results,
            "palette": [{"code": k, "label": LABELS[k], "color": COLORS[k]} for k in range(8)],
            "assignment": "Source COCO box center, mask indexed with Python round (ties to even); historical receipt used floor. Counts compared in source audit.",
            "boundary": example,
            "total_cells": sum(len(r["cells"]) for r in results),
            "cell_class": "lymphocytes and plasma cells merged",
            "box_meaning": "Publisher fixed 8 by 8 micrometre marker about a cell point, not nuclear outlines; use released coordinates unchanged",
            "density_scope": "Reference-derived arithmetic in three selected source ROIs; exclude mask 0 and absent-area classes; merge 2+6 by summed counts divided by summed area",
        },
    )
    shutil.copyfile(
        root / ".local/wsi-ground-truth/source-metadata/tiger-license.txt",
        output / "DATA-LICENSE.txt",
    )
    (output / "NOTICE.md").write_text("""# TIGER tissue-context teaching pack

Source: TIGER challenge data, curated by Radboud University Medical Center and partners. Official data guide: https://tiger.grand-challenge.org/Data/ ; release: https://registry.opendata.aws/tiger/ . Selected `114S` is a JB surgical-resection training slide. Its image and annotations are **CC BY-NC 4.0**. DATA-LICENSE.txt preserves the publisher license notice; legal terms: https://creativecommons.org/licenses/by-nc/4.0/ .

The builder audits nine acquired source files, the license notice, and four unique frozen task conditions (70 files). Level-0 TIFF spacing is 20000/43793 micrometres per pixel on both axes. All three released ROI PNGs exactly match their native TIFF crops. The source XML is retained and fingerprinted but is not re-rasterized or substituted for the released masks. Only the selected ROIs carry the source cell annotations used here; other slide areas are not negative references.

Pilot roi1 = COCO 942 (20 cells), roi2 = COCO 940 (175), roi3 = COCO 941 (323). Earlier teaching receipt ordered ROIs by COCO ID. Use COCO IDs and exact crop bounds to resolve that difference. Source cell points are centers of fixed-size marker boxes for a merged lymphocyte/plasma-cell class; boxes are not nuclear segmentations. JPEG quality 78 images serve display only; original coordinates and lossless masks drive measurements. Native pyramid level 6 provides the slide overview. The dense teaching crop is reference-selected and removes search.

Tissue colors follow reference.json's explicit code palette. Cell references are yellow dashed marker boxes/crosses. White/black rings mark a constructed point displacement, not an agent output. All reference marks, masks, counts and densities require the reader reference reveal. Optional tissue-supplied tasks are a separate assistance condition. Portable HTML embeds references and must not be distributed as a solver packet.

Worked density uses mask pixels times squared physical spacing, excludes unknown code 0, reports absent area as unavailable, and optionally merges codes 2 and 6 by summing counts and areas. It is cells/mm² in selected ROIs, not clinical stromal TIL area percentage. The proposed joint task returns cells.csv, regions.geojson and summary.csv; historical pilots returned points.json only. No tissue contour or density performance is inferred, no historical score changes, and no new trial or adjudication occurs.
""")
    assets = []
    for path in sorted(output.iterdir()):
        assert path.stat().st_size <= 1024**2, path
        assets.append(
            {
                "file": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha(path),
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal"
                if path.name == "reference.json"
                else "illustration",
            }
        )
    write(
        output / "manifest.json",
        {
            "id": PACK,
            "license": "CC-BY-NC-4.0",
            "label_license": "CC-BY-NC-4.0",
            "frame": "level-0-image",
            "units": "px",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "assets": assets,
        },
    )
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    write(
        audit_path,
        {
            "schema": 1,
            "scope": "Source pixels, geometry and arithmetic; no model execution or result reinterpretation",
            "sources": sources,
            "source_files": 9,
            "frozen_tasks": frozen,
            "size_level0": [61504, 43392],
            "mpp": MPP,
            "rois": stats,
            "constructed_boundary_example": example,
            "selected_density_example": selected_roi["merged_stroma"],
            "frozen_reference_images_masks_centers_match_source": True,
        },
    )
    print(
        json.dumps(
            {"output": str(output), "audit": str(audit_path), "rois": stats, "assets": len(assets)}
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output, args.audit)
