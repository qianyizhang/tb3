# Estimate diffusion tensors from MRI

Fit diffusion tensors from **31 signal volumes of a synthetic 128×128 phantom**;
derive fractional anisotropy (FA) and mean diffusivity (MD).

## Value

FA describes directional preference; MD describes average diffusion magnitude.
This synthetic example does not establish clinical validity.

## Given

### Original data

`raw_data.npz`: float32 signals `(1,128,128,31)`, b-values `(31,)` and gradient
vectors `(31,3)`. One volume has b=0; 30 have b=1000 s/mm². Metadata declares
Rician noise σ=0.02 and 1.71875 mm pixels over 220 mm.

### Supplied helpers

Gradient table and metadata. **All L1–L3 expose truth FA, MD, tensors and the
7,186-pixel tissue mask**. The source baseline fits inside this supplied mask.
L2 adds an approach; L3 adds software design.

### Callable tools

Python and declared numerical dependencies. This audit used existing NumPy;
no installation or agent trial.

### Reference-only material

Truth and mask are solver-visible. Saved OLS/WLS outputs and function fixtures
are not seeded. A reader reveal does not imply a private evaluator.

## Task specification

Use `S = S0 exp(−b gᵀDg)`. The audited 31×7 log-signal matrix has rank 7.
Fit `[ln S0,Dxx,Dxy,Dxz,Dyy,Dyz,Dzz]` by OLS or weighted least squares;
derive FA/MD from eigenvalues.

## Expected output

Native files contain six tensor components `(1,128,128,6)` in mm²/s, FA
`(1,128,128)` dimensionless and MD `(1,128,128)` in mm²/s. The local generic
harness instead requests one `output/reconstruction.npy`.

## Evaluation

| Saved method | Masked FA NCC | Masked FA NRMSE |
|---|---:|---:|
| OLS | 0.997834 | 0.061319 |
| WLS | 0.998025 | 0.058487 |

Saved-array replays cover **7,186/16,384 pixels**, not agent results.
The task-specific helper checks FA only: zero MD/tensors do not affect its score.
The local generic scorer includes background and selects **FA even for a correct
MD map**. Its WLS FA NRMSE is 0.038734. The fallback without a host workspace
cannot find the required `.npy` truth. **No thresholds file is published**;
notebook boundaries are historical. See the audit for controls and exact dispatch.

## Visual explanation

### Workflow

- Inspect native signals and supplied gradients.
- Follow one pixel through fitting and tensor eigendecomposition.
- Reveal saved maps, reference comparisons and scoring limits.

### Input

Native arrays retain their 128×128 grid. The canonical story selects four
signal volumes and five post-hoc pixels with their source coordinates.

### Supplied helpers

Use source tensor x/y/z axes and image row/column coordinates. No anatomical
affine is supplied. Label the truth mask as supplied help.

### Reference or output

Saved maps agree with their tensor-derived values within float32 precision.
The audit retains notebook probe-label errors and a principal-axis rotation
mismatch. Use array-verified probes and axes when illustrating the result.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data including truth/mask, requirements. | Implement fitting; reference copying is possible. |
| L2 · + approach | L1 plus OLS/WLS method. | Implement fitting and scalar-map derivation. |
| L3 · + design | L2 plus interfaces and numerical details. | Implement the specified design. |

## Difficulty

Noisy directional signals must determine six components and a baseline intensity.
The truth-exposed condition does not establish blind reconstruction difficulty.

## Sources

- [Pinned task and array contract](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/diffusion_mri_dti/README.md)
- [Pinned fitting implementation](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/diffusion_mri_dti/src/solvers.py)
- [Pinned generic reference selection](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Canonical story](../stories/imaging101-dti.story.md)
- [Source audit, controls and provenance](../sources/imaging101-dti-audit.json)

## Coverage

One synthetic phantom; 13 task sources, 60 shared sources and 13 assets verified.
Eight helper fixtures and five post-hoc selected pixels replayed; no full-image
fit, phantom generation or patient study.

## Gaps

One synthetic phantom and saved fits do not establish clinical accuracy or agent
capability. Truth is exposed, evaluator scopes differ and current pass thresholds
are unavailable. The canonical story preserves these limits; explainer acceptance
is recorded in the completion ledger.
