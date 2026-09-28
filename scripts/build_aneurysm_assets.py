"""Derive BR-016 native MRA planes, projections and separately revealed weak regions."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from skimage.measure import find_contours, grid_points_in_poly


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def build(root, out):
    out.mkdir(parents=True, exist_ok=False)
    audit_path = Path("groups/lesion-localization/presentation/sources/aneurysm-audit.json")
    audit = read(root / audit_path)
    sources = {}
    png_pixels = contour_pixels = 0

    def pin(path):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        if str(relative) in audit["source_pins"]:
            assert digest == audit["source_pins"][str(relative)], relative
        sources[str(relative)] = digest
        return root / relative

    def png(gray):
        nonlocal png_pixels
        stream = io.BytesIO()
        Image.fromarray(gray).save(stream, format="PNG", optimize=True)
        raw = stream.getvalue()
        np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(raw))), gray)
        png_pixels += gray.size
        return "data:image/png;base64," + base64.b64encode(raw).decode()

    def contour(mask):
        nonlocal contour_pixels
        paths = [p[:, ::-1] - 0.5 for p in find_contours(np.pad(mask, 1), 0.5)]
        recovered = np.zeros(mask.shape, bool)
        for p in paths:
            recovered ^= grid_points_in_poly(mask.shape, p[:, ::-1] - 0.5)
        np.testing.assert_array_equal(mask, recovered)
        contour_pixels += mask.size
        return {"paths": [p.tolist() for p in paths], "pixels": int(mask.sum())}

    pin(audit_path)
    pin(Path(__file__))
    cases, references, outputs = {}, {}, {}

    def case_assets(case_id, row):
        meta = row["metadata"]
        base = Path("runs/br016-aneurysm/build") / f"aneurysm-{case_id}"
        arrays = {
            name: np.load(pin(base / f"{name}.npz"))["volume"] for name in ["brain", "original"]
        }
        pin(base / "volume.json")
        shape = meta["shape"]
        spacing = meta["spacing_mm"]
        full = [0, shape[0], 0, shape[1], 0, shape[2]]
        mask = np.zeros(shape, bool)
        for region in row["reference_regions"]:
            mask |= np.asanyarray(nib.load(pin(region["source"])).dataobj) > 0
        key = read(pin(Path(row["task"]) / "tests/expected.json"))
        accepted = np.zeros(shape, bool)
        for region in key["regions"]:
            points = np.array([list(map(int, p.split(","))) for p in region["accepted_voxels"]])
            accepted[tuple(points.T)] = True
        views = {}

        def view(
            name,
            axis,
            index=None,
            bounds=None,
            volume="brain",
            high=None,
            selection="Full scan; no target selected",
        ):
            bounds = full.copy() if bounds is None else bounds
            high = meta["display_high"] if high is None else high
            slices = [slice(bounds[2 * d], bounds[2 * d + 1]) for d in range(3)]
            if index is not None:
                assert bounds[axis * 2] <= index < bounds[axis * 2 + 1]
                slices[axis] = index

            def plane(a):
                data = a[tuple(slices)]
                return (data.max(axis=axis) if index is None else data).T[::-1]

            image = np.clip(plane(arrays[volume]) / high * 255, 0, 255).astype(np.uint8)
            remaining = [d for d in range(3) if d != axis]
            width, height = image.shape[1], image.shape[0]
            views[name] = {
                "axis": axis,
                "index": index,
                "bounds": bounds,
                "kind": "mip" if index is None else "slice",
                "volume": volume,
                "window": [0, high],
                "width": width,
                "height": height,
                "u_axis": remaining[0],
                "v_axis": remaining[1],
                "extent_mm": [width * spacing[remaining[0]], height * spacing[remaining[1]]],
                "png": png(image),
                "selection": selection,
            }
            # Image is already vertically flipped; references share exactly that pixel grid.
            references[f"{case_id}/{name}"] = {
                "weak": contour(plane(mask)),
                "accepted": contour(plane(accepted)),
            }
            if index is not None:
                # Check index-to-image and inverse at two corners and the centre.
                for u, v in [(0, 0), (width - 1, height - 1), (width // 2, height // 2)]:
                    q = [0, 0, 0]
                    q[axis] = index
                    q[remaining[0]] = bounds[2 * remaining[0]] + u
                    q[remaining[1]] = bounds[2 * remaining[1] + 1] - 1 - v
                    raw_value = arrays[volume][tuple(q)]
                    expected = np.uint8(np.clip(raw_value / high * 255, 0, 255))
                    assert image[v, u] == expected

        for axis in range(3):
            view(f"overview-{axis}", axis)
        view("original", 2, volume="original")
        if case_id == "n02":
            for i, (low, high) in enumerate(
                zip(
                    np.linspace(0, shape[2], 13, dtype=int)[:-1],
                    np.linspace(0, shape[2], 13, dtype=int)[1:],
                    strict=True,
                )
            ):
                bounds = full.copy()
                bounds[4:6] = [int(low), int(high)]
                view(
                    f"slab-{i}",
                    2,
                    bounds=bounds,
                    selection="Twelve equal axial slabs cover the full scan; supplied policy, no lesion selection",
                )
            focus = [295, 355, 180, 250, 82, 112]
            for axis, index in [(0, 312), (1, 214), (2, 94)]:
                view(
                    f"candidate-{axis}",
                    axis,
                    index,
                    focus,
                    high=1000,
                    selection="Reconstruction of selected native sections within the agent's step-14 candidate crop; not the full montage",
                )
            for index in [84, 88, 92, 94, 96, 100, 104]:
                view(
                    f"depth-{index}",
                    2,
                    index,
                    focus,
                    high=1000,
                    selection="Seven selected original sections from the agent's step-14 axial montage; discrete, no interpolation",
                )
            for axis, index in enumerate([312, 213, 94]):
                view(
                    f"point-{axis}",
                    axis,
                    index,
                    focus,
                    high=1000,
                    selection="Post-result reader sections through the submitted point; no location was supplied to the solver",
                )
        elif case_id == "n01":
            focus = [134, 199, 241, 306, 66, 103]
            for axis, index in enumerate([166, 273, 84]):
                view(
                    f"reference-{axis}",
                    axis,
                    index,
                    focus,
                    high=400,
                    selection="Post-result reference-centred reader crop; not solver input or a claimed agent close-up",
                )
            for i, center in enumerate([[192, 248, 74], [166, 309, 100]]):
                bounds = [170, 215, 225, 270, 60, 85] if i == 0 else [150, 185, 292, 328, 90, 112]
                view(
                    f"final-candidate-{i}",
                    2,
                    center[2],
                    bounds,
                    high=700 if i == 0 else 600,
                    selection="Selected axial section reconstructed from the final step-28 candidate montages; viewed at step 29",
                )
        else:
            for axis in range(3):
                view(
                    f"centre-{axis}",
                    axis,
                    (shape[axis] - 1) // 2,
                    selection="Fixed volume-centre section; no lesion location or diagnostic claim",
                )
        cases[case_id] = {
            "shape": shape,
            "spacing_mm": spacing,
            "affine": meta["affine_ijk_to_RAS_mm"],
            "axes": meta["axes"],
            "display_high": meta["display_high"],
            "views": views,
        }
        dump(out / f"{case_id}.json", cases[case_id])
        replay = next(
            r
            for r in audit["replays"]
            if r["task"] == f"aneurysm-{case_id}-v2" and r["phase"] == "sol-xhigh"
        )
        outputs[case_id] = {"answer": replay["answer"], "trace": audit["traces"][case_id]}

    for case_id, row in audit["cases"].items():
        case_assets(case_id, row)
    dump(out / "output.json", {"schema": 1, "cases": outputs})
    dump(
        out / "reference.json",
        {
            "schema": 1,
            "views": references,
            "cases": {
                key: {
                    "regions": row["reference_regions"],
                    "subject": row["subject"],
                    "group": row["group"],
                }
                for key, row in audit["cases"].items()
            },
            "replays": audit["replays"],
            "controls": audit["controls"],
            "n02_point_to_centroid_mm": audit["cases"]["n02"]["point_to_reference_centroid_mm"],
            "n02_inside_source_region": audit["cases"]["n02"]["submitted_point_inside_source_mask"],
        },
    )
    license_path = pin("runs/br016-aneurysm/source/dataset_description.json")
    (out / "DATA-LICENSE.txt").write_text(
        "Source dataset License field: CC0\nOpenNeuro ds003949; dataset description retained below.\nCC0 1.0 Universal: https://creativecommons.org/publicdomain/zero/1.0/\n\n"
        + license_path.read_text()
    )
    (out / "NOTICE.md").write_text("""# Native aneurysm localization teaching views

