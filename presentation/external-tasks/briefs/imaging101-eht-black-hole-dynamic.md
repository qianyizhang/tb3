# Reconstruct a changing black-hole image

Recover **12 brightness frames, each 30×30 pixels**, from the released synthetic
radio-interferometry measurements of a rotating crescent.

## Value

Changing telescope coverage and changing source brightness both change the
measurements. A temporal model shares information across sparse snapshots.

## Given

### Original data

28 complex visibilities per frame, with baseline coordinates, station pairs and
noise estimates. Twelve epochs span **0–6 hours**; eight EHT-inspired stations
provide **336 complex measurements** in total. This is a synthetic source,
not an observed movie of Sgr A*.

### Supplied helpers

Metadata specifies the grid, time stamps and 2 Jy source flux. **All L1–L3 copy
`data/ground_truth.npz` into the solver workspace.** L2 adds an algorithmic
approach; L3 adds software design. Source code and evaluation outputs are not seeded.

### Callable tools

Python and declared numerical dependencies. The audit used existing NumPy for
small fixtures and saved-array controls; no reconstruction or installation ran.

### Reference-only material

Saved static and StarWarps reconstructions, fixtures and historical notebook
outputs support comparison. The supplied reference video itself is solver-visible;
a reader reveal does not create a private evaluation boundary.

## Task specification

For each time, map brightness to complex Fourier samples with the supplied
baseline geometry. Couple neighboring images through a Gaussian Markov model:
a parameterized warp predicts the next image, with process noise allowing change.
StarWarps alternates forward/backward inference and warp optimization. The current
source defaults to **four affine parameters without translation**.

## Expected output

One `output/reconstruction.npy`, shape **(12, 30, 30)**, in **Jy/pixel** and original
time order. Pixels span **3.4 μas**, giving a 102 μas field. Each frame has 900 real
unknowns but only 56 real measurement components. The native solver API also
returns uncertainty and warp parameters; the released output arrays and live
local scorer cover the video.

## Evaluation

| Saved-array replay | Mean native NCC ↑ | Mean native NRMSE ↓ |
|---|---:|---:|
| Independent static frames | 0.850741 | 0.070963 |
| StarWarps | 0.881699 | 0.063803 |
| Oracle time-average image repeated | 0.986929 | 0.018853 |

The native report averages framewise centered correlation and range-normalized
error. The oracle control uses the answer and has **no motion**; its high scores
show that similarity alone does not establish correct dynamics.

The local generic scorer instead uses video-wide cosine correlation and error:
StarWarps **NCC 0.882934 / NRMSE 0.063114**. Published pass thresholds are absent.
The older runner fallback requires a 2D image; cross-runner equivalence is unverified.

## Visual explanation

### Workflow

- Inspect native Fourier coverage and time-indexed visibility measurements.
- Follow the temporal prior and compare retained static and dynamic videos.
- Reveal the supplied reference, motion diagnostics and scoring controls.

### Input

Show the 28 native u/v points at each epoch in wavelengths. Conjugate points,
if shown, are derived and do not increase the measurement count.

### Supplied helpers

Label the Gaussian prior, warp and process noise as modeling choices. The generator's
complex-RMS noise convention differs by a factor of two in variance from the
source helper's real/imaginary covariance; retain that discrepancy.

### Reference or output

Preserve all twelve frames, the native grid and a common Jy/pixel scale. Use array
coordinates with row zero at the bottom, matching the source plots. A descriptive
brightness-direction diagnostic changes **57.88°** for saved StarWarps and **90°**
for truth; this is not a fitted warp or an astrophysical position angle.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data including reference, requirements. | Implement reconstruction; reference copying is possible. |
| L2 · + approach | L1 plus temporal-model and EM guidance. | Design and implement the method. |
| L3 · + design | L2 plus interfaces and numerical details. | Implement the specified design. |

## Difficulty

Sparse sampling makes priors consequential. Better image scores, smoother motion
and correct dynamics are separate properties; one synthetic example cannot
establish general superiority or blind reconstruction ability.

## Sources

- [Pinned task and array contract](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_dynamic/README.md)
- [Pinned temporal solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_dynamic/src/solvers.py)
- [Pinned generator and noise convention](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_dynamic/src/generate_data.py)
- [Pinned generic scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [StarWarps paper, v2](https://arxiv.org/abs/1711.01357v2)
- [Canonical story](../stories/imaging101-eht-dynamic.story.md)
- [Source audit, controls and provenance](../sources/imaging101-eht-dynamic-audit.json)

## Coverage

13 task sources, 60 shared sources and all 18 released assets verified. Eight
fixture archives, original per-frame scores, saved-video controls and L1–L3
staging were checked. Two fixtures lack complete inputs for exact replay.

## Gaps

Pinned `main.py` has a syntax error at line 31. Original output arrays and scores
remain unchanged; no fresh EM execution or benchmark pass is claimed. The canonical
story preserves all twelve epochs, the oracle controls and these source limits.
The completion ledger records export and visual-review evidence separately.
