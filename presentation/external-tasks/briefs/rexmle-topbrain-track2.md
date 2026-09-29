# Label 42 MRA brain vessel classes

Produce the requested vessel mask for the pinned ReX-MLE task. This explainer uses one exact source case to explain the input and answer contract; it reports no participant result.

## Given

### Original data

25 source MRA cases; pinned random 20 train / 5 test split. Case 012 is train. The illustrated case is 012, a public training MRA volume. Native dimensions are 469×611×174 voxels at 0.296875×0.296875×0.599998 mm; the pack retains its full physical header and nine fixed native-index display slices. The image and label file identities are pinned by SHA-256 in the resolution receipt.

### Supplied helpers

The exact source label shown in the helper chapter is labeled public training material. The task also supplies a sample submission and path conventions. Helpers are not participant predictions.

### Callable tools

A participant may implement and run a segmentation workflow in the task environment. This explainer did not run a model, ReX preparer, trial or grader.

### Reference-only material

The exact illustrated source label is a public training label helper. It is source-derived public training help and is not a held-out ReX answer.

## Task specification

Read permitted MRA input and assign TopBrain 2025 v1 42-class vessel-label NIfTI, distinct from TopCoW CoW labels on the appropriate native grid. Respect the source image's coordinate map; a screen crop or equal array index is not a substitute for physical alignment.

## Expected output

The submission CSV must have `image_id,modality,predicted_mask_path`. Each relevant row points to `predictions/topcow_mr_<id>.nii.gz` (or the analogous held-out case path). The referenced file must contain the task-specific mask. No such participant file is retained here; the path is a schema illustration only.

## Evaluation

Pinned ReX grader evaluates class Dice, clDice, B0, HD95, invalid-neighbor error and side-road F1. The pinned grader nearest-neighbor resamples mismatched shapes and copies GT physical metadata onto predictions, including equal-shape predictions; it does not independently validate affine agreement. Per-case metrics average foreground labels present in GT or prediction before averaging cases; side-road F1 aggregates detection counts. No score or model behavior is inferred from the displayed source label.

## Visual explanation

### Workflow

- Inspect the exact source volume and physical grid.
- Follow the task-specific segmentation operation and empty output schema.
- Inspect the public training label helper, then read the scorer and single-case limits.

## Sources

- [Official source release and terms](https://zenodo.org/records/16878417)
- [Pinned ReX task description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topbrain-track2/description.md)
- [Pinned ReX preparation](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topbrain-track2/prepare.py)
- [Pinned ReX grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topbrain-track2/grade.py)

## Gaps

No ReX participant submission, graded score, independent clinical interpretation or materialized staging was retained. The split role was reproduced statically from the pinned adapter. The source images and labels support this one-case teaching view under noncommercial use with attribution terms.
