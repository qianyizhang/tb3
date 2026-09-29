---
schema: 2
id: rexmle-puma-track1-task1
title: Paint five tissue classes on a melanoma ROI
locale: en
purpose: Explain the pinned PUMA task from one source-matched training ROI, its allowed annotation and an empty held-out output.
scope: Actual training ROI and supplied annotation; held-out input, prediction and score are absent.
recipe: rexmle-puma-track1-task1-v1
asset_pack: retained-rexmle-puma-track1-task1-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-puma-track1-task1.md
- presentation/external-tasks/sources/rexmle-puma-track1-task1-resolution.json
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
narration: The official training GeoJSON has two tissue polygons in this ROI, tumor and necrosis. These are supplied training annotations, not a prediction or private held-out answer.
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
narration: The pinned converter fills polygon exteriors into a 1024-square integer grid. Tumor is ID 3 and necrosis ID 5 here; the full five-class contract also includes stroma, blood vessel and epidermis. Zero is background. This semantic mask describes tissue compartments, not individual nuclei.
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
narration: A held-out case would require submission.csv with case_id and predicted_mask_path, pointing to a TIF or PNG mask with pixel IDs 0 through 5. This pack has an empty output schema and no held-out prediction.
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
narration: The pinned scorer excludes background, concatenates held-out masks by foreground class, computes five class Dice values and averages them as primary micro Dice. Macro Dice separately averages per-case values. No Dice was computed.
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
narration: This ROI has only two tissue classes. The derived training mask follows the pinned polygon-fill rule but the preparer was not run.
visual: Actual, reconstructed, absent and task-scope limits.
channels:
  helper: [0, 0]
  focus: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```
