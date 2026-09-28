# Build a kidney and tumor segmentation pipeline

Select and run a model to label kidneys and kidney lesions in CT, then submit predictions.

## Value

Separating organs and lesions can support measurement and review. Here the agent is evaluated on constructing the research pipeline.

## Given

### Original data

Per-patient `ct.nii.gz` volumes. The pinned domain-branch config names `CruzAbdomen_Kidney`; its staging scripts use different directory layouts. No native kidney case is retained for this entry.

### Supplied helpers

Lite names a KiTS19 nnU-Net checkpoint and supplies requirements plus setup examples. Standard supplies candidate families and comparison guidance. Both assembled prompts include the one-patient S3 validation example.

### Callable tools

GPU/network agent environment; a separate evaluator compares submitted outputs with held-out references.

### Reference-only material

Held-out segmentation references belong to the separate evaluation environment.

## Task specification

Plan, set up, validate on one patient, infer every patient, then call `submit_results`. The config sets **3,600 seconds**. Check tumor-label coverage and preserve input geometry; an organ-only model does not satisfy the requested target.

## Expected output

Write two binary files per patient: `agents_outputs/<patient_id>/organ.nii.gz` and `lesion.nii.gz`. Retain the plan, setup and validation artifacts. `agents_decision.csv` is optional. These are requested outputs, not retained predictions.

## Evaluation

The deterministic score combines organ Dice and lesion Dice equally; lesion Dice uses evaluated reference-positive cases. Missing patient outputs trigger the completeness gate. S1–S3 require a separate judge; none was run here.

**Contract caveat:** the prompt and runner quick check require both masks, but the format helper treats organ masks as optional. Its shape/value checks and array Dice do not verify physical affines. Six nonclinical fixtures reproduce these distinctions in the linked source audit; they are not medical performance results.

## Visual explanation

### Workflow

- CT + tier guidance
- Plan, set up, validate, infer
- Segmentation + submission

### Input

No native input view curated yet. The workflow diagram explains structure only.

### Supplied helpers

The condition switch describes assistance. Both tiers receive validation guidance; no native source-derived overlay is available.

### Reference or output

No source-derived reference/output visual curated yet.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Lite guidance | Named checkpoint, requirements and S1–S3 examples | Verify preprocessing, tumor labels and complete inference. |
| Standard guidance | Candidate families, comparison guidance and S3 example | Research the model, provision dependencies and validate its outputs. |

## Difficulty

Knowing a plausible model is only the start: loading weights, mapping labels, checking preprocessing and producing valid predictions all matter.

## Sources

- [Kidney task config](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/config.yaml)
- [Lite assistance](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/lite_s1.md)
- [Standard assistance](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/standard_s1.md)
- [Task gallery](https://github.com/AutoMedBench/AutoMedBench/blob/5394fe7aa73e6b5891fe43942c99f4b0c2b50873/docs/task-gallery.md)
- [Pinned format checker](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/format_checker.py)
- [Pinned Dice and aggregate scoring](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/aggregate.py)
- [Source audit and nonclinical fixtures](../sources/automed-kidney-audit.json)

## Coverage

Segmentation · enhancement · VQA · reporting · detection · classification; the full packaged release also lists synthesis. Published coverage differs by release.

## Gaps

The source contract is audited; native input, canonical story and visual review remain open. Official KiTS19 acquisition timed out on 2026-09-28. Resume with a licensed CT/label pair, preferably `case_00000`, and reconcile its provenance with the pinned staging recipe. The separate multi-organ CT and Full-release harness do not establish this kidney condition's inputs. No model, judge or medical pipeline was run.
