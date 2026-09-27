"""Audit retained TopBrain screening and derive teaching views without inference.

Import-safe. Uses existing NumPy/SciPy/NiBabel/Pillow/trimesh imaging extras.
No historical authoring imports, optimizers, downloads or source writes.
"""

import argparse
import json
import shutil
import zlib
from pathlib import Path

import nibabel as nib
import numpy as np
import trimesh
from build_resect_assets import png
from build_respiratory_assets import dump, read, sha, world
from scipy import ndimage
from scipy.spatial import cKDTree

RAW = "runs/br033-brain-routing"
DATA = RAW + "/sources/TopBrain_Data_Release_Batches1n2nTA36_081726"
RECEIPT = "docs/evidence/br033-brain-resumption.json"
PINS = {
    RECEIPT: "c4c6f6888ccb80e97dca4789f743b41ad6f7072137e78351965b170bd4a3e213",
    "datasets/receipts/topbrain-members.json": "e8c3d87676f414031aa7dc1fdf48786d3c300413bf5d1372ea17519114aafb60",
}
TERMS = "LicenseRef-TopBrain-2026-noncommercial"
S26 = np.ones((3, 3, 3), dtype=bool)
S6 = ndimage.generate_binary_structure(3, 1)
COLORS = {
    "context": [91, 119, 216],
    "first": [244, 170, 61],
    "second": [39, 196, 188],
    "added": [231, 81, 159],
    "detached": [231, 81, 159],
}


def box(mask, pad=2):
    points = np.argwhere(mask)
    lo = np.maximum(points.min(0) - pad, 0)
    hi = np.minimum(points.max(0) + pad + 1, mask.shape)
    return lo, hi


def slices(lo, hi):
    return tuple(slice(int(a), int(b)) for a, b in zip(lo, hi, strict=True))


def raster(values, axis, index=None):
    plane = values.max(axis=axis) if index is None else np.take(values, index, axis=axis)
    return np.flipud(plane.T)


def gray(values, limits):
    return png(
        np.rint(np.clip((values - limits[0]) / (limits[1] - limits[0]), 0, 1) * 255).astype("uint8")
    )


def overlay(labels, groups, axis, index=None):
    shape = raster(labels, axis, index).shape
    rgba = np.zeros((*shape, 4), dtype="uint8")
    for ids, color in groups:
        mask = raster(np.isin(labels, ids), axis, index)
        rgba[mask] = [*COLORS[color], 175]
    return png(rgba)


def view(image, pred, ref, affine, lo, hi, groups, axis=2, index=None):
    """Calibrated native pixels or a stated depth projection, without reslicing."""
    cut = slices(lo, hi)
    values, p, r = image[cut], pred[cut], ref[cut]
    local = None if index is None else int(index - lo[axis])
    dimensions = [a for a in range(3) if a != axis]
    displayed = raster(values, axis, local)
    window = np.percentile(values, [2, 99.7]).tolist()
    if window[1] <= window[0]:
        raise ValueError("Empty image window")
    origin = lo.copy()
    origin[dimensions[1]] = hi[dimensions[1]] - 1
    origin[axis] = lo[axis] if index is None else index
    spacing = nib.affines.voxel_sizes(affine)
    public = {
        "kind": "maximum-intensity-projection" if index is None else "native-section",
        "axis": axis,
        "index": index,
        "origin_ijk": lo.tolist(),
        "end_ijk_exclusive": hi.tolist(),
        "width": displayed.shape[1],
        "height": displayed.shape[0],
        "pixel_spacing_mm": [float(spacing[a]) for a in dimensions],
        "origin_ras_mm": world(origin[None], affine)[0].tolist(),
        "dx_ras_mm": affine[:3, dimensions[0]].tolist(),
        "dy_ras_mm": (-affine[:3, dimensions[1]]).tolist(),
        "window": window,
        "image": gray(displayed, window),
        "prediction": overlay(p, groups, axis, local),
    }
    return public, overlay(r, groups, axis, local)


def attachment(labels, chain):
    lo, hi = box(np.isin(labels, chain), pad=0)
    crop = labels[slices(lo, hi)]
    cc, count = ndimage.label(np.isin(crop, chain), S26)
    ids, sizes = np.unique(cc[crop == chain[0]], return_counts=True)
    parent = int(ids[np.argmax(sizes)])
    rows = {}
    for label in chain[1:]:
        mask = crop == label
        rows[str(label)] = {
            "voxels": int(mask.sum()),
            "parent_connected_voxels": int(((cc == parent) & mask).sum()),
            "fraction": float(np.mean(cc[mask] == parent)) if mask.any() else None,
        }
    return {"chain": chain, "components_26": int(count), "branches": rows}, (
        lo,
        hi,
        crop,
        cc,
        parent,
    )


