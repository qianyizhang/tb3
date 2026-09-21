"""Render saved metrics and deterministic CT/GT/prediction review panels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def display_name(name: str) -> str:
    return name.replace("adrenal_gland", "adrenal").replace("_", " ").title()


def boundary(mask: np.ndarray) -> np.ndarray:
    inside = np.pad(mask, 1, constant_values=False)
    core = mask.copy()
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        core &= inside[1 + dx : 1 + dx + mask.shape[0], 1 + dy : 1 + dy + mask.shape[1]]
    return mask & ~core


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--answer", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    metrics = json.loads(args.metrics.read_text())
    labels = json.loads((args.task / "tests/labels.json").read_text())["labels"]
    chart = Image.new("RGB", (1100, 770), "#111b29")
    draw = ImageDraw.Draw(chart)
    draw.text((40, 28), "CT-only organ segmentation | Astra / xhigh", font=font(30), fill="white")
    draw.text(
        (40, 78),
        "One case | ten predefined organs | no pretrained segmenter weights",
        font=font(19),
        fill="#aebed0",
    )
    draw.text(
        (40, 122),
        f"Mean organ Dice: {metrics['semantic_macro_dice']:.3f}",
        font=font(26),
        fill="#6dd8eb",
    )
    draw.text((550, 124), "No label swaps in optimal matching", font=font(22), fill="white")
    x0, width = 250, 700
    for tick in range(6):
        x = x0 + int(width * tick / 5)
        draw.line((x, 195, x, 682), fill="#304054")
        draw.text((x - 12, 695), f"{tick / 5:.1f}", font=font(17), fill="#aebed0")
    for i, row in enumerate(metrics["per_label"]):
        y = 205 + i * 47
        draw.text((40, y + 3), display_name(row["name"]), font=font(20), fill="white")
        draw.rectangle((x0, y, x0 + int(width * row["dice"]), y + 29), fill="#54bfd5")
        draw.text((975, y + 2), f"{row['dice']:.3f}", font=font(21), fill="white")
    draw.text(
        (40, 740),
        "Dice measures overlap with the published reference; this is not a clinical pass/fail threshold.",
        font=font(17),
        fill="#aebed0",
    )
    chart.save(args.output / "organ-dice.png")

    ct = np.asanyarray(nib.load(args.task / "environment/data/ct.nii.gz").dataobj)
    review = Image.new("RGB", (1050, 100 + 260 * len(labels)), "#111b29")
    draw = ImageDraw.Draw(review)
    draw.text(
        (20, 12), "CT | source GT in green | agent mask in orange", font=font(24), fill="white"
    )
    draw.text(
        (20, 44),
        "Largest-GT-area axial slice per organ; identical crops. Anterior up, patient right to the right.",
        font=font(16),
        fill="#aebed0",
    )
    selections = []
    for i, label in enumerate(labels):
        gt = np.asanyarray(nib.load(args.task / "tests/reference" / label["file"]).dataobj).astype(
            bool
        )
        pred = np.asanyarray(nib.load(args.answer / label["file"]).dataobj).astype(bool)
        k = int(gt.sum(axis=(0, 1)).argmax())
        points = np.argwhere(gt[:, :, k] | pred[:, :, k])
        low = np.maximum(0, points.min(axis=0) - 15)
        high = np.minimum(ct.shape[:2], points.max(axis=0) + 16)
        sl = (slice(int(low[0]), int(high[0])), slice(int(low[1]), int(high[1])))
        gray = np.uint8(np.clip((ct[:, :, k][sl].astype(float) + 150) / 400, 0, 1) * 255)
        base = np.repeat(gray[:, :, None], 3, axis=2)
        y = 95 + 260 * i
        draw.text(
            (20, y),
            f"{display_name(label['name'])} | axial k={k} | Dice {metrics['per_label'][i]['dice']:.3f}",
            font=font(19),
            fill="white",
        )
        for col, mask, color in (
            (0, None, None),
            (1, gt[:, :, k][sl], (76, 232, 156)),
            (2, pred[:, :, k][sl], (255, 159, 72)),
        ):
            rgb = base.copy()
            if mask is not None:
                rgb[boundary(mask)] = color
            panel = Image.fromarray(rgb.transpose(1, 0, 2)[::-1])
            scale = min(325 / panel.width, 225 / panel.height)
            panel = panel.resize(
                (round(panel.width * scale), round(panel.height * scale)), Image.Resampling.NEAREST
            )
            review.paste(panel, (15 + col * 345 + (325 - panel.width) // 2, y + 30))
        selections.append(
            {
                "id": label["id"],
                "slice_k": k,
                "crop_min_ij": low.tolist(),
                "crop_max_ij_exclusive": high.tolist(),
            }
        )
    review.save(args.output / "organ-contours.png")
    (args.output / "render-selection.json").write_text(
        json.dumps(
            {
                "selection_rule": "axial maximum GT area, union crop with 15 voxel context",
                "note": "Illustrative slices do not evaluate full 3D quality.",
                "selections": selections,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
