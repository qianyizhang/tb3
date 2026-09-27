"""Audit frozen BR037 inputs and derive display views; never execute historical authors."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pydicom
from PIL import Image
from scipy import ndimage

PACK = "retained-longitudinal-mri-v1"
RAW = "runs/br037-longitudinal-reading"
PINS = {
    "docs/evidence/br037-curation.json": "eab3c15f8826a6a0c09021527a1dcf2b4a0cadd3adffb570df53f2ea6257c0b3",
    "docs/evidence/br037-freeze.json": "42f18bdc5ccfa61409983c6c933394d5d5a87ad09ca732786fd1dc47867bdd2d",
    "docs/evidence/br037-results.json": "7f00ad8f48c3ce256ae345397a28abe53d15b631852e63d0901da1b2b40b1fad",
    f"{RAW}/measurement-audit.json": "da8c08f6bfda532ed6df4eef476199894e9cb724ca98d1c0d76549e9d443feb7",
    f"{RAW}/phase-review.json": "ffaa46e13aa9db039b5aac91fb04b5421740c5933d810387cd8926bd8d896e30",
    f"{RAW}/source/ispy2.html": "0bcbf84bf91748cbc9f1df90851a4d1f245f9e90b130c46079369a2eda8cc69c",
    f"{RAW}/source/measurements.xlsx": "f714c7784b1e57daa74d7cfb20db71cd432b4e4596b9b4eacdd5a76b7f8a58dc",
    f"{RAW}/source/clinical.xlsx": "c016962d2d1e23686746ad3e74a58caeb2d1362f6393fd6209c10723f87c3a53",
    f"{RAW}/source/private-tags.xlsx": "16391cf2c0372adbb2ec9d58059ac64026a7440ee8ab3da6c32b3a3c7f66c34a",
    f"{RAW}/source/data-description.pdf": "d1c1525a962d916483b0fde69736a6717cc647ee19468690d5d591c4e077544e",
}


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def png(array, limits, reverse=False, size=None):
    lo, hi = limits
    pixels = np.rint(np.clip((array - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8).T
    if reverse:
        pixels = pixels[::-1, ::-1]
    image = Image.fromarray(pixels)
    if size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def build(root, output, audit_path):
    if output.exists() or audit_path.exists():
        raise FileExistsError("Use fresh output and audit destinations")
    sources = {}

    def pin(path, expected):
        assert sha(root / path) == expected, path
        sources[str(path)] = expected

    for path, digest in PINS.items():
        pin(path, digest)
    curation = read(root / "docs/evidence/br037-curation.json")
    frozen = read(root / "docs/evidence/br037-freeze.json")
    retained = read(root / "docs/evidence/br037-results.json")
    tasks, freezes, series, audits = {}, [], {}, {}
    for condition in frozen["conditions"]:
        name = condition["condition"]
        fp = f"{RAW}/{name}-freeze.json"
        pin(fp, condition["freeze_receipt_sha256"])
        freeze = read(root / fp)
        task = root / condition["task_path"]
        for rel, digest in freeze["files"].items():
            pin((task / rel).relative_to(root), digest)
        tasks[name] = task / "environment/data"
        freezes.append(
            {
                "condition": name,
                "files": len(freeze["files"]),
                "task_checksum": condition["task_checksum"],
            }
        )
    left = read(root / f"{RAW}/p03-neutral-freeze.json")["files"]
    right = read(root / f"{RAW}/p03-cue-freeze.json")["files"]
    assert sorted(k for k in left if left[k] != right[k]) == ["instruction.md", "task.toml"]
    for case in curation["cases"]:
        name = case["case"]
        ap = f"{RAW}/{name}-conversion-audit.json"
        pin(ap, case["conversion_audit_sha256"])
        audits[name] = {a["series"]: a for a in read(root / ap)}
        series[name] = {
            s["id"]: s for s in read(tasks[f"{name.lower()}-neutral"] / "manifest.json")["series"]
        }
    samples = []
    loaded = {}

    def load(case, sid):
        key = (case, sid)
        if key in loaded:
            return loaded[key]
        meta = series[case][sid]
        path = tasks[f"{case.lower()}-neutral"] / meta["file"]
        nii = nib.load(path)
        assert list(nii.shape) == meta["shape"]
        assert np.allclose(nii.affine, meta["affine_ras_mm"], atol=2e-5)
        assert np.allclose(nii.header.get_zooms()[:3], meta["voxel_sizes_mm"])
        sample = audits[case][sid]["sample_checks"][0]
        pin(f"{RAW}/{sample['source']}", sample["sha256"])
        ds = pydicom.dcmread(root / RAW / sample["source"])
        original = ds.pixel_array.astype(np.float32).T * float(ds.get("RescaleSlope", 1)) + float(
            ds.get("RescaleIntercept", 0)
        )
        index = (slice(None), slice(None), sample["k"])
        if len(nii.shape) == 4:
            index += (sample["phase"],)
        error = float(np.max(np.abs(np.asarray(nii.dataobj[index]) - original)))
        assert error < 1e-3
        ras = nii.affine @ [0, 0, sample["k"], 1]
        origin = np.asarray(ds.ImagePositionPatient, float) * [-1, -1, 1]
        assert np.allclose(ras[:3], origin, atol=2e-3)
        samples.append(
            {
                "case": case,
                "series": sid,
                "shape": list(nii.shape),
                "affine_ras_mm": nii.affine.tolist(),
                "dicom_pixel_max_error": error,
                "origin_error_mm": float(np.max(np.abs(ras[:3] - origin))),
            }
        )
        loaded[key] = nii
        return nii

    def plane(nii, k, phase=0):
        return np.asarray(
            nii.dataobj[:, :, k, phase] if len(nii.shape) == 4 else nii.dataobj[:, :, k],
            dtype=np.float32,
        )

    overview = []
    for case, ids in [("P01", ["S14", "S22"]), ("P02", ["S20", "S40"]), ("P03", ["S55", "S116"])]:
        row = []
        for sid in ids:
            nii = load(case, sid)
            k = nii.shape[2] // 2
            image = plane(nii, k, 1 if len(nii.shape) == 4 else 0)
            limits = np.percentile(image, [1, 99.5]).tolist()
            row.append(
                {
                    **series[case][sid],
                    "k": k,
                    "phase": 1 if len(nii.shape) == 4 else 0,
                    "display_range": limits,
                    "image": png(image, limits, case != "P02", (256, 256)),
                }
            )
        overview.append({"case": case, "visits": row})
    p02 = {"visits": []}
    phase_review = read(root / RAW / "phase-review.json")
    for j, row in enumerate(phase_review["rows"]):
        sid = row["series_id"]
        nii = load("P02", sid)
        i, k_y, k = row["native_reference_center"]
        crop = np.asarray(nii.dataobj[i - 55 : i + 55, k_y - 55 : k_y + 55, k, :], np.float32)
        limits = np.percentile(crop, [1, 99.5]).tolist()
        assert np.allclose(limits, row["display_range"])
        t2id = ["S19", "S39"][j]
        t2 = load("P02", t2id)
        center = curation["cases"][1]["source_reference_regions"][j]["voi_center_ras_mm"]
        ti, tj, tk = np.rint(np.linalg.inv(t2.affine) @ [*center, 1])[:3].astype(int)
        t2crop = plane(t2, int(tk))[ti - 55 : ti + 55, tj - 55 : tj + 55]
        p02["visits"].append(
            {
                "visit": row["visit"],
                "series": sid,
                "center": row["native_reference_center"],
                "bounds": [i - 55, k_y - 55, 110, 110],
                "spacing_mm": list(map(float, nii.header.get_zooms()[:3])),
                "range": limits,
                "phases": [
                    {
                        "phase": phase,
                        "offset_s": series["P02"][sid]["phase_acquisition_offsets_seconds"][phase],
                        "image": png(crop[:, :, phase], limits),
                    }
                    for phase in [0, 1, 2, 6]
                ],
                "t2": {
                    "series": t2id,
                    "center": [int(ti), int(tj), int(tk)],
                    "image": png(t2crop, np.percentile(t2crop, [1, 99.5])),
                },
            }
        )
    answers = []
    for result in retained["results"]:
        pin(result["answer"], result["answer_sha256"])
        answer = read(root / result["answer"])
        assert answer == result["assessment"]
        answers.append(
            {
                "condition": result["condition"],
                "assessment": answer,
                "contract_reward": result["contract_reward"],
                "clinical_pass": result["clinical_pass"],
            }
        )
    point = answers[1]["assessment"]["observations"][0]
    nii = load("P02", point["series_id"])
    image = plane(nii, point["voxel"][2], point["phase"])
    p02["citation"] = {
        **point,
        "ras_mm": (nii.affine @ [*point["voxel"], 1])[:3].tolist(),
        "image": png(image, np.percentile(image, [1, 99.5]), False, (256, 256)),
    }
    measurement = read(root / RAW / "measurement-audit.json")
    p03 = {"methods": []}
    for condition in measurement["conditions"]:
        rows = []
        for j, target in enumerate(condition["measurements"]):
            neutral = condition["condition"].endswith("neutral")
            base_id = ["S54", "S115"][j]
            post_id = (["S55", "S116"] if neutral else ["S57", "S116"])[j]
            base, post = load("P03", base_id), load("P03", post_id)
            sub = np.asarray(post.dataobj, dtype=np.float32) - np.asarray(
                base.dataobj, dtype=np.float32
            )
            seed = np.array([[388, 270, 58], [385, 301, 63]][j])
            if neutral:
                sub = ndimage.gaussian_filter(sub, 1)
                lo = np.array([[330, 200, 40], [330, 230, 40]][j])
                hi = np.array([[450, 340, 85], [450, 370, 90]][j])
            else:
                lo = seed - [30, 40, 13]
                hi = np.add(seed, [31, 41, 14])
            cut = sub[tuple(slice(a, b) for a, b in zip(lo, hi, strict=True))]
            fraction = target["method"]["threshold_fraction"]
            labels, _ = ndimage.label(
                cut >= fraction * cut.max() if neutral else cut > fraction * cut.max()
            )
            label_id = (
                labels[np.unravel_index(np.argmax(cut), cut.shape)]
                if neutral
                else labels[tuple(seed - lo)]
            )
            assert label_id > 0
            pts = np.argwhere(labels == label_id) + lo
            low, high = pts.min(0), pts.max(0)
            dims = (high - low + int(neutral)) * post.header.get_zooms()[:3]
            diameter = float(max(dims))
            assert abs(diameter - target["recomputed_mm"]) < 1e-6
            bounds = [330, 210 if j == 0 else 240, 120, 120]
            x, y, w, h = bounds
            k = int(seed[2])
            arr = plane(post, k)[x : x + w, y : y + h]
            rows.append(
                {
                    "visit": target["visit"],
                    "series": post_id,
                    "phase": 0,
                    "k": k,
                    "bounds": bounds,
                    "spacing_mm": list(map(float, post.header.get_zooms()[:3])),
                    "bbox_native_min": low.tolist(),
                    "bbox_native_max": high.tolist(),
                    "bbox_mm": dims.tolist(),
                    "diameter_mm": diameter,
                    "reported_mm": target["reported_mm"],
                    "method": target["method"],
                    "image": png(arr, np.percentile(arr, [1, 99.5]), True),
                }
            )
            del sub, cut, labels, pts
        change = (rows[1]["diameter_mm"] / rows[0]["diameter_mm"] - 1) * 100
        assert abs(change - condition["recomputed_percent_change"]) < 1e-8
        p03["methods"].append(
            {"condition": condition["condition"], "visits": rows, "change_percent": change}
        )
    references = []
    for c in curation["cases"]:
        references.append(
            {
                "case": c["case"],
                "source_id": c["source_id"],
                "ftv_cc": c["ftv_cc"],
                "diameter_raw": c["source_diameter_values"],
                "diameter_unit": "unresolved in source workbook",
                "ftv_change_percent": 100 * (c["ftv_cc"][1] / c["ftv_cc"][0] - 1),
                "diameter_change_percent": 100
                * (c["source_diameter_values"][1] / c["source_diameter_values"][0] - 1),
                "pCR": c["clinical_context"]["pCR"],
            }
        )
    output.mkdir(parents=True)
    write(
        output / "source.json",
        {
            "overview": overview,
            "cases": [
                {
                    "case": c["case"],
                    "volumes": c["visible_volumes"],
                    "frames": c["source_frame_count_visible"],
                    "days": c["visible_exam_days"],
                }
                for c in curation["cases"]
            ],
            "display": "Axial radiological: patient R left, L right, A top, P bottom. Native visits are not registered. Full field images downsampled 512 to 256 with Lanczos; crops retain native pixels. Windows fixed across phases within each P02 visit, never cross-visit calibrated.",
        },
    )
    write(output / "p02.json", p02)
    write(output / "p03.json", p03)
    write(
        output / "reference.json",
        {
            "cases": references,
            "answers": answers,
            "mechanical_passes": retained["mechanical_passes"],
            "clinical_success_rate": retained["clinical_success_rate"],
            "comparison_class": "diagnostic",
            "forecast_baseline": "All three next-visit source diameters decreased. Always smaller matches 3/3, as did the three neutral outputs; the P03 cue is not an independent patient.",
        },
    )
    (output / "DATA-LICENSE.txt").write_text(
        "I-SPY2 images and shared clinical/multifeature data: Creative Commons Attribution 4.0 International (CC BY 4.0).\nTerms: https://creativecommons.org/licenses/by/4.0/\nCollection: https://www.cancerimagingarchive.net/collection/ispy2/\nSource release record: https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=70230072\nAttribution: I-SPY 2 Trial / ACRIN 6698 investigators and The Cancer Imaging Archive; Li W et al., Predicting breast cancer response to neoadjuvant treatment using multi-feature MRI: results from the I-SPY 2 TRIAL, npj Breast Cancer 6, 63 (2020), https://doi.org/10.1038/s41523-020-00203-7.\nDerived grayscale views, crops, display windows and overlays: TB3 explainers. No endorsement implied.\n"
    )
    (output / "NOTICE.md").write_text("""# Retained BR037 longitudinal MRI teaching views

