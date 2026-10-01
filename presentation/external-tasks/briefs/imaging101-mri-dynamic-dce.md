# Reconstruct a contrast-enhanced MRI time series

Implement a computational method to reconstruct a contrast-enhanced MRI time series.

> **Actual gap:** Native synthetic k-space/masks are present, but source truth is solver-visible; generator defaults differ from the retained 15% acquisition. No participant reconstruction or perfusion result is shown. [Pinned official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_dynamic_dce).

## Value

This imaging problem tests the computational step between acquired measurements and an interpretable image or physical-property map.

## Given

### Original data

Matching native **synthetic complex64 k-space and float32 binary masks** over 20 time frames, not patient acquisition. Each 128×128 frame retains 2457/16384 frequency cells; masks are distinct and include a central 10×10 square. Time is float32 seconds 0–60; no coil axis/sensitivities, physical spacing or anatomical orientation is established.

### Supplied helpers

Sampling information and a temporal-regularization model. The assistance level can add an approach and software design.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

data/ground_truth.npz is copied with solver-visible data. Synthetic reference images are initially covered in teaching, with explicit reveal/reset; this does not establish solver-blind evaluation.

## Task specification

Reconstruct a **real magnitude sequence**, preserving native time/grid order after removing the supplied batch axis. The declared model is framewise masked centered orthonormal Fourier encoding with complex sampled-point noise; no Fourier operator is executed here. Retained metadata is 15% / noise 0.005, whereas generator defaults are 25% / 0.02; seed 42 is a source default, not a newly verified retained acquisition history.

Generator comments call gamma-variate uptake curves concentration, but executable code adds them to arbitrary phantom intensity. No signal-to-mM calibration, T1/relaxivity/sequence mapping, arterial input function, Tofts/Ktrans fit or physiological parameter is established. Source pixel (49,79) is a public synthetic truth series, not a participant reconstruction, ROI average or clinical kinetic result.

Executable main selects temporal-TV **PGD**, lambda 0.001 / max 200 / tol 1e-5, despite an ADMM header; source function defaults differ. Proximal steps act on complex temporal differences, with final magnitude output, despite magnitude-only prose. The 20-frame sequence has 19 adjacent differences, without division by elapsed seconds; this is not a concentration derivative.

## Expected output

Generic output/reconstruction.npy: one real 20×128×128 magnitude sequence. Task main instead saves source tv_reconstruction.npz with key reconstruction in evaluation/reference_outputs. No participant output is shown.

## Evaluation

Generic scoring averages **327,680 array entries** for global MSE and range-normalized RMSE; NCC is uncentered cosine over the full magnitude volume. Source visualization also reports per-frame errors over 16,384 pixels and a 20-frame mean; that average differs from one global error. Source zero-range NRMSE returns 0 while generic scoring gives infinity. Source numeric PSNR/zero-norm conventions also differ. Shape-based reference discovery favors dynamic_images after squeezing batch; the 20-entry time axis is not an image reference. Retained tree has metrics_detail but no top-level metrics.json boundary file. No metric, pass/fail or participant performance is computed.

Filesystem scoring discovers data/ground_truth.npz and squeezes the four-dimensional dynamic_images array to (20,128,128); time_points (20,) cannot match this output. No-filesystem scoring instead requires generic ground_truth.npy under reference_outputs or data, absent from the pinned DCE listing; the saved TV NPZ is not a substitute for that filename. Staged files and scorer route must be pinned before any verdict.

## Visual explanation

### Workflow

- Undersampled MRI frequency measurements over time
- Reconstruct a contrast-enhanced MRI time series
- A dynamic MRI image sequence

### Input

**Native synthetic input.** Raw complex64 k-space and float32 masks have shape 1×20×128×128; loader removes batch axis. Each frame samples 2457/16384 points (14.9963%), with native order preserved; time spans 0–60 seconds. No coil axis, sensitivities, physical spacing or patient geometry.

### Supplied helpers

**Given material, not an answer reveal.** Sampling information and a temporal-regularization model. The assistance level can add an approach and software design.

### Reference or output

**Expected artifact, not an actual prediction.** Generic output/reconstruction.npy: one real 20×128×128 magnitude sequence. Task main instead saves source tv_reconstruction.npz with key reconstruction in evaluation/reference_outputs. No participant output is shown.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Strong temporal smoothing can hide the contrast changes the scan was intended to measure.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_dynamic_dce/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native synthetic k-space/masks are present, but source truth is solver-visible; generator defaults differ from the retained 15% acquisition. No participant reconstruction or perfusion result is shown. Choose blind inversion or source-method reproduction; isolate source truth if blind, preserve 15%/0.005 retained acquisition, pin real 20×128×128 output and exact evaluator/reference before scoring.

## Retained source and reader boundary

Historical acquisition objects remain unchanged, including absent timestamps. Actual UTC attempts describe retained validation only. Native masks may be losslessly bit-packed for display; decoding must preserve every frame/row/column bit and complex center sample. Source image truth is exposed only by a later explicit helper request; backward replay, exit and shared global reset cover it before paint. Source truth is already solver-visible, so teaching coverage does not establish privacy or blind inversion. No source operator, Fourier transform, solver, scorer or model is executed.
