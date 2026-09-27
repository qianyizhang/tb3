"""Build dental-v3 native sections, saved transfer and bounded-refinement views."""

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
    audit_path = Path("groups/anatomy-audit/presentation/sources/dental-v3-audit.json")
    audit = read(root / audit_path)
    pins, pixel_count, contour_pixels = {}, 0, 0

    def pin(path):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        if str(relative) in audit["source_pins"]:
            assert audit["source_pins"][str(relative)] == digest, str(relative)
        if str(relative) in audit["local_stage_arrays"]:
            assert audit["local_stage_arrays"][str(relative)] == digest, str(relative)
        pins[str(relative)] = digest
        return root / relative

    def load(path):
        path = pin(path)
        return (
            np.load(path, mmap_mode="r")
            if path.suffix in [".npy", ".npz"]
            else np.asanyarray(nib.load(path).dataobj)
        )

    def png(plane):
        nonlocal pixel_count
        gray = np.uint8(np.clip((plane + 350) / 2550, 0, 1) * 255)
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
    task = Path(".local/dental-f018-reference-v3-astra-medium/task")
    cts = {
        "F018": load(task / "environment/data/ct.nii.gz"),
        "F008": load(task / "environment/reference/ct.nii.gz"),
    }
    gt = load(task / "tests/reference.nii.gz")
    example = load(task / "environment/reference/segmentation.nii.gz")
    labels = read(pin(task / "environment/data/labels.json"))
    models = [r for r in audit["replays"] if r["agent"] == "codex"]
    baseline, assisted = [load(r["answer"]) for r in models]
    work = Path(models[1]["answer"]).parent.parent / "work"
    atlas, before, after = [load(work / n) for n in ["atlas.npy", "teeth.npy", "teeth_final.npy"]]
    views, output_views, reference_views, example_views = {}, {}, {}, {}

    def plane(array, axis, index, bounds):
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
                points = np.argwhere(occupied)
                bounds = np.stack(
                    [np.maximum(points.min(0) - 9, 0), np.minimum(points.max(0) + 10, shape)],
                    axis=1,
                ).tolist()
            else:
                bounds = [[0, shape[0]], [0, shape[1]]]
        image = plane(cts[case], axis, index, bounds)
        views[name] = {
            "case": case,
            "axis": "ijk"[axis],
            "index": index,
            "plane_axes": ["ijk"[a] for a in range(3) if a != axis],
            "bounds_uv": bounds,
            "width": image.shape[1],
            "height": image.shape[0],
            "png": png(image),
            "window": [-350, 2200],
            "selection": selection,
            "display": "First native plane axis increases right; second increases up. Index coordinates, not clinical laterality.",
        }
        output_views[name] = {}
        for key, (array, regions) in layers.items():
            selected = plane(array, axis, index, bounds)
            items = []
            for ident, ids in regions.items():
                mask = np.isin(selected, ids)
                assert mask.sum() == np.isin(np.take(array, index, axis=axis), ids).sum(), (
                    name,
                    key,
                    ident,
                    "crop clipped selected mask",
                )
                items.append({"id": ident, **outline(mask)})
            if key == "reference":
                reference_views[name] = items
            elif key == "example":
                example_views[name] = items
            else:
                output_views[name][key] = items
        return bounds

    add_view(
        "target-input",
        "F018",
        1,
        150,
        {},
        "Full native j=150 section for context; complete volume supplied.",
    )
    add_view(
        "example-input",
        "F008",
        1,
        150,
        {"example": (example, {int(k): [int(k)] for k in labels if k != "0"})},
        "Full native j=150 example section, not an anatomical match to the target section.",
        [[0, 410], [0, 270]],
    )
    full_regions = {int(k): [int(k)] for k in labels if k != "0"}
    add_view(
        "outputs",
        "F018",
        1,
        150,
        {
            "baseline": (baseline, full_regions),
            "assisted": (assisted, full_regions),
            "reference": (gt, full_regions),
        },
        "Both submitted answers and private reference on one complete native section; global metrics use all voxels.",
        [[0, 410], [0, 264]],
    )
    upper = {t: [t, t + 100] for t in TEETH if t < 30}
    shape_bounds = add_view(
        "shape",
        "F018",
        2,
        55,
        {
            "baseline": (baseline, upper),
            "assisted": (assisted, upper),
            "atlas": (atlas, upper),
            "reference": (gt, upper),
        },
        "Selected upper-dentition section; whole-tooth union of mineralized tooth and its pulp. Full-volume identity is 29/29 in both runs.",
    )

    # Reproduce only sampling through the saved composite pull field at k=55.
    # Native tooth-38 replacement is outside this plane; no optimizer is rerun.
    pin(work / "composite2.py")
    af, u, upper_u, lower_u = [
        load(work / n) for n in ["affine.npz", "disp2.npy", "upperdisp1.npy", "lowerdisp1.npy"]
    ]
    cc = np.array(
        np.meshgrid(np.arange(410), np.arange(410), [55], indexing="ij"), dtype=np.float32
    )
    dis = np.stack(
        [ndi.map_coordinates(v, cc / 2, order=1, mode="nearest", prefilter=False) for v in u]
    )
    uc = cc.copy()
    uc[0] -= 65
    alpha = (
        np.clip((cc[0] - 65) / 10, 0, 1)
        * np.clip((344 - cc[0]) / 10, 0, 1)
        * np.clip((229 - cc[1]) / 10, 0, 1)
        * np.clip((114 - cc[2]) / 15, 0, 1)
    )
    for axis in range(3):
        dis[axis] = dis[axis] * (1 - alpha) + alpha * ndi.map_coordinates(
            upper_u[axis], uc, order=1, mode="nearest", prefilter=False
        )
    lc = cc.copy()
    lc[0] -= 55
    lc[1] -= 15
    lc[2] -= 85
    beta = (
        np.clip((cc[0] - 55) / 10, 0, 1)
        * np.clip((354 - cc[0]) / 10, 0, 1)
        * np.clip((cc[1] - 15) / 10, 0, 1)
        * np.clip((309 - cc[1]) / 10, 0, 1)
        * np.clip((cc[2] - 85) / 15, 0, 1)
        * np.clip((253 - cc[2]) / 10, 0, 1)
    )
    for axis in range(3):
        dis[axis] = dis[axis] * (1 - beta) + beta * ndi.map_coordinates(
            lower_u[axis], lc, order=1, mode="nearest", prefilter=False
        )
    coords = np.einsum("ab,bijk->aijk", af["A"], cc) + af["b"][:, None, None, None] + dis
    replayed = ndi.map_coordinates(
        example, coords, order=0, mode="constant", cval=0, prefilter=False
    )[:, :, 0]
    np.testing.assert_array_equal(replayed, atlas[:, :, 55])
    warped = ndi.map_coordinates(
        load(work / "ref.npy"), coords, order=1, mode="constant", cval=-1000, prefilter=False
    )[:, :, 0]
    np.testing.assert_array_equal(warped, load(work / "warpct.npy")[:, :, 55])
    (u0, u1), (v0, v1) = shape_bounds
    registration = {
        "view": "shape",
        "warped_example_png": png(warped[u0:u1, v0:v1].T[::-1]),
        "direction": "target voxel x -> A x + b + blended saved displacement -> F008 sample",
        "label_interpolation": "nearest neighbour; zero outside",
        "ct_interpolation": "linear; -1000 outside",
        "replayed_plane_voxels": int(replayed.size),
        "atlas_plane_exactly_reproduced": True,
        "warped_ct_plane_exactly_reproduced": True,
        "optimization_rerun": False,
        "scope": "Saved final composite map at k=55, not an animation of registration iterations.",
    }

    for label, indices in [(122, [43, 50]), (127, [156, 160, 162])]:
        for index in indices:
            add_view(
                f"pulp-{label}-j{index}",
                "F018",
                1,
                index,
                {
                    "baseline": (baseline, {label: [label]}),
                    "assisted": (assisted, {label: [label]}),
                    "atlas": (atlas, {label: [label]}),
                    "before": (before, {label: [label]}),
                    "after": (after, {label: [label]}),
                    "reference": (gt, {label: [label]}),
                },
                "Post-hoc pulp comparison: 122 has largest per-label Dice gain; 127 is worst remaining assisted pulp. Selected native sections, not exhaustive review.",
            )

    stages = next(
        path for path in audit["local_stage_arrays"] if path.endswith("pulp-127-stages.npz")
    )
    stage = load(stages)
    lo, hi = stage["lo"], stage["hi"]
    sl = tuple(slice(int(a), int(b)) for a, b in zip(lo, hi, strict=True))
    for index in [156, 160]:
        local_index = index - int(lo[1])
        name = f"pulp-eligibility-j{index}"
        image = cts["F018"][sl][:, local_index, :].T[::-1]
        views[name] = {
            "case": "F018",
            "axis": "j",
            "index": index,
            "plane_axes": ["i", "k"],
            "bounds_uv": [[int(lo[0]), int(hi[0])], [int(lo[2]), int(hi[2])]],
            "width": image.shape[1],
            "height": image.shape[0],
            "png": png(image),
            "window": [-350, 2200],
            "selection": "Exact saved pulp-refinement crop for tooth 27; geometric eligibility is a candidate restriction, not a segmentation result.",
            "display": "Native i right, k up; index coordinates, not clinical laterality.",
        }
        output_views[name] = {
            key: [{"id": key, **outline(mask[:, local_index, :].T[::-1])}]
            for key, mask in {
                "before": stage["old"],
                "eligible": stage["old"] | stage["geometry"],
                "extra": stage["extra"],
                "after": stage["after"],
                "atlas": atlas[sl] == 127,
            }.items()
        }
        reference_views[name] = [{"id": 127, **outline((gt[sl][:, local_index, :] == 127).T[::-1])}]

    canal104 = next(r for r in audit["canal_stages"] if r["label"] == 104)
    search_lo, search_hi = np.array(canal104["bounds_ijk_half_open"])
    for index in [201, 204, 207]:
        name = f"canal-104-k{index}"
        add_view(
            name,
            "F018",
            2,
            index,
            {
                "baseline": (baseline, {104: [104]}),
                "assisted": (assisted, {104: [104]}),
                "atlas": (atlas, {104: [104]}),
                "reference": (gt, {104: [104]}),
            },
            "Native k sections with fixed union crop covering full GT, both answers and the actual prior-bounded search box.",
            [[237, 301], [72, 138]],
        )
        output_views[name]["search_box"] = [
            {
                "id": "search-box",
                "pixels": 0,
                "center": None,
                "paths": [
                    [
                        [int(search_lo[0] - 237), int(138 - search_hi[1])],
                        [int(search_hi[0] - 237), int(138 - search_hi[1])],
                        [int(search_hi[0] - 237), int(138 - search_lo[1])],
                        [int(search_lo[0] - 237), int(138 - search_lo[1])],
                        [int(search_lo[0] - 237), int(138 - search_hi[1])],
                    ]
                ],
            }
        ]

    projections, output_projections, reference_projections = {}, {}, {}
    for label in [4, 104]:
        union = (gt == label) | (baseline == label) | (assisted == label) | (atlas == label)
        pos = np.argwhere(union)
        low, high = np.maximum(pos.min(0) - 6, 0), np.minimum(pos.max(0) + 7, gt.shape)
        if label == 104:
            low, high = np.minimum(low, search_lo - 3), np.maximum(high, search_hi + 3)
        for axis in range(3):
            remaining = [a for a in range(3) if a != axis]
            uaxis, vaxis = remaining
            bounds = [[int(low[a]), int(high[a])] for a in remaining]
            (u0, u1), (v0, v1) = bounds
            name = f"canal-{label}-along-{'ijk'[axis]}"
            projections[name] = {
                "case": "F018",
                "label": label,
                "collapsed_axis": "ijk"[axis],
                "plane_axes": ["ijk"[a] for a in remaining],
                "bounds_uv": bounds,
                "width": u1 - u0,
                "height": v1 - v0,
                "selection": "Complete class silhouettes across the full collapsed axis, cropped to the union bounds. Not CT sections; overlapping silhouettes may lie at different depths.",
            }
            output_projections[name] = {}
            for role, array in [
                ("baseline", baseline),
                ("assisted", assisted),
                ("atlas", atlas),
                ("reference", gt),
            ]:
                mask = (array == label).any(axis=axis)[u0:u1, v0:v1].T[::-1]
                item = [{"id": label, **outline(mask)}]
                if role == "reference":
                    reference_projections[name] = item
                else:
                    output_projections[name][role] = item
            if label == 104:
                output_projections[name]["search_box"] = [
                    {
                        "id": "search-box",
                        "pixels": 0,
                        "center": None,
                        "paths": [
                            [
                                [int(search_lo[uaxis] - u0), int(v1 - search_hi[vaxis])],
                                [int(search_hi[uaxis] - u0), int(v1 - search_hi[vaxis])],
                                [int(search_hi[uaxis] - u0), int(v1 - search_lo[vaxis])],
                                [int(search_lo[uaxis] - u0), int(v1 - search_lo[vaxis])],
                                [int(search_lo[uaxis] - u0), int(v1 - search_hi[vaxis])],
                            ]
                        ],
                    }
                ]

    for row in list(views.values()) + list(projections.values()):
        (u0, u1), (v0, v1) = row["bounds_uv"]
        for uindex, vindex in [(u0, v0), (u1 - 1, v1 - 1)]:
            x, y = uindex - u0 + 0.5, v1 - vindex - 0.5
            np.testing.assert_array_equal([u0 + x - 0.5, v1 - y - 0.5], [uindex, vindex])
    dump(
        out / "source.json",
        {
            "schema": 1,
            "views": views,
            "projections": projections,
            "labels": labels,
            "example_annotations": example_views,
        },
    )
    dump(
        out / "output.json",
        {
            "schema": 1,
            "views": output_views,
            "projections": output_projections,
            "registration": registration,
        },
    )
    dump(
        out / "reference.json",
        {
            "schema": 1,
            "views": reference_views,
            "projections": reference_projections,
            "conditions": audit["conditions"],
            "metrics": [
                {
                    "experiment": r["experiment"],
                    "score": r["score"],
                    "seconds": r["seconds"],
                    "usage": r["usage"],
                }
                for r in models
            ],
            "pooled": audit["pooled"],
            "diagnostic_details": audit["diagnostic_details"],
            "pulp_stages": audit["pulp_stages"],
            "canal_stages": audit["canal_stages"],
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
        """# Dental contract v3 reader assets

Local teaching derivatives of ToothFairy3 F_018/F_008 CBCT, permitted F008 example
annotation, two saved Astra-medium answers and private target research labels.
Source: [publisher](https://ditto.ing.unimore.it/toothfairy3/). Publisher
CC BY-NC-SA 4.0 is retained in DATA-LICENSE.txt; conflicting archive CC-BY-SA 4.0
metadata remains unresolved. No endorsement or public-redistribution decision.

Changes: native sections windowed at [-350,2200] HU, union crops, binary contours,
whole-tooth unions, saved-map sampling, bounded-refinement diagnostics and complete
canal silhouettes. Pixel centres round-trip exactly to native indices. Contours
round-trip exactly to binary pixel centres. Native plane axes increase right/up.
No submitted mask, source scan, clinical orientation or original score is changed.
The fixed RPI semantic convention is independent of retained target LPI and example
LPS headers. Physical laterality and original annotation conventions remain under review.

Separate source, output and reference files retain their different roles. Only the
assisted solver saw F008 annotation. Target GT, measurements and GT-selected crops
are reader-only reveals. Whole-volume scores must not be inferred from one section.
Contours absent in a section do not establish absence from the full volume.

The transfer comparison samples the saved composite target-to-example field at
k=55. Both 168,100-voxel atlas and warped-CT planes reproduce exactly. This is a
reader comparison of saved states, not registration optimization or a new trial.
Pulp eligibility reproduces the saved tooth-27 refinement crop. The old mask is
retained; additional voxels require tooth depth, proximity, intensity and contrast.
Eligibility is a search restriction, not a final mask or diagnosed tissue.
Canal 104's actual crop is prior bounds plus four voxels. None of its 355 target-GT
voxels lie inside that crop. Its six-voxel distance diagnostic is separate from the
canal algorithm. Geometry establishes this operation's reach, not a unique cause
of the earlier registration error or clinical adjudication of GT.

Canal projections collapse a complete axis using binary occupancy; they are not
CT sections, surfaces or voxel overlaps. Apparent silhouette overlap may arise at
different depths. Three projections and selected native slices must be labeled.
Main-canal 4 demonstrates improved overlap with worse HD95; no single measure
certifies its shape. Restoration/treated-pulp convention benefits remain untested.

Rebuild with the existing imaging environment:
`python scripts/build_dental_v3_assets.py --root . --output FRESH_DIRECTORY`.
The manifest pins all inputs, derivation code and assets. No solver or optimizer runs.

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
    checks = {
        "native_views": len(views),
        "complete_class_projections": len(projections),
        "png_pixels_roundtrip": pixel_count,
        "contour_pixels_roundtrip": contour_pixels,
        "native_display_inverse": "exact",
        "selected_plane_mask_pixels_retained": True,
        "registration": registration | {"warped_example_png": "in output.json"},
        "audit_sha256": sha(root / audit_path),
        "builder_sha256": sha(Path(__file__)),
    }
    dump(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-dental-v3-v1",
            "frame": "native-ijk",
            "units": "voxel",
            "license": "CC-BY-NC-SA-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": pins,
            "assets": assets,
            "checks": checks,
        },
    )
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output.resolve())
