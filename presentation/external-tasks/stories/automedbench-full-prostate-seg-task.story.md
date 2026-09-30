---
schema: 2
id: automedbench-full-prostate-seg-task
title: Label prostate zones on two-channel MRI
locale: en
purpose: "Explain the Full MSD Task05 prostate MRI input, label operation, output files and reference boundary."
scope: "Upstream T2/ADC training pair; Full membership unverified. Helper gated; output empty."
recipe: automed-full-prostate-seg-v1
asset_pack: retained-automed-full-prostate-seg-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-prostate-seg-task.md
- presentation/external-tasks/sources/automedbench-full-prostate-seg-task-resolution.json
- scripts/build_automed_seg_c_assets.py
---

# Start with the input

```beat
id: input
scene: input
frames: 288
caption: "Start with the input"
narration: "Official upstream training image prostate_00 is 320×320×15×2: channel 0 T2-weighted, channel 1 ADC. Its matching 3D label has IDs 0,1,2 and native RAS geometry. It is not verified as a Full staged case. Initial view contains no output or private target."
visual: "Unmarked upstream T2 image."
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
narration: "Inspect both channels at the same oblique native i,j,k on three preselected source planes. They were selected after inspecting the training annotation, so this is not a blind target search; no label is shown yet."
visual: "Paired T2/ADC native slices."
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
narration: "Read paired T2 and ADC values at each native i,j,k. Assign one mutually exclusive 3D class: background 0, peripheral zone 1, transition zone 2. This is zonal anatomy, not cancer detection."
visual: "Zone codebook."
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
narration: "Full submission requires agents_outputs/{case_id}/dseg.nii.gz. One combined dseg.nii.gz uses 0 background, 1 peripheral zone and 2 transition zone. Preserve spatial shape and affine for interpretation. No output was generated."
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
narration: "An explicit reveal shows official upstream training labels on the selected T2 slice; they are helper data, not Full private reference or a predicted result."
visual: "Optional upstream training overlay."
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
narration: "The official upstream training label is helper material. Full 20-case membership and evaluator-only masks are unverified; no prediction or score is retained. Dice averages both foreground zones; partial submissions are scaled by completion. Medal uses unscaled macro Dice. No model, preparer or evaluator ran."
visual: "Recovered source, missing Full artifacts and scoring-contract cards."
channels:
  slice: [0, 0]
  helper: [0, 0]
  output: [0, 0]
cut: intentional-cut
```
