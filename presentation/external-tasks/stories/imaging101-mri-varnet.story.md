---
schema: 2
id: imaging101-mri-varnet
title: Trace VarNet inputs without inventing a learned reconstruction
locale: en
purpose: "Explain native k-space, source mask and missing checkpoint boundaries."
scope: "Actual source-derived input; checkpoint absent; local research only."
recipe: imaging101-varnet-v1
asset_pack: retained-imaging101-varnet-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-varnet.md
- presentation/external-tasks/sources/imaging101-mri-varnet-resolution.json
- scripts/build_imaging_varnet_assets.py
---
# checkpoint-and-source-gap

```beat
id: checkpoint-and-source-gap
scene: input
frames: 168
caption: "Checkpoint absent · Official Imaging101 acquisition"
narration: "Actual k-space retained; promised checkpoint absent and no participant reconstruction."
visual: "Actual frequency-sample magnitudes; symbolic model rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# complex-encoding-and-input-axes

```beat
id: complex-encoding-and-input-axes
scene: operation
frames: 168
caption: "Keep complex encoding and display magnitude distinct"
narration: "Centered orthonormal FFT is a model convention; preview computes no transform or image."
visual: "Actual frequency-sample magnitudes; symbolic model rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# native-coil-and-mask-display

```beat
id: native-coil-and-mask-display
scene: operation
frames: 168
caption: "Inspect native samples and the saved mask"
narration: "Three display coils use the same scale; saved equispaced offset is not Bernoulli sampling."
visual: "Actual frequency-sample magnitudes; symbolic model rules; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# learned-cascade-and-calibration-boundary

```beat
id: learned-cascade-and-calibration-boundary
scene: operation
frames: 168
caption: "Keep learned cascades and calibration behind the model boundary"
narration: "Constructor and input shape known; checkpoint and exact external runtime remain absent."
visual: "Actual frequency-sample magnitudes; symbolic model rules; actual output empty."
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
visual: "Actual frequency-sample magnitudes; symbolic model rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reader-source-and-metric-rules

```beat
id: reader-source-and-metric-rules
scene: reference
frames: 168
caption: "Reveal source-truth and magnitude-scoring rules"
narration: "Source RSS is solver-visible; rules only, never private clinical truth or a new output."
visual: "Actual frequency-sample magnitudes; symbolic model rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# reopen-weights-runtime-case-rights

```beat
id: reopen-weights-runtime-case-rights
scene: limits
frames: 168
caption: "Resolve weights, runtime, case and rights"
narration: "No participant model outcome or clinical finding; local use does not authorize publication."
visual: "Actual frequency-sample magnitudes; symbolic model rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
