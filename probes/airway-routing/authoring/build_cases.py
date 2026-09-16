"""Build compact natural-error and intact-control development fixtures."""
import hashlib
import json
from pathlib import Path
import sys

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from skimage.graph import MCP_Geometric

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "probes/vessel-geometry/authoring"))
from geometry import transform, resample_path

B = ROOT / "runs/br033-airway-routing/benchmark"


def medial_path(mask, spacing, start, end):
    rad = ndi.distance_transform_edt(mask, sampling=spacing)
    cost = np.full(mask.shape, np.inf, np.float32)
    cost[mask] = 1 / (.25 + rad[mask])
    solver = MCP_Geometric(cost, sampling=tuple(spacing))
    ds, _ = solver.find_costs([tuple(start)], [tuple(end)])
    assert np.isfinite(ds[tuple(end)])
    return np.array(solver.traceback(tuple(end)))


def save_case(case_id, source_id, route, intact):
    src = ROOT / "runs/br033-brain-routing/airway-access/data" / source_id
    run = ROOT / "runs/br033-airway-routing" / ("case" + source_id)
    ni = nib.load(src / f"{source_id}_CT_HR.nii.gz")
    lo, hi = np.array(route["lo"]), np.array(route["hi"])
    sl = tuple(slice(int(x), int(y)) for x, y in zip(lo, hi))
    image = np.asarray(ni.dataobj)[sl]
    gt = np.asarray(nib.load(src / f"{source_id}_CT_HR_label_airways.nii.gz").dataobj)[sl] > 0
    proposed = np.asarray(nib.load(run / "airways/prediction/labels_Airways.nii.gz").dataobj)[sl] > 0
    aff = ni.affine.copy()
    aff[:3, 3] = transform(lo, ni.affine)
    sp = nib.affines.voxel_sizes(aff)
    start, end = np.array(route["start_ijk"]) - lo, np.array(route["end_ijk"]) - lo
    path = medial_path(gt, sp, start, end)
    if intact:
        # Real retained distal segment of the same unchanged prediction. No
        # positive error is synthetically filled to manufacture a control.
        hit = proposed[tuple(path.T)]
        groups = []
        for begin in range(len(hit)):
            if hit[begin] and (begin == 0 or not hit[begin-1]):
                stop = begin
                while stop + 1 < len(hit) and hit[stop+1]:
                    stop += 1
                groups.append((begin, stop))
        begin, stop = max(groups, key=lambda x: x[1] - x[0])
        assert stop - begin >= 5, (case_id, groups)
        start, end = path[begin], path[stop]
        path = medial_path(gt & proposed, sp, start, end)
    world = transform(path, aff)
    reference, _ = resample_path(world, .25, .35)
    missing = path[~proposed[tuple(path.T)]]
    center = path.mean(0) if intact else missing.mean(0)
    # Keep enough anatomical context; the editable sphere is not a route oracle.
    radius_mm = 8. if intact else max(8., np.max(np.linalg.norm((missing-center)*sp, axis=1)) + 3.)
    ijk = np.indices(proposed.shape).transpose(1, 2, 3, 0)
    edit = np.linalg.norm((ijk-center)*sp, axis=-1) <= radius_mm
    seed = np.zeros(proposed.shape, bool)
    seed[tuple(path.T)] = True
    tube = ndi.distance_transform_edt(~seed, sampling=sp) <= 1.5
    core = gt & tube & edit
    # Preserve existing anatomy; oracle fills only the selected route's missing
    # lumen inside the review region. Its truth use is explicitly author-only.
    oracle = proposed | (gt & edit & tube)
    if intact:
        oracle = proposed.copy()
        core &= proposed
    public = B / "input" / case_id
    private = B / "truth" / case_id
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    for name, data in [("image", image), ("proposed_mask", proposed.astype("uint8")), ("editable_region", edit.astype("uint8"))]:
        nib.save(nib.Nifti1Image(data, aff), public / (name + ".nii.gz"))
    request = {"case_id": case_id, "coordinates": "NIfTI RAS millimetres",
               "start_ras_mm": transform(start, aff).tolist(), "end_ras_mm": transform(end, aff).tolist(),
               "review_center_ras_mm": transform(center, aff).tolist(), "review_radius_mm": float(radius_mm)}
    (public / "request.json").write_text(json.dumps(request, indent=2) + "\n")
    np.savez_compressed(private / "reference.npz", image=image, affine=aff, gt=gt,
                        proposed=proposed, editable=edit, core=core, route_tube=tube,
                        reference_path=reference, anchors=transform(np.array([start, end]), aff), intact=np.array(intact))
    nib.save(nib.Nifti1Image(oracle.astype("uint8"), aff), private / "oracle_mask.nii.gz")
    record = {"id": case_id, "source_patient": source_id, "source_gap_id": route["gap_id"],
              "intact_control": intact, "shape": list(image.shape), "crop_lo": lo.tolist(),
              "reference_route_length_mm": float(np.linalg.norm(np.diff(reference, axis=0), axis=1).sum()),
              "proposed_core_coverage": float(proposed[core].mean()),
              "source_prediction_sha256": hashlib.sha256((run / "airways/prediction/labels_Airways.nii.gz").read_bytes()).hexdigest()}
    return record


if __name__ == "__main__":
    assert not B.exists(), "Never overwrite constructed benchmark inputs"
    records = []
    for patient, gap, component, positive, control in [("1", 26, 43, "A01", "A03"), ("10", 43, 112, "A04", "A02")]:
        routes = json.loads((ROOT / f"runs/br033-airway-routing/case{patient}/route-screen/comparison.json").read_text())["routes"]
        route = next(x for x in routes if x["gap_id"] == gap and x["target_component"] == component)
        records.append(save_case(positive, patient, route, False))
        records.append(save_case(control, patient, route, True))
    (B / "build.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps(records, indent=2))
