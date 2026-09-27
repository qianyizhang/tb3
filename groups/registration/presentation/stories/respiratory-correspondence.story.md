---
schema: 2
id: respiratory-correspondence
title: Transfer respiratory landmarks with explicit source depth
locale: en
purpose: Explain the source pixel to target-point contract, full-source condition
  and separate numerical and visual judgments.
scope: Retained Learn2Reg cases 1 and 3. Calibrated CT sections, historical BR-028
  output and reader-only manual targets. No new trial, dense field, clinical adjudication
  or causal source-depth claim.
recipe: respiratory-v1
asset_pack: retained-respiratory-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/registration/presentation/briefs/tb3-respiratory-correspondence.md
- docs/evidence/br021-freeze.json
- docs/evidence/br024-patient3-freeze.json
- docs/evidence/br028-freeze.json
- docs/evidence/br028-results.json
- docs/evidence/br028-adjudication.json
- docs/research-rounds/BR-023-sol-registration.md
- presentation/task-explorer/respiratory/manifest.json
- scripts/build_respiratory_assets.py
---

# Respiratory point correspondence

## inputs

```beat
id: inputs
frames: 240
scene: inputs
caption: A calibrated source slice and a complete target CT define eight point queries.
narration: The retained case three task gives an exhalation slice and an inhalation
  volume. The source slice has 189 columns and 121 rows, with eight fractional-pixel
  queries and a known pose. The target is a complete 192 by 192 by 208 array. It is
  preprocessed, cropped and affine prealigned; expiration coverage is incomplete.
  Manual target landmarks are withheld from the solver.
visual: Show the actual oblique source slice on the left and three calibrated target
  sections on the right. Mark only public source queries.
channels:
  depth:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## frame

```beat
id: frame
frames: 240
scene: frame
caption: The supplied affine locates q06 in the source, not in the target anatomy.
narration: Multiply the fractional pixel coordinates by the 1.25 millimetre spacing,
  then apply slice_to_world. The public q06 location is 220.5, 170, 140 millimetres
  in dataset-world coordinates. This is a known source acquisition pose. It does not
  solve respiratory correspondence, and no native patient LPS or RAS convention is
  asserted. q06 is a posthoc teaching example.
visual: Retain the source query geometry beside the explicit pixel-to-world formula;
  do not move the query to imply registration.
channels:
  depth:
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

## depth

```beat
id: depth
frames: 264
scene: depth
caption: Add the full source volume while preserving slice, queries, target and grader.
narration: BR-028 adds reference_volume.npz to the earlier case three task. The original
  slice, pixels, pose, target, private truth and grader are unchanged. The full source
  context appears here as three calibrated CT sections. The public queries remain
  projected slice locations, not hidden exact manual source points. Both the three
  millimetre RMS and five millimetre maximum gates still apply.
visual: Reveal real source orthogonal sections around the public q06 location without
  moving any source or target point.
channels:
  depth:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## output

```beat
id: output
frames: 240
scene: output
caption: Return eight ordered target coordinates in dataset-world millimetres.
narration: The required JSON contains query_ids and eight finite XYZ points in points_world_mm,
  written to /app/answer/points.json. These rows are the retained BR-028 Sol/xhigh
  submission. Their gradual appearance is a teaching reveal, not a replay of the solver
  search or a new prediction. The target frame remains fixed.
visual: Reveal each historical submitted point and its exact ordered coordinate row.
channels:
  depth:
  - 1
  - 1
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## reference

```beat
id: reference
frames: 288
scene: reference
caption: The RMS passes, but q06 exceeds the five millimetre maximum gate.
narration: Reveal the manual target only now. The candidate-centred target sections
  retain the actual q06 offset. Returned coordinates 219.3, 162.3, 150.2 differ from
  the manual target 218.75, 156.25, 152.25 by 6.412 millimetres in three dimensions.
  Eight-point RMS is 2.604 millimetres, so the RMS gate passes and the maximum gate
  fails. The other seven points are within 2.181 millimetres. Frozen reward remains
  zero.
visual: Cut to three target sections centred on the returned q06; reveal the manual
  point, residual and three dashed five-millimetre radius circles in the same physical
  frame.
channels:
  depth:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## judgment

```beat
id: judgment
frames: 240
scene: judgment
caption: Preserve the failed frozen gate alongside the user’s practical acceptance.
narration: The user visually judged q06 good enough for the intended example. The
  full-source condition was retired as a hard-task candidate and the idea parked.
  That decision did not correct the reference, change the tolerance, regrade the output
  or provide independent clinical adjudication. The frozen numerical result remains
  unchanged.
visual: Keep candidate and reference in their shared physical frame beside separately
  labelled numerical result and user judgment.
channels:
  depth:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## conditions

```beat
id: conditions
frames: 288
scene: conditions
caption: The case-one and case-three contracts expose different source information.
narration: BR-021 case one compares a supplied oblique slice with a paired full-volume
  condition. Its paired condition supplies exact manual source queries, whereas slice
  queries are projected by up to 0.313 millimetres. BR-023 reused the frozen two-dimensional
  case and later tested four author component interventions. BR-024 case three uses
  a harder supplied slice. BR-028 adds source depth but preserves those projected
  queries. Case two was not admitted or model-trialled.
visual: Show both actual complete source views with query markers, independently posed;
  summarize all four contracts without pooling outcomes.
channels:
  depth:
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

## limits

```beat
id: limits
frames: 264
scene: limits
caption: One attempt per condition cannot isolate the effect of added source depth.
narration: Case three moved from 12.731 millimetres RMS and 32.203 maximum in BR-024
  to 2.604 and 6.412 in BR-028. One fresh attempt per condition confounds source context,
  solver strategy and variance. A public-input author method already passed the two-dimensional
  feasibility gate. Eight sparse correspondences do not validate a dense deformation
  field, topology or unqueried regions. Public annotation availability also limits
  contamination control.
visual: Return to the actual source and target sections with the full-source answer,
  qualified condition comparison and feasibility boundary.
channels:
  depth:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```
