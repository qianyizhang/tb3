"""Build native CT planes, explicit partial references and source-audited teaching data."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image

COLORS = ["#49cfac", "#69aaff", "#ffd26b", "#ee8dbd", "#c2a0ff"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png(array):
    stream = io.BytesIO()
    Image.fromarray(array).save(stream, format="PNG")
    raw = stream.getvalue()
    assert np.array_equal(np.asarray(Image.open(io.BytesIO(raw))), array)
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text())
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    for row in audit["native_assets"]:
        assert sha(Path(row["local_path"])) == row["sha256"]
    ct = np.asarray(nib.load(audit["native_assets"][0]["local_path"]).dataobj)

    def write(name, data):
        (out / name).write_text(json.dumps(data, separators=(",", ":")) + "\n")

    views = []
    for y in [144, 164, 184]:
        # RAS indices: x grows rightwards; z grows upwards in displayed native coronal plane.
        gray = np.rint(np.clip((ct[:, y, :].T[::-1].astype(float) + 160) / 400, 0, 1) * 255).astype(
            np.uint8
        )
        views.append({"y": y, "width": 333, "height": 336, "png": png(gray)})
    write(
        "inputs.json",
        {
            "case": "TSG_00000001",
            "source_case": "s1366",
            "views": views,
            "native": audit["native_assets"][0],
            "window_hu": [-160, 240],
            "selection": "Coronal y164 selected post hoc using kidney references; neighboring planes y144 and y184 are reader navigation, not supplied solver locations.",
        },
    )
    reference = []
    for row, color in zip(audit["remap"], COLORS, strict=True):
        native = next(n for n in audit["native_assets"] if n["name"] == row["name"])
        a = np.asarray(nib.load(native["local_path"]).dataobj)[:, 164, :].T[::-1] > 0
        rgba = np.zeros((*a.shape, 4), dtype=np.uint8)
        rgba[a] = [int(color[i : i + 2], 16) for i in [1, 3, 5]] + [170]
        reference.append(
            {
                **row,
                "color": color,
                "png": png(rgba),
                "plane_voxels": int(a.sum()),
                "volume_voxels": native["foreground_voxels"],
            }
        )
    write(
        "reference.json",
        {
            "plane_y": 164,
            "structures": reference,
            "retained": 5,
            "release_reported_present": 78,
            "configured": 117,
            "role": "Reader-only released references, not model predictions.",
        },
    )
    examples = []
    for e in audit["validator_examples"]:
        completed = sum(
            p["mean_tissue_dice"] is not None for p in e["dice"]["per_patient"].values()
        )
        examples.append(
            {
                "id": e["id"],
                "format_valid": e["format"]["output_format_valid"],
                "completed": completed,
                "total": 2,
                "raw_dice": e["dice"]["macro_mean_dice"],
                "task_score": e["report"]["aggregate"]["task_score"],
                "rating": e["report"]["aggregate"]["rating"],
                "workflow_score": e["report"]["aggregate"]["agentic_score"],
            }
        )
    write(
        "contract.json",
        {
            "remap": audit["remap"],
            "examples": examples,
            "scope": audit["scope"],
            "revision": audit["revision"],
            "geometry": audit["native_assets"][0]["affine"],
            "model_version": "2.4.0",
            "model_commit": audit["model_map_source"]["ref"],
        },
    )
    (out / "NOTICE.md").write_text("""# AutoMedBench Lite multi-organ teaching assets

Native CT and five released reference masks: TotalSegmentator source s1366,
staged as TSG_00000001 by MitakaKuma/AutoMedBench-Lite-release at revision
8928073d5c3f3b842a4a4278d9b44f6e8ceaa9c5. CC BY 4.0 per pinned DATA_CARD.md.
Original dataset: Wasserthal et al., TotalSegmentator, via TotalSegmentator CT-Lite.
https://huggingface.co/datasets/YongchengYAO/TotalSegmentator-CT-Lite
https://zenodo.org/records/10047263
The audit verifies all six native files against retained published LFS hashes.

CT display: native coronal planes y144, y164 and y184, window -160 to 240 HU,
rounded 8-bit gray; transpose and reverse superior axis, no spatial resampling.
333 x 336 native pixels, 1.5 mm isotropic RAS. Right increases rightward and
superior upward. y164 was selected post hoc using kidney references. Neighboring
planes are reader navigation, not solver-supplied target locations.
Reference overlays use exact native y164 binary masks, constant per-structure
colors and alpha170/255. All five have nonempty intersections on this plane.
Overlays are hidden until the reader-reference chapter. The local collection has
five masks; the release CSV reports 78 present classes of 117. This is not a
complete reference set, model prediction or full-case segmentation score.

The label mapping is factual data extracted from TotalSegmentator 2.4.0,
commit 2e0c20058df8acb17acd54a7adf25bf7a0a33c90, and the pinned benchmark config.
Requirements allow later versions; verify the actual checkpoint label table.
No upstream executable code or model weights are included in this asset pack.
Source files were acquired through hf-mirror.com with matching revision headers
and Git blob ETags; provenance does not claim authenticated primary transport.

Seven author nonclinical fixtures use two synthetic 8x8x8 grids with eight voxels
each of labels42 and43 and 115 empty classes. Selected pinned format/scoring/
aggregation functions were replayed, not the controller, model, judge or sandbox.
All-117 empty-pair averaging contradicts the config's nonempty-reference wording.
Scorer missing-output omission is followed by completeness scaling in aggregation;
the medal remains assigned before that scaling. No clinical implication is made.

Rebuild: scripts/audit_automed_multiorgan.py then
scripts/build_automed_multiorgan_assets.py, each into a fresh local directory.
""")
    (
        out / "DATA-LICENSE.txt"
    ).write_text("""CT and reference masks: Creative Commons Attribution 4.0 International.
https://creativecommons.org/licenses/by/4.0/
Wasserthal et al., TotalSegmentator, via TotalSegmentator CT-Lite and AutoMedBench Lite.
Pinned source, derivative transformations and attribution: NOTICE.md and audit receipt.
Author nonclinical fixtures and explanatory data are teaching artifacts, not patient results.
""")
    files = ["inputs.json", "reference.json", "contract.json", "NOTICE.md", "DATA-LICENSE.txt"]
    write(
        "manifest.json",
        {
            "id": "retained-automed-multiorgan-v1",
            "frame": "RAS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(args.audit): sha(args.audit),
                "scripts/build_automed_multiorgan_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_png_roundtrip": True,
                "no_native_resampling": True,
                "native_views": 3,
                "published_lfs_matches": 6,
                "shared_native_geometry": True,
                "retained_masks": 5,
                "nonclinical_examples": 7,
                "model_run": False,
                "full_case_score": False,
            },
            "assets": [
                {
                    "file": name,
                    "sha256": sha(out / name),
                    "bytes": (out / name).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if name == "reference.json"
                    else "illustration",
                }
                for name in files
            ],
        },
    )
    print(json.dumps({"output": str(out), "native_views": 3, "partial_masks": 5}))


if __name__ == "__main__":
    main()
