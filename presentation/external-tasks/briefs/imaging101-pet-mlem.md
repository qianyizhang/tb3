> **Synthetic scaled-count sinogram only; no patient study, participant activity image or score. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/pet_mlem).**

# Trace PET counts and multiplicative updates without inventing an activity image

Show native measurement bins and background; use authored scalar mechanics to explain source MLEM and OSEM.

## Given

### Original data

One modified Shepp-Logan synthetic condition, not a patient PET study. sinogram/background float32 (1, 128, 120), batch then radial bin then angle; theta float32 (1, 120), degrees 0, 1.5, …178.5. There are 15,360 measurement bins and 16,384 intended image pixels. Radial indices are not calibrated detector positions or millimetres; no 3D, time-of-flight or motion axis. Synthetic assigned activity is relative units, not SUV, Bq/mL, dose or clinical uptake.

Generator forms clean Radon projection, adds uniform background, draws C ~ Poisson(1000 × (A x + r)), then stores y=C/1000 as float32. Native y is not integer photon counts. Background r≈10.928186 relative projection units, same scale as y; C and expected count level would require multiplication by 1000. Metadata count_level is a scaling factor, not total events per image/bin or scan duration. randoms_fraction .1 multiplies the mean of positive clean bins, not 10% of all measured coincidences; separate scatter/attenuation/normalization arrays absent. Seed 42 is a declared generator default, not a new sampling or reconstruction run.

### Supplied helpers

Uniform background estimate, projection angles, metadata image size 128, count scale 1000 and source code. Background additive in expected Ax+r; source main does not pre-subtract randoms. Some observed bins are below background, so clipping a subtracted sinogram would change the likelihood/data. No separately measured randoms/scatter uncertainty, detector efficiency, attenuation map, scatter model or absolute activity calibration established.

### Callable tools

Pinned scikit-image Radon(circle=True) and unfiltered iradon(filter_name=None, output_size 128,circle=True) scaffold. Source calls backprojector adjoint, but interpolation and normalization do not establish an exact discrete Euclidean transpose; exact runtime/kernel/version not pinned here. Denote it B in code mechanics. No Radon, backprojection, FBP, reconstruction or evaluator executed.

Native sinogram PNG maps every 128×120 cell directly: grayscale floor 255*clip(float64(y)/220,0,1). Same relative-unit scale; columns are angle indices, rows radial indices, no resize/interpolation/log transform. Interactive profiles expose source columns 0/60/119 (0°/90°/178.5°), 128 radial values each. Teal observed y, gray uniform r, x radial index, y counts/1000. These are input profiles, not reconstructed activity, line-of-response calibration or fitted noise.

### Reference-only material

Source-visible ground_truth.npz:activity_map float32 (1,128,128), assigned phantom values. Local runner stages entire data directory. Synthetic truth is not clinical uptake or held-out private data. Source saved recon_mlem.npz and likelihood are historical source results; no output or reference image bundled. Later reader card reveals rules only, synchronously covered on exit/backward/reset before paint.

## Task specification

Poisson count model includes background in mean, positivity floors 1e−10 and uniform initial x=1 unless custom x_init. Sensitivity=max(B1,1e−10), expected=max(Ax+r,1e−10), ratio=y/expected, x←max(x/sensitivity × B(ratio),1e−10). Source MLEM 50 updates; no explicit penalty, prior, stopping criterion or uptake normalization.

OSEM 10 full cycles, 6 interleaved angle subsets [s,s+6,…] of 20 angles each: 60 subset updates, not 10 or 50 MLEM-equivalent iterations. Recomputes subset sensitivity, uses matching subset background/measurements; order retained. Source main runs MLEM/OSEM only, no FBP variant. iradon with filter_name=None is unfiltered backprojection, not ramp-filtered FBP. No monotonicity, convergence or performance inferred from source inspection.

Source MLEM history stores Σ(y log(expected)−expected) using expected before update; OSEM recomputes expected after each full cycle. Uses scaled y rather than raw C, omits exposure 1000 and log-factorial constants. Exposure factor does not affect the ideal optimizer at fixed scale, but changes likelihood magnitude; histories/timing are not directly equivalent iteration evidence. No history generated or compared here.

Authored scalar A=3, x=2, r=2, y=8 gives x_new=2 through multiplicative correction. Omitting background gives 8/3 instead; illustrates role only, not native reconstruction. Uniform backprojector scaling would cancel in numerator/sensitivity for a fixed ideal operator; does not repair interpolation/mismatched adjoints or prove likelihood increase.

## Expected output

Generic participant output/reconstruction.npy, comparable 128×128 relative activity image. Source main instead writes evaluation/reference_outputs/recon_mlem.npz and recon_osem.npz with batch-first reconstruction and log_likelihood arrays; output directory contains figures. Actual participant image/score empty, saved source output never substituted.

## Evaluation

Source main evaluates activity>0 mask: 7,379 pixels, reference range .5..6 (5.5 relative units). Full image has 16,384 pixels and 0..6 range; source masked metrics differ from generic full-image comparison. Generic selector can choose sole activity_map by shape/key, squeezes, converts complex to magnitude, float64 with no scale/flux normalization or activity mask. NCC is cosine, not mean-centered Pearson; range NRMSE/MSE/PSNR/globalSSIM. No numerical score computed.

Filesystem generic scorer selects activity_map from data/ground_truth.npz and squeezes its (1,128,128) shape to (128,128); scaled y is not a raw integer count array. No-filesystem scoring instead requires generic ground_truth.npy, absent from both data and reference_outputs in the pinned tree. No metrics.json boundary file is listed; main.py derived masked-baseline thresholds are a source recipe, not a retained generic verdict.

Source main boundaries .9*max(NCC_MLEM,NCC_OSEM),1.1*min(NRMSE_MLEM,NRMSE_OSEM) may take best values from different methods; comment says best OSEM but code selects independently. Both installed generic thresholds required for pass. Threshold values/selected live reference not retained as current verdict here; masked baseline cannot silently qualify an unmasked comparison. No clinical or model performance.

## Visual explanation

### Workflow

- Native scaled-count sinogram with explicit synthetic/input-only gap and acquisition route.
- Canonical Poisson/background, three native angle profiles, source MLEM/OSEM rules.
- Empty participant activity output; later source-truth/evaluator denominators with reset/exit/backward cover.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/pet_mlem/README.md)
- [Pinned generator](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/pet_mlem/src/generate_data.py)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/pet_mlem/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/pet_mlem)
- [Resolution receipt](../sources/imaging101-pet-mlem-resolution.json)

## Limits and attribution

Imaging101 code/HF card MIT; synthetic source measurements. No patient, absolute tracer uptake, attenuation/scatter correction, exact adjoint, reconstructed finding or numerical performance established. Reopen with coherent operator/runtime/reference/threshold and actual participant output lineage; no trial, reconstruction or publication here.
