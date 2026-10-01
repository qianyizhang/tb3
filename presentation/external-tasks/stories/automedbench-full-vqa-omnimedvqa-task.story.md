---
schema: 2
id: automedbench-full-vqa-omnimedvqa-task
title: Bind four-option questions without inventing image evidence
locale: en
purpose: "Explain OmniMedVQA source QA, missing image and four-option label and educational reference."
scope: "Public README QA only; matching image, Full membership and private gold absent."
recipe: automed-omni-v1
asset_pack: retained-automed-omni-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-vqa-omnimedvqa-task.md
- presentation/external-tasks/sources/automedbench-full-vqa-omnimedvqa-task-resolution.json
- scripts/build_automed_omni_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Image/Full split absent · Official OmniMedVQA"
narration: "Source README question/options; referenced image missing and answer covered."
visual: "Source QA/options and missing image socket; authored parser controls."
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
caption: "Question +image +A–D option map"
narration: "Bind every referenced image, but authorized source modalities differ; actual image/staging absent."
visual: "Source QA/options and missing image socket; authored parser controls."
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
caption: "Inspect parser, allowed labels and schema"
narration: "Authored raw strings teach parser rules only, not model decodes."
visual: "Source QA/options and missing image socket; authored parser controls."
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
narration: "Require nonempty answer and backing raw model text. Actual values remain null."
visual: "Source QA/options and missing image socket; authored parser controls."
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
narration: "No public README annotation is copied into an answer submission."
visual: "Source QA/options and missing image socket; authored parser controls."
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
caption: "Public source README annotation; no private gold"
narration: "Educational reveal only; source answer is not model evidence or clinical correctness."
visual: "Source QA/options and missing image socket; authored parser controls."
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
caption: "Image/source authorization/Full boundaries unresolved"
narration: "A public README QA item cannot establish Full membership, heldout clinical or model performance."
visual: "Source QA/options and missing image socket; authored parser controls."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
