---
schema: 2
id: automedbench-full-spleen-seg-task
title: Segment the spleen in CT
locale: en
purpose: Inspect a matched public MSD Spleen CT and training label while keeping the exact Full output empty and private reference unavailable.
scope: Public upstream CT teaching with post hoc plane selection; Full staged case and result unavailable.
recipe: automed-full-spleen-v1
asset_pack: retained-automed-full-spleen-seg-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-spleen-seg-task.md
- presentation/external-tasks/sources/automedbench-full-spleen-seg-task-resolution.json
- scripts/build_automed_seg_d_assets.py
---

# Segment the spleen in CT

## Read the public CT before labels

```beat
id: inputs
scene: inputs
frames: 264
caption: Read the public CT before labels
narration: A recovered official MSD Task09 public training pair is spleen_19. The CT and 0/1 label share a 512 × 512 × 51 voxel grid, 0.796875 × 0.796875 × 5 mm spacing and identical affine. Three axial planes at native k 20, 26 and 32 were selected after inspecting the released training label, for teaching at display WL 40 and WW 400; their locations are not solver-provided. The Full harness includes no images and does not prove this case belongs to its staged split. No Full participant output is retained.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0, 1]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Map names to exact integer IDs

```beat
id: mapping
scene: mapping
frames: 264
caption: Map names to exact integer IDs
narration: The public MSD training label is a source helper for understanding label 1. It is held behind an explicit reader reveal. The Full Lite condition names TotalSegmentator v2 spleen subset; Standard offers choices to investigate. No model is executed here. The operation selects a class name and its required integer output value; it does not paint a mask.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Keep the dseg target empty

```beat
id: output
scene: output
frames: 264
caption: Keep the dseg target empty
narration: Submit agents_outputs/{case_id}/dseg.nii.gz on each Full case's own CT grid with integer values 0 background and 1 spleen. This pack keeps that output empty because no participant prediction exists. Shape and affine are different conditions for a physically meaningful submission.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Preserve the reference boundary

```beat
id: reference
scene: reference
frames: 264
caption: Preserve the reference boundary
narration: The explicit reader reveal can show a pink layer from the released MSD training label on the matched source CT. Before that control is used, the CT has no label overlay. This layer is a teaching helper, not Full private ground truth or a participant output. The Full private masks remain unavailable.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0, 1]
  label: [0, 0]
  reference: [0, 1]
cut: intentional-cut
```

## Read the pinned scoring boundary

```beat
id: scorer
scene: scorer
frames: 264
caption: Read the pinned scoring boundary
narration: The pinned multiclass scorer fuses separated private spleen masks and compares one combined 0/1 prediction by array shape and Dice. It does not compare NIfTI affines. The format checker rounds voxel values before its allowed-ID test, so that test alone does not prove integer-valued input. Partial submissions scale clinical Dice by completion; medal uses unscaled Dice. No Full case output, private mask, evaluator call or score is retained.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## State the result limit

```beat
id: limits
scene: limits
frames: 264
caption: State the result limit
narration: Public MSD training case and label recovered; exact Full staged-case membership, private GT, prediction and score remain unverified. This is one source example, not a model or population performance result.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
