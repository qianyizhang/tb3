---
schema: 2
id: radagent
title: Assemble a chest CT report through specialist tools
locale: en
purpose: "Explain the pinned assemble a chest ct report through specialist tools task through its actual input, operation, output and reference boundaries."
scope: "Symbolic task contract, with no native patient image. No private reference, model answer or observed score."
recipe: radagent-report-v1
asset_pack: retained-radagent-interpretation-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/radagent.md
- presentation/external-tasks/sources/radagent-resolution.json
- scripts/build_interpretation_a_assets.py
---

# Start with the input

```beat
id: input
scene: input
frames: 288
caption: "Start with the input"
narration: "The pinned agent source defines a nine-item checklist and ten specialist tools. No native CT, saved tool result, generated report or matched reference report is retained. Initial view contains no answer or private reference."
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
narration: "The v8c prompt directs a report_generation_tool draft first, then checks across nine checklist areas using specialist tools and resolution of contradictions. No saved trace establishes an actual sequence."
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
narration: "The v8c prompt directs a report_generation_tool draft first, then checks across nine checklist areas using specialist tools and resolution of contradictions. No saved trace establishes an actual sequence."
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
narration: "final assistant JSON action with answer string; single-case CLI streams the interaction trace. Separate offline CT-RATE metrics include BLEU-1, ROUGE-L, CIDEr, GREEN and RadBERT-derived labels. Full-orchestrator learned reward is optional; minimal-batch reward 0.0 is placeholder metadata. No metric was run."
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
narration: "CT-RATE is gated; the audited source tree contains no worked NIfTI, tool trace or report. No report text or metric is invented."
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
narration: "CT-RATE is gated; the audited source tree contains no worked NIfTI, tool trace or report. No report text or metric is invented. No model, grader or learned metric was run."
visual: "Actual source scope and unresolved acquisition route."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
