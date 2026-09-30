---
schema: 2
id: automedbench-full-pancreas-seg-task
title: Segment pancreas and pancreatic tumor in CT
locale: en
purpose: "Explain the Full PanTS CT input, label operation, output files and reference boundary."
scope: "Public upstream CT; no matched label, Full case or result."
recipe: automed-full-pancreas-seg-v1
asset_pack: retained-automed-full-pancreas-seg-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-pancreas-seg-task.md
- presentation/external-tasks/sources/automedbench-full-pancreas-seg-task-resolution.json
- scripts/build_automed_seg_c_assets.py
---

# Start with the input

```beat
id: input
scene: input
frames: 288
caption: "Start with the input"
narration: "A complete official PanTSMini CT, PanTS_00000684, supplies input-only pixels. The stored grid is 266 by 158 by 152 at 1.5 millimeter spacing; Full selection and a matching label are unverified. Initial view contains no output or private target."
visual: "Unmarked upstream CT input at fixed native k=38."
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
narration: "Three fixed native k planes, 38, 76 and 114, show upstream CT input. Stored intensities are windowed from minus 160 to 240; HU calibration and original acquisition geometry are unverified. The two required outputs remain separate same-grid binary masks."
visual: "Upstream CT slices and two empty output sockets; no label overlay."
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
narration: "Produce two distinct 3D binary masks on the CT grid: whole pancreas in organ.nii.gz and pancreatic tumor in lesion.nii.gz. PanTS source label remapping cannot be illustrated without a matching source label."
visual: "Source-code to binary-organ/binary-lesion truth table, or explicit unresolved PanTS mapping."
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
narration: "Full submission requires agents_outputs/{case_id}/organ.nii.gz and agents_outputs/{case_id}/lesion.nii.gz. Each mask separately uses 0 background and 1 foreground. Preserve spatial shape and affine for interpretation. No output was generated."
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
narration: "No matching source label was acquired. The separately recovered PanTS_00001349 annotation belongs to another case and is never paired with this CT. Helper and Full private-reference states remain unavailable."
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
narration: "The Full harness contains no dataset. This complete upstream CT has unverified Full membership and no matching annotation, private mask, prediction or score. Clinical score weights organ Dice and GT-positive-case lesion Dice equally and scales partial submissions by completion. The medal tier uses unscaled mean lesion Dice. No model, preparer or evaluator ran."
visual: "Recovered source, missing Full artifacts and scoring-contract cards."
channels:
  slice: [0, 0]
  helper: [0, 0]
  output: [0, 0]
cut: intentional-cut
```
