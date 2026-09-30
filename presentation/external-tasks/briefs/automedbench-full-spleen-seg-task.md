# Segment the spleen in CT

The task requests a CT segmentation. This is a source-backed explanation with **no completed Full model result**.

## Given

### Original data

A recovered official MSD Task09 public training pair is spleen_19. The CT and 0/1 label share a 512 × 512 × 51 voxel grid, 0.796875 × 0.796875 × 5 mm spacing and identical affine. Three axial planes at native k 20, 26 and 32 were selected after inspecting the released training label, for teaching at display WL 40 and WW 400; their locations are not solver-provided. Raw NIfTI scaling is 1/0 and source values span -1024 to 1372; this display is not an independent HU calibration check. The Full harness includes no images and does not prove this case belongs to its staged split.

### Supplied helpers

The public MSD training label is a source helper for understanding label 1. It is held behind an explicit reader reveal. The Full Lite condition names TotalSegmentator v2 spleen subset; Standard offers choices to investigate. No model is executed here.

### Callable tools

The Full task harness defines submission files and a 3,600-second budget. No model, preparer, evaluator, judge or clinical tool is run for this explanation.

### Reference-only material

The explicit reader reveal can show a pink layer from the released MSD training label on the matched source CT. Before that control is used, the CT has no label overlay. This layer is a teaching helper, not Full private ground truth or a participant output.

## Task specification

Public MSD training case and label recovered; exact Full staged-case membership, private GT, prediction and score remain unverified. The public source view and Full staged input are kept distinct.

## Expected output

Submit agents_outputs/{case_id}/dseg.nii.gz on each Full case's own CT grid with integer values 0 background and 1 spleen. This pack keeps that output empty because no participant prediction exists.

## Evaluation

The task requires integer IDs. The formatter rounds values before its allowed-ID test and checks shape only when the input exists; it does not compare affines. The scorer rounds combined outputs, fuses available private class masks at >0.5 with higher IDs winning overlap, and includes every foreground class with both-empty Dice 1. A missing class file contributes no foreground if another class exists. Absent/unreadable pairs are skipped; shape-error pairs contribute zero and count as completed. Aggregate scales per-class and macro means by completed-pair fraction and combines workflow and clinical scores equally; medal uses unscaled macro Dice. No evaluator was executed.

The pinned multiclass scorer fuses separated private spleen masks and compares one combined 0/1 prediction by array shape and Dice. It does not compare NIfTI affines. The format checker rounds voxel values before its allowed-ID test, so that test alone does not prove integer-valued input. No Full case output, private mask, evaluator call or score is retained.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: TotalSegmentator v2 (`-ta total`, spleen subset). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Sources

- [Exact pinned AutoMedBench Full task archive](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/tree/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation)
- [Official upstream acquisition route](https://msd-for-monai.s3-us-west-2.amazonaws.com/Task09_Spleen.tar)

## Visual explanation

### Input

Actual upstream CT planes are labeled by their native index and source role; no Full case equivalence is implied.

### Supplied helpers

The exact Full class names, IDs and file path are contract material. The public MSD training label is a source helper for understanding label 1. It is held behind an explicit reader reveal. The Full Lite condition names TotalSegmentator v2 spleen subset; Standard offers choices to investigate. No model is executed here.

### Reference or output

The prediction slot remains empty. The explicit reader reveal can show a pink layer from the released MSD training label on the matched source CT. Before that control is used, the CT has no label overlay. This layer is a teaching helper, not Full private ground truth or a participant output.

### Workflow

- Inspect source CT and native geometry before any label layer.
- Map source-defined label names to output voxel IDs.
- Keep public helper labels, private Full reference and participant output distinct.
