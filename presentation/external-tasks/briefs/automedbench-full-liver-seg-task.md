# Segment liver and lesion on CT

The task requests a segmentation from CT. This explainer shows the input or contract boundary and **no completed model result**.

## Given

### Original data

Official MSD Task03 Liver public training CT liver_53, 512 × 512 × 105 voxels at 0.85 × 0.85 × 4 mm. Fixed native k=26, 52 and 79 CT planes retain WL 40 / WW 400 HU. A fourth k=64 teaching plane is appended after examining the public label and choosing the plane with most source label-2 voxels (lower-index tie break). This is post-hoc label-guided illustration, not unbiased input sampling or evidence of a Full staged case.

### Supplied helpers

The exact Full harness specifies ct.nii.gz and separate organ and lesion outputs, but declares LiTS as source while its script uses MSD Task03. No dataset images are included in the harness.

### Callable tools

The Full task harness and environment define file submission and a 3,600-second task budget. No model, preparer, grader or clinical tool is run for this explanation.

### Reference-only material

The official matched MSD Task03 training annotation is available only after explicit reader reveal. It is not Full private ground truth or a participant output.

## Task specification

The task declares two binary submission files. The release gate flags a staging output-directory mismatch, and its declared LiTS source conflicts with the MSD Task03 script. This MSD teaching CT now has its matched public training label, but its Full identity is unverified.

## Expected output

Write separate binary agents_outputs/{case_id}/organ.nii.gz and lesion.nii.gz on the CT grid. The pinned Full config does not define an organ–lesion overlap rule, and the public MSD source-only conversion does not establish that Full rule. No participant output is retained. The task requires both files even though the formatter treats a missing mask as incomplete rather than malformed.

## Evaluation

The task manifest requires both binary files. The formatter checks exact 0/1 values but treats absent files as incomplete coverage and checks `organ.nii.gz` only when present; the Dice scorer instead thresholds at >0.5. Mean lesion Dice determines the medal tier, while the separate clinical score averages organ and lesion Dice equally and is weighted by completion for partial submissions. Shape is checked, not affine. No score was computed here.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: MONAI VISTA3D. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Sources

- [Exact pinned AutoMedBench Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/tree/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation)
- [Official upstream acquisition route](https://msd-for-monai.s3-us-west-2.amazonaws.com/Task03_Liver.tar)

## Visual explanation

### Input

Actual MSD upstream CT with three fixed planes plus one disclosed public-label-guided teaching plane; Full staging and provenance remain unresolved.

### Supplied helpers

Source-defined label names and output paths are contract text. The matched public source annotation stays reader-only; it is not supplied to a Full solver by this pack.

### Reference or output

The requested output slots are empty. Reader reveal shows the matched public source label on all four CT planes. The fourth plane was chosen post-hoc from the public label to make the lesion target inspectable; it is not evidence of Full performance. Source labels 1 or 2 form a teaching organ mask and label 2 a teaching lesion mask; neither conversion is verified for Full private ground truth.

### Workflow

- Inspect the actual public input or abstract grid and its source warning.
- Map label IDs and required output files without filling a prediction.
- Read scorer boundaries and reference availability.
