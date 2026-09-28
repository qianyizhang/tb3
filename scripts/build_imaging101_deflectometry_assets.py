"""Build source-figure and fixed-control views for refractive lens metrology.

Rendered notebook panels retain their source pixels and have no raw-intensity
interpretation. Lens sections are analytical geometry, not ray-traced results.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, selected, sha
from PIL import Image


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def encoded(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": [image.height, image.width],
    }


def numeric_image(a, lo, hi):
    a = np.asarray(a)
    assert a.ndim == 2 and np.isfinite(a).all() and a.min() >= lo - 1e-10 and a.max() <= hi + 1e-10
    pixels = np.rint(np.clip((a - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
    return {**encoded(Image.fromarray(pixels)), "range": [lo, hi], "role": "synthetic fixture"}


def profile(c0, c1, d):
    radial = np.linspace(-12.7, 12.7, 129)

    def sag(c):
        return c * radial**2 / (1 + np.sqrt(1 - c * c * radial**2))

    return {
        "r": radial.tolist(),
        "front": sag(c0).tolist(),
        "back": (d + sag(c1)).tolist(),
        "curvatures": [c0, c1],
        "thickness": d,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-deflectometry-audit.json")
    record = json.loads(record_path.read_text())
    source = args.sources
    task = source / "tasks/differentiable_deflectometry"
    for row in record["verified_assets"]:
        assert sha(source / row["path"]) == row["sha256"]
    figures = {}
    for row in record["source_figure_inspection"]["figures"]:
        p = source / Path(row["path"]).name
        assert sha(p) == row["sha256"]
        figures[row["cell"]] = Image.open(p).convert("RGB")
        assert figures[row["cell"]].size == (555, 788)
    args.output.mkdir(parents=True, exist_ok=False)
    # Interior image bounds in the upper, nonduplicated two-camera figure.
    # The figure was already rendered/resampled upstream; no numerical recovery.
    boxes = {
        "measurement": [(45, 86, 158, 200), (45, 261, 158, 374)],
        "modeled": [(215, 86, 329, 200), (215, 261, 329, 374)],
    }

    def panel(cell, kind, camera):
        box = boxes[kind][camera]
        return {
            **encoded(figures[cell].crop(box)),
            "crop_box_ltrb": list(box),
            "notebook_cell": cell,
            "camera": camera + 1,
            "source_figure_shape": [788, 555],
            "native_view_extent": [768, 768],
            "role": "rendered source figure; normalized and masked; not raw pixels",
        }

    measurements = [panel(10, "measurement", c) for c in range(2)]
    modeled = {
        name: [panel(cell, "modeled", c) for c in range(2)]
        for name, cell in [("initial", 9), ("saved", 10)]
    }
    fixture = arrays(task / "evaluation/fixtures/input_fringe_solve.npz")["imgs"]
    ns = {"np": np}
    selected(task / "src/preprocessing.py", ["_solve"], ns, "Fringe")
    probes = []
    for axis, camera, row, column in [(0, 0, 8, 8), (0, 1, 12, 16), (1, 0, 16, 24), (1, 1, 24, 12)]:
        fs = fixture[4 * axis : 4 * (axis + 1), camera]
        mean, squared_modulation, phase = ns["_solve"](fs)
        values = fs[:, row, column]
        delta_x = float(values[0] - values[2])
        delta_y = float(values[3] - values[1])
        assert np.isclose(np.arctan2(delta_y, delta_x), phase[row, column])
        probes.append(
            {
                "axis": ["x", "y"][axis],
                "camera": camera + 1,
                "row": row,
                "column": column,
                "frames": [numeric_image(f, 50, 150) for f in fs],
                "values": values.tolist(),
                "mean": float(mean[row, column]),
                "squared_modulation": float(squared_modulation[row, column]),
                "phase": float(phase[row, column]),
                "delta": [delta_x, delta_y],
                "phase_image": numeric_image(phase, -np.pi, np.pi),
            }
        )
    params = json.loads((task / "evaluation/reference_outputs/optimized_params.json").read_text())
    truth = arrays(task / "data/ground_truth.npz")
    gt = [float(truth[k][0]) for k in record["parameter_order"]]
    saved_profile = profile(params["surface_0_c"], params["surface_1_c"], params["surface_1_d"])
    initial_profile = profile(0.001, 0.001, 3)
    truth_profile = profile(1 / gt[0], 1 / gt[1], gt[2])
    assert np.isclose(saved_profile["back"][64] - saved_profile["front"][64], params["surface_1_d"])
    write(
        args.output / "inputs.json",
        {
            "measurements": measurements,
            "metadata": record["metadata"],
            "raw_available": False,
            "source_view_note": "Notebook cell10, upper two-camera figure. Normalized, masked and resampled by the source plot; extracted pixels are display samples only.",
            "fixture_probes": probes,
        },
    )
    write(
        args.output / "contract.json",
        {
            "modeled": modeled,
            "saved_parameters": params,
            "initial_profile": initial_profile,
            "saved_profile": saved_profile,
            "saved_metrics": record["saved_metrics"],
            "loss": record["loss"],
            "custom_score": record["custom_scoring"],
            "pose_control": record["custom_pose_control"],
            "generic_scoring": record["generic_scoring"],
            "staging": {k: v["available_files_copied"] for k, v in record["staging"].items()},
            "parameter_order": record["parameter_order"],
            "source_raw_shape": [1, 3, 8, 2, 2048, 2048],
            "crop_offset": [640, 640],
            "surface_aperture_diameter_mm": 25.4,
            "geometry_scope": "Spherical sag in lens-local coordinates, k=0 and no polynomial terms. Profiles use saved or initial parameters; no optical rays or inferred optimizer trajectory.",
        },
    )
    write(
        args.output / "reference.json",
        {
            "manufacturer_parameters_mm": gt,
            "profile": truth_profile,
            "relative_errors": [
                (abs(r - g) / abs(g)) for r, g in zip(record["saved_recovered_mm"], gt, strict=True)
            ],
            "solver_visible_all_levels": True,
            "pose_truth_available": False,
        },
    )
    (args.output / "BENCHMARK-LICENSE.txt").write_bytes((source / "LICENSE").read_bytes())
    (args.output / "DATA-LICENSE.txt").write_text("""Source terms and attribution

