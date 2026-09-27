"""Audit retained HuBMAP inputs and extract source teaching views; no model execution.

Run with the existing .venv-br030 interpreter and fresh --output/--audit paths.
The native TIFF and all frozen task files are read only. The worked inventory
uses source polygons and is explicitly a reader reference, never a prediction.
"""

import argparse
import base64
import hashlib
import io
import json
import math
import shutil
import xml.etree.ElementTree as ET
import zlib
from itertools import pairwise
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

PINS = {
    "datasets/receipts/wsi-teaching-samples.json": "2e1c2bdf985d7e6531dbb28883010e08568519d46a3985c0c7053609c3a35c81",
    ".local/wsi-ground-truth/source-metadata/hubmap-zenodo.json": "5ea723df7519e6d91dbd4204125ffdc1fb8e9ddfea0dd5aae761d0f7b6d5ba0b",
    "groups/lesion-localization/experiments/wsi-hubmap-inventory-astra-medium/freezes/freeze-f00304a2cc97caa2e87bb16f.json": "99f070f81b65d611b58cc442de732edb35c992f16f948f8e425a58393477de9d",
    "groups/lesion-localization/experiments/wsi-hubmap-inventory-v2-sol6-xhigh/freezes/freeze-81e0db6fb7bf21d10c7b6403.json": "4dc8b2ac7a5b5b5195f87abf0adc14cff4e995882614c202cc3f27ef0798e4ae",
}
PACK = "retained-hubmap-inventory-v1"
DETAIL = [2016, 6706, 1600, 1600]
TILES = [[2480, 7200, 640, 640], [2672, 7360, 640, 640]]


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def polygon_measure(points):
    """Signed shoelace area and area centroid in unchanged native coordinates."""
    p = np.asarray(points, dtype=np.float64)
    assert p.ndim == 2 and p.shape[1] == 2 and len(p) >= 4
    assert np.array_equal(p[0], p[-1]) and np.isfinite(p).all()
    q = p[:-1]
    nxt = np.roll(q, -1, axis=0)
    cross = q[:, 0] * nxt[:, 1] - nxt[:, 0] * q[:, 1]
    signed = float(cross.sum()) / 2
    assert abs(signed) > 0
    center = ((q + nxt) * cross[:, None]).sum(axis=0) / (6 * signed)
    return abs(signed), center.tolist()


def image_record(image: Image.Image, bounds: list[int]):
    stream = io.BytesIO()
    image.save(stream, format="JPEG", quality=80, subsampling=2)
    return {
        "bounds_level0": bounds,
        "raster_size": list(image.size),
        "image": "data:image/jpeg;base64," + base64.b64encode(stream.getvalue()).decode(),
        "display_encoding": "JPEG quality 80 with 4:2:0 chroma subsampling; no stain normalization",
    }


