---
schema: 2
id: imaging101-ptychography
title: Recover phase from overlapping diffraction
locale: en
purpose: Explain native ptychography geometry, one intensity-projection diagnostic
  and the phase-sensitive scoring boundary.
scope: One synthetic dataset, saved complex result and labeled operator diagnostics;
  no fresh inverse or agent.
recipe: imaging101-ptychography-v1
asset_pack: retained-imaging101-ptychography-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-conventional-ptychography.md
- presentation/external-tasks/sources/imaging101-ptychography-audit.json
- scripts/audit_imaging101_ptychography.py
- scripts/build_imaging101_ptychography_assets.py
---

# Canonical conventional ptychography explanation

## Measure intensity at overlapping scan positions

```beat
id: inputs
scene: inputs
frames: 336
caption: Measure intensity at overlapping scan positions
narration: The published case contains one hundred simulated diffraction frames, each
  one hundred twenty-eight pixels square. A localized probe multiplies an object patch;
  a centered Fourier transform gives a detector wave, and magnitude squared gives
  intensity. The detector does not record object phase. These native frames use one
  common logarithmic display scale. They are synthetic measurements, not images of
  a specimen.
visual: Show native diffraction at scan indices zero, forty-nine and ninety-nine with
  calibrated sampling.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Place each probe window in one object grid

```beat
id: overlap
scene: overlap
frames: 576
caption: Place each probe window in one object grid
narration: The encoder stores row and column positions in meters. Divide by the object
  pixel size, round, then add two hundred seven to obtain the upper-left pixel of
  a one hundred twenty-eight pixel patch. The same conversion exactly reproduces every
  released position. All one hundred scan origins share the five hundred forty-two
  pixel object grid. Orange marks the selected scan and its extraction window. The
  windows overlap, but their rectangular coverage is not the true beam support or
  a map of reconstruction accuracy.
visual: Traverse three actual scan windows without showing the truth image.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Replace detector amplitude in one diagnostic step

```beat
id: projection
scene: projection
frames: 576
caption: Replace detector amplitude in one diagnostic step
narration: Start from the source initialization and propagate its probe times object
  patch to the detector. Multiply that wave by the square root of measured intensity
  divided by estimated intensity plus the source numerical floor. Its amplitude approaches
  the measured amplitude while retaining the current detector phase. These three examples
  are separate one-step diagnostics from the same initial state. No object or probe
  update follows here. Fitting one detector intensity is not recovering a shared object
  across all scans.
visual: Compare initialized, measured and projected intensities with the same count
  scale and actual residuals.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the saved complex object and error history

```beat
id: output
scene: output
frames: 480
caption: Inspect the saved complex object and error history
narration: The released result stores a complex object and a joint probe estimate.
  Inspect object amplitude and raw phase separately, then the actual three hundred
  fifty recorded error values. The native phase metrics reproduce the stored correlation
  of zero point nine seven five seven and normalized error of zero point zero four
  three four. They center each phase image before comparison. The error history instead
  sums relative intensity residuals before sequential updates; it is not the amplitude
  metric described in the approach. None of these views implies a fresh inverse run.
visual: Switch among saved amplitude, raw phase and all recorded error samples.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the synthetic phase object

```beat
id: reference
scene: reference
frames: 480
caption: Reveal the synthetic phase object
narration: 'Now reveal the synthetic truth on the same full object grid and the same
  raw phase scale. Its amplitude is one at every pixel. The bars are encoded only
  through a phase change of pi over two. This explains why preserving phase matters
  for this case. The dashed purple frame identifies reference material. This reader
  reveal is separate from solver access: the released data packet already contains
  both truth files.'
visual: Reveal native synthetic truth beside saved phase, preserving pixel geometry
  and common radians.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## All three assistance levels include the truth

```beat
id: staging
scene: staging
frames: 528
caption: All three assistance levels include the truth
narration: The local runner copies the complete data directory at all three assistance
  levels. That includes both ground truth formats, whose values are identical. Level
  two adds an approach, and level three also adds a design. We reproduced these file
  copies while intercepting every installation command. Source and evaluation directories
  are not seeded by this local route. A read-only source mount does not make references
  private. The released staging therefore does not establish a hidden-reference experiment.
visual: Highlight the actual files available at each assistance level.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Magnitude scores cannot distinguish these phases

```beat
id: scoring
scene: scoring
frames: 672
caption: Magnitude scores cannot distinguish these phases
narration: 'The active generic scorer converts complex arrays to magnitude. Correct
  truth, erased phase and reversed phase consequently become the same unit array.
  All three receive correlation one and mean squared error zero. Their normalized
  error is infinity because the reference magnitude has zero range, even for exact
  truth. The native phase calculation distinguishes these controls: erased phase has
  zero correlation and reversed phase has approximately negative one. No pass thresholds
  are shipped. An amplitude-only score does not validate this task’s requested complex
  object.'
visual: Compare reproduced generic and native phase controls with the zero-range failure
  explicit.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Keep the phase result and evaluation limits separate

```beat
id: limits
scene: limits
frames: 576
caption: Keep the phase result and evaluation limits separate
narration: 'This audit establishes exact source measurements, native geometry, a small
  operator fixture, the saved result and the evaluator’s behavior. It does not establish
  a new reconstruction, agent capability, private-reference validity or a benchmark
  pass. Source prose and code also differ: the code applies momentum with a five percent
  random trigger, while the approach describes a periodic step. The original arrays
  and metrics remain unchanged. Benchmark attribution and original PtyLab academic
  and non-commercial terms are retained separately.'
visual: End with source-backed findings and the unestablished claims.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
