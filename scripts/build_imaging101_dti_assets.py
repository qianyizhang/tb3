"""Derive DTI teaching views from pinned native arrays and fixed-control receipts.

No fitting, data generation or agent execution. Quantized images retain the
128x128 source grid; numerical probes retain native or audited float values.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from audit_imaging101_poisson_lowdose import arrays, sha
from PIL import Image


def write(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def plane(a, maximum, unit, mask=None):
    a = np.asarray(a, dtype=np.float64)
    assert a.shape == (128, 128) and np.isfinite(a).all()
    assert a.min() >= 0 and a.max() <= maximum
    pixels = np.rint(a / maximum * 255).astype(np.uint8)
    if mask is None:
        image = Image.fromarray(pixels)
    else:
        image = Image.fromarray(
            np.stack([pixels, pixels, pixels, mask.astype(np.uint8) * 255], axis=-1)
        )
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return {
        "data": "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode(),
        "shape": [128, 128],
        "range": [0, maximum],
        "unit": unit,
        "source_min": float(a.min()),
        "source_max": float(a.max()),
        "quantization_max_abs_error": float(maximum / 510),
        "masked": mask is not None,
    }


def tensor_probe(elems, fa, md):
    e = np.asarray(elems, dtype=np.float64)
    D = np.array([[e[0], e[1], e[2]], [e[1], e[3], e[4]], [e[2], e[4], e[5]]])
    ev, vectors = np.linalg.eigh(D)
    order = np.argsort(ev)[::-1]
    ev, vectors = ev[order], vectors[:, order]
    assert (ev > 0).all()
    # Orthographic silhouettes of V diag(lambda) u for ||u||=1. Glyph axis
    # lengths are eigenvalues, not displacement or an anatomical surface.
    squared = D @ D
    theta = np.linspace(0, 2 * np.pi, 65)
    circle = np.vstack([np.cos(theta), np.sin(theta)])
    projections = []
    for axes in [(0, 1), (0, 2), (1, 2)]:
        covariance = squared[np.ix_(axes, axes)]
        values, basis = np.linalg.eigh(covariance)
        xy = (basis @ np.diag(np.sqrt(values)) @ circle).T
        assert np.allclose(xy[0], xy[-1])
        projections.append({"axes": list(axes), "points": (1000 * xy).tolist()})
    mean = ev.mean()
    calculated_fa = np.sqrt(1.5 * ((ev - mean) ** 2).sum() / (ev**2).sum())
    assert abs(calculated_fa - fa) < 2e-7 and abs(mean - md) < 1e-9
    return {
        "elements": e.tolist(),
        "matrix": D.tolist(),
        "eigenvalues": ev.tolist(),
        "eigenvectors": vectors.tolist(),
        "fa": float(fa),
        "md": float(md),
        "projections": projections,
        "principal_axis_unique": bool(ev[0] - ev[1] > 1e-10),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record_path = Path("presentation/external-tasks/sources/imaging101-dti-audit.json")
    record = json.loads(record_path.read_text())
    source = args.sources
    task = source / "tasks/diffusion_mri_dti"
    for row in record["verified_assets"] + record["verified_sources"]:
        assert sha(source / row["path"]) == row["sha256"]
    assert sha(Path("scripts/audit_imaging101_dti.py")) == record["script_sha256"]
    args.output.mkdir(parents=True, exist_ok=False)
    raw = arrays(task / "data/raw_data.npz")
    truth = arrays(task / "data/ground_truth.npz")
    saved = {m: arrays(task / f"evaluation/reference_outputs/dti_{m}.npz") for m in ["ols", "wls"]}
    mask = truth["tissue_mask"][0]
    indices = [0, 18, 16, 1]
    assert indices[1:] == [int(1 + np.argmax(np.abs(raw["bvecs"][1:, axis]))) for axis in range(3)]
    probes = [
        {"row": p["row"], "column": p["column"], "signal": p["signal"]}
        for p in record["selected_probes"]
    ]
    for p in probes:
        assert np.array_equal(raw["dwi_signal"][0, p["row"], p["column"]], p["signal"])
    inputs = {
        "signals": [
            {
                "volume": i,
                "bvalue": float(raw["bvals"][i]),
                "gradient": raw["bvecs"][i].tolist(),
                "image": plane(raw["dwi_signal"][0, ..., i], 1.15, "signal a.u."),
            }
            for i in indices
        ],
        "mask": plane(mask, 1, "supplied binary mask"),
        "mask_pixels": int(mask.sum()),
        "metadata": record["metadata"],
        "gradients": record["gradient_table"],
        "probes": probes,
        "selection": record["probe_selection"],
    }
    output_maps, reference_maps, errors = {}, {}, {}
    for key, scale, maximum, unit in [("fa", 1, 1, "FA"), ("md", 1000, 3.5, "10^-3 mm^2/s")]:
        reference_maps[key] = plane(truth[f"{key}_map"][0] * scale, maximum, unit, mask)
        values = {
            m: np.abs(z[f"{key}_map"][0].astype(np.float64) - truth[f"{key}_map"][0]) * scale
            for m, z in saved.items()
        }
        upper = float(np.ceil(max(float(a.max()) for a in values.values()) * 20) / 20)
        errors[key] = {m: plane(a, upper, unit, mask) for m, a in values.items()}
        output_maps[key] = {
            m: plane(z[f"{key}_map"][0] * scale, maximum, unit, mask) for m, z in saved.items()
        }
    tensor_probes = {}
    for name, data in {"truth": truth, **saved}.items():
        tensor_probes[name] = [
            tensor_probe(
                data["tensor_elements"][0, p["row"], p["column"]],
                data["fa_map"][0, p["row"], p["column"]],
                data["md_map"][0, p["row"], p["column"]],
            )
            for p in probes
        ]
    fits = record["selected_probe_fits"]
    B = np.array(record["gradient_table"]["design_matrix"])
    weights = np.exp(
        2
        * np.column_stack([np.log(fits["ols"]["fitted_s0"]), fits["ols"]["tensor_elements"]])
        @ B.T
    )
    weights = np.clip(weights, 1e-10, 1e10)
    contract = {
        "maps": output_maps,
        "tensor_probes": {m: tensor_probes[m] for m in saved},
        "fixed_pixel_fits": fits,
        "wls_weights": weights.tolist(),
        "native_metrics": record["native_masked_metrics"],
        "custom_scoring": record["custom_scoring"],
        "generic_scoring": record["generic_scoring"],
        "fallback": record["no_filesystem_workspace_dispatch"],
        "staging": {k: v["available_files_copied"] for k, v in record["staging"].items()},
        "notebook_probe_check": record["notebook_probe_check"],
        "orientation_controls": record["orientation_controls"],
        "thresholds_available": False,
        "source_axes": ["x", "y", "z"],
        "glyph_units": "10^-3 mm^2/s",
        "glyph_axis_lengths": "eigenvalues; orthographic projections",
    }
    reference = {
        "maps": reference_maps,
        "errors": errors,
        "tensor_probes": tensor_probes["truth"],
        "solver_visible_all_levels": True,
        "mask_pixels": int(mask.sum()),
    }
    for name, data in [("inputs", inputs), ("contract", contract), ("reference", reference)]:
        write(args.output / f"{name}.json", data)
    (args.output / "BENCHMARK-LICENSE.txt").write_bytes((source / "LICENSE").read_bytes())
    (args.output / "DATA-LICENSE.txt").write_text("""Source attribution

