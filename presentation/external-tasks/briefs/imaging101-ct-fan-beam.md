# Reconstruct a fan-beam CT slice

Reconstruct one synthetic attenuation image from divergent-ray measurements.
The released scans, three saved reconstructions and source operators are
inspectable. Geometry, score normalization and exposed truth limit the claims.

## Value

A pixel's detector position depends on its distance from the rotating source.
The task combines magnification, detector interpolation, filtering and weighted
backprojection. A short sweep also changes which measurements receive full weight.

## Given

### Original data

One synthetic 128×128 Shepp–Logan phantom, not an acquired patient scan.
`raw_data.npz` contains float32 `sino_full` `(1,180,192)` and `sino_short`
`(1,116,192)`: case, source-angle index, detector bin. Full-scan angles cover
360° in 2° steps; the short scan covers **232.891°** in approximately 2.008°
steps. Both exclude their ending angle. The short scan is separately sampled,
not a prefix cropped from the full scan.

Values range from **−4.331 to 52.506** for the full scan and **−3.858 to 54.620**
for the short scan. The generator adds Gaussian noise at 2% of the maximum clean
full-scan value. Negative measurements are retained. These are simulated
projection values in pixel coordinates, not photon counts or HU.

### Supplied helpers

The raw archive supplies both angle vectors in radians and 192 detector-center
positions spanning **−127⅓ to 127⅓ pixels**, spaced **1⅓ pixels** apart. Metadata
sets source-to-isocenter and isocenter-to-detector distances to **256 pixels**
each. Image pixel centers range from −63.5 to 63.5. No millimeter calibration or
patient orientation is supplied. L2 adds an approach; L3 also adds software design.

The executed mapping places the source at `(-256 sin β, 256 cos β)` and detector
center opposite it; the README formula differs by a quarter turn. The generator
and Parker helper use `atan(detector_position / 256)`, giving the declared
**26.446°** half-fan angle. The actual source-to-detector separation is 512 pixels,
giving **13.966°** to the outer detector centers. Released angles and weights
remain unchanged; 232.891° is not described as this geometry's minimum sweep.

### Callable tools

Python numerical dependencies. The audit used existing NumPy/SciPy packages for
source fixtures, saved-input FBP replay, fixed operator controls and scoring.
It did not run an iterative solver, agent, dataset generator or installer.

### Reference-only material

`data/ground_truth.npz:phantom` is float32 `(1,128,128)` with values from 0 to 1.
Actual L1/L2/L3 local file seeding copies **this truth archive** alongside
measurements and metadata. A reader-facing reveal does not imply a private
evaluator. Saved reconstructions remain in the evaluation directory, which is
not copied by that seeding path.

## Task specification

For each angle, the forward operator maps every pixel to a fractional detector
coordinate. With `t = x cos β + y sin β` and `s = −x sin β + y cos β`, it uses
`U = 256 − s` and detector coordinate `512 t / U`. Each pixel contributes to two
neighboring bins with linear weights multiplied by `512 / U`. This is a
pixel-driven splat, not the cited upstream ray tracer. Fixed unit-pixel controls
reproduce the bin positions and weights.

Source FBP optionally applies the released Parker weights, preweights detector
values, uses its Hann-windowed filter with cutoff 0.3, and interpolates filtered
projections with `256² / U²` distance weighting. Native `main.py` clips negative
reconstructions to zero. Rebuilt geometry matches the saved float32 coordinates.
Both FBP outputs reproduce **exactly as float32** from the saved noisy measurements.

The saved TV-labelled result comes from a separate 150-step source routine.
Two bounded controls limit algorithmic claims: the forward/backprojection pair
fails a Euclidean adjoint inner-product check, and the helper documented as
projection onto a radius-0.005 ball returns `(3,4)` with norm **5** unchanged.
The audit neither reruns nor repairs that solver, and does not infer that its
saved image is invalid. Its 150 saved loss values omit the TV penalty;
**66 of 149 successive steps increase**. No intermediate images or monotone
convergence guarantee are established.

## Expected output

One 128×128 reconstructed image in the task's relative attenuation scale.
Native `main.py` writes three NPZ archives under `evaluation/reference_outputs/`:
full-scan FBP, short-scan FBP and the TV-labelled short-scan result. Each has
`reconstruction` `(1,128,128)`; the last also has `loss_history` `(150,)`.
These are saved numerical results, not fresh agent outputs.

The active generic end-to-end scorer requires `output/reconstruction.npy`.
A native NPZ alone fails that filename check; stacked images and the loss vector
fail the shape check.

## Evaluation

