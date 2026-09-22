"""Freeze explanatory dataset snapshots from retained inputs; never run a model.

Use the existing imaging environment, e.g. .venv-br030/bin/python. Every input
must match its recipe fingerprint. Outputs are local; the small manifest is
tracked separately. Existing files are never modified or imported as code.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipes", type=Path, default=Path("datasets/previews/recipes.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", action="append")
    args = parser.parse_args()
    root = Path.cwd()
    args.output.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(root / ".cache/dataset-snapshots-mpl"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import nibabel as nib
    import numpy as np
    from matplotlib.lines import Line2D
    from PIL import Image
    from scipy.ndimage import binary_erosion

    plt.rcParams.update(
        {
            "figure.facecolor": "#101a28",
            "axes.facecolor": "#101a28",
            "text.color": "#e6edf7",
            "axes.labelcolor": "#c5d4e5",
            "xtick.color": "#b8c9d9",
            "ytick.color": "#b8c9d9",
            "font.size": 10,
            "savefig.facecolor": "#101a28",
        }
    )
    gold = "#ffd166"
    recipes = json.loads(args.recipes.read_text())
    results = []

    def image(ax, a, title, spacing=(1, 1), window=None):
        if window is None:
            finite = a[np.isfinite(a)]
            window = np.percentile(finite, [1, 99.5])
        ax.imshow(
            a,
            cmap="gray",
            vmin=window[0],
            vmax=window[1],
            origin="lower",
            aspect=spacing[1] / spacing[0],
            interpolation="nearest",
        )
        ax.set_title(title, fontsize=10)
        ax.set_axis_off()

    def outline(ax, a, color=gold):
        edge = (a > 0) & ~binary_erosion(a > 0)
        rgba = np.zeros((*a.shape, 4))
        rgba[edge] = matplotlib.colors.to_rgba(color)
        ax.imshow(rgba, origin="lower", aspect=ax.get_aspect(), interpolation="nearest")

    def save(fig, row, role, caption):
        p = args.output / (row["dataset_id"] + "-" + role + ".png")
        if p.exists():
            raise FileExistsError("Use a fresh snapshot destination: " + str(p))
        fig.savefig(p, dpi=130, bbox_inches="tight", pad_inches=0.2)
        plt.close(fig)
        return {"role": role, "path": str(p), "sha256": sha(p), "caption": caption}

    def volume(path):
        ni = nib.as_closest_canonical(nib.load(path))
        return ni, np.asanyarray(ni.dataobj), np.asarray(ni.header.get_zooms()[:3])

    def slices(ni, a, masks, row):
        spacing = np.asarray(ni.header.get_zooms()[:3])
        if masks:
            foreground = np.logical_or.reduce([m > 0 for m, _, _ in masks])
            indices = [
                int(np.argmax(foreground.sum(tuple(j for j in range(3) if j != i))))
                for i in range(3)
            ]
        else:
            indices = [n // 2 for n in a.shape[:3]]
        panels = []
        for role in ["input", "reference"] if masks else ["input"]:
            fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.6))
            for axis, ax in enumerate(axs):
                remaining = [i for i in range(3) if i != axis]
                cut = np.take(a, indices[axis], axis=axis).T
                title = (
                    ["yz plane", "xz plane", "xy plane"]
                    if row["kind"] == "echo"
                    else ["Sagittal · A→ / S↑", "Coronal · R→ / S↑", "Axial · R→ / A↑"]
                )[axis]
                image(
                    ax,
                    cut,
                    title + f"\ncanonical slice {indices[axis]}",
                    spacing[remaining],
                    row.get("window"),
                )
                if role == "reference":
                    for m, _label, color in masks:
                        outline(ax, np.take(m, indices[axis], axis=axis).T, color)
            if role == "reference":
                fig.legend(
                    [Line2D([0], [0], color=c, lw=2) for _, _, c in masks],
                    [label for _, label, _ in masks],
                    loc="lower center",
                    ncol=min(3, len(masks)),
                    frameon=False,
                )
            fig.suptitle(
                row["sample_id"]
                + (" · source image" if role == "input" else " · source annotation"),
                fontsize=13,
            )
            fig.subplots_adjust(bottom=0.17, top=0.84)
            panels.append(
                save(
                    fig,
                    row,
                    role,
                    row["selection"]
                    + " Canonical RAS views preserve voxel spacing; no prediction is shown.",
                )
            )
        return panels, {
            "canonical_indices": indices,
            "canonical_shape": list(a.shape),
            "spacing_mm": spacing.tolist(),
        }

    for row in recipes["entries"]:
        if args.dataset and row["dataset_id"] not in args.dataset:
            continue
        for source in row["sources"]:
            if sha(source["path"]) != source["sha256"]:
                raise ValueError("Source changed: " + source["path"])
        result = {
            k: row[k]
            for k in ("dataset_id", "sample_id", "status", "summary", "reference_note", "sources")
        }
        result["panels"] = []
        kind = row["kind"]
        if kind == "copy":
            for panel in row["panels"]:
                path = args.output / (
                    row["dataset_id"] + "-" + panel["role"] + Path(panel["source"]).suffix
                )
                if path.exists():
                    raise FileExistsError(path)
                shutil.copyfile(panel["source"], path)
                result["panels"].append(
                    {
                        "role": panel["role"],
                        "path": str(path),
                        "sha256": sha(path),
                        "caption": panel["caption"],
                    }
                )
        elif kind == "metadata":
            obj = json.loads(Path(row["source"]).read_text())
            for key in row.get("pointer", "").split("/")[1:]:
                obj = obj[int(key)] if isinstance(obj, list) else obj[key]
            result["panels"] = [
                {"role": "metadata", "text": json.dumps(obj, indent=2), "caption": row["selection"]}
            ]
        elif kind == "mask":
            ni, a, spacing = volume(row["image"])
            masks = []
            for item in row.get("masks", []):
                mn, m, _ = volume(item["path"])
                assert m.shape == a.shape and np.allclose(mn.affine, ni.affine), (
                    "Image/mask grid mismatch"
                )
                selected = np.isin(m, item["values"]) if "values" in item else m > 0
                masks.append((selected, item["label"], item.get("color", gold)))
            result["panels"], result["view"] = slices(ni, a, masks, row)
            if row.get("table"):
                rows = list(
                    csv.DictReader(Path(row["table"]).read_text(encoding="utf-8-sig").splitlines())
                )[:8]
                text = "\n".join(
                    ", ".join(
                        f"{k}: {v}"
                        for k, v in r.items()
                        if k in ["short_name", "X", "Y", "Z", "anatomical_name_en"]
                    )
                    for r in rows
                )
                result["panels"].append(
                    {
                        "role": "reference",
                        "text": text,
                        "caption": "First eight source CSV landmark rows. Coordinate mapping was rejected; these are disputed annotations, not validated ground truth.",
                    }
                )
        elif kind == "points":
            original = nib.load(row["image"])
            ni, a, spacing = volume(row["image"])
            if row["format"] == "fcsv":
                rows = list(
                    csv.reader(
                        x
                        for x in Path(row["points"]).read_text().splitlines()
                        if not x.startswith("#")
                    )
                )
                world = np.array([[float(x) for x in r[1:4]] for r in rows])
                names = [r[11] for r in rows]
                assert "# CoordinateSystem = 0" in Path(row["points"]).read_text(), (
                    "Expected RAS FCSV"
                )
            else:
                raw = json.loads(Path(row["points"]).read_text())[row["point_key"]]
                names, points = list(raw), list(raw.values())
                world = nib.affines.apply_affine(original.affine, points)
            points = nib.affines.apply_affine(np.linalg.inv(ni.affine), world)
            selected = row.get("selected", [0, 1, 2])
            for role in ["input", "reference"]:
                fig, axs = plt.subplots(1, len(selected), figsize=(11.5, 4.8))
                for ax, j in zip(np.atleast_1d(axs), selected, strict=True):
                    axis = row.get("axis", 2)
                    axes = [i for i in range(3) if i != axis]
                    p = points[j]
                    index = int(round(p[axis]))
                    assert 0 <= index < a.shape[axis]
                    image(
                        ax,
                        np.take(a, index, axis=axis).T,
                        f"{row.get('point_titles', names)[j]} · slice {index}",
                        spacing[axes],
                        row.get("window"),
                    )
                    if role == "reference":
                        ax.scatter(p[axes[0]], p[axes[1]], s=95, c=gold, marker="+", linewidths=2)
                fig.suptitle(
                    row["sample_id"]
                    + (" · image only" if role == "input" else " · gold cross = reference point"),
                    fontsize=13,
                )
                result["panels"].append(
                    save(
                        fig,
                        row,
                        role,
                        row["selection"]
                        + " Point-centred slices are post-hoc reader selections in canonical RAS; references are shown only on reveal.",
                    )
                )
        elif kind == "atlas":
            with zipfile.ZipFile(row["archive"]) as z:
                text = z.read(row["member"]).decode()
            rows = list(csv.reader(x for x in text.splitlines() if not x.startswith("#")))
            points = np.array([[float(x) for x in r[1:4]] for r in rows])
            fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.3))
            for ax, axes, title in zip(
                axs,
                [(0, 1), (0, 2), (1, 2)],
                ["Axial projection · R/A", "Coronal projection · R/S", "Sagittal projection · A/S"],
                strict=True,
            ):
                ax.scatter(points[:, axes[0]], points[:, axes[1]], c=gold, s=18)
                for p, r in zip(points, rows, strict=True):
                    ax.annotate(
                        r[11], p[list(axes)], xytext=(3, 3), textcoords="offset points", fontsize=7
                    )
                ax.set_title(title)
                ax.set_aspect("equal")
                ax.set_xlabel("mm")
                ax.set_ylabel("mm")
            fig.suptitle("Actual generic-atlas AFIDs points · MRI image unavailable", fontsize=13)
            fig.tight_layout()
            result["panels"].append(
                save(
                    fig,
                    row,
                    "reference",
                    "Gold numbered points = retained generic-template annotations (RAS mm), projected without an image. These are not target-patient landmarks.",
                )
            )
        elif kind == "feecho":
            selected = [Path(p) for p in row["selected_masks"]]
            for role in ["input", "reference"]:
                fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.4))
                for ax, p in zip(axs, selected, strict=True):
                    a = np.array(Image.open(Path(row["base"], "image", p.name)))
                    m = np.array(Image.open(p))
                    if a.ndim == 3:
                        a = a[:, :, :3].mean(2)
                    if m.ndim == 3:
                        m = m[:, :, :3].max(2)
                    image(ax, np.flipud(a), p.stem.split("_")[-1], window=[0, 255])
                    if role == "reference":
                        outline(ax, np.flipud(m))
                fig.suptitle(
                    "Patient001 · source time002"
                    + (
                        " · gold = supplied mask foreground"
                        if role == "reference"
                        else " · ultrasound only"
                    ),
                    fontsize=13,
                )
                result["panels"].append(
                    save(
                        fig,
                        row,
                        role,
                        "Three source radial planes with the largest supplied foreground at time002; selected post hoc. Original PNG raster orientation retained. Gold merges nonzero mask values; no cavity partition or physical mesh transform is inferred.",
                    )
                )
            result["view"] = {"selected_files": [str(p) for p in selected]}
        elif kind == "echo-review":
            a = np.load(row["npz"], allow_pickle=False)["images"]
            geometry = json.loads(Path(row["geometry"]).read_text())
            fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.3))
            for ax, i in zip(axs, [0, 1, 6], strict=True):
                ax.imshow(a[i, 0], cmap="gray", vmin=0, vmax=255, interpolation="nearest")
                ax.set_title(geometry[i]["name"] + " · source frame 1")
                ax.set_axis_off()
            fig.suptitle("EchoSlicer · calibrated planes from a polar acquisition")
            result["panels"].append(
                save(
                    fig,
                    row,
                    "input",
                    row["selection"]
                    + " Display axes follow each retained plane definition; no anatomical GT was supplied.",
                )
            )
        elif kind == "echo":
            if row.get("npz"):
                data = np.load(row["npz"], allow_pickle=False)
                a = data["images"][0].transpose(2, 1, 0)
                bounds = data["bounds"]
                spacing = (bounds[:, 1] - bounds[:, 0]) / (np.array(a.shape) - 1)
            else:
                a = np.load(row["npy"], mmap_mode="r")[0].transpose(2, 1, 0)
                geometry = json.loads(Path(row["geometry"]).read_text())
                spacing = np.array(geometry["spacing_xyz_mm"])

            class Grid:
                header = {"unused": True}

                def __init__(self, s):
                    self.header = self
                    self.s = s

                def get_zooms(self):
                    return self.s

            result["panels"], result["view"] = slices(Grid(spacing), a, [], row)
            # These arrays use the source/task xyz frame, not anatomical RAS.
            result["panels"][0]["caption"] = (
                row["selection"]
                + " Array xyz orthogonal sections with physical spacing; axes are acquisition coordinates, not patient RAS."
            )
            if row.get("reference"):
                ref = np.load(row["reference"], allow_pickle=False)
                pts = ref["points"]
                fig = plt.figure(figsize=(9, 4.5))
                for i, t in enumerate([0, len(pts) // 2]):
                    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
                    p = pts[t]
                    f = ref["faces"]
                    ax.plot_trisurf(
                        p[:, 0],
                        p[:, 1],
                        p[:, 2],
                        triangles=f,
                        color=gold,
                        alpha=0.8,
                        linewidth=0,
                        shade=False,
                    )
                    ax.set_box_aspect(np.ptp(p, axis=0))
                    ax.set_title(f"Reference surface · frame {t}")
                    ax.set_xlabel("x mm")
                    ax.set_ylabel("y mm")
                    ax.set_zlabel("z mm")
                fig.suptitle("Operator-derived LV endocardial reference · gold surface")
                result["panels"].append(
                    save(
                        fig,
                        row,
                        "reference",
                        "Gold = released/adjusted cavity reference at two selected phases in the acquisition coordinate frame. A cavity surface is not tracked myocardial material and is not a model prediction.",
                    )
                )
        elif kind == "nlst":
            for role, p in [("input", row["input"]), ("reference", row["reference"])]:
                d = np.load(p, allow_pickle=False)
                a = d["hu"]
                spacing = np.linalg.norm(d["voxel_to_lps"][:3, :3], axis=0)
                fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.6))
                for ax, z in zip(axs, [55, 75], strict=True):
                    image(
                        ax,
                        a[:, :, z].T,
                        f"{Path(p).stem} · native k={z}",
                        spacing[:2],
                        [-1350, 150],
                    )
                fig.suptitle("NLST · same examination, paired reconstruction kernels")
                result["panels"].append(
                    save(
                        fig,
                        row,
                        role,
                        "Same native slice indices and physical grid in B30f / B50f. The paired reconstruction is an image correspondence reference, not an anatomical segmentation GT. Display follows native array axes; LPS affine retained in provenance.",
                    )
                )
        elif kind == "straus":
            fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.3))
            for ax, t in zip(axs, [1, 10, 20], strict=True):
                p = Path(row["images"]) / f"frame_{t:02d}.png"
                a = np.array(Image.open(p))
                ax.imshow(a)
                ax.set_title(f"Simulated ultrasound · frame {t}")
                ax.set_axis_off()
            result["panels"].append(
                save(
                    fig,
                    row,
                    "input",
                    "Retained simulated ultrasound, one long-axis view at source frames 1, 10 and 20; image geometry comes from the frozen public-video metadata.",
                )
            )
            d = np.load(row["reference"], allow_pickle=False)
            points = d["points"]
            fig = plt.figure(figsize=(9, 4.6))
            for i, t in enumerate([0, 15]):
                ax = fig.add_subplot(1, 2, i + 1, projection="3d")
                p = points[t]
                idx = np.arange(0, len(p), 8)
                ax.scatter(p[idx, 0], p[idx, 1], p[idx, 2], s=2, c=gold, alpha=0.6)
                ax.set_box_aspect(np.ptp(p, axis=0))
                ax.set_title(f"Material nodes · phase {t}")
                ax.set_xlabel("x mm")
                ax.set_ylabel("y mm")
                ax.set_zlabel("z mm")
            fig.suptitle("Source simulator material nodes · same indices across phases")
            result["panels"].append(
                save(
                    fig,
                    row,
                    "reference",
                    "Gold = every eighth retained material node at phases 0 and 15; identical node identities come from the simulator. This is synthetic material truth, not a clinical cavity annotation.",
                )
            )
        elif kind == "synthetic":
            item = json.loads(Path(row["source"]).read_text())[0]
            raw = np.frombuffer(
                base64.b64decode(item["input"]["7FE00010"]["InlineBinary"]), dtype="<i2"
            ).reshape(-1, 3, 4)
            truth = np.asarray(item["expected"]["pixels"]).reshape(-1, 3, 4)
            for role, a in [("input", raw), ("reference", truth)]:
                fig, axs = plt.subplots(1, 3, figsize=(10, 3.8))
                for j, ax in enumerate(axs):
                    image(
                        ax,
                        a[j],
                        f"{'Encoded' if role == 'input' else 'Canonical'} frame {j}",
                        window=[-3000, 3000],
                    )
                    for y in range(3):
                        for x in range(4):
                            ax.text(
                                x,
                                y,
                                str(a[j, y, x]),
                                ha="center",
                                va="center",
                                color=gold,
                                fontsize=9,
                            )
                fig.suptitle("public-00-encoding-0 · actual asymmetric fixture pixels")
                result["panels"].append(
                    save(
                        fig,
                        row,
                        role,
                        "First three retained frames, integer values shown directly; grayscale window [-3000, 3000]. Metadata determines canonical ordering. No fixture generator or authoring module was executed.",
                    )
                )
        elif kind == "learn2reg":
            for role in ["input", "reference"]:
                fig, axs = plt.subplots(1, 2, figsize=(10, 5))
                for i, ax in enumerate(axs):
                    original = nib.load(row["images"][i])
                    ni, a, spacing = volume(row["images"][i])
                    p = np.loadtxt(row["points"][i], delimiter=",")[0]
                    p = nib.affines.apply_affine(
                        np.linalg.inv(ni.affine), nib.affines.apply_affine(original.affine, p)
                    )
                    z = int(round(p[2]))
                    image(
                        ax,
                        a[:, :, z].T,
                        f"Respiratory phase {i} · canonical k={z}",
                        spacing[:2],
                        [-1350, 150],
                    )
                    if role == "reference":
                        ax.scatter(p[0], p[1], marker="+", s=140, c=gold, linewidths=2)
                fig.suptitle(
                    "LungCT_0001 · same annotated correspondence in two respiratory phases"
                )
                result["panels"].append(
                    save(
                        fig,
                        row,
                        role,
                        "Slices selected through correspondence row 0 in each volume using native voxel coordinates and each affine. Gold cross = the same source landmark; slice selection uses the reference.",
                    )
                )
        elif kind == "ispy2":
            audit = json.loads(Path(row["reference"]).read_text())["cases"][0]
            loaded = []
            for i in range(2):
                ni, a, spacing = volume(row["images"][i])
                a = a[:, :, :, row.get("frame", 0)] if a.ndim == 4 else a
                point = nib.affines.apply_affine(
                    np.linalg.inv(ni.affine),
                    audit["source_reference_regions"][i]["voi_center_ras_mm"],
                )
                z = int(round(point[2]))
                assert 0 <= z < a.shape[2]
                loaded.append((a, spacing, point, z))
            for role in ["input", "reference"]:
                fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.8))
                for i, (ax, (a, spacing, point, z)) in enumerate(zip(axs, loaded, strict=True)):
                    image(
                        ax,
                        a[:, :, z].T,
                        f"Visit {i + 1} · DCE phase {row.get('frame', 0)} · slice {z}",
                        spacing[:2],
                    )
                    if role == "reference":
                        ax.scatter(point[0], point[1], marker="+", s=150, c=gold, linewidths=2)
                fig.suptitle(
                    "ISPY2-102011 · visit MRI"
                    + (" · gold = source VOI centre" if role == "reference" else "")
                )
                result["panels"].append(
                    save(
                        fig,
                        row,
                        role,
                        "DCE phase index 1 at two visits; slices selected through the source reference-region centre, canonical RAS (R→, A↑), independent 1–99.5 percentile windows. Gold on reveal marks the source VOI centre, not tumor boundaries. This is a post-hoc reader view.",
                    )
                )
            fields = {
                k: audit[k]
                for k in ["source_id", "ftv_cc", "source_diameter_values", "source_diameter_unit"]
            }
            result["panels"].append(
                {
                    "role": "reference",
                    "text": json.dumps(fields, indent=2),
                    "caption": "Retained source reference values across four visits. FTV is in cc; source diameter units remain unresolved. These clinical/functional measurements are not pixelwise segmentation GT.",
                }
            )
        else:
            raise ValueError("Unknown snapshot kind: " + kind)
        result["recipe_sha256"] = hashlib.sha256(
            json.dumps(row, sort_keys=True).encode()
        ).hexdigest()
        results.append(result)
        print(row["dataset_id"], len(result["panels"]), flush=True)
    manifest = {
        "schema_version": 1,
        "renderer": {"path": str(Path(__file__).relative_to(root)), "sha256": sha(__file__)},
        "recipes": {"path": str(args.recipes), "sha256": sha(args.recipes)},
        "entries": results,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
