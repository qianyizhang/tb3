"""Render paired WSI teaching views from selected retained files; no model inference."""

import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, ImageDraw

ROOT = Path(".local/wsi-ground-truth")
OUT = ROOT / "explainer" / "assets"


def xml_polygons(path):
    return [
        {
            "name": a.get("Name"),
            "group": a.get("PartOfGroup"),
            "color": a.get("Color"),
            "points": [[float(c.get("X")), float(c.get("Y"))] for c in a.findall(".//Coordinate")],
        }
        for a in ET.parse(path).findall(".//Annotation")
    ]


def area(points):
    p = np.asarray(points)
    return abs(np.dot(p[:, 0], np.roll(p[:, 1], 1)) - np.dot(p[:, 1], np.roll(p[:, 0], 1))) / 2


def tile_region(path, box):
    x, y, w, h = map(int, box)
    with tifffile.TiffFile(path) as t:
        p = t.pages[0]
        out = np.full((h, w, 3), 255, np.uint8)
        tw, th = p.tilewidth, p.tilelength
        cols = math.ceil(p.imagewidth / tw)
        offsets, counts, decode, tables = p.dataoffsets, p.databytecounts, p.decode, p.jpegtables
        for ty in range(
            max(0, y // th), min(math.ceil((y + h) / th), math.ceil(p.imagelength / th))
        ):
            for tx in range(max(0, x // tw), min(math.ceil((x + w) / tw), cols)):
                i = ty * cols + tx
                t.filehandle.seek(offsets[i])
                a, _, _ = decode(t.filehandle.read(counts[i]), i, jpegtables=tables)
                a = a[0]
                gx, gy = tx * tw, ty * th
                xa, ya = max(x, gx), max(y, gy)
                xb, yb = min(x + w, gx + tw, p.imagewidth), min(y + h, gy + th, p.imagelength)
                out[ya - y : yb - y, xa - x : xb - x] = a[ya - gy : yb - gy, xa - gx : xb - gx, :3]
    return Image.fromarray(out)


def thumb(path, page, ds):
    with tifffile.TiffFile(path) as t:
        w, h = t.pages[0].imagewidth, t.pages[0].imagelength
        if page is not None:
            im = Image.fromarray(t.pages[page].asarray()).crop(
                (
                    0,
                    0,
                    min(t.pages[page].imagewidth, math.ceil(w / ds)),
                    min(t.pages[page].imagelength, math.ceil(h / ds)),
                )
            )
        else:
            p = t.pages[0]
            im = Image.new("RGB", (math.ceil(w / ds), math.ceil(h / ds)), "white")
            tw, th = p.tilewidth, p.tilelength
            cols = math.ceil(w / tw)
            offsets, counts, decode, tables = (
                p.dataoffsets,
                p.databytecounts,
                p.decode,
                p.jpegtables,
            )
            for i in range(len(p.dataoffsets)):
                t.filehandle.seek(offsets[i])
                a, _, _ = decode(t.filehandle.read(counts[i]), i, jpegtables=tables)
                small = Image.fromarray(a[0, :, :, :3]).resize(
                    (tw // ds, th // ds), Image.Resampling.LANCZOS
                )
                im.paste(small, ((i % cols) * tw // ds, (i // cols) * th // ds))
    return im


def overlay(im, polys, colors, origin=(0, 0), ds=1, alpha=65, width=3):
    layer = Image.new("RGBA", im.size)
    d = ImageDraw.Draw(layer)
    for p in polys:
        color = colors.get(p["group"], p.get("color") or "#ef4444")
        rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
        xy = [((x - origin[0]) / ds, (y - origin[1]) / ds) for x, y in p["points"]]
        if len(xy) < 3:
            continue
        d.polygon(xy, fill=(*rgb, alpha))
        d.line([*xy, xy[0]], fill=(*rgb, 255), width=width)
    return layer


def save_view(key, label, im, layer, **info):
    im.save(OUT / (key + "-input.png"))
    im.save(OUT / (key + "-input.jpg"), quality=92)
    layer.save(OUT / (key + "-overlay.png"))
    Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB").save(
        OUT / (key + "-reference.png")
    )
    return dict(key=key, label=label, width=im.width, height=im.height, **info)


def bounds_crop(poly, size):
    a = np.array(poly["points"])
    cx, cy = (a.min(0) + a.max(0)) / 2
    return [round(cx - size / 2), round(cy - size / 2), size, size]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stats = {}
    views = {}
    # CAMELYON TIFF padding is not image extent: actual level-to-level transform is 2**level.
    src = ROOT / "camelyon/tumor_091.tif"
    polys = xml_polygons(ROOT / "camelyon/tumor_091.xml")
    colors = {"Tumor": "#ef3e5b", "Exclusion": "#00b8d9"}
    im = thumb(src, 6, 64)
    views["camelyon"] = [
        save_view(
            "camelyon-overview",
            "全片 overview",
            im,
            overlay(im, polys, colors, ds=64, width=2),
            downsample=64,
        )
    ]
    target = min([p for p in polys if p["group"] == "Tumor"], key=lambda p: area(p["points"]))
    box = bounds_crop(target, 1600)
    im = tile_region(src, box)
    views["camelyon"].append(
        save_view(
            "camelyon-detail",
            "GT 选出的局部 · 约 0.36 mm",
            im,
            overlay(im, polys, colors, origin=box[:2], width=5),
            crop_level0=box,
            selection="Smallest Tumor polygon by area; reader-only GT-selected crop",
        )
    )
    stats["camelyon"] = {
        "sample": "tumor_091",
        "dimensions": [61440, 53760],
        "mpp": 0.227273,
        "tumor_polygons": sum(p["group"] == "Tumor" for p in polys),
        "exclusion_polygons": sum(p["group"] == "Exclusion" for p in polys),
        "crop": box,
        "note": "Polygon count is not a connected-lesion count or clinical metastasis stage.",
    }
    # HiESD annotation XML is on the released 64x downsample grid.
    sid = "e4442edf-05b0-431b-bf61-ccf2d8cdebb6"
    src = ROOT / f"hiesd/{sid}.svs"
    polys = xml_polygons(ROOT / f"hiesd/ESD_40X_annotation_downsample64_xml/{sid}.xml")
    im = Image.open(ROOT / f"hiesd/ESD_40X_Thumbnail_downsample64/{sid}_thumbnail.png").convert(
        "RGB"
    )
    views["hiesd"] = [
        save_view(
            "hiesd-overview",
            "两条组织 · 低分辨率地图",
            im,
            overlay(im, polys, {}, alpha=85, width=1),
            downsample=64,
        )
    ]
    tumor = [p for p in polys if p["color"].upper() == "#8B0000"]
    target = max(tumor, key=lambda p: area(p["points"]))
    scaled = [{**p, "points": [[x * 64, y * 64] for x, y in p["points"]]} for p in polys]
    target = {**target, "points": [[x * 64, y * 64] for x, y in target["points"]]}
    box = bounds_crop(target, 2048)
    im = tile_region(src, box)
    views["hiesd"].append(
        save_view(
            "hiesd-detail",
            "GT 选出的腺体区 · 粗标注",
            im,
            overlay(im, scaled, {}, origin=box[:2], alpha=55, width=4),
            crop_level0=box,
            selection="Largest tub1 polygon on coarse annotation grid, mapped by x64; not exact gland borders",
        )
    )
    mask = np.array(Image.open(ROOT / f"hiesd/ESD_40X_annotation_downsample64/{sid}.png"))
    u = np.unique(mask.reshape(-1, 3), axis=0)
    stats["hiesd"] = {
        "sample": sid,
        "dimensions": [39887, 28702],
        "mpp": 0.2458,
        "annotation_dimensions": [623, 448],
        "annotation_downsample": 64,
        "annotation_unique_rgb": len(u),
        "xml_polygons": len(polys),
        "xml_colors": sorted({p["color"] for p in polys}),
        "crop": box,
        "strips": 2,
    }
    # HuBMAP selected released TIFF has one full-resolution plane.
    src = ROOT / "hubmap/aaa6a05cc.tiff"
    features = json.loads((ROOT / "hubmap/aaa6a05cc.json").read_text())
    polys = [{"group": "glomerulus", "points": f["geometry"]["coordinates"][0]} for f in features]
    colors = {"glomerulus": "#008f81"}
    assert all(
        f["geometry"]["type"] == "Polygon" and len(f["geometry"]["coordinates"]) == 1
        for f in features
    )
    im = thumb(src, None, 16)
    views["hubmap"] = [
        save_view(
            "hubmap-overview",
            "全片 · 肾小球清单",
            im,
            overlay(im, polys, colors, ds=16, width=2),
            downsample=16,
        )
    ]
    target = polys[0]
    box = bounds_crop(target, 1600)
    im = tile_region(src, box)
    views["hubmap"].append(
        save_view(
            "hubmap-detail",
            "GT 选出的局部 · 约 1.04 mm",
            im,
            overlay(im, polys, colors, origin=box[:2], width=4),
            crop_level0=box,
            selection="First source glomerulus, with surrounding tissue; reader-only selection",
        )
    )
    stats["hubmap"] = {
        "sample": "aaa6a05cc",
        "dimensions": [13013, 18484],
        "mpp": 0.65,
        "glomerulus_polygons": len(polys),
        "first_polygon_area_um2": area(target["points"]) * 0.65**2,
        "median_polygon_area_um2": float(np.median([area(p["points"]) * 0.65**2 for p in polys])),
        "crop": box,
    }
    # TIGER: exact released ROI masks and COCO boxes; no full-slide dense GT implied.
    src = ROOT / "tiger/114S.tif"
    polys = xml_polygons(ROOT / "tiger/114S.xml")
    roi_polys = [p for p in polys if p["group"] == "roi"]
    im = thumb(src, 6, 64)
    views["tiger"] = [
        save_view(
            "tiger-overview",
            "全片 · 标注仅在 3 个 ROI",
            im,
            overlay(im, roi_polys, {"roi": "#f59e0b"}, ds=64, alpha=50, width=3),
            downsample=64,
        )
    ]
    coco = json.loads((ROOT / "tiger/tiger-coco.json").read_text())
    palette = {
        1: "#e6425e",
        2: "#28a8c7",
        3: "#b678d4",
        4: "#f08c38",
        5: "#ae9566",
        6: "#88b929",
        7: "#8792a7",
    }
    roistats = []
    for j, i in enumerate(
        sorted([i for i in coco["images"] if "114S" in i["file_name"]], key=lambda i: i["id"])
    ):
        name = Path(i["file_name"]).name
        im = Image.open(ROOT / "tiger/rois" / name).convert("RGB")
        mask = np.array(Image.open(ROOT / "tiger/masks" / name))
        a = [a for a in coco["annotations"] if a["image_id"] == i["id"]]
        rgba = np.zeros((*mask.shape, 4), np.uint8)
        for v, c in palette.items():
            rgba[mask == v] = [int(c[k : k + 2], 16) for k in (1, 3, 5)] + [95]
        tissue = Image.fromarray(rgba)
        cells = Image.new("RGBA", im.size)
        d = ImageDraw.Draw(cells)
        counts = {str(k): 0 for k in range(8)}
        out = 0
        for ann in a:
            x, y, w, h = ann["bbox"]
            cx, cy = x + w / 2, y + h / 2
            d.rectangle((x, y, x + w, y + h), outline="#ffe600", width=2)
            if 0 <= cx < im.width and 0 <= cy < im.height:
                counts[str(int(mask[int(cy), int(cx)]))] += 1
            else:
                out += 1
        combined = Image.alpha_composite(tissue, cells)
        key = f"tiger-roi{j + 1}"
        v = save_view(
            key,
            f"ROI {j + 1} · {len(a)} 个细胞标记",
            im,
            combined,
            source_roi=name,
            selection="Source-defined annotated ROI, supplied helper for the proposed local task",
        )
        tissue.save(OUT / (key + "-tissue.png"))
        cells.save(OUT / (key + "-cells.png"))
        views["tiger"].append(v)
        bbox = list(map(int, re.search(r"\[(.*)\]", name).group(1).split(",")))
        mpp = 20000 / 43793
        # Compare the native TIFF crop with the released ROI PNG to verify coordinate interpretation.
        native = np.array(
            tile_region(src, [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]])
        )
        err = float(np.mean(np.abs(native.astype(float) - np.array(im).astype(float))))
        roistats.append(
            {
                "id": i["id"],
                "file": name,
                "bbox_level0_xyxy": bbox,
                "cell_boxes": len(a),
                "centroid_assignment_counts": counts,
                "centroids_outside_roi": out,
                "tissue_pixel_counts": {str(k): int((mask == k).sum()) for k in range(8)},
                "native_roi_rgb_mae": err,
                "mpp": mpp,
            }
        )
    stats["tiger"] = {
        "sample": "114S",
        "dimensions": [61504, 43392],
        "mpp": 20000 / 43793,
        "rois": roistats,
        "cell_category": coco["categories"],
    }
    (OUT.parent / "views.json").write_text(json.dumps(views, ensure_ascii=False, indent=2) + "\n")
    (OUT.parent / "measurements.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
