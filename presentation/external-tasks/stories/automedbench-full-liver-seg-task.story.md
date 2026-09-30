---
schema: 2
id: automedbench-full-liver-seg-task
title: Segment liver and lesion on CT
locale: en
purpose: Inspect a public MSD Task03 CT and reveal its matched training label to the reader while preserving the Full LiTS-versus-MSD conflict and empty two-mask output.
scope: Matched upstream CT and training label for teaching; Full case and result absent.
recipe: automed-full-liver-v1
asset_pack: retained-automed-full-liver-seg-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-liver-seg-task.md
- presentation/external-tasks/sources/automedbench-full-liver-seg-task-resolution.json
- scripts/build_automed_seg_b_assets.py
---

# Segment liver and lesion on CT

## Start with the input boundary

```beat
id: inputs
scene: inputs
frames: 264
caption: Start with the input boundary
narration: Official MSD Task03 Liver public training CT liver_53, 512 × 512 × 105 voxels at 0.85 × 0.85 × 4 mm. Three fixed native planes k=26, 52 and 79 retain WL 40 / WW 400 HU. Fourth k=64 was selected post-hoc to illustrate the public label-2 target, with a lower-index tie break; it is not unbiased input sampling or Full evidence. It is not proven to be a Full staged case. The Full harness contains no data and no saved participant prediction.
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
narration: The exact Full harness specifies ct.nii.gz and separate organ and lesion outputs, but declares LiTS as source while its script uses MSD Task03. No dataset images are included in the harness. The task declares two binary files; the release gate flags a staging output-directory mismatch. These are output semantics, not observed mask pixels.
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
narration: Write separate binary agents_outputs/{case_id}/organ.nii.gz and lesion.nii.gz on the CT grid. The pinned Full config does not define an organ–lesion overlap rule, and the public MSD label conversion does not establish that Full rule. Both files are required, though a missing mask counts as incomplete rather than malformed. No prediction is retained; preserve physical alignment because the scorer checks shape, not affine.
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
caption: Reveal the public source annotation
narration: Reveal the matched public MSD Task03 training label on all four CT planes. The fourth was selected post-hoc from the public label to show the lesion target. Source label 1 or 2 forms a teaching organ mask and label 2 a teaching lesion mask. The first three fixed planes can miss labeled anatomy; that motivated the separate disclosed teaching plane. This conversion is not verified for Full private ground truth; no participant output or score is retained.
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
narration: The package has an unresolved LiTS-versus-MSD source conflict and flagged staging output-directory mismatch. Its declared organ.nii.gz and lesion.nii.gz submission paths are known. The matched public source label does not establish Full identity or private ground truth. This is one source-backed task explanation and no population or model performance result.
visual: Task-specific source CT or symbolic grid and contract diagram; shared header carries the source warning.
channels:
  view: [0.5, 0.5]
  class: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
