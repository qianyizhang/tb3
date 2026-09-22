"""Build a local reader-only review from four pinned Longitudinal-CT v3 cases.

Uses existing numpy/nibabel/Pillow/scipy; never downloads or runs a model.
"""

import argparse
import base64
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage


COLORS = {1: "#45d5e8", 2: "#ffc85a", 3: "#b394ff", 4: "#ff8276", 5: "#6cdd9a", 6: "#f791d2"}
CASES = [
    dict(
        id="0a09c8844b",
        title="Abdominal lymph nodes",
        short="A · Abdominal nodes",
        window=0,
        field=145,
        foci=[
            ("Upper targets B1 / B2", 117, 111, [234, 271], [262, 236]),
            ("Lower target B4", 103, 111, [270, 258], [262, 236]),
            ("Separate target B3", 213, 216, [304, 263], [302, 221]),
        ],
        summary="Three baseline lesions converge on one follow-up lesion: B1 + B2 + B4 → F4. B3 remains a separate lesion.",
        caution="A one-to-one matcher cannot express this reference. The three MERGING rows repeat F4's volume; count that follow-up region once.",
        status="Candidate for correspondence review",
    ),
    dict(
        id="02522a2b27",
        title="Axillary lymph nodes",
        short="B · Axillary nodes",
        window=0,
        field=95,
        foci=[
            ("Axillary cluster", 192, 192, [127, 239], [122, 219]),
            ("Persistent skin / soft-tissue target B1", 160, 161, [101, 195], [111, 188]),
        ],
        summary="B1–B4 have persistent identities; F5 and F6 are newly appearing labels. Persistence does not imply stable size.",
        caution="Small new labels sit near larger existing lesions. These selected views disclose the search region; they are explanatory views, not an unassisted detection task.",
        status="Candidate for correspondence; new-lesion detection is an extension",
    ),
    dict(
        id="06eb133bbf",
        title="Lung targets",
        short="C · Lung targets",
        window=1,
        field=105,
        foci=[
            ("Lung target B1", 85, 86, [317, 353], [314, 344]),
            ("Lung target B2", 47, 48, [387, 359], [387, 358]),
        ],
        summary="The source labels both baseline lesions DISAPPEARING; the follow-up reference mask is empty.",
        caution="The follow-up view uses the source's registration-propagated location, not a manual follow-up target. An empty mask and one slice do not prove biological disappearance; check coverage and adjacent anatomy before hard scoring.",
        status="Disappearance reference; coverage review still required",
    ),
    dict(
        id="0777d5c17d",
        title="Facial target: hold for review",
        short="D · Facial target ⚑",
        window=1,
        field=100,
        foci=[("Facial target B1", 75, 188, [253, 52], [279, 91])],
        summary="The source labels B1 DISAPPEARING, but its baseline mask lies in the visibly defaced anterior face region.",
        caution="All 92 labeled baseline voxels have values from −413 to −321 HU. Usable original lesion appearance is questionable after defacing. Hold this case out pending image/reference adjudication; this is not an agent failure.",
        status="Review exclusion: image/reference concern",
    ),
]


def png_url(array):
    stream = io.BytesIO()
    Image.fromarray(array).save(stream, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()


def rgb(color):
    return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))


def image_slice(data, k, window):
    lo, hi = [(-160, 240), (-1000, 400)][window]
    return np.rint(np.clip((data[:, :, k].T.astype(float) - lo) / (hi - lo), 0, 1) * 255).astype(
        np.uint8
    )


def mask_slice(mask, k):
    plane = mask[:, :, k].T
    rgba = np.zeros((*plane.shape, 4), dtype=np.uint8)
    for label in np.unique(plane):
        if label == 0:
            continue
        selected = plane == label
        color = rgb(COLORS[int(label)])
        rgba[selected] = (*color, 74)
        edge = selected & ~ndimage.binary_erosion(selected)
        rgba[edge] = (*color, 255)
    return rgba


