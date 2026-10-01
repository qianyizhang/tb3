> **Source image equals visible truth; acquired k-space and participant PnP result absent. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/pnp_mri_reconstruction).**

# Trace PnP data consistency without inventing a reconstructed knee

Source-pinned mask and public mechanics; source image revealed later as visible truth, actual result empty.

## Given

### Original data

Native raw_data.npz:img float32 (1, 320, 320), source-described fastMRI knee image, exactly equal to data/ground_truth.npz:img. No acquired complex k-space, coil axis, scanner sequence, FOV, pixel spacing, physical intensity or acquisition-noise distribution established. 102,400 real image pixels, raw range 5.2586347e−6..9.889684e−5 arbitrary units. A derived image is not measured 36-line radial acquisition. It reveals supplied truth; default scene covers it. No anatomical diagnosis or new reconstruction.

### Supplied helpers

Metadata: 36 lines, 200 PGM iterations, step 1, sigma 5, patch 42, stride 7, recurrent states 8; checkpoint prefix models/checkpoints/mssn-550000iters. Three .data/.index/.meta shards Git verified but never loaded. Retained source-saved bool sampling_mask.npy (320,320), 11,766 sampled Cartesian cells /102,400=11.490234375%; inverse fraction 8.70304, not 36-fold acceleration or timing evidence. Geometry only, not acquired samples. All 3 inventory assistance Conditions preserved below.

### Callable tools

Source code inspected, never imported (solvers disables TensorFlow eager on import). No forward FFT, IFFT, denoiser, PGM, metric or evaluator executed. Default mask PNG 320 × 320 directly maps saved bool cells white sampled /black omitted; no new mask generation. Late source image preview samples every second row/column (160×160) after exact float32 minmax normalization. Grayscale floor 255×float64(normalized float32), no resize/interpolation/FFT; image indices and display units only, not mm or clinical tissue contrast. Source max−min has no constant-image guard. This display derivative is not a participant reconstruction.

### Reference-only material

End-to-end visible paths are README.md, data and requirements.txt; the entire data directory includes raw_data.npz and data/ground_truth.npz. Evaluation and source/model checkpoint trees are not in that default visible-path list; source reproduction would need an explicit route for the model. Thus supplied checkpoint retention does not establish default solver access. Normalized evaluation/reference_outputs/ground_truth.npy is first generic scoring candidate, exactly equal to float32 normalized raw image. Data raw and truth archives have identical bytes. Reference is solver-visible, not private or held-out. Late public image shares source input identity; explicit source-role label, covered immediately on exit/backward/reset before paint. Saved IFFT/PnP arrays audit only, no comparison/reconstructed image shown.

## Task specification

Source minmax x=(raw−min)/(max−min), float32. y=M fftshift(FFT2 x)/sqrt(102400)=M F x/320, no added noise despite README eta and main seed 0. Binary mask is rasterized radial lines on a Cartesian Fourier grid, not native non-Cartesian trajectories/NUFFT. Angles 0..pi excluding endpoint, deterministic ROUND_HALF_UP coordinate rasterization; ceil(size/2)+1 one-based centre gives zero-based(160,160). No coil sensitivities or random acquisition mask.

Adjoint 320 IFFT2(ifftshift(Mz)) includes mask, matching unitary discrete complex normalization. Real-valued image gradient real(AH(Ax−y)); fidelity .5 sum |Ax−y|², Fortran flatten for norm only. Missing physical k-space units/FOV prevent cycles/mm inference. Naive source IFFT explicitly multiplies y by 320 before inverse FFT, then takes magnitude; it undoes forward normalization. This magnitude baseline differs from the real-valued adjoint gradient. Mathematical discrete adjoint explanation does not verify scanner operator or runtime. No native FFT/adjoint computed.

Implemented PGM, not ADMM: x0=0; s=max(x−step×g,0), then xnext=MSSN(s), 200 fixed iterations, step 1, no momentum, dual variable or explicit penalty parameter. Positivity applies BEFORE denoiser only; no post-output clipping or upper bound. General learned denoiser is not proven proximal or contractive. Authored scalar A=M=1, y=.6 gives initial gradient−.6 and pre-denoise .6; D(.6) left unknown. No invented denoised/reconstructed outcome.

