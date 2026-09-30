# Classify colorectal tissue into nine source categories

Assign one canonical tissue label per Full histology patch. **Training patch only; Full test absent.** [Official acquisition](https://zenodo.org/records/1214456).

## Value

Patch-label agreement can compare classification methods; it does not establish patient diagnosis, slide localization, clinical benefit or independent reference adjudication.

## Given

### Original data

A retained official NCT-CRC-HE-100K training patch is 224 x 224 RGB pixels; the dataset reports 0.5 micrometers per pixel and Macenko color normalization. Preview preserves decoded pixels without resizing/stain processing. No WSI coordinates or Full case ID are available. The NONORM archive is not an exact unnormalized counterpart: stochastic patch selections differ.

### Supplied helpers

Nine configured tokens map to adipose (adi), background (back), debris (deb), lymphocytes (lym), mucus (muc), smooth muscle (mus), normal colon mucosa (norm), cancer-associated stroma (str), colorectal adenocarcinoma epithelium (tum). The retained patch's public source-folder annotation is available only after helper reader reveal; it is not a model or Full test label. Lite fixes ImageNet-initialized torchvision ResNet50_Weights.IMAGENET1K_V2 with a replaced nine-class head and authorized-training fine-tuning. Standard considers ResNet50, ConvNeXtTiny and ViTB16, selecting by balanced accuracy on train-derived validation. No checkpoint is retained. Record and verify checkpoint class-index mapping.

### Callable tools

Full terminal/model-development workflow; no training, model, preparation or evaluation was run here.

### Reference-only material

Private /data/private/{case_id}/label.json or ground_truth.csv is evaluator-only. NCT-CRC-HE-100K is training; CRC-VAL-HE-7K is the designated evaluation source with independent patients upstream. The exact Full 100-case subset remains unfrozen. Runtime filesystem isolation was not audited.

## Task specification

Preserve exact IDs and canonical tissue names. Freeze evaluation IDs before training, exclude them, and document stain/resize and checkpoint label mapping. The source envelope has no embedded pixels, model weights or private targets.

## Expected output

agents_outputs/predictions.csv with patient_id,label, alternatively per-case prediction.json with label. Both illustrated values remain unset. patient_id is a case identifier, not proof of independent patients.

## Evaluation

Executable config/run_eval/aggregate select accuracy, while data-policy prose calls balanced accuracy headline. Preserve this discrepancy; Standard uses balanced accuracy for method selection. Accuracy counts all supplied case IDs, with missing predictions wrong. Balanced accuracy averages only configured true classes with nonzero support; absent-class recall null. Both are fractions 0..1 rounded four decimals. Format can pass for incomplete nonempty valid output; zero output fails. CSV nonempty label preferred per ID with JSON fallback; duplicate IDs overwrite. Private JSON preferred over GT CSV.

Default workflow retains full S1-S5 weight denominator with S1-S3 None as zero; completed S4/S5 alone max .25. Overall=.5workflow+.5configured accuracy; clinical_score is dataset agreement, not clinical validation. The .85/.50 class-quality thresholds are provisional generic defaults, not measured CRC outcomes.

## Visual explanation

### Workflow

- Official training RGB patch with absent Full-ID socket
- Inspect tissue taxonomy, reveal public annotation and verify model mapping
- Unfilled CSV/JSON artifact and distinct scoring denominators

### Input

Native pixel-preserving preview with source-reported scale, no tissue label in first-view metadata or alt text.

### Supplied helpers

Public annotation behind reader reveal; source category legend and tier guidance are independent of predictions.

### Reference or output

Empty output and private target sockets; no logits, scores or clinical claims.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: torchvision ResNet-50. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Stain/domain differences and roughly balanced classes complicate interpretation. Source patch categories are not patient diagnoses or slide segmentation labels.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/classification/crc-histology-cls-task.tar.gz)
- [Official dataset](https://zenodo.org/records/1214456), Kather, Halama and Marx, DOI 10.5281/zenodo.1214456, CC BY 4.0

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

One verified public training tile is available. Full evaluation IDs/private labels/checkpoint/predictions/scores absent. Freeze exact subset and resolve accuracy-versus-balanced policy before a trial. No source label is promoted to a diagnostic or model finding.
