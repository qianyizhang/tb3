# Build a kidney and lesion CT segmentation pipeline

Select and run a model on kidney CT volumes, then submit **two binary masks per patient**: kidney organ and lesion. This is a task explanation, not a completed model run.

## Given

### Original data

The task describes per-patient `ct.nii.gz` volumes. This explainer shows an actual recovered KiTS19 `case_00000` CT: **611 × 512 × 512** voxels, native I/P/L axes, spacing **0.5 × 0.919921875 × 0.919921875 mm**. Three axial planes are sampled after the fact for teaching; the solver must work from the whole volume.

### Supplied helpers

Lite names a KiTS19 checkpoint and supplies requirements and setup examples. Standard gives candidate model families and comparison guidance. Both assembled prompts include S3 one-patient validation. The named model is help, not a segmentation answer.

### Reference-only material

A matching released KiTS19 source annotation was recovered for this case. Its labels remain hidden until an explicit reader reveal. The original source map uses 1 for kidney and 2 for lesion; the task's requested binary organ target is **1 or 2**, while binary lesion is **2**. This label transformation illustrates output format only; it is not a saved prediction.

## Task specification

The condition calls for research, setup, one-patient validation, inference for all patients, and `submit_results`, with a configured **3,600-second** budget.

## Expected output

The output folder is `agents_outputs/<patient_id>/` with `organ.nii.gz` and `lesion.nii.gz`. Each mask is binary 0/1 and should preserve the CT shape and physical affine. `agents_decision.csv` is optional. The explainer renders the two output slots **empty** because no clinical prediction is retained.

## Evaluation

Organ and lesion Dice contribute equally in the deterministic score; lesion Dice averages evaluated cases with reference-positive lesions. Missing patient outputs trigger completeness handling. S1–S3 need a separate judge, which was not run. The runner quick check requires both masks, but the format helper treats organ as optional. Format shape/value checks and array Dice do not establish affine alignment: a retained nonclinical fixture shifts an artificial mask origin by 100 mm while preserving array Dice. Six fixtures use only two **8 × 8 × 8 artificial arrays**; none is a patient score.

## Gaps

The original AutoMedBench source audit verifies **35/35 pinned files**. The recovered CT and annotation have matching shape and affine and are used here under the source's CC-BY-NC-SA-4.0 terms for local noncommercial interpretation. The root recipe's `data/Kidney` location differs from the task loader's `data/CruzAbdomen_Kidney`; no staging execution reconciled the paths. There is no saved model inference, agent trace, judge result or clinical performance claim.

## Sources

- [Official AutoMedBench kidney task config](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/config.yaml)
- [Lite guidance](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/lite_s1.md) and [Standard guidance](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/standard_s1.md)
- [Official KiTS19 source](https://github.com/neheller/kits19) and [imaging dataset](https://huggingface.co/datasets/neheller/KiTS-Challenge-Imaging)
- [Pinned source audit](../sources/automed-kidney-audit.json) and [recovery receipt](../sources/automed-kidney-resolution.json)

## Visual explanation

### Workflow

Native CT alone → Lite/Standard assistance → five required stages → empty two-mask output schema → explicit private source-label reveal and oracle format mapping → separate nonclinical contract checks → limits. Cyan denotes released kidney reference; gold denotes released lesion reference. Neither color denotes a model prediction.
