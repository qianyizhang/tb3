> **Synthetic phantom with solver-visible truth; no participant reconstruction or calibrated FOV/time. README coordinate units differ from source NUFFT grid scaling. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_noncartesian_cs).**

# Reconstruct a complex image from radial samples without inventing an outcome

Trace actual radial coordinates, supplied coil maps, density-compensated gridding and the separate complex wavelet objective.

## Given

### Original data

One synthetic Shepp-Logan condition: kdata complex64 (1,4,8192), coord float32 (1,8192,2), coil_maps complex64 (1,4,128,128). Four coils share 64 radial spokes × 128 readout samples: 8192 complex values/coil, 32768 total. These are ordered samples, not a Cartesian grid. Source generator uses birdcage coil maps; no patient scan, sensitivity estimation or scanner calibration claimed.

Native coordinates are verified against pinned HF LFS identities. Display selects every 16th sample: 512 points, 8/spoke. Original acquisition remains 64 spokes; controls select 1/16/64 spokes for display only. Repeated origin samples are not unique Cartesian coverage. README 8192/16384=.5 count ratio does not establish 50% unique coverage, independent information or acceleration.

### Supplied helpers

Complex coil maps, radial coordinates, db4/Haar filters, metadata and source code. Generator uses θ_i=iπ(√5−1)/2, r=linspace(−.5,.5,128,endpoint=False), coord0=128r cosθ, coord1=128r sinθ. Source passes these directly to SigPy NUFFT; coordinate order follows final two image-grid axes, no anatomical orientation.

README calls coordinates cycles/pixel despite approximately −64..64 range. Source scale is NUFFT grid indices; normalized cycles/pixel requires division by 128. No physical FOV/mm⁻¹, dwell time, TR/TE or timestamps. Flat order is spoke then readout, not milliseconds. SigPy≥0.1.26 is a lower bound, not an exact runtime/default-normalization pin; kernel width/oversampling unspecified. Do not transfer Cartesian ortho FFT guarantees to this call.

### Callable tools

Python/NumPy/SigPy scaffold, no task/NUFFT/model/evaluator executed or dependency installed. y_c=F_NU(S_c x)+η_c remains complex. Source generator default seed 42 and .005(randn+i randn)/√2 noise give declared real/imag std .005/√2 and E|η|²=.005². Metadata noise_std=.005 is not an observed noise estimate or proof of raw seed lineage.

### Reference-only material

L1/L2/L3 visible paths include full data directory; local runner copies directories recursively. ground_truth.npz:key phantom complex64 (1,128,128) is solver-visible, not private hidden truth. Separate source saved gridding/L1-wavelet outputs have no fresh execution lineage. No phantom/reconstruction/score image is bundled. Later reader card reveals rules only; backward/exit/reset closes it synchronously.

## Task specification

Forward multiplies complex coil maps then evaluates NUFFT at supplied coordinates. Density compensation is computed, not supplied: initialize w=1, repeat 30 default Pipe updates w←w/max(|F_NU F_NUᴴw|,1e−12), return |w|. Gridding applies w to each coil's kdata, adjoint NUFFT and conjugated-map combination, then divides by max(sqrt(sum|S|²),1e−12). This density-weighted normalized baseline differs from the unweighted iterative objective. DCF preparation is iterative; actual weights/gridding image absent.

FISTA source minimizes .5Σ||F_NU(S_c x)−y_c||²+λ||Ψx||₁ with db4, λ=5e−5, max 100 iterations and power-iteration step estimate. Solver adjoint sums conjugated-map adjoints without DCF or coil-power normalization. Authored 3+4i coefficient with hypothetical τ=1→2.4+3.2i illustrates phase-preserving shrinkage, never a native result. No convergence/reconstruction/performance.

Coordinate PNG is a 256² diagram: teal 512 source points, gray axis guides, dark background. Plot maps x=8+(coord1+64)240/128, y=8+(64−coord0)240/128, integer truncation. Display transform is not image geometry, NUFFT preprocessing, data interpolation or calibration. Interactive SVG uses the same native coordinate subset.

## Expected output

Generic live contract **output/reconstruction.npy**, comparable 128× 128 image. Source main separately writes evaluation/reference_outputs/gridding_reconstruction.npz and l1wav_reconstruction.npz:key reconstruction complex64. Participant path/image/score null; source saved artifacts are not new responses or verified method outcomes.

## Evaluation

Pinned reference rules were inspected without execution. The filesystem route tries explicit evaluation ground-truth filenames before data/ground_truth.npz, then later saved reconstruction candidates. Retained data truth has only phantom, complex64 (1,128,128), reduced to (128,128) because ndim > 2; its identity is not inferred from its name. Saved gridding has reconstruction (1,128,128) plus dcf (1,8192). The latter is already ndim 2 and therefore remains (1,8192), rather than being squeezed; target-shape matching and reconstruction key rank separate these arrays. Truth remains source/solver-visible, not a held-out answer. If truth is absent, different saved output candidates may be selected; do not substitute them silently. No metric result was computed.

The no-filesystem fallback differs: it seeks a 2D NPY reference, flux-normalizes output and uses relative L2 NRMSE. Filesystem scoring uses unscaled range NRMSE (zero range gives infinity); these backend contracts are not interchangeable.

The filesystem generic dispatch discovers source references by filename/shape/key, squeezes only arrays with more than two dimensions, converts complex arrays to magnitude and compares float64 without flux/scale normalization. Data phantom is solver-visible; no held-out target established. Cosine NCC has no mean centering; range NRMSE=RMS error/reference range, zero range→infinity. Generic MSE/PSNR/global SSIM and metrics.json pass thresholds differ from source main metrics_detail.json. No current threshold or new native score asserted; retain exact selected reference before outcome interpretation.

Magnitude scoring loses phase: global phase rotations can share identical magnitude. 128²=16384 comparison pixels differs from 8192 samples/coil, 32768 complex values and 64 spokes. Original pure phase/scaling/adjoint/coordinate controls establish mathematical limits, not benchmark/model/patient performance.

## Visual explanation

### Workflow

- Actual coordinate subset with labelled complex sample/coil dimensions, no reconstruction.
- Canonical display subsets inspect 1/16/64 spokes; DCF baseline versus unweighted complex-wavelet objective.
- Actual output empty; later source-truth/evaluator rules cover on backward/exit/reset.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_noncartesian_cs/README.md)
- [Pinned physics](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_noncartesian_cs/src/physics_model.py)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/mri_noncartesian_cs/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/mri_noncartesian_cs)
- [Resolution receipt](../sources/imaging101-mri-noncartesian-cs-resolution.json)

## Limits and attribution

AI4ImagingLab code/HF card MIT, synthetic source, no patient rights claim. Resolve coordinate-unit/FOV convention and exact SigPy/default normalization for reproduction, then retain participant artifact/evaluator/reference lineage. No clinical finding, model/task/evaluator execution, reconstruction, reference substitution or publication.
