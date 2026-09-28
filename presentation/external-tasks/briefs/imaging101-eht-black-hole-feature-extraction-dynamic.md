# Infer evolving black-hole image features

Infer distributions of **four crescent parameters at ten independent snapshots**
from synthetic radio-interferometry measurements.

## Value

Parameter distributions describe which source shapes fit indirect observations.
Following them through time can expose variability and uncertainty.

## Given

### Original data

**28 complex visibilities per snapshot**, baseline coordinates, station pairs and
noise estimates from eight EHT-inspired stations. Ten epochs span **0–7.2 hours**
at 0.8-hour intervals within an eight-hour synthetic observation window.

### Supplied helpers

Metadata specifies a four-parameter crescent and 64×64 grid over 120 μas.
**All L1–L3 copy both ground-truth arrays and answer-bearing `data/meta_data`
into the solver workspace.** L2 adds approach guidance; L3 adds software design.
Source code and saved evaluation outputs are not seeded.

### Callable tools

Python and declared numerical/flow dependencies. The audit used existing NumPy
for fixed arithmetic and retained arrays; no training or runtime installation ran.

### Reference-only material

Saved parameter samples, weights, mean images and notebook plots support reader
comparison. Supplied truth is solver-visible; a reader reveal does not make it private.

## Task specification

Derive closure phases from visibility triangles and log closure amplitudes from
four-station ratios. Fit a Real-NVP distribution over ring-center diameter,
Gaussian width, asymmetry and source angle, then importance-weight samples.
Each frame is fitted independently; **there is no temporal coupling**.

## Expected output

The native deliverable contains parameter samples **(10, 10000, 4)**, weights
**(10, 10000)** and mean images **(10, 64, 64)**. Parameter units are μas, μas,
dimensionless and degrees. Stored images sum to approximately one, despite the
README's Jy/pixel label; the observation generator uses **0.6 Jy**.

The live local harness instead requests `output/reconstruction.npy`. It accepts
the image stack and rejects the native posterior array. These contracts differ.

## Evaluation

- **Native saved result:** angle mean absolute error **6.08°** across ten frames;
  frame 4 has **−26.24° bias**. Weighted means and standard deviations reproduce
  within float32 rounding.
- **Weight concentration:** effective sample sizes are **4.3–110.9 of 10,000**.
  Stored sample count alone does not establish reliable uncertainty.
- **Live image score:** cosine NCC **0.996218**, range-normalized error **0.022811**.
  It does not evaluate parameter distributions; published pass thresholds are absent.

An oracle collapsed exactly at truth has zero parameter error and zero spread.
This answer-based control shows why a point-error score cannot validate uncertainty.

## Visual explanation

[Canonical story](../stories/imaging101-eht-features-dynamic.story.md).

### Workflow

- Inspect time-indexed measurements and derive gain-invariant closure quantities.
- Follow independent crescent fits and inspect retained weighted distributions.
- Reveal supplied truth, weight concentration and separate scoring contracts.

### Input

Native arrays are available and inspected. The source forms **56 phase combinations
and 70 amplitude combinations**, with linear ranks **21 and 19** respectively.
They are correlated combinations, not 126 independent measurements.

### Supplied helpers

Use a labeled four-parameter schematic. Diameter is twice the Gaussian ring's
center radius, not a sharp outer boundary; width is Gaussian σ. Source angle
follows its array formula; celestial orientation is not independently verified.

### Reference or output

Preserve all ten frames, unit-flux intensity scales, original weights and explicit
truth reveals. Histogram bins and any density smoothing must be labeled.
Error bars describe weighted spread, not a demonstrated coverage guarantee.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data including answers, requirements. | Implement inference; answer copying is possible. |
| L2 · + approach | L1 plus per-frame flow and weighting guidance. | Design and implement the method. |
| L3 · + design | L2 plus interfaces and numerical details. | Implement and reconcile the source contract. |

## Difficulty

Sparse observations and concentrated importance weights make uncertainty assessment
consequential. Ten snapshots from one synthetic sequence do not establish calibration,
blind inference ability or performance on actual Sgr A* observations.

## Sources

- [Pinned task definition](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_feature_extraction_dynamic/README.md)
- [Pinned closure preparation](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_feature_extraction_dynamic/src/preprocessing.py)
- [Pinned inference and weighting](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/eht_black_hole_feature_extraction_dynamic/src/solvers.py)
- [Pinned generic image scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Pinned parameter scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/task_scoring.py)
- [EHT variability paper cited by the release](https://arxiv.org/abs/2311.08697v1)
- [Source audit, controls and provenance](../sources/imaging101-eht-features-dynamic-audit.json)

## Coverage

14 task sources, 60 shared sources and all nine released assets verified.
The fixed crescent fixture, closure algebra, saved summaries, scoring and L1–L3
staging were audited. The native arrays were visually inspected locally.

## Gaps

Pinned source applies **70 times more likelihood weight during training than
during importance reweighting**, relative to the same log-density term. Checkpoints
and latent/log-density arrays are absent, so corrected inference cannot be inferred.
The no-filesystem scorer fallback cannot find the released NPZ truth. The source
uses linear angle statistics; a fixed wrap-boundary counterexample is retained,
but these saved samples do not cross that boundary. Original results remain intact.
The canonical story is linked above. Export and visual acceptance are recorded
separately in the [completion ledger](../../EXPLAINER-LEDGER.json).
