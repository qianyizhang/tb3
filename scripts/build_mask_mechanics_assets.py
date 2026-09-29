"""Build local BR-035 explainer assets from retained masks, answers and review data.

Only retained files are read. Historical solvers and authoring modules are not imported.
"""

import argparse
import base64
import hashlib
import json
import struct
import zlib
from pathlib import Path

import numpy as np

ROOT = next(
    parent for parent in Path(__file__).resolve().parents if (parent / "workbench.toml").is_file()
)
DRAFT = Path(__file__).resolve().parents[1]
AUDIT = Path("groups/cardiac-motion/presentation/sources/mask-mechanics-audit.json")
RESOLUTION = Path("groups/cardiac-motion/presentation/sources/mask-mechanics-resolution.json")
PREP = Path("runs/br035-segmentation-mechanics/prepared")
REVIEW = Path("runs/br035-segmentation-mechanics/review")
ANALYTIC = Path("runs/br035-segmentation-mechanics/analytic-validation.json")
ANSWERS = {
    "masks": Path(
        ".local/inputs/reproduction/cardiac-motion-br035/saved/attempt-c73a7ef0c267fd9eb63eb652/answer/prediction.npz"
    ),
    "masks-images": Path(
        ".local/inputs/reproduction/cardiac-motion-br035/saved/attempt-fb9e01e19f28f2dc5575df6a/answer/prediction.npz"
    ),
}
INPUT_SLICES = (43, 40, 42)  # z,y,x; source mask/review section alignment
TRUTH_CELL = 4639  # positive AHA 8; fixed source-cell centroid locatable in both answers


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def chunk(kind, data):
    payload = kind + data
    return (
        struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    )


def png_data(array, mask=False):
    """Lossless code-native PNG; no image library or independent reslicing."""
    arr = np.asarray(array, dtype=np.uint8)
    if mask:
        rgba = np.zeros((*arr.shape, 4), dtype=np.uint8)
        rgba[arr > 0] = (244, 188, 73, 235)
        raw = b"".join(b"\0" + row.tobytes() for row in rgba)
        color = 6
    else:
        raw = b"".join(b"\0" + row.tobytes() for row in arr)
        color = 0
    header = struct.pack(">IIBBBBB", arr.shape[1], arr.shape[0], 8, color, 0, 0, 0)
    bits = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    return "data:image/png;base64," + base64.b64encode(bits).decode("ascii")


def planes(array, selection):
    z, y, x = selection
    return (array[z, :, :], array[:, y, :], array[:, :, x])


def paths(lines):
    return "".join(
        "".join(("M" if i == 0 else "L") + f"{xy[1]:.1f} {xy[0]:.1f}" for i, xy in enumerate(line))
        for line in lines
        if len(line) > 1
    )


def round_list(a, n=4):
    return np.round(np.asarray(a, dtype=float), n).tolist()


def locate_probe(points0, tetra, position):
    centres = points0[tetra].mean(axis=1)
    distance = np.sum((centres - position) ** 2, axis=1)
    for index in np.argpartition(distance, 256)[:256]:
        v = points0[tetra[index]]
        D = np.column_stack((v[1] - v[0], v[2] - v[0], v[3] - v[0]))
        try:
            q = np.linalg.solve(D, position - v[0])
        except np.linalg.LinAlgError:
            continue
        bary = np.r_[1 - q.sum(), q]
        if bary.min() >= -1e-5 and bary.max() <= 1 + 1e-5:
            return int(index), bary
    raise AssertionError("Fixed source probe is not in saved initial mesh")


def gradient(points, cell):
    vertices = points[:, cell]
    Dm = np.column_stack(
        (
            vertices[0, 1] - vertices[0, 0],
            vertices[0, 2] - vertices[0, 0],
            vertices[0, 3] - vertices[0, 0],
        )
    )
    Ds = np.stack(
        (
            vertices[:, 1] - vertices[:, 0],
            vertices[:, 2] - vertices[:, 0],
            vertices[:, 3] - vertices[:, 0],
        ),
        axis=2,
    )
    return Ds @ np.linalg.inv(Dm)


