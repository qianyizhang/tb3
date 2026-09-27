"""Verify the retained BR-012 source screen and derive a fresh teaching pack."""

import argparse
import base64
import hashlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n")


def label(value):
    if value == 28:
        return "T13"
    if value <= 7:
        return f"C{value}"
    if value <= 19:
        return f"T{value - 7}"
    return f"L{value - 19}" if value <= 25 else "overflow"


def build(root, output, license_path):
    output.mkdir(parents=True, exist_ok=False)
    receipt_path = root / "docs/evidence/br012-curation.json"
    receipt = json.loads(receipt_path.read_text())
    script = root / "probes/revisions/br012/authoring/screen_verse.py"
    if sha(script) != receipt["script_sha256"]:
        raise ValueError("Retained author method changed")
    sources = {str(p.relative_to(root)): sha(p) for p in (receipt_path, script)}
    files = list((root / "runs/br012-curation/source/files").rglob("*"))
    for row in receipt["source_receipts"]:
        matches = [p for p in files if p.is_file() and p.as_posix().endswith(row["member"])]
        if len(matches) != 1 or sha(matches[0]) != row["sha256"]:
            raise ValueError("Missing or changed source member")
        sources[str(matches[0].relative_to(root))] = row["sha256"]
    preview_path = root / "runs/br012-curation/author/preview.json"
    previews = {s["scene"]: s for s in json.loads(preview_path.read_text())}
    sources[str(preview_path.relative_to(root))] = sha(preview_path)
    geometry, references, points_checked, instances, mask_ctd = {}, {}, 0, 0, []
    for case in receipt["cases"]:
        image = nib.load(root / case["path"])
        data = np.asanyarray(image.dataobj)
        axes = [
            np.flatnonzero(np.any(data, axis=tuple(j for j in range(3) if j != i)))
            for i in range(3)
        ]
        offset = np.array([a[0] for a in axes])
        cropped = data[tuple(slice(a[0], a[-1] + 1) for a in axes)]
        values = np.unique(cropped)
        if not np.all(np.isfinite(values)) or not np.all(values == np.rint(values)):
            raise ValueError("Source labels are not finite integers")
        if set(values) - {0, *[o["source_value"] for o in case["objects"]]}:
            raise ValueError("Unexpected source label")
        affine = np.diag([-1, -1, 1, 1]) @ image.affine
        inverse = np.linalg.inv(affine)
        voxel_ml = abs(np.linalg.det(affine[:3, :3])) / 1000
        objects, answers = [], []
        for row in case["objects"]:
            coords = np.argwhere(cropped == row["source_value"]) + offset
            centroid = coords.mean(0) @ affine[:3, :3].T + affine[:3, 3]
            if (
                len(coords) != row["voxel_count"]
                or not np.allclose(centroid, row["centroid_lps_mm"], atol=0.000051, rtol=0)
                or abs(len(coords) * voxel_ml - row["volume_ml"]) > 0.000051
            ):
                raise ValueError("Full occupancy measurement differs from receipt")
            cloud = next(o for o in previews[case["scene"]]["objects"] if o["id"] == row["id"])
            if (
                cloud["label"] != row["source_label"]
                or label(row["source_value"]) != row["source_label"]
            ):
                raise ValueError("Preview reference mismatch")
            packed = cloud["points_int16le_lps_tenths_mm"]
            points = np.frombuffer(base64.b64decode(packed), dtype="<i2").reshape(-1, 3) / 10
            voxels = np.rint(
                np.einsum("ij,kj->ik", points, inverse[:3, :3]) + inverse[:3, 3]
            ).astype(int)
            if np.any(voxels < 0) or np.any(voxels >= np.asarray(data.shape)):
                raise ValueError("Preview outside source grid")
            restored = np.einsum("ij,kj->ik", voxels, affine[:3, :3]) + affine[:3, 3]
            if (
                not np.all(np.isfinite(restored))
                or np.max(np.abs(restored - points)) > 0.050001
                or not np.all(data[tuple(voxels.T)] == row["source_value"])
            ):
                raise ValueError("Preview points do not match source occupancy")
            interior = np.ones(len(voxels), dtype=bool)
            for axis in range(3):
                for shift in (-1, 1):
                    adjacent = voxels.copy()
                    adjacent[:, axis] += shift
                    inside = np.all((adjacent >= 0) & (adjacent < np.asarray(data.shape)), axis=1)
                    same = np.zeros(len(voxels), dtype=bool)
                    same[inside] = data[tuple(adjacent[inside].T)] == row["source_value"]
                    interior &= same
            if np.any(interior):
                raise ValueError("Preview includes non-boundary voxels")
            points_checked += len(points)
            instances += 1
            objects.append(
                {
                    "id": row["id"],
                    "points_int16le_lps_tenths_mm": packed,
                    "centroid_lps_mm": centroid.tolist(),
                    "volume_ml": row["volume_ml"],
                }
            )
            answers.append(
                {"id": row["id"], "source": row["source_label"], "value": row["source_value"]}
            )
        ordered = sorted(objects, key=lambda o: -o["centroid_lps_mm"][2])
        actual = [next(a["source"] for a in answers if a["id"] == o["id"]) for o in ordered]
        multiset = [
            a["source"]
            for a in sorted(answers, key=lambda a: 19.5 if a["value"] == 28 else a["value"])
        ]
        top = next(a["value"] for a in answers if a["id"] == ordered[0]["id"])
        fixed = [label(top + i) for i in range(len(ordered))]
        if actual != case["physical_superior_order"]:
            raise ValueError("Superior ordering differs")
        for predicted, key in [
            (multiset, "supplied_multiset_sort"),
            (fixed, "fixed_12_thoracic_sort_given_top_anchor"),
        ]:
            if (
                predicted != case[key]["predictions"]
                or sum(a == b for a, b in zip(actual, predicted, strict=True))
                != case[key]["correct"]
            ):
                raise ValueError("Baseline differs from retained receipt")
        ctd_path = Path(
            str(root / case["path"]).replace("seg-vert_msk.nii.gz", "seg-subreg_ctd.json")
        )
        ctd = {
            r["label"]
            for r in json.loads(ctd_path.read_text())
            if isinstance(r, dict) and "label" in r
        }
        mask = {a["value"] for a in answers}
        mask_ctd.append(
            {
                "scene": case["scene"],
                "mask_values_missing_centroid": sorted(mask - ctd),
                "centroid_values_missing_mask": sorted(ctd - mask),
            }
        )
        geometry[case["scene"]] = {
            "objects": objects,
            "spacing_mm": case["spacing_mm"],
            "affine_lps": affine.tolist(),
        }
        references[case["scene"]] = {
            "objects": answers,
            "curation": case["curation"],
            "multiset_correct": case["supplied_multiset_sort"]["correct"],
            "fixed_correct": case["fixed_12_thoracic_sort_given_top_anchor"]["correct"],
        }
        del data, cropped, coords
        print(case["scene"], "verified", flush=True)
    if (
        mask_ctd != receipt["verification"]["source_annotation_crosscheck"]
        or points_checked != 104100
        or instances != 145
    ):
        raise ValueError("Source crosscheck or coverage differs")
    dump(output / "geometry.json", {"scenes": geometry, "frame": "LPS", "units": "mm"})
    dump(
        output / "reference.json",
        {
            "visibility": "author source curation; reader reference reveal only",
            "scenes": references,
            "summary": receipt["summary"],
            "source_annotation_crosscheck": mask_ctd,
        },
    )
    shutil.copyfile(license_path, output / "DATA-LICENSE.txt")
    (output / "NOTICE.md").write_text(
        "# VerSe anatomy curation teaching derivative\n\n"
        "VerSe data: Anjany Sekuboyina et al.; Hans Liebl, David Schinz et al.; Maximilian Loffler et al. "
        "Source: https://github.com/anjany/verse and https://doi.org/10.1038/s41597-021-01060-0 . "
        "Data and this point/reference derivative are CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/ . "
        "License text and disclaimers are retained. No source author endorses this adaptation.\n\n"
        "Derived from seven unmodified retained vertebral masks (six patients), source centroids and author previews. "
        "The builder independently recomputes all 145 full-occupancy centroids, voxel counts and volumes, both "
        "ordering screens and mask/centroid membership. Every one of 104100 sampled boundary voxel centres "
        "is inverse-mapped to its source label and checked for boundary membership and maximum 0.05 mm per-axis "
        "quantization error. Little-endian int16 values encode LPS millimetres times ten. No faces or connectivity. "
        "The 21 original source members and retained author method are hash-checked; historical code is never run.\n\n"
        "Display rotation [L,S,-P] preserves handedness. Each patient's geometry retains its native physical frame. "
        "Separate displayed scans are independently placed and uniformly scaled, never registered or fused. "
        "406 upper and lower overlap in three identities, so 145 instances are not independent subjects. "
        "The focused 406 view selects T9-T11 without changing their positions or shapes. No CT is embedded.\n\n"
        "Source labels and curation decisions live separately in reference.json, revealed only for readers. "
        "This is not a blind solver packet or clinical adjudication. Source masks omit ribs/sacrum. "
        "581 ambiguity, 406 upper C1 missing centroid, source omission policy, and differences in sampling remain "
        "unresolved qualification boundaries. Zero hard tasks admitted, zero model trials, no injected errors.\n\n"
        "Rebuild with an existing NumPy/NiBabel environment: `python scripts/build_anatomy_curation_assets.py "
        "--root . --output NEW_DIRECTORY --license PATH_TO_CC_BY_SA_4_TEXT`.\n"
    )
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-anatomy-curation-v1",
            "frame": "LPS",
            "units": "mm",
            "license": "CC-BY-SA-4.0",
            "label_license": "CC-BY-SA-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": {
                "source_files": 21,
                "instances": instances,
                "source_boundary_points": points_checked,
                "mask_centroid_crosscheck": mask_ctd,
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
                "instances": instances,
                "points": points_checked,
                "geometry_bytes": (output / "geometry.json").stat().st_size,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--license", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output, args.license)
