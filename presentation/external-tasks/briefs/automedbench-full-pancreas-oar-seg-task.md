# Label 21 structures around the pancreas

Build and run a pipeline to label 21 structures around the pancreas.

## Value

Spatial labels support measurement and anatomical review; organ overlap and lesion detection are different capabilities.

## Given

### Original data

CT input, stored as `ct.nii.gz` per case.

### Supplied helpers

Task configuration, label/output conventions and stage-specific guidance. Lite names VISTA3D (MONAI foundation model for 3D CT, 132 classes). Standard supplies candidates to investigate; model files may still need provisioning.

### Callable tools

A terminal, staged public data and task-specific ML libraries/model loaders; VQA tasks additionally document inspection and answer-submission helpers.

### Reference-only material

Private labels or reference images belong to evaluation. The manifest declares dataset.included=false; small package download does not establish that the operator has staged any images.

## Task specification

Complete the source’s plan, setup, validation, inference and submission stages. Use the selected tier’s task-specific training/model restrictions and preserve the declared data split. Full-release package ID: pancreas-oar-seg-task.

## Expected output

Write `agents_outputs/{case_id}/dseg.nii.gz`. Preserve scan geometry and map labels to the configuration’s integer taxonomy.

## Evaluation

The configuration describes foreground Dice overlap, with task-specific class aggregation. Organ/lesion tasks require both outputs; inspect the selected evaluator for their exact weighting. Planning/setup/validation artifacts are distinct from final prediction quality. The evaluator was not run for this brief.

## Visual explanation

### Workflow

- Staged images + task guidance
- Plan → set up → validate → infer
- Submit a label map

### Input

**Contract view; native sample not yet illustrated.** CT input, stored as `ct.nii.gz` per case.

### Supplied helpers

**Given material, not an answer reveal.** Task configuration, label/output conventions and stage-specific guidance. Lite names VISTA3D (MONAI foundation model for 3D CT, 132 classes). Standard supplies candidates to investigate; model files may still need provisioning.

### Reference or output

**Expected artifact, not an actual prediction.** Write `agents_outputs/{case_id}/dseg.nii.gz`. Preserve scan geometry and map labels to the configuration’s integer taxonomy.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: VISTA3D (MONAI foundation model for 3D CT, 132 classes). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Cover all 21 scored structures and preserve the source’s nonconsecutive label IDs; good pancreas overlap alone is insufficient.

## Sources

- [Pinned Full-release task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation/pancreas-oar-seg-task.tar.gz)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Native sample views are not attached to this Full-release definition. The downloaded archive is a task harness, not the image dataset or model weights.
