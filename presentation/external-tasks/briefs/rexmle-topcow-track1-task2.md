# Localize the Circle of Willis in CTA

Produce the required 3D CoW ROI box for each held-out CTA image in the pinned ReX-MLE adaptation. This one-case source explainer reports no participant result.

## Given

### Original data

TopCoW2024 contains 125 source CTA cases. The pinned ReX adapter sorts IDs and uses `train_test_split(test_size=0.2, random_state=42)`, giving 100 train and 25 test cases per modality; static reproduction places illustrated case012 in test. The exact image is 266×371×311 voxels at 0.498046875×0.498046875×0.5 mm. The pack retains its native NIfTI sform, source SHA and nine fixed-index display slices; the preparer was not run.

### Supplied helpers

The ReX adaptation provides public image inputs, training labels and a sample submission/path convention. The illustrated test image is a solver input. Training labels are development aids, not this test answer.

### Callable tools

A participant may process the volume and write task-specific JSON and CSV files. This source audit did not execute a model, preparer, trial or grader.

### Reference-only material

The full original source release contains case012 ROI text with size 102×65×42 and location 86, 113, 96 in voxel units. The ReX test partition withholds that file from the solver. The explainer shows it only after reader reveal and labels the yellow projection as a scorer interpretation, not an observed prediction.

## Task specification

Produce one 3D CoW region box per held-out scan. The JSON has `size` and `location` arrays of three native voxel integers. The pinned grader computes minimum `location` and inclusive maximum `location+size−1`; the task prose instead calls `location` a center. Both readings are shown as abstract grids before source values are revealed.

## Expected output

`submission.csv` columns are `image_id,modality,predicted_bbox_path`. The expected relative file pattern is `predictions/topcow_ct_<id>_bbox.json`. The JSON must contain size and location arrays, each containing three voxel integers. The path and question-mark schema shown in the explainer are empty examples; no participant file exists here.

## Evaluation

The pinned grader computes `Boundary_IoU` after voxel margins `ceil(0.2×size)` and a metric named `IoU` after `ceil(0.5×size)`, so the latter is not ordinary undilated box IoU. Its minimum-corner geometry conflicts with the description center wording. No box score was produced. The selected source case alone cannot establish population, clinical or model performance.

## Visual explanation

### Workflow

- Inspect the exact native source image and physical coordinate map.
- Work through the minimum-corner versus center box ambiguity in a labeled symbolic diagram.
- Read the empty output schema, then explicitly reveal the source target and scorer limits.

## Sources

- [Official TopCoW2024 release and data-use terms](https://zenodo.org/records/15692630)
- [Pinned ReX task description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track1-task2/description.md)
- [Pinned ReX preparation](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track1-task2/prepare.py)
- [Pinned ReX grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track1-task2/grade.py)

## Gaps

No materialized ReX staging, submitted JSON, grader run, score or clinical assessment was retained. Original source images and annotations are exact source-matched local assets; the test annotation remains reader-only in this teaching view. TopCoW terms permit noncommercial use with attribution; commercial use requires owner permission.
