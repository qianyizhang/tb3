# Estimate uncertainty in a black-hole image

Infer a distribution of **32×32 radio-brightness images** from sparse
interferometric measurements in the bundled DPI example.

## Value

Different images can explain similar telescope measurements. Their variation
helps describe ambiguity under the chosen likelihood, prior and model.

## Given

### Original data

938 complex visibilities, 465 closure phases and 485 log closure amplitudes;
nine stations and 100 timestamps. A visibility samples one spatial frequency.
Closure combinations cancel multiplicative station gains, but retain noise.

### Supplied helpers

Baseline coordinates, noise estimates and 160 μas field-of-view metadata.
**All L1–L3 expose the supplied reference image**, including `ground_truth.npz`
and `gt.fits`. L2 adds an approach; L3 adds software design.

### Callable tools

Python, PyTorch and declared Fourier dependencies. Existing NumPy/CPU PyTorch
replayed fixed controls; no installation, network training or sampling occurred.

### Reference-only material

Saved posterior arrays and fixtures are not seeded. The reference image is
solver-visible; a reader reveal is not an evaluator privacy boundary.

## Task specification

Approximate an image distribution with a Real-NVP flow. Balance closure-data
agreement, image priors and an entropy term. Use degrees for phase and natural
logarithms for amplitude ratios; source indices determine baseline order.

## Expected output

Native output: image samples, mean and population standard deviation in Jy/pixel
on a 32×32 grid, **5 μas/pixel**. The local end-to-end harness instead requests
one `output/reconstruction.npy` and does not assess posterior uncertainty.

## Evaluation

| Saved mean replay | NCC | NRMSE |
|---|---:|---:|
| Task-native helper | 0.656499 | 0.134476 |
| Local generic scorer | 0.714299 | 0.090637 |

Definitions differ: native scoring peak-normalizes and centers correlation;
generic scoring uses absolute intensity and cosine similarity. Neither score
checks uncertainty. No current pass thresholds are published.

**180/1,024 reference pixels** fall within saved mean ± one standard deviation.
This single-image containment is not proof of calibration. The mean/std match
all 1,024 images in `posterior_samples.npy`; the similarly named
`posterior_samples_1024.npy` contains a different set.

## Visual explanation

### Workflow

- Inspect native Fourier coverage and closure measurements.
- Follow station-gain cancellation, priors and stored image samples.
- Reveal reference comparisons and the limits of uncertainty scoring.

### Input

Retain the native u/v coordinates in wavelengths. Derived conjugate points are
not additional observations. Closure rows are not independent repeated trials.

### Supplied helpers

Distinguish the retained 2.044481 Jy prior target from the current source's
0.273831 Jy target. The former uses the APEX–ALMA baseline; the latter takes
the median over all visibilities.

### Reference or output

Use saved sample rows in their original order, without claiming a time sequence.
Display relative RA decreasing left-to-right and Dec increasing bottom-to-top.
Label sample spread, absolute error and the supplied reference separately.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data including reference, requirements. | Implement inference; reference copying is possible. |
| L2 · + approach | L1 plus flow, likelihood and prior guidance. | Design and implement the method. |
| L3 · + design | L2 plus interfaces and numerical details. | Implement the specified design. |

## Difficulty

Sparse nonlinear constraints permit ambiguity. Truth exposure prevents a blind
reconstruction claim; sample diversity alone does not establish a calibrated posterior.

## Sources

- [Pinned task and array contract](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_UQ/README.md)
- [Pinned preprocessing](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_UQ/src/preprocessing.py)
- [Pinned generic scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Original DPI example](https://github.com/HeSunPU/DPI/tree/1bf3f02a92796af737bd6fe6233d1d0dd778ffd5/dataset/interferometry1)
- [DPI paper, v2](https://arxiv.org/html/2010.14462v2)
- [Source audit, controls and provenance](../sources/imaging101-eht-uq-audit.json)

## Coverage

One bundled example: 14 task sources, 60 shared sources, three upstream sources
and 28 assets verified. Both FITS files match the original DPI example exactly.
Fixed closure/loss controls, saved-array statistics and L1–L3 staging were replayed.

## Gaps

The task's real-2015-observation claim remains unverified. `main.py` has a syntax
error; its solver expects an obsolete `obs` object absent from current preprocessing.
Prior flux also differs from retained fixtures. The unavailable NUFFT runtime
prevents replaying forward fixtures; no astrophysical or agent success is claimed.
Explainer acceptance is recorded separately in the completion ledger.
