"""Derive a reader-only replay from retained data and logged poses; never run a solver."""

import ast
import base64
import gzip
import hashlib
import io
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / ".local/anatomy-pose/trace"
OUT.mkdir(parents=True, exist_ok=True)
TASK = ROOT / "runs/br019-registration/tasks/cardiac-r01"
RUN = ROOT / "runs/br019-cardiac-r01-terra-high-v1-20260916/cardiac-r01__7yuEb55"
TRACE = RUN / "agent/trajectory.json"
trajectory = json.loads(TRACE.read_text())
steps = {s["step_id"]: s for s in trajectory["steps"]}


def observations(sid):
    result = []
    for item in steps[sid].get("observation", {}).get("results", []):
        result.extend(ast.literal_eval(item["content"]))
    return result


def text(sid):
    return "\n".join(x.get("text", "") for x in observations(sid) if x.get("type") == "input_text")


def logged_matrix(sid):
    match = re.search(r"\[\[.*?\]\]", text(sid), re.S)
    return np.fromstring(match[0].replace("[", " ").replace("]", " "), sep=" ").reshape(4, 4)


def png(array):
    image = Image.fromarray(np.asarray(array, dtype=np.uint8))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


volume = np.load(TASK / "environment/data/volume.npz")
hu = volume["hu"].astype(np.float32)
affine = volume["voxel_to_lps"]
target = np.load(TASK / "environment/data/target.npy")
answer = np.asarray(
    json.loads((RUN / "artifacts/app/answer/pose.json").read_text())["slice_to_lps"]
)
reference = np.asarray(json.loads((TASK / "tests/truth.json").read_text())["slice_to_lps"])
frozen_metrics = json.loads((RUN / "verifier/metrics.json").read_text())
axis = np.linspace(0, 179, 90)
coords = np.asarray(np.meshgrid(axis, axis, axis, indexing="ij"))
preview_hu = map_coordinates(hu, coords, order=1, prefilter=False)
preview = np.rint(np.clip((preview_hu + 1000) / 1500, 0, 1) * 255).astype(np.uint8)
preview_bytes = preview.tobytes()
target_mask = gaussian_filter((target > 5).astype(float), 2.0)
rr, cc = np.indices(target.shape, dtype=float)
pixel_grid = np.stack((cc.ravel() * 0.9, rr.ravel() * 0.9, np.zeros(cc.size), np.ones(cc.size)))
vv, uu = np.meshgrid(np.linspace(0, 191, 7), np.linspace(0, 191, 7), indexing="ij")
score_grid = np.stack((uu.ravel() * 0.9, vv.ravel() * 0.9, np.zeros(49), np.ones(49)))


def reslice(pose):
    indices = np.einsum("ij,jn->in", np.linalg.inv(affine) @ pose, pixel_grid)[:3]
    assert np.isfinite(indices).all()
    values = map_coordinates(hu, indices, order=1, mode="constant", cval=-1024, prefilter=False)
    return np.rint(np.clip((values.reshape(target.shape) + 150) / 500, 0, 1) * 255).astype(np.uint8)


def diagnostics(pose, image):
    errors = np.linalg.norm(((pose - reference) @ score_grid)[:3], axis=0)
    delta = image.astype(float) - target.astype(float)
    return {
        "rms_mm": float(np.sqrt(np.mean(errors**2))),
        "max_mm": float(errors.max()),
        "pixel_rmse": float(np.sqrt(np.mean(delta**2))),
        "equal_pixels": int((delta == 0).sum()),
        "different_pixels": int((delta != 0).sum()),
        "max_intensity_difference": float(np.abs(delta).max()),
    }


raw = np.fromstring(re.search(r"DE 6 [\d.]+ \[(.*?)\]", text(43), re.S)[1], sep=" ")
rotation = Rotation.from_euler("ZYZ", raw[:3]).as_matrix()
lo = np.array([-95.83203125, -295.33203125, 748.70001221])
hi = np.array([172.66796875, -26.83203125, 1017.20001221])
margin = (191 * 0.9 / 2) * (np.abs(rotation[:, 0]) + np.abs(rotation[:, 1]))
coarse = np.eye(4)
coarse[:3, :3] = rotation
coarse[:3, 3] = (
    lo + margin + raw[3:] * (hi - lo - 2 * margin) - rotation[:, :2] @ np.array([191 * 0.9 / 2] * 2)
)

states = []
for name, sid, pose, role in [
    (
        "early",
        17,
        logged_matrix(17),
        "Reconstructed from the printed step-17 matrix; rounded log precision.",
    ),
    (
        "bounded",
        41,
        logged_matrix(41),
        "Reconstructed from the printed step-41 matrix; rounded log precision.",
    ),
    (
        "coarse",
        43,
        coarse,
        "Reconstructed from step-43 DE seed 6 and step-29 centre mapping; rounded log parameters.",
    ),
    (
        "final",
        43,
        answer,
        "Preserved submitted pose.json, full stored precision; re-rendered from the native CT.",
    ),
]:
    image = reslice(pose)
    Image.fromarray(image).save(OUT / f"{name}.png")
    delta = np.abs(image.astype(float) - target.astype(float))
    states.append(
        {
            "id": name,
            "trace_step": sid,
            "pose": pose.tolist(),
            "image": png(image),
            "silhouette": png(255 / (1 + np.exp(-(image.astype(float) - 5) / 4))),
            "difference": png(np.clip(delta * 4, 0, 255)),
            "role": role,
            "diagnostic": diagnostics(pose, image),
        }
    )

