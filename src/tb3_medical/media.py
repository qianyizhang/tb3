"""Retained tour inputs, local display checks and lossless player assets."""

import gzip
import json
import math
import re
import shutil
from pathlib import Path

from . import core, storage
from .errors import MedicalError
from .storage import read
from .types import Document, Pathish


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MedicalError("Tour validation failed: " + message)


def finite(values: object) -> bool:
    if isinstance(values, list):
        return all(finite(v) for v in values)
    return isinstance(values, (int, float)) and math.isfinite(values)


def prepare(root: Pathish) -> Document:
    tours = Path(root) / "presentation/tours"
    entries = read(tours / "inputs.json")["files"]
    core.verify_inputs(root, entries)
    target = tours / "data"
    target.mkdir(exist_ok=True)
    for entry in entries:
        path = storage.inside(target, entry["destination"])
        if path.exists() and storage.sha(path) != entry["sha256"]:
            raise MedicalError("Tour output differs: " + str(path))
        shutil.copy2(storage.inside(root, entry["path"]), path)
    return {
        "prepared_files": len(entries),
        "scope": "Restored retained derived data; original raw derivation remains historical.",
    }


def check(root: Pathish) -> Document:
    root_path = Path(root)
    tours = root_path / "presentation/tours"
    entries = read(tours / "inputs.json")["files"]
    core.verify_inputs(
        tours / "data", [{"path": e["destination"], "sha256": e["sha256"]} for e in entries]
    )
    stories = read(tours / "storyboards.json")
    for story_name, story in stories.items():
        _require(story["steps"][0]["at"] == 0, f"story {story_name} must start at zero")
        _require(
            all(
                first["at"] < second["at"]
                for first, second in zip(story["steps"], story["steps"][1:], strict=False)
            ),
            f"story {story_name} steps must be ordered",
        )
        _require(
            story["steps"][-1]["at"] < story["duration"],
            f"story {story_name} exceeds its duration",
        )
    segmentation = read(tours / "data/segmentation.json")
    _require(
        segmentation["transferred_ml"] == 21.04 and len(segmentation["frames"]) == 24,
        "segmentation summary differs",
    )
    _require(
        abs(
            segmentation["frames"][segmentation["pointFrame"]]["z_mm"]
            - segmentation["point_lps_mm"][2]
        )
        < 1e-5,
        "segmentation point frame differs",
    )
    _require(
        all(0 <= value <= 1 for value in segmentation["pointUV"]),
        "segmentation point must use normalized coordinates",
    )
    for frame in segmentation["frames"]:
        _require(
            set(frame["images"]) == {"before", "after", "region"},
            "segmentation frame image set differs",
        )
        for filename in frame["images"].values():
            _require((tours / "data" / filename).is_file(), f"missing tour image {filename}")
    vessels = read(tours / "data/vessels.json")
    _require(len(vessels["added"]) == 103, "vessel added-point count differs")
    _require(
        vessels["cut_indices"] == list(range(len(vessels["path"]))),
        "vessel cut indices differ",
    )
    _require(
        len(vessels["cuts"]) == len(vessels["path"]) == len(vessels["arc"]) == 371,
        "vessel path lengths differ",
    )
    _require(len(vessels["cpr"]) == 8, "vessel CPR panel count differs")
    cumulative = 0.0
    for index in range(1, len(vessels["path"])):
        cumulative += math.dist(vessels["path"][index - 1], vessels["path"][index])
        _require(
            abs(cumulative - vessels["arc"][index]) < 0.005,
            f"vessel arc length differs at index {index}",
        )
    _require(
        abs(vessels["original_axis_length_mm"] - vessels["saved_line_length_mm"] - 8.890774)
        < 0.001,
        "vessel saved-line length differs",
    )
    for model_name in ["before", "after"]:
        model = vessels[model_name]
        _require(finite(model["points"]), f"vessel {model_name} points must be finite")
        _require(
            all(
                len(face) == 3 and min(face) >= 0 and max(face) < len(model["points"])
                for face in model["faces"]
            ),
            f"vessel {model_name} faces differ",
        )
    cardiac = read(tours / "data/cardiac.json")
    _require(cardiac["frames"] == len(cardiac["masks"]) == 30, "cardiac frame count differs")
    for model in cardiac["models"]:
        _require(finite(model["points"]), "cardiac model points must be finite")
    tracks = cardiac["material_tracks"]
    _require(len(set(tracks["source_cells"])) == 24, "cardiac source-cell count differs")
    for reference, prediction in zip(tracks["reference"][0], tracks["prediction"][0], strict=False):
        _require(math.dist(reference, prediction) < 0.0002, "cardiac first-frame tracks differ")
    _require(
        all(
            len(frame) == 24 and finite(frame)
            for key in ["reference", "prediction"]
            for frame in tracks[key]
        ),
        "cardiac material tracks differ",
    )
    _require(
        7.37 < cardiac["metrics"]["strain_mae_pp"][2] < 7.38,
        "cardiac strain metric differs",
    )
    registration = read(tours / "data/registration.json")
    _require(len(registration["ids"]) == 8, "registration case count differs")
    _require(
        abs(registration["methods"]["Sol / full 3D source"]["grade"]["max_mm"] - 6.411513) < 1e-5,
        "registration maximum error differs",
    )
    landmarks = read(tours / "data/landmarks.json")
    full = landmarks["cases"]["ct-full"]
    crop = landmarks["cases"]["ct-partial"]
    _require(full["plane_index"] == crop["plane_index"] == 263, "landmark plane differs")
    _require(
        crop["shape"][2] == 920 and full["shape"][2] == 1214,
        "landmark volume shapes differ",
    )
    _require(
        crop["targets"]["T4"]["reference"]["status"] == "out_of_fov",
        "landmark T4 reference status differs",
    )
    _require(
        crop["targets"]["T5"]["reference"]["status"] == "observed",
        "landmark T5 reference status differs",
    )
    _require(
        all(
            crop["targets"][key]["predictions"]["sol-xhigh"]["status"] == "out_of_fov"
            for key in ["T4", "T5"]
        ),
        "landmark cropped predictions differ",
    )
    aneurysm = read(tours / "data/aneurysm.json")
    cases = aneurysm["cases"]
    _require(set(cases) == {"N01", "N02", "N03"}, "aneurysm case set differs")
    _require(
        cases["N02"]["answer"] == [[312, 213, 94]] and cases["N02"]["accepted_prediction"],
        "aneurysm N02 result differs",
    )
    _require(
        not cases["N01"]["grade"]["passed"] and cases["N01"]["answer"] == [],
        "aneurysm N01 result differs",
    )
    _require(
        cases["N03"]["source_assisted"] and cases["N03"]["answer"] == [],
        "aneurysm N03 result differs",
    )
    for name in ["N01", "N02"]:
        case = cases[name]
        lo, hi = case["crop_bounds"]
        for plane in case["planes"]:
            axis = plane["axis"]
            axes = plane["axes"]
            frames = plane["frames"]
            _require(
                [frame["index"] for frame in frames]
                == list(
                    range(
                        case["reference_center"][axis] - 12,
                        case["reference_center"][axis] + 13,
                    )
                ),
                f"aneurysm {name} plane frames differ",
            )
            _require(
                abs(
                    plane["aspect"]
                    - (hi[axes[0]] - lo[axes[0]])
                    * case["spacing"][axes[0]]
                    / ((hi[axes[1]] - lo[axes[1]]) * case["spacing"][axes[1]])
                )
                < 1e-9,
                f"aneurysm {name} plane aspect differs",
            )
            _require(
                sum(frame["mask_voxels"] for frame in frames) == case["reference_voxels"],
                f"aneurysm {name} reference voxel count differs",
            )
            if case["answer"]:
                point = case["answer"][0]
                _require(
                    plane["point_uv"]
                    == [
                        (point[axes[0]] - lo[axes[0]] + 0.5) / (hi[axes[0]] - lo[axes[0]]),
                        1 - (point[axes[1]] - lo[axes[1]] + 0.5) / (hi[axes[1]] - lo[axes[1]]),
                    ],
                    f"aneurysm {name} point projection differs",
                )
    for filename in aneurysm["image_files"]:
        _require((tours / "data" / filename).is_file(), f"missing tour image {filename}")
    for path in tours.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if not target.startswith(("http:", "https:", "#", "exports/", "web/")):
                _require(
                    (path.parent / target.split("#")[0]).exists(),
                    f"broken link in {path.name}: {target}",
                )
    return {"verified_files": len(entries), "display_invariants": "passed"}


