"""Audit retained ABRA native geometry and regenerate selected pure task definitions."""

import argparse
import ast
import hashlib
import io
import json
import types
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pydicom
from skimage.measure import find_contours


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    src = args.sources
    out = args.output
    out.mkdir(parents=True, exist_ok=False)

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def write(name, value):
        (out / name).write_text(json.dumps(value, indent=2) + "\n")

    def subset(path, names, ns):
        tree = ast.parse(path.read_text())
        nodes = [
            n
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names
        ]
        assert {n.name for n in nodes} == set(names)
        exec(
            compile(
                ast.fix_missing_locations(
                    ast.Module(
                        body=[
                            ast.ImportFrom(
                                module="__future__",
                                names=[ast.alias(name="annotations")],
                                level=0,
                                lineno=1,
                                col_offset=0,
                            ),
                            *nodes,
                        ],
                        type_ignores=[],
                    )
                ),
                str(path),
                "exec",
            ),
            ns,
        )
        return {
            n.name: hashlib.sha256(ast.get_source_segment(path.read_text(), n).encode()).hexdigest()
            for n in nodes
        }

    ct = []
    with zipfile.ZipFile("runs/task-brief-samples/abra/ct.zip") as z:
        for name in z.namelist():
            if name.endswith(".dcm"):
                raw = z.read(name)
                d = pydicom.dcmread(io.BytesIO(raw))
                ct.append(
                    (float(d.ImagePositionPatient[2]), d, name, hashlib.sha256(raw).hexdigest())
                )
    ct.sort(key=lambda x: x[0])
    assert len(ct) == 140
    uid_to_k = {str(d.SOPInstanceUID): k for k, (_, d, *_) in enumerate(ct)}
    assert len(uid_to_k) == 140
    with zipfile.ZipFile("runs/task-brief-samples/abra/seg.zip") as z:
        names = [n for n in z.namelist() if n.endswith(".dcm")]
        assert len(names) == 1
        raw = z.read(names[0])
        seg = pydicom.dcmread(io.BytesIO(raw))
    assert seg.Modality == "SEG"
    assert int(seg.BitsAllocated) == 1
    masks = np.unpackbits(np.frombuffer(seg.PixelData, dtype=np.uint8), bitorder="little")[
        : int(seg.NumberOfFrames) * int(seg.Rows) * int(seg.Columns)
    ].reshape(int(seg.NumberOfFrames), int(seg.Rows), int(seg.Columns))
    assert np.array_equal(masks, seg.pixel_array)
    manifest = json.loads((src / "data/studies/study_manifest.json").read_text())
    studies = []

    def visit(v):
        if isinstance(v, dict):
            if v.get("study_uid") == str(seg.StudyInstanceUID) and "series" in v:
                studies.append(v)
            else:
                for x in v.values():
                    visit(x)
        elif isinstance(v, list):
            for x in v:
                visit(x)

    visit(manifest)
    assert len(studies) == 1
    study = studies[0]
    ann_sources = [
        s for s in study["series"] if s["modality"] == "SEG" and "Nodule 1 - " in s["description"]
    ]
    assert len(ann_sources) == 1 and ann_sources[0]["series_uid"] == str(seg.SeriesInstanceUID)
    ns = {"np": np, "Any": Any, "AnnotationInfo": lambda **kw: types.SimpleNamespace(**kw)}
    functions = subset(
        src / "scripts/task_generators/tier3.py",
        ["_volumetric_consensus", "_frame_to_slice_index", "t3_nodule_segmentation_tasks"],
        ns,
    )
    zmap = {round(z, 3): k for k, (z, *_) in enumerate(ct)}
    assert len(zmap) == 140
    anns = []
    frames = []
    selected = {0, 66, 139}
    shared = seg.SharedFunctionalGroupsSequence[0]
    seg_iop = np.array(shared.PlaneOrientationSequence[0].ImageOrientationPatient, float)
    seg_spacing = np.array(shared.PixelMeasuresSequence[0].PixelSpacing, float)
    for idx, pf in enumerate(seg.PerFrameFunctionalGroupsSequence):
        k = ns["_frame_to_slice_index"](pf, zmap)
        assert k is not None
        uid = str(pf.DerivationImageSequence[0].SourceImageSequence[0].ReferencedSOPInstanceUID)
        assert uid_to_k[uid] == k
        d = ct[k][1]
        np.testing.assert_allclose(
            pf.PlanePositionSequence[0].ImagePositionPatient, d.ImagePositionPatient, atol=1e-6
        )
        np.testing.assert_allclose(seg_iop, d.ImageOrientationPatient, atol=1e-6)
        np.testing.assert_allclose(seg_spacing, d.PixelSpacing, atol=1e-6)
        assert int(seg.Rows) == int(d.Rows) == 512 and int(seg.Columns) == int(d.Columns) == 512
        contour = max(find_contours(masks[idx].astype(float), 0.5), key=len)
        poly = [[round(float(c[1]), 2), round(float(c[0]), 2)] for c in contour]
        if poly[0] != poly[-1]:
            poly.append(poly[0])
        xs, ys = zip(*poly, strict=True)
        bounds = (min(xs), min(ys), max(xs), max(ys))
        ann = types.SimpleNamespace(
            segment_label=str(seg.SegmentSequence[0].SegmentLabel),
            segment_index=1,
            slice_index=k,
            polygon=poly,
            ct_series_uid=str(d.SeriesInstanceUID),
            bbox=bounds,
            nodule_number=1,
            raw_mask=masks[idx],
            annotator_id=str(seg.SeriesInstanceUID),
        )
        anns.append(ann)
        frames.append(
            {
                "frame": idx,
                "k": k,
                "z_lps_mm": ct[k][0],
                "pixels": int(masks[idx].sum()),
                "sop_uid": uid,
                "polygon": poly,
            }
        )
        selected.add(k)
    consensus = ns["_volumetric_consensus"](anns)
    assert len(consensus) == len(anns)
    for a in consensus:
        orig = next(f for f in frames if f["k"] == a.slice_index)
        assert a.polygon == orig["polygon"]
    st = types.SimpleNamespace(**study)
    tasks = ns["t3_nodule_segmentation_tasks"](st, consensus)
    chosen = next(t for t in tasks if t["expected_outcome"]["slice_index"] == 66)
    ons = {"AnnotationInfo": Any, "StudyInfo": Any}
    functions.update(
        subset(
            src / "scripts/task_generators/tier3_oracle.py",
            ["_build_oracle_data", "t3_oracle_segmentation_tasks"],
            ons,
        )
    )
    oracle = ons["t3_oracle_segmentation_tasks"](st, consensus)
    assert len(oracle) == 1
    slicens = {}
    functions.update(subset(src / "src/scoring/outcome/iou_scorer.py", ["_slice_penalty"], slicens))
    penalties = [
        {
            "delta": i,
            "penalty": slicens["_slice_penalty"](66, None if i is None else 66 + i),
            "reference_copy_polygon_score": max(
                0, 1 - slicens["_slice_penalty"](66, None if i is None else 66 + i)
            ),
        }
        for i in [0, 1, 2, 3, 4, None]
    ]
    summary = {
        "case": "LIDC-IDRI-0003",
        "ct_series_uid": str(ct[0][1].SeriesInstanceUID),
        "study_uid": str(seg.StudyInstanceUID),
        "ct_shape": [140, 512, 512],
        "slice_order": "ascending ImagePositionPatient z, zero-based",
        "spacing_mm": [float(x) for x in ct[0][1].PixelSpacing],
        "slice_step_mm": float(ct[1][0] - ct[0][0]),
        "orientation_lps": [float(x) for x in ct[0][1].ImageOrientationPatient],
        "origins_lps": {
            str(k): [float(x) for x in ct[k][1].ImagePositionPatient] for k in sorted(selected)
        },
        "selected_native_members": [
            {"k": k, "member": ct[k][2], "sha256": ct[k][3]} for k in sorted(selected)
        ],
        "seg": {
            "series_uid": str(seg.SeriesInstanceUID),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "frame_count": len(frames),
            "label": str(seg.SegmentSequence[0].SegmentLabel),
            "declared_nodule_1_annotators": ann_sources,
            "consensus_equals_single_annotator": True,
            "frame_alignment": "Every referenced SOP UID, position, orientation and pixel spacing matches the exact CT slice.",
        },
        "frames": frames,
        "ordinary": chosen,
        "oracle": oracle[0],
        "function_sha256": functions,
        "scorer_arithmetic": penalties,
        "scorer_arithmetic_scope": "Analytical same-polygon IoU=1, combined with the exact extracted slice-penalty function; not a full Shapely outcome scorer execution or a model result.",
        "limits": [
            "Only this nodule and this study are audited; other nodules require their own SEG series.",
            "Source annotations and reference-copy illustrations are not solver output or independent clinical truth.",
            "Actual OHIF runtime and full benchmark scorer were not executed; Shapely is absent and no runtime was installed.",
        ],
    }
    write("audit.json", summary)
    write("ordinary-task.json", chosen)
    write("oracle-task.json", oracle[0])
    print(
        json.dumps(
            {
                k: summary[k]
                for k in ["ct_shape", "spacing_mm", "slice_step_mm", "scorer_arithmetic"]
            }
        )
    )
    print("annotation_frames", [(f["k"], f["pixels"]) for f in frames])
    print("ordinary", chosen["id"], "oracle_slice", oracle[0]["expected_outcome"]["slice_index"])

    # Pin all inspected source files and the exact native archives.
    source_files = []
    for receipt in ["receipt.json", "extra-receipt.json"]:
        for item in json.loads((src / receipt).read_text())["files"]:
            path = src / item["path"]
            raw = path.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            assert blob == item["git_blob"]
            source_files.append(
                {**item, "local_path": str(path), "sha256": sha(path), "bytes": len(raw)}
            )
    source_pins = {str(Path(__file__).relative_to(Path.cwd())): sha(Path(__file__))}
    for p in [
        "runs/task-brief-samples/abra/ct.zip",
        "runs/task-brief-samples/abra/seg.zip",
        "presentation/external-tasks/samples.json",
    ]:
        source_pins[p] = sha(Path(p))
    assert (
        source_pins["runs/task-brief-samples/abra/ct.zip"]
        == "a780bd9438313d98e1b86302c6ed64a9c7d9941f6c418ac93054ec2628b9bb3b"
    )
    assert (
        source_pins["runs/task-brief-samples/abra/seg.zip"]
        == "5198f6646297c2675ca4b8c5d0d2195efdea3fedcae7ff4aa01f757a64dc51eb"
    )
    summary["source_files"] = source_files
    summary["source_pins"] = source_pins
    summary["scope"] = (
        "Source-derived task illustration and selected pure generator replay; not a model trial, an OHIF runtime replay or full benchmark scorer execution."
    )
    summary["license_sources"] = [
        {
            "url": "https://www.cancerimagingarchive.net/collection/lidc-idri/",
            "license": "CC BY 3.0",
            "checked": "2026-09-28",
        },
        {
            "url": "https://www.cancerimagingarchive.net/analysis-result/dicom-lidc-idri-nodules/",
            "license": "CC BY 3.0",
            "checked": "2026-09-28",
        },
    ]
    write("audit.json", summary)
    compact = {k: v for k, v in summary.items() if k not in ["frames", "ordinary", "oracle"]}
    compact["frames"] = [
        {k: v for k, v in frame.items() if k != "polygon"}
        | {"polygon_points": len(frame["polygon"])}
        for frame in frames
    ]
    compact["ordinary"] = {k: v for k, v in chosen.items() if k != "expected_outcome"} | {
        "reference_slice": 66,
        "iou_threshold": 0.5,
    }
    compact["oracle"] = {
        k: v for k, v in oracle[0].items() if k not in ["oracle_data", "expected_outcome"]
    } | {
        "reference_slice": 66,
        "iou_threshold": 0.5,
        "overview": oracle[0]["oracle_data"]["overview"],
    }
    compact["artifacts"] = {
        str(out / p): sha(out / p) for p in ["audit.json", "ordinary-task.json", "oracle-task.json"]
    }
    write("source-audit.json", compact)


if __name__ == "__main__":
    main()
