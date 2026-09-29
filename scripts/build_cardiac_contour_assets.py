"""Pack pinned BR-025 source views and saved projections for local teaching.

This reads retained outputs only. It never executes the historical authoring module.
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
AUDIT = Path("groups/cardiac-motion/presentation/sources/cardiac-contour-audit.json")
MEMBERS = Path("datasets/receipts/feecho4d-members.json")
NATIVE = Path("runs/br025-cardiac/source/native/Patient001")
PILOT = Path("runs/br025-cardiac/pilot-v1")
SPACING_MM = 0.08995


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def png_data(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")


def outline(mask, rgb):
    boundary = mask & ~binary_erosion(mask)
    rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
    rgba[boundary, :3] = rgb
    rgba[boundary, 3] = 255
    return png_data(Image.fromarray(rgba))


def projected_mask(profile, plane):
    """Same original-plane projection used by the retained saved-output audit."""
    y, x = np.indices((464, 485))
    dx, dy = x - 242, y - 172
    angle = np.arctan2(np.abs(dx), dy)
    polar = np.linspace(0, np.pi, 65)
    positive = np.interp(angle, polar, profile[plane % 72])
    negative = np.interp(angle, polar, profile[(plane + 36) % 72])
    return np.hypot(dx, dy) <= np.where(dx >= 0, positive, negative)


def build(out):
    assert not out.exists(), "Use a fresh output directory"
    audit = json.loads((ROOT / AUDIT).read_text())
    member_receipt = json.loads((ROOT / MEMBERS).read_text())
    assert sha(ROOT / MEMBERS) == audit["source_pins"][str(MEMBERS)]
    by_local = {m["local_path"]: m for m in member_receipt["members"]}
    source_files = {str(AUDIT): sha(ROOT / AUDIT), str(MEMBERS): sha(ROOT / MEMBERS)}

    def source_image(kind, plane, frame):
        relative = f"Patient001/{kind}/Patient001_slice{plane:03d}time{frame:03d}.png"
        path = ROOT / NATIVE / relative.removeprefix("Patient001/")
        assert sha(path) == by_local[relative]["sha256"], relative
        source_files[str(NATIVE / relative.removeprefix("Patient001/"))] = sha(path)
        return Image.open(path).convert("L")

    saved = {}
    mesh_samples = {}
    ring_indices = [*range(0, 63, 6), 62]
    azimuth_indices = list(range(0, 72, 6))
    assert len(ring_indices) == 12 and len(azimuth_indices) == 12
    for key in ("one", "four", "eight"):
        path = PILOT / f"{key}-mesh.npz"
        assert sha(ROOT / path) == audit["source_pins"][str(path)]
        source_files[str(path)] = sha(ROOT / path)
        with np.load(ROOT / path, allow_pickle=False) as pack:
            saved[key] = np.array(pack["radius_px"])
            vertices = np.array(pack["vertices"])
        assert saved[key].shape == (30, 72, 65)
        assert vertices.shape == (30, 4538, 3)
        mesh_samples[key] = np.round(
            vertices[
                :, [1 + ring * 72 + azimuth for ring in ring_indices for azimuth in azimuth_indices]
            ],
            5,
        ).tolist()
    curve_path = PILOT / "curves.json"
    assert sha(ROOT / curve_path) == audit["source_pins"][str(curve_path)]
    source_files[str(curve_path)] = sha(ROOT / curve_path)
    curves = json.loads((ROOT / curve_path).read_text())

    source_frames, output_frames, reference_frames, radial_samples = [], [], [], []
    for frame in range(1, 31):
        supplied = np.asarray(source_image("mask", 1, frame)) == 127
        withheld = np.asarray(source_image("mask", 8, frame)) == 127
        additional_inputs = []
        for plane in (10, 19, 28):
            supplied_extra = np.asarray(source_image("mask", plane, frame)) == 127
            additional_inputs.append(
                {
                    "plane_1based": plane,
                    "image": png_data(source_image("image", plane, frame)),
                    "contour": outline(supplied_extra, (131, 152, 173)),
                }
            )
        source_frames.append(
            {
                "frame_1based": frame,
                "supplied_image": png_data(source_image("image", 1, frame)),
                "supplied_contour": outline(supplied, (131, 152, 173)),
                "additional_inputs": additional_inputs,
                "withheld_image": png_data(source_image("image", 8, frame)),
            }
        )
        output_frames.append(
            {
                key: outline(projected_mask(saved[key][frame - 1], 7), (24, 198, 212))
                for key in saved
            }
        )
        polar_indices = list(range(0, 65, 8))
        radial_samples.append(
            {
                "polar_index": polar_indices,
                "positive_radius_px": [
                    float(saved["four"][frame - 1, 0, i]) for i in polar_indices
                ],
                "negative_radius_px": [
                    float(saved["four"][frame - 1, 36, i]) for i in polar_indices
                ],
            }
        )
        reference_frames.append({"withheld_contour": outline(withheld, (244, 188, 73))})

    out.mkdir(parents=True)
    payloads = {
        "source.json": {
            "patient": "Patient001",
            "frame": "FeEcho4D-native",
            "shape_hw": [464, 485],
            "spacing_mm_per_pixel": SPACING_MM,
            "frames": source_frames,
            "supplied_planes_1based": {
                "one": [1],
                "four": [1, 10, 19, 28],
                "eight": [1, 5, 10, 14, 19, 23, 28, 32],
            },
            "withheld_planes_1based": [3, 8, 12, 17, 21, 26, 30, 35],
        },
        "output.json": {
            "frames": output_frames,
            "curves_ml": {key: values for key, values in curves.items() if key != "dense"},
            "mesh_samples_mm": mesh_samples,
            "mesh_sample_grid": {
                "rings": len(ring_indices),
                "azimuths": len(azimuth_indices),
                "rule": "saved vertex index 1 + ring*72 + azimuth; every sixth ring/azimuth plus last ring",
            },
            "radial_samples": radial_samples,
            "source": "retained BR-025 author baseline; display sampling only",
        },
        "reference.json": {
            "frames": reference_frames,
            "dense_curve_ml": curves["dense"],
            "stats": {
                key: audit["recomputed_stats"][key]
                for key in ("one", "two", "four", "eight", "dense", "static")
            },
            "depth_control": audit["missing_depth_control"],
            "denominator": "one Patient001; 30 frames times 8 common withheld planes = 240 frame/plane pairs per sparse condition",
        },
    }
    for name, payload in payloads.items():
        (out / name).write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    notice = (ROOT / "presentation/task-explorer/cardiac-contour/NOTICE.md").read_text()
    (out / "NOTICE.md").write_text(notice)
    assets = [
        {
            "file": name,
            "sha256": sha(out / name),
            "bytes": (out / name).stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
        }
        for name in (*payloads, "NOTICE.md")
    ]
    manifest = {
        "schema": 1,
        "id": "retained-cardiac-contour-v1",
        "frame": "FeEcho4D-native",
        "units": "mm",
        "license": "LicenseRef-FeEcho4D-noncommercial-research",
        "label_license": "LicenseRef-FeEcho4D-noncommercial-research",
        "reference_policy": "reader-reference-reveal",
        "source_class": "source-derived-teaching",
        "sources": source_files,
        "checks": {
            "native_frames": 30,
            "source_planes": [1, 8],
            "withheld_plane": 8,
            "saved_projection_conditions": ["one", "four", "eight"],
            "model_execution": False,
        },
        "assets": assets,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(out), "assets": assets}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    build(parser.parse_args().out)
