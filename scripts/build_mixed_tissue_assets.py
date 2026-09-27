"""Extract three licensed BR-017 teaching slices into a fresh directory; never edit a task."""

import argparse
import hashlib
import io
import json
import shutil
import tarfile
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n")


def load_npz(source):
    with np.load(source, allow_pickle=False) as z:
        return {key: z[key] for key in z.files}


def archive_arrays(path):
    wanted = {"ct.npz", "o327.npz", "o589.npz"}
    with tarfile.open(path) as archive:
        return {
            Path(member.name).name: load_npz(io.BytesIO(archive.extractfile(member).read()))
            for member in archive.getmembers()
            if member.isfile() and Path(member.name).name in wanted
        }


def sample(array, points, key="mask"):
    affine = array["affine_lps"]
    inv = np.linalg.inv(affine)
    continuous = sum(points[..., j, None] * inv[:3, j] for j in range(3)) + inv[:3, 3]
    indices = np.rint(continuous).astype(int)
    if not np.allclose(indices, continuous, atol=1e-6):
        raise ValueError("Slice sample is off the native voxel lattice")
    data = array[key]
    valid = np.all((indices >= 0) & (indices < data.shape), axis=-1)
    result = np.zeros(indices.shape[:-1], dtype=data.dtype)
    result[valid] = data[tuple(indices[valid].T)]
    return result


def boundary(mask):
    """Exact unsmoothed pixel-edge segments; display only, never a scoring contour."""
    m = np.pad(mask.astype(bool), 1)
    commands = []
    for y, x in np.argwhere(mask):
        if not m[y, x + 1]:
            commands.append(f"M{x},{y}h1")
        if not m[y + 2, x + 1]:
            commands.append(f"M{x},{y + 1}h1")
        if not m[y + 1, x]:
            commands.append(f"M{x},{y}v1")
        if not m[y + 1, x + 2]:
            commands.append(f"M{x + 1},{y}v1")
    return "".join(commands)


def cells(mask):
    return "".join(f"M{x},{y}h1v1h-1z" for y, x in np.argwhere(mask))


