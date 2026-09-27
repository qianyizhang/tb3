---
schema: 2
id: mask-reasoning-study
title: Screen geometric shortcuts before trials
locale: en
purpose: Explain the retained author ordering and organ-template screens, their unequal
  assistance, and the boundary before model experiments.
scope: 'Retained BR-010/011 author study: 8 source patients, 24 anatomical groups
  and 131 organ instances. Source-derived sampled points; reader-only references.
  No new model trial or clinical adjudication.'
recipe: mask-screen-v1
asset_pack: retained-mask-screen-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-mask-reasoning-study.md
- docs/research-rounds/BR-010-mask-only-anatomy.md
- docs/evidence/br010-mask-reasoning-audit.json
- docs/research-rounds/BR-011-unlabeled-anatomy.md
- docs/evidence/br011-author-screen.json
- presentation/task-explorer/mask-screen/manifest.json
- scripts/build_mask_screen_assets.py
---

# Geometric shortcuts and their limits

## context

```beat
id: context
frames: 168
scene: context
caption: Existing traces already contain quantitative and relational reasoning.
narration: Seven targeted BR-010 trajectories contain inventories, morphology and
  relational checks. Terra solved the exchanged ribs. Sol surfaced a numeric signal
  in a controlled extension but still returned an empty answer; clinical significance
  remained unvalidated. The geometry here is case 32 context, not the case 28 rib-repair
  evidence.
visual: Show case-32 source ribs without predictions or references, alongside the
  counterexample and unresolved interpretation.
channels:
  measure:
  - 0
  - 0
  prediction:
  - 0
  - 0
  reference:
  - 0
  - 0
  focus:
  - 0
  - 0
```

## measure

```beat
id: measure
frames: 192
scene: ribs-32
caption: Measure the full-mask centroids in physical coordinates.
narration: This identity-audit baseline receives family membership and the proposed
  label multiset. It computes each intact object centroid in LPS millimetres, then
  orders the superior coordinates. It does not need to infer the family or unseen
  vertebral counts. The dashed guide connects centroids only; it is not anatomical
  connectivity.
visual: Reveal actual full-occupancy centroids over sampled left-rib surfaces.
channels:
  measure:
  - 0
  - 1
  prediction:
  - 0
  - 0
  reference:
  - 0
  - 0
  focus:
  - 0
  - 0
cut: intentional-cut
```

## sort

```beat
id: sort
frames: 240
scene: ribs-32
caption: Assign the supplied names by descending superior coordinate.
narration: The six left-rib objects retain their shape and relative arrangement. The
  output labels follow descending centroid height. This screen can undo whole-instance
  label permutations without a complete anatomical constraint solver. Genuine shortcuts
  remain allowed.
visual: Fill predicted labels by rank while traversing the six centroid locations.
channels:
  measure:
  - 1
  - 1
  prediction:
  - 0
  - 1
  reference:
  - 0
  - 0
  focus:
  - 0
  - 1
```

## compare

```beat
id: compare
frames: 120
scene: ribs-32
caption: Reveal source identities to evaluate the baseline.
narration: Every case-32 left-rib assignment matches its retained source. Across all
  eight patients, twenty-three of twenty-four lumbar or left/right rib groups are
  recovered by the same ordering. These are author groups, not independent model trials
  or a clinical accuracy estimate.
visual: Reveal six source labels beside the baseline assignments.
channels:
  measure:
  - 1
  - 1
  prediction:
  - 1
  - 1
  reference:
  - 0
  - 1
  focus:
  - 1
  - 1
```

## exception

```beat
id: exception
frames: 216
scene: ribs-74
caption: The one ordering exception needs coverage review.
narration: In source case 74, the left eighth and ninth rib centroids reverse order.
  The baseline assigns their names incorrectly. This limited-coverage exception is
  not a qualified difficult task. A planted permutation is not proof that a unique
  answer can be recovered from the solver inputs.
visual: Cut to actual case-74 left ribs, show the reversed ranks and two red source
  disagreements.
channels:
  measure:
  - 1
  - 1
  prediction:
  - 1
  - 1
  reference:
  - 1
  - 1
  focus:
  - 0.5
  - 0.72
cut: intentional-cut
```

## templates

```beat
id: templates
frames: 216
scene: organs-32
caption: A second baseline uses labeled examples from seven other patients.
narration: For each held-out patient, the classifier uses scan-normalized centroids,
  log physical volume and log bounding-box extents. Each class template is the coordinate-wise
  training median; training standard deviations scale squared distances. There is
  no parameter search or one-to-one assignment. Source labels are hidden in this view
  until comparison.
visual: Show the actual case-32 organ assembly and gradually assign the retained classifier
  predictions.
channels:
  measure:
  - 0
  - 0
  prediction:
  - 0
  - 1
  reference:
  - 0
  - 0
  focus:
  - 0
  - 0
cut: intentional-cut
```

## residual

```beat
id: residual
frames: 168
scene: organs-32
caption: 109 of 131 identities agree; no complete scene is correct.
narration: The case-32 spleen is predicted as stomach. Across eight patients, one
  hundred nine of one hundred thirty-one nonempty organ identities match source labels,
  but zero complete scenes pass. The author classifier has labeled training examples
  that the prototype solver does not receive. Its errors do not establish model difficulty
  or clinical truth.
visual: Reveal the spleen-to-stomach disagreement and all eight retained per-patient
  counts.
channels:
  measure:
  - 0
  - 0
  prediction:
  - 1
  - 1
  reference:
  - 0
  - 1
  focus:
  - 0
  - 0
```

## admission

```beat
id: admission
frames: 192
scene: admission
caption: Keep identity, annotation quality and unusual anatomy separate.
narration: Screen solved identity groups out as difficulty leads. The anonymous I2
  prototype still needs blind identity and ambiguity review. I3 requires verified
  unusual-anatomy context and separate identity, annotation and pattern assessments.
  A short mask alone cannot establish omitted tissue. Check alternative assignments
  and unchanged controls before any new trial.
visual: Hold the source disagreement and explicit admission decisions. These are author
  assessments, not new experiment outcomes.
channels:
  measure:
  - 0
  - 0
  prediction:
  - 1
  - 1
  reference:
  - 1
  - 1
  focus:
  - 0
  - 0
cut: intentional-cut
```
