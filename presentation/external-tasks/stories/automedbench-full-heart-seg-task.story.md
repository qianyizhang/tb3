---
schema: 2
id: automedbench-full-heart-seg-task
title: Segment the left atrium in cardiac MRI
locale: en
purpose: "Explain Full segmentation inputs, native-grid operation, output labels and the source/reference boundary for cardiac MRI."
scope: "Upstream training example; Full membership unverified. Labels gated; output empty."
recipe: automed-full-heart-seg-v1
asset_pack: retained-automed-full-heart-seg-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-heart-seg-task.md
- presentation/external-tasks/sources/automedbench-full-heart-seg-task-resolution.json
- scripts/build_automed_seg_a_assets.py
---

# Inspect the unmarked input

```beat
id: input
scene: input
frames: 288
caption: "Inspect the unmarked input"
narration: "Official MSD Task02_Heart training MRI la_007 and matching left-atrium label, 320×320×130 voxels. This upstream training example is not proven to be in the Full selected cases. It begins without labels or output."
visual: "Unmarked native slice from the official upstream cardiac MRI."
channels:
  slice: [0, 0]
  format: [0, 0]
  reference: [0, 0]
```

# Move through the 3D input

```beat
id: stack
scene: stack
frames: 336
caption: "Move through the 3D input"
narration: "Inspect three preselected native MRI planes without a mask. This post-hoc teaching selection does not test locating the left atrium; the task target is left atrium, not whole heart."
visual: "Three native-k source planes animate; no source mask is mounted. Header RAS does not independently verify patient-plane orientation."
channels:
  slice: [0, 1]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Assign task-specific tissue IDs

```beat
id: labels
scene: labels
frames: 300
caption: "Assign task-specific tissue IDs"
narration: "The required combined label map uses 0 background, 1 left atrium (task label heart). The IDs describe mutually exclusive output voxels."
visual: "Codebook and task-specific label distinctions; no patient prediction."
channels:
  slice: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Save one aligned NIfTI label map

```beat
id: schema
scene: schema
frames: 324
caption: "Save one aligned NIfTI label map"
narration: "Each Full case requires agents_outputs/{case_id}/dseg.nii.gz. The task needs a 3D integer map aligned to its input. The formatter checks rounded IDs and conditional shape, not exact integer voxels, dimensionality, or affine equality. No dseg file was generated."
visual: "Exact output path and integer codebook; prediction status absent."
channels:
  slice: [0, 0]
  format: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Reveal source labels separately

```beat
id: reference
scene: reference
frames: 336
caption: "Reveal source labels separately"
narration: "An explicit reader reveal mounts the matching upstream training mask on the selected source slice. It is not Full private ground truth or a model prediction."
visual: "Reader-only source mask overlay only after explicit reveal."
channels:
  slice: [0, 1]
  format: [0, 0]
  reference: [0, 1]
cut: intentional-cut
```

# Leave the source boundary visible

```beat
id: limits
scene: limits
frames: 300
caption: "Leave the source boundary visible"
narration: "The upstream training pair was recovered by verified byte ranges from official AWS tar. Full 20-case selection and private evaluator reference are not established. Foreground Dice on class 1. Both-empty masks yield 1.0 in the pinned scorer. No model or evaluator was run."
visual: "Source evidence, missing Full artifacts and scorer-contract cards."
channels:
  slice: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
