"""Read retained BR-026 inputs/output; reconstruct logged threshold components only."""

import ast
import base64
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, label

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / ".local/anatomy-pose/vessel"
OUT.mkdir(parents=True, exist_ok=True)
TASK = ROOT / "runs/br026-vessel-repair/tasks/vessel-v01"
RUN = ROOT / "runs/br026-vessel-v01-terra-high-v1-20260916/vessel-v01__c6dKGRX"
TRACE = RUN / "agent/trajectory.json"
ANSWER = RUN / "artifacts/app/answer/corrected_mask.nii.gz"
steps = {s["step_id"]: s for s in json.loads(TRACE.read_text())["steps"]}


def compressed(array):
    return base64.b64encode(gzip.compress(array.tobytes(), mtime=0)).decode()


def pin(path):
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def observations(sid):
    result = []
    for item in steps[sid].get("observation", {}).get("results", []):
        result.extend(ast.literal_eval(item["content"]))
    return result


def png(array):
    buf = io.BytesIO()
    Image.fromarray(array).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


image_nii = nib.load(TASK / "environment/data/image.nii.gz")
image = image_nii.get_fdata()
affine = image_nii.affine
spacing = np.linalg.norm(affine[:3, :3], axis=0)
mask = nib.load(TASK / "environment/data/proposed_mask.nii.gz").get_fdata() > 0
editable = nib.load(TASK / "environment/data/editable_region.nii.gz").get_fdata() > 0
saved_nii = nib.load(ANSWER)
saved = saved_nii.get_fdata() > 0
with np.load(TASK / "tests/truth.npz") as z:
    truth = {k: z[k] for k in z.files}
gt = truth["gt"]
added = saved & ~mask
gap = gt & ~mask
assert added.sum() == 198 and gap.sum() == 200
assert not (added & ~gap).any() and not (mask & ~saved).any()
assert np.array_equal(saved_nii.affine, affine)
assert not ((saved != mask) & ~editable).any()

# Import only the reviewed, data-only scorer. Its main entry point is guarded.
spec = importlib.util.spec_from_file_location("retained_br026_scorer", TASK / "tests/score.py")
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)
replayed = scorer.score_array(saved.astype(np.uint8), affine, truth)
frozen = json.loads((RUN / "verifier/metrics.json").read_text())
assert replayed == frozen
initial_score = scorer.score_array(mask.astype(np.uint8), affine, truth)

conn = np.ones((3, 3, 3), dtype=bool)
seed = (66, 76, 15)
states = []
expected = {150: 247, 160: 212, 165: 198, 170: 186, 180: 178, 190: 170, 200: 155, 220: 122, 250: 89}
for threshold, count in expected.items():
    labels, _ = label((image >= threshold) & ~mask & editable, conn)
    candidate = labels == labels[seed]
    assert labels[seed] != 0 and int(candidate.sum()) == count
    contacts, contact_count = label(candidate & binary_dilation(mask, conn), conn)
    states.append(
        {
            "threshold": threshold,
            "count": count,
            "indices": np.flatnonzero(candidate).tolist(),
            "contacts": [
                np.flatnonzero(contacts == k).tolist() for k in range(1, contact_count + 1)
            ],
        }
    )
assert np.array_equal(np.flatnonzero(added), np.asarray(states[2]["indices"]))
assert [len(x) for x in states[2]["contacts"]] == [32, 33]


# Exact exposed voxel faces, in native index coordinates. The viewer applies the
# full NIfTI affine; no smoothing, decimation or inferred vessel centreline.
def surface(binary):
    faces = []
    for axis in range(3):
        others = [a for a in range(3) if a != axis]
        for sign in [-1, 1]:
            neighbor = np.roll(binary, -sign, axis=axis)
            sl = [slice(None)] * 3
            sl[axis] = -1 if sign == 1 else 0
            neighbor[tuple(sl)] = False
            centres = np.argwhere(binary & ~neighbor).astype(np.float32)
            vertices = []
            for a, b in [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]:
                v = centres.copy()
                v[:, axis] += sign * 0.5
                v[:, others[0]] += a
                v[:, others[1]] += b
                vertices.append(v)
            q = np.stack(vertices, axis=1)
            faces.append(q[:, [0, 1, 2, 0, 2, 3]].reshape(-1, 3))
    return np.concatenate(faces).astype("<f4")


