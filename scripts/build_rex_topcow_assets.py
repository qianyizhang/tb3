"""Build native TopCoW CTA views with held-out labels gated for reader reveal."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image

COLORS = [
    "#ffd166",
    "#69aaff",
    "#e18dff",
    "#49cfac",
    "#ff906e",
    "#71d9df",
    "#e98ab8",
    "#c6b96a",
    "#a6df75",
    "#ffffff",
    "#ffcd8b",
    "#c9a4ff",
    "#f09de4",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png(array):
    stream = io.BytesIO()
    Image.fromarray(array).save(stream, format="PNG")
    raw = stream.getvalue()
    assert np.array_equal(array, np.asarray(Image.open(io.BytesIO(raw))))
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    audit = json.loads(args.audit.read_text())
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    for row in audit["native_assets"]:
        assert sha(Path(row["local_path"])) == row["sha256"]
    img = nib.load(audit["native_assets"][0]["local_path"])
    mask = nib.load(audit["native_assets"][1]["local_path"])
    assert img.shape == mask.shape == (266, 371, 311)
    assert np.allclose(img.affine, mask.affine)
    ct, labels = np.asarray(img.dataobj), np.asarray(mask.dataobj)
    assert nib.aff2axcodes(img.affine) == ("L", "P", "S")
    ids = [int(k) for k in audit["label_map"] if int(k)]
    assert len(ids) == len(COLORS) == 13
    palette = {
        k: [int(c[i : i + 2], 16) for i in [1, 3, 5]] + [180]
        for k, c in zip(ids, COLORS, strict=True)
    }

    def write(name, data):
        (out / name).write_text(json.dumps(data, separators=(",", ":")) + "\n")

    views, references = [], []
    for z in [108, 118, 128]:
        # Native x increases leftward, native y posteriorly. Display right rightward,
        # anterior upward by transposing x/y and reversing displayed columns.
        gray = np.rint(
            np.clip((ct[:, :, z].T[:, ::-1].astype(float) + 100) / 800, 0, 1) * 255
        ).astype(np.uint8)
        native_labels = labels[:, :, z].T[:, ::-1]
        rgba = np.zeros((*native_labels.shape, 4), dtype=np.uint8)
        for label, color in palette.items():
            rgba[native_labels == label] = color
        # Source CoW ROI x86:188, y113:178, z96:138. Native display reversal
        # moves x86:188 to columns78:180; there is no interpolation/resampling.
        crop = gray[113:178, 78:180]
        overlay_crop = rgba[113:178, 78:180]
        assert crop.shape == (65, 102)
        assert np.array_equal(
            crop,
            np.rint(
                np.clip((ct[86:188, 113:178, z].T[:, ::-1].astype(float) + 100) / 800, 0, 1) * 255
            ).astype(np.uint8),
        )
        views.append(
            {
                "z": z,
                "width": 266,
                "height": 371,
                "png": png(gray),
                "pixel_index_to_native_ijk": [[-1, 0, 265], [0, 1, 0], [0, 0, z]],
                "crop_pixel_index_to_native_ijk": [[-1, 0, 187], [0, 1, 113], [0, 0, z]],
            }
        )
        references.append(
            {
                "z": z,
                "png": png(rgba),
                "ct_crop_png": png(crop),
                "crop_png": png(overlay_crop),
                "crop_width": 102,
                "crop_height": 65,
                "plane_counts": {str(k): int((native_labels == k).sum()) for k in ids},
            }
        )
    write(
        "inputs.json",
        {
            "case": "topcow_ct_012",
            "partition": "ReX test under the pinned complete-release preparation",
            "views": views,
            "native": audit["native_assets"][0],
            "window_hu": [-100, 700],
            "selection": "Reader-selected z108/118/128, 5 mm apart, using source Acom labels. The CoW crop uses an annotation ROI unavailable to the solver for this test case; crop appears only with the reference reveal.",
            "crop_display_bounds": [78, 113, 102, 65],
        },
    )
    write(
        "reference.json",
        {
            "role": "Held-out source label for explicit reader reveal; no prediction",
            "views": references,
            "structures": [
                {
                    "id": k,
                    "name": audit["label_map"][str(k)],
                    "color": c,
                    "voxels": int((labels == k).sum()),
                }
                for k, c in zip(ids, COLORS, strict=True)
            ],
            "present_classes": 11,
            "absent_annotation_ids": [8, 15],
        },
    )
    repro = audit["nonclinical_reproduction"]
    write(
        "contract.json",
        {
            "revision": audit["source_commit"],
            "split": audit["split"],
            "label_map": audit["label_map"],
            "fixtures": repro["fixtures"],
            "geometry": repro["geometry_fragment"],
            "ranking": repro["ranking_fixture"],
            "metric_directions": audit["metric_directions"],
            "limits": repro["limits"],
            "submission": {
                "columns": ["image_id", "modality", "predicted_mask_path"],
                "example": ["012", "CTA", "predictions/topcow_ct_012_0000.nii.gz"],
            },
        },
    )
    (out / "NOTICE.md").write_text("""# ReX-MLE TopCoW CTA teaching assets