def build(root: Path, output: Path, audit_path: Path):
    if output.exists() or audit_path.exists():
        raise FileExistsError("Use fresh output and audit destinations")
    sources = {}
    for path, fingerprint in PINS.items():
        assert sha(root / path) == fingerprint, path
        sources[path] = fingerprint
    receipt = read(root / "datasets/receipts/wsi-teaching-samples.json")["samples"]["hubmap"]
    for item in receipt["files"]:
        path = root / item["local_path"]
        assert path.stat().st_size == item["bytes"] and sha(path) == item["sha256"]
        assert f"{zlib.crc32(path.read_bytes()):08x}" == item["zip_crc32"]
        assert item["archive_checksum_verified"] is False
        sources[item["local_path"]] = item["sha256"]
    metadata = read(root / ".local/wsi-ground-truth/source-metadata/hubmap-zenodo.json")
    assert metadata["metadata"]["license"]["id"] == "cc-by-4.0"
    frozen = []
    references = []
    for path in PINS:
        if "/freezes/" not in path:
            continue
        record = read(root / path)
        for name, fingerprint in record["files"].items():
            source = root / record["snapshot_path"] / name
            assert sha(source) == fingerprint, source
            sources[source.relative_to(root).as_posix()] = fingerprint
        references.append(read(root / record["snapshot_path"] / "tests/reference/reference.json"))
        frozen.append(
            {"record": path, "task_digest": record["task_digest"], "files": len(record["files"])}
        )

    source_root = root / ".local/wsi-ground-truth/hubmap"
    features = read(source_root / "aaa6a05cc.json")
    anatomy = read(source_root / "aaa6a05cc-anatomical-structure.json")
    assert len(features) == 99
    assert all(
        f["geometry"]["type"] == "Polygon" and len(f["geometry"]["coordinates"]) == 1
        for f in features
    )
    rings = [f["geometry"]["coordinates"][0] for f in features]
    assert all(r["polygons"] == rings and r["mpp"] == 0.65 for r in references)
    with tifffile.TiffFile(source_root / "aaa6a05cc.tiff") as tiff:
        assert len(tiff.pages) == 1 and tiff.pages[0].shape == (18484, 13013, 3)
        pixels = ET.fromstring(tiff.ome_metadata).find(".//{*}Pixels")
        assert pixels is not None
        assert all(
            pixels.attrib[f"PhysicalSize{axis}"] == "0.65"
            and pixels.attrib[f"PhysicalSize{axis}Unit"] == "µm"
            for axis in "XY"
        )
        native = tiff.pages[0].asarray()
    image = Image.fromarray(native)
    width, height = image.size
    objects = []
    area_roundoff = []
    for index, (feature, ring) in enumerate(zip(features, rings, strict=True)):
        assert feature["properties"]["classification"]["name"] == "glomerulus"
        assert all(0 <= x < width and 0 <= y < height for x, y in ring)
        area, center = polygon_measure(ring)
        local_area, local_center = polygon_measure(np.asarray(ring) - np.asarray(DETAIL[:2]))
        assert math.isclose(area, local_area, rel_tol=0, abs_tol=1e-6)
        assert np.allclose(np.asarray(local_center) + DETAIL[:2], center, rtol=0, atol=1e-7)
        # Independent triangle fan about the first vertex, signed then summed.
        shifted = np.asarray(ring, dtype=np.float64) - ring[0]
        fan = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in pairwise(shifted[1:]))) / 2
        area_roundoff.append(abs(fan - area))
        assert math.isclose(fan, area, rel_tol=0, abs_tol=1e-6)
        objects.append(
            {
                "id": f"ref-{index + 1:03}",
                "source_index": index,
                "source_id": feature["id"],
                "ring": ring,
                "center_level0": center,
                "area_px2": area,
                "area_um2": area * 0.65**2,
            }
        )
    assert math.isclose(
        objects[0]["area_um2"], receipt["measurements"]["first_polygon_area_um2"], abs_tol=1e-9
    )
    median = float(np.median([obj["area_um2"] for obj in objects]))
    assert math.isclose(median, receipt["measurements"]["median_polygon_area_um2"], abs_tol=1e-9)
    target = np.asarray(rings[0])
    for x, y, w, h in TILES:
        assert (target >= [x, y]).all() and (target < [x + w, y + h]).all()
    first = objects[0]
    duplicate = {
        "source_object": first["id"],
        "kind": "constructed duplicate: same reference object in two overlapping native crops",
        "local_centers": [
            (np.asarray(first["center_level0"]) - bounds[:2]).tolist() for bounds in TILES
        ],
        "unique_objects": 1,
        "view_records": 2,
    }
    for local, bounds in zip(duplicate["local_centers"], TILES, strict=True):
        assert np.allclose(
            np.asarray(local) + bounds[:2], first["center_level0"], rtol=0, atol=1e-10
        )
    x, y, w, h = DETAIL
    detail = image.crop((x, y, x + w, y + h))
    retained_detail = root / ".local/wsi-ground-truth/explainer/assets/hubmap-detail-input.png"
    assert np.array_equal(np.asarray(detail), np.asarray(Image.open(retained_detail)))
    sources[retained_detail.relative_to(root).as_posix()] = sha(retained_detail)
    preview = image.resize((563, 800), Image.Resampling.LANCZOS)
    source = {
        "sample": "aaa6a05cc",
        "size_level0": [width, height],
        "mpp": 0.65,
        "frame": "level-0-image",
        "axes": "x right, y down; upper-left origin",
        "overview": image_record(preview, [0, 0, width, height]),
        "overview_resampling": "Full native RGB to 563 by 800 with LANCZOS; display fits native physical aspect",
        "detail_selection": "First reference polygon bounding box; reference-selected teaching view removes search",
    }
    tiles = [
        image_record(image.crop((x, y, x + w, y + h)), bounds)
        for bounds in TILES
        for x, y, w, h in [bounds]
    ]
    reference = {
        "role": "reader-reference-reveal",
        "objects": objects,
        "source_object_count": len(objects),
        "id_rule": "ref-NNN is one-based source-array order; original feature ids are not unique",
        "duplicate": duplicate,
        "median_area_um2": median,
        "output_format_example": {
            "scope": "Reference-derived worked example, not a submitted answer",
            "geojson_feature": {
                "type": "Feature",
                "id": first["id"],
                "properties": {
                    "center_x_px": first["center_level0"][0],
                    "center_y_px": first["center_level0"][1],
                    "area_um2": first["area_um2"],
                },
                "geometry": features[0]["geometry"],
            },
            "csv_columns": ["id", "center_x_px", "center_y_px", "area_um2"],
        },
    }
    helpers = {
        "scope": "Optional anatomical-region context in the proposed definition; not supplied to retained point-only pilots",
        "features": anatomy,
        "provenance_limit": "Source anatomical regions are rough expert estimates, not an annotation-validity mask or exhaustive negative domain",
    }
    output.mkdir(parents=True)
    write(output / "source.json", source)
    write(output / "detail.json", image_record(detail, DETAIL))
    write(output / "tiles.json", tiles)
    write(output / "reference.json", reference)
    write(output / "helpers.json", helpers)
    shutil.copyfile(
        root / "presentation/task-explorer/airway-repair/DATA-LICENSE.txt",
        output / "DATA-LICENSE.txt",
    )
    (output / "NOTICE.md").write_text("""# HuBMAP inventory source teaching pack

Jain et al., *Segmentation of human functional tissue units in support of a Human Reference Atlas*, Zenodo v1 (2023), https://zenodo.org/records/7729610. Source image, glomerulus polygons and anatomical-region masks: **CC BY 4.0**, as recorded in the retained publisher metadata. The accompanying DATA-LICENSE.txt is the standard CC BY 4.0 legal code, not a license file extracted from data.zip.

Sample `aaa6a05cc` is a public PAS kidney training image. Exactly three ZIP members were extracted with CRC32 and SHA-256 verification; the 33.6 GB archive was not acquired or checksum-verified. The `gt_masks` member supplies 99 source polygons, not model predictions or an independently adjudicated exhaustive count. Annotation initialization was automated and then expert-corrected. Anatomical-region polygons are rough estimates; neither cortex nor unannotated tissue is an adjudicated negative domain.

`scripts/build_hubmap_inventory_assets.py` verifies retained sources and two 13-file task snapshots, then extracts RGB views and unaltered polygon coordinates. Coordinates are level-0 pixels (x right, y down); OME spacing is 0.65 micrometres on both axes. The overview uses LANCZOS reduction; detail and overlap crops use native pixels, encoded for display as JPEG quality 80 with 4:2:0 chroma subsampling without stain normalization. Geometry and areas use original coordinates, never JPEG pixels.

The 1600-pixel teaching crop begins at (2016,6706) and was selected by the first reference polygon. Two overlapping 640-pixel views demonstrate the same source object twice; this is a constructed duplicate example, not an agent error. `ref-NNN` identifiers are assigned by source-array order because source feature ids repeat. Centers are polygon area centroids, not independently annotated centers. Areas are two-dimensional profile areas, not volumes or whole-kidney counts.

Teal dashed outlines and lightly filled teal areas are reader reference. Amber marks a teaching viewport or centroid. Blue is optional cortex context; purple is optional medulla context. The reader-revealed GeoJSON/table is a reference-derived worked format, not a solver result. Retained diagnostic tasks submitted points only; no contour/area performance is inferred. Portable HTML embeds references and is not a solver packet. No new inference, annotation adjudication, trial or publication occurs.
""")
    assets = []
    for path in sorted(output.iterdir()):
        assert path.stat().st_size <= 1024**2, f"Asset exceeds retention threshold: {path}"
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
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-4.0",
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
            "scope": "Source geometry and teaching extraction; no model execution or clinical adjudication",
            "sources": sources,
            "native_shape": list(native.shape),
            "mpp": 0.65,
            "source_members": 3,
            "archive_checksum_verified": False,
            "frozen_tasks": frozen,
            "source_polygons": 99,
            "matching_frozen_reference_polygons": True,
            "original_feature_ids_unique": len({f["id"] for f in features}) == len(features),
            "first_object": {k: v for k, v in first.items() if k != "ring"},
            "median_area_um2": median,
            "max_area_arithmetic_difference_px2": max(area_roundoff),
            "detail_matches_retained_native_png": True,
            "constructed_duplicate": duplicate,
            "geometry_checks": "Closed finite single rings within native image; shoelace agrees with signed triangle fan, area/centroid translation invariance; no anatomical-validity inference",
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "audit": str(audit_path),
                "source_paths": len(sources),
                "first_area_um2": first["area_um2"],
                "assets": len(assets),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output, args.audit)
