---
schema: 2
id: automedbench-full-dentex-det-task
title: Locate dental disease on a panoramic X-ray
locale: en
purpose: "Explain the Full detection input, pixel-box operation, exact output schema and source/reference boundary for panoramic dental X-ray."
scope: "Upstream image; private Full case and result absent."
recipe: automed-full-dentex-detection-v1
asset_pack: retained-automed-full-dentex-detection-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-dentex-det-task.md
- presentation/external-tasks/sources/automedbench-full-dentex-det-task-resolution.json
- scripts/build_automed_detection_assets.py
---

# Start with the image alone

```beat
id: input
scene: input
frames: 288
caption: "Start with the image alone"
narration: "The first view shows train_266.png, an official 1976 × 976 upstream image. It is an upstream example, not a verified Full Detection100 case. No source box, prediction or private reference appears yet."
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
visual: "Show actual source image and source-pixel ruler, with half-size preview mapping; no candidate or source label box."
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
narration: "This Full task uses Caries, Deep Caries, Periapical Lesion, Impacted. A shared prompt example mistakenly names VinDr classes for every detector; the task-specific configuration and class-aware scorer are authoritative."
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

# Reveal upstream labels only when requested

```beat
id: reference
scene: reference
frames: 336
caption: "Reveal upstream labels only when requested"
narration: "Once the reader reveals this chapter, upstream source annotations can be inspected. These are upstream source labels, not Full private boxes or an agent output."
visual: "Covered reference, then source-labeled dashed amber boxes only on explicit reveal; no Full private reference."
channels:
  scan: [0, 0]
  format: [0, 0]
  reference: [0, 1]
cut: intentional-cut
```

# Keep the source and score boundary visible

```beat
id: limits
scene: limits
frames: 312
caption: "Keep the source and score boundary visible"
narration: "Full DENTEX_Detection100 membership and conversion are unverified; upstream and Full terms differ. ReX split and scorer assumptions are unrelated. The retained scorer specifies class-aware IoU 0.5 matching, 101-point per-class AP and mean AP; no result was generated."
visual: "Three cards distinguish actual source, missing Full artifacts and scoring contract."
channels:
  scan: [0, 0]
  format: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
