"""Derive native CT sections, frozen masks and saved prompts for a reader explainer."""

import argparse
import base64
import hashlib
import io
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from skimage.draw import polygon
from skimage.measure import find_contours

ATTEMPTS = {
    "xhigh": "2668797075454e54",
    "medium": "6979f136149c4e17",
    "sol": "7b643e5d3c7e4994",
    "tool": "bc57d5f3973843bc",
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, data):
    path.write_text(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n")


def outline(mask):
    # Pixel centres at (column+.5,row+.5); trace level .5 between binary samples.
    return [
        np.round(p[:, ::-1] - 0.5, 3).tolist()
        for p in find_contours(np.pad(mask, 1), 0.5, fully_connected="low")
    ]


def build(root, out):
    out.mkdir(parents=True, exist_ok=False)
    audit = read(root / "groups/anatomy-audit/presentation/sources/ct-organ-audit.json")
    pins, checked_pixels = {}, 0

    def pin(path):
        path = Path(path)
        digest = sha(root / path)
        if str(path) in audit["source_pins"]:
            assert digest == audit["source_pins"][str(path)]
        pins[str(path)] = digest
        return root / path

    task = Path(".local/ct-organ-segmentation-astra-xhigh/task")
    ctfile = pin(task / "environment/data/ct.nii.gz")
    image = nib.load(ctfile)
    ct = np.asarray(image.dataobj)
    labels = read(pin(task / "environment/data/labels.json"))["labels"]
    refs, outputs, metrics, works = {}, {}, {}, {}
    for item in labels:
        refs[item["id"]] = (
            np.asarray(nib.load(pin(task / "tests/reference" / item["file"])).dataobj) > 0
        )
    for key, aid in ATTEMPTS.items():
        trial = next((root / ".local/attempts" / ("attempt-" + aid) / "job").glob("task__*"))
        works[key] = (trial / "artifacts/app/work").relative_to(root)
        metrics[key] = read(pin((trial / "verifier/metrics.json").relative_to(root)))
        outputs[key] = {
            item["id"]: np.asarray(
                nib.load(
                    pin((trial / "artifacts/app/answer/masks" / item["file"]).relative_to(root))
                ).dataobj
            )
            > 0
            for item in labels
        }

    def png(array):
        nonlocal checked_pixels
        gray = np.uint8(np.clip((array + 160.0) / 400.0, 0, 1) * 255)
        stream = io.BytesIO()
        Image.fromarray(gray).save(stream, format="PNG", optimize=True)
        encoded = stream.getvalue()
        np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(encoded))), gray)
        checked_pixels += gray.size
        return "data:image/png;base64," + base64.b64encode(encoded).decode()

    def section(k, bounds):
        (a, b), (c, d) = bounds
        return ct[a:b, c:d, k].T[::-1]

    views, predictions, references = {}, {}, {}
    views["input"] = {
        "png": png(ct[:, 132, :].T[::-1]),
        "width": 265,
        "height": 401,
        "axis": "j",
        "index": 132,
        "horizontal": "R",
        "vertical": "S",
        "selection": "native centre coronal section; full scan supplied",
    }
    for item in labels:
        ident = item["id"]
        ref = refs[ident]
        k = int(np.argmax(ref.sum((0, 1))))
        union = ref[:, :, k] | outputs["medium"][ident][:, :, k] | outputs["tool"][ident][:, :, k]
        points = np.argwhere(union)
        lo = np.maximum(points.min(0) - 14, 0)
        hi = np.minimum(points.max(0) + 15, ct.shape[:2])
        bounds = np.stack([lo, hi], axis=1).tolist()
        name = str(ident)
        views[name] = {
            "png": png(section(k, bounds)),
            "width": int(hi[0] - lo[0]),
            "height": int(hi[1] - lo[1]),
            "index": k,
            "bounds_ij": bounds,
            "horizontal": "R",
            "vertical": "A",
            "selection": "largest reference cross-section; crop covers reference and both Astra/medium outputs",
        }
        a, b = bounds[0]
        c, d = bounds[1]
        references[name] = outline(ref[a:b, c:d, k].T[::-1])
        predictions[name] = {
            key: outline(output[ident][a:b, c:d, k].T[::-1])
            for key, output in outputs.items()
            if key in {"medium", "tool"}
        }
    # A consequential saved method: stomach anchors at k235 and k240, with four
    # between-anchor native planes. Reconstruct masks from literal coordinates only.
    contours = read(pin(works["medium"] / "contours.json"))["stomach"]
    fields = []
    for k in [235, 240]:
        p = np.asarray(contours[str(k)])
        mask = np.zeros(ct.shape[:2], bool)
        rows, cols = polygon(p[:, 0], p[:, 1], mask.shape)
        mask[rows, cols] = True
        fields.append(distance_transform_edt(mask) - distance_transform_edt(~mask))
    toolprov = read(pin(works["tool"] / "small/provenance.json"))
    anchors = read(pin(works["tool"] / "small_anchors.json"))
    # Fit all six planes together; a fixed hand-chosen crop clipped the k235
    # candidate superior edge. Preserve each complete displayed mask and box.
    method_points = []
    for k in range(235, 241):
        fraction = (k - 235) / 5
        raw = fields[0] * (1 - fraction) + fields[1] * fraction > 0
        with np.load(pin(works["tool"] / "small" / (str(k) + ".npz"))) as saved:
            index = list(saved["ids"]).index(6)
            candidate = saved["masks"][index][::-1].T
            x0, y0, x1, y1 = saved["boxes"][index]
        method_points.extend(
            np.argwhere(
                raw | candidate | outputs["medium"][6][:, :, k] | outputs["tool"][6][:, :, k]
            )
        )
        method_points.extend([[x0, 264 - y1], [x1, 264 - y0]])
    coordinates = np.asarray(method_points)
    lo = np.maximum(np.floor(coordinates.min(0)).astype(int) - 8, 0)
    hi = np.minimum(np.ceil(coordinates.max(0)).astype(int) + 9, ct.shape[:2])
    bounds = np.stack([lo, hi], axis=1).tolist()
    a, b = bounds[0]
    c, d = bounds[1]
    methods = []
    for k in range(235, 241):
        fraction = (k - 235) / 5
        raw = fields[0] * (1 - fraction) + fields[1] * fraction > 0
        pp = pin(works["tool"] / "small" / (str(k) + ".npz"))
        with np.load(pp) as saved:
            index = list(saved["ids"]).index(6)
            candidate = saved["masks"][index][::-1].T
            box = saved["boxes"][index].tolist()
        recorded = next(p["box"] for p in toolprov["jobs"][str(k)] if p["id"] == 6)
        np.testing.assert_allclose(box, recorded, atol=0, rtol=0)
        original_png = np.asarray(Image.open(pin(works["tool"] / "small" / (str(k) + ".png"))))
        # Cropped batch stores the full native windowed image before its 256px model resize.
        full = np.uint8(np.clip((ct[:, :, k].T[::-1] + 160.0) / 400.0, 0, 1) * 255)
        np.testing.assert_array_equal(original_png, full)
        views["method-" + str(k)] = {
            "png": png(section(k, bounds)),
            "width": b - a,
            "height": d - c,
            "index": k,
            "bounds_ij": bounds,
            "horizontal": "R",
            "vertical": "A",
            "selection": "reader-selected stomach crop from native pixels",
        }
        methods.append(
            {
                "k": k,
                "polygon_explicit": str(k) in contours,
                "box_explicit": str(k) in anchors["6"],
                "polygon_points": [[x - a + 0.5, d - y - 0.5] for x, y in contours.get(str(k), [])],
                "raw_polygon": outline(raw[a:b, c:d].T[::-1]),
                "box": [
                    box[0] - a + 0.5,
                    box[1] - (265 - d) + 0.5,
                    box[2] - box[0],
                    box[3] - box[1],
                ],
                "native_image_box_xyxy": box,
                "tool_candidate": outline(candidate[a:b, c:d].T[::-1]),
                "baseline_final": outline(outputs["medium"][6][a:b, c:d, k].T[::-1]),
                "tool_final": outline(outputs["tool"][6][a:b, c:d, k].T[::-1]),
            }
        )
    diagnostic = read(
        pin(Path("groups/anatomy-audit/findings/evidence/ct-organ-slice-construction-audit.json"))
    )
    dump(
        out / "source.json",
        {
            "shape": list(ct.shape),
            "affine": image.affine.tolist(),
            "spacing_mm": [1.5] * 3,
            "window_HU": [-160, 240],
            "labels": labels,
            "views": views,
        },
    )
    dump(
        out / "output.json",
        {
            "masks": predictions,
            "methods": methods,
            "provenance": {
                "medium": str(works["medium"]),
                "tool": str(works["tool"]),
                "tool_crop": toolprov["crop"],
                "checkpoint_sha256": toolprov["weights_sha256"],
            },
        },
    )
    supplement = read(pin(Path(".local/ct-organ-slice-audit/report/supplement.json")))
    matched_macro = {}
    for category in ["authored_polygon", "interpolated_shape"]:
        rows = [r for r in supplement["matched_per_organ"] if r["category"] == category]
        assert len(rows) == 10
        matched_macro[category] = {
            "n": sum(r["baseline"]["n"] for r in rows),
            "baseline": float(np.mean([r["baseline"]["dice"] for r in rows])),
            "tool": float(np.mean([r["tool"]["dice"] for r in rows])),
        }
    dump(
        out / "reference.json",
        {
            "masks": references,
            "metrics": metrics,
            "overlap_voxels": 57,
            "matched_macro": matched_macro,
            "same_baseline_strata": diagnostic["same_baseline_strata"],
            "construction": {
                k: {
                    "active": v["active_organ_slices"],
                    "raw": v["raw_macro_dice"],
                    "final": v["whole_macro_dice"],
                }
                for k, v in read(root / ".local/ct-organ-slice-audit/report/metrics.json")[
                    "conditions"
                ].items()
            },
        },
    )
    licenses = (
        root / "groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/source/licenses"
    )
    for name in ["DATA-LICENSE.txt", "LABEL-LICENSE.txt"]:
        shutil.copyfile(pin((licenses / name).relative_to(root)), out / name)
    (out / "NOTICE.md").write_text("""# CT organ segmentation reader pack

Source: TotalSegmentator v2.0.1 small dataset, s1233, Zenodo record 10047263.
Image data by the TotalSegmentator authors, CC BY 4.0; source label material,
Apache 2.0. Both exact retained notices accompany this derivative.
The source manifest and native receipt are in the anatomy-audit group.

This pack is a reader explanation, never a solver packet. It contains actual
windowed native CT pixels, submitted masks, saved prompt/candidate artifacts and
separately revealed private research references. All diagnostic view selection
occurred after submission. The initial centre section contains no masks.

Native shape 265 x 265 x 401, 1.5 mm isotropic, RAS positive directions. Axial
display columns increase i/right and rows decrease j/anterior; coronal rows
decrease k/superior. Pixel centres use half-pixel offsets. Source arrays are not
resampled. Gray window is [-160,240] HU. Contours trace the .5 level of padded
binary planes; masks remain separate, including the 57 reference overlaps.

The ten diagnostic views choose each reference's maximum-area axial section,
then a common crop covering reference and both medium predictions plus margin.
These are selected cross-sections, not a full 3D contour adjudication. The
displayed Dice values always score the full native 3D organ, not that crop.

Method views use k235-240. Baseline raw geometry is reconstructed from saved
stomach polygons and signed-distance interpolation; tool candidates are stored
small-batch masks, not fresh inference. Tool rectangles retain saved full-image
coordinates, transformed to the reader crop. The actual small-batch crop was
[75,60,225,210] in the 265px image, resized to 256px for learned inference.
Both explicit and interpolated boxes receive their own image-conditioned mask.
Later assembly unions candidates and applies filters/morphology. This numerical
comparison is not a chronological learning curve. The model's anatomical name
comes from the agent's job ID, not the box-only segmenter.

One public case and one attempt per condition; training overlap unknown. The
tool arm changes skill, instruction and runtime. Research labels are not a new
clinical adjudication. Original task and result bytes remain unchanged.

Rebuild with the existing imaging environment:
`python scripts/build_ct_organ_assets.py --root . --output FRESH_DIRECTORY`.
The manifest pins every input used and verifies PNG pixels and prompt mapping.
""")
    files = sorted(p for p in out.iterdir() if p.is_file())
    manifest = {
        "schema": 1,
        "id": "retained-ct-organ-v1",
        "frame": "RAS",
        "units": "mm",
        "license": "CC-BY-4.0",
        "label_license": "Apache-2.0",
        "reference_policy": "reader-reference-reveal",
        "sources": pins,
        "checks": {
            "png_pixels_roundtrip": checked_pixels,
            "native_views": len(views),
            "method_planes": 6,
            "saved_tool_image_pixels_matched": 6 * 265 * 265,
            "audit_sha256": sha(
                root / "groups/anatomy-audit/presentation/sources/ct-organ-audit.json"
            ),
            "builder_sha256": sha(Path(__file__)),
        },
        "assets": [
            {
                "file": p.name,
                "sha256": sha(p),
                "bytes": p.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
            }
            for p in files
        ],
    }
    dump(out / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "views": len(views),
                "pixels": checked_pixels,
                "files": {p.name: p.stat().st_size for p in out.iterdir()},
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output.resolve())
