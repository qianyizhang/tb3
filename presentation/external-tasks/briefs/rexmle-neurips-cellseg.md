# Separate individual cells in microscopy

Develop and apply a method that gives each cell a distinct instance ID on a microscopy image. A binary foreground mask alone does not separate touching cells. The source labels support method development, not a demonstrated clinical or model result.

## Given

### Original data

Microscopy images from the [official NeurIPS CellSeg archive](https://zenodo.org/records/10719375), reported under CC-BY-NC-ND-4.0. The worked source image `cell_00944.png` is an actual **512 × 512 RGB Training-labeled patch**. It is expected to be public train under a reconstructed ReX split, not a held-out case.

### Supplied helpers

The matching source `cell_00944_label.tiff` is a **training annotation** on the same pixel grid: background 0 and **36 distinct positive instance IDs** covering 8,479 of 262,144 pixels. IDs distinguish cells, not cell types. Pinned ReX preparation combines 1,000 Training-labeled and 101 Tuning pairs, then seeds an 80/20 split expected to yield **880 public train / 221 private-label test**. That split was reconstructed from pinned code and source IDs; the preparer was not executed. Original Testing and unlabeled archives are not copied into the prepared public/test set by this adapter.

### Callable tools

The task environment supports model development and mask-file submission, but no method, training, inference or grader was run for this explanation.

### Reference-only material

Held-out ReX test labels and grading CSV are evaluator material, not solver inputs. No exact held-out case or private evaluator mask is retained here. The displayed TIFF is supplied **public-training help**, not a hidden test answer.

## Task specification

For each held-out image, segment cells as separate instances while preserving its 2D pixel grid. A submitted integer mask uses **0 background** and a distinct positive ID for each predicted cell. The source label may teach this structure; it is not a prediction. The pinned ReX adapter's prepared scope is narrower than the original challenge archive, and actual runtime visibility has not been audited.

## Expected output

Write `submission/submission.csv` with the exact columns `image_id,predicted_mask_path`. Each row points to an instance-mask TIFF such as `predictions/<image_id>_label.tiff`. The explainer shows only an empty row template and output socket; it has no retained predicted mask.

## Evaluation

The pinned [grader](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/neurips-cellseg/grade.py) computes pairwise cell IoU, one-to-one Hungarian matching, and instance F1 at thresholds **0.5, 0.6, 0.7, 0.8 and 0.9**. It removes cells touching the outer **2-pixel** margin before instance matching and uses **2000 × 2000** regions for images with **at least 25 million pixels**; the 512² worked patch would use its direct branch if scored. It nearest-neighbor resizes shape-mismatched predictions. These are code-defined operations, not a score for this image; no F1 is claimed.

## Visual explanation

The first view is the unmarked real image. A later **supplied-helper reveal** overlays the real training label with a color legend. Binary foreground and separate instance IDs are compared on that same source pair, including one selected source cell. The held-out image and answer remain absent while the empty output schema and symbolic scorer pipeline explain the task.

## Sources

- [Official CellSeg Zenodo record](https://zenodo.org/records/10719375), CC-BY-NC-ND-4.0; source image/label byte-range and CRC receipts are in the resolution record.
- [Pinned ReX-MLE CellSeg adapter](https://github.com/rajpurkarlab/ReX-MLE/tree/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/neurips-cellseg).

## Gaps

No full source archive, executed ReX prepared directory, held-out image, private label, prediction, grader result or visual acceptance is retained. An authorized source-matched prepared test case and actual output would be needed for a result explainer. This local source interpretation does not imply permission to redistribute derivative imagery.
