# Segment the left atrium in cardiac MRI

Build and run a pipeline to segment the left atrium in cardiac MRI.

## Value

Spatial labels support measurement and anatomical review; organ overlap and lesion detection are different capabilities.

## Given

### Original data

MRI input, stored as `mri.nii.gz` per case.

### Supplied helpers

Task configuration, label/output conventions and stage-specific guidance. Lite names nnU-Net v2 (MSD Task02_Heart pretrained). Standard supplies candidates to investigate; model files may still need provisioning.

### Callable tools

A terminal, staged public data and task-specific ML libraries/model loaders; VQA tasks additionally document inspection and answer-submission helpers.

### Reference-only material

Private labels or reference images belong to evaluation. The manifest declares dataset.included=false; small package download does not establish that the operator has staged any images.

## Task specification

Complete the source’s plan, setup, validation, inference and submission stages. Use the selected tier’s task-specific training/model restrictions and preserve the declared data split. Full-release package ID: heart-seg-task.

## Expected output

Write `agents_outputs/{case_id}/dseg.nii.gz`. Labels: 1=heart; 0=background.

## Evaluation

The configuration describes foreground Dice overlap, with task-specific class aggregation. Organ/lesion tasks require both outputs; inspect the selected evaluator for their exact weighting. Planning/setup/validation artifacts are distinct from final prediction quality. The evaluator was not run for this brief.

## Visual explanation

### Workflow

- Staged images + task guidance
- Plan → set up → validate → infer
- Submit a label map

### Input

**Contract view; native sample not yet illustrated.** MRI input, stored as `mri.nii.gz` per case.

### Supplied helpers

**Given material, not an answer reveal.** Task configuration, label/output conventions and stage-specific guidance. Lite names nnU-Net v2 (MSD Task02_Heart pretrained). Standard supplies candidates to investigate; model files may still need provisioning.

### Reference or output

**Expected artifact, not an actual prediction.** Write `agents_outputs/{case_id}/dseg.nii.gz`. Labels: 1=heart; 0=background.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: nnU-Net v2 (MSD Task02_Heart pretrained). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Choose a model that covers the requested structures, preserve physical geometry and map class IDs correctly. A general organ segmenter may miss the target lesions.

## Sources

- [Pinned Full-release task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation/heart-seg-task.tar.gz)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Native sample views are not attached to this Full-release definition. The downloaded archive is a task harness, not the image dataset or model weights.