def view_snapshot(ct, mask, k, center, spacing, field, window, overlay):
    raw = Image.fromarray(image_slice(ct, k, window)).convert("RGBA")
    if overlay:
        raw = Image.alpha_composite(raw, Image.fromarray(mask_slice(mask, k)))
    half = field / spacing / 2
    box = (
        round(center[0] - half),
        round(center[1] - half),
        round(center[0] + half),
        round(center[1] + half),
    )
    return raw.crop(box).resize((440, 440), Image.Resampling.NEAREST).convert("RGB")


def font(size):
    for name in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True, help="Extracted archive root")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = dict(cases=[], colors=COLORS)
    audit = dict(
        dataset="Longitudinal-CT",
        release="v3",
        record="https://fdat.uni-tuebingen.de/records/qe950-g4h94",
        license="CC BY-NC 4.0",
        review_date="2026-09-22",
        model_runs=0,
        cases=[],
        files=[],
    )
    all_rows = []
    missing_uncertainty = []
    for path in sorted((args.data_root / "inputsTr").glob("*.csv")):
        rows = list(csv.DictReader(path.open()))
        all_rows.extend(rows)
        if rows and "linking_unclear" not in rows[0]:
            missing_uncertainty.append(dict(id=path.stem, rows=len(rows)))
    audit["metadata_screen"] = dict(
        patient_csvs=len(list((args.data_root / "inputsTr").glob("*.csv"))),
        row_events=dict(Counter(r["topology_class"] for r in all_rows)),
        uncertainty=dict(Counter(r.get("linking_unclear", "MISSING") for r in all_rows)),
        missing_uncertainty=missing_uncertainty,
    )
    snapshots = []
    for config in CASES:
        pid = config["id"]
        print("Reviewing", pid, flush=True)
        path = args.data_root / "inputsTr" / f"{pid}.csv"
        rows = list(csv.DictReader(path.open()))
        case = dict(config, rows=rows, visits={})
        check = dict(
            id=pid, source_events=dict(Counter(r["topology_class"] for r in rows)), visits={}
        )
        pathlist = [path]
        native = {}
        for vi, visit in enumerate(["BL", "FU"]):
            imgpath = args.data_root / "inputsTr" / f"{pid}_{visit}_img_00.nii.gz"
            maskpath = (
                args.data_root
                / ("inputsTr" if visit == "BL" else "targetsTr")
                / f"{pid}_{visit}_mask_00.nii.gz"
            )
            pathlist += [imgpath, maskpath, args.data_root / "inputsTr" / f"{pid}_{visit}_00.json"]
            img, seg = nib.load(imgpath), nib.load(maskpath)
            assert img.shape == seg.shape and np.allclose(img.affine, seg.affine)
            assert nib.aff2axcodes(img.affine) == ("L", "P", "S")
            assert np.allclose(img.affine[:3, :3], np.diag(np.diag(img.affine[:3, :3])))
            spacing = [float(x) for x in img.header.get_zooms()]
            assert np.isclose(spacing[0], spacing[1]), "Renderer needs equal in-plane spacing"
            ct, mask = np.asarray(img.dataobj), np.asarray(seg.dataobj).astype(np.uint8)
            voxel_volume = abs(float(np.linalg.det(img.affine[:3, :3])))
            labels = [int(x) for x in np.unique(mask) if x]
            points = ndimage.center_of_mass(mask > 0, mask, labels) if labels else []
            counts = np.bincount(mask.ravel())
            stats = []
            for label, point in zip(labels, points):
                row = next(r for r in rows if int(r["lesion_id"]) == label)
                csv_center = np.array([float(x) for x in row["cog_" + visit.lower()].split()])
                csv_volume = float(row["volume_" + visit.lower()])
                native_center = np.array(point)
                ras = nib.affines.apply_affine(img.affine, native_center)
                stats.append(
                    dict(
                        label=label,
                        native_centroid=native_center.tolist(),
                        ras_mm=ras.tolist(),
                        csv_minus_native=(csv_center - native_center).tolist(),
                        voxels=int(counts[label]),
                        mask_mm3=float(counts[label] * voxel_volume),
                        csv_mm3=csv_volume,
                        volume_difference_voxels=float(
                            (csv_volume - counts[label] * voxel_volume) / voxel_volume
                        ),
                    )
                )
            verify = dict(
                shape=list(img.shape),
                spacing=spacing,
                affine=img.affine.tolist(),
                orientation="LPS voxel axes; affine world RAS mm",
                mask_geometry_matches=True,
                labels=stats,
            )
            if pid == "0777d5c17d" and visit == "BL":
                values = ct[mask == 1]
                verify["facial_label_intensity"] = dict(
                    count=len(values), min=int(values.min()), max=int(values.max())
                )
            check["visits"][visit] = verify
            ks = sorted(
                {
                    k
                    for focus in config["foci"]
                    for k in range(max(0, focus[1 + vi] - 8), min(img.shape[2], focus[1 + vi] + 9))
                }
            )
            frames = {}
            for k in ks:
                frames[k] = dict(
                    raw=[png_url(image_slice(ct, k, w)) for w in [0, 1]],
                    overlay=png_url(mask_slice(mask, k)),
                )
            case["visits"][visit] = dict(
                spacing=spacing,
                shape=list(img.shape),
                affine=img.affine.tolist(),
                frames=frames,
                file=imgpath.name,
                mask=maskpath.name,
            )
            focus = config["foci"][0]
            native[visit] = [
                view_snapshot(
                    ct,
                    mask,
                    focus[1 + vi],
                    focus[3 + vi],
                    spacing[0],
                    config["field"],
                    config["window"],
                    show,
                )
                for show in [False, True]
            ]
        if pid != "0777d5c17d":
            snapshots.append((config, native))
        for path in pathlist:
            b = path.read_bytes()
            audit["files"].append(
                dict(
                    member=str(path.relative_to(args.data_root)),
                    bytes=len(b),
                    sha256=hashlib.sha256(b).hexdigest(),
                )
            )
        audit["cases"].append(check)
        result["cases"].append(case)
    audit["sample_bytes"] = sum(x["bytes"] for x in audit["files"])
    (args.output / "review-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    template = Path(__file__).with_name("viewer.html").read_text()
    (args.output / "index.html").write_text(
        template.replace("/* REVIEW_DATA */", json.dumps(result, separators=(",", ":")))
    )
    for role in ["input", "helpers", "reference"]:
        sheet = Image.new("RGB", (1000, 1690), "#0c1420")
        draw = ImageDraw.Draw(sheet)
        draw.text(
            (38, 20), "Longitudinal CT · three actual patient pairs", font=font(28), fill="white"
        )
        draw.text(
            (38, 60),
            f"{role.upper()} · reader-selected axial crops · not an agent result",
            font=font(19),
            fill="#a9bdd1",
        )
        for row, (cfg, images) in enumerate(snapshots):
            y = 105 + row * 505
            draw.text(
                (38, y),
                f"{chr(65 + row)}  {cfg['title']} · {cfg['id']}",
                font=font(22),
                fill="white",
            )
            for col, visit in enumerate(["BL", "FU"]):
                x = 38 + col * 486
                show = role == "reference" or (role == "helpers" and visit == "BL")
                sheet.paste(images[visit][int(show)], (x, y + 30))
                k = cfg["foci"][0][1 + col]
                draw.text(
                    (x, y + 472),
                    f"{visit} · native k={k} · {cfg['field']} mm field",
                    font=font(16),
                    fill="#bacbdd",
                )
        draw.text(
            (38, 1630),
            "Solid colored outlines + translucent fill = manual lesion masks (when shown).",
            font=font(17),
            fill="#bacbdd",
        )
        draw.text(
            (38, 1655),
            "IDs: 1 cyan · 2 gold · 3 purple · 4 coral · 5 green · 6 pink.  R left / L right; A top / P bottom.",
            font=font(16),
            fill="#bacbdd",
        )
        sheet.save(args.output / f"{role}.png", optimize=True)
    print(
        json.dumps(
            dict(output=str(args.output), cases=len(result["cases"]), bytes=audit["sample_bytes"])
        )
    )


if __name__ == "__main__":
    main()
