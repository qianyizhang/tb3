# Build a kidney and tumor segmentation pipeline

Select and run a model to label kidneys and kidney lesions in CT, then submit predictions.

## Value

Separating organs and lesions can support measurement and review. Here the agent is evaluated on constructing the research pipeline.

## Given

### Original data

Abdominal CT inputs; the inspected task config uses ct.nii.gz.

### Supplied helpers

Tier-specific skills. Lite includes a concrete KiTS19 checkpoint and inspection example; Standard supplies search and model-comparison guidance.

### Callable tools

GPU/network agent environment; a separate evaluator compares submitted outputs with held-out references.

### Reference-only material

Held-out segmentation references belong to the separate evaluation environment.

## Task specification

Plan, set up, validate, infer and submit. The inspected kidney config sets a 3,600-second time budget.

## Expected output

Kidney/tumor segmentation predictions plus the required staged workflow artifacts; exact submission details belong to the domain branch.

## Evaluation

Segmentation Dice plus process scoring. S1–S3 use rubric judgments; S4–S5 check completion/format deterministically.

## Visual explanation

### Workflow

- CT + tier guidance
- Plan, set up, validate, infer
- Segmentation + submission

### Input

No native input view curated yet. The workflow diagram explains structure only.

### Supplied helpers

The condition switch describes assistance. A source-derived overlay is not yet available.

### Reference or output

No source-derived reference/output visual curated yet.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Lite guidance | Concrete checkpoint + example loading code | Make the supplied model work correctly on the task. |
| Standard guidance | Model search + comparison guidance | Select a suitable model and build a working inference pipeline. |

## Difficulty

Knowing a plausible model is only the start: loading weights, mapping labels, checking preprocessing and producing valid predictions all matter.

## Sources

- [Kidney task config](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/config.yaml)
- [Lite assistance](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/lite_s1.md)
- [Standard assistance](https://github.com/AutoMedBench/AutoMedBench/blob/5a9834ce0010c4e97b9eb22a4645321b9529902b/eval_seg/kidney-seg-task/standard_s1.md)
- [Task gallery](https://github.com/AutoMedBench/AutoMedBench/blob/5394fe7aa73e6b5891fe43942c99f4b0c2b50873/docs/task-gallery.md)

## Coverage

Segmentation · enhancement · VQA · reporting · detection · classification; the full packaged release also lists synthesis. Published coverage differs by release.

## Gaps

This kidney task still needs its own case and submission audit. A separate multi-organ segmentation brief now illustrates an exact AutoMedBench Lite CT with reference masks; the two tasks are kept distinct.
