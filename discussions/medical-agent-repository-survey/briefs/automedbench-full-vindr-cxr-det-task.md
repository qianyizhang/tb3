# Draw boxes around chest X-ray abnormalities

Build and run a pipeline to draw boxes around chest X-ray abnormalities.

## Value

Localized boxes connect a finding to image evidence; they are coarser than a pixel-level segmentation.

## Given

### Original data

CXR input, stored as `image.png` per case.

### Supplied helpers

Task configuration, label/output conventions and stage-specific guidance. Lite names Single YOLOv5 detector fine-tuned on VinBigData / VinDr-CXR-style 14-class chest abnormality detection. Standard supplies candidates to investigate; model files may still need provisioning. The manifest explicitly lists external runtime assets; the small harness archive does not include them.

### Callable tools

A terminal, staged public data and task-specific ML libraries/model loaders; VQA tasks additionally document inspection and answer-submission helpers.

### Reference-only material

Private labels or reference images belong to evaluation. The manifest declares dataset.included=false; small package download does not establish that the operator has staged any images.

## Task specification

Complete the source’s plan, setup, validation, inference and submission stages. Use the selected tier’s task-specific training/model restrictions and preserve the declared data split. Full-release package ID: vindr-cxr-det-task.

## Expected output

Write `agents_outputs/{case_id}/prediction.json`. Each box records class, confidence, x1,y1,x2,y2 in original-image pixel coordinates.

## Evaluation

Detection matching uses the configured overlap threshold, 0.5 IoU; inspect the selected evaluator for final precision/recall aggregation. Planning/setup/validation artifacts are distinct from final prediction quality. The evaluator was not run for this brief.

## Visual explanation

### Workflow

- Staged images + task guidance
- Plan → set up → validate → infer
- Submit the task-specific prediction artifact

### Input

**Contract view; native sample not yet illustrated.** CXR input, stored as `image.png` per case.

### Supplied helpers

**Given material, not an answer reveal.** Task configuration, label/output conventions and stage-specific guidance. Lite names Single YOLOv5 detector fine-tuned on VinBigData / VinDr-CXR-style 14-class chest abnormality detection. Standard supplies candidates to investigate; model files may still need provisioning. The manifest explicitly lists external runtime assets; the small harness archive does not include them.

### Reference or output

**Expected artifact, not an actual prediction.** Write `agents_outputs/{case_id}/prediction.json`. Each box records class, confidence, x1,y1,x2,y2 in original-image pixel coordinates.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: Single YOLOv5 detector fine-tuned on VinBigData / VinDr-CXR-style 14-class chest abnormality detection. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Resize images for the model without losing small targets, then transform every predicted box back into source-image coordinates.

## Sources

- [Pinned Full-release task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/detection/vindr-cxr-det-task.tar.gz)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Native sample views are not attached to this Full-release definition. The downloaded archive is a task harness, not the image dataset or model weights.
