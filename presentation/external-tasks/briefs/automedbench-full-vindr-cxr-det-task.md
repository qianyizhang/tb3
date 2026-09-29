# Locate thoracic findings on chest X-rays

Build a detector that localizes findings on chest X-ray images. The worked illustration is symbolic because no official image was acquired; it is not a Full benchmark run.

## Given

### Original data

The Full harness expects `public/{case_id}/image.png` under `VinDrCXR_Detection100`. The package declares `dataset.included=false`. The official PhysioNet dataset is credentialed and no image is in this pack.

### Supplied helpers

Task-specific config and Lite/Standard guidance identify the expected classes and methods. The generic prompt incorrectly repeats a VinDr 14-class example for other tasks. The class contract here is Aortic enlargement, Atelectasis, Calcification, Cardiomegaly, Consolidation, ILD, Infiltration, Lung Opacity, Nodule/Mass, Other lesion, Pleural effusion, Pleural thickening, Pneumothorax, Pulmonary fibrosis. Model weights are not included in the task package; VinDr Lite also declares separate read-only checkpoint/config mounts absent from the package.

### Callable tools

The task environment permits method setup, validation and inference. No model, preparer, controller or evaluator was run for this explanation.

### Reference-only material

Full evaluator labels are `/data/private/{case_id}/boxes.json`, unavailable in this pack. No upstream source label or private Full label was acquired.

## Task specification

For each staged case, search the entire image, assign a task class string, and convert any detector coordinates back to original image pixels. Use the selected Full Lite or Standard condition rather than related ReX or gallery split rules.

## Expected output

Write `agents_outputs/{case_id}/prediction.json` with `{"boxes":[]}` at minimum. Each future box needs string `class` and numeric `x1,y1,x2,y2` with positive width and height inside the source image. Include `score` in `[0,1]` for ranked AP. The checker allows it to be absent, but the scorer treats missing score as `1.0`; the field is `score`, not `confidence`.

## Evaluation

The pinned Full scorer matches same-class boxes greedily at IoU ≥ 0.5, computes 101-point AP per class, and averages classes with ground truth. Case coverage affects aggregate score. No prediction, mAP or clinical result was retained.

## Visual explanation

Input alone precedes a source-pixel ruler and class mapping. The output chapter shows an empty JSON schema. An explicit reader reveal shows only upstream source labels, when available, in dashed amber; Full private boxes remain absent.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: Single YOLOv5 detector fine-tuned on VinBigData / VinDr-CXR-style 14-class chest abnormality detection. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

14 thoracic disease categories named in task guidance, with no source annotation acquired. Official data are credentialed; unauthenticated annotation request returned HTTP 403. No native image, private boxes or user-provisioned Lite model files are available.

## Sources

- [Pinned Full task harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/detection/vindr-cxr-det-task.tar.gz).
- [Official upstream source](https://physionet.org/content/vindr-cxr/1.0.0/) (PhysioNet Credentialed Health Data License 1.5.0).
- [Source resolution receipt](../sources/automedbench-full-vindr-cxr-det-task-resolution.json).
