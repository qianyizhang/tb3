# Segment Circle of Willis vessels in MRA

Produce the requested vessel mask for the pinned ReX-MLE task. This explainer uses one exact source case to explain the input and answer contract; it reports no participant result.

## Given

### Original data

125 source MRA cases; pinned random 100 train / 25 test split. Case 012 is test by static reproduction. The illustrated case is 012, a held-out test MRA volume. Native dimensions are 469×611×174 voxels at 0.296875×0.296875×0.599998 mm; the pack retains its full physical header and nine fixed native-index display slices. The image and label file identities are pinned by SHA-256 in the resolution receipt.

### Supplied helpers

Labeled source training cases are available for development; the selected test label is withheld in ReX staging. The task also supplies a sample submission and path conventions. Helpers are not participant predictions.

### Callable tools

A participant may implement and run a segmentation workflow in the task environment. This explainer did not run a model, ReX preparer, trial or grader.

### Reference-only material

The exact illustrated source label is a reader-only source reference hidden from the ReX solver. It exists in the public original release, but the ReX test staging withholds it from the solver; the explainer mounts it only after reader reveal.

## Task specification

Read permitted MRA input and assign TopCoW 2024 multiclass CoW vessel-label NIfTI, private reference in ReX staging on the appropriate native grid. Respect the source image's coordinate map; a screen crop or equal array index is not a substitute for physical alignment.

## Expected output

The submission CSV must have `image_id,modality,predicted_mask_path`. Each relevant row points to `predictions/topcow_mr_<id>_0000.nii.gz` (or the analogous held-out case path). The referenced file must contain the task-specific mask. No such participant file is retained here; the path is a schema illustration only.

## Evaluation

Pinned ReX grader evaluates class overlap, centerline and boundary metrics, group-2 detection and anterior/posterior topology. Dice, B0 and HD95 average foreground classes present in GT; clDice merges nonzero labels into a binary vessel mask. The scorer resamples shape mismatches and overwrites same-size prediction physical metadata with the ground-truth map; its array score is not affine validation. No score or model behavior is inferred from the displayed source label.

## Visual explanation

### Workflow

- Inspect the exact source volume and physical grid.
- Follow the task-specific segmentation operation and empty output schema.
- Explicitly reveal the held-out source reference, then read the scorer and single-case limits.

## Sources

- [Official source release and terms](https://zenodo.org/records/15692630)
- [Pinned ReX task description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track2-task1/description.md)
- [Pinned ReX preparation](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track2-task1/prepare.py)
- [Pinned ReX grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track2-task1/grade.py)

## Gaps

No ReX participant submission, graded score, independent clinical interpretation or materialized staging was retained. The split role was reproduced statically from the pinned adapter. The source images and labels support this one-case teaching view under noncommercial use with attribution terms.
