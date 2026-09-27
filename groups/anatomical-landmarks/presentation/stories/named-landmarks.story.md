---
schema: 2
id: named-landmarks
title: 'Named anatomy: locate, name and recognize unavailable targets'
locale: en
purpose: Explain native-coordinate localization separately from anatomical naming,
  visible misses and unavailable-target decisions.
scope: Three subjects · 11 model attempts · Reader-selected views with separate private-reference reveals.
recipe: named-landmarks-v1
asset_pack: retained-named-landmarks-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomical-landmarks/presentation/briefs/tb3-named-landmarks.md
- groups/anatomical-landmarks/presentation/sources/named-landmark-audit.json
- groups/anatomical-landmarks/presentation/sources/named-landmark-source-terms.json
- groups/anatomical-landmarks/findings/landmarks-availability-and-localization.json
- docs/evidence/br040-results.json
- scripts/build_named_landmark_assets.py
---

# Native location and anatomical identity

## Names are supplied; locations must be found

```beat
id: inputs
scene: inputs
frames: 192
caption: Names are supplied; locations must be found
narration: The inputs are actual native CT or MRI volumes with anatomical names and
  definitions. PDDCA asks for chin, condyles and dens; AFIDs supplies thirty-two names;
  VerSe requests twenty-six vertebral names. The later protocols add native arrays,
  geometry and inspection helpers. These centre sections contain no supplied detections.
  Views are fitted independently, and no private reference is shown.
visual: Three unannotated native midline sections, actual shapes, target inventories
  and source names. These are source images, not schematic anatomy.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## Native indices become RAS millimetres through the affine

```beat
id: coordinates
scene: coordinates
frames: 192
caption: Native indices become RAS millimetres through the affine
narration: This is the retained Terra T4 point in the partial CT. Its zero-based native
  triple maps through the supplied affine to RAS millimetres. Here increasing i goes
  left, j anterior and k superior. Fractional indices are allowed. A consistent conversion
  identifies where a point lies, but cannot establish that the anatomical name is
  correct. The displayed region is selected for reader review.
visual: Three calibrated sections with saved T4 cross; show its exact voxel and world
  triples. References remain hidden.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect acquired sections; do not infer depth from one image

```beat
id: search
scene: search
frames: 168
caption: Inspect acquired sections; do not infer depth from one image
narration: Step through sixteen actual axial sections near the later diagnostic region.
  This is teaching navigation through native pixels, not a reconstruction of an agent
  search trajectory. The region was selected for reader review. The solver had the
  complete supplied volume, with no private points. A named target must be localized
  in three dimensions.
visual: Advance through actual k=857 to 917 sections. Print each native index and
  axis directions; show neither outputs nor references.
channels:
  view:
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

## Terra claims observed T4; Sol returns out_of_fov

```beat
id: output
scene: output
frames: 192
caption: Terra claims observed T4; Sol returns out_of_fov
narration: The submitted outputs disagree about T4 availability. Terra provides an
  observed point inside the cropped scan; Sol returns out of field of view with no
  point. A real-looking bony location does not resolve whether the name is correct.
  These crosses and circles are stored outputs, not interpolated solver estimates.
  The private reference remains hidden.
visual: Hold the same three native diagnostic planes with only the Terra T4 cross
  and both saved statuses.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal: the T4 claim lies near source T5

```beat
id: reference
scene: reference
frames: 240
caption: 'Reveal: the T4 claim lies near source T5'
narration: Reveal the private source point for T5. Terra labelled its nearby point
  T4, only two point one four millimetres from the T5 centre. The true T4 lies above
  this crop. This is a wrong-level detection on real bone. Every displayed marker
  is projected onto the section; signed offsets below each plane show the remaining
  depth difference. Full physical coordinates determine distances.
visual: Reveal the green private T5 plus beside the orange saved T4 cross. Keep target
  names on all offset labels.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Zero outside detections still leaves visible T5 missed

```beat
id: availability
scene: availability
frames: 216
caption: Zero outside detections still leaves visible T5 missed
narration: Now inspect the actual T5 request. Sol returned out of field of view despite
  T5 being visible, so there is no Sol point to draw. Terra returned another point
  with a large depth error. Sol avoids false observed claims on all eleven outside
  targets but misses one of thirteen visible targets. Its within-tolerance denominator
  stays thirteen; the mean error uses only twelve returned points.
