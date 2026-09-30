# Decide requested findings on one chest CT

Decide requested findings on one chest CT. The worked view is a symbolic protocol with no patient image; no task run or evaluation was performed.

## Given

### Original data

The exact valid_16_a_1 CT and paired CT-RATE report require access. The case-specific labels.txt list derived from that report is also unavailable.

### Supplied helpers

The source supplies a scan-specific requested-label list only after report-derived staging; this list is absent.

### Callable tools

The pinned task permits source-specific terminal or specialist tools under its task conditions. This explanation runs no model, image preparer, grader or learned metric.

### Reference-only material

Report-derived gold.json and evidence sentences are evaluator-only; no actual gold was acquired.

## Task specification

For each supplied label name, inspect the 3D CT and write yes or no. The format examples in the prompt are not this patient’s requested list.

## Expected output

/workspace/submission/predictions.txt, one exact label: yes/no line per requested name. No prediction or final answer was created for this pack.

## Evaluation

Reward 1 only when all retained report-derived gold labels have matching parseable binary predictions; one wrong or missing answer yields 0. This is label agreement, not independent clinical diagnosis. Gold uses 17 report-phrase categories: present-only and absent-only matches are retained; both or neither are omitted. Missing or empty gold is a staging error, not a measured model failure.

## Visual explanation

The first view presents only a labeled empty input socket. The operation is then shown through a task-specific empty workflow. The required output schema remains empty; private reference stays unavailable. A three-name hypothetical matching control illustrates the all-labels reward rule without patient labels or yes/no answers.

## Difficulty

The exact CT, report, requested names, private gold and model prediction are missing. Unauthenticated HEAD returned HTTP 401 GatedRepo.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Published CT task | Requested-label list | Inspect the volume and classify every requested finding. |

## Coverage

Also: CXR correction, pathology and other healthcare terminal tasks. This preview only inspects the CT example.

## Sources

- [Pinned task contract](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ct_abnormality_valid_16_a_1/instruction.md).
- [Official data acquisition](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE).
- [Source resolution receipt](../sources/healthagentbench-resolution.json).
