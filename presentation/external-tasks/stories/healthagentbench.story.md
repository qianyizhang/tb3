---
schema: 2
id: healthagentbench
title: Decide requested findings on one chest CT
locale: en
purpose: "Explain the pinned decide requested findings on one chest ct task through its actual input, operation, output and reference boundaries."
scope: "Symbolic task contract, with no native patient image. No private reference, model answer or observed score."
recipe: healthagentbench-ct-findings-v1
asset_pack: retained-healthagentbench-interpretation-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/healthagentbench.md
- presentation/external-tasks/sources/healthagentbench-resolution.json
- scripts/build_interpretation_a_assets.py
---

# Start with the input

```beat
id: input
scene: input
frames: 288
caption: "Start with the input"
narration: "The exact valid_16_a_1 CT and paired CT-RATE report require access. The case-specific labels.txt list derived from that report is also unavailable. Initial view contains no answer or private reference."
visual: "Clearly empty input socket without patient content."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Inspect the available context

```beat
id: inspect
scene: inspect
frames: 336
caption: "Inspect the available context"
narration: "Requested names are derived from 17 report-phrase categories. Present-only or absent-only matches are retained; both or neither are omitted. These heuristic labels are not independent clinical adjudication."
visual: "Task-specific helper/tool or chronology layout without patient findings."
channels:
  cursor: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Apply the task operation

```beat
id: operation
scene: operation
frames: 336
caption: "Apply the task operation"
narration: "Inspect the CT for every supplied finding and write yes or no. Change the three hypothetical comparison outcomes to explore the matching rule. Any missing or mismatched answer prevents a pass. This is not a patient result."
visual: "Task-specific decision, tool, grid-coordinate or constrained-edit mechanism; no result claimed."
channels:
  cursor: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Write the required output

```beat
id: schema
scene: schema
frames: 300
caption: "Write the required output"
narration: "/workspace/submission/predictions.txt, one exact label: yes/no line per requested name. Reward 1 only when all retained report-derived gold labels have matching parseable binary predictions; one wrong or missing answer yields 0. This is label agreement, not independent clinical diagnosis."
visual: "Exact output schema shown as empty."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Separate evaluator material

```beat
id: reference
scene: reference
frames: 252
caption: "Separate evaluator material"
narration: "The exact CT, report, requested names, private gold and model prediction are missing. Unauthenticated HEAD returned HTTP 401 GatedRepo."
visual: "Reference-unavailable state; no hidden answer mounted."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Keep the source boundary visible

```beat
id: limits
scene: limits
frames: 288
caption: "Keep the source boundary visible"
narration: "The exact CT, report, requested names, private gold and model prediction are missing. Unauthenticated HEAD returned HTTP 401 GatedRepo. No model, grader or learned metric was run."
visual: "Actual source scope and unresolved acquisition route."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
