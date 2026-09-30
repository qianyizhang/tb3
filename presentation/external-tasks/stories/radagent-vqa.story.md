---
schema: 2
id: radagent-vqa
title: Answer a RadAgent chest CT multiple-choice question
locale: en
purpose: "Select CT evidence scope and preserve the exact full option string."
scope: "Symbolic case/tool sockets and nonclinical format fixture; CT-RATE case and participant result absent."
recipe: radagent-vqa-v1
asset_pack: retained-radagent-vqa-contract-v2
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/radagent-vqa.md
- presentation/external-tasks/sources/radagent-vqa-resolution.json
- scripts/build_radagent_vqa_assets.py
---

# Case/CT absent · huggingface.co/datasets/ibrahimhamamci/CT-RATE

```beat
id: input
scene: input
frames: 168
caption: "Case/CT absent · huggingface.co/datasets/ibrahimhamamci/CT-RATE"
narration: "Matching CT and VQA case are absent. Request access through the official CT-RATE page. Source fields map question to task and CSV answer to separate host-side gt."
visual: "Task-specific symbolic data/tool/answer boundaries; linked missing-case warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Whole-volume tool evidence is model-derived

```beat
id: whole-volume
scene: operation
frames: 168
caption: "Whole-volume tool evidence is model-derived"
narration: "If the selected agent variant supplies whole-volume VQA, send the question and CT image path. Its response is model-derived evidence, not a reference answer. No response is retained."
visual: "Task-specific symbolic data/tool/answer boundaries; linked missing-case warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Selected slices are a narrower view

```beat
id: selected-slice
scene: operation
frames: 168
caption: "Selected slices are a narrower view"
narration: "Slice VQA accepts selected 2D image paths and a precise question. It can inspect several slices, not an entire volume. Selecting evidence does not establish whole-volume absence."
visual: "Task-specific symbolic data/tool/answer boundaries; linked missing-case warning remains visible."
channels:
  progress: [0.5, 0.5]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Compare scopes; preserve exact option wording

```beat
id: reconcile
scene: operation
frames: 168
caption: "Compare scopes; preserve exact option wording"
narration: "Use the question to select evidence and resolve tool disagreement. The available tool set varies by agent; V8minus removes whole-volume VQA and disease classification. All result sockets here remain empty."
visual: "Task-specific symbolic data/tool/answer boundaries; linked missing-case warning remains visible."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Full option string · actual answer empty

```beat
id: output
scene: output
frames: 168
caption: "Full option string · actual answer empty"
narration: "The final JSON action contains the full selected option text including its prefix. The token example is authored and nonclinical; it is not a patient answer or participant submission."
visual: "Task-specific symbolic data/tool/answer boundaries; linked missing-case warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Evaluator rules · no case gt revealed

```beat
id: reference
scene: reference
frames: 168
caption: "Evaluator rules · no case gt revealed"
narration: "The VQA reward branch compares stripped lowercase answers and adds BLEU-one and ROUGE-L when reward is enabled. Optional tool terms can augment total reward. Validation disables reward computation. No actual correctness or reward is shown."
visual: "Task-specific symbolic data/tool/answer boundaries; linked missing-case warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# Source contract is not a task run

```beat
id: limits
scene: limits
frames: 168
caption: "Source contract is not a task run"
narration: "CT-RATE access remains gated. CSV gt is not in initial model messages but host scenario retains it; runtime file isolation is unaudited. No CT, tool, model or NLP scorer was executed."
visual: "Task-specific symbolic data/tool/answer boundaries; linked missing-case warning remains visible."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
