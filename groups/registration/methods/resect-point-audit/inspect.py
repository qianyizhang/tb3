#!/usr/bin/env python3
"""Render paired orthogonal FLAIR/US views around requested world points."""

from __future__ import annotations

import argparse
import gzip
import json
import struct
import zlib
from pathlib import Path

import numpy as np


DTYPES = {2: "u1", 4: "i2", 8: "i4", 16: "f4", 64: "f8", 256: "i1", 512: "u2"}


def read_nifti(path: Path):
    with gzip.open(path, "rb") as stream:
        raw = stream.read()
    endian = "<" if struct.unpack_from("<i", raw, 0)[0] == 348 else ">"
    dim = struct.unpack_from(f"{endian}8h", raw, 40)
    shape = tuple(int(x) for x in dim[1 : dim[0] + 1])
    datatype = struct.unpack_from(f"{endian}h", raw, 70)[0]
    if datatype not in DTYPES:
        raise ValueError(f"unsupported NIfTI datatype {datatype}")
    pixdim = struct.unpack_from(f"{endian}8f", raw, 76)
    offset = int(struct.unpack_from(f"{endian}f", raw, 108)[0])
    slope = struct.unpack_from(f"{endian}f", raw, 112)[0] or 1.0
    intercept = struct.unpack_from(f"{endian}f", raw, 116)[0]
    if struct.unpack_from(f"{endian}h", raw, 254)[0] == 0:
        raise ValueError("NIfTI sform is required")
    affine = np.eye(4)
    affine[0] = struct.unpack_from(f"{endian}4f", raw, 280)
    affine[1] = struct.unpack_from(f"{endian}4f", raw, 296)
    affine[2] = struct.unpack_from(f"{endian}4f", raw, 312)
    dtype = np.dtype(DTYPES[datatype]).newbyteorder(endian)
    data = np.frombuffer(raw, dtype=dtype, count=int(np.prod(shape)), offset=offset)
    data = data.reshape(shape, order="F").astype(np.float32) * slope + intercept
    return data, affine, [float(x) for x in pixdim[1:4]]


def voxel(world, affine):
    return np.linalg.inv(affine).dot(np.append(np.asarray(world, dtype=float), 1.0))[:3]


def window(volume):
    values = volume[np.isfinite(volume) & (volume != 0)]
    low, high = np.percentile(values, [1, 99])
    return float(low), float(max(high, low + 1))


def plane(volume, center, axis, radius_voxels, size=180):
    other = [i for i in range(3) if i != axis]
    line = np.linspace(-radius_voxels, radius_voxels, size)
    one, two = np.meshgrid(line, line, indexing="xy")
    coordinates = np.empty((3, size, size), dtype=int)
    coordinates[axis] = round(center[axis])
    coordinates[other[0]] = np.rint(center[other[0]] + one).astype(int)
    coordinates[other[1]] = np.rint(center[other[1]] + two).astype(int)
    valid = np.ones((size, size), dtype=bool)
    for index, bound in enumerate(volume.shape):
        valid &= (coordinates[index] >= 0) & (coordinates[index] < bound)
        coordinates[index] = np.clip(coordinates[index], 0, bound - 1)
    result = volume[coordinates[0], coordinates[1], coordinates[2]].copy()
    result[~valid] = 0
    return np.flipud(result)


def row(volume, center, spacing, radius_mm):
    low, high = window(volume)
    panels = []
    for axis in range(3):
        image = plane(volume, center, axis, radius_mm / spacing[axis])
        image = np.uint8(np.rint(np.clip((image - low) / (high - low), 0, 1) * 255))
        rgb = np.repeat(image[:, :, None], 3, axis=2)
        middle = rgb.shape[0] // 2
        rgb[middle - 1 : middle + 2, :, :] = (255, 215, 0)
        rgb[:, middle - 1 : middle + 2, :] = (255, 215, 0)
        panels.append(rgb)
    divider = np.full((180, 4, 3), 18, dtype=np.uint8)
    return np.concatenate([panels[0], divider, panels[1], divider, panels[2]], axis=1)


def write_png(path, rgb):
    height, width, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(height))

    def chunk(kind, content):
        body = kind + content
        return struct.pack(">I", len(content)) + body + struct.pack(">I", zlib.crc32(body))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=("case_a", "case_b"), required=True)
    parser.add_argument("--mri-center", nargs=3, type=float)
    parser.add_argument("--us-center", nargs=3, type=float)
    parser.add_argument("--radius-mm", type=float, default=18.0)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = Path("/app/data")
    query = {
        item["case_id"]: item for item in json.loads((data / "queries.json").read_text())["cases"]
    }[args.case]
    mri_world = args.mri_center or query["mri_world_mm"]
    us_world = args.us_center or query["initial_us_world_mm"]
    flair, flair_affine, flair_spacing = read_nifti(data / f"{args.case}_flair.nii.gz")
    us, us_affine, us_spacing = read_nifti(data / f"{args.case}_us.nii.gz")
    mri_voxel, us_voxel = voxel(mri_world, flair_affine), voxel(us_world, us_affine)
    divider = np.full((4, 548, 3), 18, dtype=np.uint8)
    image = np.concatenate(
        [
            row(flair, mri_voxel, flair_spacing, args.radius_mm),
            divider,
            row(us, us_voxel, us_spacing, args.radius_mm),
        ],
        axis=0,
    )
    write_png(args.out, image)
    print(
        json.dumps(
            {
                "case_id": args.case,
                "mri_world_mm": mri_world,
                "mri_voxel": mri_voxel.tolist(),
                "us_world_mm": us_world,
                "us_voxel": us_voxel.tolist(),
                "radius_mm": args.radius_mm,
                "output": str(args.out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
