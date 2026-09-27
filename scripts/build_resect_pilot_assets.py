"""Build compact, calibrated views of a retained cue-present RESECT pilot.

Import-safe. Reads pinned inputs and trace images; never runs an optimizer,
model, historical preparation module or verifier. Needs existing imaging extras.
"""

import argparse
import ast
import json
import math
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from build_resect_assets import MANIFEST, MANIFEST_SHA, png, section
from build_respiratory_assets import dump, read, sha
from PIL import Image

AUDIT = "groups/registration/findings/evidence/resect-point-prompt-cue-audit.json"
AUDIT_SHA = "fe135ac559f29feef251e9fc43fb5809a3cc5f5192cfec931b21bf70780c247e"
FREEZE = "groups/registration/experiments/resect-point-audit-astra-medium/freezes/freeze-8440876faee54bf2546c10bb.json"
TRIAL = ".local/attempts/attempt-fa7a4c4250aa4cca/job/task__N85tFCt"


def build(root, output):
    output.mkdir(parents=True, exist_ok=False)
    sources = {}

    def pin(rel, expected=None):
        path = root / rel
        value = sha(path)
        if expected is not None and value != expected:
            raise ValueError(f"Source hash mismatch: {rel}")
        sources[rel] = value
        return path

    audit = read(pin(AUDIT, AUDIT_SHA))
    for rel, expected in audit["sources"].items():
        pin(rel, expected)
    manifest = read(pin(MANIFEST, MANIFEST_SHA))
    freeze = read(pin(FREEZE))
    task = freeze["snapshot_path"]
    queries = read(root / task / "environment/data/queries.json")["cases"]
    truth = read(root / task / "tests/reference.json")["cases"]
    answers = read(root / TRIAL / "artifacts/app/answer/result.json")
    public, references = [], []
    for i, query in enumerate(queries):
        case_id = query["case_id"]
        source = manifest["cases"][[0, 2][i]]
        folder = ".local/datasets/resect-sample/e86fb37/" + source["case_id"]
        tag = next(s for s in source["source_files"] if s["name"].endswith(".tag"))
        rows = []
        for line in pin(folder + "/" + tag["name"], tag["sha256"]).read_text().splitlines():
            try:
                values = [float(x) for x in line.split()[:6]]
            except ValueError:
                continue
            if len(values) == 6:
                rows.append(values)
        selected = rows[[1, 12][i]]
        if (
            selected[:3] != query["mri_world_mm"]
            or selected[3:] != truth[i]["reference_us_world_mm"]
        ):
            raise ValueError("Frozen query or target differs from published tag")
        center = np.array(query["mri_world_mm"])
        item = {**query, "source_case": source["case_id"], "modalities": {}}
        for key, suffix, frozen in [("mri", "FLAIR", "flair"), ("us", "US-before", "us")]:
            source_file = next(
                s
                for s in source["source_files"]
                if s["name"] == f"{source['case_id']}-{suffix}.nii.gz"
            )
            raw = pin(folder + "/" + source_file["name"], source_file["sha256"])
            staged = root / task / f"environment/data/{case_id}_{frozen}.nii.gz"
            if sha(raw) != sha(staged):
                raise ValueError("Staged image differs from pinned sample")
            image = nib.load(staged)
            if nib.aff2axcodes(image.affine) is None or int(image.header["sform_code"]) != 1:
                raise ValueError("Unexpected NIfTI geometry")
            data = image.get_fdata(dtype=np.float32)
            window = np.percentile(data[data > 0], [1, 99]).tolist()
            item["modalities"][key] = {
                "shape": list(image.shape),
                "affine": image.affine.tolist(),
                "window": window,
                "native": section(data, image.affine, center, (0, 1), window, native=True),
                "ras": [
                    section(data, image.affine, center, axes, window)
                    for axes in [(0, 1), (0, 2), (1, 2)]
                ]
                if key == "us"
                else [],
            }
        metrics = audit["retained_scores"][i]
        returned = answers["cases"][i]["us_world_mm"]
        if abs(math.dist(returned, selected[3:]) - metrics["final_error_mm"]) > 1e-12:
            raise ValueError("Independent distance mismatch")
        public.append(item)
        references.append({**metrics, "selected_index_zero_based": [1, 12][i]})

    def crop(name, box):
        rel = TRIAL + "/artifacts/app/answer/views/" + name
        path = pin(rel)
        if not any(
            d["view"] == name and d["sha256"] == sha(path) for d in audit["delivered_saved_views"]
        ):
            raise ValueError("Image not proven delivered in trace")
        with Image.open(path) as image:
            pixels = image.crop(box).resize((161, 161), Image.Resampling.LANCZOS)
            return {"png": png(np.array(pixels)), "source": rel, "crop_xyxy": list(box)}

    # The original agent panels are independently centred and +R right / +A up.
    cue_views = [crop("b_candidate.png", (820, y, 1221, y + 401)) for y in [35, 480]]
    slabs = [
        [crop("b_slabs.png", (col * 208, y, col * 208 + 201, y + 201)) for y in [945, 1175]]
        for col in range(5)
    ]
    trajectory = read(root / TRIAL / "agent/trajectory.json")
    step = next(s for s in trajectory["steps"] if s["step_id"] == 21)
    chunks = ast.literal_eval(step["observation"]["results"][0]["content"])
    stdout = json.loads(chunks[1]["text"])["output"]
    peaks = []
    for i, line in enumerate(stdout.splitlines()):
        _, radius, literal = line.split(" ", 2)
        point, score = ast.literal_eval(literal)[0]
        peaks.append(
            {
                "case_id": "case_b" if i < 3 else "case_a",
                "radius_mm": float(radius),
                "top_world_mm_rounded": point,
                "score_rounded": score,
            }
        )
    if len(peaks) != 6:
        raise ValueError("Unexpected retained correlation output")
    dump(output / "geometry.json", {"frame": "RAS", "units": "mm", "cases": public})
    dump(
        output / "trace.json",
        {
            "cue_world_mm": audit["prompt_cue"]["world_mm"],
            "cue_views": cue_views,
            "slabs": slabs,
            "slab_offsets_mm": [-2, -1, 0, 1, 2],
            "peaks": peaks,
        },
    )
    dump(output / "output.json", answers)
    dump(
        output / "reference.json",
        {
            "cases": references,
            "cue_error_mm": audit["prompt_cue"]["distance_to_reference_mm"],
            "diagnostics": audit["diagnostic_counterexamples"],
        },
    )
    shutil.copyfile(
        root / "presentation/task-explorer/resect/DATA-LICENSE.txt", output / "DATA-LICENSE.txt"
    )
    (output / "NOTICE.md").write_text("""# Retained RESECT pilot teaching views

Images/landmarks: Xiao et al., RESECT (2017), https://doi.org/10.1002/mp.12268,
CC BY 4.0 (DATA-LICENSE.txt). Archive: https://doi.org/10.11582/2017.00004
(the article also cites 10.11582/2016.00003). Sample: MedOtter/RESECT-SEG
revision e86fb37dd93f7a9c64e48952f71410af59b04b9b,
https://huggingface.co/datasets/MedOtter/RESECT-SEG/tree/e86fb37dd93f7a9c64e48952f71410af59b04b9b.
No tumor-mask imagery is distributed in this pack. Selection used mask centroids
and published tags before inference; these are two selected public training points.

geometry.json: new complete native XY previews through each supplied MRI query;
US RAS sections share that same fixed initial centre, 48 mm field, 0.5 mm pixels,
positive-intensity 1st/99th windows, linear interpolation and transparent outside
source support. Pixel origins/directions are NIfTI RAS+ mm. No registration run.

trace.json: actual delivered agent PNG panels, cropped with retained pixel boxes
and reduced to 161 square pixels using Lanczos. The agent independently centred
MRI on the query and US on the candidate, using positive-intensity 1st/99.5th
windows and +R right / +A up in axial views. The prompt-candidate panels span
30 mm. Five adjacent final-candidate slabs span 20 mm, at z offsets -2..+2 mm;
the animation changes displayed section only, not anatomy or candidate coordinates.
Original gold centre crosses are retained. Crosses on noncentral slabs indicate
the projected centre, not a point on that slice. All displayed originals match
trace-delivered image hashes. Correlation peaks are rounded retained step-21
stdout, not a new search, probability or reference agreement.

output.json is the actual retained world-coordinate answer. reference.json is
reader-only target/error data and labeled post-hoc verifier diagnostics. References
remain embedded in the portable HTML: reveal is a presentation boundary, not a
security guarantee. Frozen prompt supplies B [-30,15,15], 0.505444 mm from the
reference, versus returned error 1.130199 mm. Original scores remain unchanged;
unaided recovery, cue causal necessity, generalization and clinical claims are
unsupported. Original nop missed result.json; artifact reward is not physical
success. No new medical/model trial or optimizer is executed by this builder.
""")
    assets = [
        {
            "file": p.name,
            "sha256": sha(p),
            "bytes": p.stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
        }
        for p in sorted(output.iterdir())
    ]
    if any(a["bytes"] > 1024 * 1024 for a in assets):
        raise ValueError("Asset exceeds retention limit")
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-resect-pilot-v1",
            "frame": "RAS",
            "units": "mm",
            "license": "CC-BY-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": {
                "frozen_copies": 32,
                "delivered_view_hashes": 12,
                "independent_point_errors": 2,
            },
            "assets": assets,
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "sources": len(sources),
                "asset_bytes": {a["file"]: a["bytes"] for a in assets},
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.output)
