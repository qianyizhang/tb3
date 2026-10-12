---
schema: 2
id: br030-native-trace
title: Follow a coronary repair, route and source-linked curved view
locale: en
purpose: Explain recorded native CTA inspections and original saved mask, route,
  CPR and mesh with a separate frozen-result and author-intervention reveal.
scope: One retained BR-030 Terra/high development attempt with supplied mask,
  review region and route endpoints. Geometry checks do not establish clinical accuracy.
recipe: native-trace-v1
manifest: groups/tubular-anatomy/presentation/native-coronary-trace/native-trace.json
fps: 24
reference_policy: reader-reference-reveal
source_class: source-derived-teaching
source_locators:
- groups/tubular-anatomy/presentation/native-coronary-trace/canonical-mapping.md
- groups/tubular-anatomy/presentation/native-coronary-trace/README.md
- groups/tubular-anatomy/presentation/briefs/br030.md
- docs/evidence/br030-sources.json
- docs/evidence/br030-results.json
---

# Follow a coronary repair, route and source-linked curved view

Canonical migration candidate, pending source-pinned visual review. Seven discrete 168-frame holds,
24 fps, 1,176 frames / 49 seconds. Selected recorded operations and reader
navigation remain distinct; no hidden reasoning or continuous search is asserted.

## 1. Receive the crop and helpers

```beat
id: input
scene: input
frames: 168
caption: One native CTA crop, a supplied mask and explicit route helpers.
narration: >-
  The solver received the whole CTA crop, an unchanged predicted mask, an editable
  region and two route endpoints. Native indices map to RAS millimetres through
  the supplied affine. These helpers constrain repair and route selection;
  private reference annotations remain separate.
visual: Entire supplied crop with unmarked CT context, binary helper region and
  supplied RAS endpoints. Positive native axes L/A/S; excluded full-CTA regions hidden.
state: input
trace_steps: [7, 9, 10]
reference: false
```

## 2. Inspect local native planes

```beat
id: search
scene: search
frames: 168
caption: Three exact montages retain the observed local CT evidence.
narration: >-
  The solver inspected axial, coronal and sagittal planes around the review
  region. Red shows supplied mask; green tint shows editable pixels outside it.
  These are actual delivered observations. A missing montage command prompted a
  Pillow replacement before the three images were opened.
visual: Exact steps 17/18/19 PNGs, sequential native levels and half-open support
  bounds; original −200..500 HU window and 3× tile resize. No reference overlay.
state: search
trace_steps: [11, 12, 13, 14, 15, 16, 17, 18, 19]
reference: false
```

## 3. Compare connections and choose a ridge

```beat
id: contacts
scene: contacts
frames: 168
caption: Printed alternatives precede the eventual fourteen-point ridge.
narration: >-
  Component distances alone did not select the connection. The solver compared
  local intensities, skeleton endpoints and HU-weighted paths, then explicitly
  wrote a fourteen-point voxel ridge at step thirty-eight. This is its eventual
  chosen geometry, not an earlier detected trajectory or a reference path.
visual: Recorded alternatives from steps 20..36 plus actual step-38 bridge.
  Exact binary region governs edit permission; enclosing box is context only.
state: contacts
trace_steps: [20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 38]
reference: false
```

## 4. Save the repair and route

```beat
id: route
scene: route
frames: 168
caption: Original saved repair adds 103 voxels and preserves the surroundings.
narration: >-
  The saved method adds contrast-supported voxels near the chosen ridge, inside
  the editable region. It preserves all outside voxels, skeletonizes the repaired
  mask and follows a physical shortest path. The saved route has 371 RAS points
  and the exact requested endpoints.
visual: Original added/removed lists and original saved RAS route, tied to the
  whole supplied crop. No intermediate repair mask or annotation-based route substitution.
state: route
trace_steps: [38, 39, 40, 42]
reference: false
```

## 5. Link curved samples back to CT

```beat
id: cpr
scene: cpr
frames: 168
caption: Each saved CPR pixel has HU and a retained source position.
narration: >-
  Curved planar reformation, or CPR, samples planes along the saved route. Eight
  angles and sixty-five offsets retain each pixel’s CT intensity and source RAS
  coordinate. Reader controls follow these stored samples; this later visualization
  is not an image delivered to the solver.
visual: Original HU/source-coordinate arrays, angles 0..315 degrees, offsets
  −8..8 mm. Original saved arc metadata remains intact; native source link uses indices.
state: cpr
trace_steps: [38, 39, 40]
reference: false
```

## 6. Inspect the original complete package

```beat
id: output
scene: output
frames: 168
caption: Mask, route, curved samples and world-space surface stay linked.
narration: >-
  The fourth saved artifact is a complete world-space vessel mesh, including both
  coronary trees. The solver inspected closure, winding and mask preservation.
  These arrays and logged checks are saved evidence. The interactive reader is
  a later explanation, not an observed solver rendering session.
visual: Original mesh vertex/triangle order and four saved outputs. Full surface
  is preserved; no display simplification or independently adjudicated anatomy implied.
state: saved
trace_steps: [38, 39, 40, 41, 42]
reference: false
```

## 7. Reveal the frozen result and separate correction

```beat
id: reference
scene: reference
frames: 168
caption: Compare the saved package with frozen checks and a later intervention.
narration: >-
  Frozen repair, trace and mesh checks pass; CPR distance consistency fails.
  Original arc metadata exceeds saved-line distance by 8.891498 millimetres.
  A later author correction changes only that array and passes separately.
  It is not another model success or evidence of difficult clinical discrimination.
visual: Original reward 0/stages, old arc endpoint 184.809253 mm versus actual
  saved-line 175.917755 mm. Separate retained author intervention; source-related
  references and training-split limitations. Original saved state stays fixed.
state: saved
trace_steps: [39, 40, 42]
reference: true
```
