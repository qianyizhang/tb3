"""Derive BR-030 reader assets from retained bytes without executing old methods."""

from __future__ import annotations

import argparse
import ast
import base64
import gzip
import hashlib
import io
import json
import re
from datetime import datetime
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
GEOMETRY = ROOT / "runs/br030-vessel-geometry"
TASK = GEOMETRY / "tasks/coronary-cpr"
RUN = ROOT / "runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL"
ANSWER = RUN / "artifacts/app/answer"
CORRECTION = GEOMETRY / "geometry/terra-arc-correction"
ATTEMPT = "attempt-1fd0ceae7bf0308d3f0a2562"
IMAGE_HASHES = {
    17: "a2e53580318de80899002dbc0f47e553ae07b00914a495213da9dfed698644b8",
    18: "e05d1d7ab5d1adb66928f9f290c36a3549589cbd2307fbaeeb43026b825be94c",
    19: "bbe7544ff7d74287e0a8446fe20b52ceded4cfee803a80373517359393791511",
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def asset(path: Path, role: str, step: int | None = None) -> dict:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
        "bytes": path.stat().st_size,
        "role": role,
        "step": step,
    }


def packed(values: np.ndarray, dtype: str) -> str:
    raw = np.asarray(values, dtype=dtype).tobytes(order="C")
    return base64.b64encode(gzip.compress(raw, mtime=0)).decode()


