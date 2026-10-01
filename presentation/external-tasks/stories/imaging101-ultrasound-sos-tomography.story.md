---
schema: 2
id: imaging101-ultrasound-sos-tomography
title: "Separate ultrasound speed and slowness conventions"
locale: en
purpose: "Explain exact synthetic projection samples and unsubmitted inverse contracts."
scope: "Native synthetic source; unresolved time/path calibration; source truth visible; no participant result."
recipe: imaging-ultrasound-sos-v1
asset_pack: retained-imaging-ultrasound-sos-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-ultrasound-sos-tomography.md
- presentation/external-tasks/sources/imaging101-ultrasound-sos-tomography-resolution.json
- scripts/build_imaging_ultrasound_sos_assets.py
---

# native-detector-sums

```beat
id: native-detector-sums
scene: input
frames: 168
caption: "Time units unresolved \u00b7 huggingface.co/datasets/starpacker52/imaging-101"
narration: "Native noisy parallel-beam samples and angles are exact indexed synthetic source values. Radon lacks physical pixel-length scaling; do not label seconds or acquired ring paths."
visual: "Indexed native detector values plus symbolic signed-slowness rule; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# signed-slowness-baseline

```beat
id: signed-slowness-baseline
scene: operation
frames: 168
caption: "Convert signed slowness with the right baseline"
narration: "Delta slowness is 1/c\u22121/1500. Slower speed gives positive perturbation; faster speed gives negative. Main disables positivity; source defaults differ. No projection, inverse or reconstruction is executed."
visual: "Indexed native detector values plus symbolic signed-slowness rule; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# source-inverse-conventions

```beat
id: source-inverse-conventions
scene: operation
frames: 168
caption: "FBP, source SART and TV are distinct conventions"
narration: "Source FBP uses ramp-filtered backprojection. Its named SART performs full-sinogram residual updates; textbook row-action equivalence is unverified. Main TV uses 300 iterations, lambda 1e-6 and positivity false, differing from helper defaults. These are source conventions, not new reconstructions."
visual: "Indexed native detector values plus symbolic signed-slowness rule; no reconstruction."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# adjoint-normalization-boundary

```beat
id: adjoint-normalization-boundary
scene: operation
frames: 168
caption: "Adjoint scale and stopping are source assumptions"
narration: "The physics helper scales unfiltered iradon by pi over twice the angle count; TV updates omit that factor. Exact discrete adjoint and step scaling remain unverified. A fixed iteration count and approximate norm do not establish convergence. No operator or solver is executed."
visual: "Indexed native detector values plus symbolic signed-slowness rule; no reconstruction."
channels:
  progress: [1, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# unsubmitted-speed-artifact

```beat
id: unsubmitted-speed-artifact
scene: output
frames: 168
caption: "Speed NPY differs from multiple source maps"
narration: "Generic output/reconstruction.npy is one real speed map. Main source writes multiple speed/slowness arrays to reconstructions.npz. No prediction, clinical finding, metric or verdict is supplied."
visual: "Indexed native detector values plus symbolic signed-slowness rule; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# late-source-visible-truth

```beat
id: late-source-visible-truth
scene: helper
frames: 168
caption: "Source phantom is already solver-visible"
narration: "Clean/full projections and speed/slowness phantom are visible in supplied data. Explicit educational reveal covers only this teaching view, resets before paint on backward replay and exit, and does not create a private reference."
visual: "Indexed native detector values plus symbolic signed-slowness rule; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# speed-slowness-reference-boundary

```beat
id: speed-slowness-reference-boundary
scene: limits
frames: 168
caption: "Full speed scoring differs from cropped slowness"
narration: "Generic scorer uses 16384 speed entries, range-normalized RMSE and uncentered cosine without flux scaling. Main uses 0.8 cropped slowness over 10,404 entries. Source constant-range NRMSE returns zero while the generic rule returns infinity. Operator/adjoint and thresholds remain source contract boundaries."
visual: "Indexed native detector values plus symbolic signed-slowness rule; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
