# Locate nuclei in ten fine classes

Detect individual nuclei in melanoma H&E ROIs and assign a fine-grained cell type. These identities support tissue analysis but do not establish treatment response.

## Given

### Original data

The official [PUMA record](https://zenodo.org/records/14869398) reports CC0-1.0. The worked 1024 × 1024 H&E ROI `training_set_metastatic_roi_001.tif` and matching annotations are hash- and archive-verified. Across 205 images paired with both annotation sets, pinned seed-42 splitting reconstructs 164 public train and 41 private-label test cases; this ROI falls in public train. The preparer was not executed.

### Supplied helpers

The same official training ROI has 633 source nucleus features; pinned Polygon-only conversion keeps 628 and skips five MultiPolygons. Accepted labels in this ROI are 498 tumor, 119 apoptotic cells, 8 lymphocytes and 3 endothelium.

### Callable tools

The task environment supports method development and file submission. No model, ReX preparer or grader was run for this explanation.

### Reference-only material

Held-out labels and test-label CSV belong to the evaluator. None is retained in this pack. The shown annotation is public-training help, not a private answer. Local source recovery does not prove runtime visibility inside an executed ReX task.

## Task specification

Search the full 1024 × 1024 ROI and keep ten classes distinct: tumor, lymphocytes, plasma cells, histiocytes, melanophages, neutrophils, stromal cells, epithelium, endothelium and apoptotic cells. The post-hoc crop is an inspection view, not a supplied target location.

## Expected output

Submit `submission/submission.csv` with `case_id,predicted_nuclei_path`. The per-case JSON accepts class-named polygons or simplified centroids with optional confidence. The example JSON is empty.

## Evaluation

The pinned Track 2 grader pairs same-class centroids at distance **less than or equal to 15 pixels**, then averages F1 across ten classes. It orders eligible predictions by confidence then distance and consumes each match once. For each class it averages only cases where that class appears in GT or predictions; it then averages the ten class means. A class absent across every case contributes 0. This case denominator differs from Track 1. No prediction or F1 was run.

## Visual explanation

The first view is the actual unmarked ROI. A later helper reveal shows its matching public-training annotation with a role and color legend. The operation scene traces source polygon-to-centroid mapping without turning the source label into a model output. The held-out artifact socket stays empty; the final scene explains the pinned scorer without a result.

## Difficulty

Only four of ten classes appear in this selected ROI. The five MultiPolygons excluded by conversion must not be counted as predictions or evaluator outcomes.

## Sources

- [Official PUMA Zenodo record](https://zenodo.org/records/14869398), CC0-1.0.
- [Pinned ReX-MLE adapter](https://github.com/rajpurkarlab/ReX-MLE/tree/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/puma-track2-task2).

## Gaps

Only one matched public-training source ROI is illustrated. The 164/41 split is reconstructed from code, not materialized by running the preparer. No held-out input, private label, model prediction, score or visual acceptance is retained.
