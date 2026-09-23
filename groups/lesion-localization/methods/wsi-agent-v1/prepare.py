"""Prepare five diagnostic WSI conditions from the pinned local teaching selection."""

import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).resolve().parent
SOURCE = ROOT / ".local/wsi-ground-truth"
DEST = ROOT / ".local/wsi-agent-v1"
RECEIPT = ROOT / "datasets/receipts/wsi-teaching-samples.json"
COMPOSE = ROOT / ".local/longitudinal-ct-image-only-v1/task/environment/docker-compose.yaml"
MAPPINGS = {
    "hubmap": "wsi-hubmap-inventory-sol6-xhigh",
    "tiger": "wsi-tiger-context-sol6-xhigh",
    "camelyon": "wsi-camelyon-search-sol6-xhigh",
    "hiesd": "wsi-hiesd-map-sol6-xhigh",
}
HIESD_LABELS = {
    "_0": "chronic_gastritis",
    "_1": "complete_intestinal_metaplasia",
    "_2": "lymphoid_follicle",
    "_3": "normal_glands",
    "_4": "well_differentiated_adenocarcinoma_tub1",
    "_5": "incomplete_intestinal_metaplasia",
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_file(receipt: dict, kind: str, suffix: str) -> Path:
    selected = [f for f in receipt["samples"][kind]["files"] if f["local_path"].endswith(suffix)]
    if len(selected) != 1:
        raise ValueError(f"Ambiguous source {kind} {suffix}")
    item = selected[0]
    path = ROOT / item["local_path"]
    if path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
        raise ValueError(f"Source hash mismatch: {path}")
    return path


def polygons(path: Path) -> list[dict]:
    return [
        {
            "group": ann.get("PartOfGroup"),
            "points": [
                [float(coord.get("X")), float(coord.get("Y"))]
                for coord in ann.findall(".//Coordinate")
            ],
        }
        for ann in ET.parse(path).findall(".//Annotation")
    ]


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def json_write(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def setup(kind: str, variant: str, instruction: str, reference: dict, answer: dict | Path) -> Path:
    task = DEST / kind / variant / "task"
    if task.exists():
        raise FileExistsError(f"Refusing to overwrite {task}")
    for subdir in (
        "environment/data",
        "environment/tools",
        "tests/reference",
        "solution/reference",
    ):
        (task / subdir).mkdir(parents=True)
    write(task / "instruction.md", instruction)
    shutil.copyfile(METHOD / "score.py", task / "tests/score.py")
    write(task / "tests/test.sh", "#!/bin/sh\nset -eu\npython /tests/score.py\n")
    if isinstance(answer, Path):
        shutil.copyfile(answer, task / "solution/reference/map.png")
        solve = "#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/reference/map.png /app/answer/map.png\n"
    else:
        json_write(task / "solution/reference/points.json", answer)
        solve = "#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/reference/points.json /app/answer/points.json\n"
    write(task / "solution/solve.sh", solve)
    for executable in (task / "tests/test.sh", task / "solution/solve.sh"):
        executable.chmod(0o755)
    json_write(task / "tests/reference/reference.json", reference)
    shutil.copyfile(COMPOSE, task / "environment/docker-compose.yaml")
    write(
        task / "environment/Dockerfile",
        "FROM tb3-wsi-agent-runtime:v1\nWORKDIR /app\nCOPY data /app/data\nCOPY tools /app/tools\nRUN mkdir -p /app/answer /app/work && chmod -R a-w /app/data\n",
    )
    write(
        task / "tests/Dockerfile",
        "FROM tb3-wsi-agent-runtime:v1\nCOPY . /tests\nRUN mkdir -p /app/answer /logs/verifier\n",
    )
    write(
        task / "task.toml",
        f"""version = "1.0"
artifacts = ["/app/answer", "/app/work"]
[metadata]
category = "medical-imaging"
[agent]
timeout_sec = 3600.0
[verifier]
timeout_sec = 300.0
environment_mode = "separate"
[verifier.environment]
docker_image = "tb3-wsi-{kind}-{variant}-evaluator:v1"
network_mode = "no-network"
cpus = 2
memory_mb = 4096
[environment]
docker_image = "tb3-wsi-{kind}-{variant}-solver:v1"
build_timeout_sec = 900.0
cpus = 4
memory_mb = 12288
storage_mb = 16384
gpus = 0
network_mode = "public"
""",
    )
    return task


def add_slide(receipt: dict, kind: str, task: Path, suffix: str) -> None:
    shutil.copyfile(source_file(receipt, kind, suffix), task / "environment/data/slide.tif")
    shutil.copyfile(
        SOURCE / "explainer/assets" / f"{kind}-overview-input.jpg",
        task / "environment/data/overview.jpg",
    )
    shutil.copyfile(METHOD / "read_slide.py", task / "environment/tools/read_slide.py")


def hubmap(receipt: dict) -> Path:
    raw = json.loads(source_file(receipt, "hubmap", "aaa6a05cc.json").read_text())
    shapes = [feature["geometry"]["coordinates"][0] for feature in raw]
    reference = {"kind": "hubmap", "mpp": 0.65, "polygons": shapes}
    answer = {"points": [{"x": p[0][0], "y": p[0][1], "confidence": 1} for p in shapes]}
    instruction = """# Whole-slide glomerulus inventory

Inspect the complete PAS kidney slide. Locate each glomerulus and submit one
level-0 pixel point for each distinct object. Avoid duplicates. You may also
record confidence and a brief note for uncertain candidates. The output file is
`/app/answer/points.json`: `{"points":[{"x":123,"y":456,"confidence":0.8}]}`.

Inputs: `/app/data/slide.tif` and a ground-truth-free `/app/data/overview.jpg`.
The slide is 13013 x 18484 level-0 pixels at 0.65 micrometers per pixel.
Read crops with `python /app/tools/read_slide.py X Y WIDTH HEIGHT /app/work/tile.png`.
Keep coordinates in level-0 pixels. The source polygons are withheld. The slide
may contain structures that resemble glomeruli; report your uncertainty.
"""
    task = setup("hubmap", "image-only", instruction, reference, answer)
    add_slide(receipt, "hubmap", task, "aaa6a05cc.tiff")
    return task


def camelyon(receipt: dict) -> Path:
    items = polygons(source_file(receipt, "camelyon", "tumor_091.xml"))
    tumor = [p["points"] for p in items if p["group"] == "Tumor"]
    exclusion = [p["points"] for p in items if p["group"] == "Exclusion"]
    reference = {"kind": "camelyon", "tumor": tumor, "exclusion": exclusion}
    answer = {
        "points": [
            {
                "x": sum(point[0] for point in polygon) / len(polygon),
                "y": sum(point[1] for point in polygon) / len(polygon),
                "confidence": 1,
            }
            for polygon in tumor
        ]
    }
    instruction = """# Whole-slide metastatic-tissue search

Search the lymph-node H&E slide at several scales. Return point locations that
you judge to contain metastatic tissue, or an empty list if none is supported.
Use level-0 pixel coordinates. Submit `/app/answer/points.json` in this format:
`{"points":[{"x":123,"y":456,"confidence":0.8}]}`. Do not assume a number
of independent lesions from a count of annotation polygons.

Inputs: `/app/data/slide.tif`, GT-free `/app/data/overview.jpg`. The slide's
level-0 image is 61440 x 53760 pixels at 0.227273 micrometers per pixel.
Read crops with `python /app/tools/read_slide.py X Y WIDTH HEIGHT /app/work/tile.png`.
The reference XML is withheld. No GT-selected detail crop is supplied.
"""
    task = setup("camelyon", "image-only", instruction, reference, answer)
    add_slide(receipt, "camelyon", task, "tumor_091.tif")
    return task


def tiger(receipt: dict, supplied: bool) -> Path:
    coco = json.loads(source_file(receipt, "tiger", "tiger-coco.json").read_text())
    source_images = [i for i in coco["images"] if "114S_[" in i["file_name"]]
    source_images.sort(key=lambda i: i["file_name"])
    if len(source_images) != 3:
        raise ValueError("Expected exactly three paired TIGER ROIs")
    names = {i["id"]: f"roi{index}" for index, i in enumerate(source_images, 1)}
    rois = {}
    answer_points = []
    for item in source_images:
        roi = names[item["id"]]
        filename = Path(item["file_name"]).name
        cells = [
            {"x": ann["bbox"][0] + ann["bbox"][2] / 2, "y": ann["bbox"][1] + ann["bbox"][3] / 2}
            for ann in coco["annotations"]
            if ann["image_id"] == item["id"]
        ]
        mask_source = source_file(receipt, "tiger", f"masks/{filename}")
        mask = np.asarray(Image.open(mask_source))
        for cell in cells:
            x, y = round(cell["x"]), round(cell["y"])
            compartment = (
                int(mask[y, x]) if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] else 0
            )
            answer_points.append({"roi": roi, **cell, "compartment": compartment})
        rois[roi] = {"cells": cells, "mask": f"{roi}-mask.png"}
    reference = {"kind": "tiger", "rois": rois}
    condition = "tissue-supplied" if supplied else "image-only"
    instruction = """# Tissue-conditioned immune-cell inventory

Three fixed H&E regions are provided as `/app/data/roi1.png` through `roi3.png`.
Mark centers of lymphocytes and plasma cells as one merged cell class. For each
center assign a tissue compartment code: 1 invasive tumor, 2 tumor-associated
stroma, 4 healthy glands, 6 inflammatory stroma, 7 other, or 0 unknown/ignore.
Output `/app/answer/points.json` as
`{"points":[{"roi":"roi1","x":123,"y":456,"compartment":2}]}`.
Coordinates are local to each ROI. Some tissue is unlabeled; keep uncertainty.
These fixed ROIs test local cell and context reasoning, not full-slide search.
"""
    if supplied:
        instruction += "\nOfficial tissue class masks are supplied as `/app/data/roi1-tissue.png` through `roi3-tissue.png`.\n"
    else:
        instruction += "\nNo tissue mask is supplied; infer compartment from the image.\n"
    task = setup("tiger", condition, instruction, reference, {"points": answer_points})
    for item in source_images:
        roi = names[item["id"]]
        filename = Path(item["file_name"]).name
        shutil.copyfile(
            source_file(receipt, "tiger", f"rois/{filename}"), task / f"environment/data/{roi}.png"
        )
        mask = source_file(receipt, "tiger", f"masks/{filename}")
        shutil.copyfile(mask, task / f"tests/reference/{roi}-mask.png")
        if supplied:
            shutil.copyfile(mask, task / f"environment/data/{roi}-tissue.png")
    return task


def hiesd(receipt: dict) -> Path:
    original = source_file(
        receipt,
        "hiesd",
        "ESD_40X_annotation_downsample64_xml/e4442edf-05b0-431b-bf61-ccf2d8cdebb6.xml",
    )
    thumbnail = source_file(
        receipt,
        "hiesd",
        "ESD_40X_Thumbnail_downsample64/e4442edf-05b0-431b-bf61-ccf2d8cdebb6_thumbnail.png",
    )
    canvas = Image.new("L", Image.open(thumbnail).size, 0)
    draw = ImageDraw.Draw(canvas)
    for item in polygons(original):
        if len(item["points"]) >= 3:
            draw.polygon(
                [tuple(point) for point in item["points"]], fill=int(item["group"][1:]) + 1
            )
    mask = DEST / "hiesd/reference-mask.png"
    mask.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(mask)
    reference = {"kind": "hiesd", "mask": "mask.png", "n_classes": 6}
    labels = "\n".join(f"- {int(code[1:]) + 1}: {label}" for code, label in HIESD_LABELS.items())
    instruction = f"""# Coarse gastric tissue map

Map the supplied gastric ESD slide onto the 64x grid of the GT-free thumbnail.
Submit `/app/answer/map.png` as a single-channel 8-bit PNG with exactly
623 x 448 pixels. Use 0 for unknown or unsupported tissue. Codes are:\n{labels}

Inputs: `/app/data/slide.tif`, `/app/data/overview.jpg`. The level-0 slide is
39887 x 28702 pixels at 0.2458 micrometers per pixel. Map grid pixel (u,v)
near level-0 (64u,64v). Read high-resolution crops with
`python /app/tools/read_slide.py X Y WIDTH HEIGHT /app/work/tile.png`.
Keep coarse class boundaries; the source XML is withheld and unannotated
tissue is not known-normal ground truth. Do not infer invasion depth or margin.
"""
    task = setup("hiesd", "image-only", instruction, reference, mask)
    add_slide(receipt, "hiesd", task, "e4442edf-05b0-431b-bf61-ccf2d8cdebb6.svs")
    shutil.copyfile(mask, task / "tests/reference/mask.png")
    return task


def main() -> None:
    if DEST.exists():
        raise FileExistsError(f"Refusing to overwrite {DEST}")
    receipt = json.loads(RECEIPT.read_text())
    tasks = {
        "hubmap": hubmap(receipt),
        "tiger_image_only": tiger(receipt, False),
        "tiger_tissue_supplied": tiger(receipt, True),
        "camelyon": camelyon(receipt),
        "hiesd": hiesd(receipt),
    }
    config_paths = {
        "hubmap": ("hubmap", "image-only"),
        "camelyon": ("camelyon", "image-only"),
        "hiesd": ("hiesd", "image-only"),
    }
    for key, (kind, _variant) in config_paths.items():
        experiment = ROOT / "groups/lesion-localization/experiments" / MAPPINGS[kind]
        scaffold = experiment / "task"
        shutil.move(str(scaffold), str(DEST / f"unused-scaffold-{kind}"))
        config = experiment / "experiment.toml"
        config.write_text(
            config.read_text().replace(
                f"groups/lesion-localization/experiments/{MAPPINGS[kind]}/task",
                str(tasks[key].relative_to(ROOT)),
            )
        )
    tiger_exp = ROOT / "groups/lesion-localization/experiments" / MAPPINGS["tiger"]
    shutil.move(str(tiger_exp / "task"), str(DEST / "unused-scaffold-tiger"))
    config = tiger_exp / "experiment.toml"
    config.write_text(
        config.read_text().replace(
            'task_path = "groups/lesion-localization/experiments/wsi-tiger-context-sol6-xhigh/task"',
            "tasks = [\n"
            '    { id = "image-only", task_path = ".local/wsi-agent-v1/tiger/image-only/task" },\n'
            '    { id = "tissue-supplied", task_path = ".local/wsi-agent-v1/tiger/tissue-supplied/task" },\n'
            "]",
        )
    )
    json_write(
        DEST / "preparation.json",
        {
            "source_receipt": str(RECEIPT.relative_to(ROOT)),
            "source_receipt_sha256": sha(RECEIPT),
            "model": "openai/gpt-6-sol",
            "effort": "xhigh",
            "tasks": {key: str(path.relative_to(ROOT)) for key, path in tasks.items()},
            "scope": "five diagnostic conditions on four selected public cases; no model runs at preparation",
        },
    )
    print(json.dumps({key: str(path.relative_to(ROOT)) for key, path in tasks.items()}, indent=2))


if __name__ == "__main__":
    main()
