---
schema: 2
id: anatomy-audit-context
title: Inspect the supplied label in its anatomical context
locale: en
purpose: Explain label audit, evidence and valid clean-control outputs.
scope: Retained TotalSegmentator teaching assembly, source s1233. Not a finding or
  answer for the selected task case. Display anchors are not anatomical landmarks.
recipe: anatomy-audit-v1
asset_pack: retained-anatomy-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-label-audit.md
- presentation/task-explorer/anatomy/manifest.json
---

# Inspect the supplied label in its anatomical context

## context

```beat
id: context
frames: 120
caption: Start with the supplied labels and source image.
narration: The real task provides patient DICOM or CT and named labels. The shared
  assembly here is a retained teaching example, not that patient.
visual: Show the retained abdominal assembly in one shared frame.
channels:
  focus:
  - 0.0
  - 0.0
  evidence:
  - 0.0
  - 0.0
  output:
  - 0.0
  - 0.0
```

## inspect

```beat
id: inspect
frames: 168
caption: Inspect one source object in relation to its neighbours.
narration: The left kidney object remains in the original assembly. Its identity comes
  from source metadata; this is not an agent answer.
visual: Select kidney_left while preserving the other six objects and relative scale.
channels:
  focus:
  - 0.0
  - 1.0
  evidence:
  - 0.0
  - 0.0
  output:
  - 0.0
  - 0.0
```

## witness

```beat
id: witness
frames: 144
caption: A reported defect needs a spatial witness.
narration: A surface centroid is only a display anchor. Inspect patient source data
  before filling the finding schema.
visual: Keep the selected object and show an unfilled label-and-witness schema.
channels:
  focus:
  - 1.0
  - 1.0
  evidence:
  - 0.0
  - 1.0
  output:
  - 0.0
  - 0.0
```

## control

```beat
id: control
frames: 144
caption: A clean case may return an empty finding list.
narration: Do not invent a defect. An empty finding list is valid only after the supplied
  source evidence has been reviewed.
visual: Hold the assembly and distinguish unreviewed from reviewed-clean.
channels:
  focus:
  - 1.0
  - 1.0
  evidence:
  - 1.0
  - 1.0
  output:
  - 0.0
  - 1.0
```
