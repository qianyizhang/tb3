---
schema: 2
id: hubmap-inventory
title: From a PAS slide to a glomerulus inventory
locale: en
purpose: Explain object contours, slide-coordinate identity, overlap reconciliation
  and calibrated profile areas in the proposed inventory task.
scope: One retained public HuBMAP training slide, optional anatomical-region helpers
  and reader-reference teaching examples. Historical diagnostic pilots submitted points
  only; no evaluated contour/area output or new medical trial.
recipe: hubmap-inventory-v1
asset_pack: retained-hubmap-inventory-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/lesion-localization/presentation/briefs/wsi-hubmap-inventory.md
- groups/lesion-localization/presentation/briefs/wsi-hubmap-inventory.en.md
- groups/lesion-localization/presentation/sources/hubmap-inventory-audit.json
- datasets/receipts/wsi-teaching-samples.json
- groups/lesion-localization/experiments/wsi-hubmap-inventory-astra-medium/protocol.md
- groups/lesion-localization/experiments/wsi-hubmap-inventory-v2-sol6-xhigh/protocol.md
- groups/lesion-localization/methods/wsi-agent-v2/score.py
- scripts/build_hubmap_inventory_assets.py
---

# One contour, one inventory row

## Start with the actual PAS slide

```beat
id: inputs
scene: inputs
frames: 192
caption: Start with the actual PAS slide
narration: The proposed task is to find glomerular profiles, outline each instance
  and return centers and calibrated areas. Start with native image pixels; source
  object contours remain withheld. This is one public training slide, not a hidden
  clinical test set.
visual: Full-slide source image at native physical aspect; no object references, count
  or measurements.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## Declare optional regional assistance

```beat
id: helpers
scene: helpers
frames: 192
caption: Declare optional regional assistance
narration: Cortex and medulla regions may be offered as an optional helper condition.
  These rough source regions are not glomerulus outlines or a complete negative domain.
  Retained point-only pilots did not receive this regional assistance.
visual: Actual source anatomical regions with blue cortex and purple medulla. Filled
  context fades in; no glomerulus reference.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Locate a reference-selected teaching crop

```beat
id: detail
scene: detail
frames: 192
caption: Locate a reference-selected teaching crop
narration: A sixteen-hundred-pixel crop spans one thousand forty micrometres. The
  first source polygon selected it. The viewport animation teaches the crop location
  and deliberately removes the slide-search problem; it is not recorded agent navigation.
visual: Full-slide viewport moves to the exact crop bounds beside native PAS crop
  pixels. No reference outlines.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the source contour separately

```beat
id: outline
scene: outline
frames: 192
caption: Reveal the source contour separately
narration: The dashed teal boundary is an actual source annotation. It is a reader
  reference, never a submitted contour or animated inference. The teaching crop also
  contains partial neighbouring profiles, and reference completeness remains unresolved.
visual: Reveal the first polygon on the unchanged native crop; leave neighbouring
  partial profiles visible.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Return local geometry to level zero

```beat
id: coordinates
scene: coordinates
frames: 240
caption: Return local geometry to level zero
narration: Add the crop origin to local coordinates. The same transform applies to
  the polygon and its derived area centroid. Keep x right and y down in the full-slide
  pixel frame; an area centroid is not an independently annotated center point.
visual: Show actual polygon, amber centroid and local coordinates plus origin, then
  reveal the full-slide center.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Reconcile two views of one object

```beat
id: duplicate
scene: duplicate
frames: 240
caption: Reconcile two views of one object
narration: Two overlapping native crops deliberately show the same source object.
  Different local centers map to the same level-zero location. Two view records therefore
  describe one object. This constructed example teaches reconciliation and does not
  establish an agent duplicate error.
visual: Show both actual crops, their distinct origins/local centers and matching
  source contours; change two records to one unique object.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Square the physical pixel spacing

```beat
id: area
scene: area
frames: 240
caption: Square the physical pixel spacing
narration: The original polygon encloses thirty-six thousand five hundred eighty-eight
  square pixels. Multiply by zero point six-five squared to obtain fifteen thousand
  four hundred fifty-eight point four-three square micrometres. This is a two-dimensional
  section profile, not volume.
visual: Highlight the polygon interior and reveal the exact area conversion. Geometry
  uses source coordinates, never thresholded JPEG pixels.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Join every row to one contour

```beat
id: inventory
scene: inventory
frames: 240
caption: Join every row to one contour
narration: The proposed deliverables are GeoJSON contours and a CSV inventory joined
  by stable IDs. The revealed rows come from source references solely to demonstrate
  the format. Ninety-nine polygons in this member do not establish an independently
  adjudicated exhaustive count.
visual: Reveal source polygons over the full slide and expand five rounded reference-derived
  rows. Use ordinal IDs because original source IDs repeat.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Keep point pilots separate from contours

```beat
id: conditions
scene: conditions
frames: 240
caption: Keep point pilots separate from contours
narration: Historical diagnostic trials returned points only. Their private polygons
  match this source. The revised point matcher accepts inside-polygon or fifty-micrometre
  proximity matches one to one, with unmatched candidates queued for review. Those
  pilots do not measure contour or area quality.
visual: Compare proposed files and retained point-only contract; keep reference matching
  separate from clinical false positives.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Retain the open evaluation questions

```beat
id: limits
scene: limits
frames: 240
caption: Retain the open evaluation questions
narration: A contour trial still needs frozen instructions, instance and area scoring,
  and rules for partial or altered profiles. One public training slide cannot support
  population claims. Only three archive members were acquired and verified; no full-archive
  checksum or new clinical adjudication is implied.
visual: 'Four unresolved boundaries: reference inclusion, evaluator, training scope
  and two-dimensional measurement. No reference-derived result shown.'
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
