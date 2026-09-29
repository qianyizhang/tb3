---
schema: 2
id: automedbench-full-aeropath-seg-task
title: Segment lung and airway on CT
locale: en
purpose: "Explain Full segmentation inputs, native-grid operation, output labels and the source/reference boundary for chest CT."
scope: "Upstream training example; Full membership unverified. Labels gated; output empty."
recipe: automed-full-aeropath-seg-v1
asset_pack: retained-automed-full-aeropath-seg-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-aeropath-seg-task.md
- presentation/external-tasks/sources/automedbench-full-aeropath-seg-task-resolution.json
- scripts/build_automed_seg_a_assets.py
---

# Inspect the unmarked input

```beat
id: input
scene: input
frames: 288
caption: "Inspect the unmarked input"
narration: "Official AeroPath case 10 CT and matching separate lung/airway masks at 512×512×241 voxels. This upstream training example is not proven to be in the Full selected cases. It begins without labels or output."
visual: "Unmarked native source slice or empty symbolic FeTA input socket."
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
narration: "Inspect three preselected native CT planes. They were chosen using the source annotation, so this is not a blind localization test. The task contract fuses lung as 1 before airway as 2."
visual: "Three sampled native slices animate k; no source mask is mounted."
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
narration: "The required combined label map uses 0 background, 1 lung, 2 airway. The IDs describe mutually exclusive output voxels."
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
narration: "An explicit reader reveal mounts the upstream training masks. Airway class 2 replaces lung class 1 where those source masks overlap. These are not Full private ground truth or a prediction."
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
narration: "AeroPath case 10 source hashes match BR-033, but its Full staged-case membership and private reference are not established. The retained license text says CC BY 4.0 while the HF card says MIT. Macro mean foreground Dice across lung and airway. Pinned scorer treats both-empty masks as Dice 1.0, though config prose says empty ground-truth classes are skipped. No model or evaluator was run."
visual: "Source evidence, missing Full artifacts and scorer-contract cards."
channels:
  slice: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
