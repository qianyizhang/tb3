# Label melanoma tissue regions

Develop a semantic mask for melanoma H&E tissue ROIs. This is tissue compartment labeling, not individual nucleus detection or a clinical outcome.

## Given

### Original data

The official [PUMA record](https://zenodo.org/records/14869398) reports CC0-1.0. The worked 1024 × 1024 H&E ROI `training_set_metastatic_roi_001.tif` and matching annotations are hash- and archive-verified. Across 205 images paired with both annotation sets, pinned seed-42 splitting reconstructs 164 public train and 41 private-label test cases; this ROI falls in public train. The preparer was not executed.

### Supplied helpers

Public-training GeoJSON tissue polygons and class definitions. This selected ROI has one tumor polygon and one necrosis polygon. A deterministic local mask rendering follows the pinned exterior-fill rule; it is training help, not a model prediction.

### Callable tools

The task environment supports method development and file submission. No model, ReX preparer or grader was run for this explanation.

### Reference-only material

Held-out labels and test-label CSV belong to the evaluator. None is retained in this pack. The shown annotation is public-training help, not a private answer. Local source recovery does not prove runtime visibility inside an executed ReX task.

## Task specification

Paint one 1024 × 1024 pixel class mask per held-out ROI. The pinned adapter maps background 0, stroma 1, blood vessel 2, tumor 3, epidermis 4 and necrosis 5. Its description also says epithelium in prose; ID 4 is `tissue_epidermis` in converter and grader.

## Expected output

Submit `submission/submission.csv` with `case_id,predicted_mask_path` and a TIF or PNG semantic mask using integer IDs 0–5. The staged example output is empty.

## Evaluation

The pinned grader excludes background, concatenates masks by foreground class, computes class Dice for IDs 1–5, then averages them as primary micro Dice. Macro Dice separately averages case scores. It nearest-neighbor resizes shape mismatches; no prediction or score was run.

## Visual explanation

The first view is the actual unmarked ROI. A later helper reveal shows its matching public-training annotation with a role and color legend. The operation scene traces polygon-to-pixel tissue conversion without turning the source label into a model output. The held-out artifact socket stays empty; the final scene explains the pinned scorer without a result.

## Difficulty

Only tumor and necrosis occur in the worked ROI; the full five-class task is broader.

## Sources

- [Official PUMA Zenodo record](https://zenodo.org/records/14869398), CC0-1.0.
- [Pinned ReX-MLE adapter](https://github.com/rajpurkarlab/ReX-MLE/tree/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/puma-track1-task1).

## Gaps

Only one matched public-training source ROI is illustrated. The 164/41 split is reconstructed from code, not materialized by running the preparer. No held-out input, private label, model prediction, score or visual acceptance is retained.
