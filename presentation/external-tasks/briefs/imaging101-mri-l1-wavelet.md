> **Released R4 knee k-space differs from the README's synthetic R8 case; source truth loader requests an absent key. No participant reconstruction or result. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_l1_wavelet).**

# Balance measured complex k-space with a sparse wavelet prior

Explain the source operator and numerical boundaries while preserving the released data/README/loader mismatch.

## Given

### Original data

Released arrays contain one fastMRI-derived knee slice: masked_kspace and sensitivity_maps both complex64 (1,15,320,320), binary float32 mask (320,). Metadata cites file1000000.h5 slice 21, ESPIRiT sensitivity estimation, R=4, seed 0/random mask and ACS fraction 0.08. Exact mask retains 80/320 last-axis columns; unsampled columns are all zero across 15 coils. Metadata vertical mask means last-array-axis columns, not anatomical orientation. No DICOM/NIfTI affine, physical spacing or intensity calibration supplied; arbitrary complex signal.

README describes synthetic 8 coil 128² /R8 and preprocessing docstrings describe Gaussian coils/phantom complex128; actual released arrays differ. Retained data is an actual source measurement example for the released condition, not proof of README difficulty or an outcome. Official bounded 3560 B listing verifies all four data LFS identities. Original raw archive remains retained, not copied into portable assets.

### Supplied helpers

Coil sensitivity maps, mask, db4/Haar filters, source forward/adjoint and solver code. Source uses centered orthonormal FFT over final two axes: ifftshift→FFT(norm=ortho)→fftshift. Mask broadcasts (1,1,W); image multiplies by each complex coil map before FFT. No magnitude conversion before data-consistency optimization. Source metadata R4 is sampling count 320/80, not a measured acceleration/time or clinical claim.

### Callable tools

Task Python/NumPy numerical scaffold, no task/model/evaluator execution. Source FISTA implements .5||MFSx−y||²+λ||Ψx||₁, db4, λ=1e−3, max 100 iterations. Power-iteration step estimate and optional acceleration are source rules, not new runs. Public API infers mask from nonzero energy of first coil instead of receiving supplied mask; verify consistency before future execution. Missing source columns must not be confused with missing image pixels.

### Reference-only material

Runner staging copies full data directory, including ground_truth.npz. Its only native key is **mvue**, shape (1,1,320,320) complex64; source preprocessing requests **phantom** and would fail key lookup for this archive. No task invoked to trigger that failure. Source-visible truth is not a hidden benchmark reference. Saved L1-wavelet source output is separately retained, without fresh method lineage; no participant output or GT image is bundled/rendered. Late reader card reveals these rules only; backward/exit/reset closes it synchronously.

## Task specification

Use y_c=M F(S_c x) with complex coil maps and unitary FFT. Source solver's true SENSE adjoint sums conjugated coil maps×IFFT, without division. Physics helper named adjoint separately divides by sqrt(sum|S|²), floored 1e−12; this normalized combination is not the same linear adjoint used in solver. No IFFT or coil combination performed on native data here.

Complex shrinkage preserves phase: (|z|−τ)₊z/|z|, zero at z=0. Authored coefficient 3+4i with τ=1→2.4+3.2i illustrates one coefficient only; τ is hypothetical, not λ or actual solver step. Wavelet source implements multilevel db4 transform with zero-extension and inverse cropping, not proof of reconstructive accuracy. Missing measurements remain unconstrained by acquisition; prior regularization does not create verified anatomy.

Native input displays are direct log-magnitude k-space derivatives for coil 0/7/14, native 320², no FFT/resize. Display uint8=truncate(255log1p(hypot(re,im))/per-coil max log). Separate per-coil scales make brightness incomparable across coils; phase is hidden for display only. Original complex data remain the optimization domain. Mask legend: teal acquired, gray missing; horizontal phase-encode frequency column index, no mm/patient plane.

## Expected output

Actual generic end-to-end contract: **output/reconstruction.npy**, comparable 320×320 released condition. Source main independently writes evaluation/reference_outputs/l1_wavelet_reconstruction.npz:key reconstruction, complex64. Participant path/image/score null here; source-saved output is not a new response or evidence that this mismatching source loader completed.

## Evaluation

The filesystem generic dispatch discovers source truth candidates by filename/shape/key, squeezes extra dimensions, converts complex values to magnitude and compares float64 arrays without flux/scale normalization. NCC is cosine correlation, no mean-centering; range NRMSE is RMS error/reference range, zero range→infinity. Generic metrics include MSE/PSNR/global SSIM; only installed metrics.json thresholds produce pass/fail. Source listing contains metrics_detail.json rather than metrics.json; no current threshold claim. Separate task-aware registrations are not proof of live dispatch. Without a filesystem workspace, the fallback instead uses a 2D NPY reference, flux-normalizes output and calculates relative L2 NRMSE; it is a different backend contract, not range NRMSE.

Magnitude comparison discards phase differences; a global phase-rotated image can match magnitude. Zero arrays, scaling and reference range affect metrics. Original pure controls illustrate those limits without invoking evaluator or assigning native/image/model scores. Denominator for pixelwise generic comparison is 320²=102400 pixels after comparable shape reduction, not 15 coils or a population/sample-performance estimate.

## Visual explanation

### Workflow

- Actual released mask and coil k-space display, clearly separated from README case and image domain.
- Canonical three-step/three-coil controls explain complex forward model and an authored phase-preserving shrinkage example.
- Actual output empty; later source-truth/loader/evaluator rules cover on backward/exit/reset.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_l1_wavelet/README.md)
- [Pinned physics model](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_l1_wavelet/src/physics_model.py)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_l1_wavelet/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_l1_wavelet)
- [Resolution receipt](../sources/imaging101-mri-l1-wavelet-resolution.json)

## Limits and attribution

AI4ImagingLab code/HF card MIT; upstream fastMRI rights/terms separately unresolved, local inspection only. Reconcile README/data and phantom/mvue loader; pin coherent evaluation/output lineage before outcome claim. No model/task/evaluator run, reconstructed image, reference substitution, clinical finding or publication.
