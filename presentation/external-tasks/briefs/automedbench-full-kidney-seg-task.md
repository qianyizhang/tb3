# Segment kidney and lesion on CT

The task requests a segmentation from CT. This explainer shows the input or contract boundary and **no completed model result**.

## Given

### Original data

Official KiTS19 case_00000 CT, 611 × 512 × 512 voxels at 0.5 × 0.919921875 × 0.919921875 mm along native i×j×k. Three fixed curated teaching planes at native i=288, 311 and 344 use WL 40 / WW 400 HU. Their selection method is undocumented; they do not establish unbiased sampling. Full staged-case membership is unverified.

### Supplied helpers

The exact Full harness specifies ct.nii.gz and separate organ and lesion outputs. A released KiTS19 source label is held back from the input scene and revealed only to the reader. It is not Full private ground truth.

### Callable tools

The Full task harness and environment define file submission and a 3,600-second task budget. No model, preparer, grader or clinical tool is run for this explanation.

### Reference-only material

An explicit reader reveal can show the public KiTS19 source annotation and a source-only two-mask conversion. It is not a participant prediction or Full private reference.

## Task specification

Organ and lesion occupy two files. The source annotation is an oracle format example only. The retained KiTS19 CT/source label and curated planes do not prove Full staged-case or private-GT identity. Source-label counts stay behind the reader reveal. The Full package also flags an output-directory mismatch.

## Expected output

Write separate binary agents_outputs/{case_id}/organ.nii.gz and lesion.nii.gz on the CT grid. The pinned Full config does not define whether organ must include lesion tissue; do not infer that overlap from the public KiTS19 label. No participant output is retained. The task requires both files even though the formatter treats a missing mask as incomplete rather than malformed.

## Evaluation

The task manifest requires both binary files. The formatter checks exact 0/1 values but treats absent files as incomplete coverage and checks `organ.nii.gz` only when present; the Dice scorer instead thresholds at >0.5. Mean lesion Dice determines the medal tier, while the separate clinical score averages organ and lesion Dice equally and is weighted by completion for partial submissions. Shape is checked, not affine. No score was computed here.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: nnU-Net v2 (KiTS19 3d_lowres). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Sources

- [Exact pinned AutoMedBench Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/tree/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation)
- [Official upstream acquisition route](https://github.com/neheller/kits19)

## Visual explanation

### Input

Actual upstream CT and a distinct released source annotation, not verified Full staging.

### Supplied helpers

Source-defined label names and output paths are contract text. No source annotation is supplied to a Full solver by this pack.

### Reference or output

The requested output slots are empty. An explicit reader reveal can show the public KiTS19 source annotation and a source-only two-mask conversion. It is not a participant prediction or Full private reference.

### Workflow

- Inspect the actual public input or abstract grid and its source warning.
- Map label IDs and required output files without filling a prediction.
- Read scorer boundaries and reference availability.
