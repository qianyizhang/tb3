"""Read-only reconstruction of final saved contours for methodological analysis.

Requires NumPy, SciPy, NiBabel, scikit-image and Pillow. Never imports or executes
the submitted scripts. Stages use final saved contours, not historical snapshots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_fill_holes, distance_transform_edt, gaussian_filter, label
from skimage.draw import polygon


def dice(a: np.ndarray, b: np.ndarray) -> float:
    return float(2 * np.count_nonzero(a & b) / (int(a.sum()) + int(b.sum())))


def font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def edge(a: np.ndarray) -> np.ndarray:
    p = np.pad(a, 1)
    core = a.copy()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        core &= p[1 + dx : 1 + dx + a.shape[0], 1 + dy : 1 + dy + a.shape[1]]
    return a & ~core


def raster(points: list, shape: tuple[int, int]) -> np.ndarray:
    result = np.zeros(shape, bool)
    if points:
        polys = points if isinstance(points[0][0], list) else [points]
        for coords in polys:
            vertices = np.asarray(coords)
            rr, cc = polygon(vertices[:, 0], vertices[:, 1], shape=shape)
            result[rr, cc] = True
    return result


def reconstruct(data: dict, shape: tuple, smooth_ct: np.ndarray, threshold, sigma):
    anchors = {int(z): points for z, points in data.items()}
    zs = sorted(anchors)
    fields = np.zeros(shape, np.float32)
    last_z = None
    last_d = None
    for z in zs:
        m = raster(anchors[z], shape[:2])
        d = (
            distance_transform_edt(m) - distance_transform_edt(~m)
            if m.any()
            else np.full(m.shape, -3.0)
        )
        if last_z is not None:
            for k in range(last_z, z + 1):
                t = (k - last_z) / (z - last_z)
                fields[:, :, k] = last_d * (1 - t) + d * t
        last_z, last_d = z, d
    raw = fields > 0
    smooth = gaussian_filter(raw.astype(float), sigma=sigma) > 0.5
    trimmed = smooth.copy()
    if threshold is not None:
        inner = distance_transform_edt(smooth) > 2
        trimmed &= (smooth_ct > threshold) | inner
        for z in range(min(zs), max(zs) + 1):
            trimmed[:, :, z] = binary_fill_holes(trimmed[:, :, z])
    return raw, smooth, trimmed


def panel(ct, layers, crop, size=(345, 290)):
    x0, x1, y0, y1 = crop
    sl = (slice(x0, x1), slice(y0, y1))
    gray = np.uint8(np.clip((ct[sl].astype(float) + 100) / 300, 0, 1) * 255)
    rgb = np.repeat(gray[:, :, None], 3, axis=2)
    for mask, color in layers:
        rgb[edge(mask[sl])] = color
    image = Image.fromarray(rgb.transpose(1, 0, 2)[::-1])
    ratio = min(size[0] / image.width, size[1] / image.height)
    return image.resize(
        (round(image.width * ratio), round(image.height * ratio)), Image.Resampling.NEAREST
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--trial", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    work = args.trial / "artifacts/app/work"
    ct = np.load(work / "ct.npy", mmap_mode="r")
    smooth_ct = gaussian_filter(np.asarray(ct), 0.6)
    labels = json.loads((args.task / "tests/labels.json").read_text())["labels"]
    rows, masks, snapshots, anchors_all = [], {}, {}, {}
    thresholds = {1: -5, 2: -15, 3: -15, 5: -5, 7: -30, 8: -30, 9: -30}
    for item in labels:
        i, name = item["id"], item["name"]
        path = work / "contours" / (name + ".json")
        data = json.loads(path.read_text())
        anchors_all[name] = data
        raw, smooth, trimmed = reconstruct(
            data, ct.shape, smooth_ct, thresholds.get(i), 0.5 if i in (8, 9) else 0.65
        )
        gt = np.asanyarray(nib.load(args.task / "tests/reference" / item["file"]).dataobj).astype(
            bool
        )
        zs = sorted(int(z) for z, pts in data.items() if pts)
        row = {
            "id": i,
            "name": name,
            "anchor_slices": zs,
            "nonempty_anchors": len(zs),
            "median_gap_mm": float(np.median(np.diff(zs)) * 1.5),
            "max_gap_mm": int(max(np.diff(zs))) * 1.5,
            "contours_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "threshold_hu": thresholds.get(i),
            "raw_dice": dice(raw, gt),
            "smoothed_dice": dice(smooth, gt),
            "trimmed_dice": dice(trimmed, gt),
            "smoothing_changed_voxels": int(np.count_nonzero(raw != smooth)),
            "trim_and_fill_changed_voxels": int(np.count_nonzero(smooth != trimmed)),
            "raw_voxels": int(raw.sum()),
            "trimmed_voxels": int(trimmed.sum()),
        }
        rows.append(row)
        masks[i] = trimmed
        if i == 8:
            snapshots = {
                "raw": raw[:, :, 210].copy(),
                "smooth": smooth[:, :, 210].copy(),
                "trimmed": trimmed[:, :, 210].copy(),
                "gt": gt[:, :, 210].copy(),
            }
    masks[5] &= ~masks[4]
    masks[5] &= ~masks[6]
    vein = {
        188: (142, 163, 2.5),
        192: (143, 160, 3),
        196: (144, 157, 3),
        200: (147, 155, 3),
        204: (148, 152, 3),
        208: (150, 151, 2.5),
    }
    xx, yy = np.ogrid[: ct.shape[0], : ct.shape[1]]
    zs = sorted(vein)
    for z in range(zs[0], zs[-1] + 1):
        x, y, radius = (np.interp(z, zs, [vein[k][d] for k in zs]) for d in range(3))
        masks[7][:, :, z] &= ~(((xx - x) / radius) ** 2 + ((yy - y) / radius) ** 2 <= 1)
    for row, item in zip(rows, labels, strict=True):
        cc, n = label(masks[item["id"]])
        counts = np.bincount(cc.ravel())
        keep = np.array([np.argmax(counts[1:]) + 1]) if n else np.array([], dtype=int)
        reproduced = np.isin(cc, keep)
        original = np.asanyarray(
            nib.load(args.trial / "artifacts/app/answer/masks" / item["file"]).dataobj
        ).astype(bool)
        gt = np.asanyarray(nib.load(args.task / "tests/reference" / item["file"]).dataobj).astype(
            bool
        )
        row.update(
            final_dice=dice(original, gt),
            final_reconstruction_mismatch_voxels=int(np.count_nonzero(reproduced != original)),
        )
        # Final output is read only. Never replace it with a reconstruction.
        assert row["final_reconstruction_mismatch_voxels"] == 0, (item["name"], row)
        masks[item["id"]] = original

    canvas = Image.new("RGB", (1120, 830), "#111b29")
    draw = ImageDraw.Draw(canvas)
    draw.text((22, 15), "Where the boundary came from: right adrenal", font=font(28), fill="white")
    draw.text(
        (22, 55),
        "Final saved polygons -> interpolated slices -> limited intensity correction",
        font=font(18),
        fill="#b7c8da",
    )
    crop = (143, 183, 106, 145)
    data = anchors_all["adrenal_gland_right"]
    panels = [
        ("A. Drawn polygon, slice 208", 208, [(raster(data["208"], ct.shape[:2]), (83, 209, 239))]),
        ("B. No polygon, slice 210", 210, [(snapshots["raw"], (83, 209, 239))]),
        ("C. Drawn polygon, slice 212", 212, [(raster(data["212"], ct.shape[:2]), (83, 209, 239))]),
        (
            "D. Interpolated / smoothed",
            210,
            [(snapshots["raw"], (83, 209, 239)), (snapshots["smooth"], (255, 191, 92))],
        ),
        (
            "E. Final / reference",
            210,
            [(snapshots["gt"], (73, 225, 151)), (masks[8][:, :, 210], (255, 158, 73))],
        ),
        ("F. CT only, same slice", 210, []),
    ]
    for idx, (title, k, layers) in enumerate(panels):
        x, y = 20 + (idx % 3) * 370, 104 + (idx // 3) * 330
        draw.text((x, y), title, font=font(18), fill="white")
        im = panel(ct[:, :, k], layers, crop)
        canvas.paste(im, (x + (345 - im.width) // 2, y + 29))
    draw.text(
        (22, 775),
        "Blue: polygon/interpolation | Amber: smoothed/final | Green: reference (post-run only)",
        font=font(17),
        fill="#b7c8da",
    )
    draw.text(
        (22, 804),
        "2 slices = 3 mm. Final contours held fixed; panels reconstruct computation, not reasoning history.",
        font=font(16),
        fill="#b7c8da",
    )
    canvas.save(args.output / "adrenal-method.png")
    receipt = {
        "analysis": "post-hoc reconstruction with final saved contours; not new model outputs or altered scores",
        "all_final_masks_reproduced_exactly": True,
        "per_organ": rows,
        "primary_macro_dice_unchanged": float(np.mean([r["final_dice"] for r in rows])),
        "raw_interpolation_macro_dice": float(np.mean([r["raw_dice"] for r in rows])),
        "smoothed_macro_dice": float(np.mean([r["smoothed_dice"] for r in rows])),
        "trimmed_macro_dice": float(np.mean([r["trimmed_dice"] for r in rows])),
    }
    (args.output / "method-reconstruction.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "per_organ"}, indent=2))


if __name__ == "__main__":
    main()
