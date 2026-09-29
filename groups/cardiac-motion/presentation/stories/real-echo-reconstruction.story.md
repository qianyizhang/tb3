---
schema: 2
id: real-echo-reconstruction
title: 'Four real echo planes to a saved moving cavity surface'
locale: en
purpose: Explain the BR-032 source images, calibrated sparse-plane interpretation, saved mesh,
  image-only withheld review and artifact-versus-anatomy boundary.
scope: One preselected EchoSlicer volunteer sequence; one original agent attempt and retained controls.
recipe: cardiac-real-echo-v1
asset_pack: retained-real-echo-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/cardiac-motion/presentation/briefs/tb3-real-echo-reconstruction.md
- groups/cardiac-motion/presentation/sources/real-echo-audit.json
- groups/cardiac-motion/presentation/sources/real-echo-resolution.json
- docs/evidence/br032-real-echo-results.json
- scripts/build_cardiac_real_echo_assets.py
---

# A real acquisition gives four sparse planes, not a cavity answer

## Replay the actual solver images

```beat
id: inputs
scene: inputs
frames: 144
caption: Four synchronized reslices; 18 original times
narration: The solver received seventy-two grayscale images from one real three-dimensional
  ultrasound acquisition. These four simultaneous planes each show the same eighteen source
  times. They are reslices, not four separate probe recordings. No contour, seed, mesh or
  cavity answer was supplied.
visual: Replay the four actual 256-by-256 public plane sequences together, with frame and
  elapsed source time. Show no saved output or withheld review plane.
channels:
  phase:
  - 0
  - 1
  planes:
  - 0
  - 0
  output:
  - 0
  - 0
  alternative:
  - 0
  - 0
  review:
  - 0
  - 0
  control:
  - 0
  - 0
```

## Locate pixels in millimetres

```beat
id: geometry
scene: geometry
frames: 120
caption: Supplied geometry locates each pixel; it does not label anatomy
narration: The seventy-third public file fixes each plane origin and its in-plane directions.
  A pixel centre maps into the task frame using zero point seven five millimetres per pixel
  about centre one hundred twenty-seven point five. The two long-axis planes and the short-axis
  planes at depths sixty-five and one hundred five millimetres sample different locations in
  the same acquisition.
visual: Keep all four actual images visible and reveal calibrated row and column axes. Do
  not show a contour or inferred surface.
channels:
  phase:
  - 0.5294117647058824
  - 0.5294117647058824
  planes:
  - 1
  - 1
  output:
  - 0
  - 0
  alternative:
  - 0
  - 0
  review:
  - 0
  - 0
  control:
  - 0
  - 0
cut: intentional-cut
```

## Separate image viewing from fixed assumptions

```beat
id: interpretation
scene: interpretation
frames: 120
caption: The original agent inspected pixels, then fixed measurement tables
narration: Its retained trace shows individual images, contact sheets and pixel grids being
  inspected. The agent then recorded framewise radii, centres, basal depths and apical depths
  in six fixed observed tables. The basal cap and shape between planes are modeling choices,
  not source annotations.
visual: Continue actual synchronized images. Keep output hidden while naming the original
  inspection and its unobserved completion choices.
channels:
  phase:
  - 0.11764705882352941
  - 0.11764705882352941
  planes:
  - 1
  - 1
  output:
  - 0
  - 0
  alternative:
  - 0
  - 0
  review:
  - 0
  - 0
  control:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the saved moving surface

```beat
id: reconstruction
scene: reconstruction
frames: 216
caption: A saved 1,202-vertex surface intersects the original image plane
narration: The submitted primary output has eighteen closed meshes, each with one thousand
  two hundred two vertices and two thousand four hundred triangles. Cyan is the section of
  that saved surface through a calibrated input plane. The fixed millimetre projection and
  volume axis replay its motion without normalizing each frame. Volumes from fifty-four to
  one hundred seventy-eight millilitres are properties of the model geometry, not clinical
  ejection fraction.
