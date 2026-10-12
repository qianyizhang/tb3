"""Recover BR-037 P03 neutral evidence and bounded native MRI previews.

Read retained bytes only. Never execute the solver's method, historical preparation,
supplied viewer or scorer. All generated data stay in a fresh ignored directory.
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

import nibabel as nib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
TASK = ROOT / "runs/br037-longitudinal-reading/tasks/p03-neutral"
RUN = ROOT / "runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF"
ATTEMPT = "attempt-6c8ee6d062c12e5b435afa42"
AUDIT = HERE.parent / "sources/longitudinal-mri-audit.json"
FREEZE = ROOT / "runs/br037-longitudinal-reading/p03-neutral-freeze.json"
LICENSE = ROOT / "presentation/task-explorer/longitudinal-mri/DATA-LICENSE.txt"
IMAGE_HASHES = {
    15: "bd0dde1637698d1f164473fd2b4d581c98983a76af22da9761017e9a3431a40a",
    18: "ace35d019a226a1eb147a10b2f7df9e07b4753af947aa60fd757d5ff75407187",
    22: "43762cfa527ab8b8fae3331588662a05abdab6bafc44603c1969cf5589b8cc55",
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


def content(step: dict) -> list[dict]:
    values = []
    for result in step.get("observation", {}).get("results", []):
        values.extend(ast.literal_eval(result["content"]))
    return values


def text(step: dict) -> str:
    return "\n".join(
        value.get("text", "") for value in content(step) if value.get("type") == "input_text"
    )


def view(visit: str, series: str, *, axis=None, levels=None, bounds=None, center=None) -> dict:
    return {
        "visit": visit,
        "series_id": series,
        "axis": axis,
        "levels": levels or [],
        "bounds": bounds,
        "center_ijk": center,
    }


def state(
    name: str, step: int, label: str, kind: str, views: list, description: str, delivered=None
) -> dict:
    return {
        "id": name,
        "trace_step": step,
        "label": label,
        "kind": kind,
        "views": views,
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
    if not out.is_relative_to(ROOT / ".local/anatomy-pose/mri"):
        parser.error("output must be fresh and under .local/anatomy-pose/mri")
    if args.manifest and args.manifest.resolve() != HERE / "native-trace.json":
        parser.error("--manifest may only select this recipe's native-trace.json")

    # The committed mapping pins the audit/freeze themselves before their maps are trusted.
    mapping = (HERE / "canonical-mapping.md").read_text()
    pinned = re.findall(r"\| `([^`]+)` \| [\d,]+ \| `([0-9a-f]{64})` \|", mapping)
    source_assets = []
    for relative, expected in pinned:
        path = ROOT / relative
        if digest(path) != expected:
            raise ValueError(f"mapped source hash mismatch: {relative}")
        role = "provenance"
        if "/tasks/" in relative:
            role = "private-reference" if "/tests/" in relative else "task-input"
        elif "/agent/" in relative:
            role = "trace"
        elif "/artifacts/" in relative:
            role = "saved-output"
        elif "/verifier/" in relative or relative.endswith("measurements.xlsx"):
            role = "private-reference"
        source_assets.append(asset(path, role))
    assert any(item["path"] == AUDIT.relative_to(ROOT).as_posix() for item in source_assets)
    audit = json.loads(AUDIT.read_text())
    freeze = json.loads(FREEZE.read_text())
    for relative, expected in freeze["files"].items():
        if digest(TASK / relative) != expected:
            raise ValueError(f"frozen task hash mismatch: {relative}")
    metadata = json.loads((TASK / "environment/data/manifest.json").read_text())
    inventory = []
    for item in metadata["series"]:
        path = TASK / "environment/data" / item["file"]
        if digest(path) != audit["sources"][path.relative_to(ROOT).as_posix()]:
            raise ValueError(f"audited input hash mismatch: {path}")
        source_assets.append(asset(path, "task-input"))
        inventory.append(
            {
                "visit": item["visit"],
                "id": item["id"],
                "description": item["sequence"],
                "shape": item["shape"],
                "affine": item["affine_ras_mm"],
                "phase_count": len(item["phase_acquisition_offsets_seconds"])
                if len(item["shape"]) == 4
                else 1,
            }
        )
    assert len(inventory) == 122
    for path, role in [
        (HERE / "canonical-mapping.md", "provenance"),
        (HERE / "prepare_trace.py", "provenance"),
        (LICENSE, "license"),
    ]:
        source_assets.append(asset(path, role))

    visits = []
    preview_receipts = []
    for visit, first, day, count in [("V1", 54, 0, 53), ("V2", 115, 34, 50)]:
        native = nib.load(TASK / "environment/data" / f"{visit}_S{first:02}.nii.gz")
        shape = list(native.shape)
        affine = native.affine
        spacing = np.linalg.norm(affine[:3, :3], axis=0).tolist()
        preview_shape = [128, 128, count]
        indices = [
            np.rint(np.linspace(0, size - 1, samples)).astype(int)
            for size, samples in zip(shape, preview_shape, strict=True)
        ]
        for axis, samples in enumerate(indices):
            assert samples[0] == 0 and samples[-1] == shape[axis] - 1
            assert np.all(np.diff(samples) > 0)
        selected = []
        percentiles = []
        for ordinal in range(8):
            sid = f"S{first + ordinal}"
            path = TASK / "environment/data" / f"{visit}_{sid}.nii.gz"
            image = nib.load(path)
            assert list(image.shape) == shape and np.array_equal(image.affine, affine)
            # NIfTI proxy is read-only; no source file is modified or method replayed.
            values = np.asanyarray(image.dataobj)[np.ix_(*indices)].astype(np.float32)
            assert np.isfinite(values).all()
            selected.append((sid, ordinal, values))
            percentiles.append(np.percentile(values, [1, 99.8]).tolist())
        # Same deterministic fixed window across all eight series in one visit.
        # Visit windows are independent display scales, never signal calibration.
        window = [min(row[0] for row in percentiles), max(row[1] for row in percentiles)]
        window[1] = max(window[1], window[0] + 1)
        series = []
        uint8_hashes = {}
        poster = ""
        for sid, ordinal, values in selected:
            image = np.rint(
                np.clip((values - window[0]) / (window[1] - window[0]), 0, 1) * 255
            ).astype(np.uint8)
            raw = image.tobytes(order="C")
            zipped = gzip.compress(raw, mtime=0)
            assert len(gzip.decompress(zipped)) == int(np.prod(preview_shape))
            series.append(
                {"id": sid, "ordinal": ordinal, "volume": base64.b64encode(zipped).decode()}
            )
            uint8_hashes[sid] = hashlib.sha256(raw).hexdigest()
            if ordinal == 1:
                # Whole supplied first-post grid, no solver/reference selections or marks.
                projection = Image.fromarray(np.flipud(image.max(axis=1).T))
                buffer = io.BytesIO()
                projection.save(buffer, format="PNG")
                poster = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
        visits.append(
            {
                "id": visit,
                "day": day,
                "shape": shape,
                "affine": affine.tolist(),
                "spacing": spacing,
                "preview_shape": preview_shape,
                "preview_indices": [samples.tolist() for samples in indices],
                "preview_window": window,
                "series": series,
                "poster": poster,
            }
        )
        preview_receipts.append(
            {
                "visit": visit,
                "window": window,
                "series_percentiles_1_99_8": percentiles,
                "indices": [samples.tolist() for samples in indices],
                "uint8_sha256": uint8_hashes,
            }
        )

    trajectory = json.loads((RUN / "agent/trajectory.json").read_text())
    steps = {step["step_id"]: step for step in trajectory["steps"]}
    assessment = json.loads((RUN / "artifacts/app/answer/assessment.json").read_text())
    measurements_saved = json.loads(
        (RUN / "artifacts/app/answer/measurement_summary.json").read_text()
    )
    citations = [
        {
            "visit": item["visit"],
            "series_id": item["series_id"],
            "phase": item["phase"],
            "ijk": item["voxel"],
            "description": item["description"],
        }
        for item in assessment["observations"]
    ]
    assert all(item["phase"] == 0 for item in citations)
    measurements = []
    for visit, sid in [("V1", "S55"), ("V2", "S116")]:
        saved = measurements_saved[visit]
        stated = next(
            item
            for item in assessment["comparison"]["size_measurements_mm"]
            if item["visit"] == visit
        )
        bounds = np.array(saved["bbox_native_inclusive"])
        measurements.append(
            {
                "visit": visit,
                "series_id": sid,
                "phase": 0,
                "fraction": 0.3,
                "bbox_min": bounds[:, 0].tolist(),
                "bbox_max": bounds[:, 1].tolist(),
                "spans_mm": saved["bbox_mm"],
                "diameter_mm": saved["longest_diameter_mm"],
                "reported_mm": stated["longest_diameter_mm"],
                "method": saved["threshold"]
                + "; connected component containing local peak; largest native voxel-edge bbox span. Saved prose: "
                + stated["method"],
            }
        )
    dynamic_views = [
        view("V1", "S55", axis=2, levels=[51, 50, 49, 52], bounds=[[0, 0, 49], [512, 512, 53]]),
        view("V2", "S116", axis=2, levels=[49, 48, 50, 46], bounds=[[0, 0, 46], [512, 512, 51]]),
    ]
    mip_views = [
        view(visit, sid, axis=2, bounds=[[lo, 120, 15], [hi, 490, last]])
        for visit, sid, last in [("V1", "S55", 96), ("V2", "S116", 90)]
        for lo, hi in [(20, 256), (256, 492)]
    ]
    centers = {"V1": [390, 270, 60], "V2": [386, 302, 64]}
    focus_views = []
    for visit, first in [("V1", 54), ("V2", 115)]:
        i, j, k = centers[visit]
        for ordinal in [0, 1, 2, 4, 7]:
            focus_views.append(
                view(
                    visit,
                    f"S{first + ordinal}",
                    axis=2,
                    levels=[k],
                    bounds=[[i - 45, j - 45, k], [i + 46, j + 46, k + 1]],
                    center=centers[visit],
                )
            )
    extent_views = [
        view("V1", "S55", bounds=[[330, 200, 40], [450, 340, 85]]),
        view("V2", "S116", bounds=[[330, 230, 40], [450, 370, 90]]),
    ]
    saved_views = [
        view(item["visit"], item["series_id"], axis=2, levels=[item["ijk"][2]], center=item["ijk"])
        for item in citations
    ]
    states = [
        state(
            "input",
            10,
            "Receive both native examinations",
            "inventory",
            [view(v["id"], v["series"][0]["id"], bounds=[[0, 0, 0], v["shape"]]) for v in visits],
            "Whole supplied 122-series inventory; context previews cover the sixteen selected dynamic grids, not every input series. No target disclosed.",
        ),
        state(
            "dynamic",
            15,
            "Recorded early-subtraction axial montage",
            "planes",
            dynamic_views,
            "Four actual axial k levels selected per visit; S55-S54 / S116-S115. Enclosing bounds include unsampled gaps. Delivered overview also shows baseline, ordinal 7 and peak-subtraction panels.",
            15,
        ),
        state(
            "mip",
            18,
            "Recorded early-subtraction projections",
            "slab",
            mip_views,
            "Maximum over native k; two i halves and j=120:490. This exact delivered image has laterality labels corrected in subsequent code at step 20; preserve the observation and caveat.",
            18,
        ),
        state(
            "focus",
            22,
            "Recorded native focus and phase views",
            "focus",
            focus_views,
            "Exact inspection centres and 91x91 native windows at ordinals 0,1,2,4,7. Red cross is solver-selected focus, not GT. Saved citations differ by one voxel.",
            22,
        ),
        state(
            "extent",
            23,
            "Recorded component threshold comparison",
            "measurement",
            extent_views,
            "Actual local computational ROIs; sigma=1 voxel early subtraction, fractions 0.20..0.60 inspected; saved method uses 0.30. Axis-aligned component-box span is not clinical diameter.",
        ),
        state(
            "saved",
            29,
            "Saved qualified assessment and measurements",
            "saved",
            saved_views,
            "Four exact 3D citations (file phase 0), final report and rounded measurement summary. Step 29 printed summary before unrelated git-not-found tail error; contract correctness is not clinical correctness.",
        ),
        state(
            "orientation-correction",
            20,
            "Logged laterality-label correction",
            "slab",
            mip_views,
            "Step 20 corrects the MIP labels in code; final saved corrected figure is a separate artifact. No corrected MIP view_image delivery is recorded.",
        ),
        state(
            "candidate-focus",
            19,
            "Printed early-subtraction candidates",
            "focus",
            [
                view("V1", "S55", bounds=[[280, 180, 10], [480, 460, 96]], center=centers["V1"]),
                view("V2", "S116", bounds=[[280, 180, 10], [480, 460, 90]], center=centers["V2"]),
            ],
            "ROI smoothed with sigma=(2,2,1) native voxels; printed positive-R centres. The original code comment said left; anatomical orientation and subsequent label correction identify right.",
        ),
        state(
            "component-boxes",
            29,
            "Saved component bounding boxes",
            "measurement",
            [
                view(
                    item["visit"],
                    item["series_id"],
                    bounds=[item["bbox_min"], [value + 1 for value in item["bbox_max"]]],
                )
                for item in measurements
            ],
            "Inclusive saved voxel extrema converted to half-open array-cell endpoints. Physical edges use affine(bounds-0.5). Reproducing a bbox method does not validate a clinical tumor contour.",
        ),
    ]
    for item in states:
        for inspection in item["views"]:
            shape = next(v["shape"] for v in visits if v["id"] == inspection["visit"])
            if inspection["bounds"]:
                for lo, hi, size in zip(*inspection["bounds"], shape, strict=True):
                    assert 0 <= lo < hi <= size
            if inspection["center_ijk"]:
                assert all(
                    0 <= value < size
                    for value, size in zip(inspection["center_ijk"], shape, strict=True)
                )
    clinical = next(row for row in audit["reference_summary"] if row["case"] == "P03")
    reproduction = next(
        row for row in audit["measurement_reproduction"] if row["condition"] == "p03-neutral"
    )
    frozen = json.loads((RUN / "verifier/contract.json").read_text())
    reference = {
        "contract_pass": frozen["contract_pass"],
        "reward": float((RUN / "verifier/reward.txt").read_text()),
        "clinical_accuracy": frozen["clinical_accuracy"],
        "ftv_cc": clinical["ftv_cc"],
        "diameter_raw": clinical["diameter_raw"],
        "diameter_unit": clinical["diameter_unit"],
        "pcr": clinical["pCR"],
        "audit_diameters_mm": [row["diameter_mm"] for row in reproduction["visits"]],
        "audit_change_percent": reproduction["change_percent"],
        "forecast_baseline": "All three neutral next-visit source diameters decreased; always-smaller also matches 3/3. Same-patient cue is not an independent fourth case. No forecast benefit or generalization established.",
    }
    selected_steps = [7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29]
    trace = [
        {
            "step": sid,
            "timestamp": steps[sid].get("timestamp"),
            "calls": [
                json.dumps(call["arguments"], ensure_ascii=False)
                for call in steps[sid].get("tool_calls", [])
            ],
            "output": text(steps[sid]),
        }
        for sid in selected_steps
    ]
    times = [
        datetime.fromisoformat(step["timestamp"].replace("Z", "+00:00"))
        for step in trajectory["steps"]
    ]
    data = {
        "attempt": ATTEMPT,
        "visits": visits,
        "inventory": inventory,
        "registered": False,
        "states": states,
        "measurements": measurements,
        "citations": citations,
        "summary": assessment["comparison"]["summary"],
        "impression": assessment["impression"]["leading_explanation"],
        "forecast": {
            "direction": assessment["forecast"]["next_exam_extent"],
            "confidence": assessment["forecast"]["confidence"],
            "basis": assessment["forecast"]["basis"],
        },
        "evidence": (RUN / "artifacts/app/answer/report.md").read_text(),
        "trace": trace,
        "elapsed_seconds": (times[-1] - times[0]).total_seconds(),
        "steps_in_trace": len(trajectory["steps"]),
        "reference": reference,
    }
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
        with Image.open(path) as image:
            image.verify()
        derivatives.append(asset(path, "delivered-image", sid))
        delivered.append({"step": sid, "path": path.name})
    data["delivered_images"] = delivered
    (out / "data.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    derivatives.insert(0, asset(out / "data.json", "derived-display"))
    for source, name, role in [
        (LICENSE, "DATA-LICENSE.txt", "license"),
        (TASK / "instruction.md", "instruction.txt", "task-input"),
    ]:
        (out / name).write_bytes(source.read_bytes())
        derivatives.append(asset(out / name, role))
    notice = """I-SPY2 / ACRIN 6698 investigators and The Cancer Imaging Archive; Li W et al., npj Breast Cancer 6,63 (2020), https://doi.org/10.1038/s41523-020-00203-7 . Collection DOI 10.7937/TCIA.D8Z0-9T85 . Images/data CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Collection https://www.cancerimagingarchive.net/collection/ispy2/ . No endorsement implied.
