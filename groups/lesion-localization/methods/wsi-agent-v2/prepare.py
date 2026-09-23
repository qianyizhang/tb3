"""Build fresh, local WSI diagnostic tasks from retained source bytes.

Run explicitly in the prebuilt tb3-wsi-agent-runtime:v1 image with this checkout
mounted at /repo. This script refuses to replace an existing destination.
"""

import hashlib
import importlib.util
import json
import math
import random
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_erosion, label
from skimage.draw import polygon as raster_polygon

ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).resolve().parent
SOURCE = ROOT / ".local/wsi-ground-truth"
OLD = ROOT / ".local/wsi-agent-v1"
DEST = ROOT / ".local/wsi-agent-v2"
CAMELYON = SOURCE / "camelyon"
CAM_MPP = 0.227273
CAM_DOWNSAMPLE = 16
CAM_CONNECT_UM = 50
CAM_NEW = {
    "tumor_084.tif": (
        838426602,
        "73c9766616c40aff2bd6315eb44cd39e7b3d6bb7292cb52e25d3872256baee30",
    ),
    "normal_108.tif": (
        326607275,
        "f606e8ef726a42840a2e0d33d3ffcd1afe9ea52ff98ef0880502958c2a07fe3c",
    ),
}
CLASSES = {
    1: "chronic gastritis",
    2: "complete intestinal metaplasia",
    3: "lymphoid follicle",
    4: "normal glands",
    5: "well differentiated adenocarcinoma, tub1",
    6: "incomplete intestinal metaplasia",
}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def put_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def source_check() -> dict:
    checksums = (SOURCE / "source-metadata/camelyon-checksums.md5").read_text()
    result = {}
    for filename, (size, digest) in CAM_NEW.items():
        path = CAMELYON / filename
        if path.stat().st_size != size or sha256(path) != digest:
            raise ValueError(f"Source byte mismatch: {path}")
        if f"*images/{filename}" not in checksums:
            raise ValueError(f"Publisher checksum missing: {filename}")
        result[filename] = {"bytes": size, "sha256": digest}
    return result


def copy_task(kind: str, old_variant: str, new_variant: str, *, skip_slide: bool = False) -> Path:
    original = OLD / kind / old_variant / "task"
    task = DEST / kind / new_variant / "task"
    if task.exists():
        raise FileExistsError(task)

    def ignore(folder: str, names: list[str]) -> set[str]:
        return (
            {"slide.tif", "overview.jpg"} & set(names)
            if skip_slide and folder.endswith("environment/data")
            else set()
        )

    shutil.copytree(original, task, ignore=ignore)
    shutil.copyfile(METHOD / "score.py", task / "tests/score.py")
    lines = (task / "task.toml").read_text().splitlines()
    image_lines = [i for i, line in enumerate(lines) if line.startswith("docker_image = ")]
    if len(image_lines) != 2:
        raise ValueError(f"Expected two image fields in {task}")
    stem = f"tb3-wsi-v2-{kind}-{new_variant}"
    lines[image_lines[0]] = f'docker_image = "{stem}-evaluator:v1"'
    lines[image_lines[1]] = f'docker_image = "{stem}-solver:v1"'
    (task / "task.toml").write_text("\n".join(lines) + "\n")
    return task


def set_instruction(task: Path, instruction: str) -> None:
    (task / "instruction.md").write_text(instruction.strip() + "\n")


def set_reference(
    task: Path, reference: dict, oracle: dict, *, filename: str = "points.json"
) -> None:
    put_json(task / "tests/reference/reference.json", reference)
    put_json(task / "solution/reference" / filename, oracle)
    (task / "solution/solve.sh").write_text(
        "#!/bin/sh\nset -eu\nmkdir -p /app/answer\n"
        f"cp /solution/reference/{filename} /app/answer/{filename}\n"
    )
    (task / "solution/solve.sh").chmod(0o755)


