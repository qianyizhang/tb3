# Label 21 pancreas-region targets

The task requests a segmentation from CT. This explainer shows an official upstream PanTSMini CT and the output contract, with **no completed model result**.

## Given

### Original data

The Full harness requires per-case ct.nii.gz and includes no dataset pixels. A bounded official range retrieval recovered PanTSMini PanTS_00000684 CT, an upstream image with 266 × 158 × 152 stored voxels, 1.5 mm isotropic spacing and RAS sform. Three native k planes (38, 76, 114) are fixed fractional samples with no label guidance. Display window [−160, 240] is applied to stored values; HU calibration, clipping and earlier preprocessing are unverified. The source CT is not proven to be a Full staged case.

### Supplied helpers

The exact Full harness lists 21 nonconsecutive foreground label IDs. Its PanTS release gate says not to redistribute converted or staged derivatives.

### Callable tools

The Full task harness and environment define file submission and a 3,600-second task budget. No model, preparer, grader or clinical tool is run for this explanation.

### Reference-only material

No matching annotation for PanTS_00000684 or Full private mask is retained. The class key comes from the pinned contract, not this CT; a different-case source label is excluded.

## Task specification

The 21 targets include pancreas, pancreatic lesion and surrounding structures. Their Full output IDs are nonconsecutive: 1–4, 6, 8–17, 22–26 and 28. The recovered CT illustrates input viewing only; no matched source annotation or Full private label is shown. The Full package excludes data and carries a no-redistribution gate for converted or staged derivatives, distinct from local noncommercial source interpretation.

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

Official upstream CT displayed on three fixed native k planes; no matched label or Full-case equivalence.

### Supplied helpers

Source-defined label names and output paths are contract text. This pack uses one upstream CT for teaching; no matched annotation or Full case is supplied to a solver.

### Reference or output

The requested output slots are empty. No matching annotation for PanTS_00000684 or Full private mask is retained. The class key comes from the pinned contract, not this CT; a different-case source label is excluded.

### Workflow

- Inspect three fixed native CT planes and the source-membership warning.
- Map label IDs and required output files without filling a prediction.
- Read scorer boundaries and reference availability.
