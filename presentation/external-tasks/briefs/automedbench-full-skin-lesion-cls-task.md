> **Source HAM10000 example only — Full case split, private labels and results absent; acquire through the [official ISIC archive](https://api.isic-archive.com/collections/212/).**

# Classify dermoscopy images into seven source-defined classes

Implement the selected tier's classifier and emit one canonical class per staged case. A public source label or checkpoint taxonomy is not a clinical diagnosis or model prediction.

## Given

### Original data

Full expects RGB `image.jpg` per public case and declares dataset.included=false. **1 public HAM10000 example**, ISIC_0024306, is retained from the official original-file URL at **600×450 RGB**. Its membership in collection212 is source-backed; equivalence to a frozen Full case is absent. Stored source-delivered JPEG bytes are unchanged. API declared size **22,038 bytes** differs from received **25,247 bytes**; source filename/dimensions match, but original-file hash equality is not established. No resampling/cropping/annotation performed in this pack.

### Supplied helpers

Lite fixes `spycoder/vit-base-patch16-224-in21k-enhanced-ham10000`: no substitution, ensembling, training or fine-tuning. Its seven id2label abbreviations and image processor configs were independently pinned/verified at revision `13b148c76ec7a29663604b7278db1fe1ab6eb48c`; weights and inference remain absent. Source metadata has a public descriptive Nevus label with serial-imaging confirmation, not histopathologic adjudication or Full private GT. Native example may overlap checkpoint training; no independent validation or performance claim follows.

### Callable tools

Source prescribes terminal/Transformers/CUDA implementation and validation. No checkpoint weights, GPU/model/runtime/tool execution or installation occurred here.

### Reference-only material

Private case `label.json` or `ground_truth.csv` belongs to evaluator and is absent. Exact Full case IDs, patients/lesion split, overlap and actual mount isolation are unresolved. Exclude evaluation records from tuning/model selection. A public HAM10000 metadata label remains source/helper information rather than private test reference.

## Task specification

RGB source → prescribed AutoImageProcessor → ViT logits → argmax abbreviation → canonical string. Pinned processor declares 224×224 resize, 1/255 rescale, per-channel mean/std .5/.5. This pack shows source settings, not a processed model tensor. Validate `(1,7)` output and exact mapping before batch inference. Standard may research ready seven-class ViT/EfficientNet/ConvNeXt/Swin/ResNet checkpoints; actual source classes must map unambiguously.

| Index | Abbreviation | Canonical class |
|---|---|---|
| 0 | akiec | actinic_keratoses |
| 1 | bcc | basal_cell_carcinoma |
| 2 | bkl | benign_keratosis_like_lesions |
| 3 | df | dermatofibroma |
| 4 | mel | melanoma |
| 5 | nv | melanocytic_nevi |
| 6 | vasc | vascular_lesions |

The task name actinic_keratoses covers source akiec (actinic keratoses/intraepithelial carcinoma); no additional subtype or malignancy/localization output is requested. Use source canonical strings, not invented class aliases.

**Prompt conflict:** generic S4/S5 retain organ/lesion NIfTI instructions while task envelope, Lite S3 and classification checker require label files. Effective prompt assembly unverified; this interpretation does not establish a qualified end-to-end runtime.

## Expected output

`agents_outputs/predictions.csv` with `patient_id,label`, or per-case `prediction.json` with label. Canonical labels case-insensitive; raw `nv`/other checkpoint abbreviations are not canonical and fail format unless remapped. CSV present label precedes JSON fallback; emit unique IDs. Actual outputs null; toy row is unrelated to displayed source image.

## Evaluation

Headline **balanced_accuracy = mean recall over GT classes represented in supplied patient_ids**, not necessarily all seven. Missing predictions count wrong within their true class. An absent class has recall None and is omitted from mean. Plain accuracy separately divides correct by all supplied IDs, including missing predictions/reference. No extra completion scaling; completeness n_predicted/N separately. Partial outputs may be format-valid; empty or unmapped/unknown labels fail. Source thresholds .80/.45 are configured gates, not observed/calibrated performance. Pure synthetic fixture (three correct classA, missing classB) confirms plain accuracy3/4=.75 and macro recall(1.0+0)/2=.5, not model results or clinical evidence.

## Conditions

| Condition | Supplied helper | What remains |
|---|---|---|
| Full · Lite | Fixed ViT HAM10000 seven-class checkpoint and pinned processor/mapping instructions. | Provision the prescribed checkpoint, validate exact class mapping and submit one canonical label per case. |
| Full · Standard | Candidate ready seven-class checkpoints and task-specific comparison guidance. | Research, choose, configure and validate a suitable pipeline without tuning on private test labels. |
| Related source listing | Older gallery/branch/Lite-package listing; exact release equivalence is unverified. | Follow that listing's own data, weights, metrics and assistance contract. |

## Visual explanation

### Workflow

- Public source example and helper metadata; Full test socket empty.
- RGB processor settings → seven-index abbreviation remap → canonical file schema.
- Reader explicitly reveals represented-class denominator, never private labels or scores.

## Sources

- [Pinned Full task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/classification/skin-lesion-cls-task.tar.gz)
- [Official HAM10000 collection](https://api.isic-archive.com/collections/212/)
- [Per-image metadata](https://api.isic-archive.com/api/v2/images/ISIC_0024306/)
- [Pinned checkpoint config](https://huggingface.co/spycoder/vit-base-patch16-224-in21k-enhanced-ham10000/blob/13b148c76ec7a29663604b7278db1fe1ab6eb48c/config.json)
- [Resolution receipt](../sources/automedbench-full-skin-lesion-cls-task-resolution.json)

## Gaps

Full split/case IDs/private references, exact whole-collection terms, actual weights/processor run/logits/predictions/scores absent. One HAM10000 source example with CC BY-NC terms does not qualify Full evaluation or public redistribution. Metadata/received byte-size discrepancy retained.
