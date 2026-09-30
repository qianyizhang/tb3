# Assemble a chest CT report through specialist tools

Assemble a chest CT report through specialist tools. The worked view is a symbolic protocol with no patient image; no task run or evaluation was performed.

## Given

### Original data

The pinned agent source defines a nine-item checklist and ten specialist tools. No native CT, saved tool result, generated report or matched reference report is retained.

### Supplied helpers

Pinned task instructions, prompts, runtime contracts and helper descriptions are retained, but no case-specific helper output is available.

### Callable tools

The pinned task permits source-specific terminal or specialist tools under its task conditions. This explanation runs no model, image preparer, grader or learned metric.

### Reference-only material

The paired clinical report is read separately by report evaluation, not placed in the initial minimal-inference request.

## Task specification

The v8c prompt directs a report_generation_tool draft first, then checks across nine checklist areas using specialist tools and resolution of contradictions. No saved trace establishes an actual sequence. The tool description instead suggests drafting after region checks; this source conflict remains explicit.

## Expected output

final assistant JSON action with answer string; single-case CLI streams the interaction trace. No prediction or final answer was created for this pack.

## Evaluation

Separate offline CT-RATE metrics include BLEU-1, ROUGE-L, CIDEr, GREEN and RadBERT-derived labels. Full-orchestrator learned reward is optional; minimal-batch reward 0.0 is placeholder metadata. CIDEr is skipped for a single paired case. No metric was run.

## Visual explanation

The first view presents only a labeled empty input socket. The operation is then shown through a task-specific empty workflow. The required output schema remains empty; private reference stays unavailable.

## Difficulty

CT-RATE is gated; the audited source tree contains no worked NIfTI, tool trace or report. No report text or metric is invented.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Minimal single-case inference | Ten tools and the v8c checklist | Inspect the CT, reconcile tool findings and return the final report/trace. |
| CT-RATE batch inference | Same workflow plus a split manifest | Produce per-case traces; account separately for failures, absent outputs and report quality. |

## Coverage

Report generation · CT-RATE multiple-choice VQA · tool ablations. This anchor covers reporting only.

## Sources

- [Pinned task contract](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/minimal_inference/README.md).
- [Official data acquisition](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE).
- [Source resolution receipt](../sources/radagent-resolution.json).
