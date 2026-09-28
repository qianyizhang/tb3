"""Derive calibrated localized CT views from audited native inputs; no inference."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw
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
    audit_path = Path("groups/longitudinal-reading/presentation/sources/localized-ct-audit.json")
    audit = read(root / audit_path)
    for path, digest in audit["source_pins"].items():
        assert sha(root / path) == digest, path
    sources = {
        str(audit_path): sha(root / audit_path),
        "scripts/build_localized_ct_assets.py": sha(Path(__file__)),
    }
    task = root / ".local/freezes" / audit["task_digest"] / "task"
    job = root / audit["trace"]["job"]
    refs, png_pixels, contour_pixels, jpeg_checks = {}, 0, 0, []

    def png(gray):
        nonlocal png_pixels
        stream = io.BytesIO()
        Image.fromarray(gray).save(stream, format="PNG", optimize=True)
        np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(stream.getvalue()))), gray)
        png_pixels += gray.size
        return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()

    def contour(mask):
        nonlocal contour_pixels
        paths = [p[:, ::-1] - 0.5 for p in find_contours(np.pad(mask, 1), 0.5)]
        recovered = np.zeros(mask.shape, bool)
        for path in paths:
            recovered ^= grid_points_in_poly(mask.shape, path[:, ::-1] - 0.5)
        np.testing.assert_array_equal(mask, recovered)
        contour_pixels += mask.size
        return {"paths": [p.tolist() for p in paths], "pixels": int(mask.sum())}

    for geo in audit["geometry"]:
        visit = geo["visit"]
        image = nib.load(task / f"environment/data/{visit}.nii.gz")
        data = np.asarray(image.dataobj)
        mask = np.asarray(nib.load(task / f"tests/reference/{visit}_instances.nii.gz").dataobj) > 0
        spacing = geo["spacing_mm"]
        i, j, k = geo["native_ijk"]
        shape = geo["shape"]
        views = {}

        def view(
            name,
            axis,
            index,
            bounds,
            flip_v,
            selection,
            *,
            data=data,
            mask=mask,
            views=views,
            spacing=spacing,
            visit=visit,
        ):
            slices = [slice(bounds[2 * d], bounds[2 * d + 1]) for d in range(3)]
            slices[axis] = index

            def plane(a):
                result = a[tuple(slices)].T
                return result[::-1] if flip_v else result

            raw = plane(data)
            gray = np.uint8(np.clip((raw.astype(float) + 150) / 400, 0, 1) * 255)
            remaining = [d for d in range(3) if d != axis]
            h, w = gray.shape
            views[name] = {
                "axis": axis,
                "index": index,
                "bounds": bounds,
                "u_axis": remaining[0],
                "v_axis": remaining[1],
                "flip_v": flip_v,
                "width": w,
                "height": h,
                "extent_mm": [w * spacing[remaining[0]], h * spacing[remaining[1]]],
                "png": png(gray),
                "selection": selection,
                "window": [-150, 250],
            }
            refs[f"{visit}/{name}"] = contour(plane(mask))
            for u, v in [(0, 0), (w - 1, h - 1), (w // 2, h // 2)]:
                q = [0, 0, 0]
                q[axis] = index
                q[remaining[0]] = bounds[remaining[0] * 2] + u
                q[remaining[1]] = (
                    bounds[remaining[1] * 2 + 1] - 1 - v if flip_v else bounds[remaining[1] * 2] + v
                )
                assert gray[v, u] == np.uint8(
                    np.clip((float(data[tuple(q)]) + 150) / 400, 0, 1) * 255
                )

        full = [0, shape[0], 0, shape[1], 0, shape[2]]
        view(
            "input",
            2,
            k,
            full,
            False,
            "Supplied candidate-center plane; full native CT was available",
        )
        crop = (
            [250, 325, 235, 290, 0, shape[2]]
            if visit == "baseline"
            else [248, 323, 193, 248, 0, shape[2]]
        )
        center_panels = []
        for n, z in enumerate(range(k - 2, k + 2)):
            view(
                f"axial-{n}",
                2,
                z,
                crop,
                False,
                "Saved agent crop from steps 13-14; adjacent slice, same projected point",
            )
            raw = data[crop[0] : crop[1], crop[2] : crop[3], z].T
            tile = (
                Image.fromarray(np.uint8(np.clip((raw.astype(float) + 150) / 400, 0, 1) * 255))
                .convert("RGB")
                .resize((375, 275))
            )
            draw = ImageDraw.Draw(tile)
            draw.text((8, 8), f"k={z}", fill="yellow")
            x, y = (i - crop[0]) * 5, (j - crop[2]) * 5
            draw.line((x - 12, y, x - 5, y), fill="red", width=2)
            draw.line((x + 5, y, x + 12, y), fill="red", width=2)
            center_panels.append(tile)
        montage = Image.new("RGB", (1500, 275))
        for n, tile in enumerate(center_panels):
            montage.paste(tile, (n * 375, 0))
        stream = io.BytesIO()
        montage.save(stream, format="JPEG")
        original = job / f"artifacts/app/work/{visit}_center.jpg"
        jpeg_checks.append(
            {
                "file": str(original.relative_to(root)),
                "sha256": sha(original),
                "reconstructed_exact": stream.getvalue() == original.read_bytes(),
            }
        )
        assert jpeg_checks[-1]["reconstructed_exact"]
        mpr_panels = []
        saved_spacing = 0.8222656 if visit == "baseline" else 0.84765625
        for axis, axis_name, coordinate in [(0, "i", i), (1, "j", j)]:
            bounds = [i - 45, i + 46, j - 45, j + 46, k - 18, k + 25]
            for n, offset in enumerate([-5, 0, 5]):
                index = coordinate + offset
                view(
                    f"{axis_name}-{n}",
                    axis,
                    index,
                    bounds,
                    True,
                    "Saved step-11 orthogonal plane; point projection is off-plane except the center panel",
                )
                raw = (
                    data[index, j - 45 : j + 46, k - 18 : k + 25].T[::-1]
                    if axis == 0
                    else data[i - 45 : i + 46, index, k - 18 : k + 25].T[::-1]
                )
                tile = (
                    Image.fromarray(np.uint8(np.clip((raw.astype(float) + 150) / 400, 0, 1) * 255))
                    .convert("RGB")
                    .resize((364, round(43 * 3 / saved_spacing * 4)))
                )
                draw = ImageDraw.Draw(tile)
                draw.text((10, 10), f"{visit} {axis_name}={index}", fill="yellow")
                x, y = 45 * 4, round(24 * 3 / saved_spacing * 4)
                draw.line((x - 12, y, x - 5, y), fill="red", width=2)
                draw.line((x + 5, y, x + 12, y), fill="red", width=2)
                mpr_panels.append(tile)
        montage = Image.new("RGB", (1092, mpr_panels[0].height * 2))
        for n, tile in enumerate(mpr_panels):
            montage.paste(tile, (n % 3 * 364, n // 3 * tile.height))
        stream = io.BytesIO()
        montage.save(stream, format="JPEG")
        original = job / f"artifacts/app/work/{visit}_mpr.jpg"
        jpeg_checks.append(
            {
                "file": str(original.relative_to(root)),
                "sha256": sha(original),
                "reconstructed_exact": stream.getvalue() == original.read_bytes(),
            }
        )
        assert jpeg_checks[-1]["reconstructed_exact"]
        for n, z in enumerate(range(k - 9, k + 14, 2)):
            bounds = (
                [235, 330, 220, 302, 0, shape[2]]
                if visit == "baseline"
                else [235, 330, 180, 262, 0, shape[2]]
            )
            view(
                f"serial-{n}",
                2,
                z,
                bounds,
                False,
                "Saved step-10 detail crop and native slice list; reader replay, not a new solver path",
            )
        dump(out / (visit + ".json"), {**geo, "views": views})
    dump(
        out / "reference.json",
        {
            "views": refs,
            "metrics": audit["attempts"]["saved"]["metrics"],
            "geometry": audit["geometry"],
            "controls": {
                k: {
                    "valid": v["metrics"]["valid"],
                    "acceptance": v["metrics"]["recognition"].get("acceptance_sensitivity"),
                    "detected": v["metrics"]["detection_micro"]["tp"],
                }
                for k, v in audit["verifier_diagnostics"].items()
            },
        },
    )
    dump(
        out / "output.json",
        {
            "judgments": read(job / "artifacts/app/answer/candidate_judgments.json"),
            "events": read(job / "artifacts/app/answer/events.json"),
            "report": (job / "artifacts/app/answer/report.md").read_text(),
            "trace": audit["trace"],
        },
    )
    (out / "DATA-LICENSE.txt").write_text(
        (root / "presentation/task-explorer/longitudinal-ct-revised/DATA-LICENSE.txt").read_text()
    )
    (out / "NOTICE.md").write_text("""# Localized CT candidate teaching views

