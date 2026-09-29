---
schema: 2
id: rexmle-puma-track1-task2
title: Group detected nuclei into three classes
locale: en
purpose: Explain the pinned PUMA task from one source-matched training ROI, its allowed annotation and an empty held-out output.
scope: Actual training ROI and supplied annotation; held-out input, prediction and score are absent.
recipe: rexmle-puma-track1-task2-v1
asset_pack: retained-rexmle-puma-track1-task2-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-puma-track1-task2.md
- presentation/external-tasks/sources/rexmle-puma-track1-task2-resolution.json
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
narration: The official source nuclei GeoJSON has 633 features. The pinned Polygon-only converter keeps 628 and skips five MultiPolygons. Colored training centroids are helper labels, never predicted detections.
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
narration: The pinned adapter maps accepted source nuclei into tumor, TILs and other. This ROI yields 498 tumor, 8 TIL and 122 other polygons. Centroids are arithmetic means of exterior path points. The 256-square crop is post-hoc label-guided inspection; the full ROI remains the search field.
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
narration: A held-out submission requires case_id and predicted_nuclei_path in submission.csv. The per-case JSON accepts named polygons with path_points or simplified centroid records and optional confidence. The output array is empty here.
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
narration: Track 1 matches same-class centroids only when distance is strictly less than 15 pixels. For each GT nucleus it chooses an eligible prediction by confidence then distance and consumes the match once. Each class F1 averages every submitted case (both-empty class/case contributes 0), then macro F1 averages the three class means. No F1 was computed.
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
narration: Five source MultiPolygons are skipped by pinned conversion. This public-training example does not contain a held-out prediction or score.
visual: Actual, reconstructed, absent and task-scope limits.
channels:
  helper: [0, 0]
  focus: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```
