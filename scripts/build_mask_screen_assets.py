"""Verify retained BR-011 screens and derive small author-review views into a fresh folder."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np

ORGANS = [*range(1, 15), 51, 52, 63]
FAMILIES = {
    "lumbar_L1_L5": [31, 30, 29, 28, 27],
    "left_ribs_5_10": list(range(96, 102)),
    "right_ribs_5_10": list(range(108, 114)),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n")


def world(points, affine):
    return points @ affine[:3, :3].T + affine[:3, 3]


def boundary(mask):
    interior = mask.copy()
    for axis in range(3):
        for shift in (-1, 1):
            neighbor = np.roll(mask, shift, axis)
            edge = [slice(None)] * 3
            edge[axis] = 0 if shift == 1 else -1
            neighbor[tuple(edge)] = False
            interior &= neighbor
    return np.argwhere(mask & ~interior)


def build(root, output):
    output.mkdir(parents=True, exist_ok=False)
    receipt_path = root / "docs/evidence/br011-author-screen.json"
    receipt = json.loads(receipt_path.read_text())
    taxonomy = root / "runs/br004-v1/build/data/label-list.json"
    author_script = root / "probes/revisions/br011/authoring/screen_and_export.py"
    if (
        sha(taxonomy) != receipt["taxonomy_sha256"]
        or sha(author_script) != receipt["script_sha256"]
    ):
        raise ValueError("Retained method or taxonomy drift")
    names = {int(k): v for k, v in json.loads(taxonomy.read_text()).items()}
    sources = {str(p.relative_to(root)): sha(p) for p in (receipt_path, taxonomy, author_script)}
    features, ordering, geometry, reference = [], [], {}, {}
    for source in receipt["sources"]:
        path = root / source["path"]
        if sha(path) != source["sha256"]:
            raise ValueError("Retained source changed")
        sources[source["path"]] = source["sha256"]
        with np.load(path, allow_pickle=False) as z:
            labels, affine = z["original"], z["affine"]
        case = source["case_id"]
        coords = {n: np.argwhere(labels == n) for n in set(ORGANS).union(*FAMILIES.values())}
        for family, ids in FAMILIES.items():
            present = [n for n in ids if coords[n].size]
            ordered = sorted(present, key=lambda n: -world(coords[n].mean(0), affine)[2])
            ordering.append(
                {
                    "case_id": case,
                    "family": family,
                    "instances": len(present),
                    "source_order": [names[n] for n in present],
                    "centroid_order": [names[n] for n in ordered],
                    "correct_assignments": sum(
                        a == b for a, b in zip(present, ordered, strict=True)
                    ),
                    "all_correct": bool(present) and present == ordered,
                }
            )
        for n in ORGANS:
            p = coords[n]
            if not len(p):
                continue
            extents = (np.ptp(p, axis=0) + 1) * np.linalg.norm(affine[:3, :3], axis=0)
            volume = len(p) * abs(np.linalg.det(affine[:3, :3]))
            vector = np.r_[
                p.mean(0) / (np.asarray(labels.shape) - 1), np.log(volume), np.log(extents)
            ]
            features.append({"case": case, "label": n, "features": vector})
        scenes = []
        if case in (32, 74):
            # Fixed arbitrary order prevents the display IDs from revealing anatomical order.
            scenes.append((f"ribs-{case}", [99, 96, 101, 98, 100, 97], 950))
        if case == 32:
            scenes.append(("organs-32", ORGANS, 700))
        for scene, ids, budget in scenes:
            objects, answers = [], []
            for i, n in enumerate(ids):
                p = coords[n]
                surface = boundary(labels == n)
                selected = surface[
                    np.linspace(0, len(surface) - 1, min(len(surface), budget), dtype=int)
                ]
                object_id = f"{scene}-o{i + 1}"
                objects.append(
                    {
                        "id": object_id,
                        "points_lps_mm": np.round(world(selected, affine), 5).tolist(),
                        "centroid_lps_mm": world(p.mean(0), affine).tolist(),
                        "source_surface_points": len(surface),
                        "source_voxels": len(p),
                    }
                )
                answers.append({"id": object_id, "source": names[n]})
            geometry[scene] = {"case_id": case, "affine_lps": affine.tolist(), "objects": objects}
            reference[scene] = answers
    if ordering != receipt["coordinate_sort"]["rows"]:
        raise ValueError("Coordinate-order screen differs from retained receipt")
    predicted_rows = []
    example = None
    for source in receipt["sources"]:
        case = source["case_id"]
        train = [row for row in features if row["case"] != case]
        test = [row for row in features if row["case"] == case]
        classes = sorted({row["label"] for row in train})
        scale = np.maximum(np.std([row["features"] for row in train], axis=0), 1e-6)
        templates = np.array(
            [
                np.median([row["features"] for row in train if row["label"] == n], axis=0)
                for n in classes
            ]
        )
        predictions = []
        for row in test:
            distances = np.sum(((templates - row["features"]) / scale) ** 2, axis=1)
            label = classes[int(np.argmin(distances))]
            if case == 32 and row["label"] == 1:
                example = {
                    "object_id": "organs-32-o1",
                    "features": row["features"].tolist(),
                    "feature_units": ["scan fraction"] * 3 + ["ln(mm^3)"] + ["ln(mm)"] * 3,
                    "nearest_templates": [
                        {"label": names[classes[i]], "squared_distance": float(distances[i])}
                        for i in np.argsort(distances)[:3]
                    ],
                    "training_cases": sorted({r["case"] for r in train}),
                }

            predictions.append(
                {
                    "source_label": names[row["label"]],
                    "predicted": names[label],
                    "correct": label == row["label"],
                }
            )
        predicted_rows.append(
            {
                "case_id": case,
                "correct": sum(p["correct"] for p in predictions),
                "total": len(predictions),
                "all_correct": all(p["correct"] for p in predictions),
                "predictions": predictions,
            }
        )
    if predicted_rows != receipt["organ_baseline"]["rows"]:
        raise ValueError("Organ-template screen differs from retained receipt")
    audit_path = root / "docs/evidence/br010-mask-reasoning-audit.json"
    audit = json.loads(audit_path.read_text())
    sources[str(audit_path.relative_to(root))] = sha(audit_path)
    for trial in audit["trials"]:
        path = root / trial["trajectory_path"]
        if sha(path) != trial["trajectory_sha256"]:
            raise ValueError("Retained trajectory changed")
        sources[trial["trajectory_path"]] = trial["trajectory_sha256"]
    dump(output / "geometry.json", {"scenes": geometry, "frame": "LPS", "units": "mm"})
    dump(
        output / "reference.json",
        {
            "visibility": "author study references; reader reveal only, never solver inputs",
            "scenes": reference,
            "feature_example": example,
            "coordinate_sort": receipt["coordinate_sort"],
            "organ_baseline": receipt["organ_baseline"],
            "retrospective": {
                "trajectories": len(audit["trials"]),
                "receipt": str(audit_path.relative_to(root)),
            },
        },
    )
    public = root / receipt["prototype"]["public_path"]
    for name in ("DATA-LICENSE.txt", "LABEL-LICENSE.txt"):
        expected = next(row for row in receipt["prototype"]["files"] if row["path"] == name)
        if sha(public / name) != expected["sha256"]:
            raise ValueError("License drift")
        shutil.copyfile(public / name, output / name)
    (output / "NOTICE.md").write_text(
        "# Mask-reasoning author screen\n\n"
        "TotalSegmentator small v2.0.1, Wasserthal / University Hospital Basel. "
        "https://zenodo.org/records/10047263 . Data CC BY 4.0; labels Apache 2.0. "
        "Exact license bytes are retained. No source author endorses this view.\n\n"
        "Source arrays are the unmodified retained original masks, not BR-004's planted defects. "
        "This builder independently recomputes all 24 family-order rows and all 131 organ "
        "predictions using the retained method, verifying every row against the BR-011 receipt. "
        "All eight arrays, taxonomy, author script and seven BR-010 trajectories are hash-checked. "
        "Historical authoring code is read as data and is never imported or executed.\n\n"
        "The three views show case-32 left ribs, case-74 left ribs and case-32 organs. "
        "Boundary voxel centres are deterministically sampled up to 950 points/rib and 700/organ. "
        "Centroids use all occupancy voxels, not displayed samples. Source LPS millimetres and "
        "shared scale are retained within each scene. The proper display rotation is [L,S,-P]. "
        "Separate patients are independently fitted and are not registered. Points have no "
        "mesh faces; source occupancy remains authoritative. No CT is embedded.\n\n"
        "reference.json holds author-only source labels and historical baseline predictions. "
        "Reader reveal is pedagogical; this bundle is not a blind solver packet. The ordering "
        "screen knows family membership and the label multiset. The organ baseline trains "
        "on seven other patients; prototype solvers do not receive those labeled examples. "
        "Source labels are not independent clinical or mask-only adjudication. The coverage "
        "exception is not a qualified hard task. I1/I3 remain proposals; no new model trial.\n\n"
        "Rebuild using `uv run --no-sync python scripts/build_mask_screen_assets.py --root . "
        "--output NEW_DIRECTORY`. Existing NumPy is required. Never overwrite an accepted pack.\n"
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
            "id": "retained-mask-screen-v1",
            "frame": "LPS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "Apache-2.0",
            "reference_policy": "reader-reference-reveal",
            "assets": assets,
            "sources": sources,
            "checks": {
                "arrays": 8,
                "trajectories": 7,
                "family_rows_exact": len(ordering),
                "organ_predictions_exact": sum(row["total"] for row in predicted_rows),
            },
        },
    )
    print(
        json.dumps(
            {
                "geometry_bytes": (output / "geometry.json").stat().st_size,
                "families": [sum(row["all_correct"] for row in ordering), len(ordering)],
                "organs": [
                    sum(row["correct"] for row in predicted_rows),
                    sum(row["total"] for row in predicted_rows),
                ],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output)
