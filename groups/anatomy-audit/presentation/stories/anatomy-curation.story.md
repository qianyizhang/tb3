---
schema: 2
id: anatomy-curation
title: Curate anatomy before claiming a difficult task
locale: en
purpose: Explain how source context, geometric shortcuts and reference ambiguity determine
  five pre-trial curation decisions.
scope: 'Retained BR-012 author screen: six patients, seven source volumes and 145 annotated
  instances including three overlapping identities. Source-derived boundary points and reader-only
  references. Zero admitted hard tasks and zero model trials.'
recipe: anatomy-curation-v1
asset_pack: retained-anatomy-curation-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-anatomy-curation.md
- docs/research-rounds/BR-012-anatomy-curation.md
- docs/evidence/br012-curation.json
- presentation/task-explorer/anatomy-curation/manifest.json
- scripts/build_anatomy_curation_assets.py
---

# Source curation and task admission

## count

```beat
id: count
frames: 240
scene: pair
caption: Two patients can have 25 vertebrae and different regional identities.
narration: The retained author study acquired seven masks, seven centroid files and seven
  source preview images from six patients. These two patients both contribute twenty-five
  vertebral objects. Their masks contain no ribs or sacrum, and equal counts do not identify
  the thoracic-lumbar boundary. The scans are independently fitted; this is not a matched
  intervention.
visual: Traverse anonymous source objects in 547 and 585 with reference names hidden.
channels:
  reference:
  - 0
  - 0
  focus:
  - 0
  - 0.49
```

## partition

```beat
id: partition
frames: 264
scene: pair
caption: Reveal the source partitions and the assistance given to each baseline.
narration: 547 has seven cervical, thirteen thoracic and five lumbar labels. 585 has seven
  cervical, twelve thoracic and six lumbar labels. Sorting the supplied label multiset recovers
  both exactly. A fixed twelve-thoracic sequence, even with the true top anchor, recovers
  nineteen of twenty-five in 547 and all twenty-five in 585. Different sampling and missing
  context limit a mask-only recognition claim.
visual: Reveal source region colors and counts, both baseline scores and voxel spacings.
channels:
  reference:
  - 0
  - 1
  focus:
  - 0.49
  - 1
```

## preserve

```beat
id: preserve
frames: 264
scene: preservation
caption: An unusual shape is not automatically an annotation error.
narration: The focused source view preserves 406 lower-scan T9, T10 and T11 in their original
  relative arrangement. Their full-mask volumes are 37.49, 13.79 and 45.17 millilitres. T10
  is about one third of its neighbors mean volume. This descriptive check followed visual
  inspection; it is not an independent predeclared baseline. Neither size nor shape alone
  establishes a disease or an annotation error.
visual: Cut to the three real vertebral point clouds and highlight T10 beside exact source-volume
  measurements.
channels:
  reference:
  - 1
  - 1
  focus:
  - 0
  - 0
cut: intentional-cut
```

## overlap

```beat
id: overlap
frames: 240
scene: overlap
caption: Keep overlapping source grids and the unresolved C1 discrepancy separate.
narration: 406 upper has nine identities and lower has nineteen. C7, T1 and T2 overlap, but
  the separate image grids have not been validated for fusion. The upper mask contains C1
  without a matching centroid entry. The cause is unresolved, so this is not an unquestioned
  anchor key. Assumed segment structure and segmented counts remain distinct.
visual: Show the separate upper source scan and its annotation-membership limitation.
channels:
  reference:
  - 1
  - 1
  focus:
  - 0
  - 1
cut: intentional-cut
```

## calibrate

```beat
id: calibrate
frames: 192
scene: calibration
caption: Typical numbering supports a control, not a pathology-free verdict.
narration: 823 supplies twenty-four identities in a seven-cervical, twelve-thoracic, five-lumbar
  pattern. Both anchored ordering screens recover all twenty-four. Retain it for calibration.
  Typical enumeration does not certify absence of all pathology or establish a difficult recognition
  task.
visual: Show all 24 source objects with their source regions, alongside the calibration decision.
channels:
  reference:
  - 1
  - 1
  focus:
  - 0
  - 1
cut: intentional-cut
```

## reserve

```beat
id: reserve
frames: 216
scene: reserve
caption: Reserve cropped anatomy until coverage, anchors and nomenclature are checked.
narration: 642 has C5 through C7, eleven thoracic and six lumbar source objects. Supplied-multiset
  sorting recovers twenty of twenty; fixed twelve-thoracic sorting with the true top anchor
  recovers fourteen. Missing upper cervical coverage, approximately three-millimetre left-right
  sampling and absent rib or sacral masks keep the case in reserve.
visual: Show actual cropped 642 geometry and the separate coverage and baseline limitations.
channels:
  reference:
  - 1
  - 1
  focus:
  - 0
  - 1
cut: intentional-cut
```

## ambiguity

```beat
id: ambiguity
frames: 240
scene: ambiguity
caption: Reject an exact key when the source itself admits ambiguity.
narration: The paper explicitly calls 581 ambiguous and reports Castellvi category 3b. It
  assumes six lumbar levels but segments only five lumbar instances. Partly sacral-fused vertebrae
  may intentionally be unsegmented. This is not an injected or discovered missing-object defect.
  A future uncertainty task needs a defensible acceptable-answer set and independent review.
visual: Show source 581 masks with the rejection decision and source omission policy.
channels:
  reference:
  - 1
  - 1
  focus:
  - 0
  - 1
cut: intentional-cut
```

## admission

```beat
id: admission
frames: 264
scene: admission
caption: Five candidate cards, zero admitted hard tasks, zero model trials.
narration: Across seven volumes the supplied-multiset sort recovers 145 of 145 annotated instances,
  and the fixed-twelve-thoracic rule recovers 128. The denominator includes three repeated
  identities in 406. The outputs are candidate cards and admission limits. No clinical gold,
  injected-error controls, or blind expert adjudication was added. Reopen with missing anatomical
  context, input-only identifiability review, acceptable-answer rules and verified controls.
visual: Return to the recognition pair beside all five curation decisions and reopening conditions.
channels:
  reference:
  - 1
  - 1
  focus:
  - 0
  - 1
cut: intentional-cut
```