def optimize(root: Pathish) -> Document:
    from PIL import Image

    tours = Path(root) / "presentation/tours"
    output = tours / "web"
    output.mkdir(exist_ok=True)
    manifest: Document = {
        "json": {},
        "images": {},
        "files": {},
        "source_bytes": 0,
        "served_bytes": 0,
        "method": "Lossless WebP pixels; gzip level 9 exact JSON bytes; original authoring data retained.",
    }
    for source in sorted((tours / "data").iterdir()):
        if source.suffix == ".json" and source.name != "provenance.json":
            served = output / (source.name + ".gz")
            served.write_bytes(gzip.compress(source.read_bytes(), compresslevel=9, mtime=0))
            _require(
                gzip.decompress(served.read_bytes()) == source.read_bytes(),
                f"gzip round trip changed {source.name}",
            )
            manifest["json"][source.stem] = served.name
        elif source.suffix == ".png":
            served = output / (source.stem + ".webp")
            with Image.open(source) as source_image:
                source_pixels = source_image.convert("RGBA").tobytes()
                source_image.save(served, format="WEBP", lossless=True, method=6, exact=True)
            with Image.open(served) as served_image:
                served_pixels = served_image.convert("RGBA").tobytes()
            _require(
                source_pixels == served_pixels,
                f"lossless WebP conversion changed {source.name}",
            )
            manifest["images"][source.name] = served.name
        else:
            continue
        manifest["source_bytes"] += source.stat().st_size
        manifest["served_bytes"] += served.stat().st_size
        manifest["files"][served.name] = {
            "source": source.name,
            "source_sha256": storage.sha(source),
            "sha256": storage.sha(served),
            "bytes": served.stat().st_size,
        }
    _require(manifest["source_bytes"] > 0, "no player data was optimized")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Lossless player data: {manifest['source_bytes'] / 1e6:.2f} -> {manifest['served_bytes'] / 1e6:.2f} MB ({1 - manifest['served_bytes'] / manifest['source_bytes']:.1%} reduction)"
    )
    return {"output": str(output), "files": len(manifest["files"])}
