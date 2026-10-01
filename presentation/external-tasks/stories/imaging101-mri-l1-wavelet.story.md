---
schema: 2
id: imaging101-mri-l1-wavelet
title: Keep complex MRI measurements separate from wavelet outcomes
locale: en
purpose: "Explain released sampling, complex SENSE and wavelet regularization without outcome claims."
scope: "Native R4 differs from README R8 and source truth loader; participant output absent."
recipe: imaging101-wavelet-v1
asset_pack: retained-imaging101-wavelet-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-l1-wavelet.md
- presentation/external-tasks/sources/imaging101-mri-l1-wavelet-resolution.json
- scripts/build_imaging_wavelet_assets.py
---
# Input

```beat
id: input
scene: input
frames: 168
caption: "README/loader differ · Official Imaging101 MRI acquisition"
narration: "Released native masked k-space is not an image reconstruction; loader mismatch persists."
visual: "Native mask/coil k-space display; symbolic wavelet rule; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Sampling

```beat
id: sampling
scene: operation
frames: 168
caption: "Sampling columns and coil maps are input semantics"
narration: "Mask sampling 80 of 320 columns on 15 coils differs from README condition."
visual: "Native mask/coil k-space display; symbolic wavelet rule; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Forward model

```beat
id: forward-model
scene: operation
frames: 168
caption: "Inspect complex forward model and source coil displays"
narration: "Coil displays have separate log-magnitude scales; optimizer uses complex samples."
visual: "Native mask/coil k-space display; symbolic wavelet rule; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Wavelet prior

```beat
id: wavelet-prior
scene: operation
frames: 168
caption: "Wavelet shrinkage preserves coefficient phase"
narration: "Authored coefficient example only; no native reconstruction or convergence."
visual: "Native mask/coil k-space display; symbolic wavelet rule; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 168
caption: "Participant reconstruction and score remain empty"
narration: "Saved source output is not new model performance."
visual: "Native mask/coil k-space display; symbolic wavelet rule; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Source rules

```beat
id: source-rules
scene: reference
frames: 168
caption: "Explicitly reveal source and evaluator rules"
narration: "Solver-visible mvue versus phantom loader and magnitude-only scoring; no truth image."
visual: "Native mask/coil k-space display; symbolic wavelet rule; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 168
caption: "Resolve README/data/loader and rights gaps"
narration: "Preserve source condition and no-outcome boundary."
visual: "Native mask/coil k-space display; symbolic wavelet rule; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
