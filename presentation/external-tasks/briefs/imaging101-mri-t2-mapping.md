> **Synthetic echoes only; generic reference may select M0 rather than T2. No participant fit or clinical result. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_t2_mapping).**

# Trace echo decay without inventing a fitted T2 map

Actual native echo images illustrate magnitude inputs; symbolic equations explain fitting and source/evaluator boundaries.

## Given

### Original data

One modified Shepp-Logan synthetic condition. multi_echo_signal float32 (1,256,256,10), batch then row/column then echo. Ten TE values 10,20,…100 ms, not a time-series frame interval. Exactly 655360 magnitude samples across 65536 pixels. No complex phase or coil axis. Native signal nonnegative, range ≈.00003931–1.004664 a.u. Metadata declares synthetic FOV 220 mm, pixel .859375 mm; no scanner orientation, actual acquisition or patient interpretation.

### Supplied helpers

Metadata and source code; ground_truth.npz:T2_map/M0_map float32 (1,256,256), tissue_mask bool same shape. Source main reads truth-derived mask and uses it for fitting and scoring; 27817 included pixels, 37719 background. Truth parameters solver-visible, not private held-out clinical labels. Generator assigns hypothetical phantom regions, not measured tissue properties. Source seed 42/default parameters are declared; no generator rerun or exact noise draw provenance newly established.

### Callable tools

Pinned NumPy/source LM scaffold, never executed here. S(TE)=M0 exp(−TE/T2), TE/T2 in matching ms; M0 and signal arbitrary units. Source noise independently draws real/imag Gaussian σ=.02 per channel then sqrt((S+nr)²+ni²), not additive zero-mean Gaussian magnitude noise. E|η|²=2σ²=.0008, differs from doc CN(0,σ²) shorthand. Magnitude floor includes nonzero background; no Gaussian/Rician likelihood fit or measured bias claimed.

Preprocess casts float64, removes batch and clips signal at zero; native already nonnegative. Three input previews use echo indices 0/4/9 (TE 10/50/100 ms), same native 256² array cells. Fixed grayscale floor255*clip(signal,0,1), no per-echo normalization/interpolation/log/fitting; native values above1 clip for display only. Gray brightness is a.u., not T2 ms. Image-derived contrast cannot establish a fitted T2 or patient finding.

### Reference-only material

Local runner stages whole data directory, including T2/M0/tissue mask. Saved source T2_map_nonlinear.npz is an old fit, not participant output. No truth or fitted map bundled. Later reader card reveals source-visible truth/evaluator rules only; exits/backward/reset cover synchronously before paint.

## Task specification

Log-linear doc says weighted regression, implementation calls unweighted np.linalg.lstsq on A=[1,TE], log(max(S,1e−10)). Slope=−1/T2, intercept=logM0; T2 clip 0..5000 ms, nonfinite→0; M0 exp intercept, nonfinite→0. No echo weights or Rician-noise correction. Flat/increasing log signals can yield invalid/clamped maps, no measured outcome asserted.

Nonlinear source minimizes unweighted signal-domain Σ(S−M0 exp(−TE/T2))², not Rician likelihood. Per-pixel LM up to 50 iterations, log-linear initialization (T2≥1 ms,M0≥1e−6); gradient/step eps1=eps2= 1e−8, tau 1e−3. Jacobian columns exp(−TE/T2), M0 TE/T2² exp(−TE/T2). Diagonal damping, gain-ratio accept/reject; trial positivity M0≥1e−10,T2≥.1 ms. Final T2 clip 0..5000, failure falls back to initial maps. Background outside mask stays 0. Source doc calls nonlinear unbiased; this objective/source inspection does not establish statistical unbiasedness, accuracy or convergence.

Authored M0=.8 a.u.,T2=80 ms at TE 10/50/100 illustrates expected exponential signal only, not native truth/fit/noise realization. No solver, least squares, model inference or native metric executed.

## Expected output

Generic participant output/reconstruction.npy intended T2 map comparable 256×256 in ms. Source main writes T2_map_loglinear.npz and T2_map_nonlinear.npz under evaluation/reference_outputs, each T2_map/M0_map float32 (1,256,256); creates output directory for figures, not generic reconstruction.npy. Actual participant map/score absent; saved source fit never substituted.

## Evaluation

Task-local NCC returns 0.0 when either norm is below 1e-12; its range NRMSE returns infinity when reference range is below 1e-12. Generic filesystem range NRMSE only tests range >0 and NCC adds epsilon 1e-30. These near-zero guards differ. The no-filesystem backend instead requires a strict 2D NPY reference, flux-normalizes output and uses relative L2 NRMSE; it is a distinct route. No scorer run.

Source main masked cosine NCC and range NRMSE compare T2 on 27817 pixels, range 40..150 ms (110 ms denominator). Full T2 including background has 0..150 ms range and 65536 pixels; masked/full metrics are different. Generic dispatch uses reference_scoring, squeezes, reduces complex to magnitude, float64, no intensity normalization and no source tissue mask. Two numeric same-shaped arrays in native ground_truth have no canonical key match: fallback alphabetical M0_map precedes T2_map; bool tissue_mask is rejected. Both float32 maps have stored shape (1,256,256), reduced to (256,256) only because ndim>2; shape compatibility does not establish target identity. Static ranking proof identifies a possible M0 target conflict; no live evaluator/reference selection run. Preserve/reconcile selected target and units before score interpretation.

Generic cosine NCC (not Pearson), range NRMSE, MSE, PSNR/global SSIM, 65536 pixels. Source main creates evaluation/metrics.json boundaries .9*NCC_nls and1.1*NRMSE_nls from masked T2 baseline. Both thresholds required by generic pass predicate; native source installed thresholds absent/unverified here. Do not transfer masked baseline to unmasked M0 comparison. Scale-invariant NCC differs from scale-sensitive error; ms↔seconds changes numeric scale if reference not converted.

## Visual explanation

### Workflow

- Native magnitude echo preview with ms versus a.u. legend and persistent synthetic/evaluator gap.
- Canonical signal/noise, three echo displays, log/LM contract rules.
- Participant map empty; late source-truth/evaluator mismatch rules cover on exit/backward/reset.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_t2_mapping/README.md)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_t2_mapping/src/solvers.py)
- [Pinned native metrics](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_t2_mapping/src/visualization.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_t2_mapping)
- [Resolution receipt](../sources/imaging101-mri-t2-mapping-resolution.json)

## Limits and attribution

Imaging101 code/HF card MIT; synthetic echo derivatives, no patient rights/clinical claims. Resolve exact generic target/units/threshold/mask lineage before numerical verdict; matching participant output and fit remain absent. No fit, metric execution, clinical result or statistical unbiasedness claim.
