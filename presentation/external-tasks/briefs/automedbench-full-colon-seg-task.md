# Segment primary colon cancer in CT

Segment a 3D abdominal CT into the task's integer labels. The worked material is one official upstream training example; no Full evaluation was run.

## Given

### Original data

The Full package expects `public/{case_id}/ct.nii.gz` under its named data root and declares `dataset.included=false`. Official MSD Task10_Colon training CT colon_219 and matching tumor label, 512×512×137 voxels. The displayed source is not confirmed as a prepared Full case.

### Supplied helpers

Task configuration and Lite/Standard method guidance are available. The pinned task's target codebook is 0 background, 1 primary colon cancer. The upstream training label is shown only to the reader after a reveal; it was not supplied as the answer for this Full case.

### Callable tools

The Full workflow permits environment setup, validation and inference. No model, preparer, controller or scorer ran for this explanation.

### Reference-only material

Private Full masks belong to the evaluator. The pack contains upstream public training annotations for reader-only teaching, not Full private labels.

## Task specification

Inspect three preselected native CT planes without a mask. This post-hoc teaching selection does not test finding the tumor in a whole volume; the task target is the primary tumor, not colon organ. The output must be a combined 3D integer NIfTI on each Full input grid; the upstream example has its own native grid, and a 2D screenshot is only a teaching view.

## Expected output

Write `agents_outputs/{case_id}/dseg.nii.gz` for each case. Valid IDs are 0 background, 1 primary colon cancer. The task calls for a 3D integer map. The formatter checks rounded unique values against allowed IDs and compares shape only if the input scan is present; it does not separately enforce integer voxels, three dimensions, or affine equality. Preserve the input affine for coherent physical geometry. No output file or result is in this pack.

## Evaluation

Foreground Dice on class 1. Both-empty masks yield 1.0 in the pinned scorer. The saved artifact is a scoring contract, not an observed Dice value.

## Visual explanation

An unmarked source slice comes first. Three sampled native-k planes are inspected, then the exact label codebook and empty output path appear. Only explicit reader reveal mounts matching upstream source labels.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: MONAI VISTA3D (label_prompt=[27], colon-cancer primaries). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

The upstream training pair was recovered by verified byte ranges from official AWS tar. Full 20-case selection and private evaluator reference are not established.

## Sources

- [Pinned Full task harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation/colon-seg-task.tar.gz).
- [Official upstream source](https://msd-for-monai.s3-us-west-2.amazonaws.com/Task10_Colon.tar) (CC BY-SA 4.0).
- [Source resolution receipt](../sources/automedbench-full-colon-seg-task-resolution.json).