gray = np.rint(np.clip((image - 70) / 580, 0, 1) * 255).astype(np.uint8)
roi = [[49, 59, 7], [83, 94, 25]]
trace = []
for sid in [7, 9, 12, 14, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31]:
    trace.append(
        {
            "step": sid,
            "time": steps[sid].get("timestamp", ""),
            "call": "\n".join(c["arguments"]["input"] for c in steps[sid].get("tool_calls", [])),
            "output": "\n".join(
                x.get("text", "") for x in observations(sid) if x.get("type") == "input_text"
            ),
        }
    )
delivered = []
for sid in [10, 11, 13, 15, 19, 22, 24, 27]:
    for n, item in enumerate(observations(sid)):
        if item.get("type") == "input_image":
            dest = OUT / f"delivered-{sid}-{n}.png"
            dest.write_bytes(base64.b64decode(item["image_url"].split(",", 1)[1]))
            delivered.append({"step": sid, "file": dest.name})

surface_data = surface(mask)
data = {
    "shape": list(image.shape),
    "affine": affine.tolist(),
    "spacing": spacing.tolist(),
    "seed": list(seed),
    "roi": roi,
    "volume": compressed(gray),
    "mask": compressed(mask.astype(np.uint8)),
    "editable": compressed(editable.astype(np.uint8)),
    "surface": compressed(surface_data),
    "surface_vertices": len(surface_data),
    "states": states,
    "added": np.flatnonzero(added).tolist(),
    "residual": np.flatnonzero(gt & ~saved).tolist(),
    "frozen": frozen,
    "initial": initial_score,
    "source_voxels": int(mask.sum()),
    "global_components": int(label(mask, conn)[1]),
    "trace": trace,
    "delivered": delivered,
    "mip": png(gray.max(axis=2).T[::-1].copy()),
}
(OUT / "data.json").write_text(json.dumps(data, separators=(",", ":")))
sources = [
    TRACE,
    ANSWER,
    TASK / "tests/truth.npz",
    TASK / "tests/score.py",
    RUN / "verifier/metrics.json",
    TASK / "instruction.md",
    TASK / "environment/SOURCE_NOTICE.md",
    TASK / "environment/DATA-LICENSE.txt",
]
sources.extend(
    TASK / "environment/data" / name
    for name in ["image.nii.gz", "proposed_mask.nii.gz", "editable_region.nii.gz"]
)
receipt = {
    "recipe": pin(Path(__file__)),
    "sources": [pin(p) for p in sources],
    "attempt": "vessel-v01__c6dKGRX",
    "source": "TopCoW 2024 MRA case 007",
    "derived": {
        "volume": "Native grid, display-only uint8 mapping 70..650 source intensity; no spatial resampling.",
        "surface": "Exposed voxel faces of proposed mask; corners at index +/-0.5, full NIfTI RAS affine.",
        "thresholds": "Nine step-28 seed components reconstructed from public inputs with 26-connectivity; every logged count reproduced.",
        "contacts": "Step-29 candidate voxels adjacent to original mask, split into 26-connected patches. 165 yields 32 and 33 voxels.",
        "local_views": "Reader-selected crop [49:83,59:94,7:25] around logged seed; not the agent's original screen.",
        "reference": "200 deleted reference voxels / 2 residual voxels revealed only in final phase; evaluator-only teaching overlay.",
    },
    "verification": {
        "frozen_score_reproduced_exactly": True,
        "saved_output_equals_165_component_union": True,
        "added": 198,
        "gap": 200,
        "deleted": 0,
        "unrelated_additions": 0,
        "threshold_counts": expected,
        "contact_sizes": [32, 33],
    },
    "delivered_images": delivered,
    "limits": [
        "Synthetic deletion in real MRA; not a natural segmentation-model error.",
        "One calibration attempt, not clinical validation or general success rate.",
        "Threshold states are deterministic reconstructions, not new agent attempts.",
        "Whole solver-visible MRA crop, not the entire original scan.",
    ],
}
(OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
for source, name in [
    (TASK / "instruction.md", "instruction.txt"),
    (TASK / "tests/score.py", "scorer.txt"),
    (TASK / "environment/DATA-LICENSE.txt", "DATA-LICENSE.txt"),
    (TASK / "environment/SOURCE_NOTICE.md", "SOURCE_NOTICE.txt"),
]:
    shutil.copyfile(source, OUT / name)
print(
    json.dumps(
        {
            "shape": image.shape,
            "surface_vertices": len(surface_data),
            "data_bytes": (OUT / "data.json").stat().st_size,
            "frozen_replay": "exact",
            "thresholds": expected,
        }
    )
)
