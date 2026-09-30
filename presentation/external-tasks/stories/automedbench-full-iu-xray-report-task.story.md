---
schema: 2
id: automedbench-full-iu-xray-report-task
title: One report per study, then strict text validation
locale: en
purpose: "Explain study grouping, text validity and the scorer boundary."
scope: "Symbolic only; matching source data and Full references absent."
recipe: automed-iu-xray-report-v1
asset_pack: retained-automed-full-iu-report-workflow-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-iu-xray-report-task.md
- presentation/external-tasks/sources/automedbench-full-iu-xray-report-task-resolution.json
- scripts/build_automed_iu_report_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Images/reports absent · openi.nlm.nih.gov/faq"
narration: "Symbolic study and image sockets only; acquire matching source through official Open-i."
visual: "Task-specific symbolic study, validity and missing actual outputs."
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
caption: "One study, one report; image count varies"
narration: "Two illustrative image sockets belong to one illustrative study, never two output reports."
visual: "Task-specific symbolic study, validity and missing actual outputs."
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
caption: "40–8000 chars; ≥20 letters; ASCII printable"
narration: "These are artifact checks, not factual or clinical report validation."
visual: "Task-specific symbolic study, validity and missing actual outputs."
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
narration: "Equal seven-component intent lacks MLRG backend and weights bindings; default lightweight scoring differs."
visual: "Task-specific symbolic study, validity and missing actual outputs."
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
visual: "Task-specific symbolic study, validity and missing actual outputs."
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
caption: "All requested studies; any invalid report forces F"
narration: "Completion counts studies. Explicit reveal exposes mechanics, never private reports."
visual: "Task-specific symbolic study, validity and missing actual outputs."
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
caption: "Source acquisition and metric assets unresolved"
narration: "No clinical performance, source report or Full case equivalence is established."
visual: "Task-specific symbolic study, validity and missing actual outputs."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