def contact(labels, a, b):
    lo, hi = box(np.isin(labels, [a, b]))
    cut = labels[slices(lo, hi)]
    result = {
        f"contact_voxels_{n}": int(
            (ndimage.binary_dilation(cut == b, structure) & (cut == a)).sum()
        )
        for n, structure in [(6, S6), (26, S26)]
    }
    return result


def calibration(root, pin, image, pred, ref, affine, receipt):
    folder = RAW + "/gap-calibration"
    paths = {
        name: pin(folder + "/" + name)
        for name in [
            "corrected_labels.nii.gz",
            "original_labels.nii.gz",
            "corrected_crop_labels.nii.gz",
            "image.nii.gz",
            "centerline.npy",
            "reference_centerline.npy",
            "cpr.npz",
            "basilar-right-sca.ply",
        ]
    }
    ni = nib.load(paths["corrected_labels.nii.gz"])
    after = np.asarray(ni.dataobj, dtype="uint8")
    if ni.shape != pred.shape or not np.array_equal(ni.affine, affine):
        raise ValueError("Calibration output grid changed")
    changed = pred != after
    expected = np.array([[190, 306, 79], [191, 307, 79]])
    if not np.array_equal(np.argwhere(changed), expected) or not (
        np.all(pred[changed] == 0) and np.all(after[changed] == 25)
    ):
        raise ValueError("Calibration edits differ from retained two-voxel repair")
    meta = receipt["calibration"]
    lo, hi = np.array(meta["crop_lo"]), np.array(meta["crop_hi"])
    sca, sca_count = ndimage.label(pred[slices(lo, hi)] == 25, S26)
    sizes = np.bincount(sca.ravel())[1:]
    if sca_count != 2 or int(sizes.min()) != 247:
        raise ValueError("Saved distal SCA fragment differs")
    main_id, fragment_id = int(sizes.argmax() + 1), int(sizes.argmin() + 1)
    main_points = world(np.argwhere(sca == main_id) + lo, affine)
    fragment_points = world(np.argwhere(sca == fragment_id) + lo, affine)
    nearest = float(cKDTree(main_points).query(fragment_points)[0].min())
    if abs(nearest - meta["nearest_center_distance_mm"]) > 1e-8:
        raise ValueError("Saved nearest same-label centre distance differs")
    for name, full in [
        ("image.nii.gz", image),
        ("original_labels.nii.gz", pred),
        ("corrected_crop_labels.nii.gz", after),
    ]:
        crop = nib.load(paths[name])
        if not np.array_equal(np.asarray(crop.dataobj), full[slices(lo, hi)]):
            raise ValueError("Calibration crop differs from full source")
        expected_affine = affine.copy()
        expected_affine[:3, 3] = world(lo[None], affine)[0]
        if np.max(abs(crop.affine - expected_affine)) > 2e-5:
            raise ValueError("Calibration crop affine exceeds float32 storage rounding")
    anchors = np.array(meta["anchors_native_ijk"])
    connects = []
    for mask in [pred, after]:
        cc, _ = ndimage.label(np.isin(mask[slices(lo, hi)], [1, 25]), S26)
        ids = cc[tuple((anchors - lo).T)]
        connects.append(bool(ids[0] > 0 and ids[0] == ids[1]))
    if connects != [False, True]:
        raise ValueError("Saved parent-to-target connection does not reproduce")
    line = np.load(paths["centerline.npy"], allow_pickle=False)
    reference_line = np.load(paths["reference_centerline.npy"], allow_pickle=False)
    arc = np.r_[0, np.linalg.norm(np.diff(line, axis=0), axis=1).cumsum()]
    distance = cKDTree(reference_line).query(line)[0]
    for measured, recorded in [
        (arc[-1], meta["route_length_mm"]),
        (np.percentile(distance, 95), meta["route_to_reference_p95_mm"]),
        (distance.max(), meta["route_to_reference_max_mm"]),
    ]:
        if abs(measured - recorded) > 1e-9:
            raise ValueError("Saved route metrics do not reproduce")
    with np.load(paths["cpr.npz"], allow_pickle=False) as z:
        cpr = {k: z[k] for k in z.files}
    inverse = np.linalg.inv(affine)
    coords = cpr["source_ras_mm"] @ inverse[:3, :3].T + inverse[:3, 3]
    if not (
        np.isfinite(coords).all()
        and np.all(coords >= 0)
        and np.all(coords < np.array(image.shape) - 1)
    ):
        raise ValueError("CPR sample outside original MRA")
    floor = np.floor(coords).astype(int)
    frac = coords - floor
    values = np.zeros(coords.shape[:-1])
    for shift in np.ndindex(2, 2, 2):
        shifted = floor + np.array(shift)
        values += image[tuple(np.moveaxis(shifted, -1, 0))] * np.where(shift, frac, 1 - frac).prod(
            -1
        )
    error = float(np.max(abs(values - cpr["intensity"])))
    if (
        abs(error - receipt["calibration_validation"]["source_mra_trilinear_max_absolute_error"])
        > 1e-9
    ):
        raise ValueError("Saved CPR source comparison changed")
    zero = int(np.flatnonzero(np.isclose(cpr["offsets_mm"], 0)).item())
    if not all(
        [
            np.allclose(cpr["source_ras_mm"][:, :, zero], line[None], atol=1e-6),
            np.allclose(
                np.linalg.norm(cpr["source_ras_mm"] - line[None, :, None], axis=-1),
                abs(cpr["offsets_mm"])[None, None],
                atol=1e-6,
            ),
            np.allclose(cpr["arc_mm"], arc, atol=1e-6),
            np.array_equal(cpr["angles_deg"], np.arange(0, 360, 45)),
        ]
    ):
        raise ValueError("Saved CPR coordinates, arc or angles changed")
    mesh = trimesh.load(paths["basilar-right-sca.ply"], process=False)
    if not (
        mesh.is_watertight
        and len(mesh.split(only_watertight=False)) == 1
        and np.isfinite(mesh.vertices).all()
    ):
        raise ValueError("Saved target mesh is not one finite watertight component")
    groups = [([1, 25], "context")]
    overview, reference = view(image, pred, ref, affine, lo, hi, groups, axis=1)
    overview["route_native_ijk"] = world(line, np.linalg.inv(affine)).tolist()
    overview["anchors_native_ijk"] = anchors.tolist()
    local_lo, local_hi = np.array([175, 291, 77]), np.array([207, 323, 82])
    planes, references = [], []
    for k in range(77, 82):
        plane, ref_overlay = view(image, pred, ref, affine, local_lo, local_hi, groups, index=k)
        plane["added"] = overlay(
            changed[slices(local_lo, local_hi)].astype("uint8"), [([1], "added")], 2, k - 77
        )
        planes.append(plane)
        references.append(ref_overlay)
    # A uniform arc display interpolates only retained signal rows; no new source sampling.
    uniform = np.linspace(arc[0], arc[-1], len(arc) * 2)
    window = [
        float(np.percentile(cpr["intensity"], 2)),
        float(np.percentile(cpr["intensity"], 99.7)),
    ]
    cpr_views = []
    for angle, signal in zip(cpr["angles_deg"], cpr["intensity"], strict=True):
        displayed = np.stack(
            [np.interp(uniform, arc, signal[:, j]) for j in range(signal.shape[1])]
        )
        cpr_views.append(
            {
                "angle": float(angle),
                "width": len(uniform),
                "height": signal.shape[1],
                "png": gray(np.flipud(displayed), window),
                "raw_rows_png": gray(np.flipud(signal.T), window),
            }
        )
    checks = {
        "distal_fragment_voxels": int(sizes.min()),
        "nearest_same_label_centres_mm": nearest,
        "changed_voxels_native_ijk": expected.tolist(),
        "added_reference_labels": {
            str(int(v)): int(n)
            for v, n in zip(*np.unique(ref[changed], return_counts=True), strict=True)
        },
        "connected_before_after": connects,
        "route_length_mm": float(arc[-1]),
        "route_p95_mm": float(np.percentile(distance, 95)),
        "route_max_mm": float(distance.max()),
        "cpr_samples": int(values.size),
        "cpr_max_signal_error": error,
        "mesh_components": 1,
        "mesh_watertight": True,
    }
    public = {
        "overview": overview,
        "gap_sections": planes,
        "cpr": cpr_views,
        "arc_mm": arc.tolist(),
        "offsets_mm": cpr["offsets_mm"].tolist(),
        "cpr_window": window,
        "cpr_display_extent_mm": [float(arc[-1] + (uniform[1] - uniform[0])), 10.2],
        "changes_native_ijk": expected.tolist(),
    }
    return public, {"overview": reference, "gap_sections": references, "checks": checks}, checks


