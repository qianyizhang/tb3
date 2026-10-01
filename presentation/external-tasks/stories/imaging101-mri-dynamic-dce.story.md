---
schema: 2
id: imaging101-mri-dynamic-dce
title: "Couple dynamic MRI frames with temporal regularization"
locale: en
purpose: "Explain native synthetic masked k-space and unsubmitted temporal inverse."
scope: "Retained 15% acquisition; source truth solver-visible; no reconstruction/perfusion result."
recipe: imaging-dynamic-mri-v1
asset_pack: retained-imaging-dynamic-mri-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-dynamic-dce.md
- presentation/external-tasks/sources/imaging101-mri-dynamic-dce-resolution.json
- scripts/build_imaging_dynamic_mri_assets.py
---

# Input

```beat
id: input
scene: input
frames: 192
caption: "No reconstruction \u00b7 huggingface.co/datasets/starpacker52/imaging-101"
narration: "Native twenty-frame complex k-space and binary Cartesian masks sample 2457 points per 128-square frame. No coil axis or patient geometry is supplied."
visual: "Native point mask and symbolic temporal coupling; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 192
caption: "Covered synthetic source truth \u00b7 not private gold"
narration: "Source truth is solver-visible in data. Only an explicit educational reveal displays a source pixel series, reset on exit/backward replay; no perfusion parameter is inferred."
visual: "Native point mask and symbolic temporal coupling; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 1

```beat
id: operation-0
scene: operation
frames: 168
caption: "Native measurement axes"
narration: "Twenty synthetic frames retain native order. The source model uses spatial encoding and nineteen adjacent-index differences, without concentration calibration or a computed reconstruction."
visual: "Canonical step and source-method contract; no Fourier or solver execution."
channels:
  progress: [0.0, 0.0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 2

```beat
id: operation-1
scene: operation
frames: 168
caption: "Masked consistency"
narration: "Twenty synthetic frames retain native order. The source model uses spatial encoding and nineteen adjacent-index differences, without concentration calibration or a computed reconstruction."
visual: "Canonical step and source-method contract; no Fourier or solver execution."
channels:
  progress: [0.3333333333333333, 0.3333333333333333]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 3

```beat
id: operation-2
scene: operation
frames: 168
caption: "Temporal neighbors"
narration: "Twenty synthetic frames retain native order. The source model uses spatial encoding and nineteen adjacent-index differences, without concentration calibration or a computed reconstruction."
visual: "Canonical step and source-method contract; no Fourier or solver execution."
channels:
  progress: [0.6666666666666666, 0.6666666666666666]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 4

```beat
id: operation-3
scene: operation
frames: 168
caption: "Magnitude artifact"
narration: "Twenty synthetic frames retain native order. The source model uses spatial encoding and nineteen adjacent-index differences, without concentration calibration or a computed reconstruction."
visual: "Canonical step and source-method contract; no Fourier or solver execution."
channels:
  progress: [1.0, 1.0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 192
caption: "Magnitude sequence remains unsubmitted"
narration: "Generic reconstruction.npy differs from source TV reconstruction NPZ. The display contains no image reconstruction, model metric or saved reference result."
visual: "Native point mask and symbolic temporal coupling; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 192
caption: "Retained acquisition and evaluator must stay matched"
narration: "Generator defaults25percent and noise0.02 differ retained15percent and0.005. Whole-volume metrics differ from frame averages; synthetic arbitrary intensity is not contrast concentration or patient perfusion."
visual: "Native point mask and symbolic temporal coupling; no reconstruction."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
