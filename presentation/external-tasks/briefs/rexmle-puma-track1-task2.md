# Locate nuclei in three broad classes

Detect individual nuclei in melanoma H&E ROIs and classify each as tumor, tumor-infiltrating lymphocyte group, or other. This is per-nucleus localization, not a tissue mask.

## Given

### Original data

The official [PUMA record](https://zenodo.org/records/14869398) reports CC0-1.0. The worked 1024 × 1024 H&E ROI `training_set_metastatic_roi_001.tif` and matching annotations are hash- and archive-verified. Across 205 images paired with both annotation sets, pinned seed-42 splitting reconstructs 164 public train and 41 private-label test cases; this ROI falls in public train. The preparer was not executed.

### Supplied helpers

The source training GeoJSON has 633 nucleus features. Pinned Polygon-only conversion keeps 628 and skips five MultiPolygons. In this ROI it maps 498 accepted tumor, 8 TIL and 122 other nuclei. Training centroids and a post-hoc inspection crop are source help, not predictions.

### Callable tools

The task environment supports method development and file submission. No model, ReX preparer or grader was run for this explanation.

### Reference-only material

Held-out labels and test-label CSV belong to the evaluator. None is retained in this pack. The shown annotation is public-training help, not a private answer. Local source recovery does not prove runtime visibility inside an executed ReX task.

## Task specification

Find nucleus locations across the full 1024 × 1024 ROI and assign tumor, TILs or other. The adapter groups source lymphocytes and plasma cells as TILs; other listed non-tumor types become other.

## Expected output

Submit `submission/submission.csv` with `case_id,predicted_nuclei_path`. The per-case JSON accepts named polygons with `path_points` or simplified class-and-centroid records; confidence is optional. The example JSON is empty.

## Evaluation

The pinned Track 1 grader pairs same-class centroids only when distance is strictly **less than 15 pixels**. For each GT nucleus it favors confidence, then distance, and consumes a prediction once. It averages three class F1 values. It averages each class F1 across every submitted case (both-empty class/case contributes 0), then averages the three classes. No prediction or F1 was run.

## Visual explanation

The first view is the actual unmarked ROI. A later helper reveal shows its matching public-training annotation with a role and color legend. The operation scene traces source polygon-to-centroid mapping without turning the source label into a model output. The held-out artifact socket stays empty; the final scene explains the pinned scorer without a result.

## Difficulty

Crowded nuclei and grouping source classes are distinct operations; five MultiPolygons in the source case do not enter pinned conversion.

## Sources

- [Official PUMA Zenodo record](https://zenodo.org/records/14869398), CC0-1.0.
- [Pinned ReX-MLE adapter](https://github.com/rajpurkarlab/ReX-MLE/tree/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/puma-track1-task2).

## Gaps

Only one matched public-training source ROI is illustrated. The 164/41 split is reconstructed from code, not materialized by running the preparer. No held-out input, private label, model prediction, score or visual acceptance is retained.
