# Segment hepatic vessels and tumor on CT

The task requests a segmentation from CT. This explainer shows the input or contract boundary and **no completed model result**.

## Given

### Original data

Official MSD Task08 HepaticVessel public test CT hepaticvessel_306, 512 × 512 × 28 voxels at 0.785156 × 0.785156 × 7.5 mm. Three selected native axial planes use a fixed WL 40 and WW 400 HU display. This CT is not proven to be a Full staged case.

### Supplied helpers

The exact Full harness specifies ct.nii.gz, two foreground IDs, separated private reference masks, and a combined output map. The harness archive contains no dataset images.

### Callable tools

The Full task harness and environment define file submission and a 3,600-second task budget. No model, preparer, grader or clinical tool is run for this explanation.

### Reference-only material

No reference mask is in this pack; the private reference remains absent.

## Task specification

Two foreground labels are compared separately. A thin vessel tree and a tumor occupy different label values; neither is a substitute for the other. The public test CT has no matched source label here. Full staged-case membership, private ground truth, prediction and score are unknown.

## Expected output

Write agents_outputs/{case_id}/dseg.nii.gz as one integer NIfTI map on the CT grid. Values are 0 background, 1 hepatic vessel and 2 hepatic tumor. No participant output is retained.

## Evaluation

The pinned multiclass scorer fuses separated private reference tissues and compares the combined prediction by shape and voxel label. It reports macro mean Dice for vessel and tumor. Tumor ID 2 overwrites vessel ID 1 when separated private masks overlap. Label values are rounded; both-empty class Dice is 1, shape mismatch contributes zeros, and missing cases are skipped. The formatter also rounds values before checking allowed IDs; that does not replace the declared integer-map contract. Neither check establishes NIfTI affine equality. No case Dice was computed here.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: nnU-Net v2 (MSD Task08_HepaticVessel pretrained). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Sources

- [Exact pinned AutoMedBench Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/tree/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation)
- [Official upstream acquisition route](https://msd-for-monai.s3-us-west-2.amazonaws.com/Task08_HepaticVessel.tar)

## Visual explanation

### Input

Actual upstream CT input, not a verified Full staged sample.

### Supplied helpers

Source-defined label names and output paths are contract text. No source annotation is supplied to a Full solver by this pack.

### Reference or output

The requested output slots are empty. No reference mask is in this pack; the private reference remains absent.

### Workflow

- Inspect the actual public input or abstract grid and its source warning.
- Map label IDs and required output files without filling a prediction.
- Read scorer boundaries and reference availability.
