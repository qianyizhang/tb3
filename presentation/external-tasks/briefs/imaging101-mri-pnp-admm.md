> **No measured k-space or participant result; pinned metadata omits required noise_scale. Actual masks only. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_pnp_admm).**

# Trace PnP-ADMM without inventing a reconstructed brain image

Explain actual source masks and the pinned data-consistency / denoiser / dual updates.

## Given

### Original data

One single-coil 256×256 source image condition. raw_data.npz has five float32 arrays (1,256,256): mask_random, mask_radial, mask_cartesian, noises_real, noises_imag. No acquired or synthesized y is stored. Actual mask cells: random 19674/65536, radial 19249/65536, Cartesian 19456/65536. Radial here is a Cartesian-grid binary pattern, not a non-Cartesian trajectory. No coil sensitivity maps, physical FOV, millimetre spacing, scanner orientation or time calibration.

### Supplied helpers

Source image image float32 (1,256,256), cast float64 by preprocessing; metadata says float64, a loading convention rather than stored dtype. Pretrained RealSN_DnCNN_noise15.pth is 11028772 bytes; retained SHA pinned, never deserialized. 17 convolution layers, 64 features, batch normalization in middle layers, real spectral-normalization hooks; loader wraps DataParallel and eval. README convergence and Lipschitz claims do not establish a verified property of this loaded checkpoint/runtime or actual iterations.

### Callable tools

Pinned NumPy/Torch scaffold only, not executed. Source get_complex_noise default scale=3 exists, but prepare_data explicitly indexes metadata['noise_scale']; pinned metadata lacks the key. No effective scale or distribution variance inferred. Stored noise described as Gaussian, not a new generated realization. Noise is added at every Fourier bin, including outside the mask. Denoiser sigma=15 is an 8-bit training/scaling parameter, not measurement noise standard deviation or physical MRI units.

### Reference-only material

Visible data includes ground_truth.npz:image. Local runner copies data directory recursively; truth is solver-visible, not held-out private truth. Used to synthesize observation and compute per-iteration PSNR. No source truth image, saved source reconstruction, participant image or score is bundled. Later reader card reveals source/evaluator rules only, covered synchronously on backward/exit/reset. Upstream Brain.jpg rights not independently verified.

## Task specification

The unshifted default FFT forward is not unitary. Its linear Hilbert adjoint requires the grid-size factor 256² = 65536 times inverse FFT, with the sampling mask; the helper called zero-filled adjoint returns magnitude of inverse FFT, which is a nonlinear initializer. No Fourier operation was executed here.

The retained 11028772-byte checkpoint matches the primary HF LFS identity. We did not load or unpickle it, inspect learned parameters, run spectral normalization or denoise. Source code targets a 17-layer RealSN-DnCNN residual model and scales convolution weights by 0.3^(1/17); the eval hook does not recompute normalization. That source declaration and checkpoint identity do not establish an effective network Lipschitz bound, training provenance, PnP convergence or reconstruction quality. Batch normalization, runtime state and theorem assumptions would require separate verification.

Unshifted NumPy default FFT2 (forward unnormalized, inverse 1/65536): y=M FFT2(image)+scale(noise_real+i noise_imag). Single coil, complex128 synthesized y; real image iterates. x0=v0=abs(ifft2(y)), u0=0. Source main fixes alpha=2, sigma=15, 100 iterations, CPU; no adaptive schedule or stopping test. No initialization or FFT performed in this explainer.

vtilde=x+u; vf=FFT2(vtilde); sampled vf=(La2 vf+y)/(1+La2), La2=1/(2alpha)=.25; unsampled vf unchanged; v=real(ifft2(vf)). Code weighting is retained verbatim; do not substitute another ADMM/rho convention or an orthonormal complex adjoint.

xtilde=2v−xold−uold. Normalize using min/max without a constant-input guard. Scale range=1+15/255/2, shift=(1−range)/2, send float tensor (1,1,256,256) to residual network. Subtract model residual, invert scaling and range, then u=uold+xold−v. This update order differs from generic textbook ADMM notation. No learned residual or reconstructed output invented; authored scalar sampled-bin examples demonstrate only arithmetic. No checkpoint inference, convergence or clinical effect.

Native mask PNGs preserve all 256² binary cells: teal (87,209,204) sampled, dark (18,41,57) unsampled; rows/columns are stored Fourier-array indices, not anatomical axes. No fftshift, interpolation or reconstruction. Three controls select a display mask only; pinned main remains random.

## Expected output

Generic live participant path output/reconstruction.npy, comparable real 256×256 image (65536 comparison pixels). Source main separately writes evaluation/reference_outputs/pnp_admm_reconstruction.npz:reconstruction float32 (1,256,256), zerofill.npz, psnr_history.npy, ground_truth.npy and metrics.json. Saved source examples are not participant submissions or fresh runs. Actual output, truth display and scores absent.

## Evaluation

Actual retained truth has only image: float32 (1,256,256), reduced to (256,256) by the filesystem helper because ndim > 2. Candidate path, key and prepared shape were audited without calling a scorer; The retained subset has no evaluation/reference_outputs/ground_truth.npy, so its data truth precedes fallback saved reconstruction candidates. Source main separately writes an evaluation ground_truth.npy, which would outrank data truth when actually staged; that file is not acquired or pixel-verified in this packet. The no-filesystem fallback instead requires a 2D NPY reference, flux-normalizes output and uses relative L2 NRMSE, unlike filesystem unscaled range NRMSE. These routes establish no measured result.

Generic source reference selection prefers ground_truth files and shape/key compatibility. Squeezes only arrays above two dimensions, complex becomes magnitude, float64 comparison without intensity normalization. Cosine NCC has no mean centering; range NRMSE=RMS error/reference range (constant reference → infinity). MSE, PSNR and global SSIM are declared metrics; both ncc_boundary and nrmse_boundary required for a pass predicate. Source main metrics.json pnp_admm/zerofill fields are distinct from a verified installed threshold contract. No task evaluator executed, reference selected live or metric verdict. Phase information is discarded by generic magnitude comparison; cosine NCC is scale-insensitive while range NRMSE is not.

## Visual explanation

### Workflow

- Actual binary source masks, missing observation and metadata scale explained first.
- Canonical steps expose Fourier consistency, three display masks and residual-denoiser/dual rules.
- Participant output empty; late reader rules cover on backward/exit/reset.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_pnp_admm/README.md)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_pnp_admm/src/solvers.py)
- [Pinned preprocessing](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_pnp_admm/src/preprocessing.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_pnp_admm)
- [Resolution receipt](../sources/imaging101-mri-pnp-admm-resolution.json)

## Limits and attribution

Imaging101 code and HF card declare MIT. Mask-only derivatives avoid unverified upstream Brain.jpg display rights. Reopen when matching effective noise_scale / runtime / staged reference / participant output lineage is established. No reconstructed finding, denoiser performance, private reference, convergence proof or medical outcome.