Source: Lausanne TOF-MRA cohort, OpenNeuro ds003949, CC0.
Credit: Di Noto et al., *Towards automated brain aneurysm detection in TOF-MRA:
open data, weak labels, and anatomical knowledge*, Neuroinformatics (2022),
https://doi.org/10.1007/s12021-022-09597-0 .
Pinned dataset tree: 8921f7b9beab038e1a314f9aab84d7358c4568c5.
Exact selected image/mask bytes, original task freezes, receipts and trajectories
are verified in the group's aneurysm-audit.json. No inference runs here.

The solver received full native original/skull-stripped MRA volumes, metadata,
three full-volume MIPs and twelve equal axial slabs, plus a slice/MIP helper.
Source case identifiers, weak lesion masks and acceptance regions were not in
the image archive. The public dataset was identified in a supplied source notice,
and network lookup was allowed. N03 used it; retain that separate evidence basis.

PNG images preserve exactly the windowed uint8 values. Arrays are transposed and
vertically flipped, so horizontal follows the first remaining native axis and
vertical points upward along the second: +i Right, +j Anterior, +k Superior.
Native anisotropic spacing determines displayed physical aspect. There is no
resampling, registration or radiological left-right reversal. Bounds are half-open.
Pixel centre (u+.5,v+.5) maps to the stated original [i,j,k]. MIPs collapse depth;
they are not single sections and do not establish localization by themselves.

