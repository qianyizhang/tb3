"""Build a bounded real-CT, source-pinned ABRA longitudinal teaching pack.

Reads only retained official NLST ZIPs and audited metadata. No ABRA module,
model, viewer, evaluator or clinical inference is executed.
"""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import sys
import zipfile
from pathlib import Path

from PIL import Image


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "workbench.toml").is_file())
RECEIPT = Path("presentation/external-tasks/sources/abra-longitudinal-resolution.json")
SOURCE_ROOT = Path(".local/explainers/core-20260929/abra-longitudinal-source")
PACK_ID = "retained-abra-longitudinal-v1"
CENTER_HU, WIDTH_HU = -600, 1500
SAMPLE_COUNT = 16


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def selected_instance_numbers(count: int) -> list[int]:
    numbers = [1 + round(i * (count - 1) / (SAMPLE_COUNT - 1)) for i in range(SAMPLE_COUNT)]
    assert len(numbers) == len(set(numbers)) == SAMPLE_COUNT
    assert numbers[0] == 1 and numbers[-1] == count
    return numbers


def render_dicom(data: bytes, row: dict, destination: Path) -> None:
    assert row["transfer_syntax"] == "1.2.840.10008.1.2.1"
    assert row["rows"] == row["columns"] == 512
    assert row["rescale_slope"] == 1 and row["rescale_intercept_hu"] == -1024
    tag = b"\xe0\x7f\x10\x00OW\x00\x00"
    at = data.find(tag)
    assert at > 0
    nbytes = int.from_bytes(data[at + 8 : at + 12], "little")
    assert nbytes == 512 * 512 * 2 == row["pixel_bytes"]
    pixels = array.array("H")
    pixels.frombytes(data[at + 12 : at + 12 + nbytes])
    if sys.byteorder != "little":
        pixels.byteswap()
    lo = CENTER_HU - WIDTH_HU / 2
    gray = bytes(max(0, min(255, round((v - 1024 - lo) * 255 / WIDTH_HU))) for v in pixels)
    Image.frombytes("L", (512, 512), gray).save(destination, optimize=True)


