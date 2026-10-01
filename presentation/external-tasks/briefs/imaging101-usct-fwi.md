> **Numerical phantom observations; true speed, calibrated pressure and participant output absent. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/usct_FWI).**

# Trace frequency-domain USCT without inventing a speed reconstruction

Native numerical phantom observations and source-pinned inversion rules; participant outcome empty.

## Given

### Original data

Pinned task usct_FWI, numerical breast phantom, not patient or paper volunteer data. raw_data.npz: twenty complex64 dobs_0.3 through dobs_1.25 MHz arrays, each (1, 256, 256): batch, receiver, source. 65,536 receiver–source pairs per frequency; 1,310,720 complex cells. receiver_ix / receiver_iy float32 (1, 256), 1-indexed grid positions, also used as transmitters. Values are complex frequency observations, not measured time RF, calibrated Pa, clinical tissue maps or scanner acquisition evidence. No sample interval, pulse waveform, noise distribution or time window defined.

### Supplied helpers

Metadata grid 480 × 480, spacing 50 µm, background 1480 m/s, bounds 1300–1700 m/s, 256 active of 512 ring transducers, subsample factor 2. Twenty frequencies 0.3–1.25 MHz in 0.05 steps. Metadata domain_size_cm=[24,24] conflicts with 480 × 50 µm = 24 mm = 2.4 cm; centre span 479 × 50 µm = 23.95 mm. Preserve conflict, do not claim patient FOV. baseline_reference.npz:vp_reconstructed float32 (1,480,480) is a prior 20-frequency reconstruction in m/s, not phantom truth. All three original inventory Conditions retained.

### Callable tools

No source imports: main unconditionally selects a CUDA device (default 0). Native displays select receiver/source indices 0,2,…254 for dobs_0.3 /0.8 /1.25 real component (128 × 128). Each grayscale uses its own maximum absolute native real component: floor(255 × (real / max_abs + 1)/2), float64, no resize, interpolation, FFT, wave solve or inversion. Black negative, midgray zero, white positive; scales are arbitrary observation amplitude, different across frequencies. Three source-zero profiles retain all 256 receiver real/imaginary cells exactly in JSON. Native values are synthetic observations, not toy measurements or outputs.

### Reference-only material

No ground_truth.npz. End-to-end visible paths README.md/data/requirements.txt stage the entire data directory, including baseline_reference.npz; the baseline is solver-visible. Evaluation and source trees are not default-staged. Generic first candidate evaluation/reference_outputs/reconstruction.npy is a different saved reconstruction, not raw phantom truth. Saved baseline_reference.npy equals data baseline cells exactly; saved reconstruction differs by maximum 131.6034 m/s. Saved speed maps remain audit only, never image/display/outcome. Reader-only late reveal teaches selection and denominators; covered on backward/exit/reset before paint.

## Task specification

README Helmholtz (∇² + ω²s²)u = −rho, s=1/c. rho denotes source term, not density. No independent mass-density map, attenuation, optical fluence or clinical property inference. Constant-density slowness forward model. Frequency passed as MHz × 10 in internal 100 kHz units; grid dh in µm. setup pixel_size=lamb/ppw=1/8, scale=dh/pixel_size; lamb_val=mean(speed)/(freq×scale), k0=2π/lamb_val. Dimension conventions are code-pinned, not independently calibrated SI pressure. Boundary argument 20 is multiplied by ppw 8 to 160 padded cells. CBS max iterations loop uses born_max 500; computed max_iterations is unused. Stop checks incremental-field energy/init energy <1e−5 or iteration>=500 only at phase-cycle boundary; no current residual/convergence certificate. Final native field = −conj(E).T/dh² × 2.5e10, not an unscaled textbook field.

Receiver restriction index (iy−1)×ny+ix−1; forward returns transpose/conjugate. Keep these exact axes, not a guessed C-order receiver orientation. Authored asymmetric-grid test distinguishes swapped indices; no native forward/adjoint evaluated. 7500 µm muting uses Euclidean grid distance ×50µm, keep distance>=7500. mask_esi excludes near/self pairs; mask_misfit also excludes exactly zero observations. No physical attenuation correction or new noise draw.

