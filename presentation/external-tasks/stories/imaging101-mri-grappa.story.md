---
schema: 2
id: imaging101-mri-grappa
title: "Calibrate GRAPPA across eight coils"
locale: en
purpose: "Explain native full source data and symbolic ACS interpolation without a result."
scope: "Synthetic full k-space visible; supplied R2/ACS20 rule; no blind condition or participant result."
recipe: imaging-grappa-v1
asset_pack: retained-imaging-grappa-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-grappa.md
- presentation/external-tasks/sources/imaging101-mri-grappa-resolution.json
- scripts/build_imaging_grappa_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full data visible \u00b7 huggingface.co/datasets/starpacker52/imaging-101"
narration: "Native full eight-coil synthetic k-space and Gaussian sensitivities are present. R2 alternating rows and twenty ACS lines are a supplied preprocessing rule, not missing raw data."
visual: "Native coil values and symbolic ACS rule/kernel; no reconstructed MRI."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "ACS examples differ from private reconstruction targets"
narration: "Full source targets are already solver-visible. Explicit educational reveal shows a native source k-space target, hidden initially and reset before paint on backward replay or exit."
visual: "Native coil values and symbolic ACS rule/kernel; no reconstructed MRI."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Fit cross-coil weights from ACS patches"
narration: "A 5×5 kernel collects acquired neighbor samples across eight coils. Source ridge coefficient is scaled by normal-matrix norm and source count; no weights, missing k-space or RSS image are computed."
visual: "Native coil values and symbolic ACS rule/kernel; no reconstructed MRI."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 288
caption: "Magnitude image remains unsubmitted"
narration: "Centered Fourier operations apply to spatial axes 0 and 1, not coil axis. Source GRAPPA NPZ differs from generic NPY. All prediction and performance fields remain unset."
visual: "Native coil values and symbolic ACS rule/kernel; no reconstructed MRI."
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
frames: 288
caption: "Reference and SSIM implementation must stay explicit"
narration: "Source RSS reference differs from bare phantom. Generic discovery prefers saved RSS when present; source local SSIM differs generic global surrogate. No measured method result is displayed."
visual: "Native coil values and symbolic ACS rule/kernel; no reconstructed MRI."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
