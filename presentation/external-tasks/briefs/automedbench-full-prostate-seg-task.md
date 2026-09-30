# Label prostate zones on two-channel MRI

Segment MSD Task05 prostate MRI according to the pinned Full task. This explanation uses an official upstream training example; no Full evaluation was run.

## Given

### Original data

Full expects `public/{case_id}/mri.nii.gz` in its named data root; `dataset.included=false`. Official upstream training image prostate_00 is 320×320×15×2: channel 0 T2-weighted, channel 1 ADC. Its matching 3D label has IDs 0,1,2 and native RAS geometry. Its 0.6×0.6×4 mm grid is oblique RAS; the image/label affine difference is 1.526e-5 mm (header precision). It is not verified as a Full staged case.

### Supplied helpers

The pinned task package contains Lite and Standard guidance, configuration and output conventions. The official MSD training annotation is an upstream helper and is shown only after a reader reveal; it was not the Full case answer.

### Callable tools

The Full workflow permits planning, setup, validation and inference using task-specific libraries and models. No model, source preparer, controller or evaluator ran for this explanation.

### Reference-only material

Private Full masks remain with the evaluator and are unavailable here. The upstream training label is not a Full private target.

## Task specification

Read paired T2 and ADC values at each native i,j,k. Assign one mutually exclusive 3D class: background 0, peripheral zone 1, transition zone 2. This is zonal anatomy, not cancer detection. Preserve a 3D spatial grid; the displayed diagrams or slices are teaching views, not submitted masks.

## Expected output

Write agents_outputs/{case_id}/dseg.nii.gz. One combined dseg.nii.gz uses 0 background, 1 peripheral zone and 2 transition zone. The task requires integer IDs 0/1/2. The formatter rounds unique values before checking membership and compares leading spatial dimensions for the 4D input/3D output only if the input exists. Missing files count as incomplete; affine equality is not checked. Preserve the input affine for physical alignment. No output file or prediction is retained.

## Evaluation

Formatter and scorer round values; task contract requires integer IDs0/1/2. The scorer averages both foreground classes across valid available pairs, includes both-empty class Dice1 and shape-error zeros, then averages class means. Aggregate scales Dice by completed-pair fraction and blends workflow/clinical equally; medal uses unscaled macro Dice. Separated private masks are fused with higher class ID winning overlaps; missing class files contribute no foreground if another class exists. No score was run. These describe the pinned evaluator, not measured quality.

## Visual explanation

The input is unmarked first. Native planes k=2,5,8 were selected after inspecting the public training label; this is not blind localization. T2 and ADC use separate source-volume 1st–99.5th percentile display windows, not shared calibrated units. The next scenes show the paired T2/ADC channels, then the zonal codebook. Output files remain empty. An explicit helper reveal shows the upstream training zones, not private Full truth.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: nnU-Net v2 (MSD Task05_Prostate pretrained). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

The official upstream training label is helper material. Full 20-case membership and evaluator-only masks are unverified; no prediction or score is retained.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation/prostate-seg-task.tar.gz).
- [Official upstream source](https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar) (CC BY-SA 4.0).
- [Source resolution receipt](../sources/automedbench-full-prostate-seg-task-resolution.json).