Source amplitude alpha = sum(conj(dsrc)×dobs)/sum(abs(dsrc)²), per source after muting. Denominator has no zero guard. Authored real vectors dsrc=[1,2], dobs=[2,4] give alpha=2; this is mathematics, not a fitted native result. Cost sums squared complex residual across sources/receivers, not average or half-cost. Gradient contracts forward fields with conjugate residual, −real(u×q)×2ω²/vp, transposes and divides 1e10. No independent adjoint or finite-difference verification; gradient smoothing 9 × 9 Gaussian sigma 5 at ≤0.3 MHz, sigma 2 at <0.8, sigma 1 thereafter, zero-pad 4. It is optimization smoothing in grid cells, not measurement noise or image truth.

Initial homogeneous speed 1480 m/s. NCG slowness bounds 1/1700 to 1/1300; Polak–Ribiere beta clamped nonnegative, More–Thuente line search max 5 evaluations, max 3 iterations per frequency. Multi mode bootstraps low to high over 20 frequencies; single mode uses selected frequency. Initial objective/gradient scaling lacks zero guards; line-search warning can continue. Runtime CUDA/PyTorch/SymPy versions, physical unit consistency and end-to-end success unverified. No CBS/NCG/wave inversion/metric executed; no model or learned denoiser in this task.

## Expected output

Generic participant output/reconstruction.npy intended real 480×480 sound speed m/s (230,400 cells). Source main instead writes evaluation/reference_outputs/reconstruction.npy in multi mode, reconstruction_{freq:g}.npy single mode, per-frequency maps and metrics.json. This path mismatch is not resolved by showing source files as participant outputs. Actual output, reconstruction, clean truth and metrics empty.

## Evaluation

Source NCC cosine and NRMSE RMSE/reference range against baseline_reference.npz, no mean-centering. Filesystem generic first existing reference is saved reconstruction.npy, returned regardless of output target shape before a later shape check; full 230,400 pixels; squeeze, complex→magnitude, float64; NRMSE=RMSE/reference range, the same range-normalized formula as source, with a DIFFERENT reference array. Retained audit’s norm-relative source NRMSE assumption is corrected by the newly pinned visualization.py. Filesystem has no output flux/max normalization. The no-filesystem route instead requires evaluation/reference_outputs/ground_truth.npy or data/ground_truth.npy, both absent in the official pinned USCT listing; it errors before the comparison. Its generic fallback snippet would require strictly 2D output and apply flux rescaling/norm-relative NRMSE if that missing file were supplied, unlike the filesystem contract. No fallback reference is automatically invented; speed offset/background affects cosine correlation. Generic additional MSE/PSNR/global SSIM are not clinical tissue validation. main metrics keys ncc_vs_ref/nrmse_vs_ref/mode/freq lack generic ncc_boundary/nrmse_boundary, so no pass/fail threshold under this source boundary schema; no score computed. Generic reference is another reconstruction, not independent speed truth. Do not claim recovered anatomy, diagnosis or convergence/performance.

## Visual explanation

### Workflow

- Native complex observation real-component cells, persistent phantom/truth/output gap and official route.
- Canonical unit/muting, three native frequency, amplitude-fit/NCG rules; authored alpha only.
- Empty participant output; later source/generic reference and metric rules, reset/exit/backward cover.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

A wave solver must explain diffraction and refraction; local minima can survive a low residual.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/usct_FWI/README.md)
- [Pinned physics](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/usct_FWI/src/physics_model.py)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/usct_FWI/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/usct_FWI)
- [Resolution receipt](../sources/imaging101-usct-fwi-resolution.json)

## Limits and attribution

Code/HF card MIT, numerical phantom provenance per source README; primary human breast paper only modality context, no patient identification or diagnosis. Local-teaching display LicenseRef is restriction, not expanded rights. Reopen with coherent physical geometry/pressure calibration, independent phantom truth, intended participant path, gradient/runtime evidence and current evaluator thresholds. No publication, new reconstruction or medical performance.
