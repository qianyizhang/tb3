---
schema: 2
id: automedbench-full-hepaticvessel-seg-task
title: Segment hepatic vessels and tumor on CT
locale: en
purpose: Inspect an actual public MSD Task08 CT and the Full two-label segmentation contract while keeping all participant and private-reference results empty.
scope: Upstream CT teaching sample; Full case and result absent.
recipe: automed-full-hepaticvessel-v1
asset_pack: retained-automed-full-hepaticvessel-seg-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-hepaticvessel-seg-task.md
- presentation/external-tasks/sources/automedbench-full-hepaticvessel-seg-task-resolution.json
- scripts/build_automed_seg_b_assets.py
---

# Segment hepatic vessels and tumor on CT

## Start with the input boundary

```beat
id: inputs
scene: inputs
frames: 264
caption: Start with the input boundary
narration: Official MSD Task08 HepaticVessel public test CT hepaticvessel_306, 512 × 512 × 28 voxels at 0.785156 × 0.785156 × 7.5 mm. Three selected native axial planes use a fixed WL 40 and WW 400 HU display. This CT is not proven to be a Full staged case. The Full harness contains no data and no saved participant prediction.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0, 1]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Map source-defined target IDs

```beat
id: mapping
scene: mapping
frames: 264
caption: Map source-defined target IDs
narration: The exact Full harness specifies ct.nii.gz, two foreground IDs, separated private reference masks, and a combined output map. The harness archive contains no dataset images. Two foreground labels are compared separately. A thin vessel tree and a tumor occupy different label values; neither is a substitute for the other. These are output semantics, not observed mask pixels.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Keep required output slots empty

```beat
id: output
scene: output
frames: 264
caption: Keep required output slots empty
narration: Write agents_outputs/{case_id}/dseg.nii.gz as one integer NIfTI map on the CT grid. Values are 0 background, 1 hepatic vessel and 2 hepatic tumor. No participant output is retained. Physical alignment should preserve the source frame even though the pinned Dice scorer only checks shape.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Read the source reference boundary

```beat
id: reference
scene: reference
frames: 264
caption: Read the source reference boundary
narration: No reference mask is in this pack; the private reference remains absent. No Full private ground truth or score is retained.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0, 1]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Separate array scoring from physical geometry

```beat
id: scorer
scene: scorer
frames: 264
caption: Separate array scoring from physical geometry
narration: The pinned multiclass scorer fuses separated private reference tissues and compares the combined prediction by shape and voxel label. Tumor ID 2 overwrites vessel ID 1 at overlap. After rounding labels, the scorer averages both foreground classes; both-empty Dice is one, and missing cases are skipped. It does not compare NIfTI affines. No case Dice was computed here.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Preserve the evidence limit

```beat
id: limits
scene: limits
frames: 264
caption: Preserve the evidence limit
narration: The public test CT has no matched source label here. Full staged-case membership, private ground truth, prediction and score are unknown. This is one source-backed task explanation and no population or model performance result.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
