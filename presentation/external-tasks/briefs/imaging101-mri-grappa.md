# Reconstruct multi-coil MRI with GRAPPA

Implement a computational method to reconstruct multi-coil MRI with GRAPPA.

> **Actual gap:** Native full eight-coil k-space and phantom truth are solver-visible; R=2/20-line ACS undersampling is a supplied rule, not raw missing data. No participant reconstruction or performance is shown. [Official pinned acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_grappa).

## Value

This imaging problem tests the computational step between acquired measurements and an interpretable image or physical-property map.

## Given

### Original data

Native fully sampled synthetic complex k-space and Gaussian sensitivity maps: 1×128×128×8 float32 real/imag arrays. Source preprocessing defines R=2 even phase-encode rows plus ACS 54–73; 74/128 retained lines, not raw missing data.

### Supplied helpers

An autocalibration region that teaches missing-sample interpolation. The assistance level can add an approach and software design.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

Full eight-coil k-space, sensitivity maps and phantom truth are solver-visible in data. Source main compares fully sampled RSS, a different intensity reference from the bare phantom. Teaching reveal does not establish blind evaluation.

## Task specification

Implement the linked README’s forward/inverse problem with its array conventions and units. The expected artifact below describes the scientific result; the selected harness mode owns exact filenames and callable signatures.

## Expected output

Generic output/reconstruction.npy: one real 128×128 magnitude image. Source main instead writes grappa_reconstruction.npz key reconstruction with 1×128×128 batch and compares fully sampled RSS. No participant result is shown.

## Evaluation

The filesystem generic route prefers evaluation/reference_outputs/ground_truth.npy (full-data RSS) before data/ground_truth.npz (bare phantom). It compares 16384 pixels without flux scaling: range NRMSE returns infinity for zero reference range and cosine uses epsilon 1e-30. The task-local helper also returns infinity for zero range, uses cosine epsilon 1e-12 and skimage local SSIM; generic SSIM uses whole-image moments. The no-filesystem fallback instead flux-normalizes output and uses relative L2 NRMSE against a 2D NPY reference. Nested saved source metrics supply no top-level pass thresholds. No route was executed and no metric result is shown.

## Visual explanation

### Workflow

- Native full eight-coil k-space; supplied R2/ACS20 rule
- Reconstruct multi-coil MRI with GRAPPA
- Expected magnitude-image contract after k-space completion and coil combination; no image submitted

### Input

**Native full source array samples; supplied mask illustrated separately.** Native fully sampled synthetic complex k-space and Gaussian sensitivity maps: 1×128×128×8 float32 real/imag arrays. Source preprocessing defines R=2 even phase-encode rows plus ACS 54–73; 74/128 retained lines, not raw missing data.

### Supplied helpers

**Given material, not an answer reveal.** An autocalibration region that teaches missing-sample interpolation. The assistance level can add an approach and software design.

### Reference or output

**Expected artifact, not an actual prediction.** Generic output/reconstruction.npy: one real 128×128 magnitude image. Source main instead writes grappa_reconstruction.npz key reconstruction with 1×128×128 batch and compares fully sampled RSS. No participant result is shown.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Calibrate the interpolation from the available center region and respect coil/sample indexing.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_grappa/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native full eight-coil k-space and phantom truth are solver-visible; R=2/20-line ACS undersampling is a supplied rule, not raw missing data. No participant reconstruction or performance is shown. Choose method reproduction or blind reconstruction; stage only undersampled k-space/ACS for blind work, isolate full data/truth, pin RSS versus phantom reference and output/scorer semantics.
