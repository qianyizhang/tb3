"""Render native ABRA teaching views from the audited retained CT/SEG pair."""

import argparse
import base64
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text())
    for path, digest in audit["source_pins"].items():
        assert sha(Path(path)) == digest
    for item in audit["source_files"]:
        assert sha(Path(item["local_path"])) == item["sha256"]
    out = args.output
    out.mkdir(parents=True, exist_ok=False)

    def write(name, value):
        (out / name).write_text(json.dumps(value, separators=(",", ":")) + "\n")

    def png(array):
        stream = io.BytesIO()
        Image.fromarray(array).save(stream, format="PNG")
        encoded = stream.getvalue()
        assert np.array_equal(np.asarray(Image.open(io.BytesIO(encoded))), array)
        return "data:image/png;base64," + base64.b64encode(encoded).decode()

    members = {row["k"]: row for row in audit["selected_native_members"]}
    full = []
    crops = []
    # Crop is explicitly reader/reference-selected, never a solver hint.
    crop = [313, 292, 424, 403]
    with zipfile.ZipFile("runs/task-brief-samples/abra/ct.zip") as archive:
        for k, item in sorted(members.items()):
            raw = archive.read(item["member"])
            assert hashlib.sha256(raw).hexdigest() == item["sha256"]
            ds = pydicom.dcmread(io.BytesIO(raw))
            hu = ds.pixel_array.astype(np.float64) * float(ds.RescaleSlope) + float(
                ds.RescaleIntercept
            )
            # DICOM LINEAR VOI: center -600, width 1500, native pixel geometry.
            gray = np.rint(np.clip((hu - (-600 - 0.5)) / (1500 - 1) + 0.5, 0, 1) * 255).astype(
                np.uint8
            )
            if k in [0, 64, 66, 68, 139]:
                full.append(
                    {"k": k, "png": png(gray), "origin_lps_mm": audit["origins_lps"][str(k)]}
                )
            if 62 <= k <= 69:
                crops.append({"k": k, "png": png(gray[crop[1] : crop[3], crop[0] : crop[2]])})
    write(
        "inputs.json",
        {
            "case": audit["case"],
            "shape": audit["ct_shape"],
            "spacing_mm": audit["spacing_mm"],
            "slice_step_mm": audit["slice_step_mm"],
            "orientation_lps": audit["orientation_lps"],
            "series_uid": audit["ct_series_uid"],
            "study_uid": audit["study_uid"],
            "full": full,
            "window": {"center_hu": -600, "width_hu": 1500, "function": "DICOM LINEAR"},
            "target_k": 66,
        },
    )
    write(
        "reference.json",
        {
            "crop_bounds": crop,
            "crops": crops,
            "frames": audit["frames"],
            "ordinary": audit["ordinary"],
            "oracle": audit["oracle"],
            "scorer_arithmetic": audit["scorer_arithmetic"],
            "scope": audit["scope"],
        },
    )
    (out / "NOTICE.md").write_text("""# ABRA annotation source views

Native LIDC-IDRI-0003 CT (140 axial slices) and DICOM-LIDC-IDRI-Nodules SEG,
Nodule 1 / Annotation 12, are retained from the 2026-09-21 sample receipt.
Five full slices and eight reader-selected 111 x 111 crops use DICOM LINEAR
window center -600 HU, width 1500 HU. Native rows/columns are not resampled.
Patient right appears at image left. Pixel centers are zero-based (x=column,
y=row); display overlays add one half pixel in SVG coordinates. In-plane spacing
is 0.820312 mm; ascending patient-z slices are 2.5 mm apart. The crop origin
(313,292) is a reader-selected reference aid, never a supplied target location.

The pinned ABRA manifest lists one annotator for Nodule 1. All eight masks align
by source SOP UID, position, orientation and spacing. Replaying the selected pure
consensus and task-generator functions reproduces that single mask and yields
ordinary s066 and oracle Nodule 1 tasks targeting the same slice. Contours use
the largest marching-squares component at level 0.5, in native pixel coordinates.
This does not validate other nodules or reproduce a published benchmark run.

The ordinary task supplies slice 66 and a lung window; its reference is private.
The separate oracle task deliberately supplies reference-derived contours and
hardcoded confidence values through a callable tool. The oracle is not newly run
pathology inference. Reference-copy annotations and slice-penalty arithmetic are
author teaching examples, not saved agent answers or measured model performance.
Full Shapely scoring and OHIF interaction were not executed. The pure penalty
function and source logic, not a fabricated benchmark run, support the displayed
same-polygon arithmetic. Shape normalization is heuristic, not proven optimal.

Data attribution: Armato et al., LIDC-IDRI, TCIA, DOI 10.7937/K9/TCIA.2015.LO9QL9SX;
Fedorov et al., DICOM-LIDC-IDRI-Nodules, DOI 10.7937/TCIA.2018.h7umfurq.
Both data sources list CC BY 3.0. ABRA code is MIT at commit
688814615dc368a66276798cb864fe9a587d7e6c. No clinical or model accuracy is inferred.
Rebuild with scripts/audit_abra_annotation.py and scripts/build_abra_annotation_assets.py
into fresh local destinations. Exact source and derivation hashes are in the audit.
""")
    (out / "DATA-LICENSE.txt").write_text("""Selected native CT and SEG-derived contours: CC BY 3.0.
https://creativecommons.org/licenses/by/3.0/
https://www.cancerimagingarchive.net/collection/lidc-idri/
https://www.cancerimagingarchive.net/analysis-result/dicom-lidc-idri-nodules/
Attribution and transformations: NOTICE.md. Public source listings checked 2026-09-28.
""")
    manifest = {
        "id": "retained-abra-annotation-v1",
        "frame": "LPS",
        "units": "mm",
        "license": "CC-BY-3.0",
        "label_license": "CC-BY-3.0",
        "reference_policy": "reader-reference-reveal",
        "sources": {
            "presentation/external-tasks/sources/abra-annotation-audit.json": sha(
                Path("presentation/external-tasks/sources/abra-annotation-audit.json")
            ),
            "scripts/build_abra_annotation_assets.py": sha(Path(__file__)),
        },
        "checks": {
            "native_png_roundtrip": True,
            "full_views": len(full),
            "reference_crops": len(crops),
            "no_native_resampling": True,
            "aligned_seg_frames": 8,
            "single_annotator_consensus": True,
            "task_generator_replay": True,
            "model_or_viewer_run": False,
        },
        "assets": [
            {
                "file": name,
                "sha256": sha(out / name),
                "bytes": (out / name).stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
            }
            for name in ["inputs.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"]
        ],
    }
    write("manifest.json", manifest)
    print(json.dumps({"output": str(out), "checks": manifest["checks"]}))


if __name__ == "__main__":
    main()
