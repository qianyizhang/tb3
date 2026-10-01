---
schema: 2
id: automedbench-full-nih-cxr-sr-task
title: Trace NIH CXR geometry without inventing high-resolution chest X-ray
locale: en
purpose: "Explain declared 2× geometry, Full assistance, output validity and private-evaluator boundaries."
scope: "Matching Full chest X-ray case/private target absent; symbolic geometry and actual output empty."
recipe: automedbench-full-nih-cxr-sr-task-v1
asset_pack: retained-automedbench-full-nih-cxr-sr-task-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-nih-cxr-sr-task.md
- presentation/external-tasks/sources/automedbench-full-nih-cxr-sr-task-resolution.json
- scripts/build_automed_nih_cxr_sr_assets.py
---
# missing-full-cxr-pair

```beat
id: missing-full-cxr-pair
scene: input
frames: 168
caption: "Full pair absent · Official NIH acquisition"
narration: "Full harness supplies no image cases; matching input, private target, degradation geometry and metric assets unresolved."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no chest X-ray or high-resolution output."
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
visual: "Authored pixel geometry, source-pinned assistance/format rules; no chest X-ray or high-resolution output."
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
visual: "Authored pixel geometry, source-pinned assistance/format rules; no chest X-ray or high-resolution output."
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
visual: "Authored pixel geometry, source-pinned assistance/format rules; no chest X-ray or high-resolution output."
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
narration: "No enhanced.npy is supplied; symbolic sockets do not establish a method outcome."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no chest X-ray or high-resolution output."
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
caption: "Reader may reveal public evaluator rules; private target absent"
narration: "Explicit reader button reveals public source rules only. Runner metrics, missing bands and fallback differ from config; no private reference or score shown."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no chest X-ray or high-resolution output."
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
narration: "No acquired NIH chest radiograph, private target, SR result, device/anatomy preservation claim or measured metric."
visual: "Authored pixel geometry, source-pinned assistance/format rules; no chest X-ray or high-resolution output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
