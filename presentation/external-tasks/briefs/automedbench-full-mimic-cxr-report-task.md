# Write chest X-ray findings from one or more views

Build and run a pipeline to write chest X-ray findings from one or more views.

## Value

Image-grounded text can make observations accessible to a reader, but fluent wording does not establish factual accuracy.

## Given

### Original data

Case images under the staged `images/` directory; the task configuration names the source dataset and allowed views.

### Supplied helpers

Task configuration and report-generation model candidates. Even Lite asks the agent to compare suitable public pipelines; it is not a fixed-checkpoint condition.

### Callable tools

A terminal, staged public data and task-specific ML libraries/model loaders; VQA tasks additionally document inspection and answer-submission helpers.

### Reference-only material

Private labels or reference images belong to evaluation. The manifest declares dataset.included=false; small package download does not establish that the operator has staged any images.

## Task specification

Complete the source’s plan, setup, validation, inference and submission stages. Use the selected tier’s task-specific training/model restrictions and preserve the declared data split. Full-release package ID: mimic-cxr-report-task.

## Expected output

Write `agent_outputs/{case_id}/report.txt`.

## Evaluation

The lightweight report backend combines observation F1 (0.7) and report similarity (0.3). Planning/setup/validation artifacts are distinct from final prediction quality. The evaluator was not run for this brief.

## Visual explanation

### Workflow

- Staged images + task guidance
- Plan → set up → validate → infer
- Submit the task-specific prediction artifact

### Input

**Contract view; native sample not yet illustrated.** Case images under the staged `images/` directory; the task configuration names the source dataset and allowed views.

### Supplied helpers

**Given material, not an answer reveal.** Task configuration and report-generation model candidates. Even Lite asks the agent to compare suitable public pipelines; it is not a fixed-checkpoint condition.

### Reference or output

**Expected artifact, not an actual prediction.** Write `agent_outputs/{case_id}/report.txt`.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Candidate report-generation methods, rather than one fixed checkpoint. | Compare suitable pipelines, select one and validate findings-only generation. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Reconcile the model’s preprocessing with the source image scale and required output. An apparently reasonable image or text can still violate the task contract.

## Sources

- [Pinned Full-release task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/report/mimic-cxr-report-task.tar.gz)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Native sample views are not attached to this Full-release definition. The downloaded archive is a task harness, not the image dataset or model weights.
