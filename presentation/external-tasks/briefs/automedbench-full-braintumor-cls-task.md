# Classify brain MRI into four source categories

Develop a pipeline that maps each Full image.jpg case to one canonical label. **MRI and Full case IDs absent; symbolic workflow.** [Official acquisition](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset).

## Value

A fixed source taxonomy makes labels comparable. Dataset-label agreement does not establish histopathologic truth, localization, independent-patient generalization or clinical benefit.

## Given

### Original data

One MRI raster image.jpg per case. No matching source pixels, orientation, sequence, voxel geometry or frozen Full ID is retained. patient_id is an output identifier, not evidence of patient independence.

### Supplied helpers

Pinned configuration names glioma, meningioma, notumor and pituitary in that order. This is not a checkpoint logit-index mapping: inspect id2label and remap names before inference. Lite names ViT/ResNet guidance; neither checkpoint nor completed inference is supplied here. Only genuine upstream training folders may carry public training labels.

### Callable tools

The Full harness describes terminal/model development. Lite uses its own dependency environment; Standard supplies method candidates. No runtime, checkpoint or image operation was run.

### Reference-only material

Private /data/private/{case_id}/label.json or ground_truth.csv targets belong to evaluation, not solver input. The package declares dataset.included=false and runtime_assets empty. Runtime mount visibility was not audited.

## Task specification

Preserve exact case IDs and one canonical label per case. Verify checkpoint label ordering, input normalization and source partition before inference. Model guidance is not performance evidence.

## Expected output

agents_outputs/predictions.csv with patient_id,label; alternatively agents_outputs/{case_id}/prediction.json with label. The illustrated schema is unfilled. No case, source label, prediction or score is fabricated.

## Evaluation

Accuracy = correct / all supplied case IDs, including missing predictions. Balanced accuracy averages recalls over configured classes with nonzero true-class counts; zero-support recalls are null. Coefficients are 0..1 fractions rounded to four decimals. Format accepts valid present labels even if cases are missing, but rejects wholly empty output. CSV labels take precedence per ID; missing labels fall back to JSON. GT JSON is preferred over GT CSV. Duplicate CSV IDs overwrite, so preserve uniqueness.

Configured headline accuracy selects .85/.50 quality bands; these are rules, not results. Aggregate workflow keeps the full S1-S5 weight denominator while S1-S3 are None; S4/S5 alone contribute at most .25 under default weights. Overall = .5 workflow + .5 accuracy. The field named clinical_score contains label agreement; it is not clinical validation.

## Visual explanation

### Workflow

- Absent native image socket and source taxonomy
- Verify checkpoint mapping and infer one label per exact case
- Unfilled CSV/JSON schema with evaluator boundary

### Input

Explicit empty MRI socket, no schematic image presented as patient pixels.

### Supplied helpers

Tier guidance and taxonomy only; symbolic mapping exercise uses named tokens, not invented logits or class findings.

### Reference or output

Unsubmitted CSV/JSON alternatives, private targets absent, formulas without outcomes.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: BrainTumor-ViT (timm ViT-B/16, fine-tuned on Brain Tumor MRI). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Avoid silently equating a checkpoint index, a filename or a source folder with a verified Full label. Completeness and format checks differ from accuracy.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/classification/braintumor-cls-task.tar.gz)
- [Official MRI dataset](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Two anonymous official metadata reads timed out; no native asset or matching Full ID was acquired. This does not establish an access barrier. Harness declares CC BY 4.0 source policy; no dataset pixels are redistributed by this symbolic pack. Recover matching assets, label-map and partition evidence before reopening execution.