def hubmap() -> Path:
    task = copy_task("hubmap", "image-only", "reference-recall")
    reference = json.loads((task / "tests/reference/reference.json").read_text())
    oracle = json.loads((task / "solution/reference/points.json").read_text())
    set_reference(task, reference, oracle)
    set_instruction(
        task,
        """
# Whole-slide glomerulus inventory

Inspect the complete PAS kidney TIFF. Return one level-0 center for each
glomerular profile you judge to be present. Include uncertain or altered profiles
with an optional confidence (0 to 1) and short note; do not silently discard
them. Avoid duplicate points. Save `/app/answer/points.json` as
`{"points":[{"x":123,"y":456,"confidence":0.8,"note":"uncertain"}]}`.

Inputs: `/app/data/slide.tif` and GT-free `/app/data/overview.jpg`. The level-0
image is 13013 x 18484 pixels at 0.65 micrometers per pixel. Read crops with
`python /app/tools/read_slide.py X Y WIDTH HEIGHT /app/work/tile.png`.

The private reference has source glomerulus polygons, all labeled only
"glomerulus". It has no sclerosis subtype or explicit inclusion rule for
partial and altered profiles. The main measure is recall against those polygons;
unmatched points enter a review queue and are not called false positives. The
source polygons and any GT-selected details are withheld from you.
""",
    )
    return task


def tiger_instruction(mask_supplied: bool) -> str:
    mask_line = (
        "Official tissue masks are `/app/data/roi1-tissue.png` through `roi3-tissue.png`.\n"
        "Read their integer pixel codes at your submitted points."
        if mask_supplied
        else "No tissue mask is supplied; infer the compartment from the H&E images."
    )
    return f"""
# Tissue-conditioned immune-cell inventory

Three fixed H&E regions are `/app/data/roi1.png` through `roi3.png`.
Mark centers of lymphocytes and plasma cells as one merged cell class. For each
center return a tissue code in `/app/answer/points.json`:
`{{"points":[{{"roi":"roi1","x":123,"y":456,"compartment":2}}]}}`.
Coordinates are local to each ROI. {mask_line}

Official TIGER tissue codes: 0 unannotated/unknown; 1 invasive tumor;
2 tumor-associated connective-tissue stroma; 3 in-situ tumor; 4 healthy glands;
5 non-in-situ necrosis; 6 inflamed tumor-associated stroma with high lymphocyte
density; 7 other/rest tissue such as healthy stroma, adipose tissue or artifacts.
Code 6 is the inflamed subset of tumor-associated stroma, not generic
inflammation anywhere. Use 0 when the local tissue cannot be determined.

A submitted point may match a source cell center within 20 ROI pixels. The
primary compartment comparison reads the source mask at that matched source
cell center; a second diagnostic comparison reads it at your submitted point.
Both conventions and the 20-pixel boundary band will be reported. The source
cell positions and the private scorer remain withheld. These ROIs test local
cell/context reasoning, not autonomous whole-slide search or clinical sTIL score.
"""


def tiger(mask_supplied: bool) -> Path:
    variant = "tissue-supplied" if mask_supplied else "image-only"
    task = copy_task("tiger", variant, variant)
    reference = json.loads((task / "tests/reference/reference.json").read_text())
    oracle = json.loads((task / "solution/reference/points.json").read_text())
    set_reference(task, reference, oracle)
    set_instruction(task, tiger_instruction(mask_supplied))
    return task


def source_polygons(xml_path: Path) -> tuple[list[list[list[float]]], list[list[list[float]]]]:
    tumor, exclusion = [], []
    for annotation in ET.parse(xml_path).findall(".//Annotation"):
        points = [
            [float(item.get("X")), float(item.get("Y"))]
            for item in annotation.findall(".//Coordinate")
        ]
        group = annotation.get("PartOfGroup")
        if group == "Tumor":
            tumor.append(points)
        elif group == "Exclusion":
            exclusion.append(points)
    return tumor, exclusion


def polygon_pixels(
    points: list[list[float]], shape: tuple[int, int]
) -> tuple[np.ndarray, np.ndarray]:
    coordinates = np.asarray(points) / CAM_DOWNSAMPLE
    return raster_polygon(coordinates[:, 1], coordinates[:, 0], shape=shape)


