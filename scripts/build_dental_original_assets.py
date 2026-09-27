"""Build native dental reader views from retained inputs, outputs and diagnostics."""

import argparse
import base64
import hashlib
import io
import json
import re
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.measure import find_contours

TEETH = [q * 10 + i for q in range(1, 5) for i in range(1, 9)]
ATTEMPTS = {
    "medium": "21af29aaf8034aa6",
    "xhigh": "68d5acdeb63f4262",
    "f002": "4338cd3dae024fc8",
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def outline(mask):
    paths = [
        (p[:, ::-1] - 0.5).tolist()
        for p in find_contours(np.pad(mask, 1), 0.5, fully_connected="low")
    ]
    for points in paths:
        p = np.asarray(points)
        assert np.all(p >= 0) and np.all(p <= [mask.shape[1], mask.shape[0]])
    return paths


def build(root, out):
    out.mkdir(parents=True, exist_ok=False)
    audit_path = Path("groups/anatomy-audit/presentation/sources/dental-original-audit.json")
    audit = read(root / audit_path)
    pins, pixels = {}, 0

    def pin(path):
        path = Path(path)
        digest = sha(root / path)
        if str(path) in audit["source_pins"]:
            assert digest == audit["source_pins"][str(path)], str(path)
        pins[str(path)] = digest
        return root / path

    pin(audit_path)
    cts, references, outputs, works = {}, {}, {}, {}
    for row in audit["cases"]:
        cts[row["case"]] = np.asanyarray(nib.load(pin(row["ct"])).dataobj)
        references[row["case"]] = np.asanyarray(nib.load(pin(row["reference"])).dataobj)
    for key, aid in ATTEMPTS.items():
        trial = next((root / ".local/attempts" / ("attempt-" + aid) / "job").glob("task__*"))
        outputs[key] = np.asanyarray(
            nib.load(
                pin((trial / "artifacts/app/answer/segmentation.nii.gz").relative_to(root))
            ).dataobj
        )
        works[key] = (trial / "artifacts/app/work").relative_to(root)
    labels = read(pin(Path(".local/dental-ct-only-astra-medium/task/environment/data/labels.json")))
    views, saved, truth = {}, {}, {}

    def png(plane):
        nonlocal pixels
        gray = np.uint8(np.clip((plane + 400) / 2900, 0, 1) * 255)
        stream = io.BytesIO()
        Image.fromarray(gray).save(stream, format="PNG", optimize=True)
        data = stream.getvalue()
        np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(data))), gray)
        pixels += gray.size
        return "data:image/png;base64," + base64.b64encode(data).decode()

    def plane(array, axis, index, bounds):
        (a, b), (c, d) = bounds
        return np.take(array, index, axis=axis)[a:b, c:d].T[::-1]

    def view(name, case, axis, index, ids, keys, selection, bounds=None, pooled=False):
        arrays = {key: outputs[key] for key in keys} | {"reference": references[case]}
        occupied = np.zeros(np.take(cts[case], index, axis=axis).shape, bool)
        for array in arrays.values():
            occupied |= np.isin(np.take(array, index, axis=axis), ids)
        if bounds is None:
            if ids:
                pos = np.argwhere(occupied)
                lo = np.maximum(pos.min(0) - 12, 0)
                hi = np.minimum(pos.max(0) + 13, occupied.shape)
                bounds = np.stack([lo, hi], axis=1).tolist()
            else:
                bounds = [[0, occupied.shape[0]], [0, occupied.shape[1]]]
        image = plane(cts[case], axis, index, bounds)
        axes = [i for i in range(3) if i != axis]
        views[name] = {
            "case": case,
            "axis": "ijk"[axis],
            "index": index,
            "plane_axes": ["ijk"[i] for i in axes],
            "bounds_uv": bounds,
            "width": image.shape[1],
            "height": image.shape[0],
            "png": png(image),
            "selection": selection,
            "window": [-400, 2500],
            "display": "native first plane axis increases right; second increases up; no patient-side assertion",
            "ids": ids,
            "pooled": pooled,
        }
        saved[name] = {}
        for key, array in arrays.items():
            lab = plane(array, axis, index, bounds)
            assert np.count_nonzero(np.isin(lab, ids)) == np.count_nonzero(
                np.isin(np.take(array, index, axis=axis), ids)
            ), (name, key, "selected contours clipped by reader crop")
            items = []
            for ident in ["canals"] if pooled else ids:
                mask = np.isin(lab, ids) if pooled else lab == ident
                pos = np.argwhere(mask)
                if not len(pos):
                    continue
                centre = (pos.mean(0)[::-1] + 0.5).tolist()
                items.append(
                    {
                        "id": ident,
                        "paths": outline(mask),
                        "center": centre,
                        "pixels": int(mask.sum()),
                    }
                )
            if key == "reference":
                truth[name] = items
            else:
                saved[name][key] = items

    view(
        "input-f018", "F018", 1, 205, [], [], "Full native j=205 section; complete volume supplied."
    )
    view("input-f002", "F002", 1, 205, [], [], "Full native j=205 section; separate source case.")
    view(
        "identity",
        "F018",
        2,
        55,
        TEETH,
        ["medium", "xhigh"],
        "Retained audit k=55; crop fits every selected tooth label in reference and both outputs plus 12 voxels.",
    )
    for j in [145, 205]:
        view(
            f"canals-{j}",
            "F018",
            1,
            j,
            [3, 4],
            ["medium", "xhigh"],
            "Retained audit cross-section; two main-canal IDs pooled to remove side-ID disagreement.",
            bounds=[[50, 365], [70, 230]],
            pooled=True,
        )
    view(
        "restorations",
        "F002",
        2,
        125,
        [8, 9, 10, *TEETH],
        ["f002"],
        "Retained audit k=125; reference and output define the reader crop after submission.",
    )
    view(
        "omitted-canals",
        "F002",
        1,
        145,
        [3, 4, 103, 104, 105],
        ["f002"],
        "Reader canal example. Whole-volume count verifies all five submitted labels are absent.",
        bounds=[[50, 365], [70, 260]],
        pooled=True,
    )

    # Reproduce a consequential saved rule, not the solver script. All displayed
    # gates use its retained float32 image and tooth envelope. Reference is used
    # only to select a reader plane and measure overlap after the attempt.
    work = works["f002"]
    a = np.load(pin(work / "ct.npy"), mmap_mode="r")
    s = np.load(pin(work / "refined.npy"), mmap_mode="r")
    pin(work / "pulp.py")
    np.testing.assert_array_equal(a, cts["F002"].astype(np.float32))
    gt_tooth, model_tooth = 16, 26
    indices = np.where(s == model_tooth)
    bb = tuple(
        slice(max(0, int(c.min()) - 3), min(s.shape[j], int(c.max()) + 4))
        for j, c in enumerate(indices)
    )
    envelope = s[bb] == model_tooth
    smooth = ndi.gaussian_filter(a[bb], 0.55)
    distance = ndi.distance_transform_edt(envelope)
    candidates = {"envelope": envelope, "distance": distance > 1.6}
    candidates["intensity"] = candidates["distance"] & (smooth < 1180)
    zz = np.arange(bb[2].start, bb[2].stop)[None, None, :]
    candidates["slice"] = candidates["intensity"] & (zz < 66)
    candidates["final"] = outputs["f002"][bb] == model_tooth + 100
    ref = references["F002"][bb] == gt_tooth + 100
    counts = {key: int(np.count_nonzero(mask & ref)) for key, mask in candidates.items()}
    row = next(r for r in audit["pulp_by_tooth"] if r["gt_tooth"] == gt_tooth)
    expected = dict(
        zip(
            candidates,
            [
                row[k]
                for k in [
                    "inside_corresponding_tooth_envelope",
                    "after_distance_gate",
                    "after_intensity_gate",
                    "after_slice_gate",
                    "final_correct_overlap",
                ]
            ],
            strict=True,
        )
    )
    assert counts == expected
    i = int(np.argmax(ref.sum((1, 2))))
    image = cts["F002"][bb][i].T[::-1]
    name = "pulp-gates"
    views[name] = {
        "case": "F002",
        "axis": "i",
        "index": i + bb[0].start,
        "plane_axes": ["j", "k"],
        "bounds_uv": [[bb[1].start, bb[1].stop], [bb[2].start, bb[2].stop]],
        "width": image.shape[1],
        "height": image.shape[0],
        "png": png(image),
        "selection": "GT tooth 16 has the largest gate-associated reference loss. Native i plane maximizes its reference pulp area within the saved tooth envelope bounding box.",
        "window": [-400, 2500],
        "display": "native j increases right, k up; no patient-side assertion",
        "ids": [116, 126],
        "pooled": False,
    }
    saved[name] = {key: outline(mask[i].T[::-1]) for key, mask in candidates.items()}
    truth[name] = outline(ref[i].T[::-1])
    gate_description = {
        "reference_tooth": gt_tooth,
        "saved_tooth": model_tooth,
        "selection": "post-hoc opposing-side pairing for a method diagnostic, not corrected identity",
        "reference_pulp_voxels": row["gt_pulp"],
        "overlap_counts": counts,
        "reference_overlap_is_not_precision": True,
        "parameters": {
            "distance_voxels_gt": 1.6,
            "gaussian_sigma_voxels": 0.55,
            "intensity_lt": 1180,
            "native_k_lt": 66,
        },
        "final_stage": "Saved submitted pulp label; includes component/core filters, closing and later cleanup, not strictly nested.",
    }
    # Check every projected pixel centre has an exact inverse in native space.
    for row in views.values():
        (u0, u1), (v0, v1) = row["bounds_uv"]
        for u, v in [(u0, v0), (u1 - 1, v1 - 1), ((u0 + u1 - 1) / 2, (v0 + v1 - 1) / 2)]:
            x, y = u - u0 + 0.5, v1 - v - 0.5
            np.testing.assert_array_equal([u0 + x - 0.5, v1 - y - 0.5], [u, v])

    dump(
        out / "source.json",
        {"schema": 1, "views": views, "labels": labels, "cases": audit["cases"]},
    )
    dump(out / "output.json", {"schema": 1, "views": saved, "gate_description": gate_description})
    dump(
        out / "reference.json",
        {
            "schema": 1,
            "views": truth,
            "diagnostics": audit["diagnostics"],
            "pulp_gates": audit["pulp_gates"],
        },
    )
    license_path = pin(Path("presentation/task-explorer/clinical-cavity/DATA-LICENSE.txt"))
    assert license_path.read_text().startswith(
        "Attribution-NonCommercial-ShareAlike 4.0 International"
    )
    (out / "DATA-LICENSE.txt").write_text(license_path.read_text().rstrip() + "\n")
    page_path = Path(".local/dental-dataset-contract-audit-20260922/sources/toothfairy3.html")
    page = pin(page_path).read_text()
    citations = json.loads(
        re.search(
            r'<script id="cite-apa-data" type="application/json">(.*?)</script>', page, re.S
        ).group(1)
    )
    (out / "NOTICE.md").write_text(
        """# Original dental contract reader assets

Derived by the assistant from retained ToothFairy3 F_018 and F_002 native CBCT,
three unchanged Astra outputs and private research reference labels. Source:
[ToothFairy3 publisher](https://ditto.ing.unimore.it/toothfairy3/) and
[challenge](https://toothfairy3.grand-challenge.org/dataset/).
The publisher identifies CC BY-NC-SA 4.0; its exact standard license is retained
in DATA-LICENSE.txt. The archive metadata instead says CC-BY-SA 4.0. That conflict
is retained, not resolved by this derivation. Local teaching derivatives retain
the publisher's noncommercial and share-alike conditions. Raw data stay local;
no public redistribution or endorsement is claimed.

Changes: source-windowed PNG sections, native binary-mask boundary contours,
numeric label centroids, selected crops, retained scores and reproduced method
diagnostics. CT pixels use the fixed [-400,2500] window. Contours trace binary
level 0.5 with pixel-centre offset 0.5. No spatial resampling, patient-side repair,
mask editing or model inference is performed. Increasing plane axes map right/up;
native voxel indices are explicit because physical laterality is unadjudicated.
F018 archive/viewer arrays are equal but z-affines differ; each output uses the
exact solver/reference pairing. Shape/affine agreement is not clinical orientation.

Input sections contain CT only. Private references and scores are reader reveals.
Diagnostic crops and the selected tooth-16 pulp plane use post-submission reference
information. They are not solver assistance or exhaustive clinical inspection.
The label-swap operation changes displayed IDs only, never their geometry; it is
not a revised submission. The active-class denominator changes under the diagnostic.

The pulp view independently reconstructs distance, intensity and slice gates from
retained float32 CT and tooth-26 envelope. Reference tooth-16 pulp is paired only
for this diagnostic. Final pulp is the saved answer; later closing/cleanup is not
a nested gate. Counts measure reference retention, not precision or a validated fix.

Rebuild with the existing imaging environment:
`python scripts/build_dental_original_assets.py --root . --output FRESH_DIRECTORY`.
The source audit and manifest pin inputs, exact native geometry and PNG round trips.

## Publisher-requested citations

"""
        + citations
        + "\n"
    )
    assets = [
        {
            "file": p.name,
            "sha256": sha(p),
            "bytes": p.stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
        }
        for p in sorted(out.iterdir())
        if p.is_file()
    ]
    manifest = {
        "schema": 1,
        "id": "retained-dental-original-v1",
        "frame": "native-ijk",
        "units": "voxel",
        "license": "CC-BY-NC-SA-4.0",
        "reference_policy": "reader-reference-reveal",
        "sources": pins,
        "assets": assets,
        "checks": {
            "png_pixels_roundtrip": pixels,
            "native_views": len(views),
            "pulp_gate_counts": counts,
            "source_ct_float32_matches_saved": True,
            "native_display_inverse": "exact",
            "contours_within_bounds": True,
            "selected_plane_mask_pixels_retained": True,
            "audit_sha256": sha(root / audit_path),
            "builder_sha256": sha(Path(__file__)),
        },
    }
    dump(out / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "views": len(views),
                "pixels": pixels,
                "gates": counts,
                "files": {p.name: p.stat().st_size for p in out.iterdir()},
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output.resolve())
