---
schema: 2
id: automedbench-full-panther-t1-seg-task
title: Segment pancreas and tumor in arterial T1 MRI
locale: en
purpose: "Explain the Full PANTHER diagnostic contrast-enhanced arterial T1 MRI input, label operation, output files and reference boundary."
scope: "Symbolic protocol; no native case, private target or prediction."
recipe: automed-full-panther-t1-seg-v1
asset_pack: retained-automed-full-panther-t1-seg-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-panther-t1-seg-task.md
- presentation/external-tasks/sources/automedbench-full-panther-t1-seg-task-resolution.json
- scripts/build_automed_seg_c_assets.py
---

# Start with the input

```beat
id: input
scene: input
frames: 288
caption: "Start with the input"
narration: "No task-matched native T1 scan or label was recovered. The official PANTHER Zenodo record is restricted and lists no files to an unauthenticated reader. Initial view contains no output or private target."
visual: "Empty symbolic input socket."
channels:
  slice: [0, 0]
  helper: [0, 0]
  output: [0, 0]
```

# Inspect the native channels

```beat
id: channels
scene: channels
frames: 336
caption: "Inspect the native channels"
narration: "The unavailable native volume is an input socket. The two output sockets are separate same-grid binary masks, not measured anatomy."
visual: "Unmeasured 3D input and two output sockets."
channels:
  slice: [0, 1]
  helper: [0, 0]
  output: [0, 0]
cut: intentional-cut
```

# Map task-specific labels

```beat
id: mapping
scene: mapping
frames: 336
caption: "Map task-specific labels"
narration: "Convert source MHA codes 1=tumor and 2=pancreatic parenchyma into two separate binary Full targets: organ=1 for source {1,2}; lesion=1 for source {1}. This is a label-contract transform only, not a segmentation."
visual: "PANTHER source-code to binary-organ/binary-lesion truth table; no observed anatomy."
channels:
  slice: [0, 0]
  helper: [0, 0]
  output: [0, 0]
cut: intentional-cut
```

# Save the required masks

```beat
id: output
scene: output
frames: 324
caption: "Save the required masks"
narration: "Full submission requires agents_outputs/{case_id}/organ.nii.gz and agents_outputs/{case_id}/lesion.nii.gz. Each output mask separately uses 0 background and 1 foreground. Preserve spatial shape and affine for interpretation. No output was generated."
visual: "Required output paths and absent prediction status."
channels:
  slice: [0, 0]
  helper: [0, 0]
  output: [0, 1]
cut: intentional-cut
```

# Inspect training help separately

```beat
id: helper
scene: helper
frames: 312
caption: "Inspect training help separately"
narration: "No source label was acquired; the helper and Full private-reference states remain unavailable."
visual: "Unavailable source-label state."
channels:
  slice: [0, 1]
  helper: [0, 1]
  output: [0, 0]
cut: intentional-cut
```

# Keep the evidence boundary

```beat
id: limits
scene: limits
frames: 300
caption: "Keep the evidence boundary"
narration: "Research access to the PANTHER dataset is required. The Full harness contains no image; no Full case, private mask, prediction or score is retained. Organ and GT-positive lesion Dice are weighted equally and scaled by lesion-output completion; the medal uses unscaled mean lesion Dice. No model, preparer or evaluator ran."
visual: "Recovered source, missing Full artifacts and scoring-contract cards."
channels:
  slice: [0, 0]
  helper: [0, 0]
  output: [0, 0]
cut: intentional-cut
```
