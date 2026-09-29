# Segment pancreatic tumor on MR-Linac MRI

Produce a binary pancreatic tumor mask for held-out T2-weighted MRI from an Elekta Unity MR-Linac during radiotherapy. This source-backed explainer is **symbolic** because the official matching MRI and labels are restricted and unavailable locally; [request research access](https://zenodo.org/records/15192302). No patient pixels, prediction or score appear.

## Given

### Original data

The pinned ReX preparer expects native MHA volumes named `ImagesTr/*_0000.mha` and matches source labels at `LabelsTr/<patient-ID>.mha`. The source description names 50 annotated cases. It sorts matched cases and applies `train_test_split(test_size=0.2, random_state=42)`: **40 training / 10 test only if all 50 described cases match**. No preparer run or native case geometry is retained here. Official PANTHER files require noncommercial research access and are absent from the anonymous record's file list.

### Supplied helpers

Public current-domain training images and tumor masks, plus case/scan metadata. Diagnostic Task 1 data are a different imaging domain; any transfer method would be a development choice, not a registered same-patient label. The held-out input image is public in the ReX staging contract; its label is not.

### Callable tools

A participant may build and run an allowed image-segmentation method and write MHA predictions in the task environment. This explanation did not install dependencies or run preparation, inference or grading.

### Reference-only material

The pinned preparer stages held-out tumor masks under `private/test/labels` with `test_labels.csv`; those are evaluator material. Source labels may include 0 background, 1 tumor and 2 pancreas; pinned grading extracts `GT == 1`. No held-out label pixels are bundled or revealed as patient imagery. This task describes a current-session tumor contour, not an adaptive treatment plan, delivery result or cross-session deformation.

## Task specification

Segment tumor on each public held-out T2-weighted MRI from an Elekta Unity MR-Linac during radiotherapy. Use the current image's native MHA dimensions, spacing, origin and direction when constructing the answer mask. These values are unknown in this symbolic pack. Public training masks are method help; they do not substitute for a private held-out mask.

## Expected output

The **pinned ReX adapter**, rather than the prose example in its challenge description, defines `submission/submission.csv` columns `image_id,predicted_mask_path`; each row points to `predictions/<image_id>.mha`. The answer is a binary mask, 0 background and 1 tumor, in the current input grid. Here the CSV and MHA mask are empty schema illustrations, not files produced by an agent.

## Evaluation

The pinned grader defines Dice, 5-mm Surface Dice, HD95, MASD and tumor-volume RMSE. It resizes shape-mismatched predictions by nearest neighbor, reads physical spacing from the **prediction** MHA for surface/volume metrics, and does not compare affine, origin or direction equality. Consequently an array score would not by itself prove physical alignment. No metric result is reported. Inference time matters in the radiotherapy workflow, but the pinned ReX grader does not measure it.

## Visual explanation

A unitless grid shows voxel-index selection, the symbolic MHA index-to-world formula, and an empty same-grid output socket. This is a document-pinned contract illustration, not a source MRI or synthetic patient. The private-reference chapter explains role and label semantics only; there is no reference asset.

## Sources

- [Official restricted PANTHER record](https://zenodo.org/records/15192302)
- [Pinned ReX Task 2 description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/panther-task2/description.md)
- [Pinned ReX Task 2 preparer](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/panther-task2/prepare.py)
- [Pinned ReX Task 2 grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/panther-task2/grade.py)

## Gaps

No task-matched MRI, native MHA geometry, training label, held-out case, prediction or score is available locally. The official record lists CC-BY-NC-4.0 and no redistribution for granted files, while the pinned ReX config says CC BY-NC-SA 4.0; these terms are not reconciled here. Source-derived patient views require approved access, exact file/case hashes and verified split roles. The diagrams remain symbolic even though their contract is pinned to source code.
