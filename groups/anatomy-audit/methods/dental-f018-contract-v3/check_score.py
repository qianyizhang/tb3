"""Small discriminating controls for independent geometry and identity metrics."""

import importlib.util
import json
import tempfile
from pathlib import Path

import nibabel as nib
import numpy as np

spec = importlib.util.spec_from_file_location("dental_score", Path(__file__).with_name("score.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    allowed = (
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 103, 104, 105]
        + module.TEETH
        + [k + 100 for k in module.TEETH]
    )
    labels = {str(k): str(k) for k in allowed}
    data = np.zeros((len(allowed) * 4, 6, 6), dtype=np.uint8)
    for i, k in enumerate(allowed[1:]):
        data[i * 4 : i * 4 + 2, 1:3, 1:3] = k
    affine = np.diag([0.3, 0.3, 0.3, 1])
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        gt = folder / "gt.nii.gz"
        nib.save(nib.Nifti1Image(data, affine), gt)

        def measure(a, grid=affine):
            path = folder / "answer.nii.gz"
            nib.save(nib.Nifti1Image(a, grid), path)
            return module.score(path, gt, labels)

        exact = measure(data)
        assert exact["valid"] and exact["macro_dice"] == 1
        assert exact["whole_tooth_geometry_and_identity"]["fdi_correct_among_detected"] == 1
        assert all(m["hd95_mm"] == 0 for m in exact["canal_surface_metrics"].values())
        empty = measure(np.zeros_like(data))
        assert empty["valid"] and empty["macro_dice"] == 0
        assert (
            empty["whole_tooth_geometry_and_identity"]["geometry_mean_dice_with_unmatched_zero"]
            == 0
        )
        swapped = data.copy()
        for k in module.TEETH:
            q, i = divmod(k, 10)
            dest = {1: 2, 2: 1, 3: 4, 4: 3}[q] * 10 + i
            swapped[data == k] = dest
            swapped[data == k + 100] = dest + 100
        swap = measure(swapped)
        assert (
            swap["whole_tooth_geometry_and_identity"]["geometry_mean_dice_with_unmatched_zero"] == 1
        )
        assert swap["whole_tooth_geometry_and_identity"]["fdi_correct_among_detected"] == 0
        merged = data.copy()
        for k in module.TEETH:
            merged[data == k + 100] = k
        merge = measure(merged)
        assert (
            merge["whole_tooth_geometry_and_identity"]["geometry_mean_dice_with_unmatched_zero"]
            == 1
        )
        assert merge["groups"]["pulp"]["macro_dice"] == 0
        shifted = affine.copy()
        shifted[0, 3] = 1
        assert not measure(data, shifted)["valid"]
        assert not measure(data[:-1])["valid"]
        unknown = data.copy()
        unknown[0, 0, 0] = 99
        assert not measure(unknown)["valid"]
        fractional = data.astype(float)
        fractional[0, 0, 0] = 0.5
        assert not measure(fractional)["valid"]
        assert module.score(folder / "missing.nii.gz", gt, labels)["reason"] == "missing_output"
        print(
            json.dumps(
                {
                    "passed": [
                        "exact",
                        "empty",
                        "identity_swapped_geometry_preserved",
                        "pulp_merged_geometry_preserved",
                        "wrong_affine",
                        "wrong_shape",
                        "unknown_label",
                        "fractional_label",
                        "missing_output",
                    ],
                    "identity_swap_macro": swap["macro_dice"],
                    "pulp_merge_macro": merge["macro_dice"],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