MSSN patches 42 × 42 stride 7 with terminal start 278; 41 positions per axis, 1,681 overlapping patches. Input scaled 255, cast float32, model residual per patch averaged by coverage then added to noisy input, divided by 255. Last stride gap 5, not uniform 7; no missing borders. sigma 5 accepted constructor argument is UNUSED by graph/inference, so it is a README training-noise claim, not measurement sigma or a tunable reconstruction-strength control. States 8, heads 2, key/value 128, batch 1 defaults; main passes state count but other defaults not arbitrary metadata binding. BSD500 training/learned weights semantics and exact TensorFlow/legacy Keras compatibility unverified. No graph/checkpoint/model loading.

History SNR uses pre-update x (first zero estimate gives 0 dB against nonzero truth); iterate-distance squared is not data-fidelity residual/objective, relative change starts infinity and later has no zero-norm guard. No stopping test/convergence certificate. Source main all_metrics keys IFFT/PnP-MSSN differ from plot_comparison keys ifft/pnp_mssn: KeyError on figure stage AFTER reconstruction/metrics save if earlier stages succeed. Retained outputs do not establish successful current end-to-end execution.

## Expected output

One real output/reconstruction.npy, intended 320 × 320 normalized image. main also writes snr_history.npy, dist_history.npy, output/metrics.json and per-iteration MAT files. These do not replace generic output/scoring files. Participant image, denoiser output, histories and numerical outcome absent.

## Evaluation

Filesystem generic scoring first selects normalized evaluation/reference_outputs/ground_truth.npy regardless of target shape, then requires matching output shape. No-filesystem scoring also seeks that exact ground_truth.npy, which is retained and listed here, then relies on runner exec to make it readable in its sandbox; successful transfer/execution is unverified. Both use the normalized saved reference, not raw-scale data truth; all 102,400 pixels. Filesystem generic prepares ndim>2 by squeeze, complex→magnitude and float64, with no flux/max/minmax normalization of output. The no-filesystem snippet instead requires strictly 2D output, casts float64 without the same preparation, rescales output by gt.sum/(out.sum+1e−30), and uses norm-relative NRMSE. It rounds differently and does not apply the filesystem boundary verdict. These are different effective contracts, not interchangeable backend scores. Its non-filesystem host-to-sandbox reference-copy branch is pass; reference readability and successful execution are unverified. Source NRMSE=error norm/reference norm; generic NRMSE=RMSE/reference range. Source SNR 20 log10(reference norm/error norm) measures reconstruction error against visible truth, not acquisition noise. Both cosine NCC, no mean-centering; generic MSE/PSNR/globalSSIM additional. Source output/metrics.json is not generic evaluation/metrics.json; Pinned evaluation/reference_outputs/metrics.json contains nested saved IFFT/PnP-MSSN results, not flat ncc_boundary/nrmse_boundary. Filesystem therefore has both boundaries None and passed=None; the no-filesystem snippet applies no verdict. Historical metric values are not reproduced or presented as performance. No metric or performance computed. Visible source identity means no blind inverse-problem claim.

## Visual explanation

### Workflow

- Saved source mask with persistent missing acquired-k-space/result warning and acquisition route.
- Canonical PGM step, Fourier scale, mask geometry and patch coverage controls; denoiser output unknown.
- Empty participant output; late public source-image/reference-normalization reveal, reset/exit/backward cover.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Patch scaling and overlap affect the learned prior. The source uses the same image as raw input and reference, so visibility must be checked.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/pnp_mri_reconstruction/README.md)
- [Pinned preprocessing](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/pnp_mri_reconstruction/src/preprocessing.py)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/pnp_mri_reconstruction/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/pnp_mri_reconstruction)
- [Resolution receipt](../sources/imaging101-pnp-mri-reconstruction-resolution.json)

## Limits and attribution

Code/HF card MIT; original fastMRI and MSSN/BSD500 checkpoint reuse rights not independently verified. LicenseRef-fastMRI-MSSN-local-teaching is local-use restriction, not redistribution permission. No publication, diagnosis, clinical image-quality or model performance. Reopen with intended visibility/measurement condition, coherent reference/metric units, model/runtime/rights and participant lineage.