def lesion_groups(
    polygons: list[list[list[float]]], width: int, height: int
) -> tuple[list[list[int]], list[np.ndarray]]:
    if not polygons:
        return [], []
    shape = (math.ceil(height / CAM_DOWNSAMPLE), math.ceil(width / CAM_DOWNSAMPLE))
    union = np.zeros(shape, dtype=bool)
    rasterized = []
    for points in polygons:
        rr, cc = polygon_pixels(points, shape)
        if not len(rr):
            raise ValueError("Tumor polygon vanished at grouping resolution")
        union[rr, cc] = True
        rasterized.append(np.stack((rr, cc), axis=1))
    # Dilate each side by ~25 um; touching components are a 50 um study group.
    radius = math.ceil(CAM_CONNECT_UM / CAM_MPP / CAM_DOWNSAMPLE / 2)
    yy, xx = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    footprint = xx * xx + yy * yy <= radius * radius
    connected, _ = label(binary_dilation(union, structure=footprint))
    by_label: dict[int, list[int]] = {}
    for index, pixels in enumerate(rasterized):
        ids = np.unique(connected[pixels[:, 0], pixels[:, 1]])
        ids = ids[ids != 0]
        if len(ids) != 1:
            raise ValueError(f"Polygon {index} has ambiguous group labels: {ids}")
        by_label.setdefault(int(ids[0]), []).append(index)
    groups = sorted(by_label.values(), key=lambda items: items[0])
    return groups, rasterized


def oracle_for_groups(
    polygons: list[list[list[float]]],
    exclusions: list[list[list[float]]],
    groups: list[list[int]],
    rasterized: list[np.ndarray],
) -> dict:
    sys.path.insert(0, str(METHOD))
    from score import inside_polygon

    points = []
    for indices in groups:
        chosen = None
        for index in indices:
            pixels = rasterized[index]
            center = pixels.mean(axis=0)
            order = np.argsort(((pixels - center) ** 2).sum(axis=1))
            for position in order:
                row, col = pixels[position]
                x, y = (float(col) + 0.5) * CAM_DOWNSAMPLE, (float(row) + 0.5) * CAM_DOWNSAMPLE
                if inside_polygon(x, y, polygons[index]) and not any(
                    inside_polygon(x, y, other) for other in exclusions
                ):
                    chosen = {"x": x, "y": y, "confidence": 1.0}
                    break
            if chosen is not None:
                break
        if chosen is None:
            raise ValueError("No non-excluded interior oracle point for lesion group")
        points.append(chosen)
    return {"points": points}


def slide_info_and_overview(slide: Path, output: Path) -> tuple[int, int]:
    with tifffile.TiffFile(slide) as tiff:
        page = tiff.pages[0]
        width, height = page.imagewidth, page.imagelength
        level = tiff.pages[6]
        scale = 64
        wanted_width, wanted_height = math.ceil(width / scale), math.ceil(height / scale)
        if level.imagewidth < wanted_width or level.imagelength < wanted_height:
            raise ValueError("Pyramid does not contain the expected 64x level")
        data = level.asarray()[:wanted_height, :wanted_width, :3]
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(data).save(output, quality=88)
    return width, height


