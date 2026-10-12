"""Extract retained BR-039 observations and derive a bounded reader-only preview.

No historical preparation module, solver, scorer, or supplied helper is executed.
The output directory must not exist. The tracked manifest is updated only when
explicitly requested with --manifest, after all source and derivative checks pass.
"""

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

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
TASK = ROOT / "runs/br039-ct-landmarks/tasks/ct-partial"
RUN = ROOT / "runs/br039-ct-partial-terra-high-v1-20260917/ct-partial__DeU639y"
ATTEMPT = "attempt-824eaf2afb12f840a722b998"
TERMS = ROOT / "groups/anatomical-landmarks/presentation/sources/named-landmark-source-terms.json"
LICENSE = ROOT / "presentation/task-explorer/named-landmarks/VERSE-CC-BY-SA.txt"
IMAGE_HASHES = {
    11: "e3e1b8a262d565d0a942cedc904dce9434ac6219771c7aca65f97fcdf31b617e",
    15: "9c6100c1cc8531e4fab1bdd105924bfd26c6ce4caaa300582c84f26dc08c4062",
    17: "c5de0b2aea26a27fb283d89a379a44e6d6f7ee49f4a9b572dc20af676706c2a5",
    20: "8ee89b99a0c85bce139179c700097544ac9dc90326a617dab162e664e3f85646",
    22: "ddcec1f064436d3ba688b476015d9b099939e1cb03170b4374d318cadae27fa8",
    24: "750f198d5fdf1cafca909fd7ab9f536aeec71cd9ca34a356efecad2ce0d11487",
    27: "e522c56394cae209285122d28810bdcc16c1b743b09c68c697ce60360089d6e1",
    29: "0dcffc9fe6a0513d5f1ab40205e6392661b97eb5e4551653d6053ed0203db289",
    30: "a9b68f40a41c6929ca9e741c01b5dc47222a356031cdd2a0a594586d4f078493",
    33: "04469bf244fc90be00dc19ba2e3a8b079ec20bb32b2bd0335ee02ca7c3f4ae67",
}
PINNED = {
    "environment/volume.npy": "9d800b5afb3dda6d2b6b4d7ebafd5f91bacb0fcc9b351982232df362df55c1d5",
    "environment/volume.nii.gz": "d0820fce2984ab65448fed1fea8b41b88b739468fe46677ee9147f05de680439",
    "environment/geometry.json": "8aa4dfd5e420440b2c74f34672bdf7e72b27a6d21cf169c5d25488fc6780b62c",
    "environment/volume_tools.py": "9e45612aae89c572509492807b4323ee8027201c69b3a3336faff4ff18a0f058",
    "environment/landmarks.json": "c01dd5b1366b3b6d5c16b997c4549ccf8a8610c60da357ab0d3fd4301404167a",
    "instruction.md": "48d4dfa2accae7922cbc54a9f7d9b5dc9d266bb1028cd5fb98544197d267d830",
    "tests/truth.json": "3de07e775860f7cbf10f11a66666cda62dfc0b5e26f4186f402f651f22de585e",
    "tests/score.py": "10dd7d5417180e95d8f98f677904a0136a772dbee5f14d4b34e9d2fc3c1b9ef4",
    "environment/SOURCE_NOTICE.md": "91188f8f2a43b8bf02b5e02914c44d7b47d8afdb17e8d5e1b0a9a1769ed4ddd1",
}
RUN_PINNED = {
    "agent/trajectory.json": "d2c5338c2eac8ffa249a193aac09ba6a4aaa0bc5224340190f6cf9bd9b6837d4",
    "artifacts/app/answer/landmarks.json": "3e7ab43535874c35152d1830af7b55dedb73ebfc52d7726de5331f3a5636cdfe",
    "artifacts/app/answer/evidence.md": "fa8bc02a6b5f35df4c6db6c978d6103883076be9e372b1bb09d0911398aab991",
    "verifier/details.json": "2fbb5abae1bf6add106a90ec030d74e4cdc7c8302b774d644f4e3651d7a62a47",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def asset(path: Path, role: str, step: int | None = None) -> dict:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
        "bytes": path.stat().st_size,
        "role": role,
        "step": step,
    }


