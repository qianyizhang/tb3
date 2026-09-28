"""Build native MRI and public-contract views from the BCER teaching audit."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import SimpleITK as sitk
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text())
    for path, digest in audit["source_pins"].items():
        assert sha(Path(path)) == digest
    for row in audit["source_files"]:
        assert sha(Path(row["local_path"])) == row["sha256"]
    out = args.output
    out.mkdir(parents=True, exist_ok=False)

    def write(name, value):
        (out / name).write_text(json.dumps(value, separators=(",", ":")) + "\n")

    views = []
    for row in audit["sequences"]:
        image = sitk.ReadImage(row["original"])
        array = sitk.GetArrayFromImage(image)[row["slice_k"]]
        lo, hi = row["display_range"]
        gray = np.rint(np.clip((array.astype(float) - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        stream = io.BytesIO()
        Image.fromarray(gray).save(stream, format="PNG")
        raw = stream.getvalue()
        assert np.array_equal(np.asarray(Image.open(io.BytesIO(raw))), gray)
        views.append({**row, "png": "data:image/png;base64," + base64.b64encode(raw).decode()})
    t2 = sitk.ReadImage(audit["sequences"][0]["original"])
    witnesses = []
    for x in [160.0, 319.5, 480.0]:
        point = t2.TransformContinuousIndexToPhysicalPoint([x, 319.5, 10.0])
        ijks = [
            list(sitk.ReadImage(r["original"]).TransformPhysicalPointToContinuousIndex(point))
            for r in audit["sequences"]
        ]
        assert all(abs(v[2] - 10) < 1e-5 for v in ijks)
        witnesses.append({"lps_mm": list(point), "native_ijk": ijks})
    write("inputs.json", {"case": audit["case"], "sequences": views, "witnesses": witnesses})
    write(
        "contract.json",
        {
            k: audit[k]
            for k in [
                "task",
                "commit",
                "contract",
                "template",
                "manifest",
                "validator_examples",
                "scope",
            ]
        },
    )
    (out / "NOTICE.md").write_text("""# BCER prostate workflow teaching assets

Three native acquired MRI planes from PI-CAI case 10001_1000001, Twilt et al.,
Zenodo record 6624726 v2.0, DOI 10.5281/zenodo.6624726. Images are CC BY-NC 4.0.
The three retained MHA arrays equal their prepared NIfTI arrays exactly; spacing,
origin and direction differ by less than 1e-5 from representation precision.
One native k=10 plane per sequence is shown, without registration or image
resampling. Display uses each whole volume's 1st/99.5th percentiles, rounded
to 8-bit gray. Native pixels are stretched uniformly to the displayed panel;
panel sizes differ in physical field of view and are not a common physical scale.
LPS physical-coordinate witnesses use header geometry only; matching headers
do not establish anatomical registration. White crosses are author ruler points,
not lesions. SVG positions add half a native pixel to address voxel centers.

Public BCER contract/template excerpts are pinned at
d10816712793a9e27f2e70640f9afc06f08a0c5c; BCER-LICENSE.txt retains its MIT terms.
The old locally authored lowercase modality manifest is preserved unchanged.
A fresh derived manifest replays selected canonical modality rules on prepared
filenames; it is a representative input example, not an official BCER split.
Filename-derived modality flags are not a scan-quality or metadata assessment.

Five author nonclinical validator fixtures use a one-voxel 8 x 8 x 8 grid,
empty/missing files, trivial CSV and JSON. They exercise selected pure functions,
not the controller or fault harness. No mask is placed over the patient images.
All displayed contract checks are public; there is no private reference reveal.
No BCER pipeline, medical tool, model, registration or segmentation was run.
No actual clinical outputs or ground truth are retained for this example.

Rebuild using scripts/audit_bcer_workflow.py and scripts/build_bcer_workflow_assets.py
into fresh local destinations. The source audit retains hashes, exact contracts,
selected-function digests, native geometry and all five check outcomes.
""")
    (
        out / "DATA-LICENSE.txt"
    ).write_text("""PI-CAI MRI: Creative Commons Attribution-NonCommercial 4.0 International.
https://creativecommons.org/licenses/by-nc/4.0/
Twilt et al., PI-CAI: Prostate Imaging - Cancer AI, v2.0 (2022).
https://zenodo.org/records/6624726
https://zenodo.org/records/6624726/files/LICENSE?download=1
Attribution and transformations: NOTICE.md. License verified 2026-09-28.
""")
    license_row = next(r for r in audit["source_files"] if r["path"] == "LICENSE")
    (out / "BCER-LICENSE.txt").write_bytes(Path(license_row["local_path"]).read_bytes())
    manifest = {
        "id": "retained-bcer-workflow-v1",
        "frame": "LPS",
        "units": "mm",
        "license": "CC-BY-NC-4.0",
        "label_license": None,
        "reference_policy": "no-reference-assets",
        "sources": {
            str(args.audit): sha(args.audit),
            "scripts/build_bcer_workflow_assets.py": sha(Path(__file__)),
        },
        "checks": {
            "native_png_roundtrip": True,
            "native_views": 3,
            "no_native_resampling": True,
            "mha_nifti_voxels_equal": True,
            "geometry_tolerance_mm": 1e-5,
            "nonclinical_validator_examples": 5,
            "public_contract_only": True,
            "medical_tool_or_model_run": False,
        },
        "assets": [
            {
                "file": name,
                "sha256": sha(out / name),
                "bytes": (out / name).stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "illustration",
            }
            for name in [
                "inputs.json",
                "contract.json",
                "NOTICE.md",
                "DATA-LICENSE.txt",
                "BCER-LICENSE.txt",
            ]
        ],
    }
    write("manifest.json", manifest)
    print(json.dumps({"output": str(out), "checks": manifest["checks"]}))


if __name__ == "__main__":
    main()
