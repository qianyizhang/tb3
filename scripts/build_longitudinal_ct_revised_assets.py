"""Verify three revised CT conditions and derive native reader assets, without inference."""

import argparse
import base64
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from scipy import ndimage

GROUP = "groups/longitudinal-reading"
PACK = "retained-longitudinal-ct-revised-v1"
PINS = {
    f"{GROUP}/findings/evidence/longitudinal-ct-v2-and-localized.json": "40fc5bb3f21a6aae5415d6b6b822b8f6ef088554639f3e33c4957bbfbbe71974",
    f"{GROUP}/findings/evidence/longitudinal-ct-case02-astra-medium.json": "a2969ebdb772e2df3bf2e3bdf9953576bdbdd07eb757f53b3decd739cc0f1d33",
    f"{GROUP}/findings/evidence/longitudinal-ct-context-comparison.json": "b0e0f523696d547b696b005a9f8a0e66cd96b63dac6114198c9ee97ffba835d8",
    f"{GROUP}/findings/evidence/longitudinal-ct-image-only-comparison.json": "099020ce4bc2fb3d94703e9f7a83f2b093cccfdc9925e7354ac6f550df180657",
    f"{GROUP}/examples/longitudinal-ct-case02-preparation.json": "3329139db6c68ec3b5b5b7e89e63438f1f5d3b367d26fba699fbf4020d98b271",
    f"{GROUP}/examples/longitudinal-ct-case02-selection.json": "dd1ad9fddc14116e659e00428d1d3d229f4e1daae28c4157496b429dfba92a3e",
    f"{GROUP}/examples/longitudinal-ct-context-preparation.json": "637890a71ce3f078ba86b9e0bbee8143d6ae34a492871d3367ba4020bfa38ce7",
    f"{GROUP}/examples/longitudinal-ct-review-20260922.json": "f98c77d343a1b2432c256e92a852a80be4b63af8227abed09c2ef80e1df94c82",
}
CONDITIONS = {
    "case1-revised": (
        "longitudinal-ct-v2-astra-medium",
        "attempt-4749bbfb347f4809",
        "110a8ffd31c0991525ff33800c7a91023bb7cb24cddda518fecd3395f34d75f1",
    ),
    "case2-image": (
        "longitudinal-ct-case02-astra-medium",
        "attempt-92800845745342f4",
        "e12f6fc10c83c8dfb2bc4ca3bd4cfffc90811bdb7249ad8ddedcf55655b1083a",
    ),
    "case2-context": (
        "longitudinal-ct-context-supplied-astra-medium",
        "attempt-81ee755346d04be7",
        "ffdf321ba2637b46484309d8ec2c39fdffd5234b99e3152842c245a25a149215",
    ),
}
COLORS = {
    "reference": "#36dcdd",
    "case1-original": "#ffb636",
    "case1-revised": "#e583ea",
    "case2-image": "#e583ea",
    "case2-context": "#ffb636",
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def png(array, rgba=False, size=None):
    if not rgba:
        array = np.rint(np.clip((array + 160) / 400, 0, 1) * 255).astype(np.uint8).T
    image = Image.fromarray(array)
    if size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    data = io.BytesIO()
    image.save(data, format="PNG")
    return "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()


def outline(mask, color):
    rgba = np.zeros((*mask.T.shape, 4), dtype=np.uint8)
    labels = []
    for label in [int(n) for n in np.unique(mask) if n]:
        binary = mask.T == label
        edge = binary & ~ndimage.binary_erosion(binary, structure=np.ones((3, 3)))
        rgba[edge] = [int(color[i : i + 2], 16) for i in (1, 3, 5)] + [255]
        point = np.argwhere(binary).mean(axis=0)
        labels.append({"id": label, "pixel_ij": [float(point[1]), float(point[0])]})
    return {"image": png(rgba, rgba=True), "labels": labels}


def view(image, g, predictions, visit, k, center, fov_mm, selection):
    spacing = float(image.header.get_zooms()[0])
    width = round(fov_mm / spacing)
    origin = np.rint(np.asarray(center[:2]) - width / 2).astype(int)
    assert np.all(origin >= 0) and np.all(origin + width <= np.array(image.shape[:2]))
    crop = (
        slice(int(origin[0]), int(origin[0] + width)),
        slice(int(origin[1]), int(origin[1] + width)),
        int(k),
    )
    return {
        "visit": visit,
        "k": int(k),
        "origin_ij": origin.tolist(),
        "width_pixels": width,
        "fov_mm": width * spacing,
        "z_ras_mm": float((image.affine @ [0, 0, k, 1])[2]),
        "selection": selection,
        "image": png(np.asarray(image.dataobj[crop])),
        "reference": outline(g[crop], COLORS["reference"]),
        "outputs": {name: outline(mask[crop], COLORS[name]) for name, mask in predictions.items()},
    }


def build(root, output, audit_path, replay):
    for path in (output, audit_path, replay):
        if path.exists():
            raise FileExistsError(f"Fresh destination required: {path}")
    sources = {}

    def pin(path, expected):
        assert sha(root / path) == expected, path
        sources[str(path)] = expected

    for path, expected in PINS.items():
        pin(path, expected)
    revised = read(root / GROUP / "findings/evidence/longitudinal-ct-v2-and-localized.json")[
        "conditions"
    ]["whole-volume"]
    case2 = read(root / GROUP / "findings/evidence/longitudinal-ct-case02-astra-medium.json")
    context = read(root / GROUP / "findings/evidence/longitudinal-ct-context-comparison.json")
    original = read(root / GROUP / "findings/evidence/longitudinal-ct-image-only-comparison.json")[
        "conditions"
    ]["astra-medium"]
    context_prep = read(root / GROUP / "examples/longitudinal-ct-context-preparation.json")[
        "provenance"
    ]
    for record in revised["sources"][:2]:
        pin(record["path"], record["sha256"])
    for name in [
        ".local/longitudinal-ct-context-v1/supplied/analysis/evidence.json",
        ".local/longitudinal-ct-context-v1/supplied/trace-review.json",
    ]:
        pin(name, context["sources"][name])
    v2_analysis = read(root / revised["sources"][0]["path"])
    context_analysis = read(
        root / ".local/longitudinal-ct-context-v1/supplied/analysis/evidence.json"
    )
    evidence = {
        "case1-revised": v2_analysis,
        "case2-image": case2,
        "case2-context": context_analysis,
    }
    for record in evidence.values():
        for path, expected in record.get("source_files", record.get("source_hashes", {})).items():
            pin(path, expected)
    pin(context_prep["demographics_file"], context_prep["demographics_sha256"])
    pin(
        ".local/longitudinal-ct-case02/source/record-v3-current.json",
        context_prep["source_record_sha256"],
    )
    pin(
        f"{GROUP}/methods/longitudinal-ct-context-v1/context-block.md",
        context_prep["context_block_sha256"],
    )
    row = next(
        r
        for r in csv.DictReader((root / context_prep["demographics_file"]).open())
        if r["ID"] == "bcbe3365e6"
    )
    assert row == context_prep["demographics_row"]
    source_files = read(root / GROUP / "examples/longitudinal-ct-case02-preparation.json")[
        "preparation"
    ]["source_hashes"]
    for path, expected in source_files.items():
        pin(".local/longitudinal-ct-case02/raw/" + path, expected)
    for record in read(root / GROUP / "examples/longitudinal-ct-review-20260922.json")["files"]:
        if "0a09c8844b" in record["member"]:
            pin(".local/longitudinal-ct-review/raw/" + record["member"], record["sha256"])
    tasks, answers, freezes, results = {}, {}, {}, {}
    replay.mkdir(parents=True)
    for name, (experiment, attempt, digest) in CONDITIONS.items():
        records = list((root / GROUP / "experiments" / experiment / "freezes").glob("*.json"))
        assert len(records) == 1
        freeze = read(records[0])
        assert freeze["task_digest"] == digest
        task = root / freeze["snapshot_path"]
        for path, expected in freeze["files"].items():
            pin((task / path).relative_to(root), expected)
        tasks[name] = task
        freezes[name] = freeze
        jobs = list((root / ".local/attempts" / attempt / "job").glob("task__*"))
        assert len(jobs) == 1
        answers[name] = jobs[0] / "artifacts/app/answer"
        metrics = read(jobs[0] / "verifier/metrics.json")
        assert metrics == evidence[name]["metrics"]
        subprocess.run(
            [
                sys.executable,
                str(task / "tests/score.py"),
                "--answer",
                str(answers[name]),
                "--reference",
                str(task / "tests/reference"),
                "--output",
                str(replay / name),
            ],
            check=True,
            capture_output=True,
        )
        fresh = read(replay / name / "metrics.json")
        assert fresh == metrics
        results[name] = {
            "attempt": attempt,
            "metrics": metrics,
            "events": read(answers[name] / "events.json"),
            "report": (answers[name] / "report.md").read_text(),
            "replay_exact": True,
        }
    old_freeze_path = (
        root
        / GROUP
        / "experiments/longitudinal-ct-image-only-astra-medium/freezes/freeze-9e363d3d3a81bb8b7933cd4a.json"
    )
    old = read(old_freeze_path)
    assert [p for p, h in old["files"].items() if freezes["case1-revised"]["files"][p] != h] == [
        "instruction.md"
    ]
    assert [
        p
        for p, h in freezes["case2-image"]["files"].items()
        if freezes["case2-context"]["files"][p] != h
    ] == ["instruction.md"]
    assert (
        freezes["case1-revised"]["files"]["instruction.md"]
        == freezes["case2-image"]["files"]["instruction.md"]
    )
    assert len({f["files"]["tests/score.py"] for f in freezes.values()}) == 1
    old_jobs = list((root / ".local/attempts" / original["attempt_id"] / "job").glob("task__*"))
    assert len(old_jobs) == 1
    answers["case1-original"] = old_jobs[0] / "artifacts/app/answer"
    for path, expected in original["predictions"].items():
        pin((answers["case1-original"] / path).relative_to(root), expected)
    results["case1-original"] = {
        "attempt": original["attempt_id"],
        "metrics": original["metrics"],
        "events": read(answers["case1-original"] / "events.json"),
        "report": (answers["case1-original"] / "report.md").read_text(),
        "replay_exact": "previous entry 016",
    }
    prompt = (tasks["case2-image"] / "instruction.md").read_text()
    block = (root / GROUP / "methods/longitudinal-ct-context-v1/context-block.md").read_text()
    expected = prompt.replace(
        "Use your best image-based judgment of lesion presence:",
        block.rstrip()
        + "\n\nUse your best judgment of lesion presence from the images and supplied broad context:",
    )
    assert expected == (tasks["case2-context"] / "instruction.md").read_text()
    output.mkdir(parents=True)
    overview, geometry, instances, measurements, point_checks, groups = [], [], [], [], [], {}
    for case, patient, raw_root, variants in [
        (
            "case1",
            "0a09c8844b",
            ".local/longitudinal-ct-review/raw",
            ["case1-original", "case1-revised"],
        ),
        (
            "case2",
            "bcbe3365e6",
            ".local/longitudinal-ct-case02/raw",
            ["case2-image", "case2-context"],
        ),
    ]:
        task = tasks["case1-revised" if case == "case1" else "case2-image"]
        groups[case] = read(task / "tests/reference/events.json")["groups"]
        for visit, code in [("baseline", "BL"), ("followup", "FU")]:
            image = nib.load(task / f"environment/data/{visit}.nii.gz")
            source_image = nib.load(root / raw_root / f"inputsTr/{patient}_{code}_img_00.nii.gz")
            ref_image = nib.load(task / f"tests/reference/{visit}_instances.nii.gz")
            assert image.shape == source_image.shape == ref_image.shape
            assert np.array_equal(image.affine, source_image.affine) and np.array_equal(
                image.affine, ref_image.affine
            )
            assert np.array_equal(np.asarray(image.dataobj), np.asarray(source_image.dataobj))
            assert nib.aff2axcodes(image.affine) == ("L", "P", "S")
            spacing = list(map(float, image.header.get_zooms()[:3]))
            g = np.asarray(ref_image.dataobj).astype(np.uint16)
            predictions = {}
            for name in variants:
                p = nib.load(answers[name] / f"{visit}_instances.nii.gz")
                assert image.shape == p.shape and np.allclose(
                    image.affine, p.affine, rtol=0, atol=1e-5
                )
                predictions[name] = np.asarray(p.dataobj).astype(np.uint16)
            geo = {
                "case": case,
                "visit": visit,
                "shape": list(image.shape),
                "spacing_mm": spacing,
                "affine_ras_mm": image.affine.tolist(),
                "full_source_pixels_equal": True,
            }
            geometry.append(geo)
            k = image.shape[2] // 2
            overview.append(
                {**geo, "k": k, "image": png(np.asarray(image.dataobj[:, :, k]), size=(256, 256))}
            )
            rows = []
            for label, box in enumerate(ndimage.find_objects(g), 1):
                if box is None:
                    continue
                region = g[box] == label
                coords = np.argwhere(region) + np.array([s.start for s in box])
                center = coords.mean(axis=0)
                volume = float(len(coords) * np.prod(spacing) / 1000)
                components, _ = ndimage.label(region, ndimage.generate_binary_structure(3, 1))
                sizes = sorted(int(n) for n in np.bincount(components.ravel())[1:])
                item = {
                    "case": case,
                    "visit": visit,
                    "id": label,
                    "voxels": len(coords),
                    "volume_ml": volume,
                    "center_ijk": center.tolist(),
                    "center_ras_mm": nib.affines.apply_affine(image.affine, center).tolist(),
                    "max_area_k": int(np.bincount(coords[:, 2]).argmax()),
                    "components_6": sizes,
                    "stratum": "<=1 mL"
                    if volume <= 1
                    else ">1 to 10 mL"
                    if volume <= 10
                    else ">10 mL",
                    "outputs": {},
                }
                for name, mask in predictions.items():
                    per_gt = next(
                        r
                        for r in results[name]["metrics"]["visits"][visit]["per_gt"]
                        if r["gt_id"] == label
                    )
                    assert per_gt["voxels"] == len(coords)
                    item["outputs"][name] = {
                        "matched_id": per_gt["detection_prediction_id"],
                        "gt_macro_dice": per_gt["best_one_to_one_dice"],
                        "coverage": float(np.count_nonzero(region & (mask[box] > 0)) / len(coords)),
                    }
                rows.append(item)
                instances.append(item)
                if case == "case2":
                    expanded = tuple(
                        slice(max(0, s.start - 1), min(image.shape[i], s.stop + 1))
                        for i, s in enumerate(box)
                    )
                    local = g[expanded]
                    adjacent = ndimage.binary_dilation(
                        local == label, ndimage.generate_binary_structure(3, 1)
                    )
                    assert not np.any(adjacent & (local != 0) & (local != label))
            total = sum(r["volume_ml"] for r in rows)
            dominant = next(r for r in rows if r["id"] == 4)
            measurements.append(
                {
                    "case": case,
                    "visit": visit,
                    "instances": len(rows),
                    "total_reference_ml": total,
                    "dominant_reference_ml": dominant["volume_ml"],
                    "dominant_share": dominant["volume_ml"] / total,
                }
            )
            views = {}
            if case == "case1":
                if visit == "baseline":
                    views["partition"] = [
                        view(image, g, predictions, visit, k, [255, 263], 150, "reference-selected")
                        for k in [108, 116, 120]
                    ]
                focus = next(r for r in rows if r["id"] == 3)
                views["focus"] = view(
                    image,
                    g,
                    predictions,
                    visit,
                    focus["max_area_k"],
                    focus["center_ijk"],
                    100,
                    "reference-selected",
                )
            else:
                views["dominant"] = view(
                    image,
                    g,
                    predictions,
                    visit,
                    dominant["max_area_k"],
                    dominant["center_ijk"],
                    200,
                    "reference-selected",
                )
                point = [190, 199, 406] if visit == "baseline" else [182, 165, 524]
                assert g[tuple(point)] == 2
                assert f"({','.join(map(str, point))})" in results["case2-context"]["report"]
                assert (
                    "benign cyst-like or vascular focus favored over tumor"
                    in results["case2-context"]["report"]
                )
                views["excluded"] = view(
                    image,
                    g,
                    predictions,
                    visit,
                    point[2],
                    point,
                    64 * spacing[0],
                    "saved-report-coordinate",
                )
                views["excluded"]["reported_point_ijk"] = point
                point_checks.append(
                    {
                        "visit": visit,
                        "point_ijk": point,
                        "reference_id": int(g[tuple(point)]),
                        "context_mask_at_point": int(predictions["case2-context"][tuple(point)]),
                    }
                )
                if visit == "followup":
                    new = next(r for r in rows if r["id"] == 13)
                    assert new["components_6"] == [1, 1207]
                    views["new_focus"] = [
                        view(
                            image,
                            g,
                            predictions,
                            visit,
                            k,
                            new["center_ijk"],
                            90,
                            "reference-selected",
                        )
                        for k in [527, 529, 531]
                    ]
            write(output / f"{case}-{visit}.json", views)
            del g, predictions
    assert len(instances) == 28
    strata = {}
    for name in ["case2-image", "case2-context"]:
        strata[name] = []
        for stratum in ["<=1 mL", ">1 to 10 mL", ">10 mL"]:
            selected = [r for r in instances if r["case"] == "case2" and r["stratum"] == stratum]
            strata[name].append(
                {
                    "stratum": stratum,
                    "count": len(selected),
                    "localized": sum(
                        r["outputs"][name]["matched_id"] is not None for r in selected
                    ),
                    "macro_dice": float(
                        np.mean([r["outputs"][name]["gt_macro_dice"] for r in selected])
                    ),
                }
            )
        assert [r["count"] for r in strata[name]] == [11, 9, 2]
        assert [r["localized"] for r in strata[name]] == [0, 1, 2]
    write(
        output / "source.json",
        {
            "overview": overview,
            "colors": COLORS,
            "window_hu": [-160, 240],
            "clinical_context": context_prep["field_provenance"],
            "context_block": block,
            "conditions": [
                {"name": k, "experiment": v[0], "attempt": v[1], "digest": v[2]}
                for k, v in CONDITIONS.items()
            ],
        },
    )
    write(
        output / "reference.json",
        {
            "instances": instances,
            "measurements": measurements,
            "strata": strata,
            "groups": groups,
            "results": results,
            "point_checks": point_checks,
            "comparison_class": "diagnostic",
        },
    )
    (output / "DATA-LICENSE.txt").write_text(
        "Longitudinal-CT v3, University Hospital Tübingen. Küstner, Peisen, Gatidis, Wagner, Megne, Othman, Sanner, Loßau, Moltz, Kohlbrandt and Hering.\nCreative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).\nhttps://creativecommons.org/licenses/by-nc/4.0/\nSource: https://fdat.uni-tuebingen.de/records/qe950-g4h94 ; DOI 10.57754/FDAT.qe950-g4h94.\nTB3 derived grayscale crops, native mask outlines and teaching layout; no endorsement implied. Noncommercial use only under the source terms.\n"
    )
    (output / "NOTICE.md").write_text("""# Revised longitudinal CT teaching views

Two selected Longitudinal-CT v3 cases and three retained Astra-medium conditions. Source attribution and CC BY-NC 4.0 terms are in DATA-LICENSE.txt. The original first-case attempt is a pinned comparator. Full source/input voxels and native affines agree. All three 18-file task freezes, source acquisition members and final answers are checked. The original private scorer replays three saved answers into fresh local destinations with exact parsed-field equality. This is not a new model trial; no historical authoring module is executed.

Only instruction.md differs between original and revised first-case tasks, and between image-only and context-supplied second-case tasks. The two revised image-only instructions are byte-identical. The same scientific scorer is used throughout. The context block supplies released age 44, recorded sex female, 121-day interval and explicitly cohort-level metastatic melanoma/systemic therapy/staging context; it supplies no individual report, regimen, surgery history or lesion annotation. A separate context-inference output never enters this condition.

Display uses fixed [-160,240] HU mapped to 8-bit grayscale. Full-field middle slices are downsampled to 256 pixels with Lanczos; crops retain native pixels. Native axial plane transpose places R left, L right and A top. Scale follows actual native spacing; visits are not registered. The second pair uses 2.0/2.5 mm slice spacing, not the first pair's 3 mm. Mask outlines are one-pixel inner boundaries with 8-neighbor erosion; colors identify sources, not diagnosis. ID text anchors are per-slice means, not lesion centroids or new labels. Cyan is reference; purple is revised/image-only output; amber is original/context-supplied output, as each scene specifies.

Most crops are post-hoc reference-selected and remove search; the excluded-candidate crop instead uses exact saved report coordinates. The point marker belongs to the saved report and the cyan annotation is revealed separately. The report rejects these points as benign cyst-like/vascular; both are in source GT2, with zero context-output coverage. This documents disagreement relative to GT, not clinical adjudication. Accepted follow-up source ID13 retains its original one-voxel satellite; neither labels nor scores are corrected. All 22 second-case instances remain in visit-level size strata, with the two large instances representing one identity at two visits.

Foreground overlap, one-to-one detection, equal-instance overlap, mapped links and complete typed events retain separate denominators. Case 1's instance/confluence adjudication stays open. Case 2's distinct source labels do not touch; it contains seven persistent and eight new groups, with no merging/disappearing group. The same 3/22 instances are detected with and without broad context. One attempt each and bundled context changes do not isolate causality or rule out effects of unavailable detailed reports. No population accuracy, clinical response or general model ranking is inferred. Portable HTML embeds private-to-solver reference material and is a reader explanation, never a solver packet.
""")
    assets = []
    for p in sorted(output.iterdir()):
        assert p.stat().st_size <= 1024**2, p
        assets.append(
            {
                "file": p.name,
                "bytes": p.stat().st_size,
                "sha256": sha(p),
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
            }
        )
    write(
        output / "manifest.json",
        {
            "id": PACK,
            "license": "CC-BY-NC-4.0",
            "label_license": "CC-BY-NC-4.0",
            "frame": "RAS",
            "units": "mm",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "assets": assets,
        },
    )
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    write(
        audit_path,
        {
            "schema": 1,
            "scope": "Three-condition source verification and saved-output replay; no new inference or clinical adjudication",
            "sources": sources,
            "frozen_tasks": {
                k: {"digest": v["task_digest"], "files": len(v["files"])}
                for k, v in freezes.items()
            },
            "instruction_only_comparisons": [
                "case1 original to revised",
                "case2 image-only to context-supplied",
            ],
            "image_only_prompt_identical_across_cases": True,
            "scorer_identical": True,
            "geometry": geometry,
            "instances": instances,
            "measurements": measurements,
            "strata": strata,
            "point_checks": point_checks,
            "replay_exact": list(CONDITIONS),
            "clinical_context_fields": context_prep["field_provenance"],
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "audit": str(audit_path),
                "source_pins": len(sources),
                "frozen_files": 54,
                "instances": len(instances),
                "saved_replays": len(CONDITIONS),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output, args.audit, args.replay)