def build(repo_root: Path, output: Path, receipt_path: Path, source_root: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing destination: {output}")
    receipt = json.loads(receipt_path.read_text())
    if (
        receipt.get("entry_id") != "abra-longitudinal"
        or receipt.get("illustration_basis") != "mixed"
    ):
        raise ValueError("Wrong ABRA receipt or basis")
    if any(not a.get("attempted_at") or not a.get("source") for a in receipt["attempts"]):
        raise ValueError("Every source attempt needs a timestamp and source")
    if receipt["source_commit"] != "688814615dc368a66276798cb864fe9a587d7e6c":
        raise ValueError("Changed ABRA commit")
    pair_path = source_root / "pinned-source/nlst_longct_pairs.json"
    pair_sha = next(x["sha256"] for x in receipt["source_files"] if x["role"] == "pair-manifest")
    if sha(pair_path) != pair_sha:
        raise ValueError("Changed pinned pair manifest")
    pair = json.loads(pair_path.read_text())[0]
    assert pair["participant_id"] == "110494"

    # Only after every source preflight succeeds do we create a fresh output.
    series_data = []
    for series in receipt["full_native_series"]:
        role = series["role"]
        zip_path = source_root / "samples" / f"{role}-full-series.zip"
        inv_path = source_root / "samples" / f"{role}-full-series-inventory.json"
        if sha(zip_path) != series["archive_sha256"] or sha(inv_path) != series["inventory_sha256"]:
            raise ValueError(f"Changed {role} native source")
        inventory = json.loads(inv_path.read_text())
        if len(inventory) != series["instance_count"]:
            raise ValueError(f"Changed {role} instance count")
        if {x["sop_uid"] for x in inventory} != {
            x["SOPInstanceUID"]
            for x in json.loads((source_root / "samples" / f"{role}-sops.json").read_text())
        }:
            raise ValueError(f"Changed {role} official SOP set")
        series_data.append((series, zip_path, inventory))

    output.mkdir(parents=True)
    (output / "images").mkdir()
    with (
        zipfile.ZipFile(series_data[0][1]) as baseline_archive,
        zipfile.ZipFile(series_data[1][1]) as followup_archive,
    ):
        nlst_license = baseline_archive.read("LICENSE")
        if followup_archive.read("LICENSE") != nlst_license:
            raise ValueError("NLST archive license texts differ")
    (output / "NLST-LICENSE.txt").write_bytes(nlst_license)
    visits = []
    asset_paths = []
    for series, zip_path, inventory in series_data:
        role = series["role"]
        by_instance = {x["instance_number"]: x for x in inventory}
        samples = []
        with zipfile.ZipFile(zip_path) as archive:
            assert archive.testzip() is None
            for order, number in enumerate(selected_instance_numbers(series["instance_count"])):
                row = by_instance[number]
                data = archive.read(row["member"])
                if hashlib.sha256(data).hexdigest() != row["sha256"]:
                    raise ValueError(f"Changed {role} DICOM member {row['member']}")
                name = f"images/{role}-{order:02d}.png"
                render_dicom(data, row, output / name)
                asset_paths.append(name)
                samples.append(
                    {
                        "sample_order_zero_based": order,
                        "image": name,
                        "instance_number": number,
                        "sop_uid": row["sop_uid"],
                        "source_zip_member": row["member"],
                        "source_dicom_sha256": row["sha256"],
                        "image_position_lps_mm": row["image_position_lps_mm"],
                        "pixel_spacing_row_col_mm": row["pixel_spacing_row_col_mm"],
                        "rows_columns": [512, 512],
                        "viewer_slice_index": None,
                    }
                )
        visits.append(
            {
                "role": role,
                "study_uid": series["study_uid"],
                "series_uid": series["series_uid"],
                "study_date_yyyymmdd": "19990102" if role == "baseline" else "20000102",
                "kernel": "B50f" if role == "baseline" else "B30f",
                "native_instance_count": series["instance_count"],
                "sample_count": SAMPLE_COUNT,
                "sample_rule": "InstanceNumber nearest to 16 equally spaced endpoints from 1 through N; no viewer index mapping",
                "samples": samples,
            }
        )

    source = {
        "frame": "per-study native DICOM LPS; coordinates are not registered across visits",
        "units": "mm for DICOM positions and spacing; HU before display transform",
        "visits": visits,
        "display": {
            "window_center_hu": CENTER_HU,
            "window_width_hu": WIDTH_HU,
            "formula": "clip(round((stored_value - 1024 - (-1350)) * 255 / 1500), 0, 255)",
            "output": "8-bit grayscale display only",
        },
        "source_roles": {
            "input": "exact official NLST paired CT series",
            "helper": "ABRA supplied pairing, IDs, metadata/image/navigation/submission tools",
            "answer": "not retained",
        },
        "viewer_order_verified": False,
        "cross_study_registration": False,
    }
    output_state = {
        "status": "not-retained",
        "agent_answer": None,
        "agent_finding": None,
        "agent_score": None,
        "note": "Output sockets are schema only; no ABRA agent run exists.",
    }
    reference = {
        "role": "reader-only source reference; never solver input or initial DOM",
        "interval_days": 365,
        "slice_count_followup_minus_baseline": 1,
        "single_lesion": {
            "finding_type": "new_lesion",
            "viewer_slice_index_zero_based": 23,
            "pixel_x": 262,
            "pixel_y": 355,
            "lesion_id": "110494_L1",
            "sop_mapping_verified": False,
            "patient_image_overlay_allowed": False,
        },
        "scorer": {
            "metadata": "normalized exact match",
            "single_point_threshold_px": 20,
            "multi_point_threshold_px": 20,
            "multi_false_positive_penalty": 0.1,
        },
        "clinical_truth_adjudicated_here": False,
    }
    write_json(output / "source.json", source)
    write_json(output / "output.json", output_state)
    write_json(output / "reference.json", reference)
    (output / "NOTICE.md").write_text(
        "# ABRA longitudinal local teaching pack\n\n"
        "The 32 grayscale PNGs are display-only, fixed-window derivatives of exact NLST "
        "DICOM series selected by pinned ABRA commit 6888146. The full native ZIPs remain "
        "local outside this bounded pack. NLST data are CC BY 4.0; source route: "
        "https://www.cancerimagingarchive.net/collection/nlst/. ABRA code is MIT. "
        "Pair-manifest coordinates are in a separate reader-only reference file.\n\n"
        "The two studies are not registered. Equal LPS-z numbers or sampled positions "
        "do not imply matching anatomy; inspected equal-z inputs showed different chest "
        "levels. The ABRA viewer index-to-SOP mapping remains unverified, so no private "
        "point is drawn on CT. No agent answer, score or radiologic adjudication was generated.\n"
    )
    asset_paths.extend(
        ["source.json", "output.json", "reference.json", "NOTICE.md", "NLST-LICENSE.txt"]
    )
    assets = [
        {
            "file": name,
            "sha256": sha(output / name),
            "bytes": (output / name).stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
        }
        for name in asset_paths
    ]
    write_json(
        output / "manifest.json",
        {
            "schema": 1,
            "id": PACK_ID,
            "frame": "NLST-native-LPS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "LicenseRef-ABRA-pair-manifest",
            "reference_policy": "reader-reference-reveal",
            "source_class": "source-derived-teaching",
            "illustration_basis": "mixed",
            "sources": {
                str(RECEIPT): sha(receipt_path),
                str(SOURCE_ROOT / "pinned-source/nlst_longct_pairs.json"): sha(pair_path),
                **{
                    str(SOURCE_ROOT / "samples" / f"{x['role']}-full-series.zip"): x[
                        "archive_sha256"
                    ]
                    for x, _, _ in series_data
                },
            },
            "checks": {
                "actual_selected_ct": True,
                "complete_native_series_locally_retained": True,
                "sampled_native_slices_per_visit": SAMPLE_COUNT,
                "agent_output_retained": False,
                "viewer_reference_sop_mapped": False,
                "cross_study_registration": False,
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", required=True, type=Path, help="fresh destination; refuse overwrite"
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--receipt", type=Path, help="isolated staged receipt override")
    parser.add_argument("--source-root", type=Path, help="retained native source override")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    build(
        root,
        args.output.resolve(),
        (args.receipt or root / RECEIPT).resolve(),
        (args.source_root or root / SOURCE_ROOT).resolve(),
    )