Source: I-SPY2 public MRI and the pinned 384-patient measurement workbook used in BR037, not a newer collection cohort. Three stratified cases and four saved Terra/high attempts are retained. Source images/measurements are CC BY 4.0; see DATA-LICENSE.txt. Sources and original task hashes are in manifest.json. The builder verifies all original task files, source metadata and saved assessments before derivation. It reads historical conversion/measurement audits but never executes their authoring modules.

Full-field middle axial slices show actual solver-visible reconstructed inputs without target labels. This teaching subset is not the complete solver packet (22/40/122 volumes, including split scouts). P02 phase/T2 crops are explicitly post-hoc source-VOI selected, remove search, and appear only after reference reveal. Native voxel centers map through each NIfTI affine into RAS mm. Visits are not registered. Radiological display flips axes only: R on screen left, A at top. P02 phase windows remain fixed within each visit; there is no quantitative cross-visit intensity calibration. Crops retain native pixels; full-field PNGs are downsampled 512 to 256 with Lanczos and all intensities are mapped to 8-bit display values.

Amber solid marks are saved output citations or projections of independently reproduced saved-method 3D component bounding boxes. They are not lesion contours or adjudicated diameters. P03 file-level phase index is zero because each acquisition phase is a separate 3D file. Neutral uses first postcontrast, sigma 1, threshold 0.30 and voxel-edge spans; cue uses postcontrast 3 then 1, no smoothing, threshold 0.50 and voxel-center spans. The comparison is diagnostic: one pair with several method changes cannot establish a causal cue effect. Display boxes project the entire 3D extent, not a slice-specific segmentation.

