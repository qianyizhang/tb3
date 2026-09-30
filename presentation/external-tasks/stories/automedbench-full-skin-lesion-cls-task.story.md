---
schema: 2
id: automedbench-full-skin-lesion-cls-task
title: Remap seven dermoscopy checkpoint classes to output labels
locale: en
purpose: "Explain native source input, fixed checkpoint remapping and macro recall."
scope: "Public HAM10000 example; Full cases, clinical judgement and model output absent."
recipe: automed-skin-lesion-cls-v1
asset_pack: retained-automed-full-skin-lesion-source-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-skin-lesion-cls-task.md
- presentation/external-tasks/sources/automedbench-full-skin-lesion-cls-task-resolution.json
- scripts/build_automed_skin_lesion_assets.py
---
# input

```beat
id: input
scene: input
frames: 168
caption: "Full cases absent · api.isic-archive.com/collections/212"
narration: "One HAM10000 source-delivered image is available under CC BY-NC terms. It is not a Full test case or model result."
visual: "Native public source example; explicitly empty actual test/output fields."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# processor

```beat
id: processor
scene: operation
frames: 168
caption: "Source RGB to prescribed processor; tensor absent"
narration: "Pinned processor settings resize224 square, rescale1/255 and normalize mean/std point5. No processor or model was run."
visual: "Native public source example; explicitly empty actual test/output fields."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# mapping

```beat
id: mapping
scene: operation
frames: 168
caption: "Select source class index; no predicted index"
narration: "Checkpoint abbreviations must be remapped to canonical target strings; selection demonstrates taxonomy only."
visual: "Native public source example; explicitly empty actual test/output fields."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# files

```beat
id: files
scene: operation
frames: 168
caption: "One canonical class per case file"
narration: "CSV or per-case JSON. Unmapped abbreviations fail format; actual prediction remains absent."
visual: "Native public source example; explicitly empty actual test/output fields."
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
caption: "Output schema only; no native-image prediction"
narration: "A labeled toy string teaches syntax and is unrelated to the displayed source image."
visual: "Native public source example; explicitly empty actual test/output fields."
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
caption: "Mean recall over represented true classes"
narration: "Absent GT classes are omitted from macro recall. Missing predictions are wrong. No private reference or score is revealed."
visual: "Native public source example; explicitly empty actual test/output fields."
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
caption: "Split, overlap, prompt assembly and outputs unresolved"
narration: "This preparation does not diagnose lesions or establish classifier performance; received-size mismatch remains retained."
visual: "Native public source example; explicitly empty actual test/output fields."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
