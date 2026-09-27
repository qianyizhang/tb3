---
schema: 2
id: dental-original
title: 'Dental CBCT: separate geometry, identity and reference conventions'
locale: en
purpose: Explain the three original-contract dental attempts using unchanged native
  outputs, explicit private-reference reveals and diagnostic-only label permutation.
scope: Two cases · three completed attempts · selected native views · reference conventions under review.
recipe: dental-original-v1
asset_pack: retained-dental-original-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-dental-original.md
- groups/anatomy-audit/presentation/sources/dental-original-audit.json
- groups/anatomy-audit/findings/dental-ct-only-astra-medium.md
- groups/anatomy-audit/findings/dental-f018-effort-comparison.md
- groups/anatomy-audit/findings/dental-f002-astra-medium.md
- groups/anatomy-audit/findings/dental-trace-root-causes.md
- groups/anatomy-audit/findings/dental-dataset-contract-audit.md
- scripts/build_dental_original_assets.py
- scripts/audit_dental_original_evidence.py
---

# Original dental contract

## Full CT and all possible labels; no case inventory

```beat
id: inputs
scene: inputs
frames: 216
caption: Full CT and all possible labels; no case inventory
narration: The solver receives the complete F018 CBCT and the dataset-wide label dictionary.
  The unannotated native section here is a reader view. Seventy-seven sparse foreground
  IDs cover teeth, pulp, jaws, air spaces, canals and restorations. The dictionary
  does not reveal which classes occur in this patient. There are no masks, examples
  or evaluation scores.
visual: Actual F018 native j205 source image, untouched pixels under a fixed window;
  no contours.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
```

## Preserve the grid; one integer label at every voxel

```beat
id: contract
scene: contract
frames: 240
caption: Preserve the grid; one integer label at every voxel
narration: The answer is an integer segmentation on the exact input dimensions and
  affine, plus method notes. Unlike independent binary masks, this map assigns one
  class per voxel. The original package provides label names but omits the source-specific
  orientation convention. A later publisher audit warns that header direction is not
  physically accurate; this is reader context, not advice supplied to those original
  solvers.
visual: Retain unannotated CT and show sparse IDs, exclusive output and native-grid
  requirements.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Inspect, choose regions, construct masks, then compose labels

```beat
id: method
scene: method
frames: 240
caption: Inspect, choose regions, construct masks, then compose labels
narration: The retained scripts show image-guided classical processing. Agents select
  regions and landmarks, use thresholds and morphology, construct tooth envelopes,
  extract internal pulp, and trace canals or omit them. Xhigh additionally uses three-dimensional
  watershed. These are source-backed operations reconstructed from code and observable
  actions. The diagram is not a record of hidden reasoning or a new segmentation run.
visual: Actual CT beside a compact method flow; no private reference or scores.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Two independent outputs on identical F018 task bytes

```beat
id: output
scene: output
frames: 240
caption: Two independent outputs on identical F018 task bytes
narration: Astra medium and xhigh produce valid integer NIfTI outputs using the same
  frozen task. Here are their original tooth IDs at native k fifty-five. The contours
  and numeric labels come from saved answers. These are outputs, not supplied masks.
  Their native arrays and source headers are unchanged; the private reference has
  not yet been revealed.
visual: Two saved output panels, orange medium and cyan xhigh, original numeric IDs.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the private reference: location and identity separate

```beat
id: reference
scene: reference
frames: 288
caption: 'Reveal the private reference: location and identity separate'
narration: The private research labels now appear in a separate panel. At essentially
  the same native tooth positions, the agent and reference assign opposing side IDs.
  For example, eleven and twenty-one occupy opposite named positions. This is not
  a mirrored array. The original agents followed the supplied affine; source orientation
  and clinical laterality require adjudication before this discrepancy can be treated
  as a clean anatomical-identity failure.
visual: Keep saved xhigh panel fixed and reveal green dashed reference with independently
  readable numeric IDs.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Swap displayed IDs while keeping every contour fixed

