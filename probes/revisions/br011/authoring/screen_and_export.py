"""Local BR-011 author screen and unlabeled-volume example; no model calls.

Run from the workshop root with its existing NumPy environment. Source inputs
are retained BR-004 arrays. This produces a source-label calibration example,
not a clinically adjudicated task or a new qualified benchmark.
"""

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

import numpy as np


CASES = [19, 28, 32, 46, 61, 74, 83, 95]
ORGANS = list(range(1, 15)) + [51, 52, 63]
FAMILIES = {
    "lumbar_L1_L5": [31, 30, 29, 28, 27],
    "left_ribs_5_10": list(range(96, 102)),
    "right_ribs_5_10": list(range(108, 114)),
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def surface(mask):
    interior = np.zeros_like(mask)
    interior[1:-1, 1:-1, 1:-1] = (
        mask[1:-1, 1:-1, 1:-1]
        & mask[:-2, 1:-1, 1:-1] & mask[2:, 1:-1, 1:-1]
        & mask[1:-1, :-2, 1:-1] & mask[1:-1, 2:, 1:-1]
        & mask[1:-1, 1:-1, :-2] & mask[1:-1, 1:-1, 2:]
    )
    return np.argwhere(mask & ~interior)


def to_world(points, affine):
    # Small explicit affine avoids platform BLAS warnings for integer arrays.
    result = sum(points[:, axis, None] * affine[:3, axis] for axis in range(3)) + affine[:3, 3]
    assert np.isfinite(result).all()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("runs/br011-mask-identification"))
    parser.add_argument("--evidence", type=Path, default=Path("docs/evidence/br011-author-screen.json"))
    args = parser.parse_args()
    start = time.monotonic()
    taxonomy_path = Path("runs/br004-v1/build/data/label-list.json")
    names = {int(k): v for k, v in json.loads(taxonomy_path.read_text()).items()}
    sources, family_rows, features = [], [], []
    chosen = None
    for case in CASES:
        path = Path(f"runs/br004-v1/build/case-{case}-private.npz")
        with np.load(path) as data:
            labels, affine = data["original"], data["affine"]
            if case == 32:
                chosen = labels.copy(), affine.copy()
            sources.append({"case_id": case, "path": str(path), "sha256": digest(path)})
            coords = {n: np.argwhere(labels == n) for n in set(ORGANS).union(*FAMILIES.values())}
            for family, order in FAMILIES.items():
                present = [n for n in order if len(coords[n])]
                # Uses the proposed names' multiset and group; no clean shape reference.
                predicted = sorted(present, key=lambda n: -(affine @ np.r_[coords[n].mean(0), 1])[2])
                family_rows.append({
                    "case_id": case, "family": family, "instances": len(present),
                    "source_order": [names[n] for n in present],
                    "centroid_order": [names[n] for n in predicted],
                    "correct_assignments": sum(a == b for a, b in zip(present, predicted)),
                    "all_correct": bool(present) and predicted == present,
                })
            for n in ORGANS:
                p = coords[n]
                if not len(p):
                    continue
                # Position normalized by scan extent; independent of origin and patient ID.
                center = p.mean(0) / (np.array(labels.shape) - 1)
                size_mm = (p.max(0) - p.min(0) + 1) * np.linalg.norm(affine[:3, :3], axis=0)
                volume = len(p) * abs(np.linalg.det(affine[:3, :3]))
                features.append({"case": case, "label": n,
                                 "features": np.r_[center, np.log(volume), np.log(size_mm)].tolist()})

    baseline_rows = []
    for case in CASES:
        train = [r for r in features if r["case"] != case]
        test = [r for r in features if r["case"] == case]
        x = np.array([r["features"] for r in train])
        scale = np.maximum(x.std(0), 1e-6)
        vocab = sorted({r["label"] for r in train})
        templates = np.array([np.median([r["features"] for r in train if r["label"] == n], axis=0) for n in vocab])
        predictions = []
        for r in test:
            error = (((np.array(r["features"]) - templates) / scale) ** 2).sum(1)
            pred = vocab[int(error.argmin())]
            predictions.append({"source_label": names[r["label"]], "predicted": names[pred], "correct": pred == r["label"]})
        baseline_rows.append({"case_id": case, "correct": sum(p["correct"] for p in predictions),
                              "total": len(predictions), "all_correct": all(p["correct"] for p in predictions),
                              "predictions": predictions})

    labels, affine = chosen
    rng = np.random.default_rng(2026091511)
    order = rng.permutation(ORGANS).tolist()
    codes = rng.choice(np.arange(100, 1000), size=len(order), replace=False)
    public = args.output / "public"
    private = args.output / "author"
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    volume = np.zeros_like(labels)
    objects, answers, preview = [], [], []
    for value, (n, code) in enumerate(zip(order, codes), start=1):
        mask = labels == n
        if not mask.any():
            continue
        object_id = f"o{code}"
        volume[mask] = value
        points = surface(mask)
        world = to_world(points, affine)
        ply = public / f"{object_id}.ply"
        with ply.open("w") as f:
            f.write(f"ply\nformat ascii 1.0\nelement vertex {len(world)}\nproperty float x\nproperty float y\nproperty float z\nend_header\n")
            np.savetxt(f, world, fmt="%.5f")
        objects.append({"object_id": object_id, "mask_value": value, "surface_points": ply.name})
        answers.append({"object_id": object_id, "label": names[n]})
        sample = points[rng.choice(len(points), min(1200, len(points)), replace=False)]
        sample_world = to_world(sample, affine)
        preview.append({"id": object_id, "label": names[n], "points": np.round(sample_world, 2).tolist(),
                        "volume_ml": round(float(mask.sum() * 27 / 1000), 2)})
    np.savez_compressed(public / "objects.npz", objects=volume, affine_lps=affine)
    write_json(public / "scene.json", {"array_axes": "x,y,z", "coordinates": "LPS millimetres", "objects": objects})
    write_json(public / "vocabulary.json", sorted(names.values()))
    write_json(private / "expected.json", {"assignments": answers})
    write_json(private / "preview-data.json", {"objects": preview})
    source_env = Path("runs/br004-v1/task-snapshot/dicom-anatomy-audit/environment")
    for name in ["DATA-LICENSE.txt", "LABEL-LICENSE.txt"]:
        shutil.copyfile(source_env / name, public / name)
    (public / "SOURCE_NOTICE.md").write_text(
        "# Source\n\nDerived from TotalSegmentator small v2.0.1, Wasserthal / University Hospital Basel.\n"
        "Data: CC BY 4.0; label definitions: Apache 2.0.\n"
        "https://zenodo.org/records/10047263\n\n"
        "Locally derived 3 mm masks with anonymous object IDs; no CT intensities supplied.\n"
        "This example has not received independent clinical or mask-only identifiability review.\n")
    (public / "instruction.md").write_text(
        "# Identify the 3-D objects\n\nAssign each object in scene.json an anatomical label from vocabulary.json.\n"
        "Objects retain their physical positions, scale and patient orientation.\n"
        "Positive x is left, y is posterior and z is superior. IDs carry no anatomical meaning.\n"
        "Write assignments.json as {\"assignments\":[{\"object_id\":\"o123\",\"label\":\"label-name\"}]}.\n"
        "Include each supplied object exactly once.\n\n"
        "objects.npz contains an integer array named objects and affine_lps, mapping\n"
        "[x,y,z,1] array coordinates to LPS millimetres. All other values are background.\n"
        "The PLY files contain boundary voxel centres, not watertight meshes.\n"
        "The volume is authoritative for occupancy/connectivity.\n\n"
        "This is an authoring calibration example. The source-key grade alone does not establish task fairness.\n")
    # Exact round-trip and no-CT/clean-label exposure checks, separate from semantic validity.
    with np.load(public / "objects.npz") as data:
        assert set(data.files) == {"objects", "affine_lps"}
        for obj, answer in zip(objects, answers):
            source_id = next(n for n, name in names.items() if name == answer["label"])
            assert np.array_equal(data["objects"] == obj["mask_value"], labels == source_id)
            decoded_points = np.loadtxt(public / obj["surface_points"], skiprows=7)
            assert np.allclose(decoded_points, to_world(surface(labels == source_id), affine), atol=1e-5, rtol=0)
        assert np.array_equal(data["affine_lps"], affine)
    receipt = {
        "round_id": "BR-011", "status": "author screening and unlabeled prototype; no model trials",
        "script_sha256": digest(Path(__file__)), "taxonomy_sha256": digest(taxonomy_path), "sources": sources,
        "coordinate_sort": {"method": "descending physical superior-coordinate centroid, separately within named families; exact supplied-label multiset available in identity-audit condition",
                            "rows": family_rows, "families_all_correct": sum(r["all_correct"] for r in family_rows), "families_tested": len(family_rows)},
        "organ_baseline": {"method": "leave-one-patient-out nearest median template; standardized scan-normalized centroid, log physical volume and three log bounding-box extents; no tuning or one-to-one assignment",
                           "rows": baseline_rows, "correct": sum(r["correct"] for r in baseline_rows), "total": sum(r["total"] for r in baseline_rows),
                           "limitation": "Author baseline has labeled examples from seven other patients. This is not an LLM trial, not evidence that a harder-looking residual is fair, and not a mask-only clinical adjudication."},
        "prototype": {"source_case_id": 32, "public_path": str(public), "private_key_path": str(private / "expected.json"),
                      "object_count": len(objects), "roundtrip_exact": True,
                      "files": [{"path": str(p.relative_to(public)), "sha256": digest(p), "bytes": p.stat().st_size} for p in sorted(public.iterdir())]},
        "elapsed_seconds": round(time.monotonic() - start, 3),
    }
    write_json(args.evidence, receipt)
    print(json.dumps({"coordinate_families": [receipt["coordinate_sort"]["families_all_correct"], len(family_rows)],
                      "organ_correct_total": [receipt["organ_baseline"]["correct"], receipt["organ_baseline"]["total"]],
                      "prototype_objects": len(objects), "seconds": receipt["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
