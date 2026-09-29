---
schema: 2
id: cardiac-anchor-feasibility
title: 'Sparse anchors: track an echo cavity, then test the mesh'
locale: en
purpose: Explain BR-027's actual one- and two-anchor packages, saved image-conditioned masks,
  interpolated mesh and the separate input-view and withheld-direction judgments.
scope: One previously inspected FeEcho4D patient; author development baselines, no independent model attempt.
recipe: cardiac-anchor-v1
asset_pack: retained-cardiac-anchor-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/cardiac-motion/presentation/briefs/tb3-cardiac-anchor-feasibility.md
- groups/cardiac-motion/presentation/sources/cardiac-anchor-audit.json
- groups/cardiac-motion/presentation/sources/cardiac-anchor-resolution.json
- docs/evidence/br027-cardiac-results.json
- scripts/build_cardiac_anchor_assets.py
---

# Sparse contours are starting help, not motion answers

## Read the four actual video directions

```beat
id: inputs
scene: inputs
frames: 180
caption: Four real radial echo videos are the input
narration: FeEcho4D Patient001 supplies thirty source frames in each of four radial views,
  one hundred twenty images in all. The panels replay those actual prepared pixels, shown
  at half resolution. The presumed view angles are zero, forty-five, ninety and one hundred
  thirty-five degrees. These radial poses were assumed, not independently measured.
visual: Replay all four native image sequences together, labelled by source plane and filename frame.
  Show no contour, output or evaluator reference yet.
channels:
  phase:
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
```

## Reveal exactly the supplied anchor

```beat
id: anchors
scene: anchors
frames: 144
caption: Frame 2 is a supplied contour, not a tracked result
narration: The one-anchor package gives one cavity mask per view at filename frame two.
  The two-anchor package additionally gives frame seventeen in each view. No other
  target-time masks, dense contours, volumes or meshes are supplied to the solver.
  Source reference contours stay hidden from the reader here.
visual: Hold frame 2 across all four views and reveal the blue-grey supplied mask boundaries.
channels:
  phase:
  - 0.034482758620689655
  - 0.034482758620689655
  helper:
  - 1
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Track with one anchor

```beat
id: tracking-one
scene: tracking-one
frames: 240
caption: One anchor leaves motion to be inferred from current images
narration: The retained author baseline tracks through successive ultrasound frames with
  DIS optical flow and warps signed-distance masks. Cyan boundaries replay its saved
  predictions. The saved cavity-volume curve is an output of its mesh sequence;
  comparison against hidden source annotations comes later. This is an author
  development method on one previously inspected patient.
visual: Animate thirty native frames with synchronized saved input-view masks and a saved
  cavity-volume cursor. Do not show evaluator contours.
channels:
  phase:
  - 0
  - 1
  helper:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Add a second supplied time

```beat
id: tracking-two
scene: tracking-two
frames: 240
caption: A second anchor changes the assistance
narration: The two-anchor package supplies the same frame two and also frame seventeen
  in every view. Its saved baseline propagates from both anchors and blends the fields.
  At supplied frame seventeen, exact agreement with the supplied mask is not tracking
  success. The second anchor changes the assistance; numerical comparisons are revealed
  only after the source-reference chapter.
visual: Replay all four views with the saved two-anchor masks, including the supplied
  frame-17 helper, and its separate saved volume curve.
channels:
  phase:
  - 0
  - 1
  helper:
  - 1
  - 1
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Interpolate a surface into unseen directions

```beat
id: surface
scene: surface
frames: 240
caption: Four image directions do not directly observe every section
narration: The saved radial profiles are interpolated into a closed cavity mesh at each
  of thirty times. This cyan plane-eight cross-section comes from that saved mesh;
  plane eight was not a solver input. The source image stays hidden until the reader
  reference reveal. Each mesh has four thousand five hundred thirty-eight vertices
  and nine thousand seventy-two faces. Shared vertex indexing is a surface parameterization,
  not observed myocardial material tracking.
visual: Animate the saved one-anchor mesh section across the thirty frames on a neutral
  field, without any hidden source image or reference contour.
channels:
  phase:
  - 0
  - 1
  helper:
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

## Reveal one withheld native section

```beat
id: reference
scene: reference
frames: 180
caption: Reveal the withheld source plane only for review
narration: At plane eight, frame seventeen, the gold boundary is a source mask kept by
  the evaluator. It was not supplied to either package. The cyan saved mesh section
  differs locally. The dense volume curve is fitted from all thirty-six source directions,
  including the evaluation views; it is not independent three-dimensional or clinical truth.
visual: Hold frame 17 and reveal the actual withheld image and gold source boundary
  beside the dense annotation-derived curve.
channels:
  phase:
  - 0.5517241379310345
  - 0.5517241379310345
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

## Separate supplied agreement from unsupplied tracking

```beat
id: comparison
scene: comparison
frames: 180
caption: Frame 17 and frame 25 answer different questions
narration: On input plane twenty-eight, frame seventeen is a supplied mask only in the
  two-anchor condition. The one-anchor cyan mask had to be tracked there. Frame
  twenty-five is unsupplied to both conditions. The four matched panels pair both
  methods at each time, with gold source boundaries as reader-only reveals.
visual: Show a four-panel grid with one and two anchors at frame 17, then both at frame
  25, with the corresponding saved masks and revealed source boundaries.
channels:
  phase:
  - 0.5517241379310345
  - 0.5517241379310345
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

## Keep the interpretation bounded

```beat
id: limits
scene: limits
frames: 180
caption: A useful development screen is not clinical validation
narration: Two-anchor DIS passes the round's proposed shape, volume, EF and topology
  gates; one-anchor DIS does not. Mean withheld Dice is zero point eight eight seven
  versus zero point nine two zero; full-curve volume error is twenty-nine point one six
  versus seven point eight two percent; EF error is twenty-one point six zero versus
  zero point eight two percentage points. These gates are development targets, not
  clinical tolerances. The author had inspected this same patient before method development,
  and no independent model attempt was run. No unique three-dimensional motion,
  material strain or performance on new patients is established.
visual: Return to the selected withheld section and show the saved-versus-source
  distinction with the one-patient denominator and output schema.
channels:
  phase:
  - 0.5517241379310345
  - 0.5517241379310345
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