Derivatives: two independent native RAS grids, eight selected 3D dynamic series per visit, nearest integer native sample indices to 128x128x53/50; fixed per-visit display window, min(series sampled 1st percentile) to max(series sampled 99.8th percentile). uint8 rounded/clipped C-order, deterministic gzip mtime=0. Whole first-post coronal MIP posters over j, i toward R horizontally and k toward S upward; no solver/reference marks. Native scouts/WATER/FAT retained in inventory only. These previews are context displays, not native-resolution lesion measurements, registration or cross-visit signal calibration.
All three delivered PNGs are extracted exact embedded bytes. Step18 retains its then-incorrect side labels; code correction at step20 and final saved corrected PNG have distinct provenance. Saved final PNGs are not substituted as deliveries. Observed measurements preserve saved rounded bbox spans; private references retain prior audit precision and unresolved source-diameter units. Mechanical pass is not clinical accuracy. Source identities, future outcomes and VOIs were withheld from the solver and stay reader-reference material.
"""
    (out / "SOURCE_NOTICE.txt").write_text(notice)
    derivatives.append(asset(out / "SOURCE_NOTICE.txt", "license"))
    # Keep final figure identities in provenance, without declaring their bytes deliveries.
    for path in sorted((RUN / "artifacts/app/answer").glob("*.png")):
        source_assets.append(asset(path, "saved-output"))
    receipt = {
        "schema": 1,
        "attempt": ATTEMPT,
        "sources": source_assets,
        "derivatives": derivatives,
        "preview": preview_receipts,
        "verification": {
            "frozen_task_files": len(freeze["files"]),
            "inventory_volumes": len(inventory),
            "dynamic_previews": 16,
            "delivered_pngs_exact": 3,
            "states_bounds_valid": True,
            "native_grids_registered": False,
            "clinical_method_recomputed": False,
        },
        "sampling": "Explicit nearest integer native indices, all endpoints included, C-order uint8 gzip mtime=0; fixed window per visit from sampled eight-series percentiles.",
        "poster": "Unmarked whole first-post preview coronal MIP over j; i toward R horizontally, k toward S upward.",
        "limits": [
            "No historical method/helper/scorer/model executed; no new clinical result.",
            "Preview does not provide native-resolution localization or quantitative MR signal calibration.",
            "Independent grids are not registered; dynamic ordinal0..7 differs from file citation phase0.",
            "Delivered images differ from final saved PNGs; preserve step18 label correction boundary.",
            "Selected actions only, no private reasoning or continuous video.",
            "Component bbox span is not adjudicated clinical diameter; source-diameter units unresolved.",
            "Intermediate on-disk script/PNG versions and calibrated injection/phase times absent.",
            "No browser visual acceptance or canonical binding performed.",
        ],
        "runtime": {"numpy": np.__version__, "nibabel": nib.__version__},
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    derivatives.append(asset(out / "receipt.json", "provenance"))
    manifest = {
        "schema": 1,
        "id": "br037-native-trace",
        "entry_id": "tb3-longitudinal-mri",
        "attempt": ATTEMPT,
        "adapter": "longitudinal-mri",
        "coordinates": "RAS-mm",
        "saved_state": "saved",
        "notice": "One retained BR-037 P03 neutral Terra/high breast MRI attempt. Visits are independent native grids; component-box spans and mechanical contract success do not establish clinical accuracy. Exact step18 delivery predates a laterality-label correction.",
        "recovery": "Recover pinned P03 neutral source bytes, then run groups/longitudinal-reading/presentation/native-mri-trace/prepare_trace.py into a fresh .local/anatomy-pose/mri directory. See README; no trial or historical recipe execution is implied.",
        "assets": derivatives + source_assets,
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
                "dynamic_previews": 16,
                "inventory": 122,
                "states": len(states),
                "selected_calls": len(trace),
                "preview_windows": [visit["preview_window"] for visit in visits],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
