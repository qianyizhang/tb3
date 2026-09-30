---
schema: 2
id: automedbench-full-crc-histology-cls-task
title: "Classify colorectal histology source categories"
locale: en
purpose: "Explain native training patch, tissue annotation and Full classification contract."
scope: "One official public training patch; Full IDs/private labels/checkpoint/results absent; symbolic operation/output."
recipe: automed-crc-cls-v1
asset_pack: retained-automed-crc-cls-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-crc-histology-cls-task.md
- presentation/external-tasks/sources/automedbench-full-crc-histology-cls-task-resolution.json
- scripts/build_automed_crc_cls_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full test absent · zenodo.org/records/1214456"
narration: "One official public training patch is shown at its native 224 pixel grid. The source reports half a micrometer per pixel and color normalization. No Full evaluation case is identified, no coordinates or patient diagnosis inferred. Obtain further assets through the linked official record."
visual: "Dedicated input panel with native public training patch or absent contract values; no invented result."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Nine categories; reveal public annotation"
narration: "Inspect the tissue taxonomy independently of model outputs. Reveal the retained public training-folder annotation explicitly; it supplies training help, not Full test truth or a prediction. The NONORM archive does not provide exact counterparts for all normalized patches."
visual: "Dedicated helper panel with native public training patch or absent contract values; no invented result."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Train within the permitted partition"
narration: "Lite fixes an ImageNet-initialized ResNet fifty and a replaced nine-class head. Standard selects among permitted architectures using balanced accuracy on training-derived validation. Record checkpoint class mapping and exclude exact frozen evaluation IDs. No checkpoint or training run is retained."
visual: "Dedicated operation panel with native public training patch or absent contract values; no invented result."
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
caption: "CSV or JSON remains unsubmitted"
narration: "The required artifact holds one canonical label for each Full case ID. CSV and per-case JSON are alternatives. Schema values remain unset; no reference, output or score is synthesized. Public training annotation is separate from these absent results."
visual: "Dedicated output panel with native public training patch or absent contract values; no invented result."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "Accuracy executable; balanced policy unresolved"
narration: "The executable headline is accuracy despite prose requesting balanced accuracy. Accuracy counts all case IDs including missing predictions; balanced accuracy averages recalls over supported true classes. Thresholds are provisional. Workflow and overall are separate aggregate fields; no measured result or clinical benefit is established."
visual: "Dedicated limits panel with native public training patch or absent contract values; no invented result."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