Native evaluation crops 12 pixels from each edge, retaining **104×104 =
10,816/16,384 pixels**, then independently min-max normalizes each image.
NCC is cosine similarity without mean subtraction; NRMSE divides by the reference
range. The live generic scorer uses the full unnormalized image and selects
`data/ground_truth.npz:phantom`.

| Saved result | Native NCC | Native NRMSE | Generic NCC | Generic NRMSE |
| --- | ---: | ---: | ---: | ---: |
| Full-scan FBP | 0.6518 | 0.1929 | 0.6380 | 0.1854 |
| Short-scan FBP | 0.5578 | 0.2110 | 0.5626 | 0.1927 |
| TV-labelled short scan | 0.9661 | 0.0855 | 0.9706 | 0.0634 |

Native replay matches all six four-decimal values in notebook cell 17. That
retained cell also prints boundaries NCC ≥0.8695 and NRMSE ≤0.0941. However,
**no `metrics.json` is shipped** in the pinned source tree or asset manifest.
The actual generic scorer returns metrics without pass/fail; historical printed
boundaries have not been installed or treated as current.

Half-strength truth, truth plus one, and truth changed only outside the crop all
retain native NCC **1** and NRMSE **0**. Their generic NRMSE values are **0.1165**,
**1.0000** and **5.8296**, respectively. Copying staged truth yields perfect scores
but does not demonstrate reconstruction. The separate non-filesystem fallback
looks for the absent `ground_truth.npy` and reports that error.

## Visual explanation

### Workflow

- Inspect native full and short sinograms with actual angular sampling.
- Follow source rotation and magnification through explicit pixel/bin controls.
- Inspect released Parker weights and the declared fan-angle discrepancy.
- Compare three saved images on one scale, then reveal synthetic truth.
- Show the native crop and normalization alongside full-array scoring.
- Disclose truth staging, operator controls and saved-loss limits.

### Input

**Native source views.** Angle runs down sinogram
rows; detector position runs across columns. Preserve negative values, a common
projection scale and the 180-versus-116 sample counts.

### Supplied helpers

**Pixel geometry and exact source operations.** Geometry views must follow the
numerical angle convention. Unit-pixel controls are diagnostic fixtures, not
patient images or optimization traces. Do not substitute parallel-beam Radon.

### Reference or output

**Saved reconstructions and synthetic truth remain separate.** Preserve one raw
image scale before showing metric-specific cropping and normalization. Disclose
that solver inputs already include the phantom when revealing the reference.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| L1 · README | README, requirements and complete data directory, including the phantom. | Implement reconstruction; hidden-reference evaluation is not established. |
| L2 · + approach | L1 plus the numerical approach. | Implement the method and check geometry and operators. |
| L3 · + design | L2 plus software design. | Implement the interfaces; source and evaluation directories are not seeded by the local runner. |

## Difficulty

Magnification couples angle, pixel position and detector bins. Source operators
use different weights, and cropped normalized scores can conceal scale, offset
and image-edge errors. A good saved image alone does not establish the claimed
optimization method or general scanner accuracy.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_fan_beam/README.md)
- [Pinned geometry and operators](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_fan_beam/src/physics_model.py)
- [Pinned native pipeline](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_fan_beam/main.py)
- [Notebook with retained metric output](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_fan_beam/notebooks/ct_fan_beam.ipynb)
- [Pinned active scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Pinned numeric assets](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ct_fan_beam)
- [Canonical story](../stories/imaging101-fan-beam.story.md)
- [Source and numerical audit](../sources/imaging101-fan-beam-audit.json)
- [Cited upstream FBP source](https://github.com/leehoy/CTReconstruction/tree/5e70b4fc91347b7ecf1cb00e993072b51c5a47c6)
- [Cited upstream curved-detector projector](https://github.com/xtie97/CT_fanbeam_recon_numba/tree/e80a62c5f982d2680edf211b8e84648c6631df63)

## Coverage

One phantom, two scans and three saved images. Thirteen task sources, 60 shared
sources and all seven numeric/metadata assets are verified. The benchmark has an
MIT notice; the cited leehoy repository has GPL-2.0 license text, and the pinned
xtie97 tree has no license file. These provenance differences remain explicit;
the benchmark's MIT notice is not assigned to both upstreams. The cited curved-
detector ray tracer differs from this flat-detector pixel-driven adaptation.
Original arrays, source and historical scores remain intact.

## Gaps

The canonical story illustrates this pinned source condition. No fresh iterative
reconstruction, agent result, hidden-reference validity, current benchmark pass
or patient accuracy is established. Technical controls qualify the source's
operator descriptions without rewriting any saved result.
