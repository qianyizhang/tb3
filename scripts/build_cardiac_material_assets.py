#!/usr/bin/env python3
"""Bounded source-derived BR-029 display pack; no solver, fitting or model run."""

import argparse
import base64
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT: Path
RUN = ROOT / "runs/br029-dynamic-heart"
PINS = {
    "runs/br029-dynamic-heart/public-video/initial_mesh.npz": "e6746eebb0a1f41354e624a551c6118eabbe1f6f5692193071c58e031faa46b6",
    "runs/br029-dynamic-heart/analysis-v2/healthy_reference.npz": "c2476764cf1819d32fd7392b768ac119c01a75f406780a6ad707bafdd1c97737",
    "runs/br029-dynamic-heart/analysis-v2/video_affine.npz": "b922eb20315b0a2ff8f394f42f72985fd93f742f87862c12199374a6f21466c6",
    "runs/br029-dynamic-heart/tissue-analysis-v3/tissue_fit.npz": "285d814709ccb37d4d0cd0678211bf6af525dea10175294da63d3f3b873b8e98",
    "runs/br029-dynamic-heart/deliverables/tissue-model.npz": "2af4dce6e931d5a4026be2ca4445421bba3877f3baf23268906e5e59afb192a0",
}
CELL = 10000
MISSING = 7722


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def clean(values, digits=4):
    a = np.round(np.asarray(values, float), digits)

    def value(x):
        return None if not np.isfinite(x) else float(x)

    return np.vectorize(value, otypes=[object])(a).tolist()