def camelyon(slide_name: str, variant: str) -> Path:
    task = copy_task("camelyon", "image-only", variant, skip_slide=True)
    slide = CAMELYON / f"{slide_name}.tif"
    shutil.copyfile(slide, task / "environment/data/slide.tif")
    width, height = slide_info_and_overview(slide, task / "environment/data/overview.jpg")
    xml_path = CAMELYON / f"{slide_name}.xml"
    tumor, exclusion = source_polygons(xml_path) if xml_path.exists() else ([], [])
    if slide_name.startswith("normal_") and tumor:
        raise ValueError("Selected negative slide has tumor annotations")
    groups, rasterized = lesion_groups(tumor, width, height)
    reference = {
        "kind": "camelyon_lesions",
        "slide": slide_name,
        "mpp": CAM_MPP,
        "grouping_um": CAM_CONNECT_UM,
        "tumor": tumor,
        "exclusion": exclusion,
        "lesion_groups": groups,
    }
    oracle = oracle_for_groups(tumor, exclusion, groups, rasterized)
    set_reference(task, reference, oracle)
    set_instruction(
        task,
        f"""
# Whole-slide metastasis localization

Search the lymph-node H&E slide at several scales. Return distinct points in
suspected metastatic tissue, or an empty list when none is supported. Every
point needs level-0 `x`, `y` and confidence from 0 to 1. Save
`/app/answer/points.json` as
`{{"points":[{{"x":123,"y":456,"confidence":0.8}}]}}`.

Inputs: `/app/data/slide.tif`, GT-free `/app/data/overview.jpg`. This slide is
{width} x {height} level-0 pixels. Native pixel spacing is approximately
{CAM_MPP} micrometers per pixel. Read crops with
`python /app/tools/read_slide.py X Y WIDTH HEIGHT /app/work/tile.png`.
The overview is the 64x pyramid level cropped to the native image extent.

The source XML is withheld. This study groups nearby XML Tumor polygons into
lesion units if they connect after a 50-micrometer grouping operation. A point
inside any non-excluded Tumor polygon hits its group. Extra, duplicate and
Exclusion-region points are reported per slide; confidence permits a later
free-response curve across cases. Do not infer lesion count from XML polygon
count. The selected release lists this slide among its fully annotated cases.
""",
    )
    return task


def hiesd_patch_centers(mask: np.ndarray, overview: np.ndarray) -> list[tuple[int, int, int]]:
    selected = []
    tissue = overview.mean(axis=2) < 235
    for code in range(1, 7):
        pure = binary_erosion(mask == code, structure=np.ones((5, 5), dtype=bool))
        candidates = np.column_stack(np.where(pure))
        if len(candidates) < 2:
            raise ValueError(f"Too few pure candidate centers for class {code}")
        # Require tissue in the GT-free 64x thumbnail. XML regions can cross blank
        # slide space, and a blank target would make a histotype label unfair.
        tissue_scores = np.array(
            [tissue[row - 2 : row + 3, col - 2 : col + 3].mean() for row, col in candidates]
        )
        eligible = np.flatnonzero(tissue_scores >= 0.8)
        if len(eligible) < 2:
            raise ValueError(f"Too few tissue-rich centers for class {code}")
        first = int(eligible[np.argmax(tissue_scores[eligible])])
        distances = ((candidates[eligible] - candidates[first]) ** 2).sum(axis=1)
        distances[eligible == first] = -1
        second = int(eligible[np.argmax(distances)])
        for index in (first, second):
            row, col = candidates[index]
            selected.append((code, int(row), int(col)))
    random.Random(20260923).shuffle(selected)
    return selected


