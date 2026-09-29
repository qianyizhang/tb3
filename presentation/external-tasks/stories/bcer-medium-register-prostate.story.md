---
schema: 2
id: bcer-medium-register-prostate
title: Map diffusion MRI into the T2w grid
locale: en
purpose: Inspect native prostate MRI inputs and trace header-based identity resampling while preserving the absent output and alignment-reference boundary.
scope: Actual representative PI-CAI input planes with symbolic registration operation and empty target artifacts; no BCER medium run.
recipe: bcer-prostate-registration-v1
asset_pack: retained-bcer-prostate-registration-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-medium-register-prostate.md
- presentation/external-tasks/sources/bcer-workflow-audit.json
- presentation/external-tasks/sources/bcer-medium-register-prostate-resolution.json
- scripts/build_bcer_prostate_registration_assets.py
---

# Prostate MRI registration, with output absent

## Establish the source gap

```beat
id: availability
scene: availability
frames: 264
caption: Real source MRI, no retained target registration
narration: These are real PI-CAI images from case 10001_1000001, retained as a representative input for an earlier BCER workflow audit. No execution of the medium prostate registration task, transform, resampled patient image, or independent alignment reference is retained. The linked PI-CAI source and pinned BCER task route show where new evidence would come from. The top notice remains visible in every scene.
visual: Source-gap notice above an actual native T2w image; no registration result or private reference.
channels:
  view: [0, 0]
  moving: [0, 0]
  operation: [0, 0]
  swap: [0, 0]
```

## Inspect the three native inputs

```beat
id: inputs
scene: inputs
frames: 336
caption: Three unregistered contrasts have different grids
narration: The task requires T2-weighted MRI plus ADC or high-b diffusion MRI. This representative case has all three. T2w spans 640 by 640 by 21 voxels at 0.3 millimeters in-plane. ADC and high-b DWI each span 120 by 128 by 21 at two millimeters in-plane. These are native central planes with sequence-specific intensity windows and fields of view. Their display widths are not a common physical scale.
visual: Actual T2w, ADC and high-b DWI native planes, highlighted in turn with sizes and spacing.
channels:
  view: [0, 1]
  moving: [0, 0]
  operation: [0, 0]
  swap: [0, 0]
cut: intentional-cut
```

## Select fixed and moving roles

```beat
id: select
scene: select
frames: 288
caption: T2w is fixed; diffusion is moving
narration: Identify sequences first, using the supplied case manifest and typed paths. The requested registration passes T2w as fixed and ADC or high-b DWI as moving. The output should occupy the T2w grid. Changing the moving choice changes the input contrast, not the task's reference space. The manifest and runtime state are helpers, not answer masks.
visual: T2w remains fixed while the actual ADC and high-b DWI panels alternate as moving input.
channels:
  view: [0, 0]
  moving: [0, 1]
  operation: [0, 0]
  swap: [0, 0]
cut: intentional-cut
```

## Map one LPS witness

```beat
id: coordinates
scene: coordinates
frames: 360
caption: One physical point, different voxel indices
narration: A header-coordinate witness at about minus 25, 30.57, minus 1.65 millimeters in LPS lies near voxel 319.5, 319.5, 10 in T2w and 59.93, 63.93, 10 in ADC or DWI. The gold cross is an author ruler point, not a lesion or corresponding anatomical landmark. Inverse affines translate a physical location between native grids; they do not prove that anatomy is aligned.
visual: The same LPS coordinate marked on two actual source images, with distinct native voxel indices.
channels:
  view: [0, 0]
  moving: [0, 1]
  operation: [0, 0]
  swap: [0, 0]
cut: intentional-cut
```

## Trace the default operation

```beat
id: resample
scene: resample
frames: 456
caption: Identity transform still requires resampling
narration: The registered tool defaults to method identity and linear interpolation. For each target T2w voxel, its affine gives an LPS point; the inverse moving affine gives a moving-image coordinate; linear interpolation samples the diffusion intensity there. This is a symbolic grid and formula, not a resampled patient image. Rigid and affine mutual-information optimization are supported, but neither was run for this entry.
visual: Dense fixed grid to LPS to coarse moving grid, with the sample point and mapping formula; no patient output pixels.
channels:
  view: [0, 0]
  moving: [0, 1]
  operation: [0, 1]
  swap: [0, 0]
cut: intentional-cut
```

## Read the artifact contract and swap fault

```beat
id: contract
scene: contract
frames: 408
caption: File checks do not establish alignment quality
narration: The registry expects transform_path and resampled_path plus successful identify and register stages. It checks path existence and a nonempty resampled NIfTI. Both artifact sockets are empty here. Swapping fixed and moving may still produce files, but on the diffusion grid instead of the requested T2w grid. The evaluator supplies no independent landmark or anatomical alignment reference.
visual: Two empty output sockets and structural checks; switch to an explicit fixed/moving swap counterexample.
channels:
  view: [0, 0]
  moving: [0, 0]
  operation: [0, 0]
  swap: [0, 1]
cut: intentional-cut
```

## State the evidentiary limit

```beat
id: limits
scene: limits
frames: 240
caption: Header mapping is not a scored registration
narration: We have three hash-verified PI-CAI input images, their LPS geometry and the pinned BCER contract. We can explain the default identity-header resampling operation symbolically. We have no task-specific transform, patient resample, independent target or alignment metric. The prior source pack is not a medium-task run, and structural validator checks do not measure registration accuracy.
visual: Four evidence and gap cards below the persistent source-gap notice.
channels:
  view: [0, 0]
  moving: [0, 0]
  operation: [0, 0]
  swap: [0, 0]
cut: intentional-cut
```
