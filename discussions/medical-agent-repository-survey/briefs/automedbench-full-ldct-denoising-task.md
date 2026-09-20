# Denoise simulated low-dose CT slices

Build and run a pipeline to denoise simulated low-dose CT slices.

## Value

Restoration tests whether an image-processing pipeline preserves useful structure while reducing simulated noise or resolution loss.

## Given

### Original data

A 512×512 float32 CT slice in input.npy, with simulated low-dose noise and intensities in Hounsfield units.

### Supplied helpers

Task configuration, label/output conventions and stage-specific guidance. Lite names DRUNet (deep residual UNet denoiser). Standard supplies candidates to investigate; model files may still need provisioning.

### Callable tools

A terminal, staged public data and task-specific ML libraries/model loaders; VQA tasks additionally document inspection and answer-submission helpers.

### Reference-only material

Private labels or reference images belong to evaluation. The manifest declares dataset.included=false; small package download does not establish that the operator has staged any images.

## Task specification

Complete the source’s plan, setup, validation, inference and submission stages. Use the selected tier’s task-specific training/model restrictions and preserve the declared data split. Full-release package ID: ldct-denoising-task.

## Expected output

Write `agents_outputs/{case_id}/enhanced.npy`.

## Evaluation

Task-specific image-quality scoring compares predictions with private reference images; numerical scaling and shape are part of the contract. Planning/setup/validation artifacts are distinct from final prediction quality. The evaluator was not run for this brief.

## Visual explanation

### Workflow

- Staged images + task guidance
- Plan → set up → validate → infer
- Submit the task-specific prediction artifact

### Input

**Contract view; native sample not yet illustrated.** A 512×512 float32 CT slice in input.npy, with simulated low-dose noise and intensities in Hounsfield units.

### Supplied helpers

**Given material, not an answer reveal.** Task configuration, label/output conventions and stage-specific guidance. Lite names DRUNet (deep residual UNet denoiser). Standard supplies candidates to investigate; model files may still need provisioning.

### Reference or output

**Expected artifact, not an actual prediction.** Write `agents_outputs/{case_id}/enhanced.npy`.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: DRUNet (deep residual UNet denoiser). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Suppress noise while preserving structure and the required intensity units. Synthetic degradation differs from unknown real scanner noise.

## Sources

- [Pinned Full-release task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/enhancement/ldct-denoising-task.tar.gz)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Native sample views are not attached to this Full-release definition. The downloaded archive is a task harness, not the image dataset or model weights.
