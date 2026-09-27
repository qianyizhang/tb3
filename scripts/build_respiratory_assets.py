"""Verify retained respiratory task bytes and derive small, coordinate-calibrated views."""

import argparse
import base64
import hashlib
import io
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from scipy.interpolate import RegularGridInterpolator


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, data):
    path.write_text(json.dumps(data, separators=(",", ":")) + "\n")


def world(points, affine):
    return np.einsum("ij,nj->ni", affine[:3, :3], points) + affine[:3, 3]


def load_volume(path):
    with np.load(path, allow_pickle=False) as z:
        if set(z.files) != {"hu", "voxel_to_world"}:
            raise ValueError("Unexpected public NPZ fields")
        return z["hu"], z["voxel_to_world"]


def plane(hu, origin, dx, dy, name):
    pixels = np.rint(255 * np.clip((hu.astype(float) + 1000) / 1200, 0, 1)).astype("uint8")
    stream = io.BytesIO()
    Image.fromarray(pixels).save(stream, format="PNG")
    height, width = hu.shape
    return {
        "name": name,
        "width": width,
        "height": height,
        "origin_world_mm": list(origin),
        "dx_world_mm": list(dx),
        "dy_world_mm": list(dy),
        "gray_u8": base64.b64encode(pixels.tobytes()).decode(),
        "png": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
    }


def reslice(data, affine, center, patch=False):
    inverse = np.linalg.inv(affine)
    interp = RegularGridInterpolator(
        tuple(np.arange(n) for n in data.shape), data, bounds_error=True
    )
    slices = []
    for a, b, name in [(0, 1, "XY"), (0, 2, "XZ"), (1, 2, "YZ")]:
        if patch:
            width = height = 65
            dx, dy = np.eye(3)[a], np.eye(3)[b]
            origin = center - 32 * (dx + dy)
        else:
            width, height = data.shape[a], data.shape[b]
            dx, dy = affine[:3, a], affine[:3, b]
            voxel = world(np.asarray(center)[None], inverse)[0]
            voxel[a] = voxel[b] = 0
            origin = world(voxel[None], affine)[0]
        vv, uu = np.indices((height, width))
        points = origin + uu[..., None] * dx + vv[..., None] * dy
        coords = world(points.reshape(-1, 3), inverse)
        # Floating arithmetic at a nominal volume edge must not become extrapolation.
        if np.any(coords < -1e-8) or np.any(coords > np.array(data.shape) - 1 + 1e-8):
            raise ValueError("Teaching section exceeds source coverage")
        coords = np.clip(coords, 0, np.array(data.shape) - 1)
        hu = interp(coords).reshape(height, width)
        slices.append(plane(hu, origin, dx, dy, name))
    return slices


