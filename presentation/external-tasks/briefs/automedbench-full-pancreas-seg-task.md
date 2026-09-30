# Segment pancreas and pancreatic tumor in CT

Segment PanTS CT according to the pinned Full task. This explanation uses a complete official PanTSMini CT as an input-only upstream example. Its Full case membership is unverified; no Full evaluation was run.

## Given

### Original data

Full expects `public/{case_id}/ct.nii.gz` in its named data root; `dataset.included=false`. A complete official PanTSMini CT, case PanTS_00000684, was recovered from a bounded source pass. It has a stored 266×158×152 RAS grid at 1.5 mm spacing. The three displayed native k planes are 38, 76 and 114, selected without label guidance. Stored intensities are windowed from −160 to 240; HU calibration and original acquisition geometry are unverified. This upstream case is not verified as a Full staged case.

### Supplied helpers

The pinned task package contains Lite and Standard guidance, configuration and output conventions. No matching source training annotation was acquired. The recovered CT supplies input pixels only; task code supplies the output contract.

### Callable tools

The Full workflow permits planning, setup, validation and inference using task-specific libraries and models. No model, source preparer, controller or evaluator ran for this explanation.

### Reference-only material

Private Full masks remain with the evaluator and are unavailable here. No matching training label or Full private reference is in the pack. The separately recovered PanTS_00001349 label belongs to a different case and is not paired or overlaid.

## Task specification

Produce two distinct 3D binary masks on the CT grid: whole pancreas in organ.nii.gz and pancreatic tumor in lesion.nii.gz. PanTS source label remapping cannot be illustrated without a matching source label. Preserve a 3D spatial grid; the displayed source slices are teaching views, not submitted masks.

## Expected output

Write agents_outputs/{case_id}/organ.nii.gz and agents_outputs/{case_id}/lesion.nii.gz. Each mask separately uses 0 background and 1 foreground. The formatter requires exact 0/1 values and checks shape only when the input exists; it treats absent masks as incomplete and its internal organ-mask check is optional, although the task contract requires both files. Affine equality is not checked; physical alignment still requires the input frame. No output file or prediction is retained.

## Evaluation

For available shape-valid pairs, the scorer averages organ Dice and averages lesion Dice only across GT-positive lesion cases. It thresholds masks at >0.5. The aggregate recomputes organ mean from non-null per-case scores, including shape errors scored 0, and scales clinical metrics by inference completion for partial submissions. Clinical score weights organ and lesion equally; the medal tier uses unscaled mean lesion Dice. The scorer was not run, so these are contract definitions rather than observed quality.

## Visual explanation

The input is unmarked first. The next scenes show the actual upstream CT input on fixed native planes, then the dual-mask requirement. Output files remain empty. No source or private annotation can be revealed.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: MedFormer (PanTS). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

The Full harness contains no dataset; no Full case, private mask, prediction or score is retained. A complete upstream CT input is retained, but no same-case label or verified Full membership was recovered. Source-to-Full taxonomy conversion remains unresolved.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation/pancreas-seg-task.tar.gz).
- [Official upstream source](https://github.com/MrGiovanni/PanTS) (PanTS/Full declared CC BY-NC-ND 4.0 and restricted derivative handling).
- [Source resolution receipt](../sources/automedbench-full-pancreas-seg-task-resolution.json).