visual: Animate the actual long-zero-degree image, its saved mesh section, a sampled shaded
  projection of the same saved vertices and the full 18-frame volume curve. Use fixed scales.
channels:
  phase:
  - 0
  - 1
  planes:
  - 1
  - 1
  output:
  - 1
  - 1
  alternative:
  - 0
  - 0
  review:
  - 0
  - 0
  control:
  - 0
  - 0
cut: intentional-cut
```

## Change the unobserved basal completion

```beat
id: alternatives
scene: alternatives
frames: 168
caption: An alternative saved shape changes assumptions, not confidence coverage
narration: The orange saved basal alternative shares the timing and mesh connectivity of
  the primary but changes the completed cavity. It is one of three retained alternatives.
  Their spread describes sensitivity to chosen assumptions; it is not a calibrated interval
  that must contain the true cavity.
visual: Hold a matched source frame, show its orange basal-alternative section and sampled
  mesh, and plot the dashed alternative volume curve against cyan primary on fixed axes.
channels:
  phase:
  - 0.17647058823529413
  - 0.17647058823529413
  planes:
  - 1
  - 1
  output:
  - 1
  - 1
  alternative:
  - 1
  - 1
  review:
  - 0
  - 0
  control:
  - 0
  - 0
cut: intentional-cut
```

## Reveal withheld images, not truth contours

```beat
id: review
scene: review
frames: 180
caption: Four withheld ultrasound planes permit image-only section review
narration: The reader now sees long-axis forty-five and one hundred thirty-five degrees and
  short-axis depths forty-five and eighty-five millimetres. These images were withheld from
  the solver. Cyan sections are intersections of the submitted surface with the calibrated
  review planes. An absent section means the saved mesh does not cross that plane. There is
  no independent contour or three-dimensional truth here to score overlap against.
visual: Explicitly reveal all four actual withheld image sequences with the matching saved
  mesh sections, including empty sections where the retained geometry does not intersect.
channels:
  phase:
  - 0
  - 1
  planes:
  - 1
  - 1
  output:
  - 1
  - 1
  alternative:
  - 0
  - 0
  review:
  - 1
  - 1
  control:
  - 0
  - 0
cut: intentional-cut
```

## Test what reward and replay actually show

```beat
id: controls
scene: controls
frames: 180
caption: Format reward 1 also admits an image-ignorant static ellipsoid
narration: The primary and a static ellipsoid format control both received artifact reward
  one; a no-output control received zero. Reward checks file structure, surface validity
  and volume arithmetic, not anatomy. A later replay changed sixty-eight of seventy-two
  image files to static inputs yet the saved script returned exactly the same mesh points.
  That limits reusable executable input dependence; it does not erase the original trace's
  real image viewing.
visual: Show the original primary volume curve beside the static-control volume at eighty
  point five three millilitres, with equal format rewards labelled separately. Keep the
  withheld review pixels out of this chapter.
channels:
  phase:
  - 0.5294117647058824
  - 0.5294117647058824
  planes:
  - 1
  - 1
  output:
  - 1
  - 1
  alternative:
  - 0
  - 0
  review:
  - 0
  - 0
  control:
  - 1
  - 1
cut: intentional-cut
```

## Keep the evidence boundary visible

```beat
id: limits
scene: limits
frames: 144
caption: One real case and a valid artifact do not establish clinical function
narration: This is one preselected volunteer sequence and one original agent attempt. The
  eighteen frames are not an adjudicated beat. The saved mesh has no independent cavity
  contour or paired three-dimensional reference; persistent surface indices do not track
  myocardial material. The withheld images are useful for qualitative review, not a
  clinical ejection fraction, strain, diagnosis or population performance claim.
visual: Return to the explicitly revealed image-only review at a fixed source frame, with
  cyan sections and the one-case evidence limits.
channels:
  phase:
  - 0.5294117647058824
  - 0.5294117647058824
  planes:
  - 1
  - 1
  output:
  - 1
  - 1
  alternative:
  - 0
  - 0
  review:
  - 1
  - 1
  control:
  - 0
  - 0
cut: intentional-cut
```
