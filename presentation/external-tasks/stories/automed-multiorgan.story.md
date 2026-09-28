---
schema: 2
id: automed-multiorgan
title: Build a multi-organ CT segmentation pipeline
locale: en
purpose: Preserve native CT geometry, remap named structures to benchmark IDs, and
  inspect all-class Dice and coverage separately.
scope: Native CT, five partial references and nonclinical evaluator fixtures. No model
  run.
recipe: automed-multiorgan-v1
asset_pack: retained-automed-multiorgan-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-tsg.md
- presentation/external-tasks/sources/automed-multiorgan-audit.json
- scripts/audit_automed_kidney.py
- scripts/audit_automed_multiorgan.py
- scripts/build_automed_multiorgan_assets.py
---

# Canonical multi-organ pipeline explanation

## A whole CT volume enters the pipeline

```beat
id: inputs
scene: inputs
frames: 288
caption: A whole CT volume enters the pipeline
narration: The Lite task includes forty CT cases. This native example has three hundred
  thirty-three by three hundred thirty-three by three hundred thirty-six voxels, at
  one point five millimeters. These teaching planes were selected post hoc using kidney
  references. The solver receives the volume, not an organ boundary or supplied target
  slice.
visual: Three native coronal planes, without reference overlays.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Five stages organize the required work

```beat
id: workflow
scene: workflow
frames: 480
caption: Five stages organize the required work
narration: 'Follow the five-stage condition: research, set up, validate one case,
  infer over all cases, and submit. Lite supplies TotalSegmentator guidance, requirements
  and cache conventions. The agent still has to prepare the model, inspect labels,
  preserve geometry and save per-patient outputs. The configured budget is thirty-six
  hundred seconds. These highlights follow the public instructions; they do not replay
  an agent run.'
visual: Five successive stage selections with their concrete responsibility.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Match class names before writing integer IDs

```beat
id: remap
scene: remap
frames: 480
caption: Match class names before writing integer IDs
narration: TotalSegmentator and the benchmark do not share integer numbering. In the
  pinned version two point four map, left kidney is three, but the benchmark expects
  forty-two. Right kidney maps from two to forty-three; liver from five to forty-four;
  spleen from one to eighty-four; aorta from fifty-two to three. Use structure names
  to join the maps. The requirements permit later versions, so inspect the actual
  checkpoint table.
visual: Five exact name-mediated ID conversions; selected row and conversion move
  together.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Output labels must keep the CT’s native grid

```beat
id: geometry
scene: geometry
frames: 336
caption: Output labels must keep the CT’s native grid
narration: Return one integer label map per patient, named dseg dot nii dot gz. Zero
  is background; the foreground IDs range from one to one hundred seventeen. Shape
  alone is insufficient. The pinned checks also compare affine geometry and active
  qform and sform. A synthetic array shifted by one hundred millimeters fails format
  and gets zero Dice. This explanation does not resample the native CT.
visual: Native CT and exact output fields; switch from matching geometry to a separately
  labeled toy shift.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal five released reference masks

```beat
id: reference
scene: reference
frames: 480
caption: Reveal five released reference masks
narration: 'The overlays now reveal evaluator references for the reader. They are
  not model predictions or supplied solver assistance. Five masks are retained: both
  kidneys, liver, spleen and aorta. The release CSV reports seventy-eight present
  classes in this case, from one hundred seventeen configured classes. Each color
  matches the legend. The selected mask brightens while the others dim. This partial
  set cannot establish a full-case result.'
visual: Input-only chapter start; explicit reveal followed by five named native-mask
  selections.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Inspect the denominator in the pinned scorer

```beat
id: scoring
scene: scoring
frames: 384
caption: Inspect the denominator in the pinned scorer
narration: The config claims a mean over classes with nonempty ground truth. The pinned
  implementation instead loops through all one hundred seventeen classes and gives
  empty versus empty Dice one. Our nonclinical toy contains only two occupied classes.
  Exact labels score one; an all-background prediction still receives one hundred
  fifteen empty-pair credits, or zero point nine eight two nine. This is evaluator
  arithmetic, not anatomical performance.
visual: Documented and implemented denominator side by side, followed by exact and
  empty synthetic cases.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Keep validity, coverage and overlap separate

```beat
id: coverage
scene: coverage
frames: 672
caption: Keep validity, coverage and overlap separate
narration: Seven synthetic fixtures separate the checks. Exact labels pass. Empty
  or swapped labels receive empty-pair credit. A shifted origin or fractional value
  fails format and receives zero Dice. One missing patient leaves the raw Dice at
  one, then coverage scales the final task score to one half. With both outputs missing,
  format remains true but coverage and Dice are zero. Malformed present outputs still
  count in completeness. Medals are assigned before coverage scaling, and the first
  three workflow steps are unscored here.
visual: Seven fixture rows and synchronized selected-case explanation; no patient
  predictions.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## What this explanation establishes

```beat
id: limits
scene: limits
frames: 240
caption: What this explanation establishes
narration: We have one hash-verified CT, five matching native masks, a pinned label
  mapping and seven nonclinical evaluator examples. We do not have a full reference
  set, patient prediction or model capability result. No controller, judge or runtime
  isolation test was executed. The explainer shows how to inspect this specific Lite
  task and its score.
visual: Four evidence and limit cards.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