Source functional tumor volume (FTV, cc), workbook longest diameter (unit unresolved), pathological complete response and predicted enhancing-component extent are different endpoints. Use unit-invariant diameter percent changes; do not infer mm from source raw values. Four mechanical passes validate schema/citation bounds only, not diagnosis, extent or forecast. Null diameter is permitted. Three next-visit source diameters decreased, so an always-smaller baseline ties the three neutral forecasts. Stratified public cases cannot establish prevalence, held-out generalization, calibration or a clinical success rate.

Portable HTML embeds private-to-solver source references and saved answers. It is a reader explanation, never a solver input packet. No new trial, clinical adjudication, score revision or source-image registration occurs.
""")
    assets = []
    for p in sorted(output.iterdir()):
        assert p.stat().st_size <= 1024**2, p
        assets.append(
            {
                "file": p.name,
                "bytes": p.stat().st_size,
                "sha256": sha(p),
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
            }
        )
    write(
        output / "manifest.json",
        {
            "id": PACK,
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-4.0",
            "frame": "RAS",
            "units": "mm",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "assets": assets,
        },
    )
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    write(
        audit_path,
        {
            "schema": 1,
            "scope": "Source geometry and saved-method reproduction; no clinical adjudication or model execution",
            "sources": sources,
            "frozen_tasks": freezes,
            "p03_same_image_pair": True,
            "dicom_samples": samples,
            "measurement_reproduction": [
                {k: v for k, v in m.items() if k != "visits"}
                | {
                    "visits": [
                        {k: v for k, v in row.items() if k != "image"} for row in m["visits"]
                    ]
                }
                for m in p03["methods"]
            ],
            "reference_summary": references,
            "limits": [
                "Selected DICOM samples verify pixels and geometry, not every acquired instance.",
                "Saved-method reproduction does not validate clinical diameter.",
                "Reference-selected crops remove localization search; visits remain unregistered.",
            ],
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "audit": str(audit_path),
                "frozen_files": sum(x["files"] for x in freezes),
                "dicom_samples": len(samples),
                "measurement_changes": [m["change_percent"] for m in p03["methods"]],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output, args.audit)
