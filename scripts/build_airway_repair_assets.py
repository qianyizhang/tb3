"""Audit saved BR-033 outputs and derive calibrated teaching assets, without inference.

Import-safe. Requires the existing NumPy/SciPy/NiBabel/Pillow/scikit-image environment.
Every destination is fresh; historical task, trial and authoring files are read-only.
"""

import argparse
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from build_resect_assets import png
from build_respiratory_assets import dump, plane, read, sha, world
from scipy import ndimage
from scipy.interpolate import RegularGridInterpolator
from skimage.measure import marching_cubes

PINS = {
    "docs/evidence/br033-freeze.json": "d44adf4e098c1d54b1f567af765f63d2ba480a810349225f6ee2dfbd5f66e3c8",
    "docs/evidence/br033-results.json": "7747d60a45eb10a2e7fd1e672d5b9b885cebedcd5449fcb3f2c2141d0a6e43a0",
    "docs/evidence/br033-scope-audit.json": "d1e0e0056821fc780cd9bfc56183629c0099e0c97e35a2e78e9012ae36db2265",
    "docs/evidence/br033-source-audit.json": "8c1607d37554eadf288e4eed9d79b49ce9577f2ee2f26e1d589e55343ca2994a",
    "runs/br033-airway-routing/benchmark/build.json": "7965fb9acccdf507a315a1dc1b26080a401648cb13ef497801aa77645c609e91",
    "runs/br033-airway-routing/benchmark/validation.json": "7660a550674393bd58a9acbf30b629c25e2a659fef1095888c21496a0841f1f3",
}
CASES = ["A01", "A02", "A03"]
STRUCTURE = np.ones((3, 3, 3), dtype=bool)


def mesh(mask, affine):
    if not mask.any():
        return {"vertices": [], "faces": []}
    # Padding closes the crop cuts for display; these caps are not anatomical endpoints.
    vertices, faces, _, _ = marching_cubes(np.pad(mask.astype("uint8"), 1), 0.5)
    return {
        "vertices": np.round(world(vertices - 1, affine), 3).tolist(),
        "faces": faces.tolist(),
    }


def components(mask, anchor_ijk):
    labels, count = ndimage.label(mask, STRUCTURE)
    sizes = np.bincount(labels.ravel())
    ids = labels[tuple(anchor_ijk.T)]
    largest = int(np.argmax(sizes[1:]) + 1)
    return {
        "components": count,
        "anchor_components": ids.tolist(),
        "anchor_component_voxels": sizes[ids].tolist(),
        "anchors_connected": bool(ids[0] > 0 and ids[0] == ids[1]),
        "anchors_in_largest_component": (ids == largest).tolist(),
    }


def overlay(mask, color):
    rgba = np.zeros((*mask.shape, 4), dtype="uint8")
    rgba[mask] = [*color, 155]
    return png(rgba)


