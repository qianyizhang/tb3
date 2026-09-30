# Label 21 pancreas-region structures

The task requests a segmentation from CT. This explainer shows the input or contract boundary and **no completed model result**.

## Given

### Original data

The Full harness requires per-case ct.nii.gz, but it includes no dataset pixels and no PanTS case is retained. The input diagram is an abstract unitless grid, not a patient image. Bounded image/label archive requests failed at the configured local proxy before bytes arrived. This does not establish an upstream access restriction. Retry permitted local acquisition through the official PanTS route; the Full package supplies no case.

### Supplied helpers

The exact Full harness lists 21 nonconsecutive foreground label IDs. Its PanTS release gate says not to redistribute converted or staged derivatives.

### Callable tools

The Full task harness and environment define file submission and a 3,600-second task budget. No model, preparer, grader or clinical tool is run for this explanation.

### Reference-only material

No source annotation, Full private mask or patient image is retained; the class key comes only from the pinned contract.

## Task specification

The 21 targets include pancreas, pancreatic lesion and surrounding structures. Their source IDs are nonconsecutive: 1–4, 6, 8–17, 22–26 and 28. No PanTS pixels or labels are retained. The Full package excludes data and carries a no-redistribution gate for converted or staged derivatives; this view is symbolic.

## Expected output

Write agents_outputs/{case_id}/dseg.nii.gz as one integer NIfTI map. Keep the source-defined IDs, including gaps at 5, 7, 18 through 21 and 27. No participant output is retained.

## Evaluation

The config describes macro Dice over GT-nonempty classes. The pinned scorer iterates all 21 IDs and assigns Dice 1 when both masks are empty, leaving the intended denominator unresolved. The formatter rounds values for allowed-ID checking, though the requested map is integer; it checks shape against available CT, not affine. The aggregate scales multiclass Dice by completion for partial submissions. No score was computed here.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: VISTA3D (MONAI foundation model for 3D CT, 132 classes). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Sources

- [Exact pinned AutoMedBench Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/tree/f894057807cc334421784e702ead2c1883583e1b/tasks/segmentation)
- [Official upstream acquisition route](https://github.com/MrGiovanni/PanTS)

## Visual explanation

### Input

Document-pinned contract and abstract grid, with no patient pixels.

### Supplied helpers

Source-defined label names and output paths are contract text. This pack supplies no PanTS case or annotation to a Full solver.

### Reference or output

The requested output slots are empty. No source annotation, Full private mask or patient image is retained; the class key comes only from the pinned contract.

### Workflow

- Inspect the abstract grid and its source-access warning.
- Map label IDs and required output files without filling a prediction.
- Read scorer boundaries and reference availability.
