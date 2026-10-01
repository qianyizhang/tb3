---
schema: 2
id: imaging101-mri-noncartesian-cs
title: Trace radial coordinates without inventing an MRI reconstruction
locale: en
purpose: "Explain actual synthetic radial samples, NUFFT/DCF and complex-wavelet contracts."
scope: "Source-visible phantom; uncalibrated FOV/time/runtime; no participant outcome."
recipe: imaging101-noncartesian-v1
asset_pack: retained-imaging101-noncartesian-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-noncartesian-cs.md
- presentation/external-tasks/sources/imaging101-mri-noncartesian-cs-resolution.json
- scripts/build_imaging_noncartesian_assets.py
---
# source-input-and-gap

```beat
id: source-input-and-gap
scene: input
frames: 168
caption: "Synthetic source; output absent · Official Imaging101 acquisition"
narration: "Actual trajectory coordinates, source-visible phantom and missing participant outcome."
visual: "Actual coordinate diagram; symbolic algorithm rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# radial-coil-coordinate-contract

```beat
id: radial-coil-coordinate-contract
scene: operation
frames: 168
caption: "Keep coordinate units, coil and time axes distinct"
narration: "Grid-scaled radial samples do not supply physical FOV or millisecond timing."
visual: "Actual coordinate diagram; symbolic algorithm rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# display-density-compensation

```beat
id: display-density-compensation
scene: operation
frames: 168
caption: "Inspect display subsets and density compensation roles"
narration: "Native samples shown 1-in-16; display selection never changes acquisition or computes weights."
visual: "Actual coordinate diagram; symbolic algorithm rules; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# complex-wavelet-consistency

```beat
id: complex-wavelet-consistency
scene: operation
frames: 168
caption: "Complex data consistency differs from gridding baseline"
narration: "Wavelet coefficient illustration only; no native NUFFT/reconstruction performed."
visual: "Actual coordinate diagram; symbolic algorithm rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# participant-output-empty

```beat
id: participant-output-empty
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Actual coordinate diagram; symbolic algorithm rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reader-source-metric-rules

```beat
id: reader-source-metric-rules
scene: reference
frames: 168
caption: "Reveal source-truth and magnitude-scoring rules"
narration: "Source phantom solver-visible; educational rules only, no private or image reference."
visual: "Actual coordinate diagram; symbolic algorithm rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# reopen-coordinate-and-runtime-contract

```beat
id: reopen-coordinate-and-runtime-contract
scene: limits
frames: 168
caption: "Reconcile units and runtime before method claims"
narration: "No calibrated physical geometry, time or participant artifact."
visual: "Actual coordinate diagram; symbolic algorithm rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
