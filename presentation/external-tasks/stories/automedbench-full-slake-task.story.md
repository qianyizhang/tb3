---
schema: 2
id: automedbench-full-slake-task
title: "Connect SLAKE questions, short answers and scoring"
locale: en
purpose: "Explain native public train input and Full open-answer contract without a result."
scope: "Mixed upstream training example; exact Full case absent; educational annotation reader reveal only."
recipe: automed-slake-v1
asset_pack: retained-automed-slake-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-slake-task.md
- presentation/external-tasks/sources/automedbench-full-slake-task-resolution.json
- scripts/build_automed_slake_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full split absent · Official SLAKE"
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
  reference: [1, 1]
cut: intentional-cut
```

# Bind the question to its required images

```beat
id: bind
scene: operation
frames: 72
caption: "Bind the question to its required images"
narration: "The public training question and native image are given inputs; Full staging conversion remains unknown."
visual: "Source-specific contract step, no decode or output."
channels:
  progress: [0.0, 0.0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Preserve the declared prompt and raw text

```beat
id: prompt
scene: operation
frames: 72
caption: "Preserve the declared prompt and raw text"
narration: "Lite fixes the source method; Standard candidates are instructions, not measured comparisons or provisioned runtimes."
visual: "Source-specific contract step, no decode or output."
channels:
  progress: [0.3333333333333333, 0.3333333333333333]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Short phrase or exact yes/no

```beat
id: normalize
scene: operation
frames: 72
caption: "Short phrase or exact yes/no"
narration: "Open phrases are normalized; binary gold uses strict normalized yes/no. No five-word cap or answer is inferred."
visual: "Source-specific contract step, no decode or output."
channels:
  progress: [0.6666666666666666, 0.6666666666666666]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Write provenance with the answer record

```beat
id: write
scene: operation
frames: 72
caption: "Write provenance with the answer record"
narration: "Six expected fields require genuine execution evidence. This participant output stays empty."
visual: "Source-specific contract step, no decode or output."
channels:
  progress: [1.0, 1.0]
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
narration: "Heuristic uses strict binary match or half exact match and half token F1. Optional answer judge replaces primary accuracy. All evaluator-supplied IDs remain the denominator; discovery is the default; no score or clinical result is shown."
visual: "Own-colored limits chapter; native source input, empty output, no private reference."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
