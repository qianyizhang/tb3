"""Build three source-matched PUMA training explainers without running ReX."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

SOURCE = Path(".local/explainers/core-20260929/rex-puma-source")
CASE = "training_set_metastatic_roi_001"
REV = "b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53"
ENTRIES = ("rexmle-puma-track1-task1", "rexmle-puma-track1-task2", "rexmle-puma-track2-task2")
TISSUE = {
    "tissue_white_background": 0,
    "tissue_stroma": 1,
    "tissue_blood_vessel": 2,
    "tissue_tumor": 3,
    "tissue_epidermis": 4,
    "tissue_necrosis": 5,
}
FINE = {
    "nuclei_tumor": "tumor",
    "nuclei_lymphocyte": "lymphocytes",
    "nuclei_plasma_cell": "plasma_cells",
    "nuclei_histiocyte": "histiocytes",
    "nuclei_melanophage": "melanophages",
    "nuclei_neutrophil": "neutrophils",
    "nuclei_stroma": "stromal_cells",
    "nuclei_epithelium": "epithelium",
    "nuclei_endothelium": "endothelium",
    "nuclei_apoptosis": "apoptotic_cells",
}
COARSE = {
    "tumor": "tumor",
    "lymphocytes": "TILs",
    "plasma_cells": "TILs",
    "histiocytes": "other",
    "melanophages": "other",
    "neutrophils": "other",
    "stromal_cells": "other",
    "epithelium": "other",
    "endothelium": "other",
    "apoptotic_cells": "other",
}


def repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "presentation/EXPLAINER-SCOPE.json").is_file():
            return p
    raise RuntimeError("Cannot locate tb3 checkout")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def tissue_assets(raw: Path, output: Path) -> dict:
    geo = json.loads((raw / f"{CASE}_tissue.geojson").read_text())
    mask = Image.new("L", (1024, 1024), 0)
    draw = ImageDraw.Draw(mask)
    for feature in geo["features"]:
        name = feature["properties"]["classification"]["name"].lower()
        if name not in TISSUE:
            continue
        geometry = feature["geometry"]
        rings = (
            [geometry["coordinates"]]
            if geometry["type"] == "Polygon"
            else geometry["coordinates"]
            if geometry["type"] == "MultiPolygon"
            else []
        )
        for polygon in rings:
            if polygon and len(polygon[0]) >= 3:
                draw.polygon(
                    [(float(x), float(y)) for x, y in polygon[0]],
                    fill=TISSUE[name],
                    outline=TISSUE[name],
                )
    mask.save(output / "training-tissue-mask.png", optimize=True)
    counts = collections.Counter(mask.getdata())
    colors = {3: (20, 198, 212), 5: (244, 188, 73)}
    overlay = Image.new("RGBA", mask.size)
    values = list(mask.getdata())
    tinted = []
    for index, value in enumerate(values):
        if value not in colors:
            tinted.append((0, 0, 0, 0))
            continue
        x, y = index % 1024, index // 1024
        adjacent = (
            values[index - 1] if x else 0,
            values[index + 1] if x < 1023 else 0,
            values[index - 1024] if y else 0,
            values[index + 1024] if y < 1023 else 0,
        )
        edge = any(other != value for other in adjacent)
        tinted.append((*colors[value], 220 if edge else 25 if value == 3 else 78))
    overlay.putdata(tinted)
    overlay.save(output / "training-tissue-overlay.png", optimize=True)
    return {
        "role": "supplied-public-training-tissue-annotation",
        "source_format": "GeoJSON polygons",
        "derived_mask": "training-tissue-mask.png",
        "overlay": "training-tissue-overlay.png",
        "converter": "pinned prepare.py exterior-ring polygon fill order; no preparer execution",
        "class_ids": TISSUE,
        "selected_source_classes": ["tissue_necrosis", "tissue_tumor"],
        "pixels_by_id": {str(i): counts[i] for i in range(6)},
        "feature_count": len(geo["features"]),
    }


def nuclei_assets(raw: Path, output: Path, coarse: bool) -> dict:
    geo = json.loads((raw / f"{CASE}_nuclei.geojson").read_text())
    points = []
    skipped = collections.Counter()
    for index, feature in enumerate(geo["features"]):
        geometry = feature["geometry"]
        if geometry.get("type") != "Polygon":
            skipped[geometry.get("type", "unknown")] += 1
            continue
        ring = geometry.get("coordinates", [[]])[0]
        if len(ring) < 3:
            skipped["short-polygon"] += 1
            continue
        name = feature["properties"]["classification"]["name"].lower()
        if name not in FINE:
            skipped["unknown-class"] += 1
            continue
        fine = FINE[name]
        cls = COARSE[fine] if coarse else fine
        points.append(
            {
                "source_index": index,
                "x_px": round(sum(float(p[0]) for p in ring) / len(ring), 3),
                "y_px": round(sum(float(p[1]) for p in ring) / len(ring), 3),
                "source_class": name,
                "class": cls,
            }
        )
    classes = collections.Counter(p["class"] for p in points)
    return {
        "role": "supplied-public-training-nuclei-annotation",
        "source_format": "GeoJSON nuclei polygons",
        "centroid_rule": "arithmetic mean of exterior path points as pinned grader",
        "source_feature_count": len(geo["features"]),
        "accepted_polygon_count": len(points),
        "skipped": dict(skipped),
        "class_counts": dict(classes),
        "class_mapping": COARSE if coarse else FINE,
        "zoom": {
            "x_px": 512,
            "y_px": 512,
            "width_px": 256,
            "height_px": 256,
            "selection": "post-hoc author view, not an assisted localization",
        },
        "points": points,
    }


def build(root: Path, entry: str, output: Path, receipt_path: Path) -> None:
    if entry not in ENTRIES:
        raise ValueError("Unknown PUMA entry")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("entry_id") != entry or receipt.get("illustration_basis") != "mixed":
        raise ValueError("Wrong source receipt")
    if any(not a.get("attempted_at") for a in receipt["attempts"]):
        raise ValueError("Untimed source attempt")
    raw = root / SOURCE
    evidence = json.loads((raw / "source-evidence.json").read_text())
    paths = [f"{CASE}.tif", f"{CASE}_{'tissue' if entry.endswith('task1') else 'nuclei'}.geojson"]
    for name in paths:
        if sha(raw / name) != evidence["files"][name]["sha256"]:
            raise ValueError(f"Changed source member: {name}")
    image = Image.open(raw / f"{CASE}.tif")
    if image.size != (1024, 1024) or image.mode != "RGBA":
        raise ValueError("Unexpected source image geometry")
    output.mkdir(parents=True)
    image.convert("RGB").save(output / "training-roi.png", optimize=True)
    image.convert("RGB").crop((512, 512, 768, 768)).save(
        output / "training-zoom.png", optimize=True
    )
    tissue = entry.endswith("task1")
    helper = (
        tissue_assets(raw, output)
        if tissue
        else nuclei_assets(raw, output, entry.endswith("track1-task2"))
    )
    write_json(output / "helper.json", helper)
    write_json(
        output / "source.json",
        {
            "role": "reconstructed-public-training-input",
            "case_id": CASE,
            "image": "training-roi.png",
            "zoom_image": "training-zoom.png",
            "frame": "image-pixel-top-left",
            "units": "px",
            "width_px": 1024,
            "height_px": 1024,
            "source_zip_member": f"01_training_dataset_tif_ROIs/{CASE}.tif",
            "source_tif_sha256": evidence["files"][f"{CASE}.tif"]["sha256"],
            "split": {
                "matched_image_tissue_nuclei_cases": 205,
                "reconstructed_public_train": 164,
                "reconstructed_private_label_test": 41,
                "selected_role": "public-train",
                "preparer_executed": False,
            },
            "notice": {
                "label": "Real PUMA training ROI and annotation; no held-out prediction or score",
                "text": "This image is reconstructed as public train from pinned code. Its annotation is training help; no ReX run was made.",
                "url": "https://zenodo.org/records/14869398",
                "link_label": "Official PUMA source",
            },
        },
    )
    if tissue:
        schema = {
            "submission_csv": "submission/submission.csv",
            "csv_columns": ["case_id", "predicted_mask_path"],
            "row_template": {
                "case_id": "<held-out case_id>",
                "predicted_mask_path": "predictions/<case_id>.tif",
            },
            "mask_values": {str(v): k for k, v in TISSUE.items()},
            "mask_shape_px": [1024, 1024],
            "prediction": None,
            "score": None,
        }
        metric = {
            "primary": "mean per-class micro Dice across five foreground classes, background excluded",
            "foreground_ids": [1, 2, 3, 4, 5],
            "zero_empty_class_score": 0,
            "secondary": "mean per-case class-average Dice",
            "shape_mismatch": "nearest-neighbor resize to 1024x1024",
            "result": None,
        }
    else:
        schema = {
            "submission_csv": "submission/submission.csv",
            "csv_columns": ["case_id", "predicted_nuclei_path"],
            "row_template": {
                "case_id": "<held-out case_id>",
                "predicted_nuclei_path": "predictions/<case_id>.json",
            },
            "json_template": {"polygons": []},
            "accepted_shape": "polygons with name/path_points or simplified nuclei with class/centroid; optional score",
            "prediction": None,
            "score": None,
        }
        metric = {
            "primary": "macro F1 over 3 classes"
            if entry.endswith("track1-task2")
            else "macro F1 over 10 classes",
            "distance_px": 15,
            "distance_rule": "strictly less than"
            if entry.endswith("track1-task2")
            else "less than or equal to",
            "match_policy": "for each ground-truth nucleus, eligible same-class prediction sorted by confidence descending then distance ascending; consume match once",
            "result": None,
        }
    write_json(
        output / "output.json",
        {"role": "empty-held-out-output-schema", "status": "not-retained", **schema},
    )
    write_json(output / "metric.json", {"role": "pinned-scorer-operation-only", **metric})
    (output / "NOTICE.md").write_text(
        "Official PUMA record 14869398, CC0-1.0. This locally reconstructed public-training example uses one image and its matching source annotation. The ReX preparer, model, grader and score were not run. Derived masks/points are source teaching views, not predictions.\n"
    )
    (output / "DATA-LICENSE.txt").write_text(
        "PUMA source record https://zenodo.org/records/14869398 reports CC0-1.0 in the official Zenodo API. Cite the PUMA dataset and retain source provenance.\n"
    )
    assets = []
    for p in sorted(x for x in output.iterdir() if x.is_file()):
        assets.append(
            {
                "file": p.name,
                "sha256": sha(p),
                "bytes": p.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "illustration",
            }
        )
    write_json(
        output / "manifest.json",
        {
            "id": f"retained-{entry}-v1",
            "frame": "image-pixel-top-left",
            "units": "px",
            "license": "CC0-1.0",
            "label_license": "CC0-1.0",
            "reference_policy": "no-reference-assets",
            "sources": {str(SOURCE / name): evidence["files"][name]["sha256"] for name in paths},
            "checks": {
                "matched_cases": 205,
                "reconstructed_train": 164,
                "reconstructed_test": 41,
                "source_annotation_features": helper.get(
                    "feature_count", helper.get("source_feature_count")
                ),
                "preparer_run": False,
                "model_run": False,
                "grader_run": False,
            },
            "assets": assets,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=repo_root())
    parser.add_argument("--entry", choices=ENTRIES, required=True)
    parser.add_argument(
        "--receipt", type=Path, help="Staged receipt path; default is live repository receipt"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    receipt = (
        args.receipt.resolve()
        if args.receipt
        else root / "presentation/external-tasks/sources" / f"{args.entry}-resolution.json"
    )
    build(root, args.entry, args.output.resolve(), receipt)


if __name__ == "__main__":
    main()
