"""Build four Full task teaching packs from pinned contracts and available public CTs.

This reads sources only. It never executes a task adapter, model, preparer, or scorer.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image

KEYS = ("hepaticvessel", "kidney", "liver", "pancreas-oar")
SRC = Path(".local/explainers/core-20260929/automed-seg-b-source")
LABELS = {
    "hepaticvessel": {"0": "background", "1": "hepatic_vessel", "2": "hepatic_tumor"},
    "kidney": {"0": "background", "1": "foreground"},
    "liver": {"0": "background", "1": "foreground"},
    "pancreas-oar": {
        "0": "background",
        "1": "adrenal_gland_left",
        "2": "adrenal_gland_right",
        "3": "aorta",
        "4": "bladder",
        "6": "colon",
        "8": "duodenum",
        "9": "femur_left",
        "10": "femur_right",
        "11": "gall_bladder",
        "12": "kidney_left",
        "13": "kidney_right",
        "14": "liver",
        "15": "lung_left",
        "16": "lung_right",
        "17": "pancreas",
        "22": "pancreatic_lesion",
        "23": "postcava",
        "24": "prostate",
        "25": "spleen",
        "26": "stomach",
        "28": "veins",
    },
}


def root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "presentation/EXPLAINER-SCOPE.json").exists():
            return parent
    raise RuntimeError("tb3 root not found")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")


def nifti(path: Path, *, pants_verified_identity: bool = False):
    with gzip.open(path, "rb") as stream:
        data = stream.read()
    endian = "<" if struct.unpack_from("<i", data)[0] == 348 else ">"
    assert struct.unpack_from(endian + "i", data)[0] == 348
    d = struct.unpack_from(endian + "8h", data, 40)
    shape = tuple(int(v) for v in d[1 : d[0] + 1])
    spacing = list(struct.unpack_from(endian + "8f", data, 76)[1 : d[0] + 1])
    slope, intercept = struct.unpack_from(endian + "2f", data, 112)
    # Read on-disk header bytes directly; nibabel may clear scaling after load.
    if (slope, intercept) != (1.0, 0.0):
        raise ValueError("Expected verified identity NIfTI scaling in pinned source")
    datatype = struct.unpack_from(endian + "h", data, 70)[0]
    bitpix = struct.unpack_from(endian + "h", data, 72)[0]
    offset = int(struct.unpack_from(endian + "f", data, 108)[0])
    dtype = {2: "u1", 4: "i2", 8: "i4", 16: "f4", 64: "f8"}[datatype]
    arr = np.frombuffer(
        data, dtype=np.dtype(endian + dtype), count=int(np.prod(shape)), offset=offset
    ).reshape(shape, order="F")
    assert arr.size * (bitpix // 8) + offset <= len(data)
    sform = struct.unpack_from(endian + "h", data, 254)[0]
    affine = (
        [list(struct.unpack_from(endian + "4f", data, 280 + 16 * j)) for j in range(3)]
        if sform
        else None
    )
    geometry = {
        "shape_ijk": shape,
        "voxel_spacing_mm": spacing,
        "affine_first_three_rows": affine,
        "slice_axis_ijk": 2,
        "stored_value_scaling": {"slope": slope, "intercept": intercept}
        if not pants_verified_identity
        else {
            "raw_header_slope": slope,
            "raw_header_intercept": intercept,
            "effective_slope": 1.0,
            "effective_intercept": 0.0,
        },
        "datatype": datatype,
        "axis_display": "flipud(native_i_j_slice.T)",
        "window_stored_values" if pants_verified_identity else "window_hu": [-160, 240],
    }
    if pants_verified_identity:
        geometry["uncompressed_nifti_sha256"] = hashlib.sha256(data).hexdigest()
        geometry["qform_code"] = struct.unpack_from(endian + "h", data, 252)[0]
        geometry["sform_code"] = sform
    return arr, geometry


def png_data_uri(arr: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(arr, mode="L").save(buf, format="PNG", optimize=False)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def rgba_data_uri(arr: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(arr, mode="RGBA").save(buf, format="PNG", optimize=False)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def slices(path: Path, *, pants_source: bool = False):
    volume, geometry = nifti(path, pants_verified_identity=pants_source)
    length = volume.shape[2]
    indices = sorted({min(length - 1, max(0, round(length * f))) for f in (0.25, 0.5, 0.75)})
    selected = []
    for k in indices:
        plane = volume[:, :, k]
        grey = np.rint(np.clip((plane.astype(np.float32) + 160) / 400, 0, 1) * 255).astype(np.uint8)
        selected.append(
            {
                "native_index": k,
                "ct_png": png_data_uri(np.flipud(grey.T)),
                ("source_min_stored" if pants_source else "source_min_hu"): float(np.min(plane)),
                ("source_max_stored" if pants_source else "source_max_hu"): float(np.max(plane)),
            }
        )
    return selected, geometry


def make(r: Path, key: str, out: Path, receipt: Path):
    if key not in KEYS:
        raise ValueError(key)
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite {out}")
    builder = Path(__file__).resolve()
    receipt = receipt.absolute()
    if builder == (r / "scripts/build_automed_seg_b_assets.py").resolve():
        live_receipt = (
            r
            / "presentation/external-tasks/sources"
            / f"automedbench-full-{key}-seg-task-resolution.json"
        )
        if receipt != live_receipt or receipt.is_symlink():
            raise ValueError("Live builder requires the matching live resolution receipt")
    receipt = receipt.resolve()
    d = json.loads(receipt.read_text())
    assert d["entry_id"] == f"automedbench-full-{key}-seg-task" and all(
        a.get("attempted_at") for a in d["attempts"]
    )
    pkg = r / SRC / "packages" / f"{key}.tar.gz"
    assert sha(pkg) == d["task_package"]["sha256"]
    for rel, pin in d["task_package"]["pinned_files"].items():
        p = r / SRC / "packages" / key / "automedbench-task" / rel
        assert sha(p) == pin["sha256"]
    example = d["source_example"]
    sample_slices = []
    geometry = None
    reference = None
    sources = {
        str(pkg.relative_to(r)): sha(pkg),
        str(receipt.relative_to(r)): sha(receipt),
        str(builder.relative_to(r)): sha(builder),
    }
    if key in ("hepaticvessel", "liver"):
        p = r / example["path"]
        assert sha(p) == example["sha256"]
        sources[example["path"]] = example["sha256"]
        sample_slices, geometry = slices(p)
        if key == "liver":
            source_ref = d["source_reference"]
            label_path = r / source_ref["path"]
            attempt_path = r / source_ref["recovery_receipt_path"]
            prior_path = r / source_ref["prior_attempt_receipt_path"]
            assert sha(label_path) == source_ref["sha256"]
            assert sha(attempt_path) == source_ref["recovery_receipt_sha256"]
            assert sha(prior_path) == source_ref["prior_attempt_receipt_sha256"]
            attempt = json.loads(attempt_path.read_text())
            member = attempt["tar_member"]
            assert member["path"] == "Task03_Liver/labelsTr/liver_53.nii.gz"
            assert member["data_offset"] == source_ref["tar_data_offset"]
            assert member["bytes"] == label_path.stat().st_size
            assert attempt["label_sha256"] == source_ref["sha256"]
            assert attempt["ct_sha256"] == example["sha256"]
            labels, label_geometry = nifti(label_path)
            assert tuple(labels.shape) == tuple(geometry["shape_ijk"])
            assert label_geometry["affine_first_three_rows"] == geometry["affine_first_three_rows"]
            assert set(np.unique(labels).tolist()) == {0, 1, 2}
            assert [v["native_index"] for v in sample_slices] == [26, 52, 79]
            # An explicitly post-hoc source-label-guided teaching plane follows
            # the three existing fixed CT samples; ties choose the lower k.
            lesion_by_k = np.count_nonzero(labels == 2, axis=(0, 1))
            illustrative_k = int(np.argmax(lesion_by_k))
            assert illustrative_k == source_ref["illustrative_plane_native_k"]
            assert illustrative_k not in (26, 52, 79)
            ct_volume, _ = nifti(p)
            plane = ct_volume[:, :, illustrative_k]
            grey = np.rint(np.clip((plane.astype(np.float32) + 160) / 400, 0, 1) * 255).astype(
                np.uint8
            )
            sample_slices.append(
                {
                    "native_index": illustrative_k,
                    "ct_png": png_data_uri(np.flipud(grey.T)),
                    "source_min_hu": float(np.min(plane)),
                    "source_max_hu": float(np.max(plane)),
                }
            )
            geometry["view_selection"] = {
                "first_three_native_k": [26, 52, 79],
                "fourth_native_k": illustrative_k,
                "fourth_rule": "post-hoc public source label 2 maximum on native k; lower-index tie break",
                "interpretation": "label-guided teaching view, not unbiased input sampling or Full benchmark evidence",
            }
            sources[source_ref["path"]] = source_ref["sha256"]
            sources[source_ref["recovery_receipt_path"]] = source_ref["recovery_receipt_sha256"]
            sources[source_ref["prior_attempt_receipt_path"]] = source_ref[
                "prior_attempt_receipt_sha256"
            ]
            views = []
            for sample in sample_slices:
                k = sample["native_index"]
                plane = labels[:, :, k]
                organ = plane == 1
                lesion = plane == 2
                overlay = np.zeros((*plane.shape, 4), dtype=np.uint8)
                overlay[organ] = (31, 187, 197, 135)
                overlay[lesion] = (250, 183, 56, 180)
                views.append(
                    {
                        "index": k,
                        "overlay_png": rgba_data_uri(np.flipud(overlay.transpose(1, 0, 2))),
                        "organ_voxels": int(np.count_nonzero(plane > 0)),
                        "lesion_voxels": int(np.count_nonzero(lesion)),
                    }
                )
            reference = {
                "role": "reader-only-public-MSD-Task03-source-annotation-not-Full-private-GT",
                "mapping": [
                    {
                        "target": "organ.nii.gz",
                        "rule": "source label 1 OR 2 (teaching conversion; Full overlap unverified)",
                        "color": "#1fbbc5",
                    },
                    {
                        "target": "lesion.nii.gz",
                        "rule": "source label 2 (teaching conversion; Full mapping unverified)",
                        "color": "#fab738",
                    },
                ],
                "views": views,
                "full_private_reference": None,
                "prediction": None,
            }
    elif key == "pancreas-oar":
        p = r / example["path"]
        integrity_path = r / example["native_integrity_path"]
        correction_path = r / example["native_header_correction_path"]
        acquisition_path = r / example["acquisition_receipt_path"]
        assert sha(p) == example["sha256"]
        assert sha(integrity_path) == example["native_integrity_sha256"]
        assert sha(correction_path) == example["native_header_correction_sha256"]
        assert sha(acquisition_path) == example["acquisition_receipt_sha256"]
        integrity = json.loads(integrity_path.read_text())[example["case_id"]]
        correction = json.loads(correction_path.read_text())
        assert integrity["compressed_sha256"] == example["sha256"]
        assert correction["source_sha256"] == example["sha256"]
        assert correction["prior_integrity_sha256"] == example["native_integrity_sha256"]
        assert correction["on_disk_header"] == {"scl_slope": 1.0, "scl_inter": 0.0}
        assert correction["nibabel_dataobj_proxy"] == {"slope": 1.0, "intercept": 0.0}
        assert integrity["nested_gzip_crc_valid"] is True
        sample_slices, geometry = slices(p, pants_source=True)
        assert (
            [v["native_index"] for v in sample_slices]
            == example["selected_native_k"]
            == [38, 76, 114]
        )
        assert list(geometry["shape_ijk"]) == example["shape_ijk"] == integrity["shape_ijk"]
        assert (
            list(geometry["voxel_spacing_mm"])
            == example["voxel_spacing_mm"]
            == integrity["voxel_spacing_mm"]
        )
        assert geometry["datatype"] == 4 and integrity["stored_datatype"] == "int16"
        assert geometry["qform_code"] == 0 and geometry["sform_code"] == 2
        assert geometry["uncompressed_nifti_sha256"] == integrity["uncompressed_nifti_sha256"]
        assert geometry["affine_first_three_rows"] == integrity["selected_affine"][:3]
        assert example["axis_codes"] == "RAS" and integrity["axis_codes"] == ["R", "A", "S"]
        assert integrity["nib_dataobj_slope"] == 1.0 and integrity["nib_dataobj_inter"] == 0.0
        assert geometry["window_stored_values"] == example["display_window_stored_values"]
        geometry["axis_codes"] = "RAS"
        geometry["intensity_unit"] = "stored-value; HU calibration unverified"
        geometry["view_selection"] = {"native_k": [38, 76, 114], "rule": example["selection_rule"]}
        sources[example["path"]] = example["sha256"]
        sources[example["native_integrity_path"]] = example["native_integrity_sha256"]
        sources[example["native_header_correction_path"]] = example[
            "native_header_correction_sha256"
        ]
        sources[example["acquisition_receipt_path"]] = example["acquisition_receipt_sha256"]
    elif key == "kidney":
        for p_key, sha_key in (("path", "sha256"), ("label_path", "label_sha256")):
            assert sha(r / example[p_key]) == example[sha_key]
            sources[example[p_key]] = example[sha_key]
        legacy_source = r / "presentation/task-explorer/automed-kidney/source.json"
        legacy_ref = r / "presentation/task-explorer/automed-kidney/reference.json"
        source_doc = json.loads(legacy_source.read_text())
        reference_doc = json.loads(legacy_ref.read_text())
        assert source_doc["source_sha256"] == example["sha256"]
        assert reference_doc["source_sha256"] == example["label_sha256"]
        sources[str(legacy_source.relative_to(r))] = sha(legacy_source)
        sources[str(legacy_ref.relative_to(r))] = sha(legacy_ref)
        sample_slices = [
            {"native_index": v["index"], "ct_png": v["ct_png"]} for v in source_doc["views"]
        ]
        geometry = {
            "shape_ijk": source_doc["shape"],
            "voxel_spacing_mm": source_doc["spacing_mm"],
            "affine_first_three_rows": source_doc["affine"][:3],
            "slice_axis_ijk": 0,
            "axis_display": "retained KiTS19 source pack native axial projection along voxel i",
            "window_hu": [-160, 240],
        }
        reference = {
            "role": "reader-only-public-KiTS19-source-annotation-not-Full-private-GT",
            "mapping": reference_doc["mapping"],
            "views": reference_doc["views"],
            "full_private_reference": None,
            "prediction": None,
        }
    out.mkdir(parents=True)
    notice = {
        "label": "Upstream teaching image; Full case unverified"
        if sample_slices
        else "Symbolic PanTS contract",
        "text": d["actual_data_gap"],
        "url": d["acquisition_route"],
    }
    if key == "pancreas-oar":
        notice["label"] = "Public PanTSMini CT; Full case unverified"
        notice["text"] = (
            "No matched label, private GT or result. Obtain paired data through the official PanTS route."
        )
    public_example = (
        {k: v for k, v in example.items() if k not in ("label_path", "label_sha256")}
        if example
        else None
    )
    source = {
        "entry_id": d["entry_id"],
        "role": "official-upstream-example-not-proven-Full-staging"
        if sample_slices
        else "document-pinned-symbolic-protocol",
        "native_geometry": geometry,
        "views": sample_slices,
        "input_filename": "ct.nii.gz",
        "notice": notice,
        "license": d["source_license"],
        "full_case_membership": "unverified",
        "full_case_available": False,
        "upstream_example_available": bool(sample_slices),
        "source_example": public_example,
    }
    output = {
        "role": "required-empty-output-schema",
        "paths": d["task_package"]["output_contract"]["paths"],
        "root": "agents_outputs",
        "prediction": None,
        "score": None,
        "private_reference": None,
        "labels": LABELS[key],
        "mask_layout": "separate-binary" if key in ("kidney", "liver") else "combined-integer",
        "same_shape_required": True,
        "physical_affine_should_match": True,
        "scorer_checks_affine": False,
        "scoring_note": "Macro Dice across vessel and tumor after rounding labels. Separated GT is fused in ID order: tumor 2 overwrites vessel 1 at overlap. Both-empty Dice is 1; missing cases are skipped."
        if key == "hepaticvessel"
        else "Binary organ and lesion Dice; lesion mean is over GT-positive cases; package flags staging-path mismatch."
        if key == "kidney"
        else "Binary organ and lesion Dice; package leaves LiTS-vs-MSD provenance and staging path unresolved."
        if key == "liver"
        else "Config says GT-nonempty classes only, while pinned code includes all 21 IDs and treats both-empty as Dice 1; denominator unresolved.",
    }
    dump(out / "source.json", source)
    dump(out / "output.json", output)
    if reference is not None:
        dump(out / "reference.json", reference)
    (out / "NOTICE.md").write_text(
        notice["label"] + ". " + notice["text"] + " " + notice["url"] + "\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        d["source_license"] + ". Local source interpretation only. " + d["acquisition_route"] + "\n"
    )
    assets = []
    for name in ("source.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"):
        p = out / name
        if not p.exists():
            continue
        assets.append(
            {
                "file": name,
                "sha256": sha(p),
                "bytes": p.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
            }
        )
    dump(
        out / "manifest.json",
        {
            "id": f"retained-automed-full-{key}-seg-v1",
            "frame": "native-NIfTI-voxel-ijk" if geometry else "symbolic-unit-grid",
            "units": "voxel" if geometry else "unitless",
            "license": d["source_license"],
            "label_license": "CC-BY-NC-SA-4.0"
            if key == "kidney"
            else "CC-BY-SA-4.0"
            if key == "liver"
            else None,
            "reference_policy": d["reference_policy"],
            "sources": sources,
            "checks": {
                "full_staged_case": "unverified",
                "full_staged_case_available": False,
                "upstream_example_available": bool(sample_slices),
                "full_private_reference": False,
                "saved_prediction": False,
                "model_run": False,
                "scorer_run": False,
                "selected_source_slices": len(sample_slices),
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entry", required=True, choices=KEYS)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    make(root(), args.entry, args.output, args.receipt)
