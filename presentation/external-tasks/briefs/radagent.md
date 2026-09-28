# Write a chest CT report using specialist tools

Inspect a chest CT through specialist tools and assemble a report with an inspectable interaction trace.

## Value

The intended product summarizes imaging findings for a reader. Report quality and tool usage need separate evaluation.

## Given

### Original data

A chest CT NIfTI volume readable by the tool services. The pinned minimal-inference agent receives the request and image path as text; its specialist backends read the image. CT-RATE batch mode resolves paths from a report-generation manifest.

### Supplied helpers

The v8c prompt supplies a nine-item diagnosis checklist and descriptions of ten callable tools. Draft reports, pathology predictions and masks are generated assistance, not reference annotations. CT-Chat supplies the draft-report and whole-volume VQA backends; separate models support classification, segmentation and slice VQA.

### Callable tools

Whole-volume and slice VQA, draft-report generation, an 18-pathology classifier, anatomy and effusion segmentation, largest-mask and distributed-mask slice selection, whole-volume slice selection, and windowing. A shared MCP proxy forwards calls to the separate backends. Availability requires the corresponding model assets and services.

### Reference-only material

The minimal batch loader takes only the request and image identity from the manifest. Its scenarios omit the paired reference report. The separate metric reader loads that report for comparison. The full training implementation retains `gt` in the host scenario for reward computation; it is not inserted into the initial user message. These are source-level data-flow observations, not a runtime filesystem-isolation test.

## Task specification

Given an image path, orchestrate tool calls and return a generated report. The v8c prompt requests an initial draft, checklist coverage, additional checks of abnormalities, and reconciliation of disagreements. The minimal runtime allows up to 60 assistant steps and requests JSON actions: `call_tool` or `final_answer`. These instructions do not establish that any saved report followed them. This entry covers system inference, not a frozen benchmark submission.

## Expected output

The single-case CLI streams a JSON list of system/user, assistant and tool messages to stdout. The final assistant action contains an `answer` string. Batch mode writes per-case files under `trajectory/` or `fails/`; successful traces append `status: success` and `reward: 0.0`. That zero is placeholder metadata, not a measured report-quality score.

## Evaluation

CT-RATE evaluation compares generated and reference reports using BLEU-1, ROUGE-L, CIDEr and the learned GREEN scorer. A RadBERT classifier separately extracts 18 binary labels from both texts for classification metrics; these labels are model-derived. RadChest-CT lacks reference reports and instead joins generated-report classifications to its provided label table.

**Coverage:** cases with no output file are removed from the reference set. Recorded failures remain as the literal text `Failed`; they are not assigned a fixed zero by the loader. Report quality therefore needs a separate attempted/completed-case denominator.

**Serialization:** the rollout parser tolerates fenced JSON and Python-style literal dictionaries, but the report-metric reader uses strict JSON parsing. Nonclinical fixtures reproduce accepted runtime decisions becoming empty evaluation reports. A failure file also overrides a success file for the same scan key when both exist. These are source-reader observations; no learned scorer or medical inference was run.

## Visual explanation

### Workflow

- Chest CT
- Consult and reconcile tools
- Report + interaction trace

### Input

No native case is retained. The official CT-RATE page, checked on 2026-09-28, still requires accepted conditions and authentication. Its separate access terms restrict redistribution. The older HTTP 401 receipt concerns a HealthAgentBench sample, not a new RadAgent download attempt.

### Supplied helpers

No case-specific specialist trace is retained. The pinned repository's complete 288-file tree contains no NIfTI/DICOM/NPZ input and its output directory contains only three task-to-image maps. Those maps do not supply tool results or generated reports.

### Reference or output

The source audit includes nonclinical text fixtures for prompt/reference separation and trace parsing. They contain no scan, medical finding or model prediction and do not substitute for the missing worked example.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Minimal single-case inference | Ten tools and the v8c checklist | Inspect the CT, reconcile tool findings and return the final report/trace. |
| CT-RATE batch inference | Same workflow plus a split manifest | Produce per-case traces; account separately for failures, absent outputs and report quality. |

## Difficulty

The agent must reconcile several specialist outputs. Its capability depends partly on those models and checkpoints.

## Sources

- [System and tools](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/README.md)
- [Single-case inference interface](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/minimal_inference/README.md)
- [Prompt, actions and rollout parser](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/minimal_inference/app/runtime/agent_runtime.py)
- [Batch input projection](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/minimal_inference/app/runtime/dataset_scenarios.py)
- [Saved-output reader and case pairing](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/radagent/evaluation/process_generated_reports.py)
- [Report and label metrics](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/radagent/evaluation/compute_metrics.py)
- [CT-RATE downloader](https://github.com/eth-medical-ai-lab/rad-agent/blob/9e9d32936ce24676cba32c81605720fe74a5da5a/dataset_utils/CT-RATE/download_scripts/download_dataset.py)
- [Dataset and access terms](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE)
- [Sample download and rendering receipt](../samples.json)
- [Pinned source audit and nonclinical fixtures](../sources/radagent-report-audit.json)

## Coverage

Report generation · CT-RATE multiple-choice VQA · tool ablations. This anchor covers reporting only.

## Gaps

The source contract is audited; the native worked example, canonical story and visual review remain unfinished. Resume with an authorized CT, its matching saved RadAgent trace/final report, and provenance for tool-generated assets. Keep any paired reference report in a separate reader-only reveal. Downloading a CT alone does not supply the missing outputs. No model or learned-metric run was launched, and this audit does not complete the separate VQA entry.
