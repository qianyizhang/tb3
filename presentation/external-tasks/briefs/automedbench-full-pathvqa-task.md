# Answer questions about pathology images

Build and run a pipeline to answer questions about pathology images.

## Value

A focused image question tests visual interpretation and answer formatting without requiring a complete report.

## Given

### Original data

question.json containing the question, referenced image paths and, for multiple-choice tasks, answer options. Dataset: PathVQA.

### Supplied helpers

Task configuration, label/output conventions and stage-specific guidance. Lite names microsoft/llava-med-v1.5-mistral-7b. Standard supplies candidates to investigate; model files may still need provisioning.

### Callable tools

A terminal, staged public data and task-specific ML libraries/model loaders; VQA tasks additionally document inspection and answer-submission helpers.

### Reference-only material

Private labels or reference images belong to evaluation. The manifest declares dataset.included=false; small package download does not establish that the operator has staged any images.

## Task specification

Complete the source’s plan, setup, validation, inference and submission stages. Use the selected tier’s task-specific training/model restrictions and preserve the declared data split. Full-release package ID: pathvqa-task.

## Expected output

Write `{question_id}/answer.json`. Keep predicted_label empty; predicted_answer is a concise normalized phrase or exactly yes/no for binary questions.

## Evaluation

Answer correctness uses the task’s multiple-choice or normalized open-ended evaluator; these are separate answer modes. Planning/setup/validation artifacts are distinct from final prediction quality. The evaluator was not run for this brief.

## Visual explanation

### Workflow

- Staged images + task guidance
- Plan → set up → validate → infer
- Submit the task-specific prediction artifact

### Input

**Contract view; native sample not yet illustrated.** question.json containing the question, referenced image paths and, for multiple-choice tasks, answer options. Dataset: PathVQA.

### Supplied helpers

**Given material, not an answer reveal.** Task configuration, label/output conventions and stage-specific guidance. Lite names microsoft/llava-med-v1.5-mistral-7b. Standard supplies candidates to investigate; model files may still need provisioning.

### Reference or output

**Expected artifact, not an actual prediction.** Write `{question_id}/answer.json`. Keep predicted_label empty; predicted_answer is a concise normalized phrase or exactly yes/no for binary questions.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: microsoft/llava-med-v1.5-mistral-7b. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Pair each question with all required images and map the decoded answer to the exact output schema; medical language alone is insufficient.

## Sources

- [Pinned Full-release task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/pathvqa-task.tar.gz)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Native sample views are not attached to this Full-release definition. The downloaded archive is a task harness, not the image dataset or model weights.
