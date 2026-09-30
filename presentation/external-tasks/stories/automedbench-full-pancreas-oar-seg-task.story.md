---
schema: 2
id: automedbench-full-pancreas-oar-seg-task
title: Label 21 pancreas-region structures
locale: en
purpose: Inspect the exact Full PanTS-derived label and output contract on an abstract voxel grid without fabricating patient anatomy or scores.
scope: Symbolic Full contract; patient pixels and result absent.
recipe: automed-full-pancreas-oar-v1
asset_pack: retained-automed-full-pancreas-oar-seg-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-pancreas-oar-seg-task.md
- presentation/external-tasks/sources/automedbench-full-pancreas-oar-seg-task-resolution.json
- scripts/build_automed_seg_b_assets.py
---

# Label 21 pancreas-region structures

## Start with the input boundary

```beat
id: inputs
scene: inputs
frames: 264
caption: Start with the input boundary
narration: "The Full harness requires per-case ct.nii.gz, but it includes no dataset pixels and no PanTS case is retained. The input diagram is an abstract unitless grid, not a patient image. Bounded source requests failed locally before any image bytes arrived. Obtain an actual case through the official PanTS route; the Full harness includes no pixels or saved prediction."
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
narration: "The Full harness defines pancreas, pancreatic lesion and surrounding structures as 21 nonconsecutive foreground IDs: 1 through 4, 6, 8 through 17, 22 through 26 and 28. These are contract labels, not observed pixels. Its release gate forbids redistribution of converted or staged derivatives."
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
narration: "Write agents_outputs/{case_id}/dseg.nii.gz as one integer NIfTI map. Keep the source-defined IDs, including gaps at 5, 7, 18 through 21 and 27. No participant output is retained. For an actual CT, preserve its physical frame; this symbolic grid has no patient affine, and the scorer checks shape rather than affine."
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
narration: "No source annotation, Full private reference mask or patient image is retained. The class key is contract text, not observed labels; no score exists here."
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
narration: "Config prose excludes GT-empty classes, but the pinned scorer iterates all 21 IDs and assigns both-empty Dice 1. The intended denominator remains unresolved. The formatter rounds IDs and checks shape, not affine; the aggregate weights partial-case macro Dice by completion. No score was computed."
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
narration: "No PanTS pixels or labels are retained. The Full package excludes data and carries a no-redistribution derivative gate; this view is symbolic. This is one source-backed task explanation and no population or model performance result."
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
