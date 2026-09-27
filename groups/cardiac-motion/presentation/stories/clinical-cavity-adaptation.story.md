---
schema: 2
id: clinical-cavity-adaptation
title: 'Clinical cavity: track, measure and test'
locale: en
purpose: Explain current-image tracking, supplied initialization, saved input responses and
  the separation of surface proximity from cavity contraction accuracy.
scope: One Sol/xhigh attempt and two case replays. Source annotations lack independent adjudication.
recipe: clinical-cavity-v1
asset_pack: retained-clinical-cavity-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/cardiac-motion/presentation/briefs/tb3-clinical-cavity-adaptation.md
- groups/cardiac-motion/presentation/sources/clinical-cavity-audit.json
- docs/evidence/br034-clinical-adaptation-results.json
- scripts/build_clinical_cavity_assets.py
---

# Actual motion, separate judgments

## Start with actual acquired images

```beat
id: images
scene: inputs
frames: 192
caption: Start with actual acquired images
narration: The solver receives eighteen consecutive acquired three-dimensional ultrasound frames,
  calibration and an initial cavity surface. These center sections show the actual prepared
  pixels. Sampling is one millimeter and about twenty-two point six volumes per second. Playback
  here is slowed and holds discrete acquired frames; no intermediate motion is invented. Later
  reference surfaces remain private.
visual: Play all eighteen unannotated source frames in the calibrated native slice planes. Show
  native indices, elapsed milliseconds and the actual input inventory.
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

## The initial cavity is supplied

```beat
id: initial
scene: initial
frames: 192
caption: The initial cavity is supplied
narration: At frame zero, the supplied endocardial surface already includes its basal closure,
  with nineteen hundred forty-six vertices and thirty-eight hundred eighty-eight triangles.
  The initial surface determines the local coordinate basis and crop. These local axes are not
  anatomical planes. Later tracking is still required; dense indices do not identify myocardial
  material points.
visual: Hold actual frame zero. Reveal only the blue-grey public initial surface and its calibrated
  sections; leave saved output and later reference hidden.
channels:
  phase:
  - 0
  - 0
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

## Current pixels drive the saved surface

```beat
id: tracking
scene: tracking
frames: 240
caption: Current pixels drive the saved surface
narration: The submitted executable uses sequential three-dimensional TV-L1 optical flow, advects
  cavity vertices and distributes loop drift while preserving initialization. The animation
  shows its saved surfaces, not an invented flow field. Integrating each closed surface yields
  the cyan volume curve. Its maximum occurs at frame two and minimum at ten, producing an ejection
  fraction of twenty-two point zero one percent.
visual: Play every saved primary mesh and corresponding image; synchronize its section contours
  and float64 volume cursor. Keep the reference hidden.
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

## Reveal the private reference at systole

```beat
id: reveal
scene: reference
frames: 192
caption: Reveal the private reference at systole
narration: At reference systole, the saved cavity remains visibly larger than the source annotation.
  The reference ejection fraction is forty-five point three one percent, giving a twenty-three
  point three zero percentage-point error. Mean sampled surface distance is only one point eight
  nine millimeters. A close average surface therefore does not establish accurate contraction.
  The gold annotation is a reader reveal, not additional solver input.
visual: Hold primary reference-systolic frame eleven. Reveal the gold surface beside the cyan
  surface at equal scale, dashed reference sections and the private volume curve.
channels:
  phase:
  - 0.6470588235294118
  - 0.6470588235294118
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

## Compare the full acquired beat

```beat
id: reference-motion
scene: reference
frames: 192
caption: Compare the full acquired beat
narration: Both surfaces use the same fixed local millimeter frame. Every timestamp, section
  and volume cursor remains synchronized. No per-frame normalization or later alignment shrinks
  the disagreement. Reference surfaces are operator and software derived; there is no independent
  cardiologist adjudication, material-motion truth or etiology here.
visual: Replay the entire beat with equal-scale paired surfaces and source sections, retaining
  the original reference and predicted volume curves.
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
  - 1
  - 1
cut: intentional-cut
```

