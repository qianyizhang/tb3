---
schema: 2
id: rexmle-seg-a
title: Segment the aortic vessel tree in CTA
locale: en
purpose: 'Show exact source pixels, physical grid, task operation, empty output contract and appropriately identified source labels without implying a participant result.'
scope: 'Actual native source image with separately identified labels; participant output and score are absent.'
recipe: rex-seg-a-v1
asset_pack: retained-rex-seg-a-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-seg-a.md
- presentation/external-tasks/sources/rexmle-seg-a-resolution.json
- scripts/build_rex_vascular_seg_assets.py
---

# Segment the aortic vessel tree in CTA

## Open the exact source image

```beat
id: inputs
scene: inputs
frames: 240
caption: 'One exact native CTA source image; no prediction'
narration: 'This is an actual public training CTA image for case K20. It has 512×512×94 native voxels at 0.55078125×0.55078125×5 mm. Nine display slices sample the 3D source at fixed native indices. The opening view contains only the image. No participant mask or score was retained.'
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
narration: 'The source header maps voxel indices to physical LPS millimeters. The displayed PNG reduces the longest axis to 384 pixels with nearest-neighbor sampling, but the original 3D grid and map are retained. A matching screen position in another scan is not a registered anatomical point.'
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
caption: 'Read volume → assign binary aortic vessel tree mask, source NRRD value 1 for aorta → write answer'
narration: 'The task asks for a binary aortic vessel tree mask, source NRRD value 1 for aorta. Reading the native input, assigning labels on its grid and writing a prediction are distinct steps. The prediction socket shown here is empty; no mask was produced in the retained record.'
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
narration: 'The ReX submission requires submission.csv columns image_id,predicted_mask_path and a relative path shaped like predictions/<image_id>.seg.nrrd. This is an empty schema for held-out images, not a saved file or prediction for the illustrated case.'
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
narration: 'Pinned ReX grader computes base-case mean Dice and Hausdorff distance, with nearest-neighbor array zoom when prediction shape differs. The adapted grader does not implement the original challenge Sobol sensitivity p1/p2. Its random case split mixes institutions despite the description of a fourth-institution test. This one source case is a teaching illustration, not a population or clinical result. No participant output, grader run or score was retained.'
visual: 'Three source and scorer limit cards without any performance number.'
channels:
  slice: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```