def build(out):
    assert not out.exists(), "Use a fresh output directory"
    resolution_path = DRAFT / RESOLUTION if (DRAFT / RESOLUTION).exists() else ROOT / RESOLUTION
    receipt = json.loads(resolution_path.read_text())
    expected = {item["path"]: item["sha256"] for item in receipt["checked_files"]}
    assert sha(ROOT / AUDIT) == "54da7ec2c18c06a927f2c5d8996ae6ce9842c03e952d70f598b5b931d18512ba"
    used = {str(AUDIT): sha(ROOT / AUDIT), str(RESOLUTION): sha(resolution_path)}

    def verify(path, digest=None):
        got = sha(ROOT / path)
        assert got == (digest or expected[str(path)]), str(path)
        used[str(path)] = got

    paths_to_verify = [
        PREP / "synthetic_masks.npz",
        PREP / "synthetic_images.npy",
        PREP / "truth.npz",
        PREP / "clinical_masks.npz",
        *ANSWERS.values(),
        Path("runs/br035-segmentation-mechanics/controls/oracle.npz"),
        Path("runs/br035-segmentation-mechanics/controls/static.npz"),
    ]
    for path in paths_to_verify:
        verify(path)
    for path, digest in (
        (
            REVIEW / "masks-synthetic/data.json",
            "0bf717c97198cd20820727a467a4a83931c743f13feb47bb759637a25beda4ca",
        ),
        (
            REVIEW / "masks-images-synthetic/data.json",
            "267111b044e5efc23a9cb1f39adbe17371ee49d96bb071789dc5b17483db81b5",
        ),
        (ANALYTIC, "3fb06487b9610fcc9cc92f7bb1639c24042f2d750ef93d87d9df6ec4e9bab1d9"),
    ):
        verify(path, digest)

    audit = json.loads((ROOT / AUDIT).read_text())
    with np.load(ROOT / PREP / "synthetic_masks.npz", allow_pickle=False) as pack:
        masks = np.asarray(pack["masks"])
    images = np.load(ROOT / PREP / "synthetic_images.npy", mmap_mode="r")
    with np.load(ROOT / PREP / "clinical_masks.npz", allow_pickle=False) as pack:
        clinical = np.asarray(pack["masks"])
    assert masks.shape == (30, 86, 81, 85) and clinical.shape == (18, 90, 55, 63)
    assert images.shape == masks.shape
    clinical_selection = tuple(
        int(np.argmax(clinical[0].sum(axis=axes))) for axes in ((1, 2), (0, 2), (0, 1))
    )
    reviews = {
        key: json.loads((ROOT / REVIEW / f"{key}-synthetic/data.json").read_text())
        for key in ANSWERS
    }
    assert reviews["masks"]["sections"][1] == reviews["masks-images"]["sections"][1], (
        "the supplied masks must match across conditions"
    )
    input_contours = [
        [paths(reviews["masks"]["sections"][1][view][phase]) for phase in range(30)]
        for view in range(3)
    ]
    image_scale = float(np.percentile(np.asarray(images[0])[np.asarray(images[0]) > 0], 99.8))
    assert image_scale > 0
    source = {
        "frame": "BR035-synthetic-world-mm",
        "spacing_mm": 1.5,
        "origin_xyz_mm": [81, -108, 95],
        "array_order": "T,Z,Y,X",
        "semantics": "myocardial_wall",
        "phase_count": 30,
        "physical_timestamps_s": None,
        "slice_zyx": list(INPUT_SLICES),
        "views": ["axial z=159.5 mm", "coronal y=-48 mm", "sagittal x=144 mm"],
        "input_masks_png": [
            [
                png_data(p.astype(np.uint8), mask=True)
                for phase in masks
                for p in [planes(phase, INPUT_SLICES)[view]]
            ]
            for view in range(3)
        ],
        "input_images_png": [
            [
                png_data(
                    np.clip(
                        np.asarray(planes(phase, INPUT_SLICES)[view], dtype=np.float64)
                        / image_scale
                        * 255,
                        0,
                        255,
                    ).astype(np.uint8)
                )
                for phase in images
            ]
            for view in range(3)
        ],
        "input_contours_px": input_contours,
        "image_display": "fixed 0 to first-frame 99.8th positive percentile, float64 scaling and uint8 truncation; registered appearance, not motion truth",
        "analytic_ambiguity": json.loads((ROOT / ANALYTIC).read_text())["ambiguity"],
        "clinical": {
            "frame": "BR035-clinical-world-mm",
            "origin_xyz_mm": [-47, -39, -70],
            "spacing_mm": 1.5,
            "semantics": "lv_cavity",
            "slice_zyx": list(clinical_selection),
            "times_seconds": audit["source_derivation"]["clinical"]["timestamps_s"],
            "mask_png": [
                [
                    png_data(planes(phase, clinical_selection)[view].astype(np.uint8), mask=True)
                    for phase in clinical
                ]
                for view in range(3)
            ],
        },
    }
    # Check source contour and chosen slices are on the same voxel coordinates.
    assert int(masks[0, INPUT_SLICES[0]].sum()) > 500
    output = {"frame": "BR035-synthetic-world-mm", "conditions": {}, "clinical": {}}
    private = {
        "role": "reader-only simulator material reference, fixed source-cell probes and controls",
        "conditions": {},
        "source_cell": TRUTH_CELL,
    }
    with np.load(ROOT / PREP / "truth.npz", allow_pickle=False) as truth:
        truth_points = np.asarray(truth["points"])
        truth_tetra = np.asarray(truth["tetra"])
        source_axes = np.asarray(truth["directions"][:, TRUTH_CELL])
        source_label = int(truth["cell_labels"][TRUTH_CELL])
        source_weight = float(truth["weights"][TRUTH_CELL])
        source_centroid = truth_points[:, truth_tetra[TRUTH_CELL]].mean(axis=1)
    assert (
        source_label > 0
        and np.isfinite(source_axes).all()
        and np.linalg.norm(source_axes, axis=1).min() > 0.5
    )
    truth_F = gradient(truth_points, truth_tetra[TRUTH_CELL])
    truth_strain = [100 * (np.linalg.norm(truth_F @ axis, axis=1) - 1) for axis in source_axes]
    private.update(
        {
            "source_AHA_label": source_label,
            "source_reference_weight": source_weight,
            "source_trajectory_mm": round_list(source_centroid),
            "source_engineering_strain_pp": [round_list(v) for v in truth_strain],
        }
    )

    for key, path in ANSWERS.items():
        with np.load(ROOT / path, allow_pickle=False) as pack:
            points = np.asarray(pack["points"])
            tetra = np.asarray(pack["tetra"])
            assert points.shape == (30, 63326, 3)
            assert tetra.shape == ((233865 if key == "masks" else 280638), 4)
            centres = points[0, tetra].mean(axis=1)
            index = int(np.argmin(np.sum((centres - points[0].mean(axis=0)) ** 2, axis=1)))
            selected = tetra[index]
            selected_points = points[:, selected]
            F = np.asarray(pack["F"][:, index])
            E = np.asarray(pack["E"][:, index])
            J = np.asarray(pack["J"][:, index])
            calculated = gradient(points, selected)
            assert np.max(np.abs(calculated - F)) < 1e-4
            assert np.max(np.abs((np.swapaxes(F, 1, 2) @ F - np.eye(3)) / 2 - E)) < 1e-4
            assert np.max(np.abs(np.linalg.det(F) - J)) < 1e-4
            probe_tetra, bary = locate_probe(points[0], tetra, source_centroid[0])
            predicted = np.einsum("tnc,n->tc", points[:, tetra[probe_tetra]], bary)
            probe_F = gradient(points, tetra[probe_tetra])
            probe_strain = [
                100 * (np.linalg.norm(probe_F @ axis, axis=1) - 1) for axis in source_axes
            ]
            sample_indices = np.arange(0, points.shape[1], 96)
            samples = round_list(points[:, sample_indices], 2)
        result = audit["saved_results"][key]
        output["conditions"][key] = {
            "vertices": 63326,
            "tetrahedra": int(tetra.shape[0]),
            "sample_rule": "saved vertex indices 0,96,...; display only",
            "sampled_points_mm": samples,
            "selected_cell_index": index,
            "selected_cell_vertex_indices": selected.tolist(),
            "selected_vertices_mm": round_list(selected_points),
            "selected_F": round_list(F, 5),
            "selected_E_fraction": round_list(E, 5),
            "selected_J": round_list(J, 5),
            "saved_sections_px": [
                [paths(reviews[key]["sections"][0][view][phase]) for phase in range(30)]
                for view in range(3)
            ],
            "mask_dice": round_list(result["geometry"]["per_frame_mask_dice"], 5),
            "construction_reward": result["reward"],
        }
        private["conditions"][key] = {
            "fixed_answer_tetra_for_source_probe": probe_tetra,
            "barycentric_weights": round_list(bary, 7),
            "predicted_probe_trajectory_mm": round_list(predicted),
            "predicted_engineering_strain_pp": [round_list(v) for v in probe_strain],
            "material_coverage_pct": round(float(result["material"]["coverage"]) * 100, 4),
            "motion_rmse_mm": round(float(result["material"]["motion_rmse_mm"]), 4),
            "radial_mae_pp": round(float(result["material"]["strain_mae_pp"][2]), 4),
        }

    for key in ("clinical-masks", "clinical-masks-images"):
        record = audit["saved_results"][key]
        output["clinical"][key] = {
            "volume_ml": round_list(record["geometry"]["volume_ml"], 5),
            "mask_volume_ml": round_list(record["geometry"]["mask_volume_ml"], 5),
            "ef_pct": round(float(record["cavity_function"]["ef_pct"]), 5),
            "myocardial_strain_supported": False,
            "construction_reward": record["reward"],
        }
    private["controls"] = {
        "oracle": {
            "role": "privileged exact-source control, not legal solver input",
            "construction_reward": audit["saved_results"]["oracle"]["reward"],
        },
        "static": {
            "role": "static/no-motion control",
            "construction_reward": audit["saved_results"]["static"]["reward"],
        },
    }
    private["missing_direction"] = (
        "Three positive-AHA source cells lack usable axes; excluded, not assigned zero strain."
    )

    out.mkdir(parents=True)
    payloads = {"source.json": source, "output.json": output, "reference.json": private}
    for name, payload in payloads.items():
        (out / name).write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    notice = (
        "# Local BR-035 teaching pack\n\nSTRAUS synthetic myocardium and EchoXFlow clinical cavity "
        "are separate source conditions. This pack is local noncommercial interpretation; inspected STRAUS "
        "metadata did not establish onward redistribution rights. Clinical source is CC-BY-NC-SA-4.0. "
        "Private simulator trajectories, anatomical axes and material probes are reader-only. "
        "No patient myocardial strain truth is included.\n"
    )
    (out / "NOTICE.md").write_text(notice)
    assets = [
        {
            "file": name,
            "sha256": sha(out / name),
            "bytes": (out / name).stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if name == "reference.json" else "illustration",
        }
        for name in (*payloads, "NOTICE.md")
    ]
    manifest = {
        "schema": 1,
        "id": "retained-mask-mechanics-v1",
        "frame": "BR035-world-mm",
        "units": "mm",
        "license": "LicenseRef-STRAUS-local-research-terms-unresolved",
        "label_license": "LicenseRef-STRAUS-local-research-terms-unresolved",
        "reference_policy": "reader-reference-reveal",
        "source_class": "source-derived-teaching",
        "sources": used,
        "checks": {
            "synthetic_phases": 30,
            "clinical_frames": 18,
            "reference_cell": TRUTH_CELL,
            "selected_answer_cells": {
                k: v["selected_cell_index"] for k, v in output["conditions"].items()
            },
            "model_execution": False,
        },
        "assets": assets,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(out), "assets": assets}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output)
