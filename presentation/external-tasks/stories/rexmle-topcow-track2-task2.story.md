---
schema: 2
id: rexmle-topcow-track2-task2
title: Localize the Circle of Willis in MRA
locale: en
purpose: 'Show the exact source image, native coordinate frame, task operation, unfilled JSON contract and reader-only source annotation without implying a participant result.'
scope: 'Exact case012 test input; reader-only source annotation; no participant result.'
recipe: rex-topcow-mr-box-v1
asset_pack: retained-rex-topcow-mr-box-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-topcow-track2-task2.md
- presentation/external-tasks/sources/rexmle-topcow-track2-task2-resolution.json
- scripts/build_rex_topcow_localization_assets.py
---

# Localize the Circle of Willis in MRA

## Open the exact source input

```beat
id: inputs
scene: inputs
frames: 240
caption: 'One native MRA test-partition image; no target or output'
narration: 'This is the exact TopCoW2024 case 012 MRA image. Static reproduction of the pinned ReX split places case 012 in test; the preparer was not run. Its native volume has 469×611×174 voxels at 0.296875×0.296875×0.599998 mm. The opening view shows input pixels only. No source target annotation, participant JSON or score is shown.'
visual: 'Actual fixed-window source slice with native k, RAS center coordinate and physical spacing.'
channels:
  slice: [0.5, 0.5]
  step: [0, 0]
  reference: [0, 0]
```

## Read native geometry

```beat
id: geometry
scene: geometry
frames: 240
caption: 'Voxel index and physical RAS position are different coordinates'
narration: 'The NIfTI sform maps native voxel i, j and k to RAS millimeters. The display PNG reverses j and reduces large slices for viewing, but the answer contract uses native voxel size and location values. Equal screen points in another scan are not guaranteed to be registered anatomy.'
visual: 'Actual input slice and its native-index to physical-z calculation, without source target overlay.'
channels:
  slice: [0.2, 0.8]
  step: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Work through the task operation

```beat
id: operation
scene: operation
frames: 288
caption: 'The same location field has two incompatible interpretations'
narration: 'The task description calls location the box center, but the pinned scorer uses location as its minimum corner. In this abstract voxel grid, the same location point and size draw different boxes. The highlighted grid is a symbolic contract example, not a box found in this image. The actual source ROI remains hidden.'
visual: 'Symbolic paired voxel grids show scorer minimum-corner versus prose center; no source ROI values.'
channels:
  slice: [0.5, 0.5]
  step: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Specify the empty answer

```beat
id: output
scene: output
frames: 240
caption: 'A CSV path must point to an answer-owned JSON file'
narration: 'The ReX sample submission requires columns image_id,modality,predicted_bbox_path and a relative JSON path shaped like predictions/topcow_mr_<id>_bbox.json. The JSON must hold size and location arrays, each containing three voxel integers. Question marks in this teaching schema mean unfilled participant values. No such file or grade is retained.'
visual: 'Exact CSV header, path pattern and empty task-specific JSON fields; no answer values.'
channels:
  slice: [0.5, 0.5]
  step: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Reveal the source annotation

```beat
id: reference
scene: reference
frames: 264
caption: 'Reader-only source ROI under scorer geometry'
narration: 'Revealing the annotation displays the source ROI size and location in voxel units, its minimum corner and inclusive maximum under the pinned scorer, and a yellow projection on the native scan. The coordinates remain covered until reveal. This is a source reference, not a participant prediction. The task prose calls location a center, so that conflict remains visible.'
visual: 'After explicit reveal, actual ROI coordinates and scorer-projected yellow image overlay; source TXT remains distinct from an absent prediction.'
channels:
  slice: [0.625, 0.625]
  step: [0.5, 0.5]
  reference: [0, 1]
cut: intentional-cut
```

## Bound the scorer claim

```beat
id: limits
scene: limits
frames: 240
caption: 'Source annotation and scorer rule are not a result'
narration: 'The pinned scorer computes overlap of dilated voxel boxes. Boundary IoU uses margins ceil of 20 percent of each box dimension. Its metric named IoU uses ceil of 50 percent, so it is not ordinary undilated 3D IoU. The description center-versus-scorer-minimum-corner conflict is unresolved. No submitted box, grading, clinical localization, or score was retained.'
visual: 'Actual-source, exact-scorer and claim-limit cards without any performance number.'
channels:
  slice: [0.5, 0.5]
  step: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
