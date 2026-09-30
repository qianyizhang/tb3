"""Build deterministic, source-bounded Full segmentation teaching packs; no inference."""

from __future__ import annotations
import argparse, gzip, hashlib, io, json, struct
from pathlib import Path
import numpy as np
import nibabel as nib
from PIL import Image

KEYS = ("pancreas", "panther-t1", "panther-t2", "prostate")
SOURCE = Path(".local/explainers/core-20260929/automed-seg-c-source")
LICENSE = {
    "pancreas": "CC-BY-NC-ND-4.0",
    "panther-t1": "LicenseRef-TB3-symbolic-teaching",
    "panther-t2": "LicenseRef-TB3-symbolic-teaching",
    "prostate": "CC-BY-SA-4.0",
}
TITLES = {
    "pancreas": "PanTS CT: pancreas and lesion",
    "panther-t1": "PANTHER diagnostic arterial T1 MRI",
    "panther-t2": "PANTHER treatment-planning T2 MR-Linac MRI",
    "prostate": "MSD two-channel prostate MRI",
}


def root():
    for p in Path(__file__).resolve().parents:
        if (p / "presentation/EXPLAINER-SCOPE.json").exists():
            return p
    raise RuntimeError("tb3 root not found")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(p, obj):
    p.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")


def png(arr, mode):
    b = io.BytesIO()
    Image.fromarray(arr, mode).save(b, format="PNG", optimize=False)
    return b.getvalue()


def display(arr):
    return np.flipud(arr.T)


