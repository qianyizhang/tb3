"""Read-only charts and matched-plane overlays for the fixed three conditions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw, ImageFont


COLORS = [(90, 196, 237), (166, 211, 112), (246, 166, 90)]


def font(size):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def edge(mask):
    padded = np.pad(mask, 1)
    core = mask.copy()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        core &= padded[1 + dx : 1 + dx + mask.shape[0], 1 + dy : 1 + dy + mask.shape[1]]
    return mask & ~core


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    task = args.root / manifest["task"]
    conditions = manifest["conditions"]
    assert len(conditions) == 3
    labels = json.loads((task / "tests/labels.json").read_text())["labels"]
    metrics = [json.loads((args.root / c["metrics"]).read_text()) for c in conditions]
    for result in metrics:
        assert result["valid"]
        assert [r["id"] for r in result["per_label"]] == [r["id"] for r in labels]
    args.output.mkdir(parents=True, exist_ok=True)
    chart = Image.new("RGB", (1130, 830), "#111b29")
    draw = ImageDraw.Draw(chart)
    draw.text(
        (25, 20),
        "Same CT, same task: three fresh segmentation attempts",
        font=font(27),
        fill="white",
    )
    for i, (condition, result) in enumerate(zip(conditions, metrics, strict=True)):
        draw.text(
            (25 + i * 365, 70),
            f"{condition['title']}  mean {result['semantic_macro_dice']:.3f}",
            font=font(20),
            fill=COLORS[i],
        )
    for tick in range(6):
        x = 235 + tick * 140
        draw.line((x, 115, x, 760), fill="#334050")
        draw.text((x - 12, 772), f"{tick / 5:.1f}", font=font(16), fill="#bdc9d4")
    for index, item in enumerate(labels):
        y = 125 + index * 63
        name = item["name"].replace("adrenal_gland", "adrenal").replace("_", " ").title()
        draw.text((25, y + 10), name, font=font(20), fill="white")
        for c, result in enumerate(metrics):
            score = result["per_label"][index]["dice"]
            top = y + c * 16
            if score > 0:
                draw.rectangle((235, top, 235 + round(700 * score), top + 11), fill=COLORS[c])
            draw.text((965, top - 3), f"{score:.3f}", font=font(16), fill=COLORS[c])
    draw.text(
        (25, 805),
        "Dice against published research GT; one attempt per condition. No clinical threshold or population ranking.",
        font=font(16),
        fill="#bdc9d4",
    )
    chart.save(args.output / "organ-dice-comparison.png")

    ct = np.asanyarray(nib.load(task / "environment/data/ct.nii.gz").dataobj)
    selections = []
    for page in range(2):
        canvas = Image.new("RGB", (1200, 1350), "#111b29")
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (20, 14),
            "Identical CT planes and crops | contours compared after submission",
            font=font(25),
            fill="white",
        )
        titles = ["Published GT"] + [c["title"] for c in conditions]
        colors = [(76, 232, 156)] + COLORS
        for col, title in enumerate(titles):
            draw.text((20 + 300 * col, 58), title, font=font(22), fill=colors[col])
        for row, item in enumerate(labels[page * 5 : (page + 1) * 5]):
            gt = np.asanyarray(nib.load(task / "tests/reference" / item["file"]).dataobj).astype(
                bool
            )
            k = int(gt.sum(axis=(0, 1)).argmax())
            planes = [gt[:, :, k]]
            for condition in conditions:
                path = args.root / condition["masks"] / item["file"]
                planes.append(np.asanyarray(nib.load(path).dataobj)[:, :, k].astype(bool))
            points = np.argwhere(np.logical_or.reduce(planes))
            low = np.maximum(0, points.min(axis=0) - 15)
            high = np.minimum(ct.shape[:2], points.max(axis=0) + 16)
            sl = tuple(slice(int(a), int(b)) for a, b in zip(low, high, strict=True))
            gray = np.uint8(np.clip((ct[:, :, k][sl].astype(float) + 150) / 400, 0, 1) * 255)
            y = 100 + row * 242
            name = item["name"].replace("adrenal_gland", "adrenal").replace("_", " ").title()
            scores = " / ".join(f"{m['per_label'][page * 5 + row]['dice']:.3f}" for m in metrics)
            draw.text(
                (20, y), f"{name} | axial k={k} | model Dice: {scores}", font=font(20), fill="white"
            )
            for col, (mask, color) in enumerate(zip(planes, colors, strict=True)):
                rgb = np.repeat(gray[:, :, None], 3, axis=2)
                rgb[edge(mask[sl])] = color
                panel = Image.fromarray(rgb.transpose(1, 0, 2)[::-1])
                scale = min(280 / panel.width, 205 / panel.height)
                panel = panel.resize(
                    (round(panel.width * scale), round(panel.height * scale)),
                    Image.Resampling.NEAREST,
                )
                canvas.paste(panel, (10 + col * 300 + (280 - panel.width) // 2, y + 30))
            selections.append(
                {
                    "id": item["id"],
                    "slice_k": k,
                    "crop_min_ij": low.tolist(),
                    "crop_max_ij_exclusive": high.tolist(),
                }
            )
        draw.text(
            (20, 1324),
            "Largest-GT-area axial slice; union crop across all models. Anterior up, patient right to the right. Illustrative planes only.",
            font=font(16),
            fill="#bdc9d4",
        )
        canvas.save(args.output / f"organ-contours-comparison-{page + 1}.png")
    (args.output / "render-selection.json").write_text(
        json.dumps({"manifest": manifest, "selections": selections}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
