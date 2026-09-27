"""Derive native dental-v2 reader views from audited arrays and saved intermediates."""

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
from skimage.measure import find_contours, grid_points_in_poly

TEETH = [q * 10 + n for q in range(1, 5) for n in range(1, 9)]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, separators=(",", ":"), allow_nan=False) + "\n")


def build(root, out):
    out.mkdir(parents=True, exist_ok=False)
    audit_path = Path("groups/anatomy-audit/presentation/sources/dental-v2-audit.json")
    audit = read(root / audit_path)
    pins, pixel_count, contour_pixels = {}, 0, 0

    def pin(path):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        if str(relative) in audit["source_pins"]:
            assert audit["source_pins"][str(relative)] == digest, str(relative)
        pins[str(relative)] = digest
        return root / relative

    def load(path):
        path = pin(path)
        return (
            np.load(path, mmap_mode="r")
            if path.suffix == ".npy"
            else np.asanyarray(nib.load(path).dataobj)
        )

    def png(plane):
        nonlocal pixel_count
        gray = np.uint8(np.clip((plane + 400) / 3620, 0, 1) * 255)
        stream = io.BytesIO()
        Image.fromarray(gray).save(stream, format="PNG", optimize=True)
        raw = stream.getvalue()
        np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(raw))), gray)
        pixel_count += gray.size
        return "data:image/png;base64," + base64.b64encode(raw).decode()

    def outline(mask):
        nonlocal contour_pixels
        paths = [
            p[:, ::-1] - 0.5 for p in find_contours(np.pad(mask, 1), 0.5, fully_connected="low")
        ]
        recovered = np.zeros(mask.shape, bool)
        for p in paths:
            assert np.all(p >= 0) and np.all(p <= [mask.shape[1], mask.shape[0]])
            recovered ^= grid_points_in_poly(mask.shape, p[:, ::-1] - 0.5)
        np.testing.assert_array_equal(recovered, mask)
        contour_pixels += mask.size
        pos = np.argwhere(mask)
        return {
            "paths": [p.tolist() for p in paths],
            "pixels": int(mask.sum()),
            "center": (pos.mean(0)[::-1] + 0.5).tolist() if len(pos) else None,
        }

    pin(audit_path)
    pin(Path(__file__))
    task = Path(".local/dental-f002-reference-v2-astra-medium/task")
    cts = {
        "F002": load(task / "environment/data/ct.nii.gz"),
        "F008": load(task / "environment/reference/ct.nii.gz"),
    }
    gt = load(task / "tests/reference.nii.gz")
    example = load(task / "environment/reference/segmentation.nii.gz")
    labels = read(pin(task / "environment/data/labels.json"))
    model_records = [r for r in audit["replays"] if r["agent"] == "codex"]
    baseline, assisted = [load(r["answer"]) for r in model_records]
    work = Path(model_records[1]["answer"]).parent.parent / "work"
    atlas = load(work / "atlas2.npy")
    before = load(work / "teeth_pulp.npy")
    after = load(work / "teeth_pulp_final.npy")
    views, output_views, reference_views, example_views = {}, {}, {}, {}

    def project(array, axis, index, bounds):
        (u0, u1), (v0, v1) = bounds
        return np.take(array, index, axis=axis)[u0:u1, v0:v1].T[::-1]

    def add_view(name, case, axis, index, layers, selection, bounds=None):
        shape = np.take(cts[case], index, axis=axis).shape
        occupied = np.zeros(shape, bool)
        for array, regions in layers.values():
            ids = [i for values in regions.values() for i in values]
            occupied |= np.isin(np.take(array, index, axis=axis), ids)
        if bounds is None:
            if occupied.any():
                pos = np.argwhere(occupied)
                bounds = np.stack(
                    [np.maximum(pos.min(0) - 8, 0), np.minimum(pos.max(0) + 9, shape)], axis=1
                ).tolist()
            else:
                bounds = [[0, shape[0]], [0, shape[1]]]
        image = project(cts[case], axis, index, bounds)
        views[name] = {
            "case": case,
            "axis": "ijk"[axis],
            "index": index,
            "plane_axes": ["ijk"[a] for a in range(3) if a != axis],
            "bounds_uv": bounds,
            "width": image.shape[1],
            "height": image.shape[0],
            "png": png(image),
            "window": [-400, 3220],
            "selection": selection,
            "display": "First native plane axis increases right; second increases up; coordinates, not clinical laterality.",
        }
        output_views[name] = {}
        for key, (array, regions) in layers.items():
            plane = project(array, axis, index, bounds)
            items = []
            for ident, ids in regions.items():
                mask = np.isin(plane, ids)
                assert mask.sum() == np.isin(np.take(array, index, axis=axis), ids).sum(), (
                    name,
                    key,
                    ident,
                    "crop clipped a selected mask",
                )
                items.append({"id": ident, **outline(mask)})
            if key == "reference":
                reference_views[name] = items
            elif key == "example":
                example_views[name] = items
            else:
                output_views[name][key] = items
        return bounds

    upper = {t: [t, t + 100] for t in TEETH if t < 30}
    add_view(
        "target-input",
        "F002",
        1,
        150,
        {},
        "Full native j=150 section; complete target volume supplied.",
    )
    add_view(
        "example-input",
        "F008",
        1,
        150,
        {"example": (example, {int(k): [int(k)] for k in labels if k != "0"})},
        "Same native section index for context only, not an anatomical correspondence.",
        bounds=[[0, 410], [0, 270]],
    )
    identity_bounds = add_view(
        "identity",
        "F002",
        2,
        55,
        {
            "baseline": (baseline, upper),
            "assisted": (assisted, upper),
            "atlas": (atlas, upper),
            "reference": (gt, upper),
        },
        "Native k=55 upper dentition; reader crop includes every selected output, prior and reference label. Tooth+pulp unions.",
    )

    # Reconstruct only the saved target-to-example sampling operation. No affine
    # or deformable optimization is rerun. Confirm the entire label plane exactly.
    pin(work / "register2.py")
    displacement = load(work / "disp_v2_2.npy")
    grid = np.array(
        np.meshgrid(np.arange(410), np.arange(410), [55], indexing="ij"), dtype=np.float32
    )
    coords = np.array(
        [
            grid[q] + ndi.map_coordinates(displacement[q], grid / 2, order=1, mode="nearest") * 2
            for q in range(3)
        ]
    )
    labels_replayed = ndi.map_coordinates(example, coords, order=0, mode="constant")[:, :, 0]
    np.testing.assert_array_equal(labels_replayed, atlas[:, :, 55])
    warped_ct = ndi.map_coordinates(cts["F008"], coords, order=1, mode="constant")[:, :, 0]
    (u0, u1), (v0, v1) = identity_bounds
    registration = {
        "view": "identity",
        "warped_example_png": png(warped_ct[u0:u1, v0:v1].T[::-1]),
        "direction": "target voxel -> saved displacement -> example sample",
        "label_interpolation": "nearest neighbour, constant outside",
        "ct_interpolation": "linear, reader-only display",
        "replayed_plane_voxels": int(labels_replayed.size),
        "atlas_plane_exactly_reproduced": True,
        "optimization_rerun": False,
    }

    fine = audit["fine_diagnostics"]
    for row in fine["supplement.json"]["slice_choices"]:
        case, lab, axis, index = row["case"], row["label"], row["axis"], row["index"]
        if case == "F008":
            layers = {"example": (example, {lab: [lab]})}
        else:
            layers = {
                "baseline": (baseline, {lab: [lab]}),
                "assisted": (assisted, {lab: [lab]}),
                "reference": (gt, {lab: [lab]}),
            }
        add_view(
            f"detail-{case}-{lab}",
            case,
            axis,
            index,
            layers,
            "Retained diagnostic maximum reference-area section; crop extends to include both outputs. Selected after submission, not exhaustive inspection.",
        )

    for j in [145, 205]:
        regions = {lab: [lab] for lab in [3, 4, 103, 104, 105]}
        add_view(
            f"canals-{j}",
            "F002",
            1,
            j,
            {
                "baseline": (baseline, regions),
                "assisted": (assisted, regions),
                "atlas": (atlas, regions),
                "reference": (gt, regions),
            },
            "Two native j sections expose different canal extents; scores cover whole volumes.",
            bounds=[[50, 365], [70, 260]],
        )

    # A consequential saved exclusion, independently reconstructed in its exact
    # original crop. Private reference is used only for reader-plane selection.
    priors = load(work / "tooth_priors.npy")
    whole = (before == 14) | (before == 114)
    pos = np.array(np.where(whole))
    lo, hi = np.maximum(pos.min(1) - 7, 0), np.minimum(pos.max(1) + 8, before.shape)
    sl = tuple(slice(int(a), int(b)) for a, b in zip(lo, hi, strict=True))
    ap = (atlas == 14) | (atlas == 114)
    shift = np.array(ndi.center_of_mass(priors == 14)) - np.array(ndi.center_of_mass(ap))
    shift[2] = 0
    prior = ndi.shift((atlas[sl] == 114).astype(np.uint8), shift, order=0) > 0
    allowed = ndi.distance_transform_edt(~prior) <= 3.5
    removed = (before[sl] == 114) & ~allowed
    np.testing.assert_array_equal(removed, (before[sl] == 114) & (after[sl] != 114))
    truth = gt[sl] == 114
    expected = next(r for r in fine["prior-clipping.json"] if r["tooth"] == 14)
    assert int((removed & truth).sum()) == expected["removed_true_pulp_voxels"] == 440
    axis = 1
    index = int((removed & truth).sum((0, 2)).argmax())
    bounds = [[int(lo[0]), int(hi[0])], [int(lo[2]), int(hi[2])]]
    image = cts["F002"][sl][:, index, :].T[::-1]
    views["prior-clipping"] = {
        "case": "F002",
        "axis": "j",
        "index": int(lo[1]) + index,
        "plane_axes": ["i", "k"],
        "bounds_uv": bounds,
        "width": image.shape[1],
        "height": image.shape[0],
        "png": png(image),
        "window": [-400, 3220],
        "selection": "Tooth 14: native j section with most correctly placed pulp voxels deleted by the saved prior rule.",
        "display": "Native i right, k up; original solver crop.",
    }
    output_views["prior-clipping"] = {
        name: [{"id": name, **outline(mask[:, index, :].T[::-1])}]
        for name, mask in {
            "before": before[sl] == 114,
            "after": after[sl] == 114,
            "prior": prior,
            "allowed": allowed,
            "removed": removed,
        }.items()
    }
    reference_views["prior-clipping"] = [{"id": 114, **outline(truth[:, index, :].T[::-1])}]
    clipping = {
        **expected,
        "before_true_overlap": int(((before[sl] == 114) & truth).sum()),
        "after_true_overlap": int(((after[sl] == 114) & truth).sum()),
        "crop_ijk": [lo.tolist(), hi.tolist()],
        "private_reference_used_for_plane_selection": True,
    }
    assert clipping["before_true_overlap"] == 443 and clipping["after_true_overlap"] == 3

    for row in views.values():
        (u0, u1), (v0, v1) = row["bounds_uv"]
        for u, v in [(u0, v0), (u1 - 1, v1 - 1)]:
            x, y = u - u0 + 0.5, v1 - v - 0.5
            np.testing.assert_array_equal([u0 + x - 0.5, v1 - y - 0.5], [u, v])
    dump(
        out / "source.json",
        {"schema": 1, "views": views, "labels": labels, "example_annotations": example_views},
    )
    dump(out / "output.json", {"schema": 1, "views": output_views, "registration": registration})
    dump(
        out / "reference.json",
        {
            "schema": 1,
            "views": reference_views,
            "conditions": audit["conditions"],
            "metrics": [
                {
                    "experiment": r["experiment"],
                    "score": r["score"],
                    "seconds": r["seconds"],
                    "usage": r["usage"],
                }
                for r in model_records
            ],
            "fine_diagnostics": fine,
            "clipping": clipping,
        },
    )
    license_path = pin(Path("presentation/task-explorer/dental-original/DATA-LICENSE.txt"))
    (out / "DATA-LICENSE.txt").write_text(license_path.read_text())
    page = pin(
        Path(".local/dental-dataset-contract-audit-20260922/sources/toothfairy3.html")
    ).read_text()
    citations = json.loads(
        re.search(
            r'<script id="cite-apa-data" type="application/json">(.*?)</script>', page, re.S
        ).group(1)
    )
    (out / "NOTICE.md").write_text(
        """# Dental contract v2 reader assets

Local teaching derivatives of ToothFairy3 F_002 and F_008 CBCT, the authorized
F008 example annotation, two unchanged Astra-medium outputs and private target
research labels. Source: [publisher](https://ditto.ing.unimore.it/toothfairy3/).
Publisher CC BY-NC-SA 4.0 is retained in DATA-LICENSE.txt. Archive CC-BY-SA 4.0
metadata conflicts with that notice; this derivation does not resolve the conflict
or authorize public redistribution. Raw data remain local. No endorsement is implied.

Changes: native sections windowed at [-400,3220], binary contours, selected crops,
saved-label union views, saved-displacement sampling, and one reconstructed prior
exclusion. All mask contours round-trip exactly to their binary pixel centres.
Pixel centres map invertibly to native indices; native plane axes increase right/up.
No native scan, submitted mask, clinical orientation or score is changed.
RPI specifies semantic names in this task; the retained LPS header does not
establish acquisition laterality. Source arrays and header geometry are verified.

The example annotation was visible only in the assisted condition. Target masks,
scores and reference-selected detail views are reader-only reveals. Separate JSON
files preserve these roles; reference data must be explicitly revealed by the story.
Whole-tooth contours union tooth tissue with its paired pulp; other views retain
exclusive labels. Omitted contours mean absent in that section, not the full volume.
Pulp contents shown as bright are observed intensities, not diagnosed materials.

Registration resamples only a selected plane with the saved target-to-example
field. Its nearest-neighbour labels reproduce the saved atlas exactly. The linear
CT overlay is a reader illustration of that map, not a new registration result.
Pulp clipping reconstructs the saved 3.5-voxel (1.05 mm) exclusion in its original
crop. It removes 440/443 correctly placed tooth-14 pulp voxels, leaving 3, while
also removing false positives. Counts are reference agreement, not clinical truth.
The selected section maximizes this measured loss; whole-volume counts and original
scores remain separately available. No optimization or solver is executed.

Rebuild using the existing imaging environment:
`python scripts/build_dental_v2_assets.py --root . --output FRESH_DIRECTORY`.
The manifest pins source evidence, derivation code and every asset.

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
    for path, digest in pins.items():
        assert sha(root / path) == digest, path
    dump(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-dental-v2-v1",
            "frame": "native-ijk",
            "units": "voxel",
            "license": "CC-BY-NC-SA-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": pins,
            "assets": assets,
            "checks": {
                "native_views": len(views),
                "png_pixels_roundtrip": pixel_count,
                "contour_pixels_roundtrip": contour_pixels,
                "native_display_inverse": "exact",
                "selected_plane_mask_pixels_retained": True,
                "atlas_plane_exact_replay": registration["replayed_plane_voxels"],
                "prior_clipping_exact_replay": clipping,
                "audit_sha256": sha(root / audit_path),
                "builder_sha256": sha(Path(__file__)),
            },
        },
    )
    print(
        json.dumps(
            {
                "views": len(views),
                "png_pixels": pixel_count,
                "contour_pixels": contour_pixels,
                "clipping": clipping,
                "files": {p.name: p.stat().st_size for p in out.iterdir()},
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output.resolve())
