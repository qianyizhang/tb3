# Reconstruct black-hole radio brightness

Recover a **64×64 radio-brightness image** from sparse, gain-corrupted Fourier
measurements of one synthetic M87-like ring.

## Value

Closure quantities cancel station gain factors, helping separate source structure
from telescope calibration effects.

## Given

### Original data

**421 complex visibility samples across 21 station pairs**, with Fourier
coordinates, station IDs and noise estimates. Both calibrated and corrupted
observations are supplied.

### Supplied helpers

The release includes **269 per-scan closure phases and 233 log amplitude ratios**,
their uncertainties and Fourier coordinates. Metadata declares 2 μas pixels and
0.6 Jy total flux. **All L1–L3 also copy `data/ground_truth.npz` into the solver
workspace.** L2 adds an approach; L3 adds software design.

### Callable tools

Python and declared numerical dependencies. This audit used fixed arithmetic;
no observation simulation, optimizer, runtime installation or agent trial ran.

### Reference-only material

Saved comparison images and fixtures remain outside initial staging. Ground truth
inside `data/` is solver-visible; a reader reveal cannot make it private.

## Task specification

Implement the Fourier operator and regularized image fitting. Compare visibility,
amplitude-plus-phase and closure-only data terms while preserving scan identity.

## Expected output

The live harness requires `output/reconstruction.npy`, shape **(64, 64)**. Its
reference sums to **one**; the separate physical image sums to **0.6 Jy**.
The README's Jy/pixel label does not distinguish these conventions.

## Evaluation

Saved corrupted closure-only output has cosine NCC **0.604421**. Its live
range-normalized error is **0.114238**; the published flux-normalized convention
gives **0.1384**. No pass thresholds are supplied. These are saved-array replays,
not a fresh reconstruction or evidence of general method superiority.

## Visual explanation

### Workflow

- Inspect sparse Fourier samples and the two supplied observation conditions.
- Combine simultaneous baselines into gain-canceling closure quantities.
- Reveal saved reconstructions, truth, flux differences and scoring limits.

### Input

Native arrays are available and inspected. No conjugate measurements are added.
The stored calibrated/corrupted closures differ because the source generates noisy
observations; they are not a pure gain-only control.

### Supplied helpers

Use the supplied per-scan closure arrays. The small preprocessing helper instead
selects the first occurrence of each station pair, producing only 35 triangles
and 35 quadrangles and mixing Fourier coordinates from different scans.

### Reference or output

Preserve the 64×64 array, 128 μas field and stored pixel sums. Label any flux
normalization or logarithmic display. Distinguish retained reference outputs from
agent predictions, and show truth only on an explicit reader reveal.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, observations, closures, metadata and ground truth. | Implement imaging; answer copying is possible. |
| L2 · + approach | L1 plus algorithm guidance. | Design and implement the method. |
| L3 · + design | L2 plus interfaces and numerical details. | Implement and reconcile source conventions. |

## Difficulty

Sparse Fourier coverage and nonlinear closure losses leave substantial dependence
on image priors. Exact gain cancellation does not establish noise immunity,
unique reconstruction or blind inference when answers are supplied.

## Sources

- [Pinned task definition](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_original/README.md)
- [Released forward operator](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_original/src/physics_model.py)
- [Live reference scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Local staging](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/local_runner.py)
- [Source, fixture and saved-array audit](../sources/imaging101-eht-original-audit.json)

## Coverage

One synthetic static source, two supplied observation conditions and three retained
comparison methods across L1–L3 assistance. This astronomy task is non-medical.

## Gaps

Canonical story, Explorer integration and video acceptance remain pending. The
audit retains inconsistent metric denominators, a malformed forward fixture,
a factor-of-two visibility-loss convention and a TV-gradient sign defect.
The six main saved comparisons use entropy regularizers, so the TV defect alone
does not explain their outcomes. Optimizer convergence and Docker fallback
execution are unverified; source discrepancies are not repaired scientific evidence.
