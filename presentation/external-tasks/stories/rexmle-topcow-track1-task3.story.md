---
schema: 2
id: rexmle-topcow-track1-task3
title: Classify Circle of Willis connections in CTA
locale: en
purpose: 'Show the exact source image, native coordinate frame, task operation, unfilled JSON contract and reader-only source annotation without implying a participant result.'
scope: 'Exact case012 test input; reader-only source annotation; no participant result.'
recipe: rex-topcow-ct-edges-v1
asset_pack: retained-rex-topcow-ct-edges-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-topcow-track1-task3.md
- presentation/external-tasks/sources/rexmle-topcow-track1-task3-resolution.json
- scripts/build_rex_topcow_localization_assets.py
---

# Classify Circle of Willis connections in CTA

## Open the exact source input

```beat
id: inputs
scene: inputs
frames: 240
caption: 'One native CTA test-partition image; no target or output'
narration: 'This is the exact TopCoW2024 case 012 CTA image. Static reproduction of the pinned ReX split places case 012 in test; the preparer was not run. Its native volume has 266×371×311 voxels at 0.498046875×0.498046875×0.5 mm. The opening view shows input pixels only. No source target annotation, participant JSON or score is shown.'
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
narration: 'The NIfTI sform maps native voxel i, j and k to RAS millimeters. The display PNG reverses j and reduces large slices for viewing, but the answer contract uses named binary connections, not display-pixel or physical coordinates. Equal screen points in another scan are not guaranteed to be registered anatomy.'
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
caption: 'Eight named candidate edges form two variant strings'
narration: 'The abstract graph names four anterior candidates, L-A1, Acom, 3rd-A2 and R-A1, and four posterior candidates, L-Pcom, L-P1, R-P1 and R-Pcom. A dashed highlighted edge is a question, not observed patient connectivity. The requested answer is eight present or absent bits, grouped into two four-bit variants. The source bits remain hidden.'
visual: 'Symbolic candidate-edge topology highlights named connections one by one; no patient connectivity asserted.'
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
narration: 'The ReX sample submission requires columns image_id,modality,predicted_edges_path and a relative JSON path shaped like predictions/topcow_ct_<id>_edges.json. The JSON must hold anterior and posterior maps with the eight exact named zero-or-one edge keys. Question marks in this teaching schema mean unfilled participant values. No such file or grade is retained.'
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
caption: 'Reader-only source eight-bit connection annotation'
narration: 'Revealing the annotation displays the archived YML connection bits on an abstract topology key. The source values remain covered until reveal. Solid green means source bit one; gray dashed means source bit zero. This is private reference in ReX test staging, not a participant output. The graph is schematic, not traced from the image.'
visual: 'After explicit reveal, actual YML bits color the abstract candidate graph; native source image stays separate and no segmentation mask is invented.'
channels:
  slice: [0.5, 0.5]
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
narration: 'The pinned scorer turns each four-bit anterior pattern and each four-bit posterior pattern into variant classes, then computes separate balanced accuracy across cases. It is not per-edge accuracy and cannot be computed from one case. No submitted graph, grader run, segmentation output, or score was retained.'
visual: 'Actual-source, exact-scorer and claim-limit cards without any performance number.'
channels:
  slice: [0.5, 0.5]
  step: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