N02 candidate sections reconstruct a selected subset of step 14, using the exact
crop and display window; they are not the original full montage. The depth series
uses actual slices. Point-centred sections are post-result reader views. N01
reference-centred crops are post-hoc teaching aids; its final candidate sections
are selected from step 28 and were viewed at step 29. N03 centre sections are
neutral display choices, not evidence of an exhaustive negative scan review.

The reference file is separate and revealed explicitly. It contains released
weak regions and frozen +1 mm Euclidean voxel-centre acceptance regions, not
clinical sac boundaries. Rasterizing all contour rings reconstructs each binary
plane exactly. The submitted point is cyan; weak region green dashed; acceptance
region gold dotted. The source weak sphere's centre is not the required answer.
No point or region is interpolated between slices. No mesh is reconstructed.

Nine saved grades replay exactly, including three model answers, three oracle
answers and three invalid-schema no-ops. The earlier missing-verifier setup failure
remains an infrastructure observation. Empty valid negative and {} are distinct.
One point per reference region is matched at most once; extras and misses fail.

These three selected cases provide workflow observations. They do not measure
population accuracy, causal method benefit, lesion contour quality or clinical
diagnostic validity. Source completeness, independent clinical review and unknown
training overlap remain qualifications. Raw frozen evidence is unchanged.
""")
    names = [
        "n01.json",
        "n02.json",
        "n03.json",
        "output.json",
        "reference.json",
        "NOTICE.md",
        "DATA-LICENSE.txt",
    ]
    assert all(sha(root / p) == digest for p, digest in sources.items())
    dump(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-aneurysm-localization-v1",
            "frame": "native-ijk",
            "units": "voxel",
            "license": "CC0-1.0",
            "label_license": "CC0-1.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": {
                "png_pixels_roundtrip": png_pixels,
                "contour_pixels_roundtrip": contour_pixels,
                "views": sum(len(c["views"]) for c in cases.values()),
                "source_audit_sha256": sha(root / audit_path),
                "builder_sha256": sha(Path(__file__)),
            },
            "assets": [
                {
                    "file": name,
                    "sha256": sha(out / name),
                    "bytes": (out / name).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if name == "reference.json"
                    else "illustration",
                }
                for name in names
            ],
        },
    )
    print(
        json.dumps(
            {
                "out": str(out),
                "png_pixels": png_pixels,
                "contour_pixels": contour_pixels,
                "sizes": {name: (out / name).stat().st_size for name in names},
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.out.resolve())
