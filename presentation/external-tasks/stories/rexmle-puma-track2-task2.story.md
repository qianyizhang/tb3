---
schema: 2
id: rexmle-puma-track2-task2
title: Classify nuclei into ten fine-grained types
locale: en
purpose: Explain the pinned PUMA task from one source-matched training ROI, its allowed annotation and an empty held-out output.
scope: Actual training ROI and supplied annotation; held-out input, prediction and score are absent.
recipe: rexmle-puma-track2-task2-v1
asset_pack: retained-rexmle-puma-track2-task2-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-puma-track2-task2.md
- presentation/external-tasks/sources/rexmle-puma-track2-task2-resolution.json
- scripts/build_rexmle_puma_assets.py
---


# One source H&E training ROI

```beat
id: input
scene: input
frames: 300
caption: One source H&E training ROI
narration: The actual PUMA H&E ROI training_set_metastatic_roi_001 is 1024 by 1024 pixels. Official image and both annotation archives match by case ID. The seed-42 split reconstructs 164 public train and 41 private-label test cases from 205 matched cases, placing this ROI in public train. The ReX preparer was not run.
visual: Actual full ROI alone and source split strip.
channels:
  helper: [0, 0]
  focus: [0, 0]
  metric: [0, 0]
```


# Open the matching training annotation

```beat
id: helper
scene: helper
frames: 360
caption: Open the matching training annotation
narration: The matching source nuclei GeoJSON has 633 features; pinned Polygon-only conversion keeps 628. Source centroid markers are supplied training help. The label-guided crop is post-hoc, not a substitute for full-ROI search.
visual: Explicit training annotation overlay with source-role legend.
channels:
  helper: [0, 1]
  focus: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```


# Trace the label operation

```beat
id: operation
scene: operation
frames: 360
caption: Trace the label operation
narration: Track 2 keeps ten fine class names rather than grouping TILs and other. This ROI has 498 tumor, 119 apoptotic, 8 lymphocyte and 3 endothelium polygons. The other six task classes are not shown as invented nuclei.
visual: Source annotation operation, with post-hoc crop only for nuclei.
channels:
  helper: [1, 1]
  focus: [0, 1]
  metric: [0, 0]
cut: intentional-cut
```


# Specify the empty held-out output

```beat
id: submission
scene: submission
frames: 360
caption: Specify the empty held-out output
narration: A held-out submission requires case_id and predicted_nuclei_path in submission.csv. Per-case JSON can hold class-named polygons or direct centroids with optional confidence. No prediction was retained; the schema array is empty.
visual: Empty held-out input and output sockets with exact CSV columns.
channels:
  helper: [0, 0]
  focus: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```


# Read the pinned scorer

```beat
id: scoring
scene: scoring
frames: 360
caption: Read the pinned scorer
narration: Track 2 uses same-class one-to-one centroid matching at distance less than or equal to 15 pixels. Eligible predictions are ordered by confidence then distance and consumed after use. Each class F1 averages cases where GT or predictions contain it; classes absent everywhere contribute zero to the ten-class mean. No score was computed.
visual: Scorer operation diagram with no measured score.
channels:
  helper: [0, 0]
  focus: [0, 0]
  metric: [0, 1]
cut: intentional-cut
```


# Bound the evidence

```beat
id: limits
scene: limits
frames: 360
caption: Bound the evidence
narration: Only four of ten classes occur in this source ROI, and five MultiPolygons are skipped by the pinned converter. No held-out prediction or score is retained.
visual: Actual, reconstructed, absent and task-scope limits.
channels:
  helper: [0, 0]
  focus: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```