Longitudinal-CT v3, case 0a09c8844b. Attribution and CC BY-NC 4.0 terms are in DATA-LICENSE.txt. Source and frozen-input arrays, native affines, cached agent arrays and selected reference masks are checked by scripts/audit_localized_ct_evidence.py. The audit preserves the clinical-report versus CT-only information gap. Original evidence and scores remain unchanged.

The original full CT pair and exact R01/R02 centers were solver-visible. Reference label 3, source identity, diagnosis and prior whole-volume results were private. Points were chosen as reference voxels nearest the voxel-index centroid, following an outcome-conditioned selection rule. Two visit instances represent one persistent focus. This is privileged localization, not blind whole-volume discovery.

scripts/build_localized_ct_assets.py builds all native views with the agent's fixed [-150,250] window, clipping then flooring to uint8. Axial images transpose native i/j (L right, P down); orthogonal images transpose and reverse k (S up). Pixel centers use a half-pixel offset inside pixel-edge coordinates. Every view retains native bounds, plane index, affine, physical extent and orientation; visits are independently displayed, not registered. Supplied points stay fixed in native 3D. Signed plane-minus-point offsets distinguish a projection on adjacent sections from a point lying in that section. Cyan solid contours are private source masks, separately revealed. Red crosses are supplied locations, never predictions.

