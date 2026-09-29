---
schema: 2
id: rexmle-topbrain-track2
title: Label 42 MRA brain vessel classes
locale: en
purpose: 'Show exact source pixels, physical grid, task operation, empty output contract and appropriately identified source labels without implying a participant result.'
scope: 'Actual native source image with separately identified labels; participant output and score are absent.'
recipe: rex-topbrain-mr-v1
asset_pack: retained-rex-topbrain-mr-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-topbrain-track2.md
- presentation/external-tasks/sources/rexmle-topbrain-track2-resolution.json
- scripts/build_rex_vascular_seg_assets.py
---

# Label 42 MRA brain vessel classes

## Open the exact source image

```beat
id: inputs
scene: inputs
frames: 240
caption: 'One exact native MRA source image; no prediction'
narration: 'This is an actual public training MRA image for case 012. It has 469×611×174 native voxels at 0.296875×0.296875×0.599998 mm. Nine display slices sample the 3D source at fixed native indices. The opening view contains only the image. No participant mask or score was retained.'
visual: 'Source image with native slice index, physical center coordinate, spacing and fixed display window.'
channels:
  slice: [0.5, 0.5]
  reference: [0, 0]
```

## Follow voxel coordinates

```beat
id: geometry
scene: geometry
frames: 240
caption: 'Native voxel indices map to physical millimeters'
narration: 'The source header maps voxel indices to physical RAS millimeters. The displayed PNG caps the longest axis at 384 pixels with nearest-neighbor sampling, but the original 3D grid and map are retained. A matching screen position in another scan is not a registered anatomical point.'
visual: 'Native image slice and selected voxel-index to physical-z calculation; no reference overlay.'
channels:
  slice: [0.2, 0.8]
  reference: [0, 0]
cut: intentional-cut
```

## Define the labeling operation

```beat
id: operation
scene: operation
frames: 240
caption: 'Read volume → assign TopBrain 2025 v1 42-class vessel-label NIfTI, distinct from TopCoW CoW labels → write answer'
narration: 'The task asks for a TopBrain 2025 v1 42-class vessel-label NIfTI, distinct from TopCoW CoW labels. Reading the native input, assigning labels on its grid and writing a prediction are distinct steps. The prediction socket shown here is empty; no mask was produced in the retained record.'
visual: 'Actual input image alongside a three-step task flow and a visibly empty predicted-mask socket.'
channels:
  slice: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```

## Specify the answer-owned files

```beat
id: output
scene: output
frames: 240
caption: 'CSV and mask path are required, but no output file exists'
narration: 'The ReX submission requires submission.csv columns image_id,modality,predicted_mask_path and a relative path shaped like predictions/topcow_mr_<id>.nii.gz. This is an empty schema for held-out images, not a saved file or prediction for the illustrated case.'
visual: 'CSV header and required relative mask path with no predicted pixels or result metric.'
channels:
  slice: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```

## Inspect the public training helper

```beat
id: helper
scene: helper
frames: 240
caption: 'Public training label helper on matching native pixels'
narration: 'The exact source label is a public training label helper. The class-colored overlay is sampled on the matching native grid and its visible values have a matching color key. These colors are not confidence. This mask is not a saved participant prediction or a score.'
visual: 'Actual source label overlay and a matching visible-class color key; public training helper shown as input assistance, not a held-out answer.'
channels:
  slice: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```

## Bound the evaluation claim

```beat
id: limits
scene: limits
frames: 240
caption: 'Source label and scorer contract are not model performance'
narration: 'Pinned ReX grader evaluates class Dice, clDice, B0, HD95, invalid-neighbor error and side-road F1. The pinned grader nearest-neighbor resamples mismatched shapes and copies GT physical metadata onto predictions, including equal-shape predictions; it does not independently validate affine agreement. Per-case metrics average foreground labels present in GT or prediction before averaging cases; side-road F1 aggregates detection counts. This one source case is a teaching illustration, not a population or clinical result. No participant output, grader run or score was retained.'
visual: 'Three source and scorer limit cards without any performance number.'
channels:
  slice: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```
