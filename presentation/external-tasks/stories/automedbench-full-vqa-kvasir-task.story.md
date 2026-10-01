---
schema: 2
id: automedbench-full-vqa-kvasir-task
title: Separate short answer scoring from source raw annotation
locale: en
purpose: "Explain Kvasir-VQA native raw input, open-ended metrics and educational reference."
scope: "Public raw example only; Full membership/private gold absent."
recipe: automed-kvasir-v1
asset_pack: retained-automed-kvasir-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-vqa-kvasir-task.md
- presentation/external-tasks/sources/automedbench-full-vqa-kvasir-task-resolution.json
- scripts/build_automed_kvasir_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Full IDs absent · HF SimulaMet-HOST/Kvasir-VQA"
narration: "Official raw source frame/question; source border/text retained, category/answer covered."
visual: "Native source input and separate raw annotation; nonclinical metric mechanics."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# bind

```beat
id: bind
scene: operation
frames: 168
caption: "Question + image; short answer without A–E"
narration: "Bind every referenced image, but task-specific plan declares one endoscopy image per sample; actual Full assembly unresolved."
visual: "Native source input and separate raw annotation; nonclinical metric mechanics."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# metrics

```beat
id: metrics
scene: operation
frames: 168
caption: "Inspect lexical, strict-binary and judge branches"
narration: "Toy token examples teach implementation only, not native-image prediction."
visual: "Native source input and separate raw annotation; nonclinical metric mechanics."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# schema

```beat
id: schema
scene: operation
frames: 168
caption: "Six output keys; scorer and schema validity differ"
narration: "Require nonempty answer and backing rawmodel text. Actual values remain null."
visual: "Native source input and separate raw annotation; nonclinical metric mechanics."
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
caption: "Participant answer empty"
narration: "No public raw annotation is copied into an answer submission."
visual: "Native source input and separate raw annotation; nonclinical metric mechanics."
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
caption: "Public raw annotation; no private gold"
narration: "Educational reveal only; source answer is not model evidence or independent clinical correctness."
visual: "Native source input and separate raw annotation; nonclinical metric mechanics."
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
caption: "Split/calibration/judge dependencies unresolved"
narration: "Source raw membership cannot establish heldout clinical or model performance."
visual: "Native source input and separate raw annotation; nonclinical metric mechanics."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
