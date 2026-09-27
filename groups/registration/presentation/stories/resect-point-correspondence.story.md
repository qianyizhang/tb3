---
schema: 2
id: resect-point-correspondence
title: Audit MRI-to-intraoperative-ultrasound correspondences
locale: en
purpose: Locate a homologous ultrasound point from a supplied MRI query while measuring
  the shared-frame shortcut.
scope: Three selected public cases; proposed voxel-output task. Query-centred source
  views, optional masks and reader-only manual targets. Separate executed world-output
  pilot; no new model result.
recipe: resect-correspondence-v1
asset_pack: retained-resect-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/registration/presentation/briefs/resect-mri-us-correspondence.md
- groups/registration/ideas/resect-mri-us-correspondence.md
- groups/registration/presentation/sources/resect-sample.json
- groups/registration/presentation/briefs/tb3-resect-point-pilot.md
- datasets/resect.json
- presentation/task-explorer/resect/manifest.json
- scripts/build_resect_assets.py
- scripts/build_respiratory_assets.py
---

# MRI to ultrasound correspondence

## inputs

```beat
id: inputs
frames: 240
scene: inputs
caption: Begin with complete native MRI and ultrasound volumes, not reference-centred
  crops.
narration: The proposed task supplies complete FLAIR and pre-resection three-dimensional
  ultrasound volumes, one MRI world query, and the same physical position as an initial
  ultrasound candidate. These complete native sections are previews through the supplied
  point. MRI and ultrasound axes differ. The selected teaching query was chosen with
  reference annotations; it is not blinded.
visual: Show six complete native sections through the query. Keep paired targets and
  tumor masks hidden.
channels:
  scan:
  - 0.5
  - 0.5
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

## frame

```beat
id: frame
frames: 288
scene: frame
caption: A shared world point has different native voxel indices.
narration: NIfTI affines map voxel indices to RAS-positive world millimetres. Inverting
  the ultrasound affine maps the same MRI query to ultrasound voxel 113.000, 229.394,
  164.959. This supplies an initial navigation guess. It neither estimates a registration
  nor proves that the two locations contain homologous anatomy.
visual: Compare co-oriented source sections centred on one world point and show both
  native indices.
channels:
  scan:
  - 0.5
  - 0.5
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

## inspect

```beat
id: inspect
frames: 288
scene: inspect
caption: Sweep adjacent source sections while keeping the query fixed.
narration: Thirteen axial sections span six millimetres below to six above the query.
  Both modalities use the same RAS orientation, centre and 48-millimetre field. Compare
  anatomy across slices despite different contrast and ultrasound speckle. The rings
  project the fixed query; only the middle section contains it. The animation moves
  the inspection plane, not a predicted correspondence.
visual: Advance through the 13 actual image pairs and update the world-z and out-of-plane
  offset.
channels:
  scan:
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

## helpers

```beat
id: helpers
frames: 240
scene: helpers
caption: Tumor masks narrow region search but do not supply point correspondence.
narration: The optional helper condition adds paired tumor masks. Pink marks the MRI
  mask; cyan marks the ultrasound mask. Native geometry is checked before nearest-neighbor
  sampling. The base condition withholds these masks. Their reference-guided role
  and separate noncommercial share-alike license remain explicit.
visual: Reveal aligned tinted tumor masks over the fixed query-centred axial images
  with matching fill legends.
channels:
  scan:
  - 0.5
  - 0.5
  helper:
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
caption: Return a native US voxel point, confidence and image evidence.
narration: The proposed output is a continuous native ultrasound voxel coordinate,
  confidence and a concise feature description. The example merely retains the initial
  candidate with zero confidence and no anatomical claim. It is an unchanged teaching
  control, not a model answer. The evaluator converts the returned voxel through the
  ultrasound affine before computing physical error.
visual: Reveal only the unchanged teaching control and native output schema. No corrected
  anatomical target is invented.
channels:
  scan:
  - 0.5
  - 0.5
  helper:
  - 0
  - 0
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
caption: Reveal the manual target without moving the image centre.
narration: Case 2 pair thirteen has a 7.166-millimetre three-dimensional separation
  between the initial candidate and manual ultrasound target. Each fixed ultrasound
  section shows their projected positions and reports the target offset normal to
  its plane. No two-dimensional segment alone is the full error. Score improvement
  over no-op, movement and worse corrections separately; a pass threshold remains
  unfrozen.
visual: Reveal the manual cross on three unchanged RAS sections and the full physical-distance
  calculation.
channels:
  scan:
  - 0.5
  - 0.5
  helper:
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

## cases

```beat
id: cases
frames: 240
scene: cases
caption: The same-world no-op is much stronger in Case 1 than Cases 2 and 3.
narration: Across fifteen published pairs per case, mean no-op error is 1.82, 5.68
  and 9.58 millimetres. The plot contains all forty-five distances. These describe
  the source geometry, not agent outcomes. Correcting misalignment while preserving
  already-close points is a hypothesis to test, not a capability established by this
  animation.
visual: Plot all 45 unchanged-coordinate distances with a shared millimetre axis and
  per-case summaries.
channels:
  scan:
  - 0.5
  - 0.5
  helper:
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

## limits

```beat
id: limits
frames: 288
scene: limits
caption: Freeze the proposed study separately from the executed two-query pilot.
narration: The base, mask-assisted and coordinate-only conditions require explicit
  sampling, viewer, ambiguity and aggregation rules before execution. Public training-set
  exposure limits unseen-test claims. Older figures were independently reference-centred.
  A separate pilot already used two selected queries and world-coordinate output;
  its results belong to that entry. This three-case voxel-output proposal remains
  unfrozen and no trial is launched here.
visual: Compare the three assistance contracts and retain the proposed-versus-executed
  boundary.
channels:
  scan:
  - 0.5
  - 0.5
  helper:
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
