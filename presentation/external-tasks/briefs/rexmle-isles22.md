# Segment ischemic stroke lesions from multimodal MRI

Produce binary lesion masks for the held-out ISLES'22 cases in the pinned ReX-MLE adaptation. This explainer uses one actual selected case to show the input geometry and output contract; it reports no model result.

## Given

### Original data

The official ISLES-2022 v2.3.1 archive contains 250 complete DWI, ADC, FLAIR and source-mask cases. The pinned ReX preparation sorts IDs and applies `train_test_split(test_size=0.2, random_state=42, shuffle=True)`, yielding 200 labeled training cases and 50 test cases whose masks are private to evaluation. The exact illustrated test case is `sub-strokecase0186` (source `sub-strokecase0186_ses-0001`). Its recovered DWI and ADC arrays are 128×128×25 at 1.796875×1.796875×4.8 mm; FLAIR is a different 224×256×24 grid at 0.859375×0.859375×6 mm. Native affines are retained in the teaching pack.

### Supplied helpers

The ReX adapter stages public test DWI, ADC and FLAIR volumes, labeled train cases, submission instructions and relative-path conventions. These are task inputs and development aids, not held-out answers.

### Callable tools

A participant may develop and execute a segmentation pipeline in the task environment. This source review did not execute the ReX preparer, a model, a trial or a grader.

### Reference-only material

The selected source mask exists locally because it was recovered from the official archive. In the ReX test contract it is a private reference, withheld from the solver and shown in the explainer only after an explicit reader reveal. Local possession of the original source archive does not establish runtime visibility of ReX private paths.

## Task specification

Use permitted training labels and the three public contrasts to produce a binary lesion mask for every held-out case. Preserve IDs and spatial geometry. DWI and ADC share the selected case's native grid; FLAIR does not, so treating matching array indices as aligned anatomy would be incorrect.

## Expected output

`submission/submission.csv` has `case_id,predicted_mask_path`. An illustrative row is `sub-strokecase0186,predictions/sub-strokecase0186_pred.nii.gz`; the referenced file would be a binary NIfTI on the DWI/ADC 128×128×25 grid, with an appropriate affine. This is an empty output schema, not a retained prediction or submitted file.

## Evaluation

The pinned ReX grader computes Dice, lesion F1, lesion-count difference and absolute volume difference in mL, using reference spacing. It resizes shape-mismatched predictions by nearest neighbor before comparing arrays and does not validate affine agreement. No score or model behavior is reported here; an array-wise score alone would not establish physical registration or clinical validity.

## Visual explanation

The opening view shows fixed-window slices from actual DWI, ADC and FLAIR with separate native indices and physical RAS coordinates. The output chapter shows blank answer-owned fields. Only the reader-only chapter mounts the selected source mask on matching DWI pixels. Its 718 positive voxels out of 409,600 describe the reference volume, not prediction performance. One selected case is not population evidence.

## Sources

- [Official ISLES-2022 v2.3.1 archive, CC BY 4.0](https://zenodo.org/records/7960856)
- [Pinned ReX-MLE task description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/isles22/description.md)
- [Pinned ReX preparation](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/isles22/prepare.py)
- [Pinned ReX grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/isles22/grade.py)

## Gaps

No materialized ReX staging, participant output, grader run or independent clinical review was retained. The 200/50 partition was reproduced statically from the pinned splitter; the preparer itself was not run. The nine images per modality are deterministic teaching samples; all four original native NIfTI members remain retained separately.