TopCoW 2024 CTA case012, source release https://zenodo.org/records/15692630.
Yang et al., Benchmarking the CoW with the TopCoW Challenge: Topology-Aware
Anatomical Segmentation of the Circle of Willis for CTA and MRA, arXiv:2312.17670.
Data owner: University Hospital of Zurich, Department of Neurology.
Non-commercial use with source attribution; commercial use needs owner permission.
The source License.txt is preserved as DATA-LICENSE.txt. No medical prediction or
model training is represented; these assets are a local teaching derivative.

The complete ZIP64 directory and the pinned ReX-MLE preparer establish 100 training
and 25 test cases when all 125 matched CTA pairs are supplied. Case012 is in the
ReX test subset, although its labels are public in the upstream challenge training
release. Its mask is therefore a held-out reader reference, never a solver helper.
Original source receipts and earlier preview images remain unchanged.

Native CT/mask: 266x371x311, spacing 0.498046875x0.498046875x0.5mm, LPS native axes
with an RAS physical affine. CT intensities are obtained through the NIfTI scaling.
PNG display clamps -100..700 HU to rounded 8-bit gray, transposes native x/y and
reverses displayed columns so right is rightward and anterior is upward.
Axial z108/118/128 are 5mm apart. z118 is chosen post hoc using the Acom reference.
All native pixels remain intact; this is not a blind search trajectory.

The source ROI x86:188,y113:178,z96:138 supplies a reader-only CoW crop at native
resolution 102x65. It appears only after reference reveal. The crop has its own
labeled magnification and does not imply new resolution. Full-volume labels can
extend beyond this ROI. Colors match all 13 named foreground IDs (1-12 and 15);
IDs 8 and 15 have zero occupancy in this annotation. Annotation absence is not an
independent clinical judgment. Alpha180/255 overlays retain exact source voxels.

Nonclinical 9x9x9 label fixtures explain selected Dice, binary clDice, B0 and
presence/IoU-based topology metrics. They are neither patient masks nor model
outputs. HD95 and the complete grader were not executed; MONAI is absent locally.
The source UInt8/CopyInformation preprocessing fragment and a leaderboard tie
fixture are separately identified. Dataset geometry requirements still apply.

Rebuild from scripts/audit_rex_topcow.py and scripts/build_rex_topcow_assets.py,
each into a new local destination. Source and fixture details remain in the audit.
""")
    license_record = next(
        r for r in audit["source_license_records"] if r["path"].endswith("License.txt")
    )
    license_path = Path(license_record["path"])
    assert sha(license_path) == license_record["sha256"]
    (out / "DATA-LICENSE.txt").write_bytes(license_path.read_bytes())
    files = ["inputs.json", "reference.json", "contract.json", "NOTICE.md", "DATA-LICENSE.txt"]
    write(
        "manifest.json",
        {
            "id": "retained-rex-topcow-v1",
            "frame": "RAS",
            "units": "mm",
            "license": "LicenseRef-TopCoW-OpenDataSwiss",
            "label_license": "LicenseRef-TopCoW-OpenDataSwiss",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(args.audit): sha(args.audit),
                "scripts/build_rex_topcow_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "png_roundtrip": True,
                "no_native_resampling": True,
                "native_views": 3,
                "shared_native_geometry": True,
                "source_case_partition": "test",
                "full_volume_present_classes": 11,
                "source_crc_matches": 3,
                "nonclinical_fixtures": 5,
                "model_run": False,
            },
            "assets": [
                {
                    "file": n,
                    "sha256": sha(out / n),
                    "bytes": (out / n).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal" if n == "reference.json" else "illustration",
                }
                for n in files
            ],
        },
    )
    print(
        json.dumps(
            {"output": str(out), "native_views": 3, "reference_classes": 13, "test_reference": True}
        )
    )


if __name__ == "__main__":
    main()
