# Locate and label dental findings in a panoramic radiograph

Develop a method that searches panoramic dental X-rays, places boxes around relevant tooth findings, and assigns each box a quadrant, tooth enumeration and diagnosis. These spatial labels support structured review; they do not independently establish a clinical diagnosis.

> **Mixed illustration:** actual source X-ray and reader-only annotation are retained; no ReX prediction or validated AP result is available. Acquire originals through [official DENTEX](https://zenodo.org/records/7812323).

## Given

### Original data

The pinned [ReX-MLE DENTEX adapter](https://github.com/rajpurkarlab/ReX-MLE/tree/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/dentex) uses the fully annotated stage of the [official DENTEX archive](https://zenodo.org/records/7812323), CC-BY-4.0. It shuffles **705 source images** with Python seed 42 into **564 public training** and **141 private-label test** images. Other partially annotated and unlabeled source material may be training context but is not the worked split's test reference. The pinned image `train_266.png` is a **1976 × 976** public ReX test input. Its **five source annotation boxes** are private ReX test targets and appear only after reader reveal.

### Supplied helpers

The method may use permitted training data and task tools.

### Reference-only material
 It must not receive the private test boxes as solver help. Local recovery of the public original archive for this explanation does not establish runtime access to ReX private answer paths; no external task execution was performed.

## Task specification

Search the full image, encode each candidate as COCO `[x,y,width,height]` in top-left source pixels, then attach `category_id_1` (quadrant), `category_id_2` (tooth enumeration), `category_id_3` (diagnosis), and `score`.

## Expected output

Submit `submission/submission.csv` with `image_id,predictions_json`; the worked row is `train_266,predictions/train_266.json`. The referenced per-image JSON is an **empty schema example**, not a prediction. Source category IDs remain zero-based.

## Evaluation

The pinned grader computes separate COCO AP-family measures for quadrant, enumeration and diagnosis, then derives mean AP. **Its category mapping is unresolved:** source ID ranges are 0–3, 0–7 and 0–3, while grader category declarations are 1–4, 1–8 and 1–4 without remapping ground truth IDs. Do not interpret an AP until that scorer discrepancy is checked. No model, judge, score or clinical performance claim is supplied here.

## Visual explanation

The explainer starts with the real unmarked radiograph and ReX split, then a pixel-coordinate localization ruler and the empty hierarchical output record. A deliberate reader action reveals all five original boxes in dashed amber with source ID/name labels. A final table contrasts source IDs with scorer IDs. The boxes are source references, never model detections. The original DENTEX challenge partitions are distinct from the pinned ReX split used here.

## Sources

Source: [DENTEX Zenodo record 7812323](https://zenodo.org/records/7812323); pinned [ReX-MLE prepare and grading adapters](https://github.com/rajpurkarlab/ReX-MLE/tree/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/dentex). Local recovery and hashes are in the task source-resolution receipt. Resolve the category-ID mismatch with a focused scorer fixture before numeric AP claims; a separately authorized task execution would be needed for any model result or runtime visibility finding.
