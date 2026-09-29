"""Build a local CellSeg training-example explainer; no ReX preparer or model run."""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image


SOURCE = Path(
    ".local/explainers/core-20260929/rex-cellseg-panther-source/pinned-source/cellseg-sample"
)
RECEIPT = Path("presentation/external-tasks/sources/rexmle-neurips-cellseg-resolution.json")
PACK_ID = "retained-rexmle-neurips-cellseg-v1"
FOCUS_IDS = (1, 16, 21, 36)  # border, small, large, and peripheral real source instances
IMAGE_SHA = "598be2ef95d7632d49c5efc76f1f82205d45d72a83e43562a57f1ce5792c5b47"
LABEL_SHA = "14ad94efdc53203552fd12dda1c6a04392e6dfc75ac2e9c48cf97ff4bf2a8b57"


def repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "presentation/EXPLAINER-SCOPE.json").is_file():
            return p
    raise RuntimeError("Cannot locate tb3 checkout")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def color(label: int) -> tuple[int, int, int]:
    red, green, blue = colorsys.hsv_to_rgb((label * 0.61803398875) % 1, 0.76, 1.0)
    return round(red * 255), round(green * 255), round(blue * 255)


def build(root: Path, output: Path, receipt_path: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    receipt = json.loads(receipt_path.read_text())
    if receipt["entry_id"] != "rexmle-neurips-cellseg" or receipt["illustration_basis"] != "mixed":
        raise ValueError("Unexpected source receipt")
    if any(not row.get("attempted_at") for row in receipt["attempts"]):
        raise ValueError("Missing source attempt timestamp")
    image_path = root / SOURCE / "cell_00944.png"
    label_path = root / SOURCE / "cell_00944_label.tiff"
    if sha(image_path) != IMAGE_SHA or sha(label_path) != LABEL_SHA:
        raise ValueError("Recovered source byte mismatch")
    image = Image.open(image_path)
    label = Image.open(label_path)
    if (
        image.size != label.size
        or image.size != (512, 512)
        or image.mode != "RGB"
        or label.mode != "I;16"
    ):
        raise ValueError("Unexpected native CellSeg image/label geometry")
    values = list(label.getdata())
    counts = Counter(values)
    if set(counts) != set(range(37)) or sum(counts[i] for i in range(1, 37)) != 8479:
        raise ValueError("Unexpected instance IDs or foreground pixels")

    output.mkdir(parents=True)
    (output / "cells").mkdir()
    shutil.copyfile(image_path, output / "cell_00944.png")
    shutil.copyfile(label_path, output / "cell_00944_label.tiff")
    width, height = image.size
    positions: dict[int, list[int]] = {i: [width, height, -1, -1] for i in range(1, 37)}
    for index, instance_id in enumerate(values):
        if instance_id:
            x, y = index % width, index // width
            box = positions[instance_id]
            box[0] = min(box[0], x)
            box[1] = min(box[1], y)
            box[2] = max(box[2], x)
            box[3] = max(box[3], y)
    instance_pixels = []
    foreground_pixels = []
    focus_pixels: dict[int, list[tuple[int, int, int, int]]] = {i: [] for i in FOCUS_IDS}
    for index, instance_id in enumerate(values):
        if not instance_id:
            instance_pixels.append((0, 0, 0, 0))
            foreground_pixels.append((0, 0, 0, 0))
            for layer in focus_pixels.values():
                layer.append((0, 0, 0, 0))
            continue
        x, y = index % width, index // width
        neighbors = (
            values[index - 1] if x else 0,
            values[index + 1] if x < width - 1 else 0,
            values[index - width] if y else 0,
            values[index + width] if y < height - 1 else 0,
        )
        edge = any(other != instance_id for other in neighbors)
        rgb = color(instance_id)
        instance_pixels.append((*rgb, 235 if edge else 104))
        foreground_pixels.append((27, 213, 224, 190 if edge else 105))
        for label_id, layer in focus_pixels.items():
            layer.append((*rgb, 255 if edge else 195) if label_id == instance_id else (0, 0, 0, 0))
    for name, pixels in (
        ("instance-map.png", instance_pixels),
        ("foreground-map.png", foreground_pixels),
    ):
        out = Image.new("RGBA", (width, height))
        out.putdata(pixels)
        out.save(output / name, optimize=True)
    for instance_id, pixels in focus_pixels.items():
        out = Image.new("RGBA", (width, height))
        out.putdata(pixels)
        highlighted = Image.alpha_composite(image.convert("RGBA"), out)
        left, top, right, bottom = positions[instance_id]
        crop = highlighted.crop(
            (max(0, left - 12), max(0, top - 12), min(width, right + 13), min(height, bottom + 13))
        )
        crop.save(output / "cells" / f"instance-{instance_id:02d}-crop.png", optimize=True)

    write_json(
        output / "source.json",
        {
            "role": "original-public-training-image",
            "image": "cell_00944.png",
            "source_zip_member": "Training-labeled/images/cell_00944.png",
            "image_id": "cell_00944",
            "width_px": 512,
            "height_px": 512,
            "frame": "image-pixel-top-left",
            "units": "px",
            "split": {
                "source_training_pairs": 1000,
                "source_tuning_pairs": 101,
                "reconstructed_public_train": 880,
                "reconstructed_private_test": 221,
                "seed": 42,
                "sample_role": "expected-public-train",
                "preparer_executed": False,
            },
            "notice": {
                "label": "Real training patch and labels; no held-out prediction or F1",
                "text": "The 36-cell label is supplied training help. Exact ReX staging was reconstructed from pinned code, not run.",
                "url": "https://zenodo.org/records/10719375",
                "link_label": "Official CellSeg source",
            },
        },
    )
    write_json(
        output / "helper.json",
        {
            "role": "supplied-public-training-label",
            "source_zip_member": "Training-labeled/labels/cell_00944_label.tiff",
            "native_label": "cell_00944_label.tiff",
            "instance_overlay": "instance-map.png",
            "binary_overlay": "foreground-map.png",
            "background_id": 0,
            "instance_ids": list(range(1, 37)),
            "instance_count": 36,
            "foreground_pixel_count": 8479,
            "total_pixel_count": 262144,
            "instances": [
                {
                    "id": i,
                    "pixels": counts[i],
                    "bbox_xyxy_inclusive": positions[i],
                    "color_rgb": color(i),
                    "focus_image": f"cells/instance-{i:02d}-crop.png" if i in FOCUS_IDS else None,
                }
                for i in range(1, 37)
            ],
            "focus_ids": list(FOCUS_IDS),
            "meaning": "Positive integers distinguish cells, not cell types or diagnoses.",
        },
    )
    write_json(
        output / "output.json",
        {
            "role": "expected-held-out-output-schema",
            "status": "not-retained",
            "test_image": None,
            "prediction_mask": None,
            "f1": None,
            "submission_csv": "submission/submission.csv",
            "csv_columns": ["image_id", "predicted_mask_path"],
            "row_template": {
                "image_id": "<held-out image_id>",
                "predicted_mask_path": "predictions/<image_id>_label.tiff",
            },
            "mask_semantics": "2D integer image on the source pixel grid: 0 background; distinct positive IDs for separate cells",
        },
    )
    write_json(
        output / "metric.json",
        {
            "role": "pinned-scorer-operation-only",
            "thresholds_iou": [0.5, 0.6, 0.7, 0.8, 0.9],
            "matching": "Hungarian one-to-one assignment of instance masks by pairwise intersection over union; threshold is inclusive",
            "boundary_margin_px": 2,
            "large_image_branch": {"at_least_pixels": 25000000, "roi_size_px": [2000, 2000]},
            "shape_mismatch": "nearest-neighbor resize of prediction to reference array shape",
            "sample_branch": "512x512 = 262144 pixels, direct evaluation branch if this were a scored case; no score run",
            "score": None,
        },
    )
    (output / "NOTICE.md").write_text(
        "Original NeurIPS CellSeg sample, Zenodo 10719375, CC-BY-NC-ND-4.0. Local noncommercial teaching only; do not infer derivative redistribution permission. The TIFF is supplied training help, not held-out evaluator truth. No ReX preparation, prediction, grader or score was run.\n"
    )
    (output / "DATA-LICENSE.txt").write_text(
        "Official CellSeg source record: https://zenodo.org/records/10719375. License reported by official Zenodo API: CC-BY-NC-ND-4.0. Preserve attribution; this local teaching pack makes no redistribution permission claim.\n"
    )
    assets = []
    for path in sorted(x for x in output.rglob("*") if x.is_file()):
        rel = path.relative_to(output).as_posix()
        assets.append(
            {
                "file": rel,
                "sha256": sha(path),
                "bytes": path.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "illustration",
            }
        )
    write_json(
        output / "manifest.json",
        {
            "id": PACK_ID,
            "frame": "image-pixel-top-left",
            "units": "px",
            "license": "CC-BY-NC-ND-4.0",
            "label_license": "CC-BY-NC-ND-4.0",
            "reference_policy": "no-reference-assets",
            "sources": {
                str(SOURCE / "cell_00944.png"): IMAGE_SHA,
                str(SOURCE / "cell_00944_label.tiff"): LABEL_SHA,
            },
            "checks": {
                "sample_role": "reconstructed-public-train",
                "source_image_px": [512, 512],
                "source_instance_count": 36,
                "source_foreground_px": 8479,
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
    parser.add_argument(
        "--receipt", type=Path, help="Staged receipt path; default is live repository path"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    build(root, args.output.resolve(), args.receipt.resolve() if args.receipt else root / RECEIPT)


if __name__ == "__main__":
    main()
