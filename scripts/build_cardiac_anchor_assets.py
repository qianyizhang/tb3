"""Build a local, source-pinned BR-027 teaching pack from retained arrays.

This reads saved packages and predictions only. It does not track, fit or score.
"""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path("groups/cardiac-motion/presentation/sources/cardiac-anchor-audit.json")
RUN = Path("runs/br027-cardiac")
NATIVE = Path("runs/br025-cardiac/source/native/Patient001")
VIEWS = [0, 9, 18, 27]
DISPLAY = (243, 232)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n")


def png_data(image):
    memory = io.BytesIO()
    image.save(memory, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(memory.getvalue()).decode()


def boundary(mask, color):
    edge = mask & ~binary_erosion(mask)
    # Make a two-native-pixel line before shrinking the fixed display by half.
    edge |= np.roll(edge, 1, axis=0) | np.roll(edge, 1, axis=1)
    rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
    rgba[edge] = (*color, 255)
    return png_data(Image.fromarray(rgba).resize(DISPLAY, Image.Resampling.NEAREST))


def section(profile, view, geo):
    yy, xx = np.indices(geo["shape_hw"])
    dx, dy = xx - geo["rotation_axis_x_px"], yy - geo["origin_y_px"]
    angle = np.arctan2(np.abs(dx), dy)
    polar = np.linspace(0, np.pi, 65)
    positive = np.interp(angle, polar, profile[view % 72])
    negative = np.interp(angle, polar, profile[(view + 36) % 72])
    return np.hypot(dx, dy) <= np.where(dx >= 0, positive, negative)


def build(out):
    assert not out.exists(), "Use a fresh destination"
    audit = json.loads((ROOT / AUDIT).read_text())
    pins = {str(AUDIT): sha(ROOT / AUDIT)}
    audit_pins = audit["source_pins"]

    def retained(relative):
        path = ROOT / relative
        digest = sha(path)
        expected = audit_pins.get(str(relative))
        if expected is None or digest != expected:
            raise ValueError(f"Unpinned or changed retained source: {relative}")
        pins[str(relative)] = digest
        return path

    source = {
        "frame_count": 30,
        "views": [],
        "anchors": {"one": {}, "two": {}},
        "shape_hw": [464, 485],
        "display_wh": list(DISPLAY),
        "spacing_mm_per_native_pixel": 0.08995,
    }
    for condition, frames in [("one", [2]), ("two", [2, 17])]:
        name = "one_anchor" if condition == "one" else "two_anchors"
        manifest_path = retained(RUN / "public" / name / "manifest.json")
        manifest = json.loads(manifest_path.read_text())
        package = ROOT / RUN / "public" / name
        for v in range(4):
            for frame in frames:
                relative = f"anchors/view_{v:02d}/frame_{frame:03d}.png"
                path = package / relative
                if sha(path) != manifest[relative]:
                    raise ValueError(f"Changed anchor {path}")
                pins[str(path.relative_to(ROOT))] = manifest[relative]
                mask = np.asarray(Image.open(path).convert("L")) > 0
                source["anchors"][condition][f"{v}-{frame}"] = boundary(mask, (137, 166, 230))
        if condition == "one":
            for v, native in enumerate(VIEWS):
                frames_data = []
                for frame in range(1, 31):
                    relative = f"video/view_{v:02d}/frame_{frame:03d}.png"
                    path = package / relative
                    if sha(path) != manifest[relative]:
                        raise ValueError(f"Changed video frame {path}")
                    pins[str(path.relative_to(ROOT))] = manifest[relative]
                    pixels = Image.open(path).convert("L")
                    if pixels.size != (485, 464):
                        raise ValueError(f"Unexpected source dimensions {path}")
                    frames_data.append(png_data(pixels.resize(DISPLAY, Image.Resampling.BOX)))
                source["views"].append(
                    {
                        "source_plane_1based": native + 1,
                        "assumed_degrees": v * 45,
                        "frames": frames_data,
                    }
                )

    paths = {"one": RUN / "one-anchor-v1/dis-mesh.npz", "two": RUN / "two-anchors-v1/dis-mesh.npz"}
    output = {"conditions": {}}
    for condition, relative in paths.items():
        data = np.load(retained(relative), allow_pickle=False)
        masks = data["input_view_masks"]
        if masks.shape != (4, 30, 464, 485):
            raise ValueError("Unexpected saved-mask shape")
        image_overlays = [
            [boundary(masks[v, t] > 0, (34, 215, 224)) for t in range(30)] for v in range(4)
        ]
        # View 8 is withheld; these are saved mesh cross-sections, not input masks.
        withheld = [
            boundary(section(data["radius_px"][t], 7, audit["geometry"]), (34, 215, 224))
            for t in range(30)
        ]
        output["conditions"][condition] = {
            "input_mask_boundaries": image_overlays,
            "withheld_plane8_mesh_sections": withheld,
            "volume_ml": data["volume_ml"].tolist(),
            # Eleven fixed polar rings, 24 azimuth samples each.
            # Every coordinate is sampled from the retained saved
            # mesh in its native millimetre frame; no fitting occurs.
            "mesh_rings_mm": [
                [
                    np.round(
                        data["vertices"][t, 1 + ring * 72 : 1 + (ring + 1) * 72 : 3], 3
                    ).tolist()
                    for ring in range(0, 63, 6)
                ]
                for t in range(30)
            ],
        }
    dense = np.load(retained(RUN / "evaluation-v2/dense-mesh.npz"), allow_pickle=False)
    reference = {
        "selected": {},
        "dense_volume_ml": dense["volume_ml"].tolist(),
        "dense_ef_percent": audit["recomputed_stats"]["dense"]["ef_percent"],
    }
    for key, native, frame in [
        ("input-28-17", 27, 17),
        ("input-28-25", 27, 25),
        ("withheld-8-17", 7, 17),
    ]:
        image_path = NATIVE / "image" / f"Patient001_slice{native + 1:03d}time{frame:03d}.png"
        mask_path = NATIVE / "mask" / f"Patient001_slice{native + 1:03d}time{frame:03d}.png"
        # The signed 2251-member receipt, already verified by the retained audit, pins source files.
        for path in [image_path, mask_path]:
            pins[str(path)] = sha(ROOT / path)
        pixels = Image.open(ROOT / image_path).convert("L")
        mask = np.asarray(Image.open(ROOT / mask_path)) == 127
        reference["selected"][key] = {
            "image": png_data(pixels.resize(DISPLAY, Image.Resampling.BOX)),
            "boundary": boundary(mask, (255, 190, 75)),
            "source_plane_1based": native + 1,
            "frame_1based": frame,
        }
    out.mkdir(parents=True)
    dump(out / "source.json", source)
    dump(out / "output.json", output)
    dump(out / "reference.json", reference)
    (out / "NOTICE.md").write_text("""# FeEcho4D BR-027 local teaching assets

Actual FeEcho4D Patient001 source images, supplied anchors and saved author outputs.
Source: https://feecho4d.github.io/Website/ . Research-use terms apply; this pack
is for the user's local noncommercial interpretation. No public redistribution
right is asserted. Keep source-derived images and geometry local.

Source images are downsampled from 485 x 464 to 243 x 232 for display. Boundary
overlays are native binary contours widened to two native pixels then scaled by
nearest neighbor. The one/two-anchor output masks are retained saved predictions;
withheld plane-8 cyan sections are projected from retained saved radius profiles.
Gold source boundaries are reader-only evaluator material, never solver input.
The dense volume comparator uses all 36 source directions, including evaluation
views; it is annotation fit rather than independent three-dimensional truth.

The 0/45/90/135-degree pose model is assumed. This viewer replays arrays and
does not run tracking, interpolation, fitting, scoring or a model attempt.
The mesh wire view samples eleven polar rings and twenty-four azimuth points
per ring directly from each retained saved mesh, rounds them to 0.001 mm for
display, and uses one fixed oblique projection and scale over all frames.
Rebuild only to a fresh local directory with scripts/build_cardiac_anchor_assets.py.
""")
    assets = []
    for name in ["source.json", "output.json", "reference.json", "NOTICE.md"]:
        path = out / name
        assets.append(
            {
                "file": name,
                "sha256": sha(path),
                "bytes": path.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
            }
        )
    dump(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-cardiac-anchor-v1",
            "frame": "FeEcho4D-native",
            "units": "mm",
            "license": "LicenseRef-FeEcho4D-noncommercial-research",
            "label_license": "LicenseRef-FeEcho4D-noncommercial-research",
            "reference_policy": "reader-reference-reveal",
            "sources": pins,
            "checks": {
                "native_input_frames": 120,
                "anchor_masks": {"one": 4, "two": 8},
                "display_downsample": list(DISPLAY),
                "model_execution": False,
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.out)