The center crops and six orthogonal planes per visit reproduce the saved rendering scripts. Four complete annotated JPEG montages are independently reconstructed byte-for-byte, including the baseline script's rounded spacing literal. Portable views use exact header spacing instead. Serial detail crops retain the exact step-10 slice lists, twelve per visit. All PNG pixels and contour-grid occupancies round-trip; no interpolated slices or synthetic anatomical geometry are used. Native source pixels are displayed with their physical aspect, not as isotropic resampled anatomy.

The saved agent rejected both candidates and wrote consistent zero masks and empty events. Grade replay retains 0/2 acceptance, 0/2 detection and 0/1 end-to-end links/events. No conditional link or event group is eligible; specificity is undefined. Synthetic verifier diagnostics expose a separate instruction-enforcement gap: rejected judgments plus oracle masks still validate. This does not change the original internally consistent answer. Mechanical validity, label agreement and clinical correctness remain different claims.

Release documentation says radiologists used CT and clinical examination reports. Those reports and independent clinical adjudication are unavailable here. The agent's normal-soft-tissue interpretation is attributed, not adopted. Reader acceptance does not adjudicate malignancy, image-only suitability, segmentation ability after positive acceptance or model performance across cases. No new trial, runtime installation or publication occurred. Exported reader HTML embeds reference material and must not be used as a solver packet.
""")
    checks = {
        "native_views": len(refs),
        "png_pixels_exact": png_pixels,
        "contour_pixels_exact": contour_pixels,
        "saved_jpeg_reconstructions": jpeg_checks,
    }
    files = sorted(out.iterdir())
    manifest = {
        "id": "retained-localized-ct-v1",
        "license": "CC-BY-NC-4.0",
        "label_license": "CC-BY-NC-4.0",
        "frame": "RAS",
        "units": "mm",
        "reference_policy": "reader-reference-reveal",
        "sources": sources,
        "checks": checks,
        "assets": [
            {
                "file": p.name,
                "bytes": p.stat().st_size,
                "sha256": sha(p),
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
            }
            for p in files
        ],
    }
    dump(out / "manifest.json", manifest)
    print(json.dumps(checks))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(Path.cwd(), args.output)


if __name__ == "__main__":
    main()
