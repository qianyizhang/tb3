"""Derive a bounded point display from the retained BR-011 I2 packet into a fresh folder."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n")


def build(root, output):
    output.mkdir(parents=True, exist_ok=False)
    receipt_path = root / "docs/evidence/br011-author-screen.json"
    receipt = json.loads(receipt_path.read_text())
    prototype = receipt["prototype"]
    public = root / prototype["public_path"]
    sources = {str(receipt_path.relative_to(root)): sha(receipt_path)}
    for record in prototype["files"]:
        path = public / record["path"]
        if sha(path) != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise ValueError(f"Prototype source changed: {path}")
        sources[str(path.relative_to(root))] = record["sha256"]
    key_path = root / prototype["private_key_path"]
    key = json.loads(key_path.read_text())
    sources[str(key_path.relative_to(root))] = sha(key_path)
    scene = json.loads((public / "scene.json").read_text())
    vocabulary = json.loads((public / "vocabulary.json").read_text())
    with np.load(public / "objects.npz", allow_pickle=False) as z:
        volume, affine = z["objects"], z["affine_lps"]
    source_record = next(s for s in receipt["sources"] if s["case_id"] == 32)
    source_path = root / source_record["path"]
    taxonomy_path = root / "runs/br004-v1/build/data/label-list.json"
    if (
        sha(source_path) != source_record["sha256"]
        or sha(taxonomy_path) != receipt["taxonomy_sha256"]
    ):
        raise ValueError("Retained source array or taxonomy changed")
    sources[str(source_path.relative_to(root))] = sha(source_path)
    sources[str(taxonomy_path.relative_to(root))] = sha(taxonomy_path)
    with np.load(source_path, allow_pickle=False) as z:
        original, source_affine = z["original"], z["affine"]
    if not np.array_equal(affine, source_affine):
        raise ValueError("Prototype/source affines differ")
    taxonomy = {name: int(value) for value, name in json.loads(taxonomy_path.read_text()).items()}
    inverse = np.linalg.inv(affine)
    names = {row["object_id"]: row["label"] for row in key["assignments"]}
    if set(names) != {row["object_id"] for row in scene["objects"]}:
        raise ValueError("Key and public object IDs differ")
    objects = []
    for row in scene["objects"]:
        if not np.array_equal(
            volume == row["mask_value"], original == taxonomy[names[row["object_id"]]]
        ):
            raise ValueError("Private identity key disagrees with retained original occupancy")
        path = public / row["surface_points"]
        lines = path.read_text().splitlines()
        end = lines.index("end_header")
        points = np.asarray([[float(v) for v in line.split()] for line in lines[end + 1 :]])
        count = int(
            next(line.split()[-1] for line in lines[:end] if line.startswith("element vertex"))
        )
        if points.shape != (count, 3) or not np.isfinite(points).all():
            raise ValueError("Malformed retained PLY")
        floating = sum(points[:, j, None] * inverse[:3, j] for j in range(3)) + inverse[:3, 3]
        indices = np.rint(floating).astype(int)
        if not (
            np.allclose(floating, indices, atol=1e-4)
            and np.all((indices >= 0) & (indices < volume.shape))
            and np.all(volume[tuple(indices.T)] == row["mask_value"])
        ):
            raise ValueError("PLY points disagree with public occupancy / affine")
        # Stratified row sampling preserves the source coordinates, not surface connectivity.
        selected = np.unique(np.linspace(0, count - 1, min(count, 1600), dtype=int))
        vertices = points[selected].tolist()
        objects.append(
            {
                "object_id": row["object_id"],
                "mask_value": row["mask_value"],
                "points_lps_mm": vertices,
                "source_points": count,
                "display_points": len(selected),
                "source_ply_sha256": sha(path),
                "centroid_lps_mm": points.mean(axis=0).tolist(),
                "occupancy_voxels": int(np.count_nonzero(volume == row["mask_value"])),
            }
        )
    if len(objects) != 17 or len(vocabulary) != 117:
        raise ValueError("Unexpected prototype inventory")
    dump(
        output / "geometry.json",
        {
            "case_id": 32,
            "coordinates": "LPS millimetres",
            "voxel_spacing_mm": [3, 3, 3],
            "objects": objects,
        },
    )
    dump(
        output / "reference.json",
        {
            "visibility": "private author key; reader reveal only",
            "assignments": key["assignments"],
            "key_sha256": sha(key_path),
            "key_boundary": "This review pins the currently retained private key and checks all 17 assignments against the hash-verified original source occupancy and taxonomy. Source agreement is not clinical adjudication or mask-only identifiability.",
        },
    )
    for name in ("vocabulary.json", "DATA-LICENSE.txt", "LABEL-LICENSE.txt"):
        shutil.copyfile(public / name, output / name)
    (output / "NOTICE.md").write_text(
        "# BR-011 I2 anonymous point display\n\n"
        "TotalSegmentator small v2.0.1, Wasserthal and University Hospital Basel. "
        "https://zenodo.org/records/10047263 . Data CC BY 4.0; label definitions Apache 2.0. "
        "Full terms are retained here. No source author endorses this view.\n\n"
        "The 17 objects come from retained prototype case 32, not the s1233 assembly used by "
        "other stories. All public files match the author-screen receipt. Each original PLY "
        "point was checked against the public 3 mm occupancy array and affine. The display "
        "keeps up to 1,600 evenly indexed source points per object; no point is relocated. "
        "This discards detail. Points have no faces and do not establish topology. The local "
        "occupancy volume remains authoritative; no CT or full occupancy array is embedded.\n\n"
        "All objects share one LPS-to-display rotation, centre and uniform scale. No object "
        "is individually rotated, reflected, centred or resized. The selected object is teal; "
        "all others are neutral. IDs, colours and order are the prototype's arbitrary identifiers.\n\n"
        "reference.json is the currently retained private author identity key, pinned by this "
        "review. All 17 assignments were checked against the separately hash-verified original "
        "source occupancy and taxonomy; the source affine is unchanged. The labels are exposed "
        "only after an explicit reader reveal and must not be given to a blind solver. "
        "Source-key agreement does not establish clinical correctness or mask-only identifiability. "
        "The packet is an authoring calibration prototype, not an admitted model experiment.\n\n"
        "Rebuild to a fresh output using `uv run --no-sync python scripts/build_prototype_identity_assets.py "
        "--root . --output NEW_DIRECTORY`. The script needs NumPy and does not import historical "
        "authoring modules, modify their outputs, download data or launch a model.\n"
    )
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
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-prototype-identity-v1",
            "frame": "LPS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "Apache-2.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "assets": assets,
            "checks": {
                "public_files_verified": len(prototype["files"]),
                "objects": len(objects),
                "native_points_checked": sum(o["source_points"] for o in objects),
                "display_points": sum(o["display_points"] for o in objects),
                "source_identity_occupancy_matches": 17,
                "source_affine_equal": True,
            },
        },
    )
    print(
        json.dumps({"output": str(output), "objects": len(objects), "vocabulary": len(vocabulary)})
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output)
