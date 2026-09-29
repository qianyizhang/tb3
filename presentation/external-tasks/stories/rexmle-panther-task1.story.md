---
schema: 2
id: rexmle-panther-task1
title: Segment pancreatic tumor on diagnostic MRI
locale: en
purpose: Explain the pinned ReX PANTHER Task 1 contract with an abstract grid, empty output and explicit private-label boundary while native source scans remain restricted.
scope: Symbolic source contract; no task-matched MRI, mask, patient geometry, prediction or score.
recipe: rex-panther-task1-v1
asset_pack: retained-rex-panther-task1-symbolic-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-panther-task1.md
- presentation/external-tasks/sources/rexmle-panther-task1-resolution.json
- scripts/build_rex_panther_assets.py
---

# A source-pinned contract without patient pixels

## Open the task input

```beat
id: input
scene: input
frames: 264
caption: "Symbolic arterial-phase contrast-enhanced T1 diagnostic MRI; no patient scan"
narration: "The pinned adapter selects ImagesTr/*_0001_0000.mha and pairs a source label using the first two ID components. Public training images and masks help method development; optional other-sequence ImagesTr_unlabeled images are unannotated training help. The official files are restricted. 73 train and 19 test only if all 92 described annotated source cases match; the preparer was not run. The grid shown is an abstract index diagram, not MRI."
visual: "Top official-access warning, unitless index grid and separate public training-help and held-out-input lanes."
channels:
  grid: [0.2, 0.7]
  reference: [0, 0]
```

## Map indices into native geometry

```beat
id: geometry
scene: geometry
frames: 240
caption: "Read MHA header before creating the mask"
narration: "A real MHA image would supply its own dimensions, spacing, origin and direction. Physical position comes from origin plus direction times spacing and voxel index. Those values are absent here, so the diagram keeps them blank and requires the output mask to carry the current input geometry."
visual: "Abstract five-by-five index cursor moves while the source-defined MHA transform and empty geometry fields remain visible."
channels:
  grid: [0.15, 0.85]
  reference: [0, 0]
cut: intentional-cut
```

## Specify answer-owned files

```beat
id: output
scene: output
frames: 240
caption: "Exact image_id and predicted_mask_path CSV"
narration: "The pinned ReX preparer writes a sample submission with image_id and predicted_mask_path columns. Each relative path points to a binary MHA tumor mask with zero for background and one for tumor. The path and mask socket are empty because no answer or model execution is retained."
visual: "Source-defined CSV columns and predictions/<image_id>.mha template flow to an unfilled binary MHA socket."
channels:
  grid: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```

## Separate the private test label

```beat
id: reference
scene: reference
frames: 216
caption: "Held-out reference role, no reference image"
narration: "Only after this reader chapter is selected, explain the private test label role. The pinned preparer holds test labels outside public test inputs. Source labels can include zero background, one tumor and sometimes two pancreas; the grader extracts tumor class one. No private patient label pixels or geometry are available to display."
visual: "Covered reference contract opens to a label-key and private-path explanation; no tumor silhouette or patient image."
channels:
  grid: [0.5, 0.5]
  reference: [0, 1]
cut: intentional-cut
```

## Bound the scorer

```beat
id: limits
scene: limits
frames: 240
caption: "Array and spacing checks do not prove physical alignment"
narration: "The pinned grader resizes shape-mismatched predictions by nearest neighbor. It uses prediction-file spacing for surface and volume metrics and does not validate affine, origin or direction equality. Dice, five-millimeter Surface Dice, HD95, MASD and tumor-volume RMSE are defined but not observed here. Other-sequence unlabeled training images are not an arterial held-out label."
visual: "Cards separate recovered adapter bytes, missing patient source and grader geometry limitation; no performance number or clinical result."
channels:
  grid: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```