def build(root, output, audit_path):
    output.mkdir(parents=True, exist_ok=False)
    if audit_path.exists():
        raise ValueError("Audit destination already exists")
    sources = {}

    def pin(rel, expected=None):
        path = root / rel
        actual = sha(path)
        if expected is not None and actual != expected:
            raise ValueError(f"Pinned source changed: {rel}")
        sources[rel] = actual
        return path

    receipts = {p: read(pin(p, h)) for p, h in PINS.items()}
    frozen = receipts["docs/evidence/br033-freeze.json"]["tasks"][0]
    task = frozen["task_path"]
    for file, h in frozen["files"].items():
        pin(task + "/" + file, h)
    actual_files = {
        str(p.relative_to(root / task)) for p in (root / task).rglob("*") if p.is_file()
    }
    if actual_files != set(frozen["files"]):
        raise ValueError("Frozen task membership changed")
    results = receipts["docs/evidence/br033-results.json"]
    scope = receipts["docs/evidence/br033-scope-audit.json"]
    source = receipts["docs/evidence/br033-source-audit.json"]["aeropath"]
    for row in source["dataset_files"]:
        p = pin("runs/br033-brain-routing/airway-access/" + row["path"], row["sha256"])
        if p.stat().st_size != row["bytes"]:
            raise ValueError("Dataset member size changed")
    trial = results["trials"]["terra-high"]
    trial_dir = trial["job"] + "/" + trial["trial"]
    pin(trial_dir + "/agent/trajectory.json")
    pin(trial_dir + "/result.json")
    build_rows = receipts["runs/br033-airway-routing/benchmark/build.json"]
    geometry, outputs, references, checks = [], [], [], []
    for case in CASES:
        row = next(r for r in build_rows if r["id"] == case)
        data = root / task / "environment/data" / case
        image = nib.load(data / "image.nii.gz")
        affine = image.affine
        hu = np.asarray(image.dataobj)
        proposed = np.asarray(nib.load(data / "proposed_mask.nii.gz").dataobj) > 0
        editable = np.asarray(nib.load(data / "editable_region.nii.gz").dataobj) > 0
        request = read(data / "request.json")
        anchors = np.array([request["start_ras_mm"], request["end_ras_mm"]])
        anchor_ijk = np.rint(world(anchors, np.linalg.inv(affine))).astype(int)
        with np.load(root / task / "tests/truth" / case / "reference.npz", allow_pickle=False) as z:
            ref = {k: z[k] for k in z.files}
        if not all(
            np.array_equal(a, b)
            for a, b in [
                (hu, ref["image"]),
                (proposed, ref["proposed"]),
                (editable, ref["editable"]),
            ]
        ):
            raise ValueError("Public/private task values mismatch")
        private_affine_error = float(np.max(np.abs(affine - ref["affine"])))
        if private_affine_error > 2e-5:
            raise ValueError("Private/native affine differs beyond NIfTI storage rounding")
        patient = row["source_patient"]
        original = root / f"runs/br033-brain-routing/airway-access/data/{patient}"
        source_ct = nib.load(original / f"{patient}_CT_HR.nii.gz")
        source_gt = nib.load(original / f"{patient}_CT_HR_label_airways.nii.gz")
        pred_rel = (
            f"runs/br033-airway-routing/case{patient}/airways/prediction/labels_Airways.nii.gz"
        )
        prediction = nib.load(pin(pred_rel, row["source_prediction_sha256"]))
        if not all(np.array_equal(source_ct.affine, n.affine) for n in [source_gt, prediction]):
            raise ValueError("Native source affines disagree")
        lo = np.array(row["crop_lo"])
        slices = tuple(slice(int(a), int(a + b)) for a, b in zip(lo, hu.shape, strict=True))
        crop_affine = source_ct.affine.copy()
        crop_affine[:3, 3] = world(lo[None], source_ct.affine)[0]
        # NIfTI stores sform translations in float32. Permit only that storage rounding.
        affine_error = float(np.max(np.abs(crop_affine - affine)))
        if (
            affine_error > 2e-5
            or not np.array_equal(hu, np.asarray(source_ct.dataobj[slices]))
            or not np.array_equal(proposed, np.asarray(prediction.dataobj[slices]) > 0)
            or not np.array_equal(ref["gt"], np.asarray(source_gt.dataobj[slices]) > 0)
        ):
            raise ValueError("Frozen crop differs from unchanged source")
        answer = root / trial_dir / "artifacts/app/answer" / case
        for name, h in results["viewer_provenance"][case]["unchanged_trial_files"].items():
            pin(str((answer / name).relative_to(root)), h)
        corrected = nib.load(answer / "corrected_mask.nii.gz")
        after = np.asarray(corrected.dataobj) > 0
        if not np.array_equal(corrected.affine, affine) or after.shape != hu.shape:
            raise ValueError("Returned mask grid changed")
        added, removed = after & ~proposed, proposed & ~after
        if removed.any() or (added & ~editable).any():
            raise ValueError("Returned edit violates preservation")
        measured = {
            "case": case,
            "before": components(proposed, anchor_ijk),
            "after": components(after, anchor_ijk),
            "added": int(added.sum()),
            "removed": int(removed.sum()),
        }
        if measured != next(r for r in scope["cases"] if r["case"] == case):
            raise ValueError("Retained connectivity audit no longer reproduces")
        # Independently check the saved method's single threshold component. No solver execution.
        chosen = np.zeros_like(proposed)
        if not measured["before"]["anchors_connected"]:
            labels, _ = ndimage.label(proposed, STRUCTURE)
            ids = labels[tuple(anchor_ijk.T)]
            candidates, count = ndimage.label((hu < -700) & editable & ~proposed, STRUCTURE)
            selected = []
            for index in range(1, count + 1):
                around = ndimage.binary_dilation(candidates == index, STRUCTURE)
                if all(np.any(around & (labels == anchor)) for anchor in ids):
                    selected.append(index)
            if len(selected) != 1:
                raise ValueError("Saved threshold method is not uniquely reproduced")
            chosen = candidates == selected[0]
        if not np.array_equal(chosen, added):
            raise ValueError("Saved edit differs from trace-described threshold component")
        route = np.load(answer / "centerline.npy", allow_pickle=False)
        with np.load(answer / "cpr.npz", allow_pickle=False) as z:
            cpr = {k: z[k] for k in z.files}
        coordinates = world(cpr["source_ras_mm"].reshape(-1, 3), np.linalg.inv(affine))
        interp = RegularGridInterpolator(
            tuple(np.arange(n) for n in hu.shape), hu, bounds_error=False, fill_value=-1024
        )
        difference = np.abs(interp(coordinates).reshape(cpr["hu"].shape) - cpr["hu"])
        sampling = {
            "pixels": int(difference.size),
            "p99_error_hu": float(np.percentile(difference, 99)),
            "max_error_hu": float(difference.max()),
        }
        if sampling["p99_error_hu"] > 0.2 or not np.allclose(
            cpr["source_ras_mm"][:, :, 32], route[None], atol=1e-9, rtol=0
        ):
            raise ValueError("Saved CPR sampling or centre axis inconsistent")
        public = {
            "id": case,
            "patient": patient,
            "shape": list(hu.shape),
            "affine_ras_mm": affine.tolist(),
            "anchors": anchors.tolist(),
            "request": request,
            "mesh_key": "A01" if case == "A03" else case,
            "sections": [],
        }
        output_case = {
            "id": case,
            "route": route.tolist(),
            "added_mesh": mesh(added, affine),
            "cpr": [],
            "slice_added": [],
        }
        reference_case = {
            "id": case,
            "core_mesh": mesh(ref["core"].astype(bool), affine),
            "reference_path": ref["reference_path"].tolist(),
            "slice_core": [],
            "metrics": trial["metrics"]["cases"][case]["metrics"],
            "connectivity": measured,
        }
        axis = 2 if case == "A02" else 0
        center = np.rint(
            world(np.array(request["review_center_ras_mm"])[None], np.linalg.inv(affine))
        ).astype(int)[0]
        dims = [d for d in range(3) if d != axis]
        a, b = dims
        indices = range(max(0, center[axis] - 4), min(hu.shape[axis], center[axis] + 5))
        for k in indices:

            def take(array, plane_index=k, slice_axis=axis):
                return np.flipud(np.take(array, plane_index, axis=slice_axis).T)

            origin = np.zeros(3)
            origin[axis], origin[b] = k, hu.shape[b] - 1
            section = plane(
                take(hu),
                world(origin[None], affine)[0],
                affine[:3, a],
                -affine[:3, b],
                f"{case} native axis {axis}, index {k}",
            )
            section.update(
                index=k,
                axis=axis,
                proposed=overlay(take(proposed), [113, 151, 169]),
                editable=overlay(take(editable), [239, 169, 51]),
            )
            public["sections"].append(section)
            output_case["slice_added"].append(overlay(take(added), [43, 187, 160]))
            reference_case["slice_core"].append(
                overlay(take(ref["core"].astype(bool)), [232, 128, 173])
            )
        arc = cpr["arc_mm"]
        display_arc = np.linspace(arc[0], arc[-1], 2 * len(arc) - 1)
        if not np.all(np.diff(arc) > 0):
            raise ValueError("Saved CPR arc is not strictly increasing")
        for i, angle in enumerate(cpr["angles_deg"]):
            # Display-only interpolation along the saved physical arc; no new CT sampling.
            display_hu = np.stack(
                [np.interp(display_arc, arc, cpr["hu"][i, :, u]) for u in range(65)], axis=1
            )
            display_u8 = np.rint(255 * np.clip((display_hu + 1000) / 1200, 0, 1)).astype("uint8")
            image_cpr = np.rint(255 * np.clip((cpr["hu"][i] + 1000) / 1200, 0, 1)).astype("uint8")
            output_case["cpr"].append(
                {
                    "angle_deg": float(angle),
                    "png": png(image_cpr),
                    "arc_png": png(display_u8),
                    "display_arc_mm": display_arc.tolist(),
                    "width": 65,
                    "height": len(route),
                    "arc_mm": cpr["arc_mm"].tolist(),
                    "offsets_mm": cpr["offsets_mm"].tolist(),
                    "sampling_edges": cpr["source_ras_mm"][i, :, [0, 64], :]
                    .transpose(1, 0, 2)
                    .tolist(),
                }
            )
        if case != "A03":
            dump(output / f"mask-{case}.json", mesh(proposed, affine))
        geometry.append(public)
        outputs.append(output_case)
        references.append(reference_case)
        checks.append(
            {
                **measured,
                "source_crop_affine_storage_error_mm": affine_error,
                "private_affine_storage_error_mm": private_affine_error,
                "source_crop_values_exact": True,
                "threshold_component_exact": True,
                "cpr_sampling": sampling,
                "core_voxels": int(ref["core"].sum()),
                "covered_core_voxels": int((after & ref["core"].astype(bool)).sum()),
            }
        )
    if not all(
        sha(root / task / "environment/data/A01" / f)
        == sha(root / task / "environment/data/A03" / f)
        for f in ["image.nii.gz", "proposed_mask.nii.gz"]
    ):
        raise ValueError("A01/A03 no longer share their crop")
    dump(output / "geometry.json", geometry)
    dump(output / "output.json", outputs)
    dump(output / "reference.json", references)
    shutil.copyfile(root / task / "environment/DATA-LICENSE.txt", output / "DATA-LICENSE.txt")
    (output / "NOTICE.md").write_text(
        "# Airway local-route repair: retained BR-033 evidence\n\n"
        "Source: AeroPath, Hofstad, Bouget, Pedersen, Støverud, Langø and Leira; "
        "https://github.com/raidionics/AeroPath and https://doi.org/10.5281/zenodo.10069289. "
        "Retained dataset revision 6d0f831ca22bf57918aba3980ae475c94d45b997. "
        "Dataset license.md and frozen DATA-LICENSE.txt say CC-BY-4.0; historical HF card "
        "metadata said MIT. Retain that mismatch; repository code terms are not data terms. "
        "Paper: https://doi.org/10.1371/journal.pone.0311416.\n\n"
        "Three requests from two patients; A01 and A03 share the same source crop. "
        "geometry.json holds public CT sections, predicted-mask sections, editable regions and "
        "anchors. mask-A01/A02.json are unchanged predicted masks, converted at level 0.5 by "
        "marching cubes with one-voxel padding. Crop caps are artificial display boundaries. "
        "Meshes round coordinates to 0.001 mm for drawing only. Native NIfTI RAS+ mm are "
        "preserved. Each case has a proper fixed display rotation and uniform fit; A01/A03 "
        "share that fit. Cases are not registered to one another.\n\n"
        "Nine native sections per request are selected around the public review centre; "
        "they are unresampled CT pixels with fixed HU window -1000 to 200. Pixel centres, "
        "spacing and affine are retained. output.json contains saved Terra/high added-mask "
        "surfaces, ordered routes and all eight CPR images; these are actual submitted values, "
        "not generated geometry. CPR axes use saved arc length and offsets. Its ribbons "
        "show saved source coordinates. The displayed CPR raster linearly interpolates submitted "
        "HU only along saved arc positions onto twice-dense uniform rows, preserving physical "
        "pixel-centre calibration; the original row raster is also retained. No new CT samples "
        "or diagnostic images are generated. Its moving cursor is reader inspection, not "
        "a reconstruction of the agent's search. Optional historical PLYs are not used.\n\n"
        "reference.json contains private core/path geometry, original numerical metrics and "
        "the separately reproduced full-crop connectivity audit. References start hidden. "
        "Portable HTML includes these assets and is not a solver packet. The frozen pass "
        "concerns requested endpoint routes, not parent-tree completeness, branch identity "
        "or clinical utility. A02/A03 remain detached from their larger parent components. "
        "No new model/inference/optimizer run or clinical adjudication is performed.\n\n"
        "Rebuild into a fresh directory with `python scripts/build_airway_repair_assets.py "
        "--root . --output NEW_DIRECTORY --audit NEW_AUDIT.json` using existing imaging extras.\n"
    )
    audit = {
        "schema": 1,
        "experiment": "tubular-anatomy-br033",
        "scope": "saved-artifact audit; no new trial",
        "sources": sources,
        "frozen_files": len(frozen["files"]),
        "source_members": len(source["dataset_files"]),
        "checks": checks,
        "A01_A03_same_crop": True,
        "original_reward_unchanged": trial["reward"],
    }
    dump(audit_path, audit)
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-airway-repair-v1",
            "frame": "RAS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": checks,
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
                "files": len(frozen["files"]),
                "source_members": len(source["dataset_files"]),
                "checks": checks,
                "bytes": {p.name: p.stat().st_size for p in output.iterdir()},
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output, args.audit)