Imaging-101 Authors, AI4ImagingLab/imaging-101-release. The benchmark supplies
an MIT license, retained in BENCHMARK-LICENSE.txt. Native synthetic arrays are
from the pinned starpacker52/imaging-101 release. The source generator describes
a resized scikit-image Shepp-Logan phantom assigned five tensor types. No patient
images, independent clinical labels, original paper figures or DIPY code are copied.
""")
    (args.output / "NOTICE.md").write_text("""# Diffusion tensor MRI source views

Benchmark revision: `dc2f668939b21e8312e22529615def610f8611df`.
Dataset revision: `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [source audit](../../external-tasks/sources/imaging101-dti-audit.json)
retains all source/asset identities, numerical controls and evaluator limits.

All images retain the 128x128 native grid with 8-bit grayscale quantization.
No image is cropped or spatially resampled. Signals 0,18,16,1 are b0 and the
available gradients closest to the absolute x/y/z axes. All use 0..1.15 a.u.;
FA uses 0..1, MD uses 0..3.5 in 10^-3 mm^2/s. Error scales cover both methods'
full retained range, rounded upward to 0.05; no clipping at notebook limits.
Excluded tissue-mask pixels are transparent in scalar maps; they are not
missing measurements. PNG ranges and quantization errors are recorded per image.

Image columns increase rightward and rows downward. Tensor x/y/z are source
coordinate axes; no patient/anatomical orientation affine is supplied. Five
fixed pixels were selected post-hoc, one per distinct truth tensor; they are not
a random evaluation sample or a new localization result. Exact native signal
values and audited fixed-pixel fits remain numerical records beside the images.
The source truth mask is supplied at all levels and may be shown as a helper.

Tensor glyphs are orthographic projections of V diag(lambda) u for unit u.
Axis lengths are eigenvalues in 10^-3 mm^2/s, not anatomical displacement or
fiber tracts. Saved OLS/WLS tensors determine the visible glyphs. Truth glyphs,
FA/MD maps and error maps live in reference.json and require a reader reveal.
Eigenvector sign is arbitrary, and isotropic truth has no unique principal axis.

The source rotation maps z to its declared direction while the largest
eigenvalue belongs to its first column. Stored anisotropic tensors therefore
disagree with those declared directions; render their actual values. Notebook
gray-matter and CSF probe labels also disagree with their stored tensor/mask.
No source arrays, labels, original scores or old receipts are rewritten.

Actual L1-L3 seeding exposes all truth and the tissue mask. The reader gate is
not solver privacy. The custom score checks only masked FA, preferring OLS when
both native files exist. Generic local scoring selects FA for scalar maps,
including MD, and uses the full grid; tensor-shaped outputs select tensor truth.
The no-workspace fallback requires absent NPY truth. Published thresholds are
absent; notebook values remain historical. No model, generator or full-image
fit runs in this pack or in its derivation.
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
            "id": "retained-imaging101-dti-v1",
            "frame": "source-record",
            "units": "mm^2/s",
            "license": "MIT",
            "label_license": "MIT",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(record_path): sha(record_path),
                "scripts/build_imaging101_dti_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "source_grid": [128, 128],
                "source_signal_volumes": 31,
                "displayed_signal_volumes": indices,
                "design_matrix_rank": 7,
                "selected_native_pixels": len(probes),
                "native_images_cropped": False,
                "negative_saved_probe_eigenvalues": 0,
                "tensor_projection_samples": 65,
                "native_mask_pixels": int(mask.sum()),
                "runtime_fits": 0,
                "model_runs": 0,
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
