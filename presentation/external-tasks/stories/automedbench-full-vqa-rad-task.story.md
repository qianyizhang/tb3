---
schema: 2
id: automedbench-full-vqa-rad-task
title: "Connect VQA-RAD questions, short answers and scoring"
locale: en
purpose: "Explain native public train input and Full open-answer contract without a result."
scope: "Mixed upstream training example; exact Full case absent; educational annotation reader reveal only."
recipe: automed-vqa-rad-v1
asset_pack: retained-automed-vqa-rad-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-vqa-rad-task.md
- presentation/external-tasks/sources/automedbench-full-vqa-rad-task-resolution.json
- scripts/build_automed_vqa_rad_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full absent \u00b7 osf.io/89kps/"
narration: "Inspect the native public training image and exact English source question. Full membership and physical acquisition geometry are unverified."
visual: "Own-colored input chapter; native source input, empty output, no private reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Reveal the public training annotation deliberately"
narration: "Public source annotation is initially hidden, explicitly labeled and reset on scene exit or backward replay. It is not private Full gold or a generated answer."
visual: "Own-colored helper chapter; native source input, empty output, no private reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Normalize a phrase or exact yes/no"
narration: "Lite fixes LLaVA-Med; Standard supplies candidates. Source S4 permits longer short phrases and warns against a five-word cap. Public calibration15 versus verifier10 is an assistance boundary."
visual: "Own-colored operation chapter; native source input, empty output, no private reference."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 288
caption: "Six fields remain unset"
narration: "One answer record per question requires nonempty short text, raw model output, model identity and runtime. Open mode ignores predicted_label; all teaching values remain null."
visual: "Own-colored output chapter; native source input, empty output, no private reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "Question means and optional judge are distinct"
narration: "Heuristic uses strict binary match or half exact match and half token F1. Optional answer judge replaces primary accuracy. All evaluator-supplied question IDs remain the main denominator; no score or clinical result is shown."
visual: "Own-colored limits chapter; native source input, empty output, no private reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
