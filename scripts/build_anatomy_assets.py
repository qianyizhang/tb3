"""Build compact teaching meshes from retained public masks; never run segmentation.

Optional authoring environment: numpy, nibabel, scipy, scikit-image and VTK.
Normal Explorer builds only read the checked-in mesh JSON files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage
from skimage.measure import marching_cubes
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData
from vtkmodules.vtkFiltersCore import vtkQuadricDecimation, vtkWindowedSincPolyDataFilter

TARGETS = {
    "liver": 1800,
    "kidney_left": 1400,
    "kidney_right": 1400,
    "spleen": 1200,
    "pancreas": 1400,
    "stomach": 1400,
    "gallbladder": 700,
    "heart": 2000,
    "lung_upper_lobe_left": 1200,
    "lung_lower_lobe_left": 1200,
    "lung_upper_lobe_right": 1200,
    "lung_middle_lobe_right": 800,
    "lung_lower_lobe_right": 1200,
    "aorta": 1600,
    "trachea": 1000,
    "pulmonary_vein": 1600,
    "vertebrae_L3": 1600,
    "prostate": 1200,
}


def make_mesh(path: Path, budget: int) -> tuple[dict, dict]:
    image = nib.load(path)
    mask = np.asanyarray(image.dataobj) > 0
    components, count = ndimage.label(mask)
    if count == 0:
        raise ValueError(f"Empty source mask: {path}")
    sizes = np.bincount(components.ravel())
    sizes[0] = 0
    mask = components == sizes.argmax()
    indices = np.argwhere(mask)
    low, high = indices.min(0), indices.max(0)
    clipped = bool(np.any(low == 0) or np.any(high == np.asarray(mask.shape) - 1))
    if clipped:
        raise ValueError(f"Truncated organ is unsuitable as a common asset: {path}")
    crop = mask[tuple(slice(a, b + 1) for a, b in zip(low, high, strict=True))]
    field = ndimage.gaussian_filter(np.pad(crop.astype(np.float32), 2), 0.65)
    vertices, faces, _, _ = marching_cubes(field, 0.5, allow_degenerate=False)
    vertices += low - 2
    # Explicit affine transform avoids platform BLAS warnings for small matrices.
    vertices = (
        sum(vertices[:, j, None] * image.affine[:3, j] for j in range(3)) + image.affine[:3, 3]
    )
    points = vtkPoints()
    points.SetData(numpy_to_vtk(vertices, deep=True))
    cells = vtkCellArray()
    cells.SetCells(
        len(faces),
        numpy_to_vtkIdTypeArray(
            np.c_[np.full(len(faces), 3), faces].astype(np.int64).ravel(), deep=True
        ),
    )
    poly = vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    smooth = vtkWindowedSincPolyDataFilter()
    smooth.SetInputData(poly)
    smooth.SetNumberOfIterations(15)
    smooth.SetPassBand(0.1)
    smooth.BoundarySmoothingOff()
    smooth.FeatureEdgeSmoothingOff()
    smooth.NormalizeCoordinatesOn()
    smooth.Update()
    simplify = vtkQuadricDecimation()
    simplify.SetInputConnection(smooth.GetOutputPort())
    simplify.SetTargetReduction(max(0, 1 - budget / smooth.GetOutput().GetNumberOfCells()))
    simplify.VolumePreservationOn()
    simplify.Update()
    result = simplify.GetOutput()
    v = np.round(vtk_to_numpy(result.GetPoints().GetData()), 2)
    f = vtk_to_numpy(result.GetPolys().GetData()).reshape(-1, 4)[:, 1:]
    data = {"vertices": v.tolist(), "faces": f.tolist()}
    simplify.SetTargetReduction(
        max(0, 1 - min(300, budget * 0.22) / smooth.GetOutput().GetNumberOfCells())
    )
    simplify.Update()
    small = simplify.GetOutput()
    small_v = np.round(vtk_to_numpy(small.GetPoints().GetData()), 2)
    small_f = vtk_to_numpy(small.GetPolys().GetData()).reshape(-1, 4)[:, 1:]
    data["lod"] = {"vertices": small_v.tolist(), "faces": small_f.tolist()}
    receipt = {
        "source": str(path),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "shape": list(image.shape),
        "affine": image.affine.tolist(),
        "source_components": count,
        "retained_component_voxels": int(mask.sum()),
        "truncated_at_image_boundary": clipped,
        "vertices": len(v),
        "triangles": len(f),
        "assembly_triangles": len(small_f),
    }
    return data, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    receipts = {}
    for name, budget in TARGETS.items():
        case = "s1336" if name == "prostate" else "s1233"
        source = args.source_root / case / "segmentations" / f"{name}.nii.gz"
        data, receipt = make_mesh(source, budget)
        data.update({"id": name, "source_case": case, "coordinates": "RAS millimetres"})
        target = args.output / f"{name}.json"
        target.write_text(json.dumps(data, separators=(",", ":")) + "\n")
        receipt["asset_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        receipt["bytes"] = target.stat().st_size
        receipts[name] = receipt
        print(name, receipt["triangles"], receipt["bytes"], flush=True)
    manifest = {
        "source": "TotalSegmentator v2.0.1 retained public source masks",
        "source_url": "https://zenodo.org/records/10047263",
        "attribution": "Jakob Wasserthal and the TotalSegmentator contributors, University Hospital Basel",
        "terms": "CC BY 4.0 dataset attribution; retained label-source receipt also records Apache-2.0.",
        "derivation": "Largest connected component; Gaussian smoothing sigma 0.65 voxels; marching cubes 0.5; 15 windowed-sinc iterations, passband 0.1; quadric triangle reduction; coordinates rounded to 0.01 mm. Display assets only, not evaluation references.",
        "assets": receipts,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
