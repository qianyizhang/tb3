"""Verify the retained RESECT sample and make query-centred teaching sections.

Read-only toward source volumes. Importing this module performs no work.
Requires the existing optional imaging environment (nibabel, NumPy, SciPy, Pillow).
"""

import argparse
import base64
import io
import itertools
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from build_respiratory_assets import dump, read, sha, world
from PIL import Image
from scipy.ndimage import map_coordinates

MANIFEST = "groups/registration/presentation/sources/resect-sample.json"
MANIFEST_SHA = "de9ab0bdd1981ecfd10200b84bfb6f21a946ee1de5ac44bcd95fbb4f17c412fa"


def png(array):
    stream = io.BytesIO()
    Image.fromarray(array).save(stream, format="PNG")
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()


def section(data, affine, center, axes, window, native=False, mask=False):
    a, b = axes
    if native:
        # Fit complete native sections to 160 pixels; retain exact world calibration.
        width = round(160 * data.shape[a] / max(data.shape[a], data.shape[b]))
        height = round(160 * data.shape[b] / max(data.shape[a], data.shape[b]))
        dx = affine[:3, a] * (data.shape[a] - 1) / (width - 1)
        dy = affine[:3, b] * (data.shape[b] - 1) / (height - 1)
        voxel = world(center[None], np.linalg.inv(affine))[0]
        voxel[a] = voxel[b] = 0
        origin = world(voxel[None], affine)[0]
    else:
        width = height = 97
        dx, dy = np.eye(3)[a] * 0.5, np.eye(3)[b] * 0.5
        origin = center - 48 * (dx + dy)
    v, u = np.indices((height, width))
    points = origin + u[..., None] * dx + v[..., None] * dy
    coords = world(points.reshape(-1, 3), np.linalg.inv(affine))
    inside = np.all((coords >= -1e-7) & (coords <= np.array(data.shape) - 1 + 1e-7), axis=1)
    sampled = map_coordinates(
        data,
        np.clip(coords, 0, np.array(data.shape) - 1).T,
        order=0 if mask else 1,
        prefilter=False,
    ).reshape(height, width)
    if mask:
        pixels = np.where(sampled > 0, 255, 0).astype("uint8")
    else:
        pixels = np.rint(
            255 * np.clip((sampled - window[0]) / (window[1] - window[0]), 0, 1)
        ).astype("uint8")
    # Transparent outside the actual source support, never extrapolated tissue.
    rgba = np.zeros((height, width, 4), dtype="uint8")
    rgba[..., :3] = pixels[..., None]
    rgba[..., 3] = inside.reshape(height, width) * 255
    if mask:
        rgba[..., 3] *= pixels > 0
    return {
        "name": ("native " if native else "RAS ")
        + ["XY" if axes == (0, 1) else "XZ" if axes == (0, 2) else "YZ"][0],
        "width": width,
        "height": height,
        "origin_world_mm": origin.tolist(),
        "dx_world_mm": dx.tolist(),
        "dy_world_mm": dy.tolist(),
        "coverage_fraction": float(inside.mean()),
        "png": png(rgba),
    }


