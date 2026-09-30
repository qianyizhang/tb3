> **Training-source example only — frozen Full evaluation IDs, test labels and results absent; acquire the [official Mendeley dataset](https://data.mendeley.com/datasets/rscbjbr9sj/2).**

# Classify pediatric chest radiographs as normal or pneumonia

Implement a two-class image pipeline, map every case to a canonical label, and submit files for evaluator-owned scoring. The source training-folder label is helper information, not a diagnosis or model prediction.

## Given

### Original data

Full expects one `image.jpg` per staged case in public data. Its harness declares dataset.included=false and requests a **100-case** evaluation split, with exact IDs unresolved. **1 native public training example** is now retained: `chest_xray/train/NORMAL/IM-0115-0001.jpeg`, grayscale **2090×1858**, original bytes. It is not a frozen Full test case. No resize or preprocessing has been applied to the stored JPEG; display scaling is visual only.

### Supplied helpers

Configuration maps `NORMAL → normal`, `PNEUMONIA → pneumonia`. Public training-folder labels may supervise authorized fitting; their visible role is distinct from private test labels. Lite fixes torchvision DenseNet-121 with ImageNet initialization, a two-output head and recorded class order `[normal,pneumonia]`. Standard compares DenseNet-121, ResNet-50 and EfficientNet-B0 using balanced accuracy on the same training-derived validation split. Models/weights are absent. Grayscale-to-model-channel conversion must be recorded; no universal resize or intensity scheme is asserted.

### Callable tools

Terminal and authorized ML runtime; this source-only interpretation invokes no model, GPU or task runtime. Task stages are plan/setup/validation/inference/submission.

### Reference-only material

Evaluation expects `/data/private/<case_id>/label.json` or `ground_truth.csv`; never use those labels for fitting, selection or calibration. Frozen evaluation IDs must be excluded from training. The exact Full split and actual mount isolation are not established here. The native training-folder label is public helper evidence, never private test ground truth.

## Task specification

Assign exactly one of `normal` or `pneumonia` per staged case. These are benchmark classes, not localization, subtype, uncertainty or clinical diagnostic findings. Before inference, validate real forward-pass output shape 1×2, finite values, grayscale handling and class-index mapping on authorized training-derived validation data. No forward pass occurred in this preparation.

**Source prompt conflict:** retained generic S4/S5 prompts ask for organ.nii.gz/lesion.nii.gz, while task.json, task-specific guidance and executable classification checker require labels. Effective runner prompt assembly is unavailable; do not present this package as an executed or fully qualified end-to-end runtime. Follow the declared classification envelope when explaining output, and resolve the generic guidance before execution.

## Expected output

Either `agents_outputs/predictions.csv` with header `patient_id,label`, or `agents_outputs/<case_id>/prediction.json` containing `{"label":"normal"}` or pneumonia. Header case/outer whitespace tolerated; canonical classes case-insensitive. CSV takes precedence for a present case label, otherwise per-case JSON fallback. Duplicate CSV IDs overwrite earlier rows in source; emit exactly one row per case. Any authored toy row is formatting only. Actual participant output absent.

## Evaluation

The executable source computes **accuracy = n_correct / len(patient_ids)**; missing prediction or missing reference never earns correctness, but every supplied case ID remains in the denominator. Present labels outside class set fail format. Partial submission can be format-valid; empty submission fails. Balanced accuracy averages recalls only across true classes represented in supplied GT; config headline is accuracy, with no extra completion scaling. Completeness is separately n_predicted/N. The declared **100** is a target, not a frozen measured denominator. Source thresholds .85/.50 are explicitly provisional generic defaults, not observed performance. No patient score is retained; bounded synthetic contract tests establish harness behavior only.

## Visual explanation

### Workflow

- Distinguish public training image/label from empty Full test input socket.
- Record preprocessing/class order and preserve private-label isolation.
- Emit one canonical class per case, then reveal evaluator denominator rules separately.

## Sources

- [Pinned Full task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/classification/chest-xray-pneumonia-cls-task.tar.gz)
- [Official native training dataset](https://data.mendeley.com/datasets/rscbjbr9sj/2)
- [Resolution receipt](../sources/automedbench-full-chest-xray-pneumonia-cls-task-resolution.json)

## Gaps

Frozen100 IDs, staged Full test images, private labels, checkpoints, predictions and scores absent. One source training example cannot establish test equivalence, clinical diagnosis or classifier performance. Generic stage-prompt conflict remains unexecuted.
