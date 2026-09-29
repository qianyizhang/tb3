---
schema: 2
id: rexmle-isles22
title: Segment ischemic stroke lesions from multimodal MRI
locale: en
purpose: Show the exact selected ReX test inputs, their separate native grids, the empty binary-mask submission contract and an explicitly revealed source mask without implying a model result.
scope: Exact ISLES-2022 ReX test input; nine native samples per modality and a gated source mask. No prediction or score.
recipe: rex-isles22-v1
asset_pack: retained-rex-isles22-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-isles22.md
- presentation/external-tasks/sources/rexmle-isles22-resolution.json
- scripts/build_rex_isles22_assets.py
---

# Three contrasts, one binary output grid

## Open the exact test inputs

```beat
id: inputs
scene: inputs
frames: 288
caption: 'Actual DWI, ADC and FLAIR; no prediction'
narration: 'This selected ReX test case has three actual MRI inputs from official ISLES-2022. DWI and ADC share a native voxel grid. FLAIR has a different grid and affine. The rails move through nine fixed native slices per contrast. No mask, model output or score appears here.'
visual: 'Three fixed-window source MRI panels with native k, RAS z, voxel dimensions and spacing; the FLAIR rail is independent.'
channels:
  slice: [0.5, 0.5]
  flair: [0.5, 0.5]
  reference: [0, 0]
```

## Read the physical geometry

```beat
id: geometry
scene: geometry
frames: 264
caption: 'Different voxel grids need their own affine maps'
narration: 'Each NIfTI affine maps voxel indices to physical RAS coordinates in millimeters. DWI and ADC share one map; FLAIR uses another. A matching slice number, or similar z coordinate, is not a registered pixel correspondence. This teaching view does not resample FLAIR onto DWI.'
visual: 'Real DWI and FLAIR source slices with their separate native index and RAS z values; explicit no-registration operation note.'
channels:
  slice: [0.25, 0.75]
  flair: [0.32, 0.68]
  reference: [0, 0]
cut: intentional-cut
```

## Build the required output path

```beat
id: output
scene: output
frames: 264
caption: 'CSV row points to a binary NIfTI that is not yet produced'
narration: 'The adapted ReX submission requires a CSV with case ID and relative predicted-mask path. For this case the path would point to a binary NIfTI on the DWI and ADC 128 by 128 by 25 grid, carrying the appropriate affine. The example row is a contract illustration. No agent mask or submitted file was retained.'
visual: 'Source-defined CSV columns and example relative path flow to an empty binary-mask socket; no mask pixels or metric.'
channels:
  slice: [0.5, 0.5]
  flair: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```

## Reveal the held-out source label

```beat
id: reference
scene: reference
frames: 264
caption: 'Reader-only source mask on matching DWI pixels'
narration: 'An explicit reader reveal now overlays the official source lesion mask on DWI, which shares its native grid. This selected source mask contains 718 positive voxels among 409600 voxels. It is private answer material in ReX test staging, not a prediction. FLAIR stays off this overlay because its native grid differs.'
visual: 'Initially covered reference opens to yellow actual mask pixels on the matching DWI image with an exact reference denominator and no fabricated overlap score.'
channels:
  slice: [0.5, 0.5]
  flair: [0.5, 0.5]
  reference: [0, 1]
cut: intentional-cut
```

## Bound the evaluation claim

```beat
id: limits
scene: limits
frames: 240
caption: 'Array comparison does not validate physical registration'
narration: 'The pinned grader resizes a shape-mismatched prediction by nearest neighbor and compares arrays for Dice, lesion F1, lesion count difference and absolute volume difference. It does not inspect affines. Two same-shape masks with shifted physical affines illustrate that limitation, without claiming a patient result. This one source case supports a teaching explanation, not a population or clinical conclusion.'
visual: 'Three evidence cards for actual source, separate FLAIR grid and scorer boundary, plus a labeled symbolic same-array shifted-affine counterexample.'
channels:
  slice: [0.5, 0.5]
  flair: [0.5, 0.5]
  reference: [0, 0]
cut: intentional-cut
```
