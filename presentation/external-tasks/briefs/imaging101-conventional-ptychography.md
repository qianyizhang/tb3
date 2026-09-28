# Recover a complex image from overlapping diffraction patterns

Recover object amplitude and phase from 100 overlapping, simulated far-field
diffraction measurements. The released saved result has useful phase structure;
the active generic evaluator discards that phase and cannot establish this task's
central requirement.

## Value

Ptychography connects a moving illumination window to intensity-only detector
measurements. Overlap constrains a shared complex object and probe. A metric that
retains only amplitude can miss the information this particular object encodes.

## Given

### Original data

Pinned `raw_data.npz` contains `ptychogram`, float32 `(100,128,128)`, and
`encoder`, float32 `(100,2)` in meters, ordered row then column. This is a
synthetic USAF phase-chart case, not an acquired specimen. The released HDF5
contains exactly the same diffraction and encoder values. Counts range from
approximately 5.07e-11 to 32,966; source generation adds a Poisson draw to its
expectation, so the stated 14-bit scale is not a hard upper bound.

### Supplied helpers

Metadata specifies wavelength 632.8 nm, sample-to-detector distance 50 mm,
128 detector pixels at 72 micrometers, and a 542-pixel object. Object/probe
sampling is 3.4331597222 micrometers. The initialization estimates the probe from
a circular aperture and focusing phase; the true probe is not a supplied array.
The file `positions.npy` agrees exactly with rounded encoder-to-pixel positions.
L2 adds an approach; L3 also adds a design.

### Callable tools

Python numerical dependencies. The published 32-pixel forward/FFT fixture and
selected initial-state intensity projections were checked locally with existing
packages. No agent, inverse iterations, dataset generation or installation ran.

### Reference-only material

Both `ground_truth.npy` and `ground_truth.npz:object` contain the same complex64
`(542,542)` synthetic truth. All 293,764 magnitudes are exactly one; 11,970 pixels
encode bars at phase pi/2 and the others have phase zero. Actual L1/L2/L3 local
file seeding copies **both truth files** because they are inside `data/`.
Reader-facing reference reveals must not be mistaken for private evaluation.

## Task specification

For each scan, extract a 128-pixel object patch, multiply by the probe, apply the
centered unitary 2D FFT and square the magnitude. The source reconstruction
projects measured intensity onto its current detector wave, back-propagates,
updates object and probe, and applies momentum and constraints. The code uses
a 5% random momentum trigger; the supplied approach's periodic description is
different. No reconstruction trajectory is synthesized by this explainer audit.

## Expected output

Scientifically, a complex object image with amplitude and phase, plus the
jointly estimated probe. The source `main.py` saves `recon.hdf5`, with object
shape `(1,1,1,1,542,542)` and probe shape `(1,1,1,1,128,128)`.
The active generic end-to-end harness instead requires `output/reconstruction.npy`
and compares squeezed, magnitude-reduced arrays. Native HDF5 output and that
harness contract are distinct.

## Evaluation

The stored 350-iteration object reproduces the native full-frame, mean-centered
phase NCC **0.9757169** and phase NRMSE **0.0434154**, matching shipped rounded
values. This is saved-output replay, not a new solver result. It performs no
registration or phase unwrapping. The phase-erased unit object gives native
phase NCC **0** and NRMSE **0.1977035**.

The generic scorer selects `data/ground_truth.npy` and discards complex phase.
Correct truth, phase-erased ones and conjugated truth all receive NCC **1** and
MSE **0**. Their generic NRMSE is **infinity**, even for exact truth, because
reference magnitude has zero range. The saved reconstruction's generic NCC is
0.728639. Shipped metrics contain no pass thresholds, so pass status is unavailable.

The stored error history ends at **1.8429171**. Source code sums relative
intensity L1 residuals before each sequential update; it is not the amplitude
metric described in the approach. A separate forward-only check of final saved
arrays gives summed relative intensity L1 **3.4429931** and global squared
amplitude error **0.00110562**. These use different metrics and evaluation states.

## Visual explanation

### Workflow

- Inspect native simulated diffraction frames and physical sampling.
- Map encoder coordinates into overlapping extraction windows.
- Illustrate one intensity projection from the source initialization.
- Inspect saved amplitude, phase and the actual 350-point error history.
- Reveal synthetic truth and compare phase-sensitive and magnitude-only controls.

### Input

**Native source views.** Three selected native
frames at scans 0, 49 and 99, with their actual encoder positions, can illustrate
the operation. Rectangular windows cover 144,986/293,764 object pixels; they are
not an illumination support or accuracy mask.

### Supplied helpers

**Geometry and initialization, not a recovered object.** The selected projection
uses the source seed-42 initial state. It changes detector-wave amplitude without
updating object or probe. Its measured-intensity agreement is not reconstruction.

### Reference or output

**Saved result and synthetic truth remain separate.** The released complex result
is inspected as stored. Truth appears only after a reader reveal in the canonical
story, with its actual solver-visible staging disclosed.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| L1 · README | README, requirements and complete data directory, including both truth files. | Implement reconstruction; this packet does not establish hidden-reference evaluation. |
| L2 · + approach | L1 plus the proposed algorithm. | Resolve differences between prose and executable behavior, then implement. |
| L3 · + design | L2 plus software design. | Implement numerical details; source and evaluation directories are not seeded by the local runner. |

## Difficulty

Intensity discards phase. Overlap couples scans to a shared object and probe,
while probe estimation and phase ambiguities complicate recovery. Constant
truth amplitude makes magnitude-only metrics particularly uninformative here.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/conventional_ptychography/README.md)
- [Pinned source solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/conventional_ptychography/src/solvers.py)
- [Pinned active scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Pinned numeric assets](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/conventional_ptychography)
- [Canonical story](../stories/imaging101-ptychography.story.md)
- [Source and numerical audit](../sources/imaging101-ptychography-audit.json)
- [Original PtyLab attribution](https://github.com/PtyLab/PtyLab.py)

## Coverage

One synthetic object and its stored reconstruction across released L1/L2/L3
packets. Nine numeric/metadata assets and 13 task-source files are pinned and
verified. Original benchmark MIT and upstream PtyLab academic/non-commercial
license texts are retained separately; no relicensing or original-toolbox
equivalence is claimed.

## Gaps

The canonical story illustrates this pinned source condition. No fresh inverse,
agent performance, hidden-reference validity,
benchmark pass or general specimen accuracy is established. Original scores and
arrays remain unchanged.
