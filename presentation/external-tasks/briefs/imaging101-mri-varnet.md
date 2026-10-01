> **Actual fastMRI-derived k-space; promised checkpoint absent, no participant reconstruction. Local research use only. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_varnet).**

# Trace VarNet inputs without inventing a learned reconstruction

Actual k-space sample magnitudes and the saved source mask explain input geometry; symbolic rules explain encoding and learned-prior boundaries.

## Given

### Original data

One retained source slice, metadata acquisition CORPD_FBK. kspace_real/imag float32 (1, 15, 640, 368), batch then coil then spatial frequency-array rows and columns. Cast to complex64, not separate echoes/time. Fifteen coils ×640 × 368 = 3,532,800 complex values. HF source identifies fastMRI knee provenance; README declares validation volume file1001077.h5; original slice index and HDF5-to-native byte lineage and scanner orientation are not established. Array coordinates and relative k-space amplitude are not calibrated mm, image anatomy, clinical truth or diagnostic evidence.

### Supplied helpers

Metadata target image shape 320 × 320, source preprocessing and learned model loader. No supplied sensitivity maps; estimation delegated to external fastmri.models.varnet.VarNet with num_low_frequencies=None. Source constructor: 12 cascades, regularizer pools 4 / channels 18, sensitivity pools 4 / channels 8. Required data/varnet_knee_state_dict.pt absent from pinned official tree. README promises a pretrained model, but saved reconstruction does not establish weights, training split, current inference or checkpoint replay. No deserialization or forward performed.

requirements lower bounds fastmri>=0.3.0 and torch>=2.0.0 do not pin exact external implementation, architecture internals or sensitivity schedule. Avoid transferring header claims that sensitivity is re-estimated every cascade to a verified runtime. Source uses CPU/eval/no_grad; no optimization/training or task trial here.

### Callable tools

Centered orthonormal FFT/IFFT utilities use spatial axes only, complex-pair last dimension2. Input to model after batch insertion (1, 15, 640, 368, 2); boolean mask broadcast (1, 1, 1, 368, 1). Data-consistency and learned prior require complex phase; grayscale k-space magnitude display cannot substitute for input or model result. Measurement noise term is conceptual; no native added-noise distribution/covariance or SNR inferred.

Source apply_mask creates equispaced columns at nominal R4 plus center_fraction .08: round(368 × .08) = 29, columns 170:199. Temporary seed 42 reset for each slice, offset drawn; masks are equispaced with a random offset, not Bernoulli random masks. Saved mask float32 (1, 368, 1) retains 113 / 368 columns, matches offset 2 pattern; native saved condition is not an executed task tensor. Effective width/sample ratio 368/113≈3.2566 differs from nominal 4 because ACS overlap. Each coil retains640 × 113 = 72,320 values, all coils 1,084,800; 29 central columns = 18,560 values per coil. ACS low-frequency support is an input to sensitivity estimation, not evidence maps or calibration were computed here.

Three native previews select coils 0 / 7 / 14, every fourth row/column (160 × 92 display cells). Formula floor255*min(log1p(hypot(float64(real),float64(imag))/1e−5)/log1p(.006/1e−5),1). Fixed scale across coils; direct source samples, no averaging, FFT, image reconstruction or per-coil normalization. Gray is log-display magnitude in relative source units; phase lost. Preview coordinates map to native indices4r, 4c, not image pixels/mm. Saved mask strip teal sampled columns/dark missing; display selection never changes source acquisition or runs model.

### Reference-only material

Local runner stages whole data directory, including ground_truth.npz:image float32 (1, 320, 320) RSS magnitude. Solver-visible source reference, not held-out private target or clinical finding. No RSS truth image or saved VarNet reconstruction bundled. Later reader card reveals source/evaluator rules only, covered on backward/exit/reset before paint. Retained packet limits these fastMRI-derived assets to internal research/education; this local handling restriction does not establish original case rights or authorize redistribution; data-derived publication/redistribution requires separate rights review. MIT code license is separate from data terms; local-only pack retains that boundary.

## Task specification

Encoding y_c=M F(S_c x); source utility centered FFT uses norm='ortho'. A proper masked orthonormal adjoint includes conjugated sensitivity and mask; maps not supplied/estimated here. Source wrapper adds batch, calls external model on masked complex-pair data and mask, num_low_frequencies=None; magnitude output returned. Learned cascades combine data consistency and image prior conceptually; no numeric model residual, sensitivity map, trajectory or learned update invented.

Authored scalar hard-consistency example mask=[1,0], measured=[2,0], proposal=[3,4] gives [2,4]. Teaching rule only; does not claim VarNet uses hard replacement (its external learned/soft data-consistency details are not pinned). Source batch wrapper center-crops magnitude from 640 × 368 to 320 × 320, start rows 160 / columns 24, no resize or intensity normalization in this wrapper. No FFT/IFFT/RSS/crop of a reconstructed image executed here.

## Expected output

Generic live output/reconstruction.npy, comparable 320 × 320 magnitude, 102,400 pixels. Source main instead writes evaluation/reference_outputs/varnet_reconstruction.npz and zerofill.npz:reconstruction float32 batch arrays and metrics.json per-slice averages. Saved old output is not participant submission or actual model outcome here. Actual participant image/score absent.

## Evaluation

Exact Git-verified task-local helper uses magnitude float64, range NRMSE (constant-reference range gives infinity), cosine NCC with epsilon 1e-12, and scikit-image windowed SSIM with reference range as data_range and no explicit zero-range SSIM guard. Generic filesystem uses epsilon 1e-30 and global-moment SSIM, so metrics are not interchangeable. No-filesystem route instead requires strict2D NPY reference and flux-normalizes output for relativeL2 NRMSE. No helper import or scoring.

Generic scorer selects source ground_truth:image by shape/canonical key, squeezes, converts complex to magnitude, compares float64 without intensity/flux normalization. Cosine NCC is not mean-centered Pearson; range NRMSE, MSE, PSNR and global SSIM. Magnitude loses phase, while scale-insensitive NCC differs from range error. Generic pass needs both installed NCC/NRMSE boundaries; source main metrics.json has only varnet_avg/zerofill_avg, not those boundary fields, so its own averages do not define a generic pass verdict. Source main averages per-slice metric dictionaries; one slice retained, but no metric execution or accuracy claim. Source saved metrics do not establish this checkpoint/runtime/reference lineage or clinical performance; compare only after retaining actual selected reference/threshold/output.

102,400 comparison image pixels differs from 113 sampled columns, 1,084,800 complex sampled coil values and 3,532,800 full values. Display stride does not create acceleration, independent samples or reconstructed resolution.

## Visual explanation

### Workflow

- Native k-space magnitude sample preview with explicit missing checkpoint and acquisition route.
- Canonical encoding, three coil displays with saved mask, symbolic learned-prior/input contract.
- Empty participant image/score and later source-reference rules with backward/exit/reset cover.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_varnet/README.md)
- [Pinned preprocessing](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_varnet/src/preprocessing.py)
- [Pinned loader](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_varnet/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_varnet)
- [Resolution receipt](../sources/imaging101-mri-varnet-resolution.json)

## Limits and attribution

Code MIT; fastMRI-derived data local research/education only, no publication or redistribution authorized here. Resolve missing checkpoint, exact external runtime, original case and applicable rights before reproduction or sharing. No model forward, FFT, reconstruction, metric verdict, clinical effect or performance ranking.
