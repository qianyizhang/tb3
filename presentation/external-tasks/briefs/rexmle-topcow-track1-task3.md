# Classify Circle of Willis connections in CTA

Produce the required named CoW connection bits for each held-out CTA image in the pinned ReX-MLE adaptation. This one-case source explainer reports no participant result.

## Given

### Original data

TopCoW2024 contains 125 source CTA cases. The pinned ReX adapter sorts IDs and uses `train_test_split(test_size=0.2, random_state=42)`, giving 100 train and 25 test cases per modality; static reproduction places illustrated case012 in test. The exact image is 266×371×311 voxels at 0.498046875×0.498046875×0.5 mm. The pack retains its native NIfTI sform, source SHA and nine fixed-index display slices; the preparer was not run.

### Supplied helpers

The ReX adaptation provides public image inputs, training labels and a sample submission/path convention. The illustrated test image is a solver input. Training labels are development aids, not this test answer.

### Callable tools

A participant may process the volume and write task-specific JSON and CSV files. This source audit did not execute a model, preparer, trial or grader.

### Reference-only material

The full original source release contains case012 YML with four anterior and four posterior 0/1 edge values. The ReX test partition withholds this file from the solver. The explainer shows the bits only after reader reveal; the graph position is schematic and not traced from patient pixels.

## Task specification

Classify presence or absence of L-A1, Acom, 3rd-A2 and R-A1 in `anterior`, and L-Pcom, L-P1, R-P1 and R-Pcom in `posterior`. The graph is a named topology schema; no source vessel segmentation is a supplied answer to this task.

## Expected output

`submission.csv` columns are `image_id,modality,predicted_edges_path`. The expected relative file pattern is `predictions/topcow_ct_<id>_edges.json`. The JSON must contain anterior and posterior maps with the eight exact named zero-or-one edge keys. The path and question-mark schema shown in the explainer are empty examples; no participant file exists here.

## Evaluation

The pinned grader concatenates each region's four edge bits into anterior and posterior variant strings, then scores balanced accuracy separately across cases. It does not report per-edge accuracy from this one case. No graph score was produced. The selected source case alone cannot establish population, clinical or model performance.

## Visual explanation

### Workflow

- Inspect the exact native source image and physical coordinate map.
- Work through the eight candidate arterial connection keys in a labeled symbolic diagram.
- Read the empty output schema, then explicitly reveal the source target and scorer limits.

## Sources

- [Official TopCoW2024 release and data-use terms](https://zenodo.org/records/15692630)
- [Pinned ReX task description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track1-task3/description.md)
- [Pinned ReX preparation](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track1-task3/prepare.py)
- [Pinned ReX grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track1-task3/grade.py)

## Gaps

No materialized ReX staging, submitted JSON, grader run, score or clinical assessment was retained. Original source images and annotations are exact source-matched local assets; the test annotation remains reader-only in this teaching view. TopCoW terms permit noncommercial use with attribution; commercial use requires owner permission.
