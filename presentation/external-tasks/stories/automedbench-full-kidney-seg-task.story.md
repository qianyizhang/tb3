---
schema: 2
id: automedbench-full-kidney-seg-task
title: Segment kidney and lesion on CT
locale: en
purpose: Inspect a released KiTS19 CT and source annotation separately while reading the exact Full two-mask contract and its unresolved staging path.
scope: Upstream CT teaching sample; Full case and result absent.
recipe: automed-full-kidney-v1
asset_pack: retained-automed-full-kidney-seg-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-kidney-seg-task.md
- presentation/external-tasks/sources/automedbench-full-kidney-seg-task-resolution.json
- scripts/build_automed_seg_b_assets.py
---

# Segment kidney and lesion on CT

## Start with the input boundary

```beat
id: inputs
scene: inputs
frames: 264
caption: Start with the input boundary
narration: Official KiTS19 case_00000 CT, 611 × 512 × 512 voxels at 0.5 × 0.919921875 × 0.919921875 mm along native i×j×k. Planes i=288, 311 and 344 are fixed curated teaching views at WL 40 / WW 400 HU; their selection method is undocumented. Full staged-case membership is unverified. The Full harness contains no data and no saved participant prediction.
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
narration: The exact Full harness specifies ct.nii.gz and separate organ and lesion outputs. A released KiTS19 source label is held back from the input scene and revealed only to the reader. It is not Full private ground truth. Organ and lesion occupy two files. The source annotation is an oracle format example only. These are output semantics, not observed mask pixels.
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
narration: Write separate binary agents_outputs/{case_id}/organ.nii.gz and lesion.nii.gz on the CT grid. The pinned Full config does not define whether organ must include lesion tissue; do not infer that overlap from the public KiTS19 label. Both files are required, though a missing mask counts as incomplete rather than malformed. No prediction is retained; preserve physical alignment because the scorer checks shape, not affine.
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
narration: An explicit reader reveal can show the public KiTS19 source annotation and a source-only two-mask conversion. It is not a participant prediction or Full private reference. No Full private ground truth or score is retained.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0, 1]
  class: [0, 0]
  reference: [0, 1]
cut: intentional-cut
```

## Separate array scoring from physical geometry

```beat
id: scorer
scene: scorer
frames: 264
caption: Separate array scoring from physical geometry
narration: The formatter requires exact 0/1 voxels but treats missing masks as incomplete and checks organ only if present. Dice uses >0.5; mean lesion Dice sets the medal tier, while the clinical score averages organ and lesion Dice equally and scales for incomplete coverage. No score was computed.
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
narration: The retained KiTS19 CT/source label and curated planes do not prove Full staged-case or private-GT identity. Source-label counts remain behind the reader reveal. The Full package also flags an output-directory mismatch. This is one source-backed task explanation and no population or model performance result.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
