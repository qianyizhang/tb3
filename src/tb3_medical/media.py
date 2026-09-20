"""Retained tour inputs, local display checks and lossless player assets."""

import gzip
import json
import math
from pathlib import Path
import re
import shutil
from . import core


def read(path):
    return core.read(path)


def finite(values):
    if isinstance(values, list):
        return all(finite(v) for v in values)
    return isinstance(values, (int, float)) and math.isfinite(values)


def prepare(root):
    tours = Path(root) / "presentation/tours"
    entries = read(tours / "inputs.json")["files"]
    core.verify_inputs(root, entries)
    target = tours / "data"
    target.mkdir(exist_ok=True)
    for entry in entries:
        path = core.inside(target, entry["destination"])
        if path.exists() and core.sha(path) != entry["sha256"]:
            raise core.MedicalError("Tour output differs: " + str(path))
        shutil.copy2(core.inside(root, entry["path"]), path)
    return {
        "prepared_files": len(entries),
        "scope": "Restored retained derived data; original raw derivation remains historical.",
    }


def check(root):
    ROOT = Path(root)
    TOURS = ROOT / "presentation/tours"
    entries = read(TOURS / "inputs.json")["files"]
    core.verify_inputs(
        TOURS / "data", [{"path": e["destination"], "sha256": e["sha256"]} for e in entries]
    )
    stories = read(TOURS / "storyboards.json")
    for name, s in stories.items():
        assert s["steps"][0]["at"] == 0
        assert all(a["at"] < b["at"] for a, b in zip(s["steps"], s["steps"][1:]))
        assert s["steps"][-1]["at"] < s["duration"]
    seg = read(TOURS / "data/segmentation.json")
    assert seg["transferred_ml"] == 21.04 and len(seg["frames"]) == 24
    assert abs(seg["frames"][seg["pointFrame"]]["z_mm"] - seg["point_lps_mm"][2]) < 1e-5
    assert all(0 <= v <= 1 for v in seg["pointUV"])
    for f in seg["frames"]:
        assert set(f["images"]) == {"before", "after", "region"}
        for filename in f["images"].values():
            assert (TOURS / "data" / filename).is_file()
    v = read(TOURS / "data/vessels.json")
    assert len(v["added"]) == 103
    assert v["cut_indices"] == list(range(len(v["path"])))
    assert len(v["cuts"]) == len(v["path"]) == len(v["arc"]) == 371
    assert len(v["cpr"]) == 8
    cumulative = 0
    for i in range(1, len(v["path"])):
        cumulative += math.dist(v["path"][i - 1], v["path"][i])
        assert abs(cumulative - v["arc"][i]) < 0.005
    assert abs(v["original_axis_length_mm"] - v["saved_line_length_mm"] - 8.890774) < 0.001
    for m in [v["before"], v["after"]]:
        assert finite(m["points"])
        assert all(len(f) == 3 and min(f) >= 0 and max(f) < len(m["points"]) for f in m["faces"])
    c = read(TOURS / "data/cardiac.json")
    assert c["frames"] == len(c["masks"]) == 30
    for m in c["models"]:
        assert finite(m["points"])
    tracks = c["material_tracks"]
    assert len(set(tracks["source_cells"])) == 24
    for a, b in zip(tracks["reference"][0], tracks["prediction"][0]):
        assert math.dist(a, b) < 0.0002
    assert all(
        len(frame) == 24 and finite(frame)
        for key in ["reference", "prediction"]
        for frame in tracks[key]
    )
    assert 7.37 < c["metrics"]["strain_mae_pp"][2] < 7.38
    r = read(TOURS / "data/registration.json")
    assert len(r["ids"]) == 8
    assert abs(r["methods"]["Sol / full 3D source"]["grade"]["max_mm"] - 6.411513) < 1e-5
    landmarks = read(TOURS / "data/landmarks.json")
    full = landmarks["cases"]["ct-full"]
    crop = landmarks["cases"]["ct-partial"]
    assert full["plane_index"] == crop["plane_index"] == 263
    assert crop["shape"][2] == 920 and full["shape"][2] == 1214
    assert crop["targets"]["T4"]["reference"]["status"] == "out_of_fov"
    assert crop["targets"]["T5"]["reference"]["status"] == "observed"
    assert all(
        crop["targets"][k]["predictions"]["sol-xhigh"]["status"] == "out_of_fov"
        for k in ["T4", "T5"]
    )
    a = read(TOURS / "data/aneurysm.json")
    cases = a["cases"]
    assert set(cases) == {"N01", "N02", "N03"}
    assert cases["N02"]["answer"] == [[312, 213, 94]] and cases["N02"]["accepted_prediction"]
    assert not cases["N01"]["grade"]["passed"] and cases["N01"]["answer"] == []
    assert cases["N03"]["source_assisted"] and cases["N03"]["answer"] == []
    for name in ["N01", "N02"]:
        c = cases[name]
        lo, hi = c["crop_bounds"]
        for p in c["planes"]:
            axis = p["axis"]
            axes = p["axes"]
            frames = p["frames"]
            assert [f["index"] for f in frames] == list(
                range(c["reference_center"][axis] - 12, c["reference_center"][axis] + 13)
            )
            assert (
                abs(
                    p["aspect"]
                    - (hi[axes[0]] - lo[axes[0]])
                    * c["spacing"][axes[0]]
                    / ((hi[axes[1]] - lo[axes[1]]) * c["spacing"][axes[1]])
                )
                < 1e-9
            )
            assert sum(f["mask_voxels"] for f in frames) == c["reference_voxels"]
            if c["answer"]:
                point = c["answer"][0]
                assert p["point_uv"] == [
                    (point[axes[0]] - lo[axes[0]] + 0.5) / (hi[axes[0]] - lo[axes[0]]),
                    1 - (point[axes[1]] - lo[axes[1]] + 0.5) / (hi[axes[1]] - lo[axes[1]]),
                ]
    for filename in a["image_files"]:
        assert (TOURS / "data" / filename).is_file()
    for path in TOURS.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if not target.startswith(("http:", "https:", "#", "exports/", "web/")):
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
    return {"verified_files": len(entries), "display_invariants": "passed"}