```beat
id: diagnostic
scene: diagnostic
frames: 336
caption: Swap displayed IDs while keeping every contour fixed
narration: The middle panel applies one fixed side-ID permutation after completion.
  Watch eleven and twenty-one change names without any contour moving. The same diagnostic
  also pairs corresponding teeth, pulps, sinuses and canals. It never changes saved
  outputs or becomes an accepted correction. The private reference is separate. Geometry
  agreement under renamed IDs cannot settle which clinical side is correct.
visual: 'Three panels: original xhigh, same geometry with thresholded ID permutation,
  and private reference; highlight 11 and21.'
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
  diagnostic:
  - 0
  - 1
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Original scores and diagnostics have different denominators

```beat
id: metrics
scene: metrics
frames: 336
caption: Original scores and diagnostics have different denominators
narration: The frozen custom macro equally averages classes present in either prediction
  or reference. Both-empty classes are excluded. Fixed relabeling changes the active
  inventory from seventy to sixty-eight for F018, and sixty-two to fifty-seven for
  F002. Its improvement is not a causal percentage of error. Foreground Dice ignores
  all semantic IDs and is dominated by large structures. Preserve every original score.
visual: Three retained attempts with original macro, diagnostic macro, active-class
  denominators and foreground overlap.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Pool canal sides; residual spatial errors remain

```beat
id: canals
scene: canals
frames: 336
caption: Pool canal sides; residual spatial errors remain
narration: These are two actual native sections through the F018 main canals. Both
  side IDs are pooled, so identity disagreement cannot explain the remaining offsets.
  Medium is orange, xhigh cyan and private research reference green dashed. The player
  cuts between native j one hundred forty-five and two hundred five. Selected cross-sections
  illustrate residual geometry; they do not adjudicate all clinical boundaries.
visual: Two output panels with separate-color pooled reference outlines; discrete
  native plane selection.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## A separate case: F002 restoration and tooth disagreement

```beat
id: restorations
scene: restorations
frames: 288
caption: 'A separate case: F002 restoration and tooth disagreement'
narration: F002 is a different source case, with its own original medium attempt.
  The native k one hundred twenty-five view shows saved restoration and tooth IDs
  beside the private reference. Eight means bridge, nine crown and ten implant. The
  output assigns bridge voxels where the reference has no bridge label. Bare names
  do not fully specify mixed-restoration conventions, and this comparison is not a
  clinical subtype adjudication or a case-difficulty ranking.
visual: Explicit case cut to actual F002 image and separate original-ID output/reference
  panels.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Locate pulp loss at a saved decision gate

```beat
id: pulp
scene: pulp
frames: 480
caption: Locate pulp loss at a saved decision gate
narration: The selected F002 example side-pairs saved tooth twenty-six with reference
  tooth sixteen for a reviewer diagnostic. Purple shows the saved envelope, reconstructed
  distance gate, intensity gate, slice gate, then submitted pulp. Of eight hundred
  forty-four reference voxels surviving the distance gate, only one survives the intensity
  cutoff. The final overlap is zero. These are full tooth-region counts, not this
  slice alone. Reference retention does not measure precision or prove that raising
  the cutoff is a safe repair.
visual: Actual native i289 source pixels; five discrete gate contours, green dashed
  reference and full-ROI overlap counts; no contour morphing.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 1
cut: intentional-cut
```

## An ID swap cannot recover omitted canals

```beat
id: omissions
scene: omissions
frames: 288
caption: An ID swap cannot recover omitted canals
narration: The F002 output contains no voxels for any of the five canal IDs, while
  the reference contains all five. Whole-volume occupancy establishes this omission;
  the displayed native section crosses only the two main canals. The original agent
  explicitly abstained where it could not resolve continuous boundaries. A label permutation
  cannot recover absent geometry. Reference semantics and method limitations remain
  separate questions.
visual: F002 native j145 with private canal outlines and five full-volume occupancy
  rows.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```

## Three completed attempts; keep attribution bounded

```beat
id: limits
scene: limits
frames: 264
caption: Three completed attempts; keep attribution bounded
narration: This explanation covers two source cases and three completed segmentation
  attempts. An authentication-only invocation is infrastructure evidence, and four
  oracle or no-op executions are controls. Native source arrays, outputs and original
  scores remain unchanged. The eight teaching views are selected after submission,
  not exhaustive clinical review. No new model ran. Later contracts and annotated
  examples belong to separate catalogue entries.
visual: Bounded evidence inventory and unresolved reference conventions; no clinical
  or population claim.
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
  diagnostic:
  - 0
  - 0
  gate:
  - 0
  - 0
cut: intentional-cut
```
