"""Private verifier: anatomical repair/routing and CPR integrity are separate."""
import json
from pathlib import Path
import sys
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

LIMITS = {"core_coverage": .80, "new_voxels_far_from_reference_mm3": 1.,
          "far_distance_mm": .8, "route_p95_mm": 1.2, "reference_coverage": .9,
          "endpoint_error_mm": 1., "route_length_relative_error": .2,
          "CPR_coordinate_error_mm": .02, "CPR_HU_p99_error": .2,
          "CPR_arc_error_mm": .1, "intact_max_changed_voxels": 0}


def transform(p, a):
    return np.asarray(p) @ a[:3, :3].T + a[:3, 3]


def sample(a, affine, p, order=1, cval=0):
    ijk = transform(p, np.linalg.inv(affine))
    return ndi.map_coordinates(a.astype(np.float32), np.moveaxis(ijk, -1, 0),
                              order=order, mode="constant", cval=cval, prefilter=False)


def score_case(answer, truth):
    z = np.load(truth, allow_pickle=False)
    aff, pr, edit, gt, ref = (z[k] for k in ["affine", "proposed", "editable", "gt", "reference_path"])
    sp = nib.affines.voxel_sizes(aff)
    checks, metrics, errors = {}, {}, {}
    mask = line = None
    try:
        ni = nib.load(answer / "corrected_mask.nii.gz")
        a = np.asarray(ni.dataobj)
        assert a.shape == pr.shape and np.allclose(ni.affine, aff, atol=1e-5, rtol=0), "mask grid"
        assert np.isin(a, [0, 1]).all(), "binary mask"
        mask = a > 0
        checks["format"] = True
        checks["preservation"] = bool(np.array_equal(mask[~edit], pr[~edit]) and np.all(mask[pr]))
        changed = int((mask != pr).sum())
        core_coverage = float(mask[z["core"]].mean())
        d = ndi.distance_transform_edt(~gt, sampling=sp)
        far = float(np.count_nonzero(mask & ~pr & (d > .8)) * np.prod(sp))
        cc, _ = ndi.label(mask & z["route_tube"], np.ones((3, 3, 3)))
        hits = sample(cc, aff, z["anchors"], 0).astype(int)
        checks["connection"] = bool(hits[0] > 0 and hits[0] == hits[1])
        checks["lumen_core"] = core_coverage >= .8
        checks["no_false_addition"] = far <= 1.
        checks["intact_preserved"] = not bool(z["intact"]) or changed == 0
        metrics.update(changed_voxels=changed, core_coverage=core_coverage, far_added_mm3=far)
    except Exception as e:
        errors["mask"] = str(e)
    try:
        line = np.load(answer / "centerline.npy", allow_pickle=False)
        assert line.ndim == 2 and line.shape[1] == 3 and 5 <= len(line) <= 3000 and np.isfinite(line).all(), "path format"
        ds = np.linalg.norm(np.diff(line, axis=0), axis=1)
        length = ds.sum()
        rlen = np.linalg.norm(np.diff(ref, axis=0), axis=1).sum()
        distance = cKDTree(ref).query(line)[0]
        coverage = float((cKDTree(line).query(ref)[0] <= 1.2).mean())
        endpoint = float(np.linalg.norm(line[[0, -1]] - z["anchors"], axis=1).max())
        p95 = float(np.percentile(distance, 95))
        checks["route_geometry"] = bool(p95 <= 1.2 and coverage >= .9 and endpoint <= 1.
                and abs(length / rlen - 1) <= .2 and ds.max() <= .75 and ds.min() >= .05)
        assert mask is not None
        outside = ndi.distance_transform_edt(~mask, sampling=sp)
        checks["route_in_mask"] = bool((sample(outside, aff, line) <= .5).mean() >= .99)
        metrics.update(route_p95_mm=p95, reference_coverage=coverage, length_mm=float(length), endpoint_error_mm=endpoint)
    except Exception as e:
        errors["route"] = str(e)
    try:
        assert line is not None
        c = np.load(answer / "cpr.npz", allow_pickle=False)
        xyz, hu, angles, offsets, arc = (c[k] for k in ["source_ras_mm", "hu", "angles_deg", "offsets_mm", "arc_mm"])
        assert xyz.shape == (8, len(line), 65, 3) and hu.shape == xyz.shape[:-1]
        assert np.isfinite(xyz).all() and np.isfinite(hu).all() and np.isfinite(arc).all()
        assert np.allclose(angles, np.arange(0, 360, 45)) and np.allclose(offsets, np.arange(-8, 8.001, .25))
        t = np.gradient(line.astype(float), axis=0)
        t /= np.linalg.norm(t, axis=1)[:, None]
        axis = np.eye(3)[np.argmin(np.abs(t[0]))]
        n = axis - axis.dot(t[0]) * t[0]
        n /= np.linalg.norm(n)
        normals = [n]
        for i in range(1, len(t)):
            cross = np.cross(t[i-1], t[i])
            sine = np.linalg.norm(cross)
            cosine = np.clip(t[i-1].dot(t[i]), -1, 1)
            if sine > 1e-10:
                n = Rotation.from_rotvec(cross / sine * np.arctan2(sine, cosine)).apply(n)
            n = n - n.dot(t[i]) * t[i]
            n /= np.linalg.norm(n)
            normals.append(n)
        normals = np.array(normals)
        bins = np.cross(t, normals)
        directions = np.cos(np.deg2rad(angles))[:, None, None] * normals + np.sin(np.deg2rad(angles))[:, None, None] * bins
        expected = line[None, :, None, :] + directions[:, :, None, :] * offsets[None, None, :, None]
        coord_error = float(np.linalg.norm(xyz - expected, axis=-1).max())
        hu_error = float(np.percentile(np.abs(hu - sample(z["image"], aff, xyz, cval=-1024)), 99))
        arc_error = float(np.max(np.abs(arc - np.r_[0., np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))])))
        checks["CPR"] = coord_error <= .02 and hu_error <= .2 and arc_error <= .1
        metrics.update(cpr_coordinate_error_mm=coord_error, cpr_HU_p99_error=hu_error, cpr_arc_error_mm=arc_error)
    except Exception as e:
        errors["CPR"] = str(e)
    anatomy = all(checks.get(k, False) for k in ["format", "preservation", "connection", "lumen_core", "no_false_addition", "intact_preserved", "route_geometry", "route_in_mask"])
    return {"anatomy": anatomy, "CPR": checks.get("CPR", False), "checks": checks, "metrics": metrics, "errors": errors}


def score(answer, truth):
    cases = {p.name: score_case(Path(answer) / p.name, p / "reference.npz") for p in sorted(Path(truth).iterdir())}
    return {"reward": int(all(c["anatomy"] and c["CPR"] for c in cases.values())),
            "anatomy_pass": all(c["anatomy"] for c in cases.values()),
            "CPR_pass": all(c["CPR"] for c in cases.values()), "cases": cases, "limits": LIMITS}


if __name__ == "__main__":
    answer = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/answer")
    truth = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/verifier/truth")
    result = score(answer, truth)
    print(json.dumps(result, indent=2))
    if len(sys.argv) == 1:
        out = Path("/logs/verifier")
        out.mkdir(parents=True, exist_ok=True)
        (out / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
        (out / "reward.txt").write_text(str(result["reward"]) + "\n")
