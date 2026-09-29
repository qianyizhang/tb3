---
schema: 2
id: automedbench-full-vindr-cxr-det-task
title: Locate thoracic findings on chest X-rays
locale: en
purpose: "Explain the Full detection input, pixel-box operation, exact output schema and source/reference boundary for chest X-ray."
scope: "Symbolic contract; native case and result absent."
recipe: automed-full-vindr-cxr-detection-v1
asset_pack: retained-automed-full-vindr-cxr-detection-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-vindr-cxr-det-task.md
- presentation/external-tasks/sources/automedbench-full-vindr-cxr-det-task-resolution.json
- scripts/build_automed_detection_assets.py
---

# Identify the missing source image

```beat
id: input
scene: input
frames: 288
caption: "Identify the missing source image"
narration: "The first view is an empty image socket because official VinDr-CXR data require credentialed access. It is not a normal or negative X-ray."
visual: "Input-only source image or unavailable-image socket; source warning always visible."
channels:
  scan: [0, 0]
  format: [0, 0]
  reference: [0, 0]
```

# Search, then return to source pixels

```beat
id: coordinate
scene: coordinate
frames: 336
caption: "Search, then return to source pixels"
narration: "A detector may resize its image for inference. Its box corners must be mapped back into the original image width and height. The moving cyan crosshair is a coordinate ruler, not a detected finding."
visual: "Show a symbolic top-left coordinate grid, a moving cyan probe and separate width/height mapping; no image, candidate or annotation."
channels:
  scan: [0, 1]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Use the task-specific class strings

```beat
id: classes
scene: classes
frames: 300
caption: "Use the task-specific class strings"
narration: "This Full task uses Aortic enlargement, Atelectasis, Calcification, Cardiomegaly, Consolidation, ILD, Infiltration, Lung Opacity, Nodule/Mass, Other lesion, Pleural effusion, Pleural thickening, Pneumothorax, Pulmonary fibrosis. A shared prompt example mistakenly names VinDr classes for every detector; the task-specific configuration and class-aware scorer are authoritative."
visual: "Full class list and task-specific caveat; selected source annotations remain covered."
channels:
  scan: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Write boxes with score and original coordinates

```beat
id: submission
scene: submission
frames: 324
caption: "Write boxes with score and original coordinates"
narration: "For every Full case, agents_outputs/{case_id}/prediction.json needs a top-level boxes array. Each future box uses class, score, x1, y1, x2 and y2. The pack keeps boxes empty because no model was run. The format checker makes score optional but AP ranks absent score as 1.0."
visual: "Required path, exact empty JSON and box-field schema; no invented prediction."
channels:
  scan: [0, 0]
  format: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Keep the unavailable reference explicit

```beat
id: reference
scene: reference
frames: 336
caption: "Keep the unavailable reference explicit"
narration: "No source label or private Full reference can be revealed; no credentialed file was acquired."
visual: "Unavailable-reference panel throughout; no source or Full private label asset."
channels:
  scan: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Keep the source and score boundary visible

```beat
id: limits
scene: limits
frames: 312
caption: "Keep the source and score boundary visible"
narration: "Official data are credentialed; unauthenticated annotation request returned HTTP 403. No native image, private boxes or user-provisioned Lite model files are available. The retained scorer specifies class-aware IoU 0.5 matching, 101-point per-class AP and mean AP; no result was generated."
visual: "Three cards distinguish actual source, missing Full artifacts and scoring contract."
channels:
  scan: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
