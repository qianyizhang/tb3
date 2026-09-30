# Detect tumor in a histology tile's center

Predict one canonical label per Full PCam tile. **Full tile absent; upstream figure only.** [Official acquisition](https://github.com/basveeling/pcam).

## Value

Patch-label agreement assesses this classification target. It does not establish patient diagnosis, clinical benefit, localization or whole-slide detection performance.

## Given

### Original data

Full requires image.jpg, a 96 x 96 color H&E tile. No indexed native dataset row or frozen Full case is retained. A symbolic frame shows only the central 32 x 32 labeling window. The official 1600 x 400 README collage includes source positive markings, so it appears only behind a reader reveal. Its row IDs and partition are unknown. No physical calibration or WSI coordinates are claimed.

### Supplied helpers

Upstream 0 maps to negative; 1 maps to positive. Positive means at least one annotated tumor pixel in the central 32 x 32 region. Outer tumor alone does not set positive. Public train and validation annotations support development. The complete public train_y gzip matches its pinned checksum, but no verified paired image row was extracted; no individual label is used here.

Lite fixes ImageNet ResNet18_Weights.IMAGENET1K_V1 with a replacement two-class head, trained only on official train. Standard considers ResNet50, DenseNet121 and ConvNeXtTiny, using public validation. No checkpoint is retained. Record class indices and crop/resize behavior while preserving the center-label semantics.

### Callable tools

The Full terminal/model-development workflow. No installation, model execution, inference or grading occurred.

### Reference-only material

Private Full label.json or ground_truth.csv is evaluator-only. Upstream train 262144 / validation 32768 / test 32768 are WSI-disjoint and 50/50 balanced according to the pinned README. Full declares 100 test-source cases, with exact IDs unresolved. Public access to upstream test labels does not authorize fitting to Full evaluation targets. Runtime visibility remains unaudited.

## Task specification

Preserve whole-slide-disjoint splits, exclude frozen Full IDs, and verify class mapping and preprocessing before inference. In a 96-pixel grid, the central half-open bounds are 32 <= x < 64 and 32 <= y < 64. The illustrated frame is a geometry rule, not an actual tumor mask.

## Expected output

agents_outputs/predictions.csv with patient_id,label, or per-case prediction.json with label. Full requires negative/positive strings; upstream numeric labels need mapping. Both values remain unset. patient_id is a schema identifier, not proof of patient independence.

## Evaluation

Accuracy = correct / all supplied case IDs, counting missing predictions as wrong. Balanced accuracy averages only classes with positive true support; absent-class recall is null. Values are 0..1 fractions rounded to four decimals. Incomplete nonempty valid output can pass format; empty output fails. CSV is preferred per ID with JSON fallback; duplicate CSV IDs overwrite. Private GT JSON is preferred over GT CSV. No score is measured.

Default workflow includes S1-S3 None as zero in the full step denominator. S4/S5 alone contribute at most .25; overall = .5 workflow + .5 accuracy. Generic .85/.50 thresholds are provisional. The clinical_score field measures dataset agreement, not clinical validation.

## Visual explanation

### Workflow

- Symbolic 96 x 96 input and central 32 x 32 rule
- Reader-revealed annotated source figure and permitted split/model guidance
- Unfilled CSV/JSON output and all-case scoring boundary

### Input

Center/context geometry only; no fabricated tissue pixels.

### Supplied helpers

The official label-marked figure is covered until reader reveal. It has no matched dataset rows or Full labels.

### Reference or output

An unsubmitted schema with private targets absent. No prediction, confidence, metric or diagnosis is invented.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: torchvision ResNet-18. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Crop/resize can change what occupies the decision window. WSI leakage can invalidate comparisons; upstream balance does not prove Full subset balance.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/classification/patchcamelyon-cls-task.tar.gz)
- [Pinned official README](https://github.com/basveeling/pcam/blob/521af5fc74c20cc6df83974f20abb1d394797612/README.md)
- [Official mirror](https://zenodo.org/records/2546921)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

The bounded attempt recovered a complete 21 KB training-label gzip and 256 KiB image-gzip prefix, insufficient to verify the chunk-addressed image-row identity. No guessed native extraction was used. Full IDs, private targets, checkpoint and outputs remain absent. The README declares data CC0 and repository MIT; exact figure bytes and provenance are retained separately. Verify an indexed x/y pair before replacing the symbolic input.
