---
schema: 2
id: mri-sampling
title: Missing frequency samples do not become recovered detail
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Unitless geometric phantom with a simplified Cartesian FFT model, not clinical MRI acquisition or model performance.
recipe: inverse-v1
asset_pack: inverse-problems-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-tv.md
acquisition: mri-cartesian
---

# Missing frequency samples do not become recovered detail

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. object

```beat
id: object
frames: 96
caption: Use the same object, but a different measurement model.
narration: MRI frequency samples are not CT line projections.
visual: Show the geometric field with its own title.
channels:
  observations:
  - 0.0
  - 0.0
  reconstruction:
  - 0.0
  - 0.0
  residual:
  - 0.0
  - 0.0
```

## 2. sampling

```beat
id: sampling
frames: 168
caption: Keep only the declared frequency samples.
narration: Every fourth row and the central eight rows are sampled in this fixture.
visual: Show the actual binary sampling mask and masked k-space.
channels:
  observations:
  - 0.0
  - 1.0
  reconstruction:
  - 0.0
  - 0.0
  residual:
  - 0.0
  - 0.0
```

## 3. baseline

```beat
id: baseline
frames: 168
caption: Zero-filled reconstruction leaves missing information.
narration: Inverse FFT gives a baseline image; no missing detail has been magically recovered.
visual: Display the actual magnitude baseline including artifacts.
channels:
  observations:
  - 1.0
  - 1.0
  reconstruction:
  - 0.0
  - 1.0
  residual:
  - 0.0
  - 0.0
```

## 4. check

```beat
id: check
frames: 144
caption: Consistency on observed samples is not full recovery.
narration: The complex image matches acquired coefficients while unobserved frequencies remain unknown.
visual: Show sampled-domain consistency and the acquisition mask together.
channels:
  observations:
  - 1.0
  - 1.0
  reconstruction:
  - 1.0
  - 1.0
  residual:
  - 0.0
  - 1.0
```
