"""Input-legal development solver; image/mask ablation share all other steps."""
import argparse
import json
from pathlib import Path
import sys
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "probes/vessel-geometry/authoring"))
from geometry import transform, resample_path, frames, cpr_coordinates, sample, mesh_from_mask
from compare_local_routes import solve
from build_cases import medial_path


def exports(out, mask, affine, im, route):
    out.mkdir(parents=True, exist_ok=True)
    line, _ = resample_path(route, .4, .35)
    arc = np.r_[0., np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))]
    _, n, b = frames(line)
    angles = np.arange(0, 360, 45.)
    offsets = np.arange(-8, 8.001, .25)
    xyz = cpr_coordinates(line, n, b, angles, offsets)
    np.save(out / "centerline.npy", line)
    np.savez_compressed(out / "cpr.npz", hu=sample(im, affine, xyz), source_ras_mm=xyz,
                        angles_deg=angles, offsets_mm=offsets, arc_mm=arc)
    nib.save(nib.Nifti1Image(mask.astype("uint8"), affine), out / "corrected_mask.nii.gz")
    mesh_from_mask(mask, affine).export(out / "airways.ply")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--mask-only", action="store_true")
    p.add_argument("--oracle", type=Path)
    p.add_argument("--repair-radius-mm", type=float, default=1.2)
    p.add_argument("--repair-threshold-HU", type=float, default=-500.)
    p.add_argument("--gap-only", action="store_true")
    a = p.parse_args()
    for src in sorted(a.input.iterdir()):
        ni = nib.load(src / "image.nii.gz")
        im = np.asarray(ni.dataobj)
        pr = np.asarray(nib.load(src / "proposed_mask.nii.gz").dataobj) > 0
        edit = np.asarray(nib.load(src / "editable_region.nii.gz").dataobj) > 0
        req = json.loads((src / "request.json").read_text())
        aff = ni.affine
        sp = nib.affines.voxel_sizes(aff)
        ends = np.rint(transform(np.array([req["start_ras_mm"], req["end_ras_mm"]]), np.linalg.inv(aff))).astype(int)
        cc, _ = ndi.label(pr, np.ones((3, 3, 3)))
        hit = cc[tuple(ends.T)]
        fixed = pr.copy()
        if a.oracle:
            fixed = np.asarray(nib.load(a.oracle / src.name / "oracle_mask.nii.gz").dataobj) > 0
        elif hit[0] == 0 or hit[0] != hit[1]:
            path = solve(im, pr, sp, ends[0], ends[1], not a.mask_only)
            assert path is not None
            seed = np.zeros(pr.shape, bool)
            seeds = path[~pr[tuple(path.T)]] if a.gap_only else path
            seed[tuple(seeds.T)] = True
            close = ndi.distance_transform_edt(~seed, sampling=sp) <= a.repair_radius_mm
            supported = np.ones(pr.shape, bool) if a.mask_only else im < a.repair_threshold_HU
            fixed |= close & supported & edit
        line = medial_path(fixed, sp, ends[0], ends[1])
        exports(a.output / src.name, fixed, aff, im, transform(line, aff))
        print(src.name, "added", int((fixed & ~pr).sum()), flush=True)