def build(root, output, audit_path):
    output.mkdir(parents=True, exist_ok=False)
    if audit_path.exists():
        raise ValueError("Audit destination already exists")
    sources = {}

    def pin(rel, expected=None):
        p = root / rel
        value = sha(p)
        if expected is not None and value != expected:
            raise ValueError(f"Pinned source changed: {rel}")
        sources[rel] = value
        return p

    receipts = {p: read(pin(p, h)) for p, h in PINS.items()}
    receipt = receipts[RECEIPT]
    for rel, h in receipt["runtime_evidence_sha256"].items():
        pin(RAW + "/" + rel, h)
    for member in receipts["datasets/receipts/topbrain-members.json"]["files"]:
        p = pin(RAW + "/sources/" + member["member"], member["sha256"])
        if p.stat().st_size != member["bytes"] or zlib.crc32(p.read_bytes()) != member["crc32"]:
            raise ValueError("TopBrain retained member size or CRC mismatch")
    manifest = read(root / RAW / "ta36-source-manifest.json")
    pin(RAW + "/ta36-model-source-layer.tar.gz", receipt["layer_sha256"])
    for row in manifest["files"]:
        p = pin(RAW + "/ta36-source/" + row["path"], row["sha256"])
        if p.stat().st_size != row["bytes"]:
            raise ValueError("Retained model/source member size mismatch")
    for name in [
        "contact-convention-audit.json",
        "variant-attachment-audit.json",
        "reference-parent-audit.json",
        "predictions-resencm-v1/review-regions.json",
    ]:
        pin(RAW + "/" + name)
    for name in [
        "infer_source.py",
        "screen_predictions.py",
        "find_review_regions.py",
        "gap_calibration.py",
        "validate_calibration.py",
    ]:
        pin("probes/brain-routing/authoring/" + name)
    screens = {
        r["case"][-3:]: r for r in read(root / RAW / "predictions-resencm-v1/reference-screen.json")
    }
    checks, refs, output_record = [], {}, {}
    for row in receipt["prediction_provenance"]["rows"]:
        case = row["case"]
        ni = nib.load(
            pin(DATA + f"/imagesTr_topbrain/topcow_mr_{case}_0000.nii.gz", row["input_sha256"])
        )
        pni = nib.load(
            pin(RAW + f"/predictions-resencm-v1/topcow_mr_{case}.nii.gz", row["output_sha256"])
        )
        rni = nib.load(
            pin(
                DATA + f"/labelsTr_topbrain_v2_topaneu36class/topcow_mr_{case}.nii.gz",
                screens[case]["reference_sha256"],
            )
        )
        if not all(ni.shape == n.shape and np.array_equal(ni.affine, n.affine) for n in [pni, rni]):
            raise ValueError("Image/prediction/reference grids differ")
        if (
            list(ni.shape) != row["shape"]
            or nib.aff2axcodes(ni.affine) != ("L", "P", "S")
            or ni.header.get_xyzt_units()[0] != "mm"
        ):
            raise ValueError("Native source grid or units changed")
        image = np.asarray(ni.dataobj)
        pred, ref = np.asarray(pni.dataobj, dtype="uint8"), np.asarray(rni.dataobj, dtype="uint8")
        if pred.max() > 36 or ref.max() > 36:
            raise ValueError("Not the TA36 label scheme")
        conf = np.bincount((ref.astype("uint16") * 37 + pred).ravel(), minlength=37 * 37).reshape(
            37, 37
        )
        present = set(np.flatnonzero(conf.sum(0) + conf.sum(1))) - {0}
        if present != {klass["label"] for klass in screens[case]["classes"]}:
            raise ValueError("Recorded screen omits a present label")
        metrics = []
        for klass in screens[case]["classes"]:
            k = klass["label"]
            nr, npred = int(conf[k].sum()), int(conf[:, k].sum())
            dice = 2 * int(conf[k, k]) / (nr + npred)
            if (
                nr != klass["reference_voxels"]
                or npred != klass["predicted_voxels"]
                or dice != klass["dice"]
            ):
                raise ValueError("Recorded label Dice or counts do not reproduce")
            metrics.append(
                {
                    "name": klass["name"],
                    "label": k,
                    "reference_voxels": nr,
                    "prediction_voxels": npred,
                    "dice": dice,
                }
            )
        mean = float(np.mean([m["dice"] for m in metrics]))
        expected = next(r for r in receipt["class_dice_summary"] if r["case"].endswith(case))
        if abs(mean - expected["mean_present_label_dice"]) > 1e-14:
            raise ValueError("Mean present-label Dice differs")
        check = {
            "case": case,
            "matched_native_grids": True,
            "labels_compared": len(metrics),
            "mean_present_label_dice": mean,
            "classes": metrics,
        }
        lo, hi = box((pred > 0) | (ref > 0), pad=2)
        overview, ref_overview = view(
            image, pred, ref, ni.affine, lo, hi, [(list(range(1, 37)), "context")]
        )
        public = {
            "id": case,
            "shape": list(ni.shape),
            "affine_ras_mm": ni.affine.tolist(),
            "overview": overview,
        }
        reference = {"overview": ref_overview, "metrics": metrics, "mean_present_label_dice": mean}
        candidate = next(
            (r for r in receipt["rejected_contact_candidates"] if r["case"] == case), None
        )
        if candidate:
            a, b = candidate["labels"]
            measured = {
                key: contact(labels, a, b)
                for key, labels in [("prediction", pred), ("reference", ref)]
            }
            if any(measured[k] != candidate[k] for k in measured):
                raise ValueError("Contact convention audit differs")
            loc = np.argwhere(ndimage.binary_dilation(pred == a, S6) & (pred == b))
            center = loc[np.argmin(np.linalg.norm(loc - loc.mean(0), axis=1))]
            low, high = np.maximum(center - 18, 0), np.minimum(center + 19, pred.shape)
            public["contacts"], reference["contacts"] = [], []
            for axis in range(3):
                plane, overlay_ref = view(
                    image,
                    pred,
                    ref,
                    ni.affine,
                    low,
                    high,
                    [([a], "first"), ([b], "second")],
                    axis=axis,
                    index=int(center[axis]),
                )
                public["contacts"].append(plane)
                reference["contacts"].append(overlay_ref)
            public["contact_labels"] = [a, b]
            reference["contact_metrics"] = measured
            check["contacts"] = measured
        if case in ["006", "011"]:
            chain = [4, 11, 15, 16]
            variants = {}
            for key, values in [("prediction", pred), ("reference", ref)]:
                stats, _ = attachment(values, chain)
                prior = receipt["variant_parent_attachment"][case][key]
                for label, name in [(15, "third_a2"), (16, "third_a3")]:
                    branch = stats["branches"][str(label)]
                    if (
                        branch["voxels"] != prior[name + "_voxels"]
                        or branch["fraction"] != prior[name + "_connected_to_right_ica_fraction"]
                    ):
                        raise ValueError("Variant parent attachment differs")
                variants[key] = stats
            lo, hi = box(np.isin(pred, chain) | np.isin(ref, chain), pad=2)
            public["variant"], reference["variant"] = view(
                image,
                pred,
                ref,
                ni.affine,
                lo,
                hi,
                [(chain, "context"), ([15], "first"), ([16], "second")],
                axis=1,
            )
            check["variant"] = variants
            reference["variant_metrics"] = variants
        if case == "007":
            stats, (lo, hi, crop, cc, parent) = attachment(ref, [6, 7, 19, 20])
            prior = read(root / RAW / "reference-parent-audit.json")["volumes"][
                DATA + "/labelsTr_topbrain_v2_topaneu36class/topcow_mr_007.nii.gz"
            ]["L-MCA"]
            if stats["components_26"] != prior["components_26"] or any(
                b["fraction"] != prior["branch_parent_connected_fraction"][k]
                for k, b in stats["branches"].items()
            ):
                raise ValueError("Reference parent-chain gap differs")
            public["parent"], reference["parent"] = view(
                image, pred, ref, ni.affine, lo, hi, [([6, 7, 19, 20], "context")], axis=1
            )
            detached = np.where(np.isin(crop, [6, 7, 19, 20]) & (cc != parent), 1, 0)
            reference["parent_detached"] = overlay(detached, [([1], "detached")], 1)
            reference["parent_metrics"] = stats
            check["parent"] = stats
        if case == "004":
            public["calibration"], reference["calibration"], check["calibration"] = calibration(
                root, pin, image, pred, ref, ni.affine, receipt
            )
        dump(output / f"case-{case}.json", public)
        refs[case] = reference
        checks.append(check)
        print(f"Verified TopBrain {case}: {len(metrics)} label scores", flush=True)
    dump(output / "reference.json", {"cases": refs})
    output_record = {
        "segmentation_predictions": 5,
        "hard_cases_admitted": 0,
        "coding_agent_trials": 0,
        "new_task_frozen": False,
        "dispositions": [
            {
                "id": "004-R-SCA",
                "status": "geometry-calibration",
                "reason": "Two-voxel input-legal geometric bridge; one added voxel is reference background.",
            },
            {
                "id": "004-L / 007-R / 011-L PCA-SCA",
                "status": "reference-convention-unresolved",
                "reason": "All three references touch at 26-neighbour connectivity.",
            },
            {
                "id": "006 / 011 third-A2-A3",
                "status": "potential-preservation-controls",
                "reason": "Predicted and reference variants already reach the selected carotid parent.",
            },
            {
                "id": "named-branch repair task",
                "status": "not-admitted",
                "reason": "No clean hard error/control set in this bounded development screen.",
            },
        ],
    }
    dump(output / "output.json", output_record)
    shutil.copyfile(root / DATA / "License.txt", output / "DATA-LICENSE.txt")
    (output / "NOTICE.md").write_text(
        "# TopBrain source-screen teaching assets\n\n"
        "Source: TopBrain Challenge Organizers / University Hospital of Zurich, TopBrain data release Batches1n2nTA36_081726, https://zenodo.org/records/21972006. "
        "MRA originates in TopCoW: https://zenodo.org/records/15692630. Released TA36 model: https://zenodo.org/records/21959166. "
        "Cite Yang et al., TopBrain segmentation challenge for whole brain vessel anatomy (2026), and Yang et al., The TopCoW Challenge (2026).\n\n"
        "The exact retained DATA-LICENSE.txt permits noncommercial use with attribution; commercial use requires the owner's permission. Code/model licensing does not replace data terms.\n\n"
        "Five public training/development MRA scans, one released ResEncM fold-4 component on MPS; no official ensemble replication or coding-agent trial. Original predictions and all historical records remain unchanged. "
        "Author-selected views use prediction/reference extents. Source labels are hidden until reader reveal; these teaching files embed references and are not a solver packet.\n\n"
        "Native pixels are unresampled. Display transposes and reverses the second in-plane axis; affine vectors, voxel bounds, axis/index, intensity windows and physical pixel spacing are retained. MIPs collapse a stated depth and do not prove 3D contacts. "
        "Overlay colors: blue context; orange first named class; turquoise second named class; pink saved additions or disconnected reference components, identified beside each scene.\n\n"
        "Contacts count PCA voxels neighboring SCA in full 3D 6/26-neighbour masks, not adjacency pairs. Attachment uses a specified named-label chain, not whole-brain connectivity or clinical adjudication. Macro Dice averages nonbackground classes present in either mask, with each class equally weighted. "
        "The retained interior screen uses a 0.5 mm reference-interior cutoff and is not exhaustive for thin vessels.\n\n"
        "The calibration changes two native voxels only. BA-to-R-SCA routing, eight CPRs and a one-component watertight mesh are saved author outputs, not newly executed repairs. "
        "All 140352 retained CPR samples are checked against original MRA. Display-only interpolation maps saved signal rows to uniform physical arc; raw row rasters remain included. Pixel-centre extent is 10.2 mm across 51 offsets at 0.2 mm. "
        "No view resolves the remaining reference-background addition or establishes a hard benchmark.\n"
    )
    manifest_out = {
        "schema": 1,
        "id": "retained-topbrain-screen-v1",
        "frame": "RAS",
        "units": "mm",
        "license": TERMS,
        "label_license": TERMS,
        "reference_policy": "reader-reference-reveal",
        "sources": sources,
        "assets": [],
    }
    for p in sorted(output.iterdir()):
        if p.stat().st_size > 1024 * 1024:
            raise ValueError(f"Teaching asset exceeds 1 MiB: {p.name}")
        manifest_out["assets"].append(
            {
                "file": p.name,
                "sha256": sha(p),
                "bytes": p.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
            }
        )
    dump(output / "manifest.json", manifest_out)
    audit = {
        "schema": 1,
        "scope": "Saved source/prediction/calibration audit and teaching extraction; no inference, optimization, adjudication or trial.",
        "source_members": len(receipts["datasets/receipts/topbrain-members.json"]["files"]),
        "model_source_members": len(manifest["files"]),
        "sources": sources,
        "cases": checks,
        "output": output_record,
    }
    dump(audit_path, audit)
    print(
        json.dumps(
            {"assets": len(manifest_out["assets"]), "sources": len(sources), "cases": len(checks)}
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output, args.audit)
