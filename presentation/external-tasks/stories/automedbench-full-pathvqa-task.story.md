---
schema: 2
id: automedbench-full-pathvqa-task
title: Separate short answer scoring from source training annotation
locale: en
purpose: "Explain PathVQA native train input, open-ended metrics and educational reference."
scope: "Public train example only; Full membership/private gold absent."
recipe: automed-pathvqa-v1
asset_pack: retained-automed-pathvqa-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-pathvqa-task.md
- presentation/external-tasks/sources/automedbench-full-pathvqa-task-resolution.json
- scripts/build_automed_pathvqa_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Full split absent · huggingface.co/datasets/flaviagiammarino/path-vqa"
narration: "Source train image and question available; source arrows retained, no new interpretation."
visual: "Native source input and separate training annotation; nonclinical metric mechanics."
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
narration: "Bind every referenced image, but helper currently selects first image; actual Full assembly unresolved."
visual: "Native source input and separate training annotation; nonclinical metric mechanics."
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
visual: "Native source input and separate training annotation; nonclinical metric mechanics."
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
visual: "Native source input and separate training annotation; nonclinical metric mechanics."
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
narration: "No public train annotation is copied into an answer submission."
visual: "Native source input and separate training annotation; nonclinical metric mechanics."
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
caption: "Public train annotation; no private gold"
narration: "Educational reveal only; source answer is not model evidence or independent pathology correctness."
visual: "Native source input and separate training annotation; nonclinical metric mechanics."
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
narration: "Source training membership cannot establish heldout clinical or model performance."
visual: "Native source input and separate training annotation; nonclinical metric mechanics."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