def mesh_arrays(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read only the exact retained binary PLY layout; never process/reorder faces."""
    with path.open("rb") as stream:
        header = []
        while len(header) < 64:
            line = stream.readline().decode("ascii").strip()
            header.append(line)
            if line == "end_header":
                break
        else:
            raise ValueError("unsupported PLY header")
        assert header[:2] == ["ply", "format binary_little_endian 1.0"]
        vertex_line = next(line for line in header if line.startswith("element vertex "))
        face_line = next(line for line in header if line.startswith("element face "))
        vertex_count = int(vertex_line.split()[-1])
        face_count = int(face_line.split()[-1])
        assert [line for line in header if line.startswith("property ")] == [
            "property float x",
            "property float y",
            "property float z",
            "property list uchar int vertex_indices",
        ]
        vertices = np.frombuffer(stream.read(vertex_count * 12), dtype="<f4").reshape(-1, 3).copy()
        faces = np.frombuffer(
            stream.read(face_count * 13),
            dtype=np.dtype([("count", "u1"), ("indices", "<i4", (3,))]),
        )
        assert len(vertices) == vertex_count and len(faces) == face_count
        assert np.all(faces["count"] == 3) and not stream.read()
        triangles = faces["indices"].astype("<u4")
        assert np.isfinite(vertices).all() and triangles.max() < vertex_count
        assert np.all(faces["indices"] >= 0)
        return vertices, triangles


def observations(step: dict) -> list[dict]:
    items = []
    for result in step.get("observation", {}).get("results", []):
        items.extend(ast.literal_eval(result["content"]))
    return items


def observed_text(step: dict) -> str:
    return "\n".join(
        item.get("text", "") for item in observations(step) if item.get("type") == "input_text"
    )


def state(
    name: str,
    label: str,
    kind: str,
    step: int,
    description: str,
    *,
    axis=None,
    levels=None,
    bounds=None,
    center=None,
    delivered=None,
) -> dict:
    return {
        "id": name,
        "label": label,
        "kind": kind,
        "trace_step": step,
        "axis": axis,
        "levels": levels or [],
        "bounds": bounds,
        "center_ijk": center,
        "description": description,
        "delivered_step": delivered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        parser.error(f"refusing to overwrite existing output: {out}")
    if not out.is_relative_to(ROOT / ".local/anatomy-pose/coronary"):
        parser.error("output must be fresh and under .local/anatomy-pose/coronary")
    if args.manifest and args.manifest.resolve() != HERE / "native-trace.json":
        parser.error("--manifest may only select this recipe's native-trace.json")
    mapping = HERE / "canonical-mapping.md"
    pins = re.findall(r"\| `([^`]+)` \| [\d,]+ \| `([0-9a-f]{64})` \|", mapping.read_text())
    sources = []
    for relative, expected in pins:
        path = ROOT / relative
        if digest(path) != expected:
            raise ValueError(f"mapped source hash mismatch: {relative}")
        role = "provenance"
        if "/environment/" in relative:
            role = (
                "license" if path.name in {"SOURCE_NOTICE.md", "DATA-LICENSE.txt"} else "task-input"
            )
        elif "/tests/" in relative or "/verifier/" in relative:
            role = "private-reference"
        elif "/agent/" in relative:
            role = "trace"
        elif "/artifacts/" in relative:
            role = "saved-output"
        elif "/terra-arc-correction/" in relative or relative.endswith(
            "terra-arc-correction-score.json"
        ):
            role = "private-reference"
        sources.append(asset(path, role))
    freeze = json.loads((GEOMETRY / "freeze.json").read_text())
    frozen_files = freeze["tasks"][0]["files"]
    for relative, expected in frozen_files.items():
        if digest(TASK / relative) != expected:
            raise ValueError(f"frozen source hash mismatch: {relative}")
    apache = ROOT / "presentation/task-explorer/assets/Apache-2.0.txt"
    sources.extend(
        [
            asset(mapping, "provenance"),
            asset(HERE / "prepare_trace.py", "provenance"),
            asset(apache, "license"),
        ]
    )

    image = nib.load(TASK / "environment/data/image.nii.gz")
    affine = image.affine
    inverse = np.linalg.inv(affine)
    shape = list(image.shape)
    spacing = np.linalg.norm(affine[:3, :3], axis=0).tolist()
    hu = np.asanyarray(image.dataobj).astype(np.float32)
    arrays = []
    for name in ["proposed_mask.nii.gz", "editable_region.nii.gz"]:
        native = nib.load(TASK / "environment/data" / name)
        assert list(native.shape) == shape and np.array_equal(native.affine, affine)
        arrays.append(np.asanyarray(native.dataobj) > 0)
    mask, editable = arrays
    corrected_image = nib.load(ANSWER / "corrected_mask.nii.gz")
    assert list(corrected_image.shape) == shape and np.array_equal(corrected_image.affine, affine)
    corrected = np.asanyarray(corrected_image.dataobj) > 0
    added = np.flatnonzero((corrected & ~mask).ravel(order="C"))
    removed = np.flatnonzero((mask & ~corrected).ravel(order="C"))
    assert len(added) == 103 and len(removed) == 0
    assert np.array_equal(corrected[~editable], mask[~editable])
    request = json.loads((TASK / "environment/data/request.json").read_text())
    preview_shape = [128, 112, 103]
    indices = [
        np.rint(np.linspace(0, size - 1, count)).astype(int)
        for size, count in zip(shape, preview_shape, strict=True)
    ]
    for axis, samples in enumerate(indices):
        assert samples[0] == 0 and samples[-1] == shape[axis] - 1
        assert np.all(np.diff(samples) > 0)
    window = [-200, 700]
    preview = np.rint(
        np.clip((hu[np.ix_(*indices)] - window[0]) / (window[1] - window[0]), 0, 1) * 255
    ).astype(np.uint8)
    poster = Image.fromarray(np.flipud(preview.max(axis=1).T))
    buffer = io.BytesIO()
    poster.save(buffer, format="PNG")
    # Reader detail: union of the three logged montage supports, plus 10 native voxels.
    detail_origin = [108, 95, 15]
    detail_shape = [70, 70, 55]
    detail = np.rint(
        np.clip((hu[108:178, 95:165, 15:70] - window[0]) / (window[1] - window[0]), 0, 1) * 255
    ).astype(np.uint8)
    input_data = {
        "shape": shape,
        "affine": affine.tolist(),
        "spacing": spacing,
        "preview_shape": preview_shape,
        "preview_indices": [sample.tolist() for sample in indices],
        "volume": packed(preview, "u1"),
        "detail_origin": detail_origin,
        "detail_shape": detail_shape,
        "detail_volume": packed(detail, "u1"),
        "preview_window": window,
        "poster": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode(),
        "mask_indices": np.flatnonzero(mask.ravel(order="C")).tolist(),
        "editable_indices": np.flatnonzero(editable.ravel(order="C")).tolist(),
        "start_ras": request["start_ras_mm"],
        "end_ras": request["end_ras_mm"],
        "review_ras": request["review_center_ras_mm"],
    }

    trajectory = json.loads((RUN / "agent/trajectory.json").read_text())
    steps = {step["step_id"]: step for step in trajectory["steps"]}
    patch_call = steps[38]["tool_calls"][0]["arguments"]["input"]
    patch = json.loads(re.search(r"const patch = (\".*?\");", patch_call, re.S)[1])
    code = "\n".join(
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    bridge = ast.literal_eval(
        re.search(r"bridge_vox = np.array\((\[.*?\]), dtype=float\)", code, re.S)[1]
    )
    assert len(bridge) == 14
    review_ijk = (inverse @ np.array([*input_data["review_ras"], 1]))[:3].tolist()
    states = [
        state(
            "input",
            "Receive native CTA, mask and helpers",
            "input",
            9,
            "Entire supplied 366x319x205 crop. Mask, binary edit region and route endpoints were supplied; no private reference. Positive native axes L/A/S.",
            bounds=[[0, 0, 0], shape],
            center=review_ijk,
        ),
        state(
            "search",
            "Recorded axial local inspections",
            "planes",
            17,
            "Exact delivered z montage: k=34..54, i=118:168, j=105:155; 21 tiles. Red supplied mask; green editable non-mask tint. Window [-200,500] HU, not detection/reference overlays.",
            axis=2,
            levels=list(range(34, 55)),
            bounds=[[118, 105, 34], [168, 155, 55]],
            delivered=17,
        ),
        state(
            "search-coronal",
            "Recorded coronal local inspections",
            "planes",
            18,
            "Exact delivered y montage: j=112..144, i=118:168, k=25:60; 33 tiles. Original montage helper missing at step14; Pillow replacement succeeds before delivery.",
            axis=1,
            levels=list(range(112, 145)),
            bounds=[[118, 112, 25], [168, 145, 60]],
            delivered=18,
        ),
        state(
            "search-sagittal",
            "Recorded sagittal local inspections",
            "planes",
            19,
            "Exact delivered x montage: i=128..157, j=105:155, k=25:60; 30 tiles. Array transposes and image resize do not change native source geometry.",
            axis=0,
            levels=list(range(128, 158)),
            bounds=[[128, 105, 25], [158, 155, 60]],
            delivered=19,
        ),
        state(
            "contacts",
            "Eventual chosen fourteen-point ridge",
            "alternatives",
            38,
            "After recorded component/HU/path alternatives (steps20..36), step38 explicitly writes this chosen voxel ridge. It is a logged choice, not an earlier detected trajectory or GT. Region bbox is context; exact binary editable membership governs repair.",
            bounds=[[122, 109, 27], [164, 151, 59]],
            center=[142, 130, 43],
        ),
        state(
            "route",
            "Saved local repair and RAS route",
            "route",
            39,
            "Original saved mask adds 103 voxels, removes 0, and preserves all outside editable. Saved 371-point RAS line follows repaired skeleton with exact requested endpoints. No intermediate repaired mask is asserted.",
        ),
        state(
            "cpr",
            "Original saved source-linked CPR",
            "cpr",
            40,
            "Eight actual saved sampled planes with HU and RAS position per pixel; reader controls are not solver screenshots. Saved reported arc_mm ends at 184.809253 mm; this is original retained metadata.",
        ),
        state(
            "mesh",
            "Original complete corrected-mask surface",
            "mesh",
            41,
            "Original RAS mesh, 36128 vertices / 72248 triangles. Includes both coronary trees. No solver-delivered mesh rendering is retained; geometry arrays are saved outputs.",
        ),
        state(
            "saved",
            "Original four-output package",
            "saved",
            42,
            "Original corrected mask, RAS centerline, CPR archive and mesh. Output assertions and saved artifacts are observed evidence; evaluation is a separate reader reference.",
        ),
    ]
    for current in states:
        if current["bounds"]:
            assert all(
                0 <= lo < hi <= size for lo, hi, size in zip(*current["bounds"], shape, strict=True)
            )
        if current["center_ijk"]:
            assert all(
                0 <= value < size for value, size in zip(current["center_ijk"], shape, strict=True)
            )
    centerline = np.load(ANSWER / "centerline.npy")
    assert centerline.shape == (371, 3) and np.isfinite(centerline).all()
    cpr = np.load(ANSWER / "cpr.npz")
    assert cpr["hu"].shape == (8, 371, 65) and cpr["source_ras_mm"].shape == (8, 371, 65, 3)
    assert np.array_equal(cpr["angles_deg"], request["angles_deg"])
    assert np.array_equal(cpr["offsets_mm"], request["offsets_mm"])
    central = int(np.flatnonzero(cpr["offsets_mm"] == 0)[0])
    source_ras = cpr["source_ras_mm"].astype(np.float64)
    central_error = np.linalg.norm(source_ras[:, :, central] - centerline[None], axis=-1)
    offset_error = np.abs(
        np.linalg.norm(source_ras - centerline[None, :, None, :], axis=-1)
        - np.abs(cpr["offsets_mm"])[None, None, :]
    )
    assert float(central_error.max()) < 0.00005 and float(offset_error.max()) < 0.00005
    source_voxels = (
        np.einsum("nj,ij->ni", source_ras.reshape(-1, 3), inverse[:3, :3]) + inverse[:3, 3]
    )
    assert np.isfinite(source_voxels).all()
    outside = np.any((source_voxels < 0) | (source_voxels > np.asarray(shape) - 1), axis=1)
    resampled = map_coordinates(
        hu, source_voxels.T, order=1, mode="constant", cval=-1024, prefilter=False
    )
    delta = np.abs(resampled - cpr["hu"].ravel(order="C"))
    assert float(np.percentile(delta, 99)) < 0.05
    assert np.all(cpr["hu"].ravel(order="C")[outside] == -1024)

    vertices, faces = mesh_arrays(ANSWER / "vessels.ply")
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    unique_edges, inverse_edges, counts = np.unique(
        np.sort(edges, axis=1), axis=0, return_inverse=True, return_counts=True
    )
    assert np.all(counts == 2)
    direction = np.where(edges[:, 0] < edges[:, 1], 1, -1)
    assert np.all(np.bincount(inverse_edges, weights=direction) == 0)
    native_vertices = np.einsum("nj,ij->ni", vertices, inverse[:3, :3]) + inverse[:3, 3]
    assert np.isfinite(native_vertices).all()
    assert np.all(native_vertices >= -0.5 - 0.0001) and np.all(
        native_vertices <= np.asarray(shape) - 0.5 + 0.0001
    )
    volume_mm3 = float(
        np.einsum(
            "ij,ij->i",
            vertices[faces[:, 0]].astype(float),
            np.cross(vertices[faces[:, 1]].astype(float), vertices[faces[:, 2]].astype(float)),
        ).sum()
        / 6
    )
    assert volume_mm3 > 0
    correction = np.load(CORRECTION / "cpr.npz")
    for key in ["hu", "source_ras_mm", "angles_deg", "offsets_mm"]:
        assert np.array_equal(cpr[key], correction[key])
    for name in ["corrected_mask.nii.gz", "centerline.npy", "vessels.ply"]:
        assert digest(ANSWER / name) == digest(CORRECTION / name)
    true_arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(centerline, axis=0), axis=1))]
    assert np.allclose(true_arc, correction["arc_mm"], rtol=0, atol=1e-9)
    assert not np.allclose(cpr["arc_mm"], true_arc)
    frozen = json.loads((RUN / "verifier/metrics.json").read_text())
    corrected_score = json.loads(
        (GEOMETRY / "geometry/terra-arc-correction-score.json").read_text()
    )
    selected = [
        7,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        22,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        38,
        39,
        40,
        41,
        42,
    ]
    trace = [
        {
            "step": sid,
            "timestamp": steps[sid].get("timestamp"),
            "calls": [
                json.dumps(call["arguments"], ensure_ascii=False)
                for call in steps[sid].get("tool_calls", [])
            ],
            "output": observed_text(steps[sid]),
        }
        for sid in selected
    ]
    times = [
        datetime.fromisoformat(step["timestamp"].replace("Z", "+00:00"))
        for step in trajectory["steps"]
    ]
    observed = {
        "states": states,
        "bridge_ijk": bridge,
        "added_indices": added.tolist(),
        "removed_indices": removed.tolist(),
        "centerline_ras": centerline.tolist(),
        "cpr": {
            "shape": list(cpr["hu"].shape),
            "angles_deg": cpr["angles_deg"].tolist(),
            "offsets_mm": cpr["offsets_mm"].tolist(),
            "arc_mm": cpr["arc_mm"].tolist(),
            "hu": packed(cpr["hu"], "<f4"),
            "source_ras_mm": packed(cpr["source_ras_mm"], "<f4"),
        },
        "mesh": {
            "vertex_count": len(vertices),
            "face_count": len(faces),
            "vertices": packed(vertices, "<f4"),
            "faces": packed(faces, "<u4"),
        },
        "trace": trace,
        "elapsed_seconds": (times[-1] - times[0]).total_seconds(),
        "steps_in_trace": len(steps),
        "evidence": "Retained BR-030 selected tool actions and four original saved outputs. Step 39 prints 103 additions, 354 skeleton nodes, 371 saved points and the reported arc endpoint 184.809253 mm. Step 40 inspects saved geometry/CPR shapes; step 41 checks closure and winding; step 42 reports outside edits 0 and components 3 to 2. No CPR/mesh screenshot was delivered. These are logged output assertions, not independent clinical or held-out validation.",
    }
    reference = {
        "reward": frozen["reward"],
        "stages": frozen["stages"],
        "metrics": {
            key: value for key, value in frozen["metrics"].items() if type(value) in (int, float)
        },
        "corrected_arc_mm": correction["arc_mm"].tolist(),
        "correction_stages": corrected_score["stages"],
        "correction_only_arc": True,
        "limits": "Original reward 0 remains frozen: repair/trace/mesh pass, CPR distance-axis consistency fails. Only arc_mm changed in the separate post-outcome author package; this is not another model success. Mask-derived references are related evidence, case 1 is training-split development, and no stenosis/plaque ground truth, independent clinical adjudication or population difficulty is established.",
    }
    data = {"attempt": ATTEMPT, "input": input_data, "observed": observed, "reference": reference}
    out.mkdir(parents=True)
    derivatives = []
    delivered = []
    for sid, expected in IMAGE_HASHES.items():
        item = ast.literal_eval(steps[sid]["observation"]["results"][0]["content"])[1]
        assert item["type"] == "input_image"
        raw = base64.b64decode(item["image_url"].split(",", 1)[1], validate=True)
        assert hashlib.sha256(raw).hexdigest() == expected
        path = out / f"delivered-step-{sid}-1.png"
        path.write_bytes(raw)
        with Image.open(path) as image_check:
            image_check.verify()
        derivatives.append(asset(path, "delivered-image", sid))
        delivered.append({"step": sid, "path": path.name})
    data["delivered_images"] = delivered
    (out / "data.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    derivatives.insert(0, asset(out / "data.json", "derived-display"))
    for source, name, role in [
        (TASK / "environment/SOURCE_NOTICE.md", "SOURCE_NOTICE.txt", "license"),
        (TASK / "environment/DATA-LICENSE.txt", "DATA-LICENSE.txt", "license"),
        (apache, "Apache-2.0.txt", "license"),
        (TASK / "instruction.md", "instruction.txt", "task-input"),
    ]:
        (out / name).write_bytes(source.read_bytes())
        derivatives.append(asset(out / name, role))
    (out / "DERIVATIVES.txt").write_text(
        "ImageCAS CTA: Xiaowei Xu and collaborators, Apache 2.0 listing; ImageCAS-X annotations/geometry CC BY 4.0, Bransby et al. Source code MIT. Exact source notice/licenses retained; no endorsement.\nReader derivatives: 128x112x103 nearest integer native CTA sampling, endpoints retained, fixed [-200,700] HU uint8 display; whole-crop coronal MIP over j, i increases toward L horizontally and k upward S. Native C-flat mask/edit/added/removed lists; ((i*shape[1])+j)*shape[2]+k. Original route retains float64 JSON precision. Original CPR float32 little-endian HU and sourceRAS buffers, shape[angle,route,offset,(xyz)], C-order gzip with mtime 0. Original mesh float32LE positions and uint32LE triangular faces, vertex/face order preserved. Exact three delivered overlays keep original [-200,500] HU view/resize/color semantics. No invented intermediate mask or corrected arc in observed payload. Reference correction is separately gated.\n"
    )
    derivatives.append(asset(out / "DERIVATIVES.txt", "license"))
    qa = {
        "central_source_ras_max_error_mm": float(central_error.max()),
        "offset_distance_max_error_mm": float(offset_error.max()),
        "source_hu_sampling_p99_error_hu": float(np.percentile(delta, 99)),
        "source_hu_sampling_max_error_hu": float(delta.max()),
        "source_samples_outside_grid": int(outside.sum()),
        "sampler": "Scipy direct sourceRAS→native trilinear, order1, prefilterFalse, modeconstant cval-1024; independent read-only byte/geometry QA, not a scorer replay or regrade.",
        "tolerances": {"central_mm": 0.00005, "offset_mm": 0.00005, "p99_hu": 0.05},
        "mesh_closed_edges": True,
        "mesh_consistent_winding": True,
        "mesh_edges": len(unique_edges),
        "mesh_volume_mm3": volume_mm3,
        "original_arc_end_mm": float(cpr["arc_mm"][-1]),
        "corrected_arc_end_mm": float(correction["arc_mm"][-1]),
        "correction_only_arc": True,
    }
    receipt = {
        "schema": 1,
        "attempt": ATTEMPT,
        "sources": sources,
        "derivatives": derivatives,
        "preview": {
            "shape": preview_shape,
            "indices": [samples.tolist() for samples in indices],
            "window_hu": window,
            "native_detail": {
                "origin": detail_origin,
                "shape": detail_shape,
                "uint8_sha256": hashlib.sha256(detail.tobytes()).hexdigest(),
                "method": "Union of logged montage supports plus 10 native voxels; same CT window, no spatial downsampling.",
            },
            "uint8_sha256": hashlib.sha256(preview.tobytes(order="C")).hexdigest(),
        },
        "verification": {
            "frozen_files": len(frozen_files),
            "exact_pngs": 3,
            "added_voxels": len(added),
            "removed_voxels": len(removed),
            "outside_edits": 0,
            "states_bounds": True,
            "qa": qa,
        },
        "limits": [
            "No historical preparation/helper/author/scorer/model code executed.",
            "Bounded preview is display context, not native-resolution validation.",
            "Original distance-axis mismatch deliberately preserved; original score unchanged.",
            "No intermediate mask or solver-viewed CPR/mesh image invented.",
            "Public training-split fixture and mask-related reference; no clinical/population claim.",
            "No browser visual acceptance or canonical binding performed.",
        ],
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    derivatives.append(asset(out / "receipt.json", "provenance"))
    manifest = {
        "schema": 1,
        "id": "br030-native-trace",
        "entry_id": "ours",
        "attempt": ATTEMPT,
        "adapter": "coronary-cpr",
        "coordinates": "RAS-mm",
        "saved_state": "saved",
        "notice": "One retained BR030 coronary repair→route→CPR Terra/high attempt on a supplied ImageCAS crop/mask/helpers. Original saved outputs and separately gated reader references have distinct roles. Training-split development geometry does not establish clinical accuracy or difficulty.",
        "recovery": "Recover mapped source bytes and run groups/tubular-anatomy/presentation/native-coronary-trace/prepare_trace.py into a fresh .local/anatomy-pose/coronary directory. See README; no trial, old recipe execution or scoring is implied.",
        "assets": derivatives + sources,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if args.manifest:
        args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(out),
                "data_bytes": (out / "data.json").stat().st_size,
                "delivered_bytes": sum(
                    item["bytes"] for item in derivatives if item["role"] == "delivered-image"
                ),
                "states": len(states),
                "selected_calls": len(trace),
                "qa": qa,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
