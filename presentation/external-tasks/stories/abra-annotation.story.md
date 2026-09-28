---
schema: 2
id: abra-annotation
title: Outline a nodule in native image coordinates
locale: en
purpose: Separate ordinary visual boundary judgment, native annotation attachment
  and oracle contour transfer.
scope: One retained LIDC CT and Nodule 1 annotation; regenerated task definitions
  and teaching examples; no model or OHIF run.
recipe: abra-annotation-v1
asset_pack: retained-abra-annotation-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/abra.md
- presentation/external-tasks/sources/abra-annotation-audit.json
- scripts/audit_abra_annotation.py
- scripts/build_abra_annotation_assets.py
---

# Canonical ABRA annotation explanation

## One native examination, a specified slice

```beat
id: inputs
scene: inputs
frames: 240
caption: One native examination, a specified slice
narration: The ordinary task opens this CT at slice zero and supplies slice 66, Nodule
  1 and a lung window. The native series has 140 slices. No mask, target coordinate
  or outline is supplied. The agent must judge the boundary and place an annotation
  within fifteen turns.
visual: Native full CT at the initial slice, beside the actual ordinary condition.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## Navigate before judging a boundary

```beat
id: navigate
scene: navigate
frames: 432
caption: Navigate before judging a boundary
narration: Selected native slices illustrate navigation to the requested plane. Set
  the slice and lung window, then retrieve an image. This is an author teaching sequence,
  not an agent trace or a replayed OHIF session. A correct navigation call does not
  establish a correct contour.
visual: Three discrete acquired slices, with slice 66 as the supplied destination.
channels:
  view:
  - 0
  - 1
  helper:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Coordinates belong to a native image and slice

```beat
id: coordinates
scene: coordinates
frames: 336
caption: Coordinates belong to a native image and slice
narration: 'Annotation tools use zero-based native image pixels: x is column, y is
  row. The white witness at 128,256 is an author ruler point, not a lesion hint. Native
  DICOM geometry maps that point to LPS millimeters. A reader crop has a different
  origin; return its coordinates to the native image before annotation.'
visual: Native slice with a nonclinical coordinate witness and explicit pixel-to-LPS
  arithmetic.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the reference and its source

```beat
id: reference
scene: reference
frames: 576
caption: Reveal the reference and its source
narration: The reader reveal shows Nodule 1, Annotation 12. The pinned manifest lists
  one annotator for this nodule, so the fifty-percent consensus function reproduces
  that single mask. Eight frames align by source image UID and geometry; slice 66
  has 629 labeled pixels. Contours use the largest marching-squares component. These
  reference-selected crops and boundaries are not ordinary solver inputs or independent
  clinical truth.
visual: Delayed private reference reveal with eight native crop sections; teal contours.
channels:
  view:
  - 0
  - 1
  helper:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Attach geometry without confusing it with an agent result

```beat
id: ordinary
scene: ordinary
frames: 384
caption: Attach geometry without confusing it with an agent result
narration: 'The dashed yellow polygon is an author reference-copy example showing
  the output contract: a label, slice index and native pixel points. It is not a retained
  agent answer. In the actual ordinary condition, the boundary must come from the
  agent reading the image. The active series and slice attachment matter alongside
  the geometry.'
visual: Source crop with reference followed by a separately styled teaching annotation.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  output:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## An oracle supplies the contour to transfer

```beat
id: oracle
scene: oracle
frames: 432
caption: An oracle supplies the contour to transfer
narration: The separate oracle condition supplies an overview and precise source-derived
  contour through query_pathology_model. For this nodule it recommends slice 66. The
  blue dotted contour is supplied assistance; the dashed yellow copy illustrates transfer.
  Confidence values are hardcoded, not calibrated predictions. This ten-turn condition
  is labeled as not requiring vision by the generator.
visual: Overview, supplied contour, then annotation transfer; distinct assistance
  boundary.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 1
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Distinguish normalized outcome from exact attachment

```beat
id: scoring
scene: scoring
frames: 576
caption: Distinguish normalized outcome from exact attachment
narration: For the same reference polygon, analytical IoU is one. The exact slice-penalty
  function yields outcomes one, point eight, point six, point four and zero for offsets
  zero through four. Missing index has no scorer penalty, though the tool requires
  it. Circle and rectangle outcomes use a shape heuristic. The hit threshold is point
  five; it is not simply raw overlap. These are teaching calculations, not a full
  scorer or viewer run. Overall scoring separately weights planning, execution and
  outcome.
visual: Six source-derived arithmetic cases; selected row moves every four seconds.
channels:
  view:
  - 0
  - 1
  helper:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Preserve what the example does and does not show

```beat
id: limits
scene: limits
frames: 288
caption: Preserve what the example does and does not show
narration: The explanation uses actual native images, one source annotation and regenerated
  ordinary and oracle task definitions. It demonstrates source geometry and assistance
  boundaries. No model trial, live viewer run, full benchmark replay or clinical adjudication
  is implied. Other nodules and task families require their own source review.
visual: 'Four scope cards: native source, recovered condition, teaching examples and
  remaining limits.'
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