final = states[-1]["diagnostic"]
assert final["different_pixels"] == 56 and final["max_intensity_difference"] == 1
assert abs(final["rms_mm"] - frozen_metrics["rms_mm"]) < 1e-10
assert abs(final["max_mm"] - frozen_metrics["max_mm"]) < 1e-10

delivered_images = []
for sid in [10, 11, 18, 26]:
    for index, item in enumerate(observations(sid)):
        if item.get("type") == "input_image":
            url = item["image_url"]
            filename = f"delivered-step-{sid}-{index}.png"
            (OUT / filename).write_bytes(base64.b64decode(url.split(",", 1)[1]))
            delivered_images.append({"step": sid, "path": filename})

early_delivered = next(item for item in delivered_images if item["step"] == 18)
assert np.array_equal(
    np.asarray(Image.open(OUT / early_delivered["path"]).convert("L")),
    np.asarray(Image.open(OUT / "early.png")),
)

selected = [
    7,
    9,
    10,
    11,
    13,
    17,
    19,
    20,
    21,
    22,
    23,
    25,
    27,
    28,
    29,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    45,
]
excerpts = []
for sid in selected:
    step = steps[sid]
    excerpt = {
        "step": sid,
        "timestamp": step["timestamp"],
        "calls": [c["arguments"]["input"] for c in step.get("tool_calls", [])],
        "output": text(sid),
    }
    excerpts.append(excerpt)

slice_previews = []
for i in range(3):
    a = np.take(preview, 45, axis=i).T
    slice_previews.append(png(a))

payload = {
    "source": "TotalSegmentator small v2.0.1 / s0915",
    "attempt": "attempt-0b9d524174a3e1a9e4bb4901",
    "shape": [180, 180, 180],
    "spacing_mm": 1.5,
    "affine": affine.tolist(),
    "preview_size": 90,
    "preview_window_hu": [-1000, 500],
    "preview_base64_gzip": base64.b64encode(gzip.compress(preview_bytes, mtime=0)).decode(),
    "target": png(target),
    "target_silhouette": png(target_mask * 255),
    "slice_previews": slice_previews,
    "states": states,
    "frozen_metrics": frozen_metrics,
    "trace": excerpts,
    "delivered_images": delivered_images,
    "reference_pose": reference.tolist(),
    "elapsed_seconds": 575.77,
    "steps_in_trace": len(trajectory["steps"]),
}
(OUT / "data.json").write_text(json.dumps(payload, separators=(",", ":")))

paths = [
    TRACE,
    TASK / "instruction.md",
    TASK / "environment/data/volume.npz",
    TASK / "environment/data/target.npy",
    TASK / "environment/data/image.json",
    TASK / "tests/truth.json",
    TASK / "tests/score.py",
    RUN / "artifacts/app/answer/pose.json",
    RUN / "verifier/metrics.json",
]
receipt = {
    "schema_version": 1,
    "purpose": "Reader-only source-derived trace explainer; no fresh model run or optimizer execution.",
    "attempt_id": payload["attempt"],
    "recipe": {
        "path": str(Path(__file__).resolve().relative_to(ROOT)),
        "sha256": hash_file(Path(__file__)),
    },
    "source_hashes": [{"path": str(p.relative_to(ROOT)), "sha256": hash_file(p)} for p in paths],
    "derivation": {
        "preview": "Trilinear 90^3 preview spanning native voxel centres 0..179, window [-1000,500] HU; not used for scoring.",
        "candidate_images": "Native 180^3 HU trilinear reslices; task window [-150,350] HU, 192^2 at 0.9 mm/pixel.",
        "silhouette": "Target Gaussian sigma=2 px of target>5; candidate display applies logistic (image-5)/4. Display uses rounded reslices; not an exact replay of the optimizer objective.",
        "difference": "Absolute 8-bit image difference multiplied by 4, clipped at 255; display only.",
    },
    "states": [
        {k: v for k, v in s.items() if k not in ["image", "silhouette", "difference"]}
        for s in states
    ],
    "verification": {
        "early_render_matches_delivered_step_18": True,
        "final_pixels_different": 56,
        "pixel_denominator": 36864,
        "max_intensity_difference": 1,
        "frozen_metrics_reproduced": True,
    },
    "limits": [
        "Only selected logged states are reconstructed; no full optimizer history was retained here.",
        "Intermediate geometric errors are post-hoc diagnostics using evaluator-only truth.",
        "All data are one same-acquisition crop, not a complete original scan or clinical validation.",
    ],
}
(OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
for source, name in [
    (TASK / "instruction.md", "instruction.txt"),
    (TASK / "environment/SOURCE_NOTICE.md", "SOURCE_NOTICE.txt"),
    (TASK / "environment/DATA-LICENSE.txt", "DATA-LICENSE.txt"),
    (TASK / "tests/score.py", "scorer.txt"),
]:
    (OUT / name).write_bytes(source.read_bytes())
print(
    json.dumps(
        {
            "output": str(OUT),
            "states": [{"id": s["id"], **s["diagnostic"]} for s in states],
            "bytes": (OUT / "data.json").stat().st_size,
        },
        indent=2,
    )
)
