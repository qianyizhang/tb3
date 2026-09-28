"""Create native CT context teaching views from audited retained inputs."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AUDIT = "groups/longitudinal-reading/presentation/sources/ct-context-audit.json"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def build(out):
    audit = json.loads((ROOT / AUDIT).read_text())
    for name, digest in audit["source_pins"].items():
        assert sha(ROOT / name) == digest, name
    out.mkdir(parents=True, exist_ok=False)
    images = []
    for geo in audit["geometry"]:
        visit = geo["visit"]
        image = nib.load(ROOT / audit["task"] / f"environment/data/{visit}.nii.gz")
        for region, k in [
            ("liver", 430 if visit == "baseline" else 542),
            ("groin", 230 if visit == "baseline" else 390),
        ]:
            bounds = [80, 430, 110, 410] if region == "liver" else [90, 420, 130, 355]
            i0, i1, j0, j1 = bounds
            raw = np.asarray(image.dataobj[:, :, k])[i0:i1, j0:j1].T
            gray = np.uint8(np.clip((raw.astype(float) + 40) / 180, 0, 1) * 255)
            buffer = io.BytesIO()
            Image.fromarray(gray).save(buffer, format="PNG", optimize=True)
            np.testing.assert_array_equal(
                np.asarray(Image.open(io.BytesIO(buffer.getvalue()))), gray
            )
            images.append(
                {
                    "id": f"{visit}-{region}",
                    "visit": visit,
                    "region": region,
                    "k": k,
                    "bounds": bounds,
                    "width": i1 - i0,
                    "height": j1 - j0,
                    "window_hu": [-40, 140],
                    "png": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode(),
                    "point": ([185, 315] if visit == "baseline" else [155, 250])
                    if region == "liver"
                    else None,
                    "roi": ([160, 215, 180, 225] if visit == "baseline" else [160, 210, 155, 205])
                    if region == "groin"
                    else None,
                }
            )

    def write(name, value):
        (out / name).write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")

    write(
        "inputs.json",
        {
            "geometry": audit["geometry"],
            "images": images,
            "checks": audit["checks"],
            "derivation": "Selected axial planes cited by the retained agent; native pixels cropped without resampling; i right, j down, patient right at image left. Window [-40,140] HU matches retained coordinate images. Author crops and overlays were not supplied inputs. No registration or GT contour.",
        },
    )
    write(
        "output.json",
        {
            "fields": audit["fields"],
            "counts": audit["status_counts"],
            "agent_seconds": audit["checks"]["agent_seconds"],
        },
    )
    write(
        "reference.json",
        {
            "metadata": audit["source_provenance"]["field_provenance"],
            "diagnostics": audit["diagnostics"],
            "rewards": [{"id": x["attempt_id"], "reward": x["reward"]} for x in audit["controls"]],
            "scope": "Private reader comparison. Patient CSV, cohort descriptions and unavailable individual history must remain distinct. Author schema diagnostics are not model runs.",
        },
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Longitudinal-CT v3, Küstner, Peisen, Gatidis et al., University Hospital Tübingen / FDAT. CC BY-NC 4.0. https://creativecommons.org/licenses/by-nc/4.0/\nhttps://fdat.uni-tuebingen.de/records/qe950-g4h94\nSource-derived teaching crops; noncommercial local research. Retained agent output and author diagnostic records are separately labeled.\n"
    )
    (out / "NOTICE.md").write_text("""# CT-only context inference

Two native CTs were the only image inputs; no demographics, diagnosis, points, masks or earlier outputs were supplied. This pack derives four axial crops at the exact slices cited by the retained agent. Grayscale is the retained [-40,140] HU window, i increases right, j down, L/P/S array axes. Coordinates are zero-based voxels; affines map to RAS millimeters, not dates. Pixel decoding is checked exactly. No resampling or registration is performed.

Amber crosses show the agent's approximate liver evidence coordinates. Amber dashed boxes show the cited groin region. These are submitted evidence citations, not supplied hints, GT, segmentations or a diagnosis. Images precede the output and metadata reveals. Source views were visually inspected beside the original retained coordinate PNGs.

Output contains the exact nine structured field records. Seven unknowns and two inferences are not an accuracy fraction. Reader reference separates patient CSV age/sex/interval, cohort diagnosis/treatment/purpose and absent individual history. Source findings retain cohort provenance and limitations. No new external source review is claimed.

Reference diagnostics use the unchanged frozen validate function on saved output and temporary author variants. All-unknown and unsupported invented assertions both pass structure; inconsistent unknown/value and missing report fail. This demonstrates the declared mechanical boundary. Original model/oracle/no-op rewards remain unchanged. No model or clinical trial was run; schema validity does not measure accuracy or confidence calibration.

Rebuild with scripts/build_ct_context_assets.py into a fresh destination after scripts/audit_ct_context.py. Raw runs and generated media stay local. Source and reconstruction hashes are in manifest.json; retained clinical source terms are in DATA-LICENSE.txt.
""")
    names = ["inputs.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"]
    write(
        "manifest.json",
        {
            "id": "retained-ct-context-v1",
            "frame": "RAS",
            "units": "mm",
            "license": "CC-BY-NC-4.0",
            "label_license": "CC-BY-NC-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                AUDIT: sha(ROOT / AUDIT),
                "scripts/build_ct_context_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "native_png_roundtrip": True,
                "views": 4,
                "no_resampling": True,
                **audit["checks"],
            },
            "assets": [
                {
                    "file": n,
                    "sha256": sha(out / n),
                    "bytes": (out / n).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal" if n == "reference.json" else "illustration",
                }
                for n in names
            ],
        },
    )
    print(json.dumps({"views": 4, "assets": names}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output)