def optimize(root):
    from PIL import Image

    ROOT = Path(root) / "presentation/tours"
    OUT = ROOT / "web"
    OUT.mkdir(exist_ok=True)
    manifest = {
        "json": {},
        "images": {},
        "files": {},
        "source_bytes": 0,
        "served_bytes": 0,
        "method": "Lossless WebP pixels; gzip level 9 exact JSON bytes; original authoring data retained.",
    }
    for p in sorted((ROOT / "data").iterdir()):
        if p.suffix == ".json" and p.name != "provenance.json":
            q = OUT / (p.name + ".gz")
            q.write_bytes(gzip.compress(p.read_bytes(), compresslevel=9, mtime=0))
            assert gzip.decompress(q.read_bytes()) == p.read_bytes()
            manifest["json"][p.stem] = q.name
        elif p.suffix == ".png":
            q = OUT / (p.stem + ".webp")
            im = Image.open(p)
            im.save(q, format="WEBP", lossless=True, method=6, exact=True)
            assert im.convert("RGBA").tobytes() == Image.open(q).convert("RGBA").tobytes()
            manifest["images"][p.name] = q.name
        else:
            continue
        manifest["source_bytes"] += p.stat().st_size
        manifest["served_bytes"] += q.stat().st_size
        manifest["files"][q.name] = {
            "source": p.name,
            "source_sha256": core.sha(p),
            "sha256": core.sha(q),
            "bytes": q.stat().st_size,
        }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Lossless player data: {manifest['source_bytes'] / 1e6:.2f} -> {manifest['served_bytes'] / 1e6:.2f} MB ({1 - manifest['served_bytes'] / manifest['source_bytes']:.1%} reduction)"
    )
    return {"output": str(OUT), "files": len(manifest["files"])}