def build(root, output, mask_license):
    output.mkdir(parents=True, exist_ok=False)
    if sha(root / MANIFEST) != MANIFEST_SHA:
        raise ValueError("Retained source manifest changed")
    record = read(root / MANIFEST)
    sources = {MANIFEST: MANIFEST_SHA}
    geometry, references, helpers, checks = [], [], {}, []
    for case in record["cases"]:
        case_id = case["case_id"]
        folder = root / ".local/datasets/resect-sample/e86fb37" / case_id
        for item in case["source_files"]:
            path = folder / item["name"]
            if path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
                raise ValueError(f"Source bytes changed: {path}")
            sources[str(path.relative_to(root))] = item["sha256"]
        tag_rows = []
        for line in (folder / f"{case_id}-MRI-beforeUS.tag").read_text().splitlines():
            pieces = line.strip().split()
            if len(pieces) >= 6:
                try:
                    tag_rows.append([float(x) for x in pieces[:6]])
                except ValueError:
                    pass
        tags = np.array(tag_rows)
        if tags.shape != (15, 6):
            raise ValueError("Unexpected paired tag schema")
        distances = np.linalg.norm(tags[:, :3] - tags[:, 3:], axis=1)
        baseline = {
            "mean_mm": float(distances.mean()),
            "rms_mm": float(np.sqrt(np.mean(distances**2))),
            "median_mm": float(np.median(distances)),
            "min_mm": float(distances.min()),
            "max_mm": float(distances.max()),
            "within_3_mm": int((distances <= 3).sum()),
            "within_5_mm": int((distances <= 5).sum()),
        }
        if any(
            abs(v - case["shared_world_coordinate_copy_baseline"][k]) > 1e-10
            for k, v in baseline.items()
        ):
            raise ValueError("Retained baseline mismatch")
        selected = case["reader_example"]["landmark_index_zero_based"]
        query, target = tags[selected, :3], tags[selected, 3:]
        if not np.array_equal(query, case["reader_example"]["mri_world_mm"]) or not np.array_equal(
            target, case["reader_example"]["us_world_mm"]
        ):
            raise ValueError("Selected reference mismatch")
        public = {"id": case_id, "query_world_mm": query.tolist(), "modalities": {}}
        for key, name, points in [("mri", "FLAIR", tags[:, :3]), ("us", "US-before", tags[:, 3:])]:
            image = nib.load(folder / f"{case_id}-{name}.nii.gz")
            mask = nib.load(folder / f"{case_id}-{name}-tumor.nii.gz")
            data, labels = np.asarray(image.dataobj), np.asarray(mask.dataobj)
            metadata = case["flair" if key == "mri" else "us_before"]
            if list(image.shape) != metadata["shape"] or not np.array_equal(
                image.affine, metadata["affine"]
            ):
                raise ValueError("Image geometry changed")
            if image.header.get_xyzt_units()[0] != "mm" or nib.aff2axcodes(image.affine) != (
                "R",
                "A",
                "S",
            ):
                raise ValueError("Unexpected frame or unit")
            if labels.shape != data.shape or not np.isfinite(data).all():
                raise ValueError("Invalid shape or intensity")
            corners = np.array(list(itertools.product(*[(0, n - 1) for n in data.shape])))
            drift = float(
                np.max(
                    np.linalg.norm(
                        world(corners, image.affine) - world(corners, mask.affine), axis=1
                    )
                )
            )
            if drift > 0.0001:
                raise ValueError("Mask and image grids differ")
            voxels = world(points, np.linalg.inv(image.affine))
            if np.any(voxels < 0) or np.any(voxels > np.array(data.shape) - 1):
                raise ValueError("Manual point outside native grid")
            roundtrip = float(np.max(np.abs(world(voxels, image.affine) - points)))
            if roundtrip > 1e-10:
                raise ValueError("Coordinate roundtrip failed")
            window = np.percentile(data[data > 0], [1, 99]).tolist()
            initial = world(query[None], np.linalg.inv(image.affine))[0]
            if np.any(initial < 0) or np.any(initial > np.array(data.shape) - 1):
                raise ValueError("Initial candidate outside grid")
            public["modalities"][key] = {
                "shape": list(data.shape),
                "spacing_mm": list(map(float, image.header.get_zooms()[:3])),
                "affine": image.affine.tolist(),
                "initial_voxel": initial.tolist(),
                "window": window,
                "native": [
                    section(data, image.affine, query, axes, window, native=True)
                    for axes in [(0, 1), (0, 2), (1, 2)]
                ],
            }
            checks.append(
                {
                    "case": case_id,
                    "modality": key,
                    "image_sform": int(image.header["sform_code"]),
                    "mask_sform": int(mask.header["sform_code"]),
                    "mask_qform": int(mask.header["qform_code"]),
                    "mask_max_corner_drift_mm": drift,
                    "point_roundtrip_max_mm": roundtrip,
                }
            )
            if case_id == "Case2":
                public["modalities"][key]["sweep"] = [
                    section(data, image.affine, np.add(query, [0, 0, z]), (0, 1), window)
                    for z in range(-6, 7)
                ]
                public["modalities"][key]["ras"] = [
                    section(data, image.affine, query, axes, window)
                    for axes in [(0, 1), (0, 2), (1, 2)]
                ]
                colored = section(labels, mask.affine, query, (0, 1), window, mask=True)
                # Retain exact calibration and tint only nonzero mask pixels.
                rgba = np.array(
                    Image.open(io.BytesIO(base64.b64decode(colored["png"].split(",")[1])))
                )
                rgba[..., :3] = [230, 91, 159] if key == "mri" else [55, 205, 205]
                rgba[..., 3] = np.rint(rgba[..., 3] * 0.4).astype("uint8")
                colored["png"] = png(rgba)
                helpers[key] = colored
        geometry.append(public)
        references.append(
            {
                "id": case_id,
                "selected_index_zero_based": selected,
                "target_world_mm": target.tolist(),
                "delta_world_mm": (target - query).tolist(),
                "initial_error_mm": float(distances[selected]),
                "all_noop_errors_mm": distances.tolist(),
                "baseline": baseline,
            }
        )
    dump(output / "geometry.json", {"frame": "RAS", "units": "mm", "cases": geometry})
    dump(output / "helpers.json", helpers)
    dump(output / "reference.json", {"cases": references})
    shutil.copyfile(
        root / "presentation/task-explorer/respiratory/DATA-LICENSE.txt",
        output / "DATA-LICENSE.txt",
    )
    if b"Attribution-NonCommercial-ShareAlike 4.0" not in mask_license.read_bytes():
        raise ValueError("Unexpected mask license")
    shutil.copyfile(mask_license, output / "LABEL-LICENSE.txt")
    (output / "NOTICE.md").write_text("""# RESECT correspondence teaching assets

Images and paired landmarks: Xiao et al., RESECT (2017),
<https://doi.org/10.1002/mp.12268>, CC BY 4.0 (DATA-LICENSE.txt).
Data archive: <https://doi.org/10.11582/2017.00004>.
The original article instead cites 10.11582/2016.00003; both identifiers are retained.

Tumor masks: Behboodi et al., RESECT-SEG (2024),
<https://doi.org/10.1002/mp.17317>, <https://osf.io/jv8bk>,
CC BY-NC-SA 4.0 (LABEL-LICENSE.txt). Combined mask-overlay views and exports
containing them follow CC BY-NC-SA 4.0. Image/landmark-only derivatives remain CC BY 4.0.
Acquisition: MedOtter/RESECT-SEG revision e86fb37dd93f7a9c64e48952f71410af59b04b9b;
15 retained files are verified against the original sample manifest, not fetched anew.
<https://huggingface.co/datasets/MedOtter/RESECT-SEG/tree/e86fb37dd93f7a9c64e48952f71410af59b04b9b>.

Changes: compact query-centred sections, grayscale clipping at each volume's
positive-intensity 1st/99th percentiles, transparent missing coverage, mask tint,
coordinate conversion and no-op distances. Linear image interpolation; nearest
mask interpolation. Native previews fit complete sections to 160 pixels;
RAS views span 48 mm at 0.5 mm sampling. No registration was estimated.
All pixel centres carry origin/dx/dy calibration in NIfTI RAS+ millimetres.
The axial sweep moves the inspection plane, never anatomy or a predicted point.
US masks use valid qform geometry; all eight corner positions agree with the
image sform within 0.0001 mm. Source geometry is not rewritten.

geometry.json contains MRI queries and same-world US initial candidates.
helpers.json contains optional tumor masks, withheld in the base condition.
reference.json contains manual US destinations and source-characterization
errors, revealed only in the reader view. These are browser presentation
boundaries, not security or solver-isolation guarantees. The teaching queries
were selected after inspecting paired masks and tags. They are not a blinded
sample. The older independently GT-centred figures are retained separately.
This proposed three-case, single-query, voxel-output contract is not frozen.
The separate two-query world-output pilot is not an outcome of this proposal.
Public training-set exposure and a strong shared-frame no-op limit difficulty claims.
""")
    assets = [
        {
            "file": p.name,
            "sha256": sha(p),
            "bytes": p.stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
        }
        for p in sorted(output.iterdir())
    ]
    if any(a["bytes"] > 1024 * 1024 for a in assets):
        raise ValueError("Teaching asset exceeds retention limit")
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-resect-v1",
            "frame": "RAS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-NC-SA-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": {"source_files": 15, "paired_landmarks": 45, "geometry": checks},
            "assets": assets,
        },
    )
    print(
        json.dumps(
            {"output": str(output), "files": len(sources), "paired_landmarks": 45, "checks": checks}
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mask-license", type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.output, args.mask_license)
