---
schema: 2
id: automedbench-full-chest-xray-pneumonia-cls-task
title: Classify pediatric chest radiographs with canonical labels
locale: en
purpose: "Explain public training versus private evaluation and two-class output."
scope: "One native training example; frozen Full test cases and outputs absent."
recipe: automed-pneumonia-cls-v1
asset_pack: retained-automed-full-pneumonia-source-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-chest-xray-pneumonia-cls-task.md
- presentation/external-tasks/sources/automedbench-full-chest-xray-pneumonia-cls-task-resolution.json
- scripts/build_automed_pneumonia_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Full test absent · Official Mendeley acquisition"
narration: "One official public training radiograph is available. Its folder label is helper information, not a model response or Full test reference."
visual: "Native public training helper and explicit empty test/output sockets."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# operation-1

```beat
id: operation-1
scene: operation
frames: 168
caption: "Record training-only preprocessing"
narration: "Choose grayscale/channel preprocessing and training-derived validation; exclude frozen evaluation IDs."
visual: "Native public training helper and explicit empty test/output sockets."
channels:
  progress: [0.0, 0.0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# operation-2

```beat
id: operation-2
scene: operation
frames: 168
caption: "Fix class index to canonical string"
narration: "Lite class order is normal then pneumonia; record mapping with checkpoint. No trained model is retained."
visual: "Native public training helper and explicit empty test/output sockets."
channels:
  progress: [0.5, 0.5]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# operation-3

```beat
id: operation-3
scene: operation
frames: 168
caption: "Infer all staged cases and write labels"
narration: "Emit one label per ID. Actual prediction fields remain empty; generic stage prompt conflict must be resolved before execution."
visual: "Native public training helper and explicit empty test/output sockets."
channels:
  progress: [1.0, 1.0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# output

```beat
id: output
scene: output
frames: 168
caption: "CSV or per-case JSON · prediction absent"
narration: "The toy row demonstrates file syntax only and is not tied to the displayed native image."
visual: "Native public training helper and explicit empty test/output sockets."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reference

```beat
id: reference
scene: reference
frames: 168
caption: "Reveal training annotation and evaluator boundaries"
narration: "Missing outputs remain in the denominator; partial format validity is distinct from completeness. No private case label or measured score is revealed."
visual: "Native public training helper and explicit empty test/output sockets."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# limits

```beat
id: limits
scene: limits
frames: 168
caption: "One training example cannot establish clinical performance"
narration: "Frozen100 split, private references, test predictions, checkpoints and effective stage prompt assembly are absent."
visual: "Native public training helper and explicit empty test/output sockets."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