def write(name, value):
    data = (json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n").encode()
    (OUT / name).write_bytes(data)
    return {
        "file": name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "provenance": "source-derived-teaching",
        "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
    }


def edge_matrix(p):
    return np.stack([p[1] - p[0], p[2] - p[0], p[3] - p[0]], axis=1)


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    OUT = args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=False)
    sources = {}
    for rel, expected in PINS.items():
        actual = sha(ROOT / rel)
        if actual != expected:
            raise ValueError(f"SHA mismatch: {rel}")
        sources[rel] = actual
    public = RUN / "public-video"
    geom_path = public / "geometry.json"
    sources[str(geom_path.relative_to(ROOT))] = sha(geom_path)
    geom = json.loads(geom_path.read_text())
    with (
        np.load(public / "initial_mesh.npz", allow_pickle=False) as mesh,
        np.load(RUN / "analysis-v2/video_affine.npz", allow_pickle=False) as video,
        np.load(RUN / "tissue-analysis-v3/tissue_fit.npz", allow_pickle=False) as tissue,
        np.load(RUN / "analysis-v2/healthy_reference.npz", allow_pickle=False) as ref,
        np.load(RUN / "deliverables/tissue-model.npz", allow_pickle=False) as export,
    ):
        p0, tetra = mesh["points"], mesh["tetra"]
        assert p0.shape == (11370, 3) and tetra.shape == (47186, 4)
        assert all(np.array_equal(tetra, a["tetra"]) for a in (video, tissue, ref, export))
        assert np.max(np.abs(p0 - ref["points"][0])) < 1e-8
        assert np.array_equal(export["points_mm"], tissue["points"].astype("float32"))
        assert int(mesh["labels"][CELL]) == 7 and int(mesh["labels"][MISSING]) > 0
        assert np.linalg.norm(mesh["directions"][:, CELL], axis=1).min() > 0.5
        assert np.linalg.norm(mesh["directions"][:, MISSING], axis=1).min() < 0.5
        boundary = np.unique(export["boundary_triangles"].ravel())
        ids = np.unique(
            np.r_[
                boundary[np.linspace(0, len(boundary) - 1, 320, dtype=int)],
                tetra[CELL],
                tetra[MISSING],
            ]
        ).astype(int)
        views, seed_sets = [], []
        for vi, plane in enumerate(geom["planes"]):
            o, u, v = (np.asarray(plane[k], float) for k in ("origin", "u", "v"))
            close = np.where(np.abs((p0 - o) @ np.cross(u, v)) <= 1.5)[0]
            seeds = close[np.linspace(0, len(close) - 1, min(24, len(close)), dtype=int)]
            seed_sets.append(seeds)
            images = []
            for frame in range(1, 31):
                path = public / f"view_{vi}" / f"frame_{frame:02d}.png"
                raw = path.read_bytes()
                sources[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
                images.append("data:image/png;base64," + base64.b64encode(raw).decode())
            views.append(
                {
                    "name": plane["name"],
                    "origin_mm": plane["origin"],
                    "u": plane["u"],
                    "v": plane["v"],
                    "seed_ids": seeds.tolist(),
                    "images": images,
                }
            )
        source = {
            "kind": "BR-029-public-input-display",
            "frame_count": 30,
            "image_size": 192,
            "spacing_mm_per_pixel": 0.75,
            "pixel_center": 95.5,
            "physical_frame_duration_seconds": None,
            "views": views,
            "sample_rule": "320 evenly indexed unique boundary vertices plus pinned cell vertices; fixed IDs",
            "sample_vertex_ids": ids.tolist(),
            "initial_points_mm": clean(p0[ids], 3),
            "tetra": {
                "id": CELL,
                "aha": 7,
                "vertex_ids": tetra[CELL].tolist(),
                "initial_vertices_mm": clean(p0[tetra[CELL]], 4),
                "directions": clean(mesh["directions"][:, CELL], 5),
            },
            "missing_axis_cell": {
                "id": MISSING,
                "aha": int(mesh["labels"][MISSING]),
                "vertex_ids": tetra[MISSING].tolist(),
                "initial_vertices_mm": clean(p0[tetra[MISSING]], 4),
                "direction_supported": False,
            },
            "projection": {
                "center_mm": [145, -48, 160],
                "scale_px_per_mm": 2.1,
                "formula": "x=150+2.1*((X-145)+0.38*(Y+48)); y=145-2.1*((Z-160)-0.20*(Y+48))",
            },
        }
        assets = [write("source.json", source)]
        inv = np.linalg.inv(edge_matrix(p0[tetra[CELL]]))
        analysis = json.loads((RUN / "analysis-v2/results.json").read_text())
        tr = json.loads((RUN / "tissue-analysis-v3/results.json").read_text())
        output = {
            "kind": "BR-029-saved-output-display",
            "frame_count": 30,
            "sample_vertex_ids": ids.tolist(),
            "selected_tetra_id": CELL,
            "missing_axis_cell_id": MISSING,
            "methods": {},
        }
        for name, arr, summary in (
            ("video_affine", video, analysis["models"]["video_affine"]),
            ("tissue_fit", tissue, tr["model"]),
        ):
            pts = arr["points"]
            selected = pts[:, tetra[CELL]]
            F = np.stack([edge_matrix(frame) @ inv for frame in selected])
            E = (F.transpose(0, 2, 1) @ F - np.eye(3)) / 2
            assert np.max(np.abs(np.linalg.det(F) - arr["jacobian"][:, CELL])) < 1e-5
            if name == "tissue_fit":
                assert np.max(np.abs(F - export["F"][:, CELL])) < 2e-5
                assert np.max(np.abs(E - export["E_green_lagrange"][:, CELL])) < 2e-5
            tracks = []
            for seeds, plane in zip(seed_sets, geom["planes"], strict=True):
                origin = np.asarray(plane["origin"])
                xy = np.stack(
                    [
                        ((pts[:, seeds] - origin) @ np.asarray(plane[k])) / 0.75 + 95.5
                        for k in ("u", "v")
                    ],
                    axis=-1,
                )
                tracks.append(clean(xy, 2))
            output["methods"][name] = {
                "sample_points_mm": clean(pts[:, ids], 3),
                "tracked_seed_projected_pixels": tracks,
                "tetra_vertices_mm": clean(selected, 4),
                "F": clean(F, 5),
                "E_green_lagrange": clean(E, 5),
                "J": clean(arr["jacobian"][:, CELL], 5),
                "engineering_strain": clean(arr["engineering"][:, CELL], 5),
                "missing_axis": {
                    "J": clean(arr["jacobian"][:, MISSING], 5),
                    "engineering_strain": [None, None, None],
                },
                "global_engineering_percent": summary["global_engineering_percent"],
                "tissue_volume_ml": summary["tissue_volume_ml"],
            }
        assets.append(write("output.json", output))
        metrics = {}
        for name, comparison in (
            ("static", analysis["models"]["static"]["comparison"]),
            ("video_affine", analysis["models"]["video_affine"]["comparison"]),
            ("tissue_fit", tr["model"]["comparison"]),
        ):
            metrics[name] = {
                "rmse_mm": comparison["material_point_rmse_mm"],
                "directional_mae_pp": comparison["directional_engineering_mae_pp"],
                "tissue_volume_error_percent": comparison[
                    "tissue_volume_curve_relative_error_percent"
                ],
            }
        reference = {
            "kind": "BR-029-reader-only-simulator-reference",
            "sample_vertex_ids": ids.tolist(),
            "sample_points_mm": clean(ref["points"][:, ids], 3),
            "tetra_vertices_mm": clean(ref["points"][:, tetra[CELL]], 4),
            "engineering_strain": clean(ref["engineering"][:, CELL], 5),
            "global_engineering_percent": analysis["models"]["healthy_reference"][
                "global_engineering_percent"
            ],
            "tissue_volume_ml": analysis["models"]["healthy_reference"]["tissue_volume_ml"],
            "directional_coverage": {
                "positive_aha_cells": 31244,
                "usable_axes": 31241,
                "missing_cell_ids": [7722, 9345, 45413],
                "aha0_excluded": 15942,
            },
            "metrics": metrics,
        }
        assets.append(write("reference.json", reference))
    notice = (
        "# BR-029 local material teaching pack\n\n"
        "Source: Multimodality STRAUS patient01_healthy. Local noncommercial interpretation only; "
        "public access does not establish onward redistribution permission. "
        "The 120 four-plane PNGs and initial mesh are solver inputs. Later source meshes and "
        "simulator reference scores are reader-only. Video-affine and tissue-fit points are "
        "retained author outputs, not new trials. Display samples retain fixed source IDs. "
        "Three positive-AHA cells have unavailable direction axes, represented as null, not zero. "
        "No physical frame duration, clinical strain, flow, force balance, EF or diagnosis is established.\n"
    )
    (OUT / "NOTICE.md").write_text(notice)
    raw = (OUT / "NOTICE.md").read_bytes()
    assets.append(
        {
            "file": "NOTICE.md",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "provenance": "source-derived-teaching",
            "role": "illustration",
        }
    )
    for path in (RUN / "analysis-v2/results.json", RUN / "tissue-analysis-v3/results.json"):
        sources[str(path.relative_to(ROOT))] = sha(path)
    manifest = {
        "schema": 1,
        "id": "retained-cardiac-material-v1",
        "frame": "STRAUS-patient01-healthy-canonical",
        "units": "mm",
        "license": "LicenseRef-STRAUS-local-noncommercial",
        "label_license": "LicenseRef-STRAUS-local-noncommercial",
        "reference_policy": "reader-reference-reveal",
        "sources": sources,
        "checks": {
            "public_input_frames": 120,
            "sampled_boundary_vertices": len(ids),
            "selected_tetra": CELL,
            "missing_axis_cell": MISSING,
            "model_execution": False,
        },
        "assets": assets,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, separators=(",", ":")) + "\n")
    print(f"wrote {OUT}; {len(ids)} fixed-ID vertices; {len(sources)} source hashes")


if __name__ == "__main__":
    main()
