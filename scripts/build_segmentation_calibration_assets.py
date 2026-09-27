"""Derive native image/box/mask teaching layers from the retained tool calibration."""

import argparse
import base64
import hashlib
import io
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.measure import find_contours, grid_points_in_poly


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def build(root, out):
    out.mkdir(parents=True, exist_ok=False)
    audit_path = Path(
        "groups/anatomy-audit/presentation/sources/segmentation-calibration-audit.json"
    )
    audit = read(root / audit_path)
    pins, contour_pixels, png_pixels = {}, 0, 0

    def pin(path):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        if str(relative) in audit["source_pins"]:
            assert digest == audit["source_pins"][str(relative)]
        pins[str(relative)] = digest
        return root / relative

    def outline(mask):
        nonlocal contour_pixels
        paths = [
            p[:, ::-1] - 0.5 for p in find_contours(np.pad(mask, 1), 0.5, fully_connected="low")
        ]
        recovered = np.zeros(mask.shape, bool)
        for p in paths:
            assert np.all(p >= 0) and np.all(p <= [265, 265])
            recovered ^= grid_points_in_poly(mask.shape, p[:, ::-1] - 0.5)
        np.testing.assert_array_equal(recovered, mask)
        contour_pixels += mask.size
        return {"paths": [p.tolist() for p in paths], "pixels": int(mask.sum())}

    def png(rgb):
        nonlocal png_pixels
        gray = rgb[..., 0]
        np.testing.assert_array_equal(rgb, np.repeat(gray[..., None], 3, axis=-1))
        stream = io.BytesIO()
        Image.fromarray(gray).save(stream, format="PNG", optimize=True)
        raw = stream.getvalue()
        np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(raw))), gray)
        png_pixels += gray.size
        return "data:image/png;base64," + base64.b64encode(raw).decode()

    pin(audit_path)
    pin(Path(__file__))
    base = Path(".local/sam-lite-bench-20260921")
    manifest = read(pin(base / "samples/manifest.json"))
    arrays = np.load(pin(base / "samples/arrays.npz"))
    tags = list(audit["aggregates"])
    outputs = {tag: np.load(pin(base / "results" / tag / "masks.npz")) for tag in tags}
    sources, predictions, references = {}, {}, {}
    for sample in manifest["samples"]:
        key = sample["id"]
        gt = arrays[key + "_gt"]
        union = gt.copy()
        predictions[key] = {}
        for tag, masks in outputs.items():
            predictions[key][tag] = {}
            for condition in ["tight", "loose"]:
                name = key + "_" + condition
                if name not in masks:
                    continue
                pred = masks[name]
                predictions[key][tag][condition] = outline(pred)
                union |= pred
        x0, y0, x1, y1 = sample["boxes"]["loose"]
        union[y0:y1, x0:x1] = True
        y, x = np.where(union)
        crop = [
            max(0, int(x.min()) - 8),
            max(0, int(y.min()) - 8),
            min(265, int(x.max()) + 9),
            min(265, int(y.max()) + 9),
        ]
        crop_mask = np.zeros_like(union)
        crop_mask[crop[1] : crop[3], crop[0] : crop[2]] = True
        assert not np.any(union & ~crop_mask)
        sources[key] = {
            **sample,
            "png": png(arrays[key + "_image"]),
            "width": 265,
            "height": 265,
            "detail_bounds_xyxy": crop,
            "lite_boxes_256": {
                c: (np.asarray(box) * (256 / 265)).astype(int).tolist()
                for c, box in sample["boxes"].items()
            },
            "sam2_boxes_1024": {
                c: (np.asarray(box, dtype=np.float32) / 265 * 1024).tolist()
                for c, box in sample["boxes"].items()
            },
        }
        references[key] = outline(gt)
    # Counts and selection expose reference information only in the reference layer.
    selections = [
        {k: s[k] for k in ["id", "organ", "q", "slice_k", "gt_pixels"]} for s in manifest["samples"]
    ]
    for view in sources.values():
        del view["gt_pixels"]
    dump(
        out / "source.json",
        {
            "schema": 1,
            "views": sources,
            "geometry": audit["geometry"],
            "window_hu": [-160, 240],
            "crop_policy": "Reader detail crop encloses every retained prediction, reference and both boxes plus 8 pixels; full native images retained. No crop at inference.",
        },
    )
    dump(
        out / "output.json",
        {
            "schema": 1,
            "views": predictions,
            "timing_denominators": audit["timing_denominators"],
            "timing": {
                tag: {k: v for k, v in agg.items() if k not in ["tight", "loose"]}
                for tag, agg in audit["aggregates"].items()
            },
        },
    )
    dump(
        out / "reference.json",
        {
            "schema": 1,
            "views": references,
            "samples": selections,
            **{
                k: audit[k]
                for k in [
                    "aggregates",
                    "controls",
                    "control_rows",
                    "per_organ",
                    "replays",
                    "paired_box_differences",
                    "backend_pairs",
                    "sam2_backend",
                    "sam2_cpu_subset_vs_full_repeat",
                    "selection_reconstruction",
                ]
            },
        },
    )
    licenses = Path(
        "groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/source/licenses"
    )
    for name in ["DATA-LICENSE.txt", "LABEL-LICENSE.txt"]:
        shutil.copyfile(pin(licenses / name), out / name)
    (out / "NOTICE.md").write_text("""# Retained segmentation-tool calibration layers

Source: TotalSegmentator v2.0.1, public CT case s1233, originally selected from
[Zenodo record 10047263](https://zenodo.org/records/10047263).
CT image data: CC-BY-4.0. Source labels: Apache-2.0. Exact license copies are retained.
Credit: Jakob Wasserthal and the TotalSegmentator contributors, *TotalSegmentator:
Robust Segmentation of 104 Anatomic Structures in CT Images* (2023),
[doi:10.1148/ryai.230024](https://doi.org/10.1148/ryai.230024).

The 2026-09-21 direct SAM 2.1 Small / LiteMedSAM calibration used official pinned
checkpoints on an Apple M5 Pro, 64 GiB unified memory, PyTorch 2.10 FP32, four CPU
threads. This asset builder replays saved bytes; it does not run those models.
Upstream SAM2 and LiteMedSAM code licenses are Apache-2.0. Model checkpoints are
not distributed in this pack. Provenance remains in the linked source audit.

All 18 native 265 by 265 RGB inputs have identical grayscale channels. Lossless
PNG retains that grayscale exactly. Display x=i and y=j increases down, fixed
native slice k; no radiological flip. Window [-160,240] HU was applied before
inference. The source volume is 265 by 265 by 401, with 1.5 mm isotropic spacing.
The affine and per-view k indices retain the connection to source coordinates.
Pixel centres are at (i+.5,j+.5) in SVG, corresponding to voxel index (i,j,k).

Source masks selected the 25th, 50th and 75th percentiles of nonempty slice
indices, using nearest-even rounding. Tight/wide boxes expand the reference
bounding rectangle by 2/10 native pixels (3/15 mm) per side, clipped to image
bounds. Native boxes are half-open xyxy. Both models receive the same full slice
and box, not the organ name or dense reference mask. Localization is privileged.

The pack includes all 116 saved masks: 72 primary MPS predictions, 8 prespecified
CPU checks and 36 additional SAM2 CPU predictions after the backend discrepancy.
Mask contours are traced at level .5; XOR rasterization at native pixel centres
reconstructs every mask exactly, including holes. A detail view always encloses
all saved CPU/MPS predictions, GT and both boxes for that sample. Crops are
reader aids derived after inference and may reveal target location. Full native
images remain available, and inference never used these crops.

Separate files preserve inputs, outputs/timing and reference/measurements. A
reader reference reveal is explanatory, not solver access. The supplied boxes
are already reference-derived. Inspecting a selected section does not establish
full-volume quality. Six middle slices are prespecified display examples; the
worst backend pair is explicitly selected after observing disagreement.

HD95 is the 95th percentile of concatenated bidirectional 2D surface distances
after 4-connected erosion, using 1.5 mm sampling. It is not the maximum of two
directional percentiles. Dice, precision and recall have their ordinary binary
pixel definitions. Backend mask-to-mask Dice is distinct from agreement with GT.
Model quality-head scores are not used as measured accuracy or calibrated confidence.

Timing separates one full-image encode from two cached box decodes. Denominators
are 18 unique encodes and 36 decodes per complete run, 2 and 4 per CPU subset.
Measured encode includes preprocessing; decode includes CPU mask return. Model
load, warmup and disk input are excluded. Memory counters are not additive and
do not establish total peak unified memory. CPU expansion is a diagnostic, not
an independent medical replication. Original masks and scores remain unchanged.

One known public CT, correlated slices, uncertain training overlap and privileged
localization do not establish autonomous localization, semantic naming, clinical
accuracy, 3D propagation or population generalization. Reference intent has not
been clinically adjudicated. No new trial or revised prompt is implied.

Rebuild: `python scripts/build_segmentation_calibration_assets.py --root . --output FRESH_DIRECTORY`.
""")
    assets = [
        {
            "file": p.name,
            "sha256": sha(p),
            "bytes": p.stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
        }
        for p in sorted(out.iterdir())
        if p.is_file()
    ]
    for path, digest in pins.items():
        assert sha(root / path) == digest
    checks = {
        "native_views": len(sources),
        "saved_masks": len(audit["replays"]),
        "png_pixels_roundtrip": png_pixels,
        "contour_pixels_roundtrip": contour_pixels,
        "detail_crops_preserve_all_saved_masks": True,
        "native_display_inverse": "exact",
        "audit_sha256": sha(root / audit_path),
        "builder_sha256": sha(Path(__file__)),
    }
    dump(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-segmentation-calibration-v1",
            "frame": "native-ijk",
            "units": "voxel",
            "license": "CC-BY-4.0",
            "label_license": "Apache-2.0",
            "reference_policy": "reader-reference-reveal",
            "sources": pins,
            "assets": assets,
            "checks": checks,
        },
    )
    print(
        json.dumps(
            {"checks": checks, "asset_bytes": {a["file"]: a["bytes"] for a in assets}}, indent=2
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output.resolve())
