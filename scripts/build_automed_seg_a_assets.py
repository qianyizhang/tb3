"""Build source-bounded Full segmentation teaching slices; never run a model or scorer."""

from __future__ import annotations
import argparse, hashlib, json, io
from pathlib import Path
import numpy as np
import nibabel as nib
from PIL import Image

KEYS = ("aeropath", "colon", "feta", "heart")
SRC = Path(".local/explainers/core-20260929/automed-seg-a-source")
FILES = {
    "aeropath": [
        "runs/br033-brain-routing/airway-access/data/10/10_CT_HR.nii.gz",
        "runs/br033-brain-routing/airway-access/data/10/10_CT_HR_label_lungs.nii.gz",
        "runs/br033-brain-routing/airway-access/data/10/10_CT_HR_label_airways.nii.gz",
    ],
    "colon": [str(SRC / "colon_219.nii.gz"), str(SRC / "colon_219-label.nii.gz")],
    "heart": [str(SRC / "la_007.nii.gz"), str(SRC / "la_007-label.nii.gz")],
}
LABELS = {
    "aeropath": {"0": "background", "1": "lung", "2": "airway"},
    "colon": {"0": "background", "1": "colon_cancer"},
    "feta": {
        "0": "background",
        "1": "eCSF",
        "2": "GM",
        "3": "WM",
        "4": "LV",
        "5": "CBM",
        "6": "SGM",
        "7": "BS",
    },
    "heart": {"0": "background", "1": "left_atrium (task label heart)"},
}
COLORS = {"1": [68, 196, 222, 145], "2": [248, 185, 59, 215]}
LICENSE = {
    "aeropath": "LicenseRef-AeroPath-terms-conflict",
    "colon": "CC-BY-SA-4.0",
    "feta": "LicenseRef-TB3-symbolic-teaching",
    "heart": "CC-BY-SA-4.0",
}
TITLES = {
    "aeropath": "Lung and airway tree in CT",
    "colon": "Primary colon cancer in CT",
    "feta": "Seven fetal-brain tissues in T2 MRI",
    "heart": "Left atrium in cardiac MRI",
}
WINDOW = {"aeropath": [-1000, 400], "colon": [-150, 250]}


def root():
    for p in Path(__file__).resolve().parents:
        if (p / "presentation/EXPLAINER-SCOPE.json").exists():
            return p
    raise RuntimeError("tb3 checkout not found")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(p, d):
    p.write_text(json.dumps(d, sort_keys=True, separators=(",", ":")) + "\n")


def png(a, mode):
    b = io.BytesIO()
    Image.fromarray(a, mode).save(b, format="PNG", optimize=False)
    return b.getvalue()


def orient(a):
    return np.flipud(a.T)


