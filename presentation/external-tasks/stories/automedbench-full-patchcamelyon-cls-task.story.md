---
schema: 2
id: automedbench-full-patchcamelyon-cls-task
title: "Classify the center of a PCam tile"
locale: en
purpose: "Explain patch-center labels and Full partition/output boundaries."
scope: "Symbolic 96-pixel geometry; official README collage is a helper. Exact dataset row, Full IDs, private targets and results are absent."
recipe: automed-pcam-cls-v1
asset_pack: retained-automed-pcam-cls-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-patchcamelyon-cls-task.md
- presentation/external-tasks/sources/automedbench-full-patchcamelyon-cls-task-resolution.json
- scripts/build_automed_pcam_cls_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full tile absent · github.com/basveeling/pcam"
narration: "The requested input is a ninety-six by ninety-six color histology tile. This frame shows only symbolic geometry because no indexed native training pair or frozen Full case was verified. The central thirty-two by thirty-two region determines the label. The official acquisition route remains linked."
visual: "Dedicated input panel; no native Full patch or result fabricated."
channels:
  progress: [0,1]
  detail: [0,1]
  reference: [0,0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Reveal upstream label-marked figure"
narration: "The retained official README figure includes positive markings, so reveal it explicitly. It is a collage, with unknown dataset row IDs and partition, not a Full tile or private answer. Source zero maps to negative and one to positive. Outer tumor alone does not determine a positive label."
visual: "Dedicated helper panel; no native Full patch or result fabricated."
channels:
  progress: [0,1]
  detail: [0,1]
  reference: [0,0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Preserve center semantics and WSI splits"
narration: "Lite fixes an ImageNet-initialized ResNet eighteen with a two-class head. Standard uses permitted candidates and public validation. Preserve whole-slide-disjoint train and test boundaries and record crop, resize and class mapping. No checkpoint or model run occurs here."
visual: "Dedicated operation panel; no native Full patch or result fabricated."
channels:
  progress: [0,1]
  detail: [0,1]
  reference: [0,0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 288
caption: "One canonical string; output unset"
narration: "CSV patient ID and label or per-case prediction JSON are alternatives. Map upstream numeric labels to the canonical negative or positive strings. All output values remain unset. The public figure supplies no matching Full case label."
visual: "Dedicated output panel; no native Full patch or result fabricated."
channels:
  progress: [0,1]
  detail: [0,1]
  reference: [0,0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "All-case denominator, no measured outcome"
narration: "Accuracy uses every supplied Full case ID, counting missing predictions as wrong. Balanced accuracy averages supported true classes. The Full hundred-case subset and its balance remain unresolved despite balanced upstream splits. Generic thresholds and aggregate rules are definitions only. No metric, diagnosis or clinical benefit is claimed."
visual: "Dedicated limits panel; no native Full patch or result fabricated."
channels:
  progress: [0,1]
  detail: [0,1]
  reference: [0,0]
cut: intentional-cut
```
