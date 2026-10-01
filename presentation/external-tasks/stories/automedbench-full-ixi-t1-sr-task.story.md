---
schema: 2
id: automedbench-full-ixi-t1-sr-task
title: Trace IXI T1 geometry without inventing high-resolution MRI
locale: en
purpose: "Explain declared 2× geometry, Full assistance, output validity and private-evaluator boundaries."
scope: "Matching Full T1 case/private target absent; symbolic geometry and actual output empty."
recipe: automedbench-full-ixi-t1-sr-task-v1
asset_pack: retained-automedbench-full-ixi-t1-sr-task-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-ixi-t1-sr-task.md
- presentation/external-tasks/sources/automedbench-full-ixi-t1-sr-task-resolution.json
- scripts/build_automed_ixi_t1_sr_assets.py
---
# missing-full-t1-pair

```beat
id: missing-full-t1-pair
scene: input
frames: 168
caption: "Full input / target missing · brain-development.org/ixi-dataset/"
narration: "One upstream T1 volume is retained separately; matching Full case, slice, normalized degradation and private target remain unresolved."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no matching Full MRI or high-resolution output; upstream example only late."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# public-input-private-target-boundary

```beat
id: public-input-private-target-boundary
scene: operation
frames: 168
caption: "Keep public input and private target separate"
narration: "Declared bicubic 2× downsample is not an exact physical degradation pipeline; private target never acquired."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no matching Full MRI or high-resolution output; upstream example only late."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# assistance-and-format-branches

```beat
id: assistance-and-format-branches
scene: operation
frames: 168
caption: "Compare Full Lite, Standard and format boundary"
narration: "Assistance controls prescribe or compare methods; checker validity remains weaker than task output requirements."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no matching Full MRI or high-resolution output; upstream example only late."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# twofold-array-grid-contract

```beat
id: twofold-array-grid-contract
scene: operation
frames: 168
caption: "Expand geometry while leaving output values unknown"
narration: "Authored 2 × 2 to 4 × 4 cells illustrate 128 × 128 to 256 × 256 geometry; no bicubic result or restored information."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no matching Full MRI or high-resolution output; upstream example only late."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# unsubmitted-high-grid

```beat
id: unsubmitted-high-grid
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no matching Full MRI or high-resolution output; upstream example only late."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# late-upstream-reader-helper

```beat
id: late-upstream-reader-helper
scene: reference
frames: 168
caption: "Reveal upstream helper, never Full private target"
narration: "Explicit late reveal shows a native stride-sampled IXI T1 source example, reader-only and has no established Full input or target mapping; evaluator rules are not a measured score."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no matching Full MRI or high-resolution output; upstream example only late."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# unresolved-full-mapping-and-metrics

```beat
id: unresolved-full-mapping-and-metrics
scene: limits
frames: 168
caption: "Resolve native cases, degradation and metric assets"
narration: "One upstream MRI example cannot establish selected Full cases, private high-resolution truth, an SR result or measured performance."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no matching Full MRI or high-resolution output; upstream example only late."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