def make(r, key, out, receipt):
    if key not in KEYS:
        raise ValueError(key)
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite {out}")
    d = json.loads(receipt.read_text())
    assert d["entry_id"] == f"automedbench-full-{key}-seg-task" and all(
        x.get("attempted_at") for x in d["attempts"]
    )
    pkg = r / SRC / "packages" / (key + ".tar.gz")
    assert sha(pkg) == d["task_package"]["sha256"]
    g = json.loads((r / SRC / "geometry-audit.json").read_text()) if key != "feta" else None
    out.mkdir(parents=True)
    parts = []
    reference_counts = []
    sources = {str(pkg.relative_to(r)): sha(pkg)}
    if key == "feta":
        canonical_receipt = (
            r
            / "presentation/external-tasks/sources/automedbench-full-feta-seg-task-resolution.json"
        )
        assert receipt.resolve() == canonical_receipt.resolve(), (
            "FeTA pack requires the tracked source-resolution receipt"
        )
        sources = {str(canonical_receipt.relative_to(r)): sha(canonical_receipt)}
    if key != "feta":
        paths = [r / p for p in FILES[key]]
        meta = g[key]
        for path, item in zip(paths, meta["files"]):
            assert sha(path) == item["sha256"]
            sources[str(path.relative_to(r))] = item["sha256"]
        ims = [nib.load(str(p)) for p in paths]
        assert all(
            im.shape == ims[0].shape and np.allclose(im.affine, ims[0].affine) for im in ims[1:]
        )
        volume = np.asanyarray(ims[0].dataobj)
        labs = [np.asanyarray(im.dataobj) > 0 for im in ims[1:]]
        z0 = meta["selected_axial_index"]
        indices = sorted({max(0, z0 - 8), z0, min(ims[0].shape[2] - 1, z0 + 8)})
        if key == "heart":
            lo, hi = np.percentile(volume, [1, 99.5]).tolist()
        else:
            lo, hi = WINDOW[key]
        for n, z in enumerate(indices):
            sl = volume[:, :, z]
            grey = np.clip((sl - lo) / (hi - lo), 0, 1)
            grey = np.rint(grey * 255).astype(np.uint8)
            img = orient(grey)
            name = f"slice-{n}.png"
            (out / name).write_bytes(png(img, "L"))
            if key == "aeropath":
                # Source contract's ascending fusion: label 2 overwrites label 1.
                label = np.zeros(sl.shape, np.uint8)
                label[labs[0][:, :, z]] = 1
                label[labs[1][:, :, z]] = 2
            else:
                label = labs[0][:, :, z].astype(np.uint8)
            label = orient(label)
            rgba = np.zeros((*label.shape, 4), np.uint8)
            for idx, color in COLORS.items():
                rgba[label == int(idx)] = color
            ref = f"source-label-{n}.png"
            (out / ref).write_bytes(png(rgba, "RGBA"))
            parts.append({"image": name, "native_k": z})
            reference_counts.append(
                {str(i): int(np.count_nonzero(label == i)) for i in range(1, len(LABELS[key]))}
            )
        shape = list(ims[0].shape)
        zooms = [float(x) for x in ims[0].header.get_zooms()[:3]]
        affine = ims[0].affine.round(6).tolist()
        axis = "".join(nib.aff2axcodes(ims[0].affine))
    else:
        shape = None
        zooms = None
        affine = None
        axis = None
        indices = []
    notice = {
        "label": "Official upstream volume; Full staged case unverified"
        if key != "feta"
        else "FeTA source restricted; no native case",
        "text": (
            "Source training labels are a reader-only teaching reveal. No Full private reference, prediction or Dice result is retained."
            if key != "feta"
            else "Zenodo files are restricted and Synapse requires an access agreement. This is a symbolic protocol only; no source MRI, label or Full result is retained."
        ),
        "url": d["upstream_url"],
        "link_label": "Official source and acquisition",
    }
    source = {
        "role": "official-upstream-volume-not-verified-Full-case"
        if key != "feta"
        else "symbolic-protocol-no-native-data",
        "title": TITLES[key],
        "input_filename": d["task_package"]["input_filename"],
        "shape_ijk": shape,
        "voxel_spacing_mm": zooms,
        "affine": affine,
        "axis_codes": axis,
        "display_transform": "flipud(native_i_j_slice.T)" if key != "feta" else None,
        "intensity_window": ([float(lo), float(hi)] if key != "feta" else None),
        "slices": parts,
        "notice": notice,
        "full_case_membership": "unverified",
    }
    output = {
        "role": "required-schema-only",
        "path": "agents_outputs/{case_id}/dseg.nii.gz",
        "status": "not-retained",
        "label_values": LABELS[key],
        "same_spatial_shape_required": True,
        "affine_alignment_required_for_interpretation": True,
        "prediction": None,
        "dice": None,
    }
    reference = {
        "role": "upstream-training-source-label" if key != "feta" else "unavailable",
        "source_label_slices": [f"source-label-{i}.png" for i in range(len(parts))],
        "slice_label_voxels": reference_counts,
        "full_private_reference": None,
        "label_values": LABELS[key],
        "fusion": "lung first, airway overwrites overlap" if key == "aeropath" else None,
        "warning": "Upstream labels are not Full private ground truth and were not solver-supplied in this Full case."
        if key != "feta"
        else "No label was acquired.",
    }
    dump(out / "source.json", source)
    dump(out / "output.json", output)
    dump(out / "reference.json", reference)
    (out / "NOTICE.md").write_text(
        notice["label"] + ". " + notice["text"] + " " + notice["url"] + "\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        LICENSE[key]
        + ". Source receipt terms: "
        + d["source_license"]
        + ". "
        + d["upstream_url"]
        + "\n"
    )
    names = [
        ("source.json", "illustration"),
        ("output.json", "illustration"),
        ("reference.json", "reader-reference-reveal" if key != "feta" else "illustration"),
        ("NOTICE.md", "illustration"),
        ("DATA-LICENSE.txt", "illustration"),
    ]
    for i, x in enumerate(parts):
        names.extend(
            ((x["image"], "illustration"), (f"source-label-{i}.png", "reader-reference-reveal"))
        )
    assets = [
        {
            "file": n,
            "sha256": sha(out / n),
            "bytes": (out / n).stat().st_size,
            "provenance": "source-derived-teaching" if key != "feta" else "symbolic-protocol",
            "role": role,
        }
        for n, role in names
    ]
    dump(
        out / "manifest.json",
        {
            "id": f"retained-automed-full-{key}-seg-v1",
            "frame": "native-NIfTI-voxel-ijk" if key != "feta" else "symbolic-NIfTI-grid",
            "units": "voxel",
            "license": LICENSE[key],
            "label_license": LICENSE[key] if key != "feta" else None,
            "reference_policy": "reader-reference-reveal"
            if key != "feta"
            else "no-reference-assets",
            "sources": sources,
            "checks": {
                "full_staged_case": "unverified" if key != "feta" else False,
                "full_private_reference": False,
                "model_run": False,
                "scorer_run": False,
                "selected_source_slices": len(parts),
            },
            "assets": assets,
        },
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--entry", choices=KEYS, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    a = p.parse_args()
    make(root(), a.entry, a.output, a.receipt)


if __name__ == "__main__":
    main()
