---
schema: 2
id: automedbench-full-pancreas-oar-seg-task
title: Label 21 pancreas-region targets
locale: en
purpose: Inspect an official upstream PanTSMini CT and the exact Full label/output contract without fabricating a matching reference or score.
scope: Public upstream CT; no matched label, Full case or result.
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

# Label 21 pancreas-region targets

## Start with the input boundary

```beat
id: inputs
scene: inputs
frames: 264
caption: Start with the input boundary
narration: "The Full harness includes no dataset pixels. A bounded official retrieval recovered upstream PanTSMini CT PanTS_00000684, 266 by 158 by 152 voxels at 1.5 mm isotropic spacing in RAS sform. Native k planes 38, 76 and 114 were fixed fractionally without labels. Their display window is on stored values, with HU calibration unverified. Full staged-case membership is unverified; no prediction is retained."
visual: Official upstream CT on fixed native k planes; shared header carries the source warning.
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
narration: "The Full harness defines pancreas, pancreatic lesion and surrounding structures as 21 nonconsecutive foreground IDs: 1 through 4, 6, 8 through 17, 22 through 26 and 28. These are contract labels, not observed annotations for this CT. Its release gate forbids redistribution of converted or staged derivatives."
visual: Official upstream CT beside the contract label key; shared header carries the source warning.
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
narration: "Write agents_outputs/{case_id}/dseg.nii.gz as one integer NIfTI map. Keep the source-defined IDs, including gaps at 5, 7, 18 through 21 and 27. No participant output is retained. For this source CT, native sform and shape are retained for interpretation; the scorer checks shape rather than affine."
visual: Empty target file schema, without a participant mask; shared header carries the source warning.
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
narration: "The source CT is retained, but none of 65 bounded label cases matches its case ID. No matching annotation or Full private reference is shown. The class key is contract text, not observed labels; no score exists here."
visual: Official upstream CT without reference overlay; shared header carries the source warning.
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
visual: Scorer contract cards without a score; shared header carries the source warning.
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
narration: "One official upstream PanTS CT is retained without a matching label. The Full package excludes data and carries a no-redistribution derivative gate; the output operation remains symbolic. This is one source-backed task explanation and no population or model performance result."
visual: Evidence-limit cards; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
