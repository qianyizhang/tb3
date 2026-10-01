---
schema: 2
id: automedbench-full-brats-t1c-sr-task
title: Trace BraTS T1c geometry without inventing high-resolution MRI
locale: en
purpose: "Explain declared 2× geometry, Full assistance, output validity and private-evaluator boundaries."
scope: "Matching Full T1c case/private target absent; symbolic geometry and actual output empty."
recipe: automedbench-full-brats-t1c-sr-task-v1
asset_pack: retained-automedbench-full-brats-t1c-sr-task-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-brats-t1c-sr-task.md
- presentation/external-tasks/sources/automedbench-full-brats-t1c-sr-task-resolution.json
- scripts/build_automed_brats_t1c_sr_assets.py
---
# missing-full-t1c-pair

```beat
id: missing-full-t1c-pair
scene: input
frames: 168
caption: "Matching MRI / target absent · Official BraTS acquisition"
narration: "Full harness supplies no image cases; matching input, private target, degradation geometry and metric assets unresolved."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no MRI or high-resolution output."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# declared-twofold-grid

```beat
id: declared-twofold-grid
scene: operation
frames: 168
caption: "Keep public input and private target separate"
narration: "Declared bicubic 2× downsample is not an exact physical degradation pipeline; private target never acquired."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no MRI or high-resolution output."
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
visual: "Authored pixel geometry, source-pinned assistance/format rules; no MRI or high-resolution output."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# normalization-and-metric-assets

```beat
id: normalization-and-metric-assets
scene: operation
frames: 168
caption: "Expand geometry while leaving output values unknown"
narration: "Authored 2 × 2 to 4 × 4 cells illustrate 128 × 128 to 256 × 256 geometry; no bicubic result or restored information."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no MRI or high-resolution output."
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
visual: "Authored pixel geometry, source-pinned assistance/format rules; no MRI or high-resolution output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# late-public-evaluator-rules

```beat
id: late-public-evaluator-rules
scene: reference
frames: 168
caption: "Reveal evaluator rules without private image access"
narration: "Runner metrics, missing bands and effective fallback differ from named config; no private reference or score shown."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no MRI or high-resolution output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# unresolved-source-access-and-truth

```beat
id: unresolved-source-access-and-truth
scene: limits
frames: 168
caption: "Resolve native cases, degradation and metric assets"
narration: "No native MRI, fabricated high-resolution truth, clinical edge claim, model execution or measured metric."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no MRI or high-resolution output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
