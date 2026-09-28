# Recover lens geometry from refracted fringe patterns

Estimate a lens's curvature, thickness and pose from how it bends displayed
stripes seen by two cameras. This is **refraction through two lens surfaces**.

## Value

Optical metrology links distorted patterns to lens geometry through calibrated
cameras, a display and a differentiable ray tracer.

## Given

### Original data

The README specifies lens-present and lens-absent stacks, each
`(1, 3, 8, 2, 2048, 2048)`: batch, fringe periods, shifts, cameras, rows, columns.
**Raw stacks are absent from the pinned benchmark dataset.** Saved notebook
figures preserve normalized camera views; they are not raw intensity samples.

### Supplied helpers

Camera/display calibration, a lens prescription and periods 70/100/110 pixels.
The source selects a centered `768 × 768` crop, starting at pixel `(640, 640)`.

### Callable tools

Python, PyTorch differentiation and optical/optimization code. The audit executes
only fixed preprocessing and scoring controls, with no ray tracing or optimization.

### Reference-only material

**Manufacturer truth and the lens prescription are solver-visible:** L1–L3 seed
the complete data directory. Lens-absent images are measurement inputs. Saved
reconstructions and metric fixtures are not seeded.

## Task specification

Extract phase from shifted fringes, infer display intersections and fit the two
refracting surfaces. Keep calibration, valid-pixel masks and coordinate units consistent.

## Expected output

Eight lens parameters: two curvatures (`mm^-1`), thickness and three origin
coordinates (`mm`), and two tilts (degrees). The native file is
`optimized_params.json`; the generic end-to-end format is incompatible with this
three-key scalar truth archive.

## Evaluation

The custom helper compares only two radii and thickness, ignoring pose. Generic
scoring rejects even the correct three-parameter truth vector; a one-radius oracle
has infinite range-normalized error. Saved metrics contain no NCC/NRMSE pass thresholds.

## Visual explanation

### Workflow

- Inspect calibrated camera views and shifted fringes
- Extract phase and fit refracting lens geometry
- Reveal saved parameters and the evaluator's limits

### Input

**Source-derived camera view available.** Pinned notebook cells 9–10 contain
normalized, masked measurement panels. The full camera archive remains unavailable;
rendered panels cannot recover quantitative raw intensities.

### Supplied helpers

**Given material.** Calibration and the lens prescription define the setup.
A separate `32 × 32` synthetic fixture demonstrates four-step phase extraction;
it is not a native camera sample.

### Reference or output

**Saved source output, not a fresh prediction.** Notebook comparisons show measured,
initially modeled and optimized views. The plotting code saves the same two-camera
figure twice; repeated notebook rows are not extra cameras or cases. Reader
reference reveals must remain distinct from measurement panels.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| L1 · README | README, data and requirements, including available truth/prescription. | Choose and implement the inversion. |
| L2 · + approach | Adds phase analysis, differentiable tracing and LM optimization. | Implement the numerical method. |
| L3 · + design | Adds module and function contracts. | Implement the code and preserve units and masks. |

## Difficulty

Curvature, thickness and pose interact in the ray geometry. A three-parameter
score cannot establish correct pose or native image agreement.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/differentiable_deflectometry/README.md)
- [Pinned notebook with measurement views](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/differentiable_deflectometry/notebooks/diff_deflectometry.ipynb)
- [Original implementation and raw-data locator](https://github.com/vccimaging/DiffDeflectometry/tree/df23bef16ed92d597f9d9397f313de54e9d4015a)
- [Canonical story](../stories/imaging101-deflectometry.story.md)
- [Source audit, controls and limitations](../sources/imaging101-deflectometry-audit.json)

## Coverage

One retained LE1234-A source example, two cameras and synthetic helper fixtures.
Thirteen task sources, 60 shared files and 43 benchmark assets were verified.
No fresh optical fit, agent evaluation or medical inference.

## Gaps

The upstream raw archive is listed as 3.22 GB; bounded retrieval failed with TLS
and connection errors. Native screen-intersection metrics cannot be replayed from
saved figures. The canonical story preserves this replay limit.
