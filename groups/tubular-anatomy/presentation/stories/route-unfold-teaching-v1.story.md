---
schema: 1
id: route-unfold-teaching-v1
title: From a curved route to a readable image
locale: en
purpose: Explain the operation, not a solver strategy or a patient result.
recipe: route-unfold-v1
asset_pack: tb3-route-kit-v1
fps: 24
reference_policy: no-reference-assets
source_class: procedural-teaching
---

# Route unfolding — canonical explainer script

This is the only authored copy-and-timing source for this pilot. Fenced `beat`
blocks are validated; generated JSON, captions, HTML and MP4 are outputs.
All visuals are an original synthetic branching phantom, not patient anatomy,
a CT image, a benchmark reference, or a reconstruction made by an agent.

## 01 · Establish the task

```beat
id: orient
duration: 5
caption: One branching volume. Two supplied endpoints.
visual: Hold the complete tree in one fixed view. Identify only the inlet and target. Keep the required output empty.
narration: >-
  Given this branching volume, build an image along the requested route.
context: [1, 1]
route: [0, 0]
ribbon: [0, 0]
cursor: [0, 0]
unfold: [0, 0]
output: [0, 0]
```

## 02 · Establish the route

```beat
id: trace
duration: 6
caption: Follow the connected route, not a straight shortcut.
visual: Trace the same connected centerline from the inlet through the junction to the target. Retain the side branches as context.
narration: >-
  Follow the connected path. A straight line between endpoints would cross empty space.
context: [1, 0.38]
route: [0, 1]
ribbon: [0, 0]
cursor: [0, 0]
unfold: [0, 0]
output: [0, 0]
```

## 03 · Explain what is sampled

```beat
id: sample
duration: 7
caption: Sample a narrow neighborhood along the route.
visual: Reveal a curved sampling ribbon. Move a cross-route sampling line along it; the right panel shows the corresponding scalar profile.
narration: >-
  Sample a transverse line at successive route positions. Keep its orientation consistent as the route bends.
context: [0.38, 0.25]
route: [1, 1]
ribbon: [0, 1]
cursor: [0, 1]
unfold: [0, 0]
output: [0, 0]
```

## 04 · Map into the output image

```beat
id: map
duration: 6
caption: Each sampled line becomes one image column.
visual: Keep the branching object fixed. Sweep the same sampling line again while revealing matching columns in the output. Link the source and destination cursors.
narration: >-
  Each sampled line becomes one image column. The tube itself does not straighten.
context: [0.25, 0.25]
route: [1, 1]
ribbon: [1, 1]
cursor: [0, 1]
unfold: [0, 1]
output: [0, 1]
```

## 05 · Make the output legible

```beat
id: inspect
duration: 5
caption: The output is sampled data, not a decorative diagram.
visual: Hold the completed image. Link a cursor on the synthetic narrowing to the identical position on the curved route. Do not invent a measurement or diagnosis.
narration: >-
  Both views show the same samples from our synthetic volume, not patient data.
context: [0.25, 0.25]
route: [1, 1]
ribbon: [1, 1]
cursor: [0.69, 0.69]
unfold: [1, 1]
output: [1, 1]
```

## 06 · State the boundary

```beat
id: boundary
duration: 4
caption: A clear explanation does not establish a correct solution.
visual: Keep input context and output visible. End on a readable still, with the synthetic-fixture boundary next to the output.
narration: >-
  The real task still needs its own source data and verification.
context: [0.25, 0.4]
route: [1, 1]
ribbon: [1, 0.3]
cursor: [0.69, 0.69]
unfold: [1, 1]
output: [1, 1]
```
