# Decide which findings are present in a chest CT

Inspect one 3D scan and answer yes or no for every requested abnormality.

## Value

Finding specific abnormalities is one component of reading a chest CT. This task scores labels, not a complete clinical report.

## Given

### Original data

One non-contrast chest CT volume (NIfTI).

### Supplied helpers

A scan-specific list of 4–12 findings to assess; no lesion coordinates are specified in the inspected prompt.

### Callable tools

Terminal, internet and installable libraries. Published patient labels/reports must not be looked up.

### Reference-only material

Gold labels are evaluator material. The inspected prompt prohibits looking up the source patient report or labels.

## Task specification

Use the supplied volume; answer every listed finding within one hour.

## Expected output

predictions.txt: one exact label name and yes/no answer per line.

## Evaluation

All requested labels must match for binary reward 1. Per-label diagnostics do not change that reward.

## Visual explanation

### Workflow

- 3D chest CT
- Inspect requested findings
- Yes / no per label

### Input

Exact CT-RATE case valid_16_a_1 returned HTTP 401 on 2026-09-21: accepted dataset access and authentication are required. No unrelated CT has been substituted.

### Supplied helpers

The requested-label list is generated during data staging. Its exact case-specific content has not been retrieved.

### Reference or output

No source report, gold labels or agent result was downloaded.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Published CT task | Requested-label list | Inspect the volume and classify every requested finding. |

## Difficulty

The label list narrows what to assess, but the agent must choose how to inspect the volume. One wrong finding loses the task reward.

## Sources

- [Exact task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ct_abnormality_valid_16_a_1/instruction.md)
- [Evaluator](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ct_abnormality_valid_16_a_1/tests/harbor_evaluator.py)

- [Dataset and access terms](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE)
- [Sample download and rendering receipt](../samples.json)

## Coverage

Also: CXR correction, pathology and other healthcare terminal tasks. This preview only inspects the CT example.

## Gaps

Access blocker: CT-RATE requires accepted terms in a Hugging Face account and authenticated retrieval. The exact URL and response are retained in the sample receipt.

## Cases

The scan and requested finding list change between cases. Their contents are not loaded here.
