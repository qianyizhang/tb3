---
schema: 2
id: automedbench
title: Build a kidney and lesion CT segmentation pipeline
locale: en
purpose: Inspect a native KiTS19 CT, distinguish two help tiers, and understand the two-mask submission and evaluator boundaries.
scope: Source-derived case_00000 teaching extract and six nonclinical contract fixtures; no model or judge run.
recipe: automed-kidney-v1
asset_pack: retained-automed-kidney-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench.md
- presentation/external-tasks/sources/automed-kidney-audit.json
- presentation/external-tasks/sources/automed-kidney-resolution.json
- scripts/build_automed_kidney_assets.py
---

# Native kidney CT to two required masks

## Begin with the whole input volume

```beat
id: inputs
scene: inputs
frames: 360
caption: "Read the native CT before any labels"
narration: "This is an actual KiTS19 case_00000 CT, sampled at three axial indices. The 611 by 512 by 512 native grid has inferior, posterior and left-increasing voxel axes. The slice spacing is half a millimeter, and the in-plane spacing is about 0.92 millimeters. We display a fixed CT window from minus 160 to 240 Hounsfield units. The solver receives the volume, not these selected teaching slices or any annotation."
visual: "Native CT planes 288, 311 and 344, with orientation labels and no source reference layer."
channels:
  view: [0, 1]
  helper: [0, 0]
  step: [0, 0]
  reference: [0, 0]
  fixture: [0, 0]
```

## Read the assistance condition

```beat
id: assistance
scene: assistance
frames: 288
caption: "Lite and Standard supply different help"
narration: "Lite names a KiTS19 checkpoint and gives requirements and setup examples. Standard gives model-choice and comparison guidance without Lite's named checkpoint. Both assembled conditions include one-case validation in stage three. Neither hands the solver this patient's answer mask."
visual: "Two help cards highlight in turn beside an unchanged native CT."
channels:
  view: [0.5, 0.5]
  helper: [0, 1]
  step: [0, 0]
  reference: [0, 0]
  fixture: [0, 0]
cut: intentional-cut
```

## Follow the required stages

```beat
id: workflow
scene: workflow
frames: 432
caption: "Five stages turn guidance into submitted files"
narration: "The task calls for research, setup, one-case validation, inference across patients and submission. Validation must inspect both binary masks and their native geometry. The configured budget is 3,600 seconds. These are task instructions, not a replay of an agent run; the separate stage-one through stage-three judge has not run here."
visual: "The five source-backed stages advance one at a time, with their concrete action beneath."
channels:
  view: [0.5, 0.5]
  helper: [0, 0]
  step: [0, 1]
  reference: [0, 0]
  fixture: [0, 0]
cut: intentional-cut
```

## Define the empty output slots

```beat
id: schema
scene: schema
frames: 336
caption: "Submit two binary NIfTI masks per patient"
narration: "Each patient needs an organ dot nii dot gz and a lesion dot nii dot gz under agents_outputs. Both must use the input CT's 611 by 512 by 512 grid and affine. The kidney target includes lesion tissue; lesion is a separate binary mask. These empty targets describe the requested output. No saved patient prediction exists in this pack."
visual: "Native CT beside two visibly empty file slots and a shared-grid diagram."
channels:
  view: [0.5, 0.5]
  helper: [0, 0]
  step: [0, 0]
  reference: [0, 0]
  fixture: [0, 0]
cut: intentional-cut
```

## Reveal the private source annotation

```beat
id: reference
scene: reference
frames: 432
caption: "Map source labels only after reader reveal"
narration: "The source annotation is now revealed for the reader, not supplied to the solver and not a prediction. Original label one denotes kidney tissue, label two lesion. An oracle format illustration sets organ to source label one or two and lesion to label two. On the displayed plane, cyan and gold match the legend. This demonstrates required file semantics, not segmentation quality."
visual: "CT starts alone; explicit reveal adds cyan kidney and gold lesion overlay and the two label-mapping rules. Advance through three native slices."
channels:
  view: [0, 1]
  helper: [0, 0]
  step: [0, 0]
  reference: [0, 1]
  fixture: [0, 0]
cut: intentional-cut
```

## Separate contract checks

```beat
id: contract
scene: contract
frames: 456
caption: "Format, completeness and overlap are distinct"
narration: "Six retained nonclinical fixtures use two artificial eight-cubed arrays. The runner quick check expects both masks, but the separate format helper can regard a missing organ as optional. Array Dice does not test physical affine alignment: a toy mask can shift its origin by one hundred millimeters and retain identical array Dice. Lesion Dice is averaged over reference-positive cases. None of these toy outcomes measures a patient or model."
visual: "Six fixture selectors and the selected quick-check/format flags; three separate gates accompany a toy shared-grid diagram."
channels:
  view: [0.5, 0.5]
  helper: [0, 0]
  step: [0, 0]
  reference: [0, 0]
  fixture: [0, 1]
cut: intentional-cut
```

## Preserve the limits

```beat
id: limits
scene: limits
frames: 240
caption: "One recovered source case is not a capability result"
narration: "We have a hash-verified KiTS19 CT and matching source annotation, thirty-five pinned task files and six nonclinical fixtures. We do not have saved clinical predictions, a model trial, judge scores or patient Dice. The pinned root recipe's data directory differs from the task loader's directory, and staging was not executed to reconcile them. This remains a source-backed explanation of the task and its checks."
visual: "Four explicit evidence and limit cards."
channels:
  view: [0.5, 0.5]
  helper: [0, 0]
  step: [0, 0]
  reference: [0, 0]
  fixture: [0, 0]
cut: intentional-cut
```
