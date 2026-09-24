"""Explicit imaging acceptance check; uses an existing NumPy/Pillow environment."""

import json
from pathlib import Path

import numpy as np
from PIL import Image


def check() -> dict[str, object]:
    folder = (
        Path(__file__).resolve().parents[1]
        / "presentation/assets/teaching-fixtures/route-unfold-v1"
    )
    route = json.loads((folder / "route.json").read_text())
    geometry = json.loads((folder / "geometry.json").read_text())
    volume = np.load(folder / "branching-phantom-volume.npz")
    points = (
        np.array(route["points"])[:, None, :]
        + np.array(route["u_m"])[None, :, None] * np.array(route["normals"])[:, None, :]
    )
    coordinates = (points - volume["origin_m"]) / volume["spacing_m"]
    low = np.floor(coordinates).astype(int)
    fraction = coordinates - low
    values = volume["values"]
    sampled = np.zeros(coordinates.shape[:2])
    for x in (0, 1):
        for y in (0, 1):
            for z in (0, 1):
                index = low + np.array([x, y, z])
                weight = np.prod(np.where(np.array([x, y, z]), fraction, 1 - fraction), axis=2)
                valid = np.all((index >= 0) & (index < np.array(values.shape)), axis=2)
                clipped = np.clip(index, 0, np.array(values.shape) - 1)
                sampled += (
                    values[clipped[:, :, 0], clipped[:, :, 1], clipped[:, :, 2]] * weight * valid
                )
    scalar_error = float(np.max(np.abs(sampled - np.array(route["sample_values"]))))
    vertex_error = float(
        np.max(
            np.linalg.norm(
                np.array(geometry["ribbon"]["vertices"]).reshape(192, 25, 3) - points[:, ::4, :],
                axis=2,
            )
        )
    )
    image = np.asarray(Image.open(folder / "cpr-sampled.png"))
    expected = (np.clip(np.array(route["sample_values"]).T[::-1], 0, 1) * 255).astype("uint8")
    raster = np.asarray(
        Image.fromarray(expected).resize((768, 184), Image.Resampling.BILINEAR).convert("RGB")
    )
    pixel_error = int(np.max(np.abs(image.astype(int) - raster.astype(int))))
    assert scalar_error < 3e-5, scalar_error
    assert vertex_error < 2e-7, vertex_error
    assert pixel_error <= 1, pixel_error
    return {
        "samples": int(sampled.size),
        "ribbon_vertices": 4800,
        "max_scalar_error": scalar_error,
        "max_vertex_error_m": vertex_error,
        "max_display_error_8bit": pixel_error,
        "display": "192x97 scalar raster, transverse row reversed; bilinear 768x184 physical-aspect display derivative",
    }


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
