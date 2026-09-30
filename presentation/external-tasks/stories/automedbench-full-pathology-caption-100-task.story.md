---
schema: 2
id: automedbench-full-pathology-caption-100-task
title: One image per case, then caption validity
locale: en
purpose: "Explain image-case selection, caption validity and the pathology scorer boundary."
scope: "Symbolic only; matching source data and Full references absent."
recipe: automed-pathology-caption-100-v1
asset_pack: retained-automed-pathology-caption-100-workflow-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-pathology-caption-100-task.md
- presentation/external-tasks/sources/automedbench-full-pathology-caption-100-task-resolution.json
- scripts/build_automed_pathology100_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Image/caption absent · huggingface.co/datasets/jamessyx/PathCap"
narration: "Symbolic image socket only; official PathCap acquisition route; historical anonymous annotation401 retained; original request timestamp unrecorded."
visual: "Task-specific symbolic image-case, validity and missing actual outputs."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# group

```beat
id: group
scene: operation
frames: 168
caption: "One image per case;100 selection absent"
narration: "One symbolic image socket belongs to one illustrative case. Actual100case IDs remain unstaged."
visual: "Task-specific symbolic image-case, validity and missing actual outputs."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# format

```beat
id: format
scene: operation
frames: 168
caption: "1–8000 chars; ≥1 letter; ASCII printable"
narration: "These are artifact checks, not factual or clinical report validation."
visual: "Task-specific symbolic image-case, validity and missing actual outputs."
channels:
  progress: [0.5, 0.5]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# metric

```beat
id: metric
scene: operation
frames: 168
caption: "Declared seven metrics; runtime defaults differ"
narration: "Seven-metric intent lacks backend/weights and pathology schema bindings. CXR regex defaults are not pathology validation."
visual: "Task-specific symbolic image-case, validity and missing actual outputs."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# output

```beat
id: output
scene: output
frames: 168
caption: "Nonclinical syntax fixture; actual report empty"
narration: "Only plain report.txt is submitted. The authored English fixture carries no patient findings."
visual: "Task-specific symbolic image-case, validity and missing actual outputs."
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
caption: "All requested image cases; invalid caption forces F"
narration: "Completion counts explicitly supplied case IDs;100 is not enforced here. Explicit reveal exposes mechanics, never private reports."
visual: "Task-specific symbolic image-case, validity and missing actual outputs."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# limits

```beat
id: limits
scene: limits
frames: 168
caption: "Source acquisition and metric assets unresolved"
narration: "No clinical performance, source report or Full case equivalence is established."
visual: "Task-specific symbolic image-case, validity and missing actual outputs."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
