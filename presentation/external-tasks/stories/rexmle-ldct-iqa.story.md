---
schema: 2
id: rexmle-ldct-iqa
title: "Predict perceived low-dose CT quality"
locale: en
purpose: "Explain no-reference scalar prediction and reader-score evaluation without invented results."
scope: "One official public training CT and label; symbolic inference/output; held-out images and private scores absent."
recipe: rex-ldct-iqa-v1
asset_pack: retained-rexmle-ldct-iqa-interpretation-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-ldct-iqa.md
- presentation/external-tasks/sources/rexmle-ldct-iqa-resolution.json
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Training CT only; test absent · zenodo.org/records/7833096"
narration: "This is one official training CT, not a held-out image. Its normalized float raster is displayed by linear scaling, without HU calibration, spacing or inferred anatomical orientation. The linked official archive is the acquisition route."
visual: "Dedicated input panel with source and absent-output boundaries. No synthetic CT or target."
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
caption: "Public training score, not a prediction"
narration: "The public training record for 0559.tif supplies a reader score. Reveal it explicitly to inspect this training helper; it cannot be used as a held-out result. The inspected adapter does not establish the score scale endpoints. Select the partition to inspect what is solver-visible and what belongs to evaluation."
visual: "Dedicated helper panel with source and absent-output boundaries. No synthetic CT or target."
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
caption: "CT input → scalar quality estimate"
narration: "Develop or adapt a no-reference predictor using allowed training examples, then infer one quality value for every exact test image ID. No pristine reference is needed at inference. The pinned preparer stages distinct upstream archives and produces zero-valued submission placeholders. Nothing is trained or executed here."
visual: "Dedicated operation panel with source and absent-output boundaries. No synthetic CT or target."
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
caption: "Required CSV remains unsubmitted"
narration: "The output is submission.csv with extensionless image_id and numeric quality_score. The illustrated values remain unset because no test data or model output is retained. An image restoration or segmentation is not the required artifact."
visual: "Dedicated output panel with source and absent-output boundaries. No synthetic CT or target."
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
caption: "Correlation sum differs from overall rank"
narration: "The grader sums three absolute correlations, which discard prediction direction. Cohort coefficients cannot be computed from this one example. Overall uses leaderboard positions when available and otherwise negative absolute Pearson correlation. Constant arrays can produce undefined coefficients. No correlation, rank or clinical benefit is measured."
visual: "Dedicated limits panel with source and absent-output boundaries. No synthetic CT or target."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
