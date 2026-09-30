# Segment pancreas and tumor in T2 MR-Linac MRI

Segment PANTHER treatment-planning T2 MR-Linac MRI according to the pinned Full task. This explanation shows a symbolic contract because no task-matched native sample was acquired; no Full evaluation was run.

## Given

### Original data

Full expects `public/{case_id}/mri.nii.gz` in its named data root; `dataset.included=false`. No task-matched native T2 MR-Linac scan or label was recovered. The official PANTHER Zenodo record is restricted and lists no files to an unauthenticated reader.

### Supplied helpers

The pinned task package contains Lite and Standard guidance, configuration and output conventions. No source training annotation was acquired. Task code supplies the label contract but no image pixels.

### Callable tools

The Full workflow permits planning, setup, validation and inference using task-specific libraries and models. No model, source preparer, controller or evaluator ran for this explanation.

### Reference-only material

Private Full masks remain with the evaluator and are unavailable here. No matching training label or Full private reference is in the pack.

## Task specification

Convert source MHA codes 1=tumor and 2=pancreatic parenchyma into two separate binary Full targets: organ=1 for source {1,2}; lesion=1 for source {1}. This is a label-contract transform only, not a segmentation. Preserve a 3D spatial grid; the displayed diagrams or slices are teaching views, not submitted masks.

## Expected output

Write agents_outputs/{case_id}/organ.nii.gz and agents_outputs/{case_id}/lesion.nii.gz. Each output mask separately uses 0 background and 1 foreground. The task requires both files. The formatter checks exact binary values and shape only when the input exists; its internal organ check is optional and missing masks count as incomplete. Preserve the affine for physical alignment; the formatter does not compare affines. No output file or prediction is retained.

## Evaluation

Scorer thresholds masks at >0.5 and averages valid available organ pairs and valid GT-positive lesion pairs. Aggregate recomputes organ mean from non-null per-case entries including shape-error zeros, scales metrics by lesion-output completion, forms 0.5 organ + 0.5 lesion clinical score and 0.5 workflow + 0.5 clinical overall score. Medal uses unscaled mean lesion Dice; none was executed. These are contract definitions rather than observed quality.

## Visual explanation

The input is unmarked first. The next scenes show the native-grid dual-mask requirement, then the source-label mapping where known. Output files remain empty. No source or private annotation can be revealed.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: VBoussot/Panther T2 single fold (ResidualEncoderUNet, CV_0) + MRSegmentator single-fold for pancreas mask. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Research access to the PANTHER dataset is required. This radiotherapy-planning T2 domain is distinct from diagnostic arterial T1; no Full case, private mask, prediction or score is retained.

## Sources

Official metadata states CC-BY-NC-4.0, while the pinned task config states CC-BY-NC-SA-4.0. No source pixels or labels are redistributed; obtain applicable terms with access. Symbolic assets use the TB3 teaching license.

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation/panther-t2-seg-task.tar.gz).
- [Official upstream source](https://zenodo.org/records/15192302) (restricted CC BY-NC 4.0).
- [Source resolution receipt](../sources/automedbench-full-panther-t2-seg-task-resolution.json).
