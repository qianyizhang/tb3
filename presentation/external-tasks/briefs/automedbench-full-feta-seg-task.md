# Label seven fetal-brain tissues in T2 MRI

Segment a 3D fetal T2-weighted super-resolution MRI into the task's integer labels. The worked material is a symbolic protocol only; no Full evaluation was run.

## Given

### Original data

The Full package expects `public/{case_id}/t2w.nii.gz` under its named data root and declares `dataset.included=false`. No native source image is retained; official Zenodo metadata report restricted files and a Synapse access route. No native image is shown.

### Supplied helpers

Task configuration and Lite/Standard method guidance are available. The pinned task's target codebook is 0 background; 1 eCSF, 2 GM, 3 WM, 4 LV, 5 CBM, 6 SGM, 7 BS. No source training label was acquired.

### Callable tools

The Full workflow permits environment setup, validation and inference. No model, preparer, controller or scorer ran for this explanation.

### Reference-only material

Private Full masks belong to the evaluator. No reference file is retained or revealable.

## Task specification

Describe mapping each voxel into one of seven mutually exclusive tissue IDs on the native 3D input grid. No numeric anatomy is drawn without an authorized image. The output must be a combined 3D integer NIfTI on each Full input grid; no authorized source image or 2D slice is available in this pack.

## Expected output

Write `agents_outputs/{case_id}/dseg.nii.gz` for each case. Valid IDs are 0 background; 1 eCSF, 2 GM, 3 WM, 4 LV, 5 CBM, 6 SGM, 7 BS. The task calls for a 3D integer map. The formatter checks rounded unique values against allowed IDs and compares shape only if the input scan is present; it does not separately enforce integer voxels, three dimensions, or affine equality. Preserve the input affine for coherent physical geometry. No output file or result is in this pack.

## Evaluation

Pinned multiclass scorer computes foreground-class Dice and macro mean; no case or class result was produced. The saved artifact is a scoring contract, not an observed Dice value.

## Visual explanation

An empty image socket comes first. An authored i/j/k wireframe then illustrates a moving sampling plane, with unknown native geometry and no anatomy or inferred labels. The literal output codebook and empty output path follow; no source or private reference is available.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: AutoFetal7-nnUNet (nnU-Net v2, FeTA-trained). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

FeTA access requires its research/education agreement through the official route. Neither input image, source label, Full private reference, prediction nor score is present.

## Sources

- [Pinned Full task harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation/feta-seg-task.tar.gz).
- [Official upstream source](https://zenodo.org/records/4541606) (restricted research and education agreement).
- [Source resolution receipt](../sources/automedbench-full-feta-seg-task-resolution.json).
