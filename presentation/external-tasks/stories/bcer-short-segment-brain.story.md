---
schema: 2
id: bcer-short-segment-brain
title: Segment brain tumor subregions from four MRI contrasts
locale: en
purpose: Trace four typed sequence inputs through identification, segmentation, label semantics and structural artifact checks.
scope: Symbolic BCER source contract only. No matching BraTS case, BCER run, segmentation output or reference mask is retained.
recipe: bcer-brain-v1
asset_pack: retained-bcer-brain-symbolic-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-short-segment-brain.md
- presentation/external-tasks/sources/bcer-brain-resolution.json
- scripts/build_bcer_brain_assets.py
---

# Canonical symbolic BCER brain segmentation explanation

## Four named contrasts are required

```beat
id: inputs
scene: inputs
frames: 216
caption: 'Symbolic: no matching four-sequence case. Acquire through official BraTS access.'
narration: 'BCER short_segment_brain requires T1, post-contrast T1c, T2 and FLAIR. These four unit-grid cards are symbols, not MRI pixels. No matching four-sequence case was retained locally; the official BraTS 2021 request route is linked in the visible warning.'
visual: Four abstract unit grids with contrast labels, a no-patient-pixels badge and the official acquisition route.
channels:
  view:
  - 0
  - 1
```

## Map each file to the right argument

```beat
id: identify
scene: identify
frames: 264
caption: Sequence identity is an input decision
narration: 'The supplied case manifest and identify_sequences tool resolve actual file paths into four typed arguments. A path can exist yet represent the wrong modality. The source fault profile swaps T1c and FLAIR to probe that semantic error; the two signals should not be silently interchanged.'
visual: Four paths flow from abstract sequence slots into exact t1_path, t1c_path, t2_path and flair_path argument sockets; switch to a clearly marked swap counterexample.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## The specialist tool owns the segmentation

```beat
id: segment
scene: segment
frames: 288
caption: The segmentation tool consumes the quartet
narration: 'The requested chain is identify_sequences followed by brats_mri_segmentation. Its normal path invokes a MONAI BraTS bundle in T1c, T1, T2, FLAIR order. If MONAI dependencies cannot load, pinned source can produce a heuristic T1c and FLAIR fallback. Neither path was executed for this explanation.'
visual: Four symbolic channels enter one tool block; two documented implementation paths remain clearly unobserved.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## A label map and whole-tumor mask are distinct

```beat
id: labels
scene: labels
frames: 312
caption: The label map and whole-tumor mask differ
narration: 'The expected seg_path is a BraTS-style label map: zero background, one necrotic core, two edema or invaded tissue, four enhancing tumor. The expected wt_mask_path is binary whole tumor: the union of labels one, two and four. These color keys explain file semantics, not an observed patient mask.'
visual: Four disjoint color-key tiles flow into an abstract WT union; empty artifact sockets for seg_path and wt_mask_path, no invented prediction shape.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## The BCER checks are structural

```beat
id: checks
scene: checks
frames: 264
caption: Structural checks do not measure tumor accuracy
narration: 'BCER requires both stages, the two output paths, and nonempty NIfTI checks for the label map and WT mask. On a NIfTI read error, its nonempty function can fall back to positive file size. Passing these checks would establish workflow artifacts, not boundary accuracy or a clinical result.'
visual: Exact two-stage, two-path and three-invariant contract lanes with no pass score or patient result.
channels:
  view:
  - 0
  - 1
cut: intentional-cut
```

## The case and reference are still missing

```beat
id: limits
scene: limits
frames: 216
caption: A case-level comparison needs new evidence
narration: 'The pinned code and contract are available, but no matching BraTS case, segmentation output, or case-matched annotation is retained. BraTS training annotations, if later acquired, belong behind a reader-only reveal and must not become solver input. This story makes no model-performance claim.'
visual: Source-available and case-evidence-missing cards; official BraTS acquisition route remains visible.
channels:
  view:
  - 0
  - 0
cut: intentional-cut
```
