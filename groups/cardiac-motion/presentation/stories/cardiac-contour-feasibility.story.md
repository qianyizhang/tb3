---
schema: 2
id: cardiac-contour-feasibility
title: 'Supplied contours to changing cavity'
locale: en
purpose: Explain the one-patient BR-025 author feasibility study from supplied all-phase contours to saved 3D cavity estimates and separate shape, volume and EF judgments.
scope: Local noncommercial teaching from pinned Patient001 source and saved author outputs; no model attempt or independent 3D truth.
recipe: cardiac-contour-v1
asset_pack: retained-cardiac-contour-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/cardiac-motion/presentation/briefs/tb3-cardiac-contour-feasibility.md
- groups/cardiac-motion/presentation/sources/cardiac-contour-audit.json
- groups/cardiac-motion/presentation/sources/cardiac-contour-resolution.json
- docs/evidence/br025-pilot-results.json
- presentation/task-explorer/cardiac-contour/manifest.json
---

# A contour on each phase is substantial help

## See the native radial input

```beat
id: inputs
scene: inputs
frames: 168
caption: Native ultrasound and supplied cavity contour
narration: Patient zero zero one has thirty source frames. The author baseline receives a clean cavity mask on plane one at every frame, while the ultrasound image provides context and does not drive its saved fit. This is one patient, not thirty independent cases.
visual: Play native plane-one image and supplied label-127 cavity outline through all thirty frames; keep plane-eight source mask hidden.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [0, 0]
  reference: [0, 0]
```

## Increase the supplied directions

```beat
id: views
scene: views
frames: 168
caption: One, four or eight clean views per phase
narration: The four-view condition supplies source cavity contours on radial planes one, ten, nineteen and twenty-eight at every phase. One- and eight-view conditions use nested sparse choices. Boundaries are already identified; the author reconstruction still has to complete unobserved directions and depth.
visual: Show four native source image planes with their supplied outlines for the current frame. Number each native plane.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Complete the unobserved cavity

```beat
id: reconstruct
scene: reconstruct
frames: 192
caption: Interpolate a saved cavity, frame by frame
narration: The retained CPU author baseline samples each supplied boundary in sixty-five polar directions, interpolates radii onto seventy-two azimuths, then closes the poles. It fits all thirty frames independently. The cyan surface is a display sample of the saved four-view cavity in a fixed millimeter camera. Its unseen geometry depends on this interpolation prior.
visual: Show native plane-one radial samples, the interpolation step and a fixed-camera display sample of the saved four-view cavity. Keep evaluator contours hidden.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Reveal a withheld source section

```beat
id: withheld
scene: withheld
frames: 192
caption: Compare on an unsupplied direction
narration: Plane eight is one of eight common evaluation directions disjoint from every sparse input set. Reveal its gold source cavity boundary only for the reader. The four-view projected boundary is close but imperfect; this displayed direction is one selected example from two hundred forty frame-plane pairs per sparse condition.
visual: Hold or move through native plane-eight frames with cyan saved projection and solid gold reader reference. Keep source and output coordinates fixed.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 1]
cut: intentional-cut
```

## Separate shape, volume and EF

```beat
id: curves
scene: curves
frames: 192
caption: Similar EF can conceal volume error
narration: In the one-view condition, mean withheld Dice is zero point eight seven four, yet volume mean absolute percentage error is thirty-one point one zero percent against the annotation-derived dense reconstruction. Its ejection-fraction difference is only two point six eight percentage points. Four and eight supplied views improve these author comparisons, but the dense curve includes evaluation planes and is source fit, not independent clinical truth.
visual: Synchronize original thirty-frame one, four and eight-view volume curves and native images. Reveal dense source-fit curve and separate scores only in this reader comparison.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [1, 1]
  reference: [1, 1]
cut: intentional-cut
```

## An observed plane cannot determine depth

```beat
id: depth
scene: depth
frames: 168
caption: A matching plane leaves 3D depth uncertain
narration: A retained control scales unobserved depth while preserving its single observed plane exactly. Derived ejection fraction changes from sixty-six point four seven to seventy-nine point eight eight percent, a thirteen point four one percentage-point difference. This counterexample does not validate either three-dimensional anatomy.
visual: Animate the same observed plane beside saved one-view surface samples and their exact retained z-scale control. The fixed camera preserves the identical z=0 plane.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Keep the study's boundaries visible

```beat
id: limits
scene: limits
frames: 192
caption: One patient, author baseline, no clinical oracle
narration: This is a single-patient author feasibility study with no model attempt. Source masks combine expert endpoint annotation and reviewed propagation. Five-degree radial poses and the ejection-fraction frame-index interpretation are pilot assumptions. Shared mesh vertex IDs do not establish myocardial material motion or strain. No clinical diagnosis, valves or flow were tested.
visual: Return to the actual supplied and withheld views with saved curve, reader-revealed reference and the one-patient denominator. Display the source-fit and pose limits beside the scores.
channels:
  phase: [0.5517241379310345, 0.5517241379310345]
  helper: [1, 1]
  output: [1, 1]
  reference: [1, 1]
cut: intentional-cut
```