def content(step: dict) -> list[dict]:
    items = []
    for result in step.get("observation", {}).get("results", []):
        items.extend(ast.literal_eval(result["content"]))
    return items


def observed_text(step: dict) -> str:
    return "\n".join(
        item.get("text", "") for item in content(step) if item.get("type") == "input_text"
    )


def points(values: dict) -> list[dict]:
    return [
        {"name": name, "status": value["status"], "ijk": value["ijk"]}
        for name, value in values.items()
    ]


def state(
    name: str,
    step: int,
    label: str,
    kind: str,
    bounds=None,
    axis=None,
    levels=None,
    values=None,
    delivered=None,
    description="",
    centre=None,
    radius=None,
) -> dict:
    return {
        "id": name,
        "trace_step": step,
        "label": label,
        "kind": kind,
        "bounds": bounds,
        "axis": axis,
        "levels": levels or [],
        "center_ijk": centre,
        "radius_mm": radius,
        "points": values or [],
        "delivered_step": delivered,
        "description": description,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        parser.error(f"refusing to overwrite existing output: {out}")
    if not out.is_relative_to(ROOT / ".local/anatomy-pose/landmarks"):
        parser.error("output must be a fresh directory under .local/anatomy-pose/landmarks")
    sources = []
    for base, pins in [(TASK, PINNED), (RUN, RUN_PINNED)]:
        for relative, expected in pins.items():
            path = base / relative
            if digest(path) != expected:
                raise ValueError(f"source hash mismatch: {path}")
            role = (
                "private-reference"
                if relative.startswith(("tests/", "verifier/"))
                else "task-input"
            )
            if relative.startswith("agent/"):
                role = "trace"
            if relative.startswith("artifacts/"):
                role = "saved-output"
            sources.append(asset(path, role))
    for path in [
        TERMS,
        LICENSE,
        HERE / "canonical-mapping.md",
        HERE / "prepare_trace.py",
        ROOT / "docs/evidence/br039-curation.json",
        ROOT / "groups/anatomical-landmarks/experiments/br039/attempts" / f"{ATTEMPT}.json",
    ]:
        sources.append(asset(path, "license" if path in [TERMS, LICENSE] else "provenance"))
    geometry = json.loads((TASK / "environment/geometry.json").read_text())
    trajectory = json.loads((RUN / "agent/trajectory.json").read_text())
    steps = {item["step_id"]: item for item in trajectory["steps"]}
    answer = json.loads((RUN / "artifacts/app/answer/landmarks.json").read_text())
    saved = points(answer["landmarks"])
    reference = json.loads((TASK / "tests/truth.json").read_text())
    frozen = json.loads((RUN / "verifier/details.json").read_text())
    affine = np.asarray(geometry["voxel_to_ras_mm"])
    shape = geometry["shape_ijk"]
    spacing = geometry["spacing_ijk_mm"]
    volume = np.load(TASK / "environment/volume.npy", mmap_mode="r")
    if list(volume.shape) != shape or shape != [512, 512, 920]:
        raise ValueError("native shape mismatch")
    if not np.allclose(np.linalg.norm(affine[:3, :3], axis=0), spacing):
        raise ValueError("affine spacing mismatch")
    for example in geometry["nonanatomical_coordinate_examples"]:
        world = affine @ np.array([*example["ijk"], 1])
        assert np.allclose(world[:3], example["ras_mm"])
    indices = [
        np.rint(np.linspace(0, size - 1, count)).astype(int)
        for size, count in zip(shape, [128, 128, 230], strict=True)
    ]
    for axis, values in enumerate(indices):
        assert values[0] == 0 and values[-1] == shape[axis] - 1
        assert np.all(np.diff(values) > 0)
    sampled = volume[np.ix_(*indices)].astype(np.float32)
    window = geometry["display_window"]
    preview = np.rint(np.clip((sampled - window[0]) / (window[1] - window[0]), 0, 1) * 255).astype(
        np.uint8
    )
    packed = gzip.compress(preview.tobytes(order="C"), mtime=0)
    assert len(gzip.decompress(packed)) == 128 * 128 * 230
    out.mkdir(parents=True)
    derivatives = []
    delivered = []
    for sid, expected in IMAGE_HASHES.items():
        item = ast.literal_eval(steps[sid]["observation"]["results"][0]["content"])[1]
        assert item["type"] == "input_image"
        raw = base64.b64decode(item["image_url"].split(",", 1)[1], validate=True)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"delivered image hash mismatch: step {sid}")
        path = out / f"delivered-step-{sid}-1.png"
        path.write_bytes(raw)
        with Image.open(path) as image:
            image.verify()
        derivatives.append(asset(path, "delivered-image", sid))
        delivered.append({"step": sid, "path": path.name})
    # Reader input poster: coronal MIP of the supplied crop preview, no solver marks.
    image = Image.fromarray(np.flipud(preview.max(axis=1).T))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    poster = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    states = [
        state(
            "crop",
            7,
            "Supplied crop",
            "region",
            [[0, 0, 0], shape],
            description="Entire supplied native crop; no target locations disclosed.",
        )
    ]
    for sid, centre, radius, name in [
        (11, [256, 220, 460], 0, "overview"),
        (15, [256, 85, 650], 180, "spine-mid"),
        (17, [256, 135, 650], 180, "spine-body"),
        (29, [248, 220, 450], 45, "l5-check"),
        (30, [262, 155, 910], 35, "t4-check"),
    ]:
        bounds = (
            [
                [max(0, p - radius / s + 0.5) for p, s in zip(centre, spacing, strict=True)],
                [
                    min(n, p + radius / s + 0.5)
                    for p, s, n in zip(centre, spacing, shape, strict=True)
                ],
            ]
            if radius
            else [[0, 0, 0], shape]
        )
        states.append(
            state(
                name,
                sid,
                f"Requested view {centre}",
                "region",
                bounds,
                delivered=sid,
                centre=centre,
                radius=radius,
                description=f"Logged orthogonal inspection centre {centre}; radius {radius} mm (0 means whole planes). Bounds are half-open array-cell endpoints: exact helper centre-coordinate limits plus 0.5; physical edges use affine(bounds-0.5). No segmentation is implied. Cyan crosshairs are requested locations, not detections.",
            )
        )
    for ii in [246, 256, 266]:
        states.append(
            state(
                f"sagittal-{ii}",
                20,
                f"Native sagittal i={ii}",
                "plane",
                [[ii, 0, 380], [ii + 1, 260, 920]],
                axis=0,
                levels=[ii],
                delivered=20,
                description="Actual native slice in delivered three-panel montage; window [-200,1600] HU.",
            )
        )
    states.extend(
        [
            state(
                "coronal-mip",
                22,
                "Coronal bone projection",
                "slab",
                [[0, 70, 380], [512, 180, 920]],
                axis=1,
                delivered=22,
                description="Logged maximum intensity projection through j=70:180; window [100,1600] HU.",
            ),
            state(
                "sagittal-mip",
                24,
                "Sagittal bone projection",
                "slab",
                [[242, 0, 380], [270, 230, 920]],
                axis=0,
                delivered=24,
                description="Logged maximum intensity projection through i=242:270; window [100,1600] HU.",
            ),
            state(
                "candidate-levels",
                27,
                "Fourteen candidate axial levels",
                "levels",
                [[180, 65, 451], [335, 225, 911]],
                axis=2,
                levels=[910, 875, 840, 805, 772, 740, 707, 673, 639, 603, 565, 526, 487, 451],
                delivered=27,
                description="Exact logged candidate k list; enclosing bounds contain unsampled gaps. These are solver-selected levels, not reference labels.",
            ),
            state(
                "lower-levels",
                33,
                "Lower axial cross-check",
                "levels",
                [[180, 120, 415], [335, 290, 640]],
                axis=2,
                levels=[639, 603, 565, 526, 487, 450, 415],
                delivered=33,
                description="Exact logged lower k list, window [-200,1400] HU; enclosing bounds contain unsampled gaps.",
            ),
        ]
    )
    axial = []
    for name, k, i, j in re.findall(
        r"^(\w+) (\d+) ([\d.]+) ([\d.]+)$", observed_text(steps[35]), re.M
    ):
        axial.append({"name": name, "status": "observed", "ijk": [float(i), float(j), int(k)]})
    centres = []
    for name, i, j, k in re.findall(
        r"^(\w+) \(np.float64\(([\d.]+)\), np.float64\(([\d.]+)\), np.float64\(([\d.]+)\)\)$",
        observed_text(steps[37]),
        re.M,
    ):
        centres.append({"name": name, "status": "observed", "ijk": [float(i), float(j), float(k)]})
    assert len(axial) == len(centres) == 14
    assert centres == [point for point in saved if point["status"] == "observed"]
    states.extend(
        [
            state(
                "axial-centres",
                35,
                "Logged axial weighted centres",
                "points",
                values=axial,
                description="Printed 2D weighted centres at solver-selected k levels; >100 HU, weights clip(HU,100,600)-100; tight solver-authored body ROIs, rounded to 0.1 voxel. Names are solver claims.",
            ),
            state(
                "body-centres",
                37,
                "Logged 3D body centres",
                "points",
                values=centres,
                description="Printed 3D intensity-weighted centres in solver-authored ROIs; rounded to 0.1 voxel. No GT segmentation or corrected numbering.",
            ),
            state(
                "saved",
                40,
                "Saved landmarks and statuses",
                "saved",
                values=saved,
                description="Exact retained answer positions/statuses written at step 40; step 41 checks contract/coordinates only.",
            ),
        ]
    )
    # Retain actual ROI bounds for each logged 3D centre, without executing its calculation.
    patch_call = steps[34]["tool_calls"][0]["arguments"]["input"]
    patch = json.loads(re.search(r"const patch = (\".*?\");", patch_call, re.S)[1])
    code = "\n".join(
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    rows = ast.literal_eval(re.search(r"rows = (\[.*?\])", code, re.S)[1])
    ranges = [
        (895, 920),
        (858, 893),
        (823, 857),
        (789, 823),
        (755, 789),
        (723, 755),
        (690, 723),
        (656, 690),
        (622, 656),
        (583, 622),
        (544, 583),
        (506, 544),
        (468, 506),
        (430, 468),
    ]
    for row, zrange, point in zip(rows, ranges, centres, strict=True):
        name, _, i0, i1, j0, j1 = row
        states.append(
            state(
                f"roi-{name.lower()}",
                37,
                f"{name} weighted-centre ROI",
                "points",
                [[i0, j0, zrange[0]], [i1, j1, zrange[1]]],
                values=[point],
                description="Actual logged 3D threshold/weighting ROI (step 36 authoring, step 37 observation); point and name are the solver's cross-check.",
            )
        )
    selected = [
        7,
        9,
        10,
        11,
        12,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
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
        37,
        39,
        40,
        41,
    ]
    actions = [
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
        datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
        for item in trajectory["steps"]
    ]
    separation = float(
        np.linalg.norm(
            affine[:3, :3]
            @ (np.asarray(answer["landmarks"]["T4"]["ijk"]) - reference["targets"]["T5"]["ijk"])
        )
    )
    data = {
        "attempt": ATTEMPT,
        "shape": shape,
        "affine": affine.tolist(),
        "spacing": spacing,
        "preview_shape": list(preview.shape),
        "preview_indices": [item.tolist() for item in indices],
        "preview_window_hu": window,
        "volume": base64.b64encode(packed).decode(),
        "names": [
            {"name": name, "definition": definition}
            for name, definition in json.loads(
                (TASK / "environment/landmarks.json").read_text()
            ).items()
        ],
        "poster": poster,
        "states": states,
        "points": saved,
        "trace": actions,
        "elapsed_seconds": (times[-1] - times[0]).total_seconds(),
        "steps_in_trace": len(trajectory["steps"]),
        "evidence": (RUN / "artifacts/app/answer/evidence.md").read_text(),
        "reference_points": points(reference["targets"]),
        "frozen": frozen,
        "wrong_level": {
            "claimed_name": "T4",
            "matched_name": "T5",
            "claimed_ijk": answer["landmarks"]["T4"]["ijk"],
            "matched_ijk": reference["targets"]["T5"]["ijk"],
            "separation_mm": separation,
            "outside_name": "T4",
            "outside_ijk": reference["targets"]["T4"]["ijk"],
        },
        "delivered_images": delivered,
    }
    (out / "data.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    derivatives.insert(0, asset(out / "data.json", "derived-display"))
    for source, name in [
        (TASK / "environment/SOURCE_NOTICE.md", "SOURCE_NOTICE.txt"),
        (LICENSE, "VERSE-CC-BY-SA.txt"),
        (TERMS, "source-terms.json"),
        (TASK / "instruction.md", "instruction.txt"),
    ]:
        (out / name).write_bytes(source.read_bytes())
        derivatives.append(
            asset(out / name, "license" if name != "instruction.txt" else "task-input")
        )
    (out / "DERIVATIVES.txt").write_text(
        "VerSe sub-verse823; Sekuboyina et al. 2021 and Liebl et al. 2021. Dataset: https://github.com/anjany/verse\nImage-derived materials: CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ . Source repository code license MIT is separate.\nDerivatives: original native k=0:920 crop; nearest native integer sampling to 128x128x230, window [-200,1400] HU, uint8, C-order, deterministic gzip; coronal MIP input poster from preview, i increases horizontally toward L and k upward toward S, no solver/reference marks. All ten delivered PNGs extracted byte-for-byte. No original full CT intensities or reference-centred panels bundled.\n"
    )
    derivatives.append(asset(out / "DERIVATIVES.txt", "license"))
    receipt = {
        "schema": 1,
        "attempt": ATTEMPT,
        "sources": sources,
        "derivatives": derivatives,
        "preview": {
            "shape": list(preview.shape),
            "indices": [item.tolist() for item in indices],
            "sampling": "Nearest native integer sample; indices are authoritative; C-order uint8 gzip with mtime=0.",
            "window_hu": window,
            "sha256_uint8": hashlib.sha256(preview.tobytes()).hexdigest(),
        },
        "verification": {
            "all_source_pins_match": True,
            "delivered_images_exact": 10,
            "affine_examples_match": True,
            "preview_endpoints": [[int(item[0]), int(item[-1])] for item in indices],
            "logged_3d_centres_match_saved": True,
            "wrong_level_separation_mm": separation,
        },
        "limits": [
            "No solver/scorer/old recipe executed.",
            "Bounded preview is for context, not native-resolution localization.",
            "Selected tool calls and observations only; no private reasoning or continuous video.",
            "Frozen result preserved; no new evaluation or clinical adjudication.",
            "Step 9 missing-image error and step 31 syntax error remain in selected observations.",
            "Original intermediate work PNGs/script are not retained; exact embedded delivered PNGs are retained.",
            "Visual acceptance and canonical binding remain pending.",
            "verifier/metrics.json is absent; frozen source is verifier/details.json.",
        ],
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    derivatives.append(asset(out / "receipt.json", "provenance"))
    manifest = {
        "schema": 1,
        "id": "br039-native-trace",
        "entry_id": "tb3-named-landmarks",
        "attempt": ATTEMPT,
        "adapter": "ct-landmarks",
        "coordinates": "RAS-mm",
        "saved_state": "saved",
        "notice": "One retained BR-039 Terra/high partial CT attempt on VerSe sub-verse823. Supplied native crop only; logged operations and frozen engineering references do not establish clinical precision or population performance.",
        "recovery": "Recover pinned retained bytes, then run groups/anatomical-landmarks/presentation/native-landmark-trace/prepare_trace.py into a fresh directory. See its README; no new trial or historical preparation is implied.",
        "assets": derivatives + sources,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if args.manifest:
        if args.manifest.resolve() != HERE / "native-trace.json":
            parser.error("--manifest may only select this recipe's owned native-trace.json")
        args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(out),
                "data_bytes": (out / "data.json").stat().st_size,
                "delivered_images": len(delivered),
                "delivered_bytes": sum(
                    item["bytes"] for item in derivatives if item["role"] == "delivered-image"
                ),
                "states": len(states),
                "selected_calls": len(actions),
                "preview_shape": list(preview.shape),
                "wrong_level_separation_mm": separation,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
