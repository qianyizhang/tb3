# ruff: noqa: RUF001 — Chinese teaching copy intentionally uses Chinese punctuation.
"""Build a local offline teaching viewer from canonical task briefs and frozen images."""

import base64
import json
from pathlib import Path

from tb3_medical.presentation import markdown
from tb3_medical.task_briefs import sections

ROOT = Path(".local/wsi-ground-truth")
OUT = ROOT / "explainer"
BASE = Path("groups/lesion-localization/presentation")


def image(path):
    p = Path(path)
    mime = "image/png" if p.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def build():
    views = json.loads((OUT / "views.json").read_text())
    s = json.loads((OUT / "measurements.json").read_text())
    config = {
        "camelyon": {
            "brief": "wsi-camelyon-search",
            "short": "CAMELYON16",
            "tagline": "搜索病灶 · 从全片到局部",
            "legend": [["#ef3e5b", "肿瘤区域"], ["#00b8d9", "排除区域"]],
            "reading": [
                "低倍：先找淋巴结组织。",
                "局部：观察细胞、脂肪与可疑区域。",
                "显示 参考标注：对照局部目标在全片的位置。",
            ],
            "insight": [
                "本例阳性区域较大，不代表最难的小病灶。",
                "局部由 参考标注 选中；全片任务须自主找到位置。",
            ],
            "overviewCaption": "全片缩略图：64× 下采样，已去除额外填充。",
            "caveat": "仅一张阳性教学片；局部裁图由参考标注选定，未运行模型。",
            "scaleNote": "标尺：TIFF 第 0 层，0.227273 µm/px。",
            "numbers": "<ul><li><strong>Tumor：</strong>6 个多边形。</li><li><strong>Exclusion：</strong>1 个多边形。</li><li><strong>计数前：</strong>处理重叠、相邻区域与排除区。</li></ul>",
        },
        "hiesd": {
            "brief": "wsi-hiesd-map",
            "short": "HiESD",
            "tagline": "组织地图 · 从局部到汇总",
            "legend": [
                ["#8B0000", "tub1 高分化腺癌"],
                ["#8A2BE2", "正常腺体"],
                ["#0000FF", "慢性胃炎"],
                ["#00FF00", "淋巴滤泡"],
                ["#008000", "完全型肠化"],
                ["#FFFF00", "不完全型肠化"],
            ],
            "reading": [
                "全片：同一张片上的两条胃组织。",
                "显示 参考标注：沿组织条观察六类区域分布。",
                "局部：查看粗轮廓与成组腺体的关系。",
            ],
            "insight": [
                "无颜色 = 未标注，不能自动归为正常。",
                "粗图 1 px ≈ 原生 64 × 64 px；边长约 15.73 µm。",
            ],
            "overviewCaption": "官方缩略图：623 × 448 px；参考标注 为同网格 XML。",
            "caveat": "粗粒度、部分区域标注适合组织地图，不支持精确腺体或切缘评分；未运行模型。",
            "scaleNote": "标尺：原生 0.2458 µm/px；XML 坐标需乘 64。",
            "numbers": "<ul><li><strong>组织：</strong>2 条。</li><li><strong>XML：</strong>6 类、88 个多边形。</li><li><strong>PNG：</strong>1,569 种 RGB，量化前须审核编码。</li></ul>",
        },
        "hubmap": {
            "brief": "wsi-hubmap-inventory",
            "short": "HuBMAP",
            "tagline": "对象清单 · 数量与面积",
            "legend": [["#008f81", "肾小球轮廓"]],
            "reading": [
                "找肾小球：近圆形毛细血管团；注意区分肾小管。",
                "显示 参考标注：检查对象在全片的分布。",
                "局部：核查轮廓，将像素面积换算为 µm²。",
            ],
            "insight": [
                "99 是来源 参考标注 对象数，非模型成绩。",
                "中央参考对象：约 15,458 µm²。面积不代表病理分级。",
            ],
            "overviewCaption": "全片缩略图：16× 下采样；黑色边缘来自源图像。",
            "caveat": "一张训练切片和 99 个来源参考对象；不含疾病分级，也未运行模型。",
            "scaleNote": "标尺：0.65 µm/px；像素面积 × 0.65² → µm²。",
            "numbers": f"<ul><li><strong>参考对象：</strong>99 个。</li><li><strong>首个面积：</strong>{s['hubmap']['first_polygon_area_um2']:,.2f} µm²。</li><li><strong>面积中位数：</strong>{s['hubmap']['median_polygon_area_um2']:,.2f} µm²。</li><li><strong>算法：</strong>多边形几何面积；与栅格计数可有边缘差异。</li></ul>",
        },
        "tiger": {
            "brief": "wsi-tiger-context",
            "short": "TIGER",
            "tagline": "上下文计数 · 细胞属于哪里",
            "legend": [
                ["#e6425e", "1 浸润性肿瘤"],
                ["#28a8c7", "2 肿瘤相关基质"],
                ["#f08c38", "4 健康腺体"],
                ["#88b929", "6 炎症基质"],
                ["#8792a7", "7 其他"],
                ["#ffe600", "淋巴细胞 + 浆细胞框"],
            ],
            "reading": [
                "全片：找到三个已标注 ROI。",
                "ROI：分别打开组织色块与黄色细胞框。",
                "比较 ROI：细胞数量、所在区室、面积分母。",
            ],
            "insight": [
                "参考标注 仅覆盖选定 ROI，框外不能当负例。",
                "细胞框给位置，组织色块给区室；关联后才能分类计数。",
            ],
            "overviewCaption": "全片缩略图：64×；参考标注 橙框标记三个 ROI。",
            "caveat": "密集细胞标注仅覆盖选定 ROI；淋巴细胞与浆细胞已合并，未运行模型。",
            "scaleNote": "标尺：0.456694 µm/px；三个 ROI 均与原生裁图逐像素一致。",
            "numbers": "",
        },
    }
    english = {
        "camelyon": {
            "tagline": "Lesion search · whole slide to detail",
            "legend": [["#ef3e5b", "Tumor region"], ["#00b8d9", "Excluded region"]],
            "reading": [
                "Survey the lymph-node tissue at low magnification.",
                "Inspect suspicious cells and tissue at higher magnification.",
                "Reveal the reference to locate this region on the whole slide.",
            ],
            "insight": [
                "This positive example has large regions; it does not represent the hardest tiny lesions.",
                "The crop was chosen from the reference, so it cannot test autonomous search.",
            ],
            "overviewCaption": "Full-slide thumbnail, downsampled 64× with padding removed.",
            "scaleNote": "Level-0 source scale: 0.227273 µm/pixel.",
            "numbers": "<ul><li>Six Tumor polygons and one Exclusion polygon.</li><li>Polygon count is not connected-lesion count.</li></ul>",
            "viewLabels": ["Whole-slide input", "Reference-selected crop · about 0.36 mm"],
            "selection": "Reference-selected teaching crop; search is already solved.",
            "caveat": "One positive teaching slide. The crop was chosen from the reference; no model was run.",
        },
        "hiesd": {
            "tagline": "Tissue map · local findings to strip summary",
            "legend": [
                ["#8B0000", "tub1 adenocarcinoma"],
                ["#8A2BE2", "Normal gland"],
                ["#0000FF", "Chronic gastritis"],
                ["#00FF00", "Lymphoid follicle"],
                ["#008000", "Complete intestinal metaplasia"],
                ["#FFFF00", "Incomplete intestinal metaplasia"],
            ],
            "reading": [
                "Find the two strips on the same slide.",
                "Reveal the coarse reference regions across each strip.",
                "Zoom in to compare region outlines with grouped glands.",
            ],
            "insight": [
                "Uncolored tissue is unannotated, not automatically normal.",
                "The coarse grid groups glands; it is not an exact gland boundary.",
            ],
            "overviewCaption": "Official 623 × 448-pixel thumbnail; XML uses the same coarse grid.",
            "scaleNote": "Source scale: 0.2458 µm/pixel. Multiply XML coordinates by 64.",
            "numbers": "<ul><li>Two strips; 88 XML regions in six classes.</li><li>The category PNG has interpolation colors and needs encoding review before counting classes.</li></ul>",
            "viewLabels": ["Two tissue strips · coarse map", "Reference-selected gland region"],
            "selection": "Reference-selected teaching crop; search is already solved.",
            "caveat": "Coarse, partly annotated regions support mapping, not exact gland or margin scoring. No model was run.",
        },
        "hubmap": {
            "tagline": "Object inventory · count and area",
            "legend": [["#008f81", "Glomerulus outline"]],
            "reading": [
                "Look for rounded glomeruli among tubules.",
                "Reveal how reference objects are distributed across the slide.",
                "Zoom in to inspect a contour and its physical area.",
            ],
            "insight": [
                "The 99 objects are source reference polygons, not a model score.",
                "Area describes geometry; it does not establish a disease grade.",
            ],
            "overviewCaption": "Full-slide thumbnail downsampled 16×; dark edges are in the source image.",
            "scaleNote": "Source scale: 0.65 µm/pixel; multiply pixel area by 0.65² for µm².",
            "numbers": f"<ul><li>99 source reference objects.</li><li>First polygon: {s['hubmap']['first_polygon_area_um2']:,.0f} µm²; median: {s['hubmap']['median_polygon_area_um2']:,.0f} µm².</li><li>Geometric and raster areas may differ at edges.</li></ul>",
            "viewLabels": [
                "Whole-slide input · glomerulus inventory",
                "Reference-selected crop · about 1.04 mm",
            ],
            "selection": "Reference-selected teaching crop; search is already solved.",
            "caveat": "One training slide with 99 source reference objects; no disease grades or model run.",
        },
        "tiger": {
            "tagline": "Contextual counting · where each cell belongs",
            "legend": [
                ["#e6425e", "Invasive tumor"],
                ["#28a8c7", "Tumor-associated stroma"],
                ["#f08c38", "Healthy glands"],
                ["#88b929", "Inflamed stroma"],
                ["#8792a7", "Other"],
                ["#ffe600", "Lymphocyte/plasma-cell boxes"],
            ],
            "reading": [
                "Find the three annotated ROIs on the whole slide.",
                "Open tissue colors and yellow cell boxes separately.",
                "Compare counts, compartments, and annotated area across ROIs.",
            ],
            "insight": [
                "Dense reference covers selected ROIs only; outside areas are not negative cases.",
                "Link cell boxes to tissue compartments before counting by compartment.",
            ],
            "overviewCaption": "Full-slide thumbnail, downsampled 64×; orange boxes locate three ROIs.",
            "scaleNote": "Source scale: 0.456694 µm/pixel; the three paired ROI images match native crops.",
            "numbers": "",
            "viewLabels": [
                "Whole slide · three annotated ROIs",
                "ROI 1 · 175 cell boxes",
                "ROI 2 · 323 cell boxes",
                "ROI 3 · 20 cell boxes",
            ],
            "selection": "Official annotated ROI; its location is supplied.",
            "caveat": "Only selected ROIs have dense cell labels. Lymphocytes and plasma cells are merged; no model was run.",
        },
    }
    rs = s["tiger"]["rois"]
    rows = ""
    for k, r in enumerate(rs, 1):
        counts = r["centroid_assignment_counts"]
        n = int(counts["2"]) + int(counts["6"])
        pixels = r["tissue_pixel_counts"]["2"] + r["tissue_pixel_counts"]["6"]
        area = pixels * r["mpp"] ** 2 / 1e6
        density = f"{n / area:,.1f}" if area else "—"
        rows += f"<tr><td>{k}</td><td>{r['cell_boxes']}</td><td>{n}</td><td>{area:.4f}</td><td>{density}</td></tr>"
    config["tiger"]["numbers"] = (
        '<table class="stats-table"><tr><th>ROI</th><th>全部框</th><th>class 2+6 内</th><th>2+6 面积 mm²</th><th>细胞/mm²</th></tr>'
        + rows
        + "</table><ul><li><strong>归属：</strong>取框中心像素的组织类别。</li><li><strong>区室：</strong>合并 class 2 + 6。</li><li><strong>ROI 3：</strong>该区室面积为 0，密度未定义。</li><li><strong>区别：</strong>该密度不是临床 sTIL 百分比。</li></ul>"
    )
    english["tiger"]["numbers"] = (
        '<table class="stats-table"><tr><th>ROI</th><th>Cell boxes</th><th>Cells in 2+6</th><th>Area 2+6 mm²</th><th>Cells/mm²</th></tr>'
        + rows
        + "</table><p>Boxes are assigned by center pixel. Classes 2 and 6 are combined; ROI 3 has zero annotated area in that combination, so density is undefined. This is not a clinical sTIL percentage.</p>"
    )
    for key, d in config.items():
        raw = sections((BASE / "briefs" / (d["brief"] + ".md")).read_text())
        raw_en = sections((BASE / "briefs" / (d["brief"] + ".en.md")).read_text())
        d["title"] = raw["title"]
        d["sections"] = {
            k: markdown(v, lambda url: url if url.startswith(("https://", "http://")) else None)
            for k, v in raw.items()
            if not k.startswith("Visual explanation")
        }
        english[key]["title"] = raw_en["title"]
        english[key]["sections"] = {
            k: markdown(v, lambda url: url if url.startswith(("https://", "http://")) else None)
            for k, v in raw_en.items()
            if not k.startswith("Visual explanation")
        }
        d["locales"] = {"en": english[key]}
        d["mpp"] = s[key]["mpp"]
        d["views"] = views[key]
        for v in d["views"]:
            if v.get("selection"):
                v["selection"] = (
                    "官方标注 ROI；局部任务已知位置。"
                    if key == "tiger"
                    else "GT 选定的教学裁图；已移除搜索工作。"
                )
            for kind, suffix in [("input", "-input.jpg"), ("overlay", "-overlay.png")]:
                v[kind] = image(OUT / "assets" / (v["key"] + suffix))
            if key == "tiger" and v["key"] != "tiger-overview":
                v["tissue"] = image(OUT / "assets" / (v["key"] + "-tissue.png"))
                v["cells"] = image(OUT / "assets" / (v["key"] + "-cells.png"))
    template = (BASE / "wsi-sample-tour.html").read_text()
    payload = json.dumps(config, ensure_ascii=False).replace("</", "<\\/")
    metadata = json.dumps(
        json.loads((OUT / "provenance.json").read_text()), ensure_ascii=False
    ).replace("</", "<\\/")
    (OUT / "index.html").write_text(
        template.replace('"__DATA__"', payload).replace('"__META__"', metadata)
    )
    print(OUT / "index.html", (OUT / "index.html").stat().st_size)


if __name__ == "__main__":
    build()