def build(root, output):
    output.mkdir(parents=True, exist_ok=False)
    sources, tasks, frozen_files = {}, {}, 0
    for name in ["br021-freeze", "br024-patient3-freeze", "br028-freeze"]:
        file = root / f"docs/evidence/{name}.json"
        record = read(file)
        sources[str(file.relative_to(root))] = sha(file)
        for task in record.get("tasks", [record.get("task")]):
            tasks[task["task"]] = root / task["task_path"]
            for member, expected in task["files"].items():
                path = root / task["task_path"] / member
                if sha(path) != expected:
                    raise ValueError(f"Frozen task changed: {path}")
                sources[str(path.relative_to(root))] = expected
                frozen_files += 1
    old, new = tasks["deform-harder-patient3"], tasks["deform-patient3-source3d"]
    changed = [
        str(p.relative_to(old))
        for p in old.rglob("*")
        if p.is_file() and sha(p) != sha(new / p.relative_to(old))
    ]
    added = [
        str(p.relative_to(new))
        for p in new.rglob("*")
        if p.is_file() and not (old / p.relative_to(new)).exists()
    ]
    if set(changed) != {"instruction.md", "task.toml"} or added != [
        "environment/data/reference_volume.npz"
    ]:
        raise ValueError("Source-depth contrast differs from frozen design")
    receipt_path = root / "datasets/receipts/learn2reg-files.json"
    receipt = read(receipt_path)
    for row in receipt["files"]:
        if sha(root / row["path"]) != row["sha256"]:
            raise ValueError("Retained source member changed")
        sources[row["path"]] = row["sha256"]
    metadata = root / "runs/br021-deformable/source/zenodo-training-record.json"
    if read(metadata)["metadata"]["license"]["id"] != "cc-by-4.0":
        raise ValueError("Unexpected retained source terms")
    sources[str(metadata.relative_to(root))] = sha(metadata)
    results_path = root / "docs/evidence/br028-results.json"
    results = read(results_path)
    sources[str(results_path.relative_to(root))] = sha(results_path)
    rows = [
        results["prior_2d_attempt"],
        next(r for r in results["prospective_rows"] if r["phase"] == "sol-xhigh"),
    ]
    truth = read(new / "tests/truth.json")
    answers = []
    for row in rows:
        for key in ["answer", "result"]:
            path = root / row[key + "_path"]
            if sha(path) != row[key + "_sha256"]:
                raise ValueError("Retained answer/result changed")
            sources[str(path.relative_to(root))] = sha(path)
        answer = read(root / row["answer_path"])
        if answer["query_ids"] != truth["query_ids"]:
            raise ValueError("Answer query order changed")
        error = np.linalg.norm(
            np.array(answer["points_world_mm"]) - truth["points_world_mm"], axis=1
        )
        if not np.allclose(error, row["grade"]["per_point_mm"], atol=1e-10, rtol=0):
            raise ValueError("Point error differs")
        if abs(float(np.sqrt(np.mean(error**2))) - row["grade"]["rms_mm"]) > 1e-10:
            raise ValueError("Aggregate error differs")
        answers.append(
            {
                "condition": "slice" if row is rows[0] else "depth",
                "answer": answer,
                "grade": row["grade"],
            }
        )
    public = new / "environment/data"
    source, affine = load_volume(public / "reference_volume.npz")
    target, target_affine = load_volume(public / "volume.npz")
    original = nib.load(
        root / "runs/br021-deformable/source/LungCT/imagesTr/LungCT_0003_0000.nii.gz"
    )
    if not np.array_equal(
        source, np.asarray(original.dataobj).astype(np.float32)
    ) or not np.array_equal(affine, original.affine):
        raise ValueError("Source NPZ differs from its NIfTI")
    views, max_difference, sampling_checks = {}, 0.0, []
    for key, task in [("patient1", tasks["deform-2d"]), ("patient3", new)]:
        folder = task / "environment/data"
        view, geometry, queries = (
            np.load(folder / "view.npy", allow_pickle=False),
            read(folder / "view.json"),
            read(folder / "queries.json"),
        )
        pose = np.array(geometry["slice_to_world"])
        spacing = np.array(geometry["spacing_xy_mm"])
        dx, dy = pose[:3, 0] * spacing[0], pose[:3, 1] * spacing[1]
        query = np.array(queries["pixels_uv"])
        positions = pose[:3, 3] + query[:, :1] * dx + query[:, 1:] * dy
        views[key] = {
            "plane": plane(view, pose[:3, 3], dx, dy, "supplied oblique slice"),
            "pixels_uv": query.tolist(),
            "source_world_mm": positions.tolist(),
            "query_ids": queries["query_ids"],
            "slice_to_world": pose.tolist(),
            "spacing_xy_mm": spacing.tolist(),
        }
        case_id = 1 if key == "patient1" else 3
        pair = []
        source_folder = root / "runs/br021-deformable/source"
        for phase in (0, 1):
            image_path = source_folder / f"LungCT/imagesTr/LungCT_{case_id:04d}_{phase:04d}.nii.gz"
            image = nib.load(image_path)
            expected_volume = np.asarray(image.dataobj).astype(np.float32)
            public_folder = tasks["deform-3d"] / "environment/data" if case_id == 1 else public
            packed, matrix = load_volume(
                public_folder / ("reference_volume.npz" if phase == 0 else "volume.npz")
            )
            if not np.array_equal(packed, expected_volume) or not np.array_equal(
                matrix, image.affine
            ):
                raise ValueError("Frozen public volume differs from official source")
            csv = source_folder / f"LungCT/landmarksTr/LungCT_{case_id:04d}_{phase:04d}.csv"
            official = (
                source_folder
                / "l2r-reference/evaluation/L2RTest/ground-truth/landmarksTr"
                / csv.name
            )
            if csv.read_bytes() != official.read_bytes():
                raise ValueError("Archive and official manual references differ")
            sources[str(official.relative_to(root))] = sha(official)
            pair.append((packed, matrix, world(np.loadtxt(csv, delimiter=","), matrix)))
        if np.array_equal(pair[0][0], pair[1][0]):
            raise ValueError("Duplicate phase images cannot establish respiratory motion")
        private = read(task / "tests/truth.json")
        reference_points = np.array(private["points_world_mm"])
        distances = np.linalg.norm(reference_points[:, None] - pair[1][2][None], axis=2)
        indices = np.argmin(distances, axis=1)
        if np.max(distances[np.arange(8), indices]) > 1e-8:
            raise ValueError("Frozen destinations not found in manual reference pairs")
        offsets = np.linalg.norm(positions - pair[0][2][indices], axis=1)
        if np.max(offsets) > 0.35:
            raise ValueError("Projected public query exceeds the declared plane approximation")
        if case_id == 1:
            exact = read(tasks["deform-3d"] / "environment/data/queries.json")
            if not np.allclose(exact["reference_world_mm"], pair[0][2][indices], atol=1e-8, rtol=0):
                raise ValueError("Paired-3D source queries do not match the manual source points")
        vv, uu = np.indices(view.shape)
        points = pose[:3, 3] + uu[..., None] * dx + vv[..., None] * dy
        sampler = RegularGridInterpolator(tuple(np.arange(n) for n in pair[0][0].shape), pair[0][0])
        reproduced = sampler(world(points.reshape(-1, 3), np.linalg.inv(pair[0][1]))).reshape(
            view.shape
        )
        difference = float(np.max(np.abs(view - reproduced)))
        if not np.isfinite(difference) or difference > 0.001:
            raise ValueError("Public slice not reproduced from source volume")
        sampling_checks.append(
            {
                "case": case_id,
                "pixels": int(view.size),
                "max_error_hu": difference,
                "manual_pair_indices": indices.tolist(),
                "max_public_source_offset_mm": float(offsets.max()),
            }
        )
        if case_id == 3:
            max_difference = difference
    selected = 5
    source_point = np.array(views["patient3"]["source_world_mm"][selected])
    returned = np.array(answers[1]["answer"]["points_world_mm"][selected])
    geometry = {
        "frame": "dataset-world",
        "units": "mm",
        "window_hu": [-1000, 200],
        "focus_query": "q06",
        "focus_selection": "Posthoc reader example, not a predeclared query or new attempt",
        "volume_shape": list(source.shape),
        "source_affine": affine.tolist(),
        "target_affine": target_affine.tolist(),
        "views": views,
        "source_sections": reslice(source, affine, source_point),
        "target_sections": reslice(target, target_affine, source_point),
        "target_returned_patch": reslice(target, target_affine, returned, patch=True),
    }
    dump(output / "geometry.json", geometry)
    dump(
        output / "output.json",
        {
            "label": "Retained BR-028 Sol/xhigh output; not a new model prediction",
            "answer": answers[1]["answer"],
        },
    )
    adjudication_path = root / "docs/evidence/br028-adjudication.json"
    sources[str(adjudication_path.relative_to(root))] = sha(adjudication_path)
    dump(
        output / "reference.json",
        {
            "visibility": "private evaluator coordinates; reader reveal only",
            "truth": truth,
            "conditions": answers,
            "adjudication": read(adjudication_path),
        },
    )
    license_path = root / "presentation/task-explorer/mask-screen/DATA-LICENSE.txt"
    shutil.copyfile(license_path, output / "DATA-LICENSE.txt")
    (output / "NOTICE.md").write_text(
        "# Respiratory correspondence teaching views\n\n"
        "Learn2Reg LungCT 1.11. Hering, Alessa; Murphy, Keelin; van Ginneken, Bram (2020), "
        "Radboud University Medical Center. Source attribution: https://doi.org/10.5281/zenodo.3835682 . "
        "CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Exact license text retained. "
        "No source creator endorses this adaptation.\n\n"
        "The original release was cropped, resampled and affine prealigned. Coordinates are supplied "
        "dataset-world millimetres, NOT asserted native LPS or RAS. Each plane stores the world position "
        "of pixel centre (0,0), column/row displacement vectors, width and height. Grayscale bytes are "
        "round(255*clip((HU+1000)/1200,0,1)); PNGs encode exactly those bytes. Orthogonal display sections "
        "are trilinearly interpolated from existing public arrays; axes are dataset X/Y/Z, not anatomical "
        "labels. No dense field, segmentation or continuous volumetric reconstruction is supplied.\n\n"
        "Public oblique patient1/patient3 slices are retained. Three source and three target display "
        "sections pass through public patient3 q06. Target closeups span 64 mm through the retained "
        "returned q06 coordinate, not a reference-centred crop. q06 was chosen after scoring for reader "
        "teaching. It is not a new search result or blinded case selection. reference.json separately "
        "holds private manual answers, scores and the later user judgment. The initial view hides these; "
        "this bundle is not a solver packet.\n\n"
        "All four task freezes and retained source members are hash-checked. BR-024/028 differ only in "
        "prompt/task name and one added full-source NPZ; old inputs, query geometry, targets, answers and "
        "grader stay identical. The source NPZ matches NIfTI exactly and independently reproduces all "
        "22869 public view pixels within 0.000031 HU. Both retained answers are independently remeasured. "
        "Historical authoring modules are never imported or executed, and no model trial is launched.\n\n"
        "Sparse RMS <=3 mm AND maximum <=5 mm are engineering gates, not observer uncertainty or "
        "clinical equivalence. BR-028 still fails its numerical gate; the later user's visual acceptance "
        "is separately retained. One fresh attempt per condition cannot isolate a causal depth effect. "
        "Source/public annotations may be retrievable externally, so image isolation is not a guarantee "
        "against training contamination or answer lookup.\n\n"
        "Rebuild with the existing NumPy/SciPy/NiBabel/Pillow environment: "
        "`python scripts/build_respiratory_assets.py --root . --output NEW_DIRECTORY`.\n"
    )
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-respiratory-v1",
            "frame": "dataset-world",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": {
                "frozen_task_files": frozen_files,
                "retained_source_members": len(receipt["files"]),
                "source_view_pixels": int(view.size),
                "source_view_max_error_hu": max_difference,
                "sampling_checks": sampling_checks,
                "changed_existing_files": changed,
                "added_files": added,
            },
            "assets": [
                {
                    "file": p.name,
                    "sha256": sha(p),
                    "bytes": p.stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if p.name == "reference.json"
                    else "illustration",
                }
                for p in sorted(output.iterdir())
            ],
        },
    )
    print(
        json.dumps(
            {
                "frozen_files": frozen_files,
                "source_members": len(receipt["files"]),
                "geometry_bytes": (output / "geometry.json").stat().st_size,
                "sampling_error_hu": max_difference,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output)
