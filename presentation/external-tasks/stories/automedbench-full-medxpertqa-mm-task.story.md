---
schema: 2
id: automedbench-full-medxpertqa-mm-task
title: Bind the visual question to exact option text
locale: en
purpose: "Explain native dev input, option mapping and educational reference visibility."
scope: "Public dev example only; Full membership and private gold absent."
recipe: automed-medxpert-mm-v1
asset_pack: retained-automed-medxpert-mm-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-medxpertqa-mm-task.md
- presentation/external-tasks/sources/automedbench-full-medxpertqa-mm-task-resolution.json
- scripts/build_automed_medxpert_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Full split absent · Official MedXpertQA"
narration: "Public dev question and its linked native image are source examples only; private Full gold absent."
visual: "Native public dev input, exact option mapping and separate educational reference."
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
caption: "One question; bind all referenced images"
narration: "This public source question has one image. Lite helper uses first image; general all-image handling unresolved."
visual: "Native public dev input, exact option mapping and separate educational reference."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# options

```beat
id: options
scene: operation
frames: 168
caption: "Select option mapping; no inference"
narration: "Letter selection only demonstrates exact source option text and does not claim clinical answer."
visual: "Native public dev input, exact option mapping and separate educational reference."
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
caption: "Letter scorer versus complete output schema"
narration: "All six output keys matter; scorer validity and checker validity differ."
visual: "Native public dev input, exact option mapping and separate educational reference."
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
caption: "Participant output empty"
narration: "No decoded letter, raw model text, runtime or checkpoint result is invented."
visual: "Native public dev input, exact option mapping and separate educational reference."
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
caption: "Public dev annotation; private gold absent"
narration: "Educational label reveal only, not a clinical recommendation or model result. Reset covers it."
visual: "Native public dev input, exact option mapping and separate educational reference."
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
caption: "Selection, calibration isolation and output unresolved"
narration: "Source dev label does not establish Full performance or independent clinical correctness."
visual: "Native public dev input, exact option mapping and separate educational reference."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