visual: Switch the saved-output key to T5 without moving the private point. Show the
  empty Sol detection and signed Terra plane offsets.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## The crop removes counting anchors, not just pixels

```beat
id: conditions
scene: conditions
frames: 216
caption: The crop removes counting anchors, not just pixels
narration: Full and partial CT reuse the same subject. The native k-zero-to-nine-twenty
  crop keeps thirteen visible targets, puts eleven outside and retains two source-confirmed
  absent requests, T13 and L6. The full image has twenty-four visible targets. Earlier
  PDDCA and MRI conditions use different target sets and output conventions; the two
  accepted cropped PDDCA responses were outside-target nulls, not successful visible
  localizations.
visual: Full and partial actual midline sections, shapes and separately disclosed
  reference counts. Retain the earlier world/voxel contract distinctions in the output
  panel.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Coordinate consistency does not establish correct anatomy

```beat
id: condyle
scene: condyle
frames: 192
caption: Coordinate consistency does not establish correct anatomy
narration: The BR-038 PDDCA right-condyle prediction is thirty-two point zero seven
  millimetres from its private reference. Long sections make the separation visible.
  The audited native arrays, reference conversion and helper mappings are consistent;
  that does not rule out a local axis mistake or selection of the wrong structure.
  No unadjudicated structure identity is assigned to the erroneous point.
visual: Actual reference-selected PDDCA sections, saved Terra cross and private condyle
  plus, with physically scaled planes and signed depth offsets.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## MRI improvement used generic atlas assistance

```beat
id: mri
scene: mri
frames: 216
caption: MRI improvement used generic atlas assistance
narration: 'Both saved splenium points are close here: one point five six millimetres
  for Terra and zero point eight three for Sol. Across all thirty-two fiducials, Sol
  reaches fourteen within three millimetres versus three for Terra. Sol used a generic
  AFIDs/MNI affine proposal and manual review. Model and reasoning effort also changed.
  The exact original runtime atlas image is not retained, so no invented atlas or
  registration intermediate is displayed.'
visual: Show actual AFID 20 MRI sections and both stored points, with private source
  reveal and the assistance boundary.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## The anterior commissure is a local counterexample

```beat
id: counterexample
scene: counterexample
frames: 192
caption: The anterior commissure is a local counterexample
narration: Aggregate MRI improvement does not mean every point improved. At the anterior
  commissure, Terra is zero point seven two millimetres from the reference and Sol
  is eight point eight one millimetres away. The same native coordinate rules apply.
  These views are centred for reader comparison. All MRI targets are visible, so this
  condition does not test unavailable-target behavior.
visual: Show AFID 1 sections, preserved saved markers and source plus. Print each
  full 3D error and plane offsets.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Report the threshold and the complete visible denominator

```beat
id: comparison
scene: comparison
frames: 360
caption: Report the threshold and the complete visible denominator
narration: Cycle through the original threshold counts. Full CT mean error improves
  but the count within five millimetres falls from two to one out of twenty-four.
  Partial CT Sol reaches four of thirteen within five millimetres, although only twelve
  visible points were returned. MRI uses three, five and ten millimetres. These are
  selected single attempts with different model, effort and methods, not a causal
  or population comparison.
visual: Hold each observed threshold table for about five seconds; no interpolation
  of reported counts. Preserve visible denominators and separate outside-target errors.
channels:
  view:
  - 0
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Preserve useful results and their limits

```beat
id: limits
scene: limits
frames: 240
caption: Preserve useful results and their limits
narration: The source audit reproduces thirty saved score records from twenty-seven
  unique executions, including eleven model attempts. It does not run new inference.
  AFIDs points twenty-two and twenty-seven have a source rater more than three millimetres
  from the consensus; retain that uncertainty without changing frozen references or
  scores. Atlas-image recovery remains incomplete. Separate coordinate correctness,
  naming, availability and localization whenever reporting these results.
visual: End with exact scope, reference uncertainty, atlas recovery gap and the no-new-execution
  boundary.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```
