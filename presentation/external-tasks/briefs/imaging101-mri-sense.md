> **Synthetic source only; loader requires absent full-kspace keys and main R4 differs from native R3. No participant reconstruction. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_sense).**

# Trace coil sensitivity encoding without inventing an MRI reconstruction

Use actual synthetic sensitivity maps and masked-data geometry to explain SENSE and its source-contract mismatch.

## Given

### Original data

One synthetic Shepp-Logan condition, eight Gaussian coil-sensitivity maps. raw_data.npz has masked_kspace_real/imag and sensitivity_maps_real/imag float32 (1,128,128,8); undersampling_mask uint8 (128,). Batch first, spatial rows/columns then coil last. Complex data reconstructed by real+i imaginary, cast float64 components to complex128 by loader helpers. No scanner, patient, anatomical orientation, physical FOV/mm, dwell/TR/TE or time calibration.

Native R3 mask with ACS16 selects every third row plus rows 56:72; 54/128 rows, 6912/16384 cells per coil and 55296 complex sample values across eight coils. Nominal R3 is not effective 128/54≈2.3704; preserved calibration lines change counts. Coil 0 nonzero pattern exactly matches supplied mask across all columns. Sensitivity maps are supplied synthetic helpers; no calibration estimation, noise covariance, coil compression or whitened data established. Maps are not normalized to unit sum-of-squares (native power range approximately .08582–.14910); never infer patient signal from them.

### Supplied helpers

Ground truth image float32 (1,128,128), source code and metadata. Native metadata R3, source main hardcodes R4/ACS16. Loader expects kspace_full_real/imag absent from released archive; native masked keys must not be silently renamed as fully sampled data. No matching full k-space acquired or synthesized here. Loader also returns normalized source phantom separately.

### Callable tools

Pinned NumPy CG-SENSE scaffold only; no task/FFT/CG/evaluator execution or runtime installed. Three source-map previews select coils 0/3/7 for display, not solver coil selection. Direct magnitude sqrt(real²+imag²), fixed display ceiling .16, grayscale floor(255*min(magnitude/.16,1)), preserves native 128² cells. Display loses phase and is not a reconstruction. Native mask strip: teal sampled rows, dark missing; no interpolation, fftshift or acquisition change.

### Reference-only material

Source-visible ground_truth.npz:image staged with data directory, not a private held-out target. Source synthetic phantom never patient truth. Saved source sense_reconstruction/zerofill archives have no fresh execution lineage. No truth, saved reconstruction or participant image shown. Later reader card reveals source/evaluator rules only; backward/exit/reset closes before paint.

## Task specification

A x=M F(S_c x), centered default FFT2 on spatial axes 0/1. NumPy forward FFT unnormalized; inverse 1/16384, not ortho. Source centered_ifft2 is inverse for this even 128² geometry. Declared AH helper sums conj(S_c)*IFFT(y_c), omits mask and is 1/16384 times Euclidean adjoint on mask-supported inputs. A true arbitrary-domain Euclidean adjoint requires mask and FFT scale. In solver normal equation both sides use the same scaled helper; do not transfer an orthonormal/fully masked adjoint identity without qualification.

Source solver infers mask=abs(first-coil kspace)>0 rather than consuming supplied mask. Native equality verified, but a legitimately sampled zero would be mistaken for unsampled. Complex conjugate inner products in CG; E=AH A, b=AH data. Zero initialization, rtol 1e-5, atol 0, maxiter default 10*n=163840, no preconditioner or explicit lambda/Tikhonov regularization. Denominator breakdown and convergence info are not propagated; code discards info. Not a convergence or reconstruction claim. Final source pipeline takes magnitude and divides by its max; source baseline separately IFFT+RSS then max normalization. No iterations or coil-combined image computed here.

Authored two-location encoding matrix [[1,2],[3,1]] with illustrative x=[1,2] gives y=[5,5]; independent of native maps, no measured solve or truth. This explains how differing coil responses encode locations, not an actual recovered phantom.

## Expected output

Generic live participant path output/reconstruction.npy, comparable 128×128 image (16384 pixels). Source main separately writes evaluation/reference_outputs/sense_reconstruction.npz:reconstruction float32 (1,128,128), zerofill.npz and fully_sampled.npy. Source max normalization is a solver convention; no participant output, convergence record, score or clinical outcome exists.

## Evaluation

The exact primary visualization.compute_metrics helper is retained and Git-blob verified after one approved bounded public HTTPS read; the first local proxy failure remains infrastructure evidence. Source-only inspection shows magnitude arrays converted to float64, range NRMSE (zero reference range gives infinity), uncentered cosine NCC with epsilon 1e-12, and scikit-image structural_similarity on the magnitude 2D arrays with reference range as data_range. Its SSIM is windowed, unlike the generic filesystem global-moment SSIM; the source helper has no explicit zero-range SSIM guard. Generic filesystem NCC uses epsilon 1e-30. Source helper SSIM therefore must not be equated with generic scores or claimed finite on constant references. No helper was imported or executed.

Header inspection confirms retained data truth contains image, float32 (1,128,128), prepared as (128,128) under the pinned filesystem rule. The retained subset lacks evaluation ground_truth.npy; this subset therefore reaches data/ground_truth.npz before later saved reconstruction candidates. Source main writes normalized phantom as fully_sampled.npy, which is neither an explicit generic truth candidate nor matched by the generic filename tokens. It therefore must not be silently substituted for data/image; that file is not acquired here. No reference/scorer function was invoked. The filesystem route uses unscaled range NRMSE (zero reference range gives infinity); without a filesystem workspace the fallback requires a 2D NPY reference, flux-normalizes output and uses relative L2 NRMSE. These are distinct backend contracts, not results.

Generic selector prioritizes ground_truth candidates and shape/key compatibility, with source data image solver-visible. Squeeze, complex→magnitude, float64 comparison; no intensity normalization. Source main normalizes phantom and reconstruction maxima before its own metrics; generic harness can instead select unnormalized data truth, so retain actual selected reference/path before comparing scores. Generic cosine NCC (no mean centering), range NRMSE, MSE, PSNR/global SSIM; both ncc_boundary and nrmse_boundary required for pass. Source main metrics.json sense/zerofill groups do not establish installed thresholds. No current evaluator run/reference selection/result. Magnitude discards phase; scale-invariant NCC differs from range-error response. 16384 pixels is not 55296 complex coil samples or 54 sampled rows.

## Visual explanation

### Workflow

- Native synthetic sensitivity magnitude and exact mask counts; loader/R mismatch prominent.
- Canonical encoding, three display coils and CG rules; no reconstructed image.
- Empty participant output and later source-truth/evaluator rules with reset/exit/backward cover.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_sense/README.md)
- [Pinned physics](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_sense/src/physics_model.py)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_sense/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_sense)
- [Resolution receipt](../sources/imaging101-mri-sense-resolution.json)

## Limits and attribution

Code/HF card MIT, synthetic map-only derivatives. Reopen on coherent released loader/full-versus-masked keys, R3/R4 and selected evaluator/reference/output lineage. Native source phantom is not clinical truth. No reconstruction, performance, convergence guarantee or patient inference.