def build(root, output):
    output.mkdir(parents=True, exist_ok=False)
    sources = {}
    tasks = {}
    for condition in ("m01", "m02", "n01", "f01"):
        freeze = root / f"docs/evidence/br017-abdomen-{condition}-freeze.json"
        record = json.loads(freeze.read_text())["tasks"][0]
        task = root / record["task_path"]
        tasks[condition] = task
        sources[freeze.relative_to(root).as_posix()] = sha(freeze)
        for name, digest in record["files"].items():
            path = task / name
            if sha(path) != digest:
                raise ValueError(f"Frozen source changed: {path}")
            sources[path.relative_to(root).as_posix()] = digest
    public = archive_arrays(tasks["m02"] / "environment/data.tar.gz")
    control = archive_arrays(tasks["n01"] / "environment/data.tar.gz")
    if sha(tasks["m02"] / "environment/data.tar.gz") != sha(
        tasks["f01"] / "environment/data.tar.gz"
    ):
        raise ValueError("M02/F01 public inputs differ")
    for key in ("hu", "affine_lps"):
        if not np.array_equal(public["ct.npz"][key], control["ct.npz"][key]):
            raise ValueError("M02/N01 CT differs")
    expected = json.loads((tasks["m02"] / "tests/expected.json").read_text())
    finding = expected["findings"][0]
    witness = np.asarray(finding["oracle_point_lps_mm"])
    region = load_npz(tasks["m02"] / "tests/region-0.npz")
    if not sample(region, witness[None, :])[0]:
        raise ValueError("Oracle point not inside native region")
    # Cross-check full native region against the public host addition and donor subtraction.
    indices = np.argwhere(region["mask"])
    points = (
        sum(indices[:, j, None] * region["affine_lps"][:3, j] for j in range(3))
        + region["affine_lps"][:3, 3]
    )
    if not (
        sample(public["o327.npz"], points).all()
        and not sample(control["o327.npz"], points).any()
        and sample(control["o589.npz"], points).all()
        and not sample(public["o589.npz"], points).any()
    ):
        raise ValueError("Retained region disagrees with transferred voxel membership")
    voxel_ml = abs(np.linalg.det(region["affine_lps"][:3, :3])) / 1000
    slices = []
    size = 149
    yy, xx = np.mgrid[:size, :size]
    for name, x_axis, y_axis, horizontal, vertical in (
        ("axial", [1.5, 0, 0], [0, 1.5, 0], "L", "P"),
        ("coronal", [1.5, 0, 0], [0, 0, -1.5], "L", "I"),
        ("sagittal", [0, 1.5, 0], [0, 0, -1.5], "P", "I"),
    ):
        dx, dy = np.asarray(x_axis), np.asarray(y_axis)
        origin = witness - 74 * (dx + dy)
        points = origin + xx[..., None] * dx + yy[..., None] * dy
        ct = sample(public["ct.npz"], points, "hu")
        pixels = np.rint(np.clip((ct.astype(float) + 150) / 400, 0, 1) * 255).astype("uint8")
        Image.fromarray(pixels).save(output / f"{name}.png")
        masks = {
            "host": sample(public["o327.npz"], points),
            "donor": sample(public["o589.npz"], points),
            "original_host": sample(control["o327.npz"], points),
            "region": sample(region, points),
        }
        if not masks["region"][74, 74] or not masks["host"][74, 74]:
            raise ValueError("Displayed witness must be inside host and reference region")
        slices.append(
            {
                "plane": name,
                "image": f"{name}.png",
                "size": size,
                "pixel_center_origin_lps_mm": origin.tolist(),
                "pixel_dx_lps_mm": dx.tolist(),
                "pixel_dy_lps_mm": dy.tolist(),
                "right": horizontal,
                "down": vertical,
                "witness_pixel": [74.5, 74.5],
                "paths": {key: boundary(value) for key, value in masks.items()},
                "region_cells": cells(masks["region"]),
                "reference_voxels_in_slice": int(masks["region"].sum()),
            }
        )
    fixture = {
        "source_case": "s1233",
        "condition": "BR-017 M02",
        "spacing_mm": 1.5,
        "window_hu": {"level": 50, "width": 400},
        "slices": slices,
        "host_id": "o327",
        "host_proposed_label": "duodenum",
        "donor_id": "o589",
        "included_label": finding["included_label"],
        "witness_lps_mm": witness.tolist(),
        "reference_voxels": len(indices),
        "reference_volume_ml": len(indices) * voxel_ml,
        "remaining_pancreas_ml": float(public["o589.npz"]["mask"].sum()) * voxel_ml,
        "tolerance_mm": expected["point_tolerance_mm"],
        "limits": "Three oracle-centred teaching crops; not a blind search or full-volume audit. Reference is author-only in the task and revealed explicitly to the reader. Synthetic mask reassignment, not disease or clinical contour adjudication.",
    }
    dump(output / "fixture.json", fixture)
    for name in ("DATA-LICENSE.txt", "LABEL-LICENSE.txt"):
        shutil.copyfile(tasks["m02"] / "environment" / name, output / name)
    (output / "NOTICE.md").write_text(
        "# BR-017 selected CT slices and mask outlines\n\n"
        "TotalSegmentator small v2.0.1, Wasserthal and University Hospital Basel. "
        "Source: https://zenodo.org/records/10047263 . Data: CC BY 4.0; taxonomy: Apache 2.0. "
        "Full terms are retained alongside these assets. No source author endorses this view.\n\n"
        "These three s1233 slices are extracted from the hash-verified BR-017 M02 task archive. "
        "CT voxel values are windowed at level 50 / width 400 HU into 8-bit PNGs, with no spatial "
        "interpolation. Each 149-pixel square covers 223.5 mm. Outlines follow native voxel edges; "
        "they are display paths, not returned contours. Pixel-centre LPS transforms are in fixture.json.\n\n"
        "All planes and crops were selected using the private oracle point. This is a reader teaching "
        "view, not evidence of finding the location independently. The gold region and witness are "
        "private-evaluator material, shown only after reference reveal. They must not be passed to "
        "a solver. Before reveal, teal marks the supplied duodenum host and blue the remaining "
        "pancreas. Gold marks transferred source-pancreas voxels after reveal; a white ring marks "
        "the reference witness. The task does not expose original reference masks.\n\n"
        "M02 is a synthetic label edit with unchanged CT. N01 source masks are used only to verify "
        "voxel lineage, not to assert clinical correctness. This retained display supports no "
        "diagnosis, population claim or new model result. Full volumes remain local.\n\n"
        "Rebuild to a fresh output with `.venv-br030/bin/python scripts/build_mixed_tissue_assets.py "
        "--root . --output NEW_DIRECTORY`; NumPy and Pillow suffice. Never import historical "
        "authoring modules or overwrite freezes.\n"
    )
    assets = [
        {
            "file": p.name,
            "sha256": sha(p),
            "bytes": p.stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if p.name == "fixture.json" else "illustration",
        }
        for p in sorted(output.iterdir())
    ]
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-mixed-tissue-v1",
            "frame": "LPS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "Apache-2.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "assets": assets,
            "source_case": "s1233",
            "derivation": str(Path(__file__).name),
            "checks": {
                "frozen_files_verified": len(sources) - 4,
                "ct_equal_m02_n01": True,
                "m02_f01_public_archive_equal": True,
                "region_membership_verified": len(indices),
            },
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "slices": 3,
                "reference_voxels": len(indices),
                "reference_volume_ml": fixture["reference_volume_ml"],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output)