def hiesd() -> Path:
    task = copy_task("hiesd", "image-only", "annotated-patches")
    source_mask = task / "tests/reference/mask.png"
    mask = np.asarray(Image.open(source_mask))
    overview = np.asarray(Image.open(task / "environment/data/overview.jpg").convert("RGB"))
    centers = hiesd_patch_centers(mask, overview)
    slide = task / "environment/data/slide.tif"
    read_spec = importlib.util.spec_from_file_location(
        "wsi_read_slide", ROOT / "groups/lesion-localization/methods/wsi-agent-v1/read_slide.py"
    )
    if read_spec is None or read_spec.loader is None:
        raise ValueError("Cannot load the retained WSI tile reader")
    module = importlib.util.module_from_spec(read_spec)
    read_spec.loader.exec_module(module)
    patches = task / "environment/data/patches"
    patches.mkdir()
    manifest = []
    labels = {}
    with tifffile.TiffFile(slide) as tiff:
        width, height = tiff.pages[0].imagewidth, tiff.pages[0].imagelength
    for number, (code, row, col) in enumerate(centers, start=1):
        patch_id = f"patch_{number:02d}"
        x, y = 64 * col + 32, 64 * row + 32
        target_x, target_y = x - 128, y - 128
        context_x = min(max(x - 512, 0), width - 1024)
        context_y = min(max(y - 512, 0), height - 1024)
        target = module.read_region(slide, target_x, target_y, 256, 256)
        context = module.read_region(slide, context_x, context_y, 1024, 1024)
        draw = ImageDraw.Draw(context)
        box = (
            target_x - context_x,
            target_y - context_y,
            target_x - context_x + 255,
            target_y - context_y + 255,
        )
        draw.rectangle(box, outline="black", width=5)
        draw.rectangle(box, outline="white", width=2)
        target.save(patches / f"{patch_id}.png")
        context.save(patches / f"{patch_id}-context.jpg", quality=88)
        manifest.append(
            {
                "id": patch_id,
                "target_level0_bbox": [target_x, target_y, 256, 256],
                "context_level0_bbox": [context_x, context_y, 1024, 1024],
            }
        )
        labels[patch_id] = code
    put_json(task / "environment/data/patches.json", {"patches": manifest})
    reference = {
        "kind": "hiesd_patches",
        "slide": "e4442edf-05b0-431b-bf61-ccf2d8cdebb6",
        "labels": labels,
        "selection": "two 256x256 center patches per XML class, each center with pure 5x5 coarse-grid support and at least 80 percent tissue in the GT-free thumbnail neighborhood",
        "coarse_centers_by_patch": {
            f"patch_{i:02d}": [row, col] for i, (_, row, col) in enumerate(centers, start=1)
        },
    }
    oracle = {"labels": [{"id": patch_id, "class": code} for patch_id, code in labels.items()]}
    (task / "solution/reference/map.png").unlink()
    source_mask.unlink()
    set_reference(task, reference, oracle, filename="labels.json")
    set_instruction(
        task,
        """
# Gastric tissue classification at annotated patches

Classify the central 256 x 256 level-0 square for every patch listed in
`/app/data/patches.json`. Each `/app/data/patches/patch_NN.png` is the target;
its `-context.jpg` shows a 1024 x 1024 surrounding crop with the target box
outlined in black and white. The full source slide and GT-free overview are
also available for broader context. The patch locations are fixed in advance;
the source XML and labels are withheld. Save `/app/answer/labels.json` as
`{"labels":[{"id":"patch_01","class":1}, ...]}` with one entry per patch.

Codes: 0 unknown/abstain; 1 chronic gastritis; 2 complete intestinal
metaplasia; 3 lymphoid follicle; 4 normal glands; 5 well differentiated
adenocarcinoma (tub1); 6 incomplete intestinal metaplasia. Judge the central
target, not every tissue type visible in its larger context. The annotations
are region-level and sparse; these selected patches test classification within
annotated domains, not whole-slide search, fine boundaries, invasion depth or
surgical margins.
""",
    )
    return task


def main() -> None:
    if DEST.exists():
        raise FileExistsError(f"Refusing to overwrite existing task destination: {DEST}")
    sources = source_check()
    tasks = {
        "hubmap": str(hubmap().relative_to(ROOT)),
        "tiger_image_only": str(tiger(False).relative_to(ROOT)),
        "tiger_tissue_supplied": str(tiger(True).relative_to(ROOT)),
        "camelyon_existing_positive": str(
            camelyon("tumor_091", "positive-existing").relative_to(ROOT)
        ),
        "camelyon_small_positive": str(camelyon("tumor_084", "small-positive").relative_to(ROOT)),
        "camelyon_negative": str(camelyon("normal_108", "negative").relative_to(ROOT)),
        "hiesd_patches": str(hiesd().relative_to(ROOT)),
    }
    put_json(
        DEST / "preparation.json",
        {
            "schema_version": 1,
            "method": "groups/lesion-localization/methods/wsi-agent-v2/prepare.py",
            "source_new_camelyon": sources,
            "tasks": tasks,
            "camelyon_grouping_um": CAM_CONNECT_UM,
            "camelyon_grouping_raster_downsample": CAM_DOWNSAMPLE,
            "hiesd_patch_selection_seed": 20260923,
        },
    )
    print(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