def gray(arr, lo, hi):
    return display(np.rint(np.clip((arr - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8))


def make(repo, key, out, receipt_path):
    if key not in KEYS:
        raise ValueError(key)
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite {out}")
    receipt = json.loads(receipt_path.read_text())
    assert receipt["entry_id"] == f"automedbench-full-{key}-seg-task" and all(
        x.get("attempted_at") for x in receipt["attempts"]
    )
    pkg = repo / SOURCE / "packages" / f"{key}.tar.gz"
    assert sha(pkg) == receipt["task_package"]["sha256"]
    canonical = (
        repo
        / "presentation/external-tasks/sources"
        / f"automedbench-full-{key}-seg-task-resolution.json"
    )
    assert receipt_path.resolve() == canonical.resolve(), (
        "Expected canonical tracked source receipt"
    )
    builder = repo / "scripts/build_automed_seg_c_assets.py"
    sources = {
        str(pkg.relative_to(repo)): sha(pkg),
        str(canonical.relative_to(repo)): sha(canonical),
        str(builder.relative_to(repo)): sha(builder),
    }
    for relative, pin in receipt["task_package"].get("pinned_files", {}).items():
        assert (
            sha(repo / SOURCE / "packages" / key / "automedbench-task" / relative) == pin["sha256"]
        )
    if key in ("panther-t1", "panther-t2"):
        # Symbolic packs compile without local raw archives. Replay still verifies the
        # task package above; the tracked receipt is the portable manifest source.
        canonical = (
            repo
            / "presentation/external-tasks/sources"
            / f"automedbench-full-{key}-seg-task-resolution.json"
        )
        assert receipt_path.resolve() == canonical.resolve(), (
            "Symbolic pack requires the tracked source-resolution receipt"
        )
        sources = {str(canonical.relative_to(repo)): sha(canonical)}
    out.mkdir(parents=True)
    prostate = key == "prostate"
    ct = key == "pancreas"
    real = prostate or ct
    slices = []
    helper_counts = []
    geometry = None
    if ct:
        ex = receipt["source_example"]
        image_path = repo / ex["image_path"]
        assert sha(image_path) == ex["image_sha256"]
        correction = receipt["native_header_correction"]
        assert sha(repo / correction["path"]) == correction["sha256"]
        with gzip.open(image_path, "rb") as stream:
            header = stream.read(348)
        assert struct.unpack_from("<ff", header, 112) == (1.0, 0.0), (
            "Expected raw on-disk NIfTI scaling 1/0"
        )
        sources[correction["path"]] = correction["sha256"]
        recovery = receipt["source_recovery_receipt"]
        assert sha(repo / recovery["path"]) == recovery["sha256"]
        sources[recovery["path"]] = recovery["sha256"]
        sources[ex["image_path"]] = ex["image_sha256"]
        image = nib.load(str(image_path))
        assert image.shape == (266, 158, 152)
        assert tuple(round(float(x), 6) for x in image.header.get_zooms()[:3]) == (1.5, 1.5, 1.5)
        arr = np.asanyarray(image.dataobj)
        assert arr.dtype == np.int16
        for i, k in enumerate((38, 76, 114)):
            name = f"ct-{i}.png"
            (out / name).write_bytes(png(gray(arr[:, :, k], -160, 240), "L"))
            slices.append({"native_k": k, "ct_image": name})
        geometry = {
            "shape_ijk": list(image.shape),
            "voxel_spacing_mm": [1.5, 1.5, 1.5],
            "axis_codes": "".join(nib.aff2axcodes(image.affine)),
            "affine": image.affine.round(6).tolist(),
            "display_transform": "flipud(native_i_j_slice.T)",
            "window_stored_intensity": [-160, 240],
            "intensity_units": "stored values; HU calibration unverified",
        }
    if prostate:
        ex = receipt["source_example"]
        image_path = repo / ex["image_path"]
        label_path = repo / ex["label_path"]
        assert sha(image_path) == ex["image_sha256"] and sha(label_path) == ex["label_sha256"]
        sources[ex["image_path"]] = ex["image_sha256"]
        sources[ex["label_path"]] = ex["label_sha256"]
        image = nib.load(str(image_path))
        label = nib.load(str(label_path))
        assert image.shape == (320, 320, 15, 2) and label.shape == image.shape[:3]
        assert np.max(np.abs(image.affine - label.affine)) < 2e-5
        arr = np.asanyarray(image.dataobj)
        lab = np.asanyarray(label.dataobj)
        assert set(np.unique(lab).tolist()) == {0, 1, 2}
        for i, k in enumerate((2, 5, 8)):
            names = []
            for channel, channel_name in enumerate(("t2", "adc")):
                plane = arr[:, :, k, channel]
                lo, hi = np.percentile(arr[:, :, :, channel], [1, 99.5])
                name = f"{channel_name}-{i}.png"
                (out / name).write_bytes(png(gray(plane, lo, hi), "L"))
                names.append(name)
            label_plane = display(lab[:, :, k])
            rgba = np.zeros((*label_plane.shape, 4), np.uint8)
            rgba[label_plane == 1] = [47, 206, 230, 168]
            rgba[label_plane == 2] = [248, 181, 65, 168]
            helper = f"training-label-{i}.png"
            (out / helper).write_bytes(png(rgba, "RGBA"))
            slices.append({"native_k": k, "t2_image": names[0], "adc_image": names[1]})
            helper_counts.append(
                {
                    "peripheral_zone": int((label_plane == 1).sum()),
                    "transition_zone": int((label_plane == 2).sum()),
                }
            )
        geometry = {
            "shape_ijk_channels": list(image.shape),
            "voxel_spacing_mm": [round(float(x), 6) for x in image.header.get_zooms()[:3]],
            "axis_codes": "".join(nib.aff2axcodes(image.affine)),
            "affine": image.affine.round(6).tolist(),
            "label_affine_max_abs_difference_mm": float(
                np.max(np.abs(image.affine - label.affine))
            ),
            "display_transform": "flipud(native_i_j_slice.T)",
        }
    notice = {
        "label": "Official upstream CT input; Full selection unverified"
        if ct
        else "Official upstream training pair; Full selection unverified"
        if prostate
        else "No task-matched native case in this pack",
        "text": "Official PanTSMini CT PanTS_00000684 is input-only; no matching label or Full membership is verified."
        if ct
        else "Upstream MSD T2/ADC training pair only; Full membership and private targets are unverified."
        if prostate
        else "No PANTHER MRI pair; official source requires an access request and Full membership is unverified.",
        "url": receipt["upstream_url"],
        "link_label": "Official source/acquisition",
    }
    source = {
        "title": TITLES[key],
        "role": "upstream-input-example-not-Full-staged"
        if ct
        else "upstream-training-example-not-Full-staged"
        if prostate
        else "symbolic-protocol-no-native-case",
        "input_filename": receipt["task_package"]["input_filename"],
        "geometry": geometry,
        "slices": slices,
        "notice": notice,
        "full_case_membership": False,
    }
    if prostate:
        operation = {
            "type": "two-channel-zonal-segmentation",
            "input_channels": [
                {"index": 0, "name": "T2-weighted anatomy"},
                {"index": 1, "name": "ADC diffusion-derived contrast"},
            ],
            "spatial_operation": "Map paired T2 and ADC values at each native i,j,k into one mutually exclusive label on the same 3D spatial grid.",
            "labels": {"0": "background", "1": "peripheral_zone", "2": "transition_zone"},
            "training_helper": "Official upstream label IDs 1/2 are shown only in the helper scene. They are not a predicted Full output.",
        }
        output = {
            "type": "combined-multiclass",
            "files": ["agents_outputs/{case_id}/dseg.nii.gz"],
            "label_values": operation["labels"],
            "same_spatial_shape_required": True,
            "affine_alignment_required_for_interpretation": True,
            "prediction": None,
            "dice": None,
            "score_contract": "Per-zone Dice; macro mean of foreground zones.",
        }
    else:
        mapping = (
            "PanTS source structure taxonomy is not represented without a matching label file."
            if key == "pancreas"
            else "PANTHER source MHA labels 1=tumor and 2=pancreatic parenchyma; staged Full GT separates whole pancreas (1∪2) and tumor (1) into two binary masks."
        )
        operation = {
            "type": "dual-binary-organ-lesion",
            "modality": "CT"
            if key == "pancreas"
            else "arterial T1 contrast-enhanced diagnostic MRI"
            if key == "panther-t1"
            else "T2-weighted MR-Linac radiotherapy-planning MRI",
            "source_mapping": mapping,
            "binary_outputs": [
                {"file": "organ.nii.gz", "foreground": "whole pancreas", "values": [0, 1]},
                {"file": "lesion.nii.gz", "foreground": "pancreatic tumor", "values": [0, 1]},
            ],
            "spatial_operation": "Predict two distinct same-grid 3D binary masks from each input volume; an organ-only mask does not supply the lesion output.",
        }
        output = {
            "type": "two-binary-masks",
            "files": [
                "agents_outputs/{case_id}/organ.nii.gz",
                "agents_outputs/{case_id}/lesion.nii.gz",
            ],
            "label_values": {"0": "background", "1": "foreground (per file)"},
            "same_spatial_shape_required": True,
            "affine_alignment_required_for_interpretation": True,
            "prediction": None,
            "dice": None,
            "score_contract": "Organ Dice and GT-positive-case lesion Dice, weighted equally and scaled by completion on partial submissions. Medal tier uses unscaled mean lesion Dice.",
        }
    helper = {
        "role": "public-upstream-training-label-helper" if prostate else "none",
        "slices": [f"training-label-{i}.png" for i in range(len(slices))] if prostate else [],
        "slice_label_voxels": helper_counts,
        "full_private_reference": None,
        "prediction": None,
        "warning": "The upstream training label is not a Full private target or a model prediction."
        if prostate
        else "No matching training label was acquired.",
    }
    dump(out / "source.json", source)
    dump(out / "operation.json", operation)
    dump(out / "output.json", output)
    dump(out / "helper.json", helper)
    (out / "NOTICE.md").write_text(
        notice["label"] + ". " + notice["text"] + " " + notice["url"] + "\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        LICENSE[key] + "; source details and restrictions in resolution receipt.\n"
    )
    items = []
    for p in sorted(out.iterdir()):
        if p.name == "manifest.json":
            continue
        # Training labels are ordinary supplied helper/teaching assets, never private references.
        items.append(
            {
                "file": p.name,
                "sha256": sha(p),
                "bytes": p.stat().st_size,
                "provenance": "source-derived-teaching" if real else "symbolic-protocol",
                "role": "illustration",
            }
        )
    dump(
        out / "manifest.json",
        {
            "id": f"retained-automed-full-{key}-seg-v1",
            "frame": "native-NIfTI-voxel-ijk" if real else "symbolic-NIfTI-grid",
            "units": "voxel",
            "license": LICENSE[key],
            "label_license": None if ct else LICENSE[key],
            "reference_policy": "no-reference-assets",
            "sources": sources,
            "checks": {
                "full_staged_case": False,
                "full_private_reference": False,
                "model_run": False,
                "scorer_run": False,
                "source_training_slices": 0 if ct else len(slices),
                "source_input_slices": len(slices) if ct else 0,
            },
            "assets": items,
        },
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--entry", choices=KEYS, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    args = p.parse_args()
    make(root(), args.entry, args.output, args.receipt)


if __name__ == "__main__":
    main()
