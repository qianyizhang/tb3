---
schema: 2
id: aneurysm-localization
title: Find a candidate, check its depth, return a point
locale: en
purpose: Explain retained aneurysm search through full MRA projections, selected native
  sections, saved points, weak-region scoring and source-assisted negative evidence.
scope: Three selected TOF-MRA examinations; original Sol/xhigh outcomes; source-derived
  views and explicit reference reveals; no clinical accuracy estimate.
recipe: aneurysm-localization-v1
asset_pack: retained-aneurysm-localization-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/lesion-localization/presentation/briefs/tb3-aneurysm-localization.md
- groups/lesion-localization/findings/lesion-localization-current-synthesis.md
- groups/lesion-localization/presentation/sources/aneurysm-audit.json
- docs/evidence/br016-results.json
- docs/evidence/br016-trace-reviews.json
- docs/research-rounds/BR-016-aneurysm-localization.md
- scripts/audit_aneurysm_evidence.py
- scripts/build_aneurysm_assets.py
---

# Retained aneurysm search

## A complete scan; no target location supplied

```beat
id: inputs
scene: inputs
frames: 240
caption: A complete scan; no target location supplied
narration: The agent receives the original and source skull-stripped angiography volume
  on the same native grid. These full-volume projections are starting views. The task
  supplies no lesion-centred crop, lesion count or private mask. The deliverable is
  one native voxel coordinate per finding, or an empty list.
visual: Two full N02 axial projections, original and skull-stripped, with native dimensions
  and spacing.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## A projection shows brightness, but collapses depth

```beat
id: projections
scene: projections
frames: 240
caption: A projection shows brightness, but collapses depth
narration: Each projection keeps the brightest value along one axis. Structures at
  different depths can overlap in the same pixel. These three views all show the same
  complete N02 scan. Their physical aspect follows voxel spacing, with Right, Anterior
  and Superior directions explicitly labelled.
visual: Three native full-volume MIPs, with collapsed-axis intervals and orientation
  labels.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Twelve fixed slabs cover the whole scan

```beat
id: slabs
scene: slabs
frames: 576
caption: Twelve fixed slabs cover the whole scan
narration: 'The supplied helper also partitions the full scan into twelve equal axial
  slabs. Every native section belongs to one slab. The sequence steps through those
  actual projections without interpolation. Slabs reduce overlap, but still compress
  depth: individual sections are needed to check a candidate.'
visual: Twelve successive axial-slab MIPs at two seconds per fixed partition; no region
  or output overlay.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Check the selected candidate in three planes

```beat
id: candidate
scene: candidate
frames: 288
caption: Check the selected candidate in three planes
narration: In N02, the agent generated and displayed candidate montages in three planes
  at trace steps fourteen and fifteen. These are selected sections reconstructed from
  the original crop and window, not the entire montages. Choosing that crop was part
  of the search; the task did not provide the location.
visual: Three source sections i312, j214 and k94, exact step-14 crop and intensity
  window; full overview beside them.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Move through real sections to resolve depth

```beat
id: depth
scene: depth
frames: 504
caption: Move through real sections to resolve depth
narration: Seven selected sections from the original axial montage show how the candidate
  appearance changes with depth. Slice indices change discretely from eighty-four
  to one hundred four. This is native source data, not an interpolated shape. Visual
  confirmation and later numerical checks preceded the saved point.
visual: Discrete k84,88,92,94,96,100,104 source sections in the original candidate
  crop.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Return a coordinate in the original grid

```beat
id: outputs
scene: outputs
frames: 240
caption: Return a coordinate in the original grid
narration: 'The saved N02 answer contains one point: three hundred twelve, two hundred
  thirteen, ninety-four. The cyan cross marks that same voxel in three reader sections
  through the answer. These point-centred sections were selected afterward. Neither
  the weak reference region nor the score is visible yet.'
visual: Native reader planes through the saved point, cyan crosses, exact JSON answer;
  reference hidden.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal a region match, not an exact-centre test

```beat
id: reference
scene: reference
frames: 336
caption: Reveal a region match, not an exact-centre test
narration: The green dashed outline is the released weak region; the gold dotted outline
  adds the frozen one-millimetre acceptance margin. The submitted point lies inside
  the released region itself, despite being two point one six millimetres from its
  centroid. This endpoint is coarse localization, not exact clinical sac segmentation.
visual: Same point-centred source views; weak and accepted regions appear together
  halfway through the chapter; private values wait for reveal.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
cut: intentional-cut
```

## An empty answer can miss a real reference region

```beat
id: miss
scene: miss
frames: 336
caption: An empty answer can miss a real reference region
narration: N01 returned an empty list, leaving its one released region unmatched.
  These reference-centred views are post-result reader aids, not inputs or claimed
  agent close-ups. The empty answer fails regardless of precise centre tolerance.
  Source fidelity does not establish clinical visibility or isolate why the region
  was missed.
visual: Three N01 native reference-centred sections with separate weak and tolerance
  contours and empty saved answer.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Generated-view coverage does not prove recognition

```beat
id: coverage
scene: coverage
frames: 288
caption: Generated-view coverage does not prove recognition
narration: N01 generated earlier views covering the reference region, but its final
  candidate close-ups focused elsewhere. These selected axial sections reconstruct
  those final montages, generated and viewed at steps twenty-eight and twenty-nine.
  More elaborate numerical checks did not ensure a matching answer; these observations
  do not establish a causal failure mechanism.
visual: Two native source sections from the final N01 candidate montages, with exact
  crop/window and reference-location caveat beside them.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Source identification changes a negative result

```beat
id: negative
scene: negative
frames: 384
caption: Source identification changes a negative result
narration: N03 inspected images, then consulted the public annotation inventory and
  matched the downloaded original scan to the task array. Its final empty answer came
  afterward. Lookup was allowed, and the original grade remains a pass. Without a
  frozen answer before lookup, it cannot measure isolated negative image interpretation.
visual: 'Native N03 overview beside an explicitly qualitative timeline: image review,
  inventory exposure at step42, equality at step48, final empty JSON.'
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Distinguish empty answers, invalid outputs and extras

```beat
id: matching
scene: matching
frames: 288
caption: Distinguish empty answers, invalid outputs and extras
narration: Scoring rounds a point to the nearest voxel and matches each accepted region
  at most once. Missing or extra detections fail. A valid empty list passes the negative
  task; the empty object used by no-op controls is invalid. Nine saved grades replay
  exactly. The earlier verifier setup failure remains separate from model outcomes.
visual: Control table for positive and negative cases; one-to-one matching rule and
  v1 packaging boundary.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Keep the three evidence conditions separate

```beat
id: limits
scene: limits
frames: 288
caption: Keep the three evidence conditions separate
narration: One reference miss, one matching point and one source-assisted negative
  are three selected workflow outcomes, with one attempt per case. Native-grid checks
  and saved-output replay preserve their interpretation. Clinical visibility, reference
  completeness, the cause of the miss and training overlap remain unresolved. No population
  accuracy or causal method ranking follows.
visual: Original TP/FP/FN by case, supported local observations and unresolved limits;
  all reference fields explicitly revealed.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```
