"""Build one source-matched DENTEX teaching pack; never run ReX or a model."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


PACK_ID = "retained-rexmle-dentex-v1"
SOURCE = Path(".local/explainers/core-20260929/rex-dentex-isles-source/dentex")
RECEIPT = Path("presentation/external-tasks/sources/rexmle-dentex-resolution.json")
IMAGE_SHA = "ac62de4d5587c9da20fc0995a01ad0e61e3d7329e5c9e9c59f74330bc234a00c"
COCO_SHA = "6e1f702cfd6c83bc63660d9a0fd79fe5b26d5a54b63d93b954a02cc254314483"
REF_SHA = "460bd63f3fb14c18a1a2705ba544abd7f385c4dfe0a8592a81b9441bacbce6d1"


def repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "presentation/EXPLAINER-SCOPE.json").is_file():
            return p
    raise RuntimeError("Cannot locate tb3 checkout")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")


def build(root: Path, output: Path, receipt_path: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    source = root / SOURCE
    receipt = json.loads(receipt_path.read_text())
    if receipt["entry_id"] != "rexmle-dentex" or receipt["illustration_basis"] != "mixed":
        raise ValueError("Unexpected source resolution")
    if any(not a.get("attempted_at") for a in receipt["attempts"]):
        raise ValueError("Missing source attempt timestamp")
    image_path = source / "train_266.png"
    coco_path = source / "train_quadrant_enumeration_disease.json"
    reference_path = source / "private-reference-train_266.json"
    for path, expected in (
        (image_path, IMAGE_SHA),
        (coco_path, COCO_SHA),
        (reference_path, REF_SHA),
    ):
        if sha(path) != expected:
            raise ValueError(f"Source hash mismatch: {path}")
    coco = json.loads(coco_path.read_text())
    ref = json.loads(reference_path.read_text())
    split = json.loads((source / "split-review.json").read_text())
    assert len(coco["images"]) == 705 and len(coco["annotations"]) == 3529
    assert split["train_count"] == 564 and split["test_count"] == 141
    assert len(ref["images"]) == 1 and ref["images"][0]["id"] == 142
    assert len(ref["annotations"]) == 5
    assert all(a["image_id"] == 142 for a in ref["annotations"])
    assert ref["images"][0]["width"] == 1976 and ref["images"][0]["height"] == 976
    assert all(a["bbox"][2] > 0 and a["bbox"][3] > 0 for a in ref["annotations"])

    output.mkdir(parents=True)
    shutil.copyfile(image_path, output / "train_266.png")
    source_data = {
        "role": "public-ReX-test-input",
        "image": "train_266.png",
        "source_image_id": 142,
        "rex_image_id": "train_266",
        "source_zip_member": "training_data/quadrant-enumeration-disease/xrays/train_266.png",
        "rex_path": "test/images/train_266.png",
        "width_px": 1976,
        "height_px": 976,
        "frame": "image-pixel-top-left",
        "units": "px",
        "split": {
            "method": "pinned ReX prepare.py; Python random seed 42",
            "public_train": 564,
            "private_label_test": 141,
        },
        "notice": {
            "label": "Real DENTEX radiograph; no saved prediction or validated AP",
            "text": "Five source boxes are a reader-only reference. The pinned scorer's category IDs disagree with the source labels.",
            "url": "https://zenodo.org/records/7812323",
            "link_label": "Official DENTEX source",
        },
    }
    output_data = {
        "role": "expected-output-schema-not-prediction",
        "status": "not-retained",
        "submission_csv": "submission/submission.csv",
        "csv_columns": ["image_id", "predictions_json"],
        "example_row": {"image_id": "train_266", "predictions_json": "predictions/train_266.json"},
        "prediction_json": {"annotations": []},
        "box_fields": ["bbox", "category_id_1", "category_id_2", "category_id_3", "score"],
        "bbox_format": "[x,y,width,height] in source image pixels",
        "label_fields": {
            "category_id_1": "quadrant",
            "category_id_2": "tooth enumeration",
            "category_id_3": "diagnosis",
        },
        "model_prediction": None,
        "ap": None,
    }
    maps = {
        key: {str(c["id"]): c["name"] for c in ref[key]}
        for key in ("categories_1", "categories_2", "categories_3")
    }
    reference_data = {
        "role": "private-reader-reference",
        "visibility": "explicit-reveal-only",
        "source_excerpt_sha256": REF_SHA,
        "source_image_id": 142,
        "rex_private_path": "ground_truth/train_266.json",
        "box_format": "[x,y,width,height] in source image pixels",
        "category_names_by_source_id": maps,
        "boxes": [
            {
                "annotation_id": a["id"],
                "bbox": a["bbox"],
                "category_id_1": a["category_id_1"],
                "category_id_2": a["category_id_2"],
                "category_id_3": a["category_id_3"],
            }
            for a in sorted(ref["annotations"], key=lambda x: x["id"])
        ],
        "scorer_caveat": {
            "source_ids": {
                "quadrant": [0, 1, 2, 3],
                "enumeration": list(range(8)),
                "diagnosis": [0, 1, 2, 3],
            },
            "grader_declared_ids": {
                "quadrant": [1, 2, 3, 4],
                "enumeration": list(range(1, 9)),
                "diagnosis": [1, 2, 3, 4],
            },
            "grader_gt_handling": "passes source category_id_1/2/3 through unchanged",
            "status": "unresolved; no AP interpretation",
        },
    }
    write_json(output / "source.json", source_data)
    write_json(output / "output.json", output_data)
    write_json(output / "reference.json", reference_data)
    (output / "NOTICE.md").write_text(
        "DENTEX source radiograph and boxes: Zenodo record 7812323, CC-BY-4.0. ReX adapter pinned at b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53. The source-derived private boxes are for explicit reader reveal; no prediction or AP is supplied.\n"
    )
    (output / "DATA-LICENSE.txt").write_text(
        "DENTEX dataset, CC-BY-4.0; https://zenodo.org/records/7812323. Retained image/labels used for local attributed teaching.\n"
    )
    assets = []
    for name, role in (
        ("train_266.png", "illustration"),
        ("source.json", "illustration"),
        ("output.json", "illustration"),
        ("reference.json", "reader-reference-reveal"),
        ("NOTICE.md", "illustration"),
        ("DATA-LICENSE.txt", "illustration"),
    ):
        p = output / name
        assets.append(
            {
                "file": name,
                "sha256": sha(p),
                "bytes": p.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": role,
            }
        )
    write_json(
        output / "manifest.json",
        {
            "id": PACK_ID,
            "frame": "image-pixel-top-left",
            "units": "px",
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(SOURCE / "train_266.png"): IMAGE_SHA,
                str(SOURCE / "train_quadrant_enumeration_disease.json"): COCO_SHA,
                str(SOURCE / "private-reference-train_266.json"): REF_SHA,
            },
            "checks": {
                "source_images": 705,
                "source_annotations": 3529,
                "rex_train": 564,
                "rex_private_test": 141,
                "selected_reference_boxes": 5,
                "saved_prediction": False,
                "scorer_category_match": False,
            },
            "assets": assets,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=repo_root())
    parser.add_argument(
        "--receipt", type=Path, help="Staged receipt path; defaults to live repository receipt"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    build(root, args.output.resolve(), args.receipt.resolve() if args.receipt else root / RECEIPT)


if __name__ == "__main__":
    main()
