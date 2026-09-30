#!/usr/bin/env python3
"""Build the symbolic tumor-tile teaching pack without WSI image bytes.

This script reads the canonical resolution receipt and pinned local audit files to
verify provenance. It never reads, decodes, or copies TIFF JPEG tile/overview bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def encode(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, required=True, help="fresh output directory; overwrite refused"
    )
    parser.add_argument(
        "--receipt", type=Path, required=True, help="staged or canonical source-resolution receipt"
    )
    args = parser.parse_args()
    root = next(
        (p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()), None
    )
    if root is None:
        raise RuntimeError("tb3 repository root not found")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    receipt_path = args.receipt.resolve()
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    if (
        receipt.get("entry_id") != "healthagentbench-tumor-tiles"
        or receipt.get("illustration_basis") != "symbolic"
    ):
        raise ValueError("wrong symbolic tumor-tiles receipt")
    source_hashes: dict[str, str] = {
        "presentation/external-tasks/sources/healthagentbench-tumor-tiles-resolution.json": sha(
            receipt_bytes
        )
    }
    for item in receipt["source_pins"]:
        raw_path = str(item["path"])
        rel = (
            raw_path
            if raw_path.startswith(".local/")
            else ".local/explainers/core-20260929/interpretation-a-source/pinned-source/" + raw_path
        )
        path = root / rel
        data = path.read_bytes()
        if len(data) != item["bytes"] or sha(data) != item["sha256"]:
            raise ValueError(f"source pin mismatch: {rel}")
        # These pins support the task contract and geometry; no source pixels enter the pack.
        # The canonical receipt retains raw audit pins; portable pack pins only that receipt.
    if len(receipt["source_pins"]) != 11:
        raise ValueError("expected eight task-file pins plus three native IFD/index pins")
    if not all(
        any(str(pin["path"]).endswith(name) for pin in receipt["source_pins"])
        for name in ("tumor-076-ifd-0.bin", "tumor-076-ifd-8.bin", "tumor-076-ifd-index.json")
    ):
        raise ValueError("native geometry pins absent")
    index = json.loads(
        (
            root
            / ".local/explainers/core-20260929/interpretation-a-source/tumor-076-ifd-index.json"
        ).read_text()
    )
    first = next(row for row in index if row["index"] == 0)
    last = next(row for row in index if row["index"] == 8)
    if (first["width"], first["height"], last["width"], last["height"]) != (
        114688,
        100352,
        512,
        512,
    ):
        raise ValueError("verified source dimensions changed")
    if (first["sha256"], last["sha256"]) != (
        "0585eff1ddb2ec9a5d9863ec378cad210728d51db770cfd29bc798e7489ebc8c",
        "9b8cd0f2f777c3a2586fc1ca28f29e5d988d4264ccc9b7c4177a50100fd12645",
    ):
        raise ValueError("IFD index/byte hashes disagree")
    stride = 256 * 16
    cols = (first["width"] + stride - 1) // stride
    rows = (first["height"] + stride - 1) // stride
    if (cols, rows, first["height"] - (rows - 1) * stride) != (28, 25, 2048):
        raise ValueError("grid geometry changed")
    task_rows = json.loads(
        (
            root
            / ".local/explainers/core-20260929/interpretation-a-source/pinned-source/tasks/tumor_area_selection_pathology_slide_0001/environment/workspace/benchmark_tasks.json"
        ).read_text()
    )
    if len(task_rows) != 1 or task_rows[0]["task_id"] != "slide_0001":
        raise ValueError("public task row changed")
    source = {
        "role": "symbolic-absent-WSI-input",
        "title": "slide_0001 · source image withheld from collection pack",
        "input": "/data/slide/current/slide.tif",
        "input_available_in_pack": False,
        "native_geometry_from_local_source_audit": {
            "width_px": 114688,
            "height_px": 100352,
            "level": 0,
        },
        "analysis_tile_size_px": 256,
        "analysis_downsample": 16,
        "tile_level0_stride_px": 4096,
        "grid_cols": 28,
        "grid_rows": 25,
        "last_row_height_level0_px": 2048,
        "notice": {
            "label": "Source image withheld · symbolic grid",
            "text": "No slide pixels: CAMELYON16 reuse permissions remain unresolved. Obtain registered access and permission through the official route. Grid only; no tumor labels or result.",
            "url": "https://camelyon16.grand-challenge.org/Rules/",
            "link_label": "CAMELYON16 rules and access",
        },
        "private_mask": None,
        "task_id": "slide_0001",
    }
    operation = {
        "type": "abstract-whole-slide-grid-search",
        "authored_schematic": True,
        "grid_domain": {"x": [0, 27], "y": [0, 24]},
        "grid_formula": "x=floor(level0_pixel_x/4096), y=floor(level0_pixel_y/4096)",
        "last_row_level0_height_px": 2048,
        "inspection_cursor_only": True,
        "tumor_threshold_from_public_row": 0.2,
        "tile_semantics": "Private verifier counts label-2 mask pixels; >=0.2 mask-patch fraction makes a gold-positive tile. No mask is present.",
        "source_gold": None,
        "predicted_tumor_tiles": None,
    }
    public_row = task_rows[0]
    output_data = {
        "path": "/workspace/submission.json",
        "role": "required-schema-only",
        "schema": {
            "task_id": "slide_0001",
            "instruction": "retain supplied instruction",
            "contains_tumor": "boolean, requested but not scored by tile evaluator",
            "predicted_tumor_tiles": "array of {x:int,y:int}",
        },
        "prediction": None,
        "reference": None,
        "score": None,
        "scorer_contract": {
            "metric": "deduplicated tile-set F1",
            "pass_threshold": 0.9,
            "coordinate_bounds_checked": False,
            "empty_sets_f1": 0,
            "submission_container": "one-row JSON list; results-list wrapper also accepted",
        },
    }
    files: dict[str, bytes] = {
        "source.json": encode(source),
        "operation.json": encode(operation),
        "public-task-row.json": encode(public_row),
        "output.json": encode(output_data),
        "NOTICE.md": (
            "Symbolic protocol only. No WSI image or mask pixels, tumor locations, prediction, or score are in this pack. Original CAMELYON16 access, intended use, and derived-image distribution terms require review: https://camelyon16.grand-challenge.org/Rules/\n"
        ).encode(),
        "DATA-LICENSE.txt": (
            "LicenseRef-TB3-symbolic-teaching\nAuthored grid geometry and text only; no CAMELYON16 image or label derivative.\n"
        ).encode(),
    }
    if any(name.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")) for name in files):
        raise AssertionError("source image bytes must not enter symbolic pack")
    manifest = {
        "id": "retained-healthagentbench-tumor-tiles-symbolic-v2",
        "frame": "symbolic-task-workflow",
        "units": "none",
        "license": "LicenseRef-TB3-symbolic-teaching",
        "label_license": "LicenseRef-TB3-symbolic-teaching",
        "reference_policy": "no-reference-assets",
        "checks": {
            "native_input": False,
            "private_reference": False,
            "model_run": False,
            "evaluator_run": False,
        },
        "sources": dict(sorted(source_hashes.items())),
        "assets": [
            {
                "file": name,
                "bytes": len(data),
                "sha256": sha(data),
                "role": "illustration",
                "provenance": "symbolic-protocol",
            }
            for name, data in sorted(files.items())
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        (output / name).write_bytes(data)
    (output / "manifest.json").write_bytes(encode(manifest))
    print(output)


if __name__ == "__main__":
    main()
