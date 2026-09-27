"""Pin original CT evidence, replay saved scores and derive native reader views."""

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

PACK = "retained-longitudinal-ct-original-v1"
GROUP = "groups/longitudinal-reading"
DIGEST = "f2aa2fb2f71acd930e927d581a2513c31dd6c5a03f1f0387ff64e00f098eea24"
PINS = {
    f"{GROUP}/findings/evidence/longitudinal-ct-image-only-comparison.json": "099020ce4bc2fb3d94703e9f7a83f2b093cccfdc9925e7354ac6f550df180657",
    f"{GROUP}/examples/longitudinal-ct-review-20260922.json": "f98c77d343a1b2432c256e92a852a80be4b63af8227abed09c2ef80e1df94c82",
    ".local/longitudinal-ct-review/source/record-v3.json": "28889bbe59bcb50ea039905596ff00542c6ae1989c1740fc5ce3ff85a64ff774",
}
COLORS = {1: "#36dcdd", 2: "#ef81e4", 3: "#a8ed70", 4: "#72a9ff"}
OUTPUT_COLOR = "#ffb636"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")


def png(array, overlay=False, resize=None):
    if not overlay:
        array = np.rint(np.clip((array + 160) / 400, 0, 1) * 255).astype(np.uint8).T
    im = Image.fromarray(array)
    if resize:
        im = im.resize(resize, Image.Resampling.LANCZOS)
    stream = io.BytesIO()
    im.save(stream, format="PNG")
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()


def outline(mask, colors):
    pixels = np.zeros((*mask.T.shape, 4), dtype=np.uint8)
    for label, color in colors.items():
        binary = mask.T == label
        edge = binary & ~ndimage.binary_erosion(binary, structure=np.ones((3, 3)))
        pixels[edge] = [int(color[i : i + 2], 16) for i in (1, 3, 5)] + [255]
    return png(pixels, overlay=True)


def equal(a, b):
    if isinstance(a, dict):
        assert a.keys() == b.keys()
        for k in a:
            equal(a[k], b[k])
    elif isinstance(a, list):
        assert len(a) == len(b)
        for x, y in zip(a, b, strict=True):
            equal(x, y)
    elif isinstance(a, float):
        assert abs(a - b) <= 1e-12, (a, b)
    else:
        assert a == b, (a, b)


