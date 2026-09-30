# Label 117 anatomical structures in CT

The task requests a CT segmentation. This is a source-backed explanation with **no completed Full model result**.

## Given

### Original data

A previously hash-verified TotalSegmentator source CT s1366 supplies three fixed native coronal views. Its 333 × 333 × 336 grid has 1.5 mm isotropic spacing and a RAS affine. The center plane was selected post hoc in an earlier Lite review using kidney reference information; it is only a teaching view and not a solver-provided location. The exact Full harness names a 40-case small-v2.0.1 selection but keeps its source-ID mapping private, so this CT is not proven to be a Full case.

### Supplied helpers

The exact Full configuration enumerates integer IDs 1 through 117, from adrenal_gland_left through vertebrae_T9. Its complete name-to-ID mapping exactly matches the retained separately reviewed Lite config. The Full Lite condition names a TotalSegmentator v2 nnU-Net ensemble; no model is run here.

### Callable tools

The Full task harness defines submission files and a 3,600-second budget. No model, preparer, evaluator, judge or clinical tool is run for this explanation.

### Reference-only material

No source label or Full private-reference pixels are shown. The center-plane selection used earlier Lite reference information, but no mask pixels or locations are presented as a Full answer. Five masks in that earlier audit are not relabeled as Full ground truth or participant output.

## Task specification

The public source CT is retained, but Full case/source-ID equivalence is unverified; private GT, participant prediction and score are unavailable. The public source view and Full staged input are kept distinct.

## Expected output

Submit agents_outputs/{case_id}/dseg.nii.gz as one combined integer NIfTI map with 0 background and the exact 117 source-defined foreground IDs, on each Full case's own CT grid. Preserving its physical frame matters anatomically, although the pinned checker does not compare affines. This pack contains no participant prediction.

## Evaluation

The task requires integer IDs. The formatter rounds values before its allowed-ID test and checks shape only when the input exists; it does not compare affines. The scorer rounds combined outputs, fuses available private class masks at >0.5 with higher IDs winning overlap, and includes every foreground class with both-empty Dice 1. A missing class file contributes no foreground if another class exists. Absent/unreadable pairs are skipped; shape-error pairs contribute zero and count as completed. Aggregate scales per-class and macro means by completed-pair fraction and combines workflow and clinical scores equally; medal uses unscaled macro Dice. No evaluator was executed.

The Full config describes macro Dice over GT-nonempty classes, but the pinned scorer loops all 117 foreground IDs and gives both-empty masks Dice 1. It checks array shape, not affine. The format checker rounds voxel values before its allowed-ID test, so the required integer map is stricter than that check. The config also declares gt_subdir=masks, while run_eval passes gt_dir unchanged and the separated loader reads gt_dir/pid/class.nii.gz. The caller may supply the masks base; its Full invocation is unavailable. These denominator and path-base contracts remain unresolved, and no Full score is computed.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: TotalSegmentator v2 (nnU-Net v2 ensemble). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Sources

- [Exact pinned AutoMedBench Full task archive](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/tree/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation)
- [Official upstream acquisition route](https://zenodo.org/records/10047263)

## Visual explanation

### Input

Actual upstream CT planes are labeled by their native index and source role; no Full case equivalence is implied.

### Supplied helpers

The exact Full class names, IDs and file path are contract material. The exact Full configuration enumerates integer IDs 1 through 117, from adrenal_gland_left through vertebrae_T9. Its complete name-to-ID mapping exactly matches the retained separately reviewed Lite config. The Full Lite condition names a TotalSegmentator v2 nnU-Net ensemble; no model is run here.

### Reference or output

The prediction slot remains empty. No source label or Full private-reference pixels are shown. The center-plane selection used earlier Lite reference information, but no mask pixels or locations are presented as a Full answer. Five masks in that earlier audit are not relabeled as Full ground truth or participant output.

### Workflow

- Inspect source CT and native geometry before any label layer.
- Map source-defined label names to output voxel IDs.
- Keep public helper labels, private Full reference and participant output distinct.
