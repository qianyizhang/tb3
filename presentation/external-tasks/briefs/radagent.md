# Write a chest CT report using specialist tools

Inspect a chest CT through specialist tools and assemble a report with an inspectable interaction trace.

## Value

The intended product summarizes imaging findings for a reader. Report quality and tool usage need separate evaluation.

## Given

### Original data

A chest CT scan, such as a CT-RATE case.

### Supplied helpers

Trained specialist backends can supply draft reports, disease predictions, organ/effusion segmentations and selected slices.

### Callable tools

CT and slice VQA, report generation, disease classification, segmentation, slice selection and windowing.

### Reference-only material

Reference reports/labels support evaluation; specialist-generated reports and classifications are assistance. Do not confuse those roles.

## Task specification

Given an image path, orchestrate tool calls and return a generated report. This is a system inference example, not a standalone frozen benchmark prompt.

## Expected output

Final report plus streamed JSON interaction trace; batch mode saves trajectories and failures.

## Evaluation

The project evaluates report and pathology-label performance. RadChest-CT lacks reference reports and therefore uses classification-based evaluation.

## Visual explanation

### Workflow

- Chest CT
- Consult and reconcile tools
- Report + interaction trace

### Input

The CT-RATE API reports gated access. A separate exact HealthAgentBench CT-RATE file request returned HTTP 401. RadAgent case retrieval has not been attempted with credentials.

### Supplied helpers

Specialist outputs need retained case-specific traces or a model run; none were generated for this survey.

### Reference or output

No actual tool-output or final-report example has been curated.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Tool-assisted report | Specialist model outputs and image-processing tools | Choose tools, reconcile findings and compose the final report. |

## Difficulty

The agent must reconcile several specialist outputs. Its capability depends partly on those models and checkpoints.

## Sources

- [System and tools](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/README.md)
- [Single-case inference interface](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/minimal_inference/README.md)

- [CT-RATE downloader](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/dataset_utils/CT-RATE/download_scripts/download_dataset.py)
- [Dataset and access terms](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE)
- [Sample download and rendering receipt](../samples.json)

## Coverage

Report generation · CT-RATE multiple-choice VQA · tool ablations. This anchor covers reporting only.

## Gaps

CT-RATE needs authorized account access. Actual specialist outputs and final report are a separate evidence gap: downloading CT alone does not supply them. No model run was launched.
