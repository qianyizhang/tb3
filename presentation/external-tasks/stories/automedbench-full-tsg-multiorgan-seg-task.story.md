---
schema: 2
id: automedbench-full-tsg-multiorgan-seg-task
title: Label 117 anatomical structures in CT
locale: en
purpose: Inspect a retained published TotalSegmentator CT and the exact Full 117-class map without presenting Lite private masks as Full reference.
scope: Public upstream CT teaching with post hoc plane selection; Full staged case and result unavailable.
recipe: automed-full-tsg-multiorgan-v1
asset_pack: retained-automed-full-tsg-multiorgan-seg-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-tsg-multiorgan-seg-task.md
- presentation/external-tasks/sources/automedbench-full-tsg-multiorgan-seg-task-resolution.json
- scripts/build_automed_seg_d_assets.py
---

# Label 117 anatomical structures in CT

## Read the public CT before labels

```beat
id: inputs
scene: inputs
frames: 264
caption: Read the public CT before labels
narration: A previously hash-verified TotalSegmentator source CT s1366 supplies three fixed native coronal views. Its 333 × 333 × 336 grid has 1.5 mm isotropic spacing and a RAS affine. The center plane was selected post hoc in an earlier Lite review using kidney reference information; it is only a teaching view and not a solver-provided location. The exact Full harness names a 40-case small-v2.0.1 selection but keeps its source-ID mapping private, so this CT is not proven to be a Full case. No Full participant output is retained.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0, 1]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Map names to exact integer IDs

```beat
id: mapping
scene: mapping
frames: 264
caption: Map names to exact integer IDs
narration: The exact Full configuration enumerates integer IDs 1 through 117, from adrenal_gland_left through vertebrae_T9. Its complete name-to-ID mapping exactly matches the retained separately reviewed Lite config. The Full Lite condition names a TotalSegmentator v2 nnU-Net ensemble; no model is run here. The operation selects a class name and its required integer output value; it does not paint a mask.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Keep the dseg target empty

```beat
id: output
scene: output
frames: 264
caption: Keep the dseg target empty
narration: Submit agents_outputs/{case_id}/dseg.nii.gz as one combined integer NIfTI map with 0 background and the exact 117 source-defined foreground IDs, on each Full case's own CT grid. Preserving its physical frame matters anatomically, although the pinned checker does not compare affines. This pack contains no participant prediction. Shape and affine are different conditions for a physically meaningful submission.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Preserve the reference boundary

```beat
id: reference
scene: reference
frames: 264
caption: Preserve the reference boundary
narration: No source label or Full private-reference pixels are shown. The center-plane selection used earlier Lite reference information, but no mask pixels or locations are presented as a Full answer. Five masks in that earlier audit are not relabeled as Full ground truth or participant output. The Full private masks remain unavailable.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0, 1]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Read the pinned scoring boundary

```beat
id: scorer
scene: scorer
frames: 264
caption: Read the pinned scoring boundary
narration: The Full config describes macro Dice over GT-nonempty classes, but the pinned scorer loops all 117 foreground IDs and gives both-empty masks Dice 1. It checks array shape, not affine. The format checker rounds voxel values before its allowed-ID test, so the required integer map is stricter than that check. The config also declares gt_subdir=masks, while run_eval passes gt_dir unchanged and the separated loader reads gt_dir/pid/class.nii.gz. The caller may supply the masks base; its Full invocation is unavailable. These denominator and path-base contracts remain unresolved, and no Full score is computed.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## State the result limit

```beat
id: limits
scene: limits
frames: 264
caption: State the result limit
narration: The public source CT is retained, but Full case/source-ID equivalence is unverified; private GT, participant prediction and score are unavailable. This is one source example, not a model or population performance result.
visual: Native source CT and task-specific class or output operation; source notice in common header.
channels:
  view: [0.5, 0.5]
  label: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
