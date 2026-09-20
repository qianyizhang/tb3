# Classify pediatric X-rays as normal or pneumonia

Build and run a pipeline to classify pediatric X-rays as normal or pneumonia.

## Value

A fixed taxonomy makes image-level decisions easy to score, while hiding localization and uncertainty unless separately requested.

## Given

### Original data

radiography input, stored as `image.jpg` per case.

### Supplied helpers

Task configuration, label/output conventions and stage-specific guidance. Lite names torchvision DenseNet-121. Standard supplies candidates to investigate; model files may still need provisioning.

### Callable tools

A terminal, staged public data and task-specific ML libraries/model loaders; VQA tasks additionally document inspection and answer-submission helpers.

### Reference-only material

Private labels or reference images belong to evaluation. The manifest declares dataset.included=false; small package download does not establish that the operator has staged any images.

## Task specification

Complete the source’s plan, setup, validation, inference and submission stages. Use the selected tier’s task-specific training/model restrictions and preserve the declared data split. Full-release package ID: chest-xray-pneumonia-cls-task.

## Expected output

Write `agents_outputs/predictions.csv`; alternatively `agents_outputs/{case_id}/prediction.json`. Use exactly one canonical class label per case: normal, pneumonia.

## Evaluation

Configured headline metric: accuracy. Planning/setup/validation artifacts are distinct from final prediction quality. The evaluator was not run for this brief.

## Visual explanation

### Workflow

- Staged images + task guidance
- Plan → set up → validate → infer
- Submit the task-specific prediction artifact

### Input

**Contract view; native sample not yet illustrated.** radiography input, stored as `image.jpg` per case.

### Supplied helpers

**Given material, not an answer reveal.** Task configuration, label/output conventions and stage-specific guidance. Lite names torchvision DenseNet-121. Standard supplies candidates to investigate; model files may still need provisioning.

### Reference or output

**Expected artifact, not an actual prediction.** Write `agents_outputs/predictions.csv`; alternatively `agents_outputs/{case_id}/prediction.json`. Use exactly one canonical class label per case: normal, pneumonia.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: torchvision DenseNet-121. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Match the source class semantics and input normalization. A plausible label in the wrong taxonomy is still incorrect.

## Sources

- [Pinned Full-release task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/classification/chest-xray-pneumonia-cls-task.tar.gz)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Native sample views are not attached to this Full-release definition. The downloaded archive is a task harness, not the image dataset or model weights. The source has not frozen all evaluation/sample identifiers.