def build(root, output, audit_path, replay):
    for path in (output, audit_path, replay):
        if path.exists():
            raise FileExistsError(f"Use a fresh destination: {path}")
    sources = {}

    def pin(path, expected):
        assert sha(root / path) == expected, path
        sources[str(path)] = expected

    for path, expected in PINS.items():
        pin(path, expected)
    retained = read(root / f"{GROUP}/findings/evidence/longitudinal-ct-image-only-comparison.json")
    source_receipt = read(root / f"{GROUP}/examples/longitudinal-ct-review-20260922.json")
    source_files = [f for f in source_receipt["files"] if "0a09c8844b" in f["member"]]
    assert len(source_files) == 7
    raw = root / ".local/longitudinal-ct-review/raw"
    for f in source_files:
        pin((raw / f["member"]).relative_to(root), f["sha256"])
    freezes = []
    for model in ("astra-medium", "sol-xhigh"):
        matches = list(
            (root / GROUP / "experiments" / f"longitudinal-ct-image-only-{model}" / "freezes").glob(
                "*.json"
            )
        )
        assert len(matches) == 1
        f = read(matches[0])
        assert f["task_digest"] == DIGEST
        task = root / f["snapshot_path"]
        for p, digest in f["files"].items():
            pin((task / p).relative_to(root), digest)
        freezes.append({"record": str(matches[0].relative_to(root)), "files": f["files"]})
    assert freezes[0]["files"] == freezes[1]["files"]
    assert len(freezes[0]["files"]) == 18
    reference = task / "tests/reference"
    reference_events = read(reference / "events.json")
    csv_rows = list(csv.DictReader((raw / "inputsTr/0a09c8844b.csv").open()))
    assert [int(r["lesion_id"]) for r in csv_rows if r["topology_class"] == "MERGING"] == [1, 2, 4]
    assert [int(r["lesion_id"]) for r in csv_rows if r["topology_class"] == "UNCHANGED"] == [3]
    assert {float(r["merged_into"]) for r in csv_rows if r["merged_into"]} == {4.0}
    assert reference_events["groups"] == [
        {"baseline_ids": [3], "followup_ids": [3], "event": "persistent"},
        {"baseline_ids": [1, 2, 4], "followup_ids": [4], "event": "merging"},
    ]
    answers, results = {}, []
    replay.mkdir(parents=True)
    for name, condition in retained["conditions"].items():
        job = root / ".local/attempts" / condition["attempt_id"] / "job"
        jobs = list(job.glob("task__*"))
        assert len(jobs) == 1
        answers[name] = jobs[0] / "artifacts/app/answer"
        for file, digest in condition["predictions"].items():
            pin((answers[name] / file).relative_to(root), digest)
        original = jobs[0] / "verifier/metrics.json"
        pin(original.relative_to(root), condition["audit"]["artifacts"]["verifier/metrics.json"])
        equal(read(original), condition["metrics"])
        subprocess.run(
            [
                sys.executable,
                str(task / "tests/score.py"),
                "--answer",
                str(answers[name]),
                "--reference",
                str(reference),
                "--output",
                str(replay / name),
            ],
            check=True,
            capture_output=True,
        )
        fresh = read(replay / name / "metrics.json")
        equal(fresh, condition["metrics"])
        results.append(
            {
                "condition": name,
                "model": condition["model"],
                "effort": condition["reasoning_effort"],
                "metrics": fresh,
                "events": read(answers[name] / "events.json"),
                "replay_equal": True,
            }
        )
    output.mkdir(parents=True)
    overview, geometry, labels, coverage, view_meta = [], [], [], [], []
    for visit, code in [("baseline", "BL"), ("followup", "FU")]:
        image = nib.load(task / f"environment/data/{visit}.nii.gz")
        original = nib.load(raw / f"inputsTr/0a09c8844b_{code}_img_00.nii.gz")
        gt = nib.load(reference / f"{visit}_instances.nii.gz")
        assert image.shape == original.shape == gt.shape
        assert np.array_equal(image.affine, original.affine)
        assert np.array_equal(image.affine, gt.affine)
        assert tuple(nib.aff2axcodes(image.affine)) == ("L", "P", "S")
        assert image.header.extensions == []
        assert not bytes(image.header["descrip"]).rstrip(b"\0")
        # A full voxel comparison, one volume at a time; no reorientation/resampling.
        array = np.asarray(image.dataobj)
        source_array = np.asarray(original.dataobj)
        assert np.array_equal(array, source_array)
        del source_array
        g = np.asarray(gt.dataobj).astype(np.uint16)
        pred = {}
        for name, answer in answers.items():
            p = nib.load(answer / f"{visit}_instances.nii.gz")
            assert p.shape == image.shape and np.allclose(p.affine, image.affine, rtol=0, atol=1e-5)
            pred[name] = np.asarray(p.dataobj).astype(np.uint16)
        assert not pred["sol-xhigh"].any()
        assert set(np.unique(pred["astra-medium"])) == {0, 1}
        spacing = list(map(float, image.header.get_zooms()[:3]))
        geo = {
            "visit": visit,
            "shape": list(image.shape),
            "spacing_mm": spacing,
            "affine_ras_mm": image.affine.tolist(),
            "source_pixels_equal": True,
        }
        geometry.append(geo)
        k = image.shape[2] // 2
        overview.append({**geo, "k": k, "image": png(array[:, :, k], resize=(256, 256))})
        instances = []
        for label in [int(n) for n in np.unique(g) if n]:
            coords = np.argwhere(g == label)
            center = coords.mean(axis=0)
            volume_mm3 = len(coords) * np.prod(spacing)
            row = {
                "visit": visit,
                "id": label,
                "voxels": len(coords),
                "center_ijk": center.tolist(),
                "center_ras_mm": nib.affines.apply_affine(image.affine, center).tolist(),
                "volume_ml": float(volume_mm3 / 1000),
                "max_area_k": int(np.bincount(coords[:, 2]).argmax()),
            }
            labels.append(row)
            instances.append(row)
            source_row = next(r for r in csv_rows if int(r["lesion_id"]) == label)
            csv_center = np.array([float(x) for x in source_row[f"cog_{code.lower()}"].split()])
            row["csv_center_minus_native_center_voxels"] = (csv_center - center).tolist()
            row["csv_volume_minus_mask_mm3"] = (
                float(source_row[f"volume_{code.lower()}"]) - volume_mm3
            )
            cov = np.count_nonzero((g == label) & (pred["astra-medium"] > 0)) / len(coords)
            coverage.append({"visit": visit, "reference_id": label, "astra_fraction_covered": cov})
        if visit == "baseline":
            components, _ = ndimage.label(g > 0, ndimage.generate_binary_structure(3, 1))
            groups = [set(np.unique(components[g == label])) - {0} for label in [1, 2, 4]]
            assert len(set.union(*groups)) == 1
            assert not groups[0] & set(np.unique(components[g == 3]))
            del components

        def view(
            k,
            center,
            fov_mm=150,
            *,
            spacing=spacing,
            image=image,
            visit=visit,
            array=array,
            g=g,
            pred=pred,
        ):
            width = round(fov_mm / spacing[0])
            lo = np.rint(np.asarray(center[:2]) - width / 2).astype(int)
            assert np.all(lo >= 0) and np.all(lo + width <= np.array(image.shape[:2]))
            crop = (slice(int(lo[0]), int(lo[0] + width)), slice(int(lo[1]), int(lo[1] + width)), k)
            meta = {
                "visit": visit,
                "k": k,
                "origin_ij": lo.tolist(),
                "width_pixels": width,
                "fov_mm": width * spacing[0],
                "z_ras_mm": float((image.affine @ [0, 0, k, 1])[2]),
            }
            view_meta.append(meta)
            return {
                **meta,
                "image": png(array[crop]),
                "reference": outline(g[crop], COLORS),
                "astra": outline(pred["astra-medium"][crop], {1: OUTPUT_COLOR}),
            }

        focus = next(r for r in instances if r["id"] == 3)
        dominant = next(r for r in instances if r["id"] == 4)
        frames = (
            [view(k, [255, 263]) for k in [114, 115, 116, 118, 119, 120]]
            if visit == "baseline"
            else [view(dominant["max_area_k"], dominant["center_ijk"])]
        )
        # Saved-output-selected view does not use any reference location.
        pcoords = np.argwhere(pred["astra-medium"] > 0)
        pk = int(np.bincount(pcoords[:, 2]).argmax())
        saved = view(pk, pcoords.mean(axis=0))
        saved.pop("reference")
        write(
            output / f"{visit}.json",
            {
                "boundary_frames": frames,
                "focus": view(focus["max_area_k"], focus["center_ijk"], 100),
                "saved_output_view": saved,
            },
        )
        del view, array, g, pred
    write(
        output / "source.json",
        {
            "case": "0a09c8844b",
            "window_hu": [-160, 240],
            "overview": overview,
            "reference_colors": COLORS,
            "output_color": OUTPUT_COLOR,
        },
    )
    write(
        output / "reference.json",
        {
            "groups": reference_events["groups"],
            "instances": labels,
            "coverage": coverage,
            "conditions": results,
            "comparison_class": "diagnostic",
            "instance_convention_review": "open",
            "six_connected_baseline_labels": [1, 2, 4],
        },
    )
    (output / "DATA-LICENSE.txt").write_text(
        "Longitudinal-CT v3, University Hospital Tübingen. Küstner, Peisen, Gatidis, Wagner, Megne, Othman, Sanner, Loßau, Moltz, Kohlbrandt and Hering.\nCreative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).\nhttps://creativecommons.org/licenses/by-nc/4.0/\nSource: https://fdat.uni-tuebingen.de/records/qe950-g4h94 ; DOI 10.57754/FDAT.qe950-g4h94.\nTB3 derived grayscale crops, native mask outlines and teaching layout; no endorsement implied. Noncommercial use only under the source terms.\n"
    )
    (output / "NOTICE.md").write_text("""# Original image-only longitudinal CT views

One retained Longitudinal-CT v3 pair, source case 0a09c8844b; CC BY-NC 4.0, attribution and terms in DATA-LICENSE.txt. The solver received two neutral-named full native CT volumes, without source identity, locations, counts, clinical history, masks or links. Source annotators had CT plus clinical reports; the solver did not. The frozen instruction, scorer and two saved attempts remain unchanged.

The builder verifies 18 shared frozen files, seven source members, release metadata, eight saved answer files and both original metric files. Full source and solver image arrays/affines agree. Both saved answers are rescored only into fresh local destinations with the original private scorer; this is saved-output replay, not new inference. Frozen preparation and analysis authoring modules are never executed.

Display: fixed [-160, 240] HU to 8-bit grayscale; overview middle slices are downsampled to 256 pixels with Lanczos. Crops keep native pixels. Axial display is the native plane transposed: patient R left, L right, A top. Both native axes have equal in-plane spacing; scale bars derive from actual crop width and spacing. Visits are unregistered. Voxel indices are zero-based; the affine maps their centers to RAS mm. Source CSV centers differ by approximately half a voxel from native mask-center means; views use mask-derived coordinates. Small source volume differences are retained in the audit.

The saved-output scene uses the Astra mask maximum-area slice and its centroid to choose a crop. All other close crops are reference-selected reader aids and remove search. Reference selection, outlines, counts and graph are shown only after an explicit reader-reference reveal. Cyan B1, pink B2, green B3/F3 and blue B4/F4 are source mask boundaries; amber solid outlines are the actual saved Astra mask. Outlines are one-pixel inner boundaries with an 8-neighbor erosion. Colors and IDs are local labels, not biological classifications. Empty Sol masks have no contour. Portable reader HTML embeds references and must not be used as a solver input packet.

Detection accepts a predicted centroid inside a reference or within 3 mm of its labeled voxel centers, with one-to-one maximum-cardinality assignment. Foreground Dice ignores instance partition; instance Dice includes zero for missed references. Links use mapped instance IDs; exact events require the entire typed group. Conditional edge success is 1/1 eligible of four GT edges for Astra; zero of two complete event groups are eligible. This cannot isolate merging ability. Empty masks and empty groups can pass the artifact contract.

The original wording treats a confluent region as one instance, while baseline reference labels 1, 2 and 4 share one 6-connected foreground component. This is an unresolved instruction/reference convention conflict, not proof that expert labels are wrong or that voxel contact establishes radiologic confluence. The issue was recognized before Sol dispatch; the same frozen prompt and no reference feedback were delivered. The comparison remains diagnostic: one selected public pair and one attempt each, with no general model ranking, clinical adjudication or new/disappearing-event coverage.
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
            "scope": "Native source verification and saved-output replay; no medical run or adjudication",
            "sources": sources,
            "shared_task_digest": DIGEST,
            "unique_frozen_files": 18,
            "freeze_records": freezes,
            "geometry": geometry,
            "instances": labels,
            "coverage": coverage,
            "views": view_meta,
            "replay": [
                {
                    "condition": r["condition"],
                    "equal": r["replay_equal"],
                    "absolute_tolerance": 1e-12,
                }
                for r in results
            ],
            "open_instance_review": True,
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "audit": str(audit_path),
                "source_pins": len(sources),
                "instances": len(labels),
                "replayed_saved_answers": len(results),
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
