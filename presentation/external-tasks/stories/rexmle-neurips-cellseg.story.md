---
schema: 2
id: rexmle-neurips-cellseg
title: Separate cell identities, then specify the held-out mask
locale: en
purpose: Inspect an actual public-training image and instance annotation, then trace the absent held-out output and pinned instance-matching grader.
scope: Real public-training image and instance labels; symbolic held-out output and scorer. No prediction or F1 run.
recipe: rexmle-neurips-cellseg-v1
asset_pack: retained-rexmle-neurips-cellseg-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-neurips-cellseg.md
- presentation/external-tasks/sources/rexmle-neurips-cellseg-resolution.json
- scripts/build_rexmle_cellseg_assets.py
---

# Begin with one public-training patch

```beat
id: input
scene: input
frames: 300
caption: A real 512 × 512 microscopy training image
narration: The official CellSeg patch cell_00944 is a real public-training source image, not a held-out ReX test case. The matching training label is available as supplied help but is not shown on first read. The pinned adapter combines 1,000 Training-labeled and 101 Tuning pairs; a seeded split is reconstructed as 880 public train and 221 private-label test. The preparer was not run.
visual: Original RGB fluorescence patch alone with a separate empty held-out lane; persistent official-source and no-result notice.
channels:
  helper: [0, 0]
  instance: [0, 0]
  metric: [0, 0]
```

# Open the supplied training label

```beat
id: helper
scene: helper
frames: 336
caption: The training TIFF contains 36 separate cell IDs
narration: The matching source TIFF is legitimate training help. Its value zero is background; positive IDs 1 through 36 distinguish individual cells, not cell types. The colored overlay comes from this exact source label and covers 8,479 of 262,144 pixels. The held-out evaluator label is not present.
visual: Explicit helper reveal overlays source-label colored boundaries on the same actual image, with a matching legend and role label.
channels:
  helper: [0, 1]
  instance: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```

# Why foreground is not enough

```beat
id: instances
scene: instances
frames: 432
caption: Binary foreground collapses identity
narration: On this exact training patch, binary foreground turns every positive pixel into one class. The source instance map keeps 36 arbitrary positive IDs so touching cells can be separated. Four selected real IDs provide label-guided post-hoc crops and native inclusive boxes. Those crops are inspection aids, not model search results.
visual: Side-by-side actual binary and instance source overlays, plus one of four label-guided source crops visibly marked as post-hoc.
channels:
  helper: [1, 1]
  instance: [0, 1]
  metric: [0, 0]
cut: intentional-cut
```

# Specify the missing held-out output

```beat
id: submission
scene: submission
frames: 348
caption: One integer-ID TIFF per held-out image
narration: The ReX task requires a submission CSV with image_id and predicted_mask_path. Each path should lead to a 2D integer instance mask on that case's pixel grid; zero is background and each cell receives a distinct positive ID. There is no retained held-out image or predicted TIFF here, so the row is a placeholder schema, not a saved answer.
visual: Empty held-out image socket leads to exact CSV columns and an empty integer-mask TIFF socket. No invented patient or cell prediction is drawn.
channels:
  helper: [0, 0]
  instance: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```

# Trace the pinned scoring operation

```beat
id: scoring
scene: scoring
frames: 432
caption: Pairwise IoU and one-to-one instance matching
narration: For a future held-out label and submission, the pinned grader would make pairwise instance IoUs, assign one-to-one pairs by the Hungarian algorithm, and count matches at inclusive IoU thresholds 0.5 through 0.9 before computing instance F1. It removes cells touching a two-pixel image border before matching. Images with at least 25 million pixels use 2000 by 2000 regions; this 512-square training patch is below that branch. No score was computed.
visual: Labeled symbolic scorer pipeline and threshold sweep; unavailable private label and prediction sockets stay empty.
channels:
  helper: [0, 0]
  instance: [0, 0]
  metric: [0, 1]
cut: intentional-cut
```

# State the evidence boundary

```beat
id: limits
scene: limits
frames: 264
caption: Real training label; no held-out result
narration: The image and 36-instance label are official source data. The expected 880/221 ReX split follows the pinned source logic but was not materialized by running its preparer. The adapter narrows the original competition archive to Training-labeled and Tuning pairs for this prepared split. No exact held-out image, private label, model mask, grader run, or F1 is retained.
visual: Actual, reconstructed, absent and source-scope cards below the persistent acquisition notice.
channels:
  helper: [0, 0]
  instance: [0, 0]
  metric: [0, 0]
cut: intentional-cut
```
