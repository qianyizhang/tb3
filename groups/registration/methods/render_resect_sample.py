#!/usr/bin/env python3
"""Render a bounded RESECT MRI/iUS landmark sample without extra dependencies.

The script reads NIfTI-1 volumes and MNI tag points, selects one reader-only
example landmark near the paired tumor-mask centroids, and writes compact PNG
previews plus a JSON manifest. The selected crops are explanatory views, not
solver inputs; the full native volumes remain the proposed task inputs.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path

import numpy as np


DTYPES = {
    2: np.dtype("u1"),
    4: np.dtype("i2"),
    8: np.dtype("i4"),
    16: np.dtype("f4"),
    64: np.dtype("f8"),
    256: np.dtype("i1"),
    512: np.dtype("u2"),
    768: np.dtype("u4"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_nifti(
    path: Path, *, require_sform: bool = True
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    with gzip.open(path, "rb") as stream:
        payload = stream.read()
    endian = "<" if struct.unpack_from("<i", payload, 0)[0] == 348 else ">"
    if struct.unpack_from(f"{endian}i", payload, 0)[0] != 348:
        raise ValueError(f"Not a NIfTI-1 file: {path}")
    dim = struct.unpack_from(f"{endian}8h", payload, 40)
    shape = tuple(int(value) for value in dim[1 : dim[0] + 1])
    datatype = struct.unpack_from(f"{endian}h", payload, 70)[0]
    dtype = DTYPES.get(datatype)
    if dtype is None:
        raise ValueError(f"Unsupported NIfTI datatype {datatype}: {path}")
    dtype = dtype.newbyteorder(endian)
    pixdim = struct.unpack_from(f"{endian}8f", payload, 76)
    vox_offset = int(struct.unpack_from(f"{endian}f", payload, 108)[0])
    slope = struct.unpack_from(f"{endian}f", payload, 112)[0] or 1.0
    intercept = struct.unpack_from(f"{endian}f", payload, 116)[0]
    sform_code = struct.unpack_from(f"{endian}h", payload, 254)[0]
    if not sform_code and require_sform:
        raise ValueError(f"NIfTI sform is required for world-coordinate tags: {path}")
    affine = np.eye(4, dtype=float)
    if sform_code:
        affine[0] = struct.unpack_from(f"{endian}4f", payload, 280)
        affine[1] = struct.unpack_from(f"{endian}4f", payload, 296)
        affine[2] = struct.unpack_from(f"{endian}4f", payload, 312)
    count = int(np.prod(shape))
    data = np.frombuffer(payload, dtype=dtype, count=count, offset=vox_offset)
    data = data.reshape(shape, order="F").astype(np.float32)
    data = data * slope + intercept
    meta = {
        "shape": list(shape),
        "spacing_mm": [float(value) for value in pixdim[1 : len(shape) + 1]],
        "affine": affine.tolist(),
        "datatype": int(datatype),
    }
    return data, affine, meta


def read_tag(path: Path) -> np.ndarray:
    points = []
    for line in path.read_text().splitlines():
        values = re.findall(r"[-+]?\d+(?:\.\d+)?", line.split('"', 1)[0])
        if len(values) == 6:
            points.append([float(value) for value in values])
    if not points:
        raise ValueError(f"No paired landmarks found: {path}")
    return np.asarray(points, dtype=float)


def world_to_voxel(world: np.ndarray, affine: np.ndarray) -> np.ndarray:
    homogeneous = np.append(world, 1.0)
    return np.linalg.inv(affine).dot(homogeneous)[:3]


def mask_centroid_world(mask: np.ndarray, affine: np.ndarray) -> np.ndarray:
    indices = np.argwhere(mask > 0)
    if len(indices) == 0:
        raise ValueError("Tumor mask is empty")
    voxel = indices.mean(axis=0)
    return affine.dot(np.append(voxel, 1.0))[:3]


def percentile_window(volume: np.ndarray) -> tuple[float, float]:
    foreground = volume[np.isfinite(volume) & (volume != 0)]
    if foreground.size == 0:
        foreground = volume[np.isfinite(volume)]
    low, high = np.percentile(foreground, [1, 99])
    if high <= low:
        high = low + 1.0
    return float(low), float(high)


def sample_plane(
    volume: np.ndarray,
    center: np.ndarray,
    axis: int,
    radius_voxels: float,
    size: int,
) -> np.ndarray:
    axes = [index for index in range(3) if index != axis]
    line = np.linspace(-radius_voxels, radius_voxels, size)
    first, second = np.meshgrid(line, line, indexing="xy")
    coords = np.empty((3, size, size), dtype=int)
    coords[axis] = int(round(center[axis]))
    coords[axes[0]] = np.rint(center[axes[0]] + first).astype(int)
    coords[axes[1]] = np.rint(center[axes[1]] + second).astype(int)
    valid = np.ones((size, size), dtype=bool)
    for index, bound in enumerate(volume.shape[:3]):
        valid &= (coords[index] >= 0) & (coords[index] < bound)
        coords[index] = np.clip(coords[index], 0, bound - 1)
    plane = volume[coords[0], coords[1], coords[2]].copy()
    plane[~valid] = 0
    return np.flipud(plane)


def normalize(plane: np.ndarray, window: tuple[float, float]) -> np.ndarray:
    low, high = window
    scaled = np.clip((plane - low) / (high - low), 0, 1)
    return np.rint(scaled * 255).astype(np.uint8)


def render_row(
    volume: np.ndarray,
    mask: np.ndarray,
    center: np.ndarray,
    spacing: list[float],
    size: int,
    radius_mm: float,
    overlay: bool,
    crosshair: bool,
    mask_color: tuple[int, int, int],
) -> np.ndarray:
    window = percentile_window(volume)
    panels = []
    for axis in range(3):
        plane = sample_plane(volume, center, axis, radius_mm / spacing[axis], size)
        gray = normalize(plane, window)
        rgb = np.repeat(gray[:, :, None], 3, axis=2)
        if overlay:
            mask_plane = sample_plane(mask, center, axis, radius_mm / spacing[axis], size) > 0
            color = np.asarray(mask_color, dtype=np.float32)
            rgb[mask_plane] = np.rint(0.35 * rgb[mask_plane] + 0.65 * color).astype(np.uint8)
        if crosshair:
            midpoint = size // 2
            rgb[midpoint - 1 : midpoint + 2, :, :] = (255, 215, 0)
            rgb[:, midpoint - 1 : midpoint + 2, :] = (255, 215, 0)
        panels.append(rgb)
    separator = np.full((size, 4, 3), 18, dtype=np.uint8)
    row = panels[0]
    for panel in panels[1:]:
        row = np.concatenate([row, separator, panel], axis=1)
    return row


def write_png(path: Path, rgb: np.ndarray) -> None:
    height, width, channels = rgb.shape
    if channels != 3 or rgb.dtype != np.uint8:
        raise ValueError("PNG input must be uint8 RGB")
    raw = b"".join(b"\x00" + rgb[row].tobytes() for row in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    payload = b"\x89PNG\r\n\x1a\n"
    payload += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += chunk(b"IDAT", zlib.compress(raw, level=9))
    payload += chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def render_case(case_dir: Path, output_dir: Path, case_id: str) -> dict[str, object]:
    flair_path = case_dir / f"{case_id}-FLAIR.nii.gz"
    us_path = case_dir / f"{case_id}-US-before.nii.gz"
    flair_mask_path = case_dir / f"{case_id}-FLAIR-tumor.nii.gz"
    us_mask_path = case_dir / f"{case_id}-US-before-tumor.nii.gz"
    tag_path = case_dir / f"{case_id}-MRI-beforeUS.tag"
    flair, flair_affine, flair_meta = read_nifti(flair_path)
    us, us_affine, us_meta = read_nifti(us_path)
    flair_mask, _, _ = read_nifti(flair_mask_path, require_sform=False)
    us_mask, _, _ = read_nifti(us_mask_path, require_sform=False)
    points = read_tag(tag_path)
    flair_centroid = mask_centroid_world(flair_mask, flair_affine)
    us_centroid = mask_centroid_world(us_mask, us_affine)
    distances = np.linalg.norm(points[:, :3] - flair_centroid, axis=1)
    distances += np.linalg.norm(points[:, 3:] - us_centroid, axis=1)
    landmark_index = int(np.argmin(distances))
    pair = points[landmark_index]
    initial_distances = np.linalg.norm(points[:, 3:] - points[:, :3], axis=1)
    flair_voxel = world_to_voxel(pair[:3], flair_affine)
    us_voxel = world_to_voxel(pair[3:], us_affine)
    size = 180
    radius_mm = 18.0
    gap = np.full((4, size * 3 + 8, 3), 18, dtype=np.uint8)

    def paired_view(overlay: bool = False, crosshair: bool = False) -> np.ndarray:
        mri_row = render_row(
            flair,
            flair_mask,
            flair_voxel,
            flair_meta["spacing_mm"],
            size,
            radius_mm,
            overlay,
            crosshair,
            (238, 84, 144),
        )
        us_row = render_row(
            us,
            us_mask,
            us_voxel,
            us_meta["spacing_mm"],
            size,
            radius_mm,
            overlay,
            crosshair,
            (0, 220, 220),
        )
        return np.concatenate([mri_row, gap, us_row], axis=0)

    names = {
        "input": f"{case_id.lower()}-input.png",
        "helper": f"{case_id.lower()}-tumor-context.png",
        "reference": f"{case_id.lower()}-landmark-reference.png",
    }
    write_png(output_dir / names["input"], paired_view())
    write_png(output_dir / names["helper"], paired_view(overlay=True))
    write_png(output_dir / names["reference"], paired_view(crosshair=True))
    displacement = pair[3:] - pair[:3]
    files = [flair_path, us_path, flair_mask_path, us_mask_path, tag_path]
    return {
        "case_id": case_id,
        "source_files": [
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ],
        "flair": flair_meta,
        "us_before": us_meta,
        "landmark_count": int(len(points)),
        "shared_world_coordinate_copy_baseline": {
            "description": "Error from predicting each MRI world coordinate unchanged as the US coordinate.",
            "mean_mm": float(initial_distances.mean()),
            "rms_mm": float(np.sqrt(np.mean(initial_distances**2))),
            "median_mm": float(np.median(initial_distances)),
            "min_mm": float(initial_distances.min()),
            "max_mm": float(initial_distances.max()),
            "within_3_mm": int(np.count_nonzero(initial_distances <= 3.0)),
            "within_5_mm": int(np.count_nonzero(initial_distances <= 5.0)),
        },
        "reader_example": {
            "selection": "Published landmark nearest the paired tumor-mask centroids; selected after inspecting evaluator-only annotations.",
            "landmark_index_zero_based": landmark_index,
            "mri_world_mm": pair[:3].round(6).tolist(),
            "us_world_mm": pair[3:].round(6).tolist(),
            "initial_displacement_mm": displacement.round(6).tolist(),
            "initial_distance_mm": float(np.linalg.norm(displacement)),
            "mri_voxel_continuous": flair_voxel.round(4).tolist(),
            "us_voxel_continuous": us_voxel.round(4).tolist(),
            "crop_radius_mm": radius_mm,
            "plane_order": ["axis-0", "axis-1", "axis-2"],
        },
        "figures": names,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    arguments = parser.parse_args()
    cases = [
        render_case(arguments.source / case_id, arguments.output, case_id)
        for case_id in ("Case1", "Case2", "Case3")
    ]
    manifest = {
        "schema_version": 1,
        "dataset": "RESECT + RESECT-SEG bounded sample",
        "upstream_revision": "e86fb37dd93f7a9c64e48952f71410af59b04b9b",
        "source": "https://huggingface.co/datasets/MedOtter/RESECT-SEG",
        "dataset_dois": {
            "current_landing_pages_and_rehost": "10.11582/2017.00004",
            "dataset_article_data_access_section": "10.11582/2016.00003",
        },
        "landmark_reference": "MNI tag files; first three values are MRI world coordinates and last three are pre-resection US world coordinates, in millimetres.",
        "license": {
            "images_and_landmarks": "CC BY 4.0",
            "resect_seg_masks": "CC BY-NC-SA 4.0",
            "combined_sample": "CC BY-NC-SA 4.0",
        },
        "cases": cases,
    }
    arguments.manifest.parent.mkdir(parents=True, exist_ok=True)
    arguments.manifest.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
