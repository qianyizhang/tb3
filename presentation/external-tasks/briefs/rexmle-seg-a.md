# Segment the aortic vessel tree in CTA

Produce the requested vessel mask for the pinned ReX-MLE task. This explainer uses one exact source case to explain the input and answer contract; it reports no participant result.

## Given

### Original data

56 published case pairs; pinned random 44 train / 12 test split. K20 is train. The illustrated case is K20, a public training CTA volume. Native dimensions are 512×512×94 voxels at 0.55078125×0.55078125×5 mm; the pack retains its full physical header and nine fixed native-index display slices. The image and label file identities are pinned by SHA-256 in the resolution receipt.

### Supplied helpers

The exact source label shown in the helper chapter is labeled public training material. The task also supplies a sample submission and path conventions. Helpers are not participant predictions.

### Callable tools

A participant may implement and run a segmentation workflow in the task environment. This explainer did not run a model, ReX preparer, trial or grader.

### Reference-only material

The exact illustrated source label is a public training label helper. It is source-derived public training help and is not a held-out ReX answer.

## Task specification

Read permitted CTA input and assign binary aortic vessel tree mask, source NRRD value 1 for aorta on the appropriate native grid. Respect the source image's coordinate map; a screen crop or equal array index is not a substitute for physical alignment.

## Expected output

The submission CSV must have `image_id,predicted_mask_path`. Each relevant row points to `predictions/<image_id>.seg.nrrd` (or the analogous held-out case path). The referenced file must contain the task-specific mask. No such participant file is retained here; the path is a schema illustration only.

## Evaluation

Pinned ReX grader computes base-case mean Dice and Hausdorff distance, with nearest-neighbor array zoom when prediction shape differs. The adapted grader does not implement the original challenge Sobol sensitivity p1/p2. Its random case split mixes institutions despite the description of a fourth-institution test. No score or model behavior is inferred from the displayed source label.

## Visual explanation

### Workflow

- Inspect the exact source volume and physical grid.
- Follow the task-specific segmentation operation and empty output schema.
- Inspect the public training label helper, then read the scorer and single-case limits.

## Sources

- [Official source release and terms](https://figshare.com/articles/dataset/Aortic_Vessel_Tree_AVT_CTA_Datasets_and_Segmentations/14806362)
- [Pinned ReX task description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/seg_a/description.md)
- [Pinned ReX preparation](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/seg_a/prepare.py)
- [Pinned ReX grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/seg_a/grade.py)

## Gaps

No ReX participant submission, graded score, independent clinical interpretation or materialized staging was retained. The split role was reproduced statically from the pinned adapter. The source images and labels support this one-case teaching view under CC BY 4.0 terms.
