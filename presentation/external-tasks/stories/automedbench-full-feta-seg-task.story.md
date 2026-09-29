---
schema: 2
id: automedbench-full-feta-seg-task
title: Label seven fetal-brain tissues in T2 MRI
locale: en
purpose: "Explain Full segmentation inputs, native-grid operation, output labels and the source/reference boundary for fetal T2-weighted super-resolution MRI."
scope: "Symbolic protocol; no source MRI, Full case, reference or prediction."
recipe: automed-full-feta-seg-v1
asset_pack: retained-automed-full-feta-seg-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-feta-seg-task.md
- presentation/external-tasks/sources/automedbench-full-feta-seg-task-resolution.json
- scripts/build_automed_seg_a_assets.py
---

# Inspect the unavailable input

```beat
id: input
scene: input
frames: 288
caption: "Inspect the unavailable input"
narration: "No native source image is retained; official Zenodo metadata report restricted files and a Synapse access route. The blank image socket is symbolic, not a fetal scan."
visual: "Empty FeTA input socket only; no source slice is available."
channels:
  slice: [0, 0]
  format: [0, 0]
  reference: [0, 0]
```

# Sample an abstract voxel grid

```beat
id: stack
scene: stack
frames: 336
caption: "Sample an abstract voxel grid"
narration: "An authored i/j/k wireframe shows a cyan sampling plane moving along schematic k. Native shape, voxel spacing, anatomy and tissue boundaries are unknown; no output labels are inferred."
visual: "Abstract wireframe volume and moving sampling plane; cyan marks the plane, not tissue or ground truth."
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
narration: "The literal output codebook is 0 background; 1 eCSF, 2 GM, 3 WM, 4 LV, 5 CBM, 6 SGM, 7 BS. These are required IDs, not observed labels or inferred tissue in the schematic."
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

# Show the unavailable reference

```beat
id: reference
scene: reference
frames: 336
caption: "Show the unavailable reference"
narration: "No source or private FeTA mask was acquired; the reference state remains unavailable."
visual: "Reference unavailable state; no source or private mask is mounted."
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
narration: "FeTA access requires its research/education agreement through the official route. Neither input image, source label, Full private reference, prediction nor score is present. Pinned multiclass scorer computes foreground-class Dice and macro mean; no case or class result was produced. No model or evaluator was run."
visual: "Source evidence, missing Full artifacts and scorer-contract cards."
channels:
  slice: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