## Replay on a separate reduced-function case

```beat
id: hidden
scene: patient
frames: 240
caption: Replay on a separate reduced-function case
narration: The unchanged executable completes on a hidden thirty-five-frame case with its own
  images, calibration and initial surface. Its ejection fraction is twenty-one point six eight
  percent against forty-seven point six two percent in the source, an error of twenty-five point
  nine four percentage points. Mean distance passes while end-systolic volume and functional
  category fail. This is executable transfer, not a second model attempt.
visual: Cut to the actual hidden-case acquisition. Play all thirty-five frames with paired surfaces,
  private curve and correct native timestamps.
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
  - 1
  - 1
cut: intentional-cut
```

## A supplementary preserved-function case

```beat
id: preserved
scene: preserved
frames: 240
caption: A supplementary preserved-function case
narration: A supplementary forty-eight-frame case was added after dispatch and before output
  inspection. Its saved ejection fraction is twenty-nine point eight zero percent against sixty
  point two nine percent, an error of thirty point four nine percentage points. Successful execution
  and mean-distance agreement coexist with substantial contraction error. These purposively
  selected cases do not estimate population performance.
visual: Cut to the preserved acquisition and play its forty-eight retained frames at fixed within-case
  scale. Identify its supplementary status.
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
  - 1
  - 1
cut: intentional-cut
```

## Repeated images produce stationary output

```beat
id: static-response
scene: static
frames: 192
caption: Repeated images produce stationary output
narration: In the retained static-input check, the executable sees the first volume repeated
  eighteen times. Its output vertices remain exactly stationary, with zero root-mean-square
  motion and zero ejection fraction. This passes the prespecified input-response limits. The
  artificial counterfactual is not a diagnosis of a biological heart.
visual: Show the actual repeated input frame, stationary saved mesh and constant volume curve
  while the counterfactual index advances. Hide clinical reference curves.
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

## A phase shift permutes the output exactly

```beat
id: shift-response
scene: shift
frames: 240
caption: A phase shift permutes the output exactly
narration: The control shifts the input by five frames and declares initialization at index
  five. Images and saved surfaces follow that same circular order. Undoing the shift produces
  exactly the original points and zero milliliter volume error. This is evidence that the executable
  follows current inputs, but it does not repair the clinical-reference contraction errors.
visual: Animate the retained shifted output, mapped original frame indices and shifted curve,
  including initialization at five and the wrap in source acquisition order.
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

## A static surface can pass the mean-distance gate

```beat
id: geometry-control
scene: judgment
frames: 240
caption: A static surface can pass the mean-distance gate
narration: A different control repeats only the initial surface against the moving primary reference.
  It reaches a passing two point seven zero millimeter mean distance, yet its ejection-fraction
  error is forty-five point three one percentage points. The independent p95, ejection-fraction,
  end-diastolic and end-systolic volume gates remain visible. Category agreement is a separate
  check. Geometry alone is insufficient.
visual: Show static initialization beside the moving private primary surface. Reveal its constant
  curve and all original numerical gate outcomes; distinguish this from the static-image response
  check.
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
  - 1
  - 1
cut: intentional-cut
```

## Preserve the result and its limits

```beat
id: output
scene: output
frames: 240
caption: Preserve the result and its limits
narration: Return the full mesh sequence, executable, method, per-frame volumes and bounded
  interpretation, alongside the saved pre-model assessment. One Sol xhigh attempt completed
  normally with a valid artifact and original reward zero. The initial uncertain mild-to-moderate
  impression became severe from its own computed ejection fraction. This within-session change
  proves no causal effect of modeling. No calibrated clinical interval, strain or disease etiology
  is established.
visual: Return to the primary reference-systolic disagreement and original curves. Show output
  schema, one-attempt denominator, original reward and clinical limits.
channels:
  phase:
  - 0.6470588235294118
  - 0.6470588235294118
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
