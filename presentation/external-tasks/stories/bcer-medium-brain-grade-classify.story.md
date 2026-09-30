---
schema: 2
id: bcer-medium-brain-grade-classify
title: "Classify brain glioma grade through BCER tools"
locale: en
purpose: "Explain the pinned four-modality artifact chain and its structural checks without a patient grade claim."
scope: "Symbolic workflow only. No matched MRI, case features, grade result or measured accuracy."
recipe: bcer-brain-grade-v1
asset_pack: retained-bcer-medium-brain-grade-classify-workflow-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-medium-brain-grade-classify.md
- presentation/external-tasks/sources/bcer-medium-brain-grade-classify-resolution.json
- scripts/build_brain_grade_refined_assets.py
---

# Identify required input

```beat
id: input
scene: input
frames: 264
caption: "Four modalities, one case"
narration: "One case must supply T1, contrast-enhanced T1c, T2 and FLAIR. All four sockets are empty here; no patient image or answer is shown. Correct modality identity matters as much as path existence."
visual: "Four labeled empty MRI sockets and a top acquisition warning."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Trace the registered chain

```beat
id: route
scene: route
frames: 288
caption: "Follow the artifact route"
narration: "BCER requires sequence identification, tumor segmentation, ROI-feature extraction, then grade classification. Each stage consumes prior artifacts. This is the contract order, not an observed tool trace."
visual: "Four source-code stage names connected by artifact arrows, no completion marks."
channels:
  progress: [0, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Inspect one stage at a time

```beat
id: operation
scene: operation
frames: 336
caption: "Inspect stages and static grade rule"
narration: "Focus a stage to see its required input, output artifact and invariant. The grade tool prefers whole-tumor feature rows, then uses maximum valid volume against an inclusive default 35 milliliter threshold; without volume, it checks how many texture fields are available. These are code branches only. No patient's feature value, predicted grade or calibrated probability exists here."
visual: "Interactive stage-focus cards and static classifier branch; all case values unset."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Keep outputs and checks distinct

```beat
id: output
scene: output
frames: 288
caption: "Require two output artifacts"
narration: "The feature-table path must lead to a CSV with a row; the classification path must lead to JSON with a nonempty predicted_grade field. These are empty sockets in this explanation. The four stage successes and two paths form a six-item completion ratio; separate success and invariant checks remain structural."
visual: "Empty CSV/JSON artifact sockets with structural checklist, no result."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# State what is not measured

```beat
id: limits
scene: limits
frames: 264
caption: "Separate structural completion from accuracy"
narration: "No case-matched annotation or independently established true HGG/LGG grade is retained, and BCER's pinned scorer does not compare with either. BraTS Task 2 is MGMT methylation, not an HGG/LGG answer. The source rule is a transparent heuristic; no clinical accuracy is claimed."
visual: "Unavailable source/reference and no observed score."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
