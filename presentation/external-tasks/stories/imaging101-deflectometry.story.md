---
schema: 2
id: imaging101-deflectometry
title: Recover lens geometry from refracted fringe patterns
locale: en
purpose: Explain calibrated fringe phase, saved refracting-lens geometry and the limited
  parameter score.
scope: 'One lens: source figures, saved parameters and synthetic controls. No raw-stack replay or new optical fit.'
recipe: imaging101-deflectometry-v1
asset_pack: retained-imaging101-deflectometry-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-differentiable-deflectometry.md
- presentation/external-tasks/sources/imaging101-deflectometry-audit.json
- scripts/audit_imaging101_deflectometry.py
- scripts/build_imaging101_deflectometry_assets.py
---

# Canonical refractive deflectometry explanation

## Two cameras observe stripes refracted by one lens

```beat
id: inputs
scene: inputs
frames: 528
caption: Two cameras observe stripes refracted by one lens
narration: Two calibrated cameras observe a display through two refracting lens surfaces.
  These measurement panels come from the pinned notebook. They are already normalized,
  masked and resampled, so their pixels cannot recover raw camera intensities. The
  original setup records three fringe periods and eight shifts with each camera, both
  with and without the lens. Repeated rows in the notebook show the same two cameras,
  not additional cases. The full raw archive is unavailable.
visual: Highlight the two retained measurement panels in turn; label their rendered
  source role and the unavailable raw stacks.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
```

## Camera pixels and display millimeters are different frames

```beat
id: calibration
scene: calibration
frames: 528
caption: Camera pixels and display millimeters are different frames
narration: The source crops a seven hundred sixty-eight pixel square from a two thousand
  forty-eight pixel sensor, starting at row and column six hundred forty. This diagram
  shows those index coordinates exactly. The display has a separate pitch of zero
  point one one five millimeters per pixel. Supplied camera and display transforms
  connect the frames. Each of the three fringe periods has four horizontal and four
  vertical phase shifts. A supplied lens prescription also constrains the problem.
visual: Show the exact center-crop diagram beside calibration quantities with camera-pixel
  and display-millimeter roles explicit.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Four shifts recover phase at one fixed pixel

```beat
id: phase
scene: phase
frames: 672
caption: Four shifts recover phase at one fixed pixel
narration: This chapter uses a separate thirty-two by thirty-two synthetic fixture.
  At a selected pixel, subtract the third intensity from the first, and the second
  from the fourth. Their two-argument arctangent gives wrapped phase. The orange mark
  identifies the same pixel in all four images, while the orange vector shows the
  two intensity differences. Four fixed examples reproduce the source helper. Their
  mean is one hundred and squared modulation is two thousand five hundred. This is
  a helper demonstration, not recovered native-camera phase.
visual: Visit four audited axis, camera and pixel controls. Show their actual four
  intensities, difference vector and wrapped phase without claiming native preprocessing
  replay.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Curvature and thickness determine a lens section

```beat
id: geometry
scene: geometry
frames: 624
caption: Curvature and thickness determine a lens section
narration: The ray model has two refracting surfaces. The source uses spherical sag,
  with signed curvature equal to inverse radius. Center thickness separates the surface
  vertices. These sections are calculated directly from the initial and saved parameters,
  using equal millimeter scales and the supplied diameter. Switching between them
  does not reconstruct an optimization trajectory. The full fit also includes three
  origin coordinates and two tilts, which are not visible in this lens-local section.
  No ray tracing or new optical fit runs here.
visual: Show initial and saved analytical lens-local sections as discrete source states,
  preserving signed curvature, equal mm axes and thickness.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Read the saved images and all eight parameters

```beat
id: output
scene: output
frames: 576
caption: Read the saved images and all eight parameters
narration: The notebook retains initial and optimized modeled views for each camera.
  These are normalized source panels, not newly rendered predictions. The saved parameter
  file contains two curvatures, thickness, three origin coordinates and two tilts.
  Taking inverse curvature gives the two radii. All eight values describe the fit,
  but the custom evaluator compares only the radii and thickness. Apparent agreement
  in these rendered images cannot substitute for replaying the missing native measurements.
visual: Inspect initial and optimized source panels for each camera beside all eight
  saved values and the radius conversion.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal manufacturer dimensions with their limits

```beat
id: reference
scene: reference
frames: 672
caption: Reveal manufacturer dimensions with their limits
narration: 'The manufacturer dimensions appear halfway through this chapter. Purple
  dashed curves show their spherical section beside the green saved section. The radius
  errors are about six point nine six and one point four six percent; thickness error
  is about nine point four five percent. These are comparisons to a manufacturer specification,
  not independent metrology of this particular sample. No pose truth is supplied.
  This reveal is for the reader: the benchmark copies truth and the lens prescription
  into all three assistance packets.'
visual: Keep manufacturer values absent before midpoint. Then reveal equal-scale profiles
  and select all three dimension comparisons, with roles and solver visibility explicit.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## A good dimension score does not establish pose

```beat
id: scoring
scene: scoring
frames: 672
caption: A good dimension score does not establish pose
narration: 'The custom helper scores a three-number vector: two radii and thickness.
  A fixed control changes the origin to one thousand millimeters on every axis and
  both tilts to ninety degrees. Its scores remain identical to the saved output because
  pose is ignored. The active generic end-to-end scorer has a separate contract defect:
  it rejects even the correct three-number truth vector, while a scalar radius oracle
  has infinite range-normalized error. Saved metrics contain no pass thresholds. These
  controls establish evaluator limits, not model failure.'
visual: Compare saved and deliberately changed pose controls, then show the actual
  generic vector rejection and scalar infinite-normalization result.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## A recorded loss curve is not a fresh reconstruction

```beat
id: limits
scene: limits
frames: 624
caption: A recorded loss curve is not a fresh reconstruction
narration: This plot contains all twenty-one saved loss samples. Its moving marker
  is an inspection aid. The optimizer records pre-update mean squared masked residual
  components over the full grid. The separately saved forty-three point zero five
  micrometer metric is a mean valid-pixel display displacement, so the two summaries
  are not interchangeable. Native intersection maps are absent and that metric was
  not replayed. Source views and fixed controls support this explanation; they establish
  no fresh optical fit, agent capability, private-reference validity or current benchmark
  pass.
visual: Plot the complete recorded loss on a labeled logarithmic mm-squared axis,
  keeping the saved micrometer metric and raw-input limitations beside it.
channels:
  view:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```
