---
schema: 2
id: br026-native-trace
title: Repair one MRA route while preserving the whole network
locale: en
purpose: Explain consequential recorded operations and native spatial context from
  one retained task-solving trace.
scope: Retained BR-026 V01 calibration run on a real MRA crop with a synthetic 200-voxel
  mask deletion. It does not demonstrate naturally occurring segmentation error repair.
recipe: native-trace-v1
manifest: groups/tubular-anatomy/presentation/anatomy-repair/native-trace.json
fps: 24
reference_policy: reader-reference-reveal
source_class: source-derived-teaching
source_locators:
- groups/tubular-anatomy/findings/br026-gap-trace.md
- groups/tubular-anatomy/presentation/briefs/tb3-vessel-connection-repair.md
---

# Repair one MRA route while preserving the whole network

Native-trace renderer migration. The original operation story and its acceptance receipt remain preserved; this condition has a separate renderer regression review.

## 1. Receive the mask

```beat
id: input
scene: input
frames: 144
caption: Almost perfect overlap can still hide a broken route.
narration: The solver received a real MRA crop, a proposed binary vessel mask and
  a broad editable region. It could repair a supported defect or return the mask unchanged.
  The location of the authored deletion was not supplied.
visual: 'Given: MRA + proposed mask + editable region → return: one corrected mask
  on the same grid.'
state: null
trace_steps:
- 7
- 9
reference: false
```

## 2. Find missing signal

```beat
id: search
scene: search
frames: 144
caption: Look for bright structure that the mask does not contain.
narration: After inspecting projections and slice montages, the solver measured bright,
  unmasked components. It reviewed six large candidates and their spatial relation
  to the mask. The component near (66, 76, 15) became the repair candidate.
visual: Brightness suggests candidates. The three-dimensional attachments determine
  whether a candidate bridges a local gap.
state: '250'
trace_steps:
- 12
- 14
- 17
- 18
- 20
- 21
- 23
- 25
- 26
reference: false
```

## 3. Grow the candidate

```beat
id: threshold
scene: threshold
frames: 192
caption: Follow one connected component as its threshold changes.
narration: The solver kept the same seed and tested nine intensity thresholds. At
  250, the component contains 89 voxels; at 165 it contains 198. Move the control
  below to reproduce those recorded alternatives.
visual: candidate = connected component at the seed of (image ≥ threshold) AND NOT
  mask AND editable region
state: '250'
trace_steps:
- 28
reference: false
```

## 4. Check both ends

```beat
id: contacts
scene: contacts
frames: 144
caption: A bridge needs two local attachments.
narration: 'At threshold 165, the solver checked which candidate voxels touched the
  original mask. They form two separated patches: 32 voxels at one end and 33 at the
  other. The amber cubes mark those exact contact voxels.'
visual: These are candidate-to-mask contacts in 3D, using 26-neighbor adjacency—not
  intersections in a projection.
state: '165'
trace_steps:
- 29
reference: false
```

## 5. Save a bounded edit

```beat
id: output
scene: output
frames: 144
caption: Add this component. Preserve everything else.
narration: The saved answer is the original mask union the selected 198-voxel component.
  The solver checked binary values, unchanged voxels outside the editable region,
  and the output’s shape and affine after reloading the NIfTI.
visual: The teal region is now the actual saved output minus the original mask. No
  original foreground was removed.
state: '165'
trace_steps:
- 31
reference: false
```

## 6. Reveal the check

```beat
id: reference
scene: reference
frames: 144
caption: Compare the saved repair with the private reference.
narration: The private reference reveals a 200-voxel authored gap in the right posterior
  communicating artery. The saved answer recovers 198, restores the tested local route
  and preserves the surrounding mask. Two missed boundary voxels appear in magenta.
visual: All frozen checks pass. Exact reference replication was not required; local
  geometry and preservation were.
state: '165'
trace_steps:
- 31
reference: true
```