Benchmark source and retained notebook: AI4ImagingLab/imaging-101-release,
MIT notice in BENCHMARK-LICENSE.txt. Cited original work: Congli Wang,
Ni Chen and Wolfgang Heidrich, Optics Express 2021, and vccimaging/DiffDeflectometry.
No license file exists in the inspected pinned upstream tree. The benchmark's
MIT notice is not assigned to the upstream repository. This pack derives views
from the benchmark notebook and fixtures; no upstream implementation is copied.
""")
    (args.output / "NOTICE.md").write_text("""# Refractive deflectometry source views

Benchmark revision: `dc2f668939b21e8312e22529615def610f8611df`.
Dataset revision: `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
[Source audit](../../external-tasks/sources/imaging101-deflectometry-audit.json)
retains source/asset hashes, original attribution, contracts and fixed controls.
The task cites Wang, Chen and Heidrich, Optics Express 2021; the upstream tree
at `df23bef16ed92d597f9d9397f313de54e9d4015a` has no license file. Read
DATA-LICENSE.txt and BENCHMARK-LICENSE.txt together.

Camera panels are exact crops from the pinned notebook's embedded PNG figures,
not extracted raw camera arrays. Inputs use cell10's upper two measurement panels;
modeled outputs use cells9/10's upper modeled panels. Crop boxes are in the JSON.
Both original figures are 555x788 pixels; the source already normalized, masked,
rendered and resampled the 768x768 camera views. Extracted panels are 113/114
pixels wide and 113/114 pixels high. Display them as rendered views, never as
raw intensity or measurement samples. The repeated lower figure is excluded:
the source saves a complete two-camera figure twice. There are two cameras.
Original notebook bytes and complete extracted figures remain local unchanged.

The 32x32 four-step fringe demonstration is a separate synthetic source fixture.
Four selected pixels retain their exact intensities, axis, camera, mean,
squared modulation and atan2 phase. Image displays use fixed 50..150 intensity
and -pi..pi phase scales with 8-bit grayscale quantization. No native-camera
phase, valid map, screen intersection or optical fit is recovered from these controls.

Lens sections show the analytical spherical sag used by the source with k=0
and no polynomial terms, at aperture radius12.7mm. Axes are declared millimeters
in the lens-local frame. Initial and saved sections are discrete states, never
invented optimizer iterates. Eight saved parameters and all21 recorded losses
retain their source values. Loss is pre-update full-grid masked component MSE;
43.0513um displacement is a separately retained valid-pixel source metric.

Manufacturer radii/thickness and their section are isolated in reference.json.
They mount only after an explicit reader reveal with dashed purple styling.
This is a presentation boundary: L1-L3 actually seed truth and the prescription.
The custom scorer ignores pose; generic scoring rejects a correct three-vector.
No pass thresholds are supplied. The raw archive remains unavailable; source
figures do not establish raw-data recovery, fresh optical fitting or agent skill.
""")
    names = [
        "inputs.json",
        "contract.json",
        "reference.json",
        "NOTICE.md",
        "DATA-LICENSE.txt",
        "BENCHMARK-LICENSE.txt",
    ]
    write(
        args.output / "manifest.json",
        {
            "id": "retained-imaging101-deflectometry-v1",
            "frame": "source-record",
            "units": "mm",
            "license": "LicenseRef-Imaging101-deflectometry-sources",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(record_path): sha(record_path),
                "scripts/build_imaging101_deflectometry_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "source_camera_views": 2,
                "source_figure_pixels_preserved_within_crops": True,
                "native_intensities_recovered": False,
                "synthetic_fixture_shape": [32, 32],
                "phase_controls": len(probes),
                "lens_profile_samples": 129,
                "source_loss_samples": len(record["loss"]["values"]),
                "model_or_optimizer_runs": 0,
            },
            "assets": [
                {
                    "file": n,
                    "sha256": sha(args.output / n),
                    "bytes": (args.output / n).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal" if n == "reference.json" else "illustration",
                }
                for n in names
            ],
        },
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sizes": {n: (args.output / n).stat().st_size for n in names},
            }
        )
    )


if __name__ == "__main__":
    main()
