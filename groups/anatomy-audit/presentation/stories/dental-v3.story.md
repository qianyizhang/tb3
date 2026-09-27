---
schema: 2
id: dental-v3
title: 'Dental v3: how far refinement can reach'
locale: en
purpose: Explain a retained same-target comparison through saved label transfer, pulp
  eligibility and bounded canal refinement, separating aggregate gains from counterexamples.
scope: One F018 development pair; unequal compute; private-reference reveals; untested conventions.
recipe: dental-v3-v1
asset_pack: retained-dental-v3-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-dental-v3.md
- groups/anatomy-audit/presentation/sources/dental-v3-audit.json
- groups/anatomy-audit/experiments/dental-f018-contract-v3-astra-medium/protocol.md
- groups/anatomy-audit/experiments/dental-f018-reference-v3-astra-medium/protocol.md
- groups/anatomy-audit/methods/dental-f018-contract-v3/instruction.md
- groups/anatomy-audit/findings/dental-f018-contract-v3-comparison.md
- groups/anatomy-audit/findings/dental-dataset-contract-audit.md
- scripts/audit_dental_v3_evidence.py
- scripts/build_dental_v3_assets.py
---

# Dental contract v3

## Same complete target, dictionary and v3 contract

```beat
id: inputs
scene: inputs
frames: 192
caption: Same complete target, dictionary and v3 contract
narration: Two independent Astra-medium attempts receive the complete F018 CBCT, the
  same sparse dictionary and the same compartment rules. Seventy-seven possible foreground
  IDs do not reveal which classes occur in this target. Private target labels, earlier
  answers and evaluation feedback are withheld. Both attempts have the same two-hour
  CPU ceiling and choose their own methods.
visual: Native unannotated F018 j150 section beside the common input contract; no
  output or target reference.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
  stage:
  - 0
  - 0
```

## Explicit compartments; unchanged native geometry

```beat
id: contract
scene: contract
frames: 288
caption: Explicit compartments; unchanged native geometry
narration: The v3 contract separates mineralized tooth tissue from supported internal
  pulp space, including occupied portions when the compartment is supported. It also
  states jaw, canal, cavity and restoration boundaries. One exclusive integer map
  must preserve the source grid and metadata. Native i, j and k name Right, Posterior
  and Inferior operationally; this does not adjudicate acquisition laterality or guarantee
  that source GT follows every convention.
visual: Unannotated target section with explicit compartment and semantic-axis rules,
  independently preserved header metadata.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Only one condition receives annotated F008

```beat
id: example
scene: example
frames: 240
caption: Only one condition receives annotated F008
narration: The assisted condition additionally receives a separate F008 CT and its
  original dense annotation. It has different anatomy and depth, but the same dictionary
  and semantic naming contract. This is permitted assistance, not the target reference.
  The example’s inventory must not be assumed to describe the target. The full volumes
  are provided; the displayed sections are selected for readers.
visual: Side-by-side actual target and example CT sections. Reveal only the supplied
  F008 contours.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 1
  transfer:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Use the saved map to compare transferred anatomy

```beat
id: transfer
scene: transfer
frames: 336
caption: Use the saved map to compare transferred anatomy
narration: The assisted agent registers the example, transfers labels, corrects tooth
  correspondences and an impacted molar’s orientation, then refines against target
  intensities. This wipe replaces target CT with example CT sampled by the saved final
  pull map. Purple contours show the transferred prior. The entire atlas and warped-CT
  plane reproduce exactly. The wipe is a reader comparison, not an animation of optimizer
  iterations or a new registration.
visual: Continuous target-versus-warped-example CT wipe on native k55; fixed saved
  atlas contours and actual method stages.
channels:
  view:
  - 0
  - 0
  helper:
  - 1
  - 1
  transfer:
  - 0
  - 1
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the original answers before revealing reference

```beat
id: outputs
scene: outputs
frames: 240
caption: Inspect the original answers before revealing reference
narration: Orange is the no-example answer and cyan is the F008-assisted answer on
  the same native target section. Each is the original submitted exclusive label map.
  Both pass the frozen shape, affine, header and label validity checks. That establishes
  valid files, not correct anatomy. Target-reference contours and quantitative measurements
  remain hidden here.
visual: Unchanged saved whole-section outputs on native j150. Target reference and
  scores absent.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 0
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Reveal whole-tooth shape separately from identity

```beat
id: shape
scene: shape
frames: 288
caption: Reveal whole-tooth shape separately from identity
narration: The private target reference now appears as a dashed green contour. Whole-tooth
  geometry unions mineralized tissue with its corresponding pulp. Across the full
  volume, geometry Dice rises from point seven-eight-five to point nine-two-six. Both
  conditions already detect and correctly name all twenty-nine reference teeth. In
  this pair, the difference is shape agreement, not a correction of tooth numbering.
visual: Same native k55 crop with independent baseline and assisted panels, explicit
  reference reveal and full-volume shape/identity counts.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Matched denominators; gains with residual disagreement

```beat
id: metrics
scene: metrics
frames: 336
caption: Matched denominators; gains with residual disagreement
narration: Original macro Dice rises from point seven-one-one to point eight-two-four
  using the same sixty-eight active labels in both arms. Pulp macro and pooled agreement
  also improve, while main and small canals remain weak. Macro averages classes; pooled
  Dice weights voxels. Nine both-empty labels do not inflate the mean. No restoration
  class is present in the reference or either output, so these results do not test
  restoration performance.
visual: Source-derived full-volume comparison table with unchanged original metrics
  and explicit denominators.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
  stage:
  - 0
  - 0
cut: intentional-cut
```

## A selected pulp success within a mixed result

```beat
id: pulp-gain
scene: pulp-gain
frames: 336
caption: A selected pulp success within a mixed result
narration: Pulp label one-twenty-two has the largest Dice gain, from point three-three-three
  to point eight-five-five. Two native sections illustrate the improved agreement;
  the number is measured over the whole volume. Twenty of twenty-nine pulp labels
  improve. Pooled pulp precision rises from fifty-five-point-five to seventy-four-point-six
  percent, while recall rises from eighty-seven-point-six to eighty-nine-point-seven
  percent. This is a selected success, not a universal outcome.
visual: Two discrete native j43 and j50 views, paired original outputs and private
  reference. No invented intermediate section.
channels:
  view:
  - 0
  - 1
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Pulp 127 is a concrete counterexample

```beat
id: pulp-loss
scene: pulp-loss
frames: 336
caption: Pulp 127 is a concrete counterexample
narration: Pulp one-twenty-seven declines from Dice point seven-five-eight to point
  one-eight-six. The transferred prior overlaps none of the eight hundred twenty-seven
  reference voxels. Later refinement recovers some, but the final answer overlaps
  only one hundred fifteen. Three native sections show the mismatch. Better aggregate
  pulp agreement does not remove this local loss, and a reference disagreement is
  not itself a clinical adjudication.
visual: Three discrete j156, j160 and j162 sections compare unchanged baseline and
  assisted masks against private target reference.
channels:
  view:
  - 0
  - 1
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Replay the saved refinement and its geometric limit

```beat
id: pulp-reach
scene: pulp-reach
frames: 432
caption: Replay the saved refinement and its geometric limit
narration: Step through the transferred prior, saved initial pulp, allowed region,
  intensity-selected addition and final mask. Expansion must remain inside the preceding
  whole tooth, at least two-and-a-half voxels deep and within six voxels of the prior.
  The initial mask plus geometrically eligible region reaches only one hundred twenty-eight
  of eight hundred twenty-seven reference voxels before intensity filtering. The final
  mask reaches one hundred fifteen. These exact saved operations establish limited
  reach; overlapping restrictions are not additive losses or proof of one unique upstream
  cause.
visual: Five discrete saved or exactly reconstructed stages on fixed j156/j160 sections.
  Gold even-odd fill marks the actual eligible region including its holes; counts
  cover the full source crop and target label.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
  stage:
  - 0
  - 1
cut: intentional-cut
```

## A crop outside the reference cannot recover that canal

```beat
id: canal-crop
scene: canal-crop
frames: 432
caption: A crop outside the reference cannot recover that canal
narration: For canal one-zero-four, the assisted algorithm searches only the transferred
  prior’s bounding box plus four voxels. That crop contains zero of the three hundred
  fifty-five reference voxels. Refinement changes the prior from one hundred eighty-nine
  to two hundred three voxels but cannot reach the reference region. Native sections
  provide CT context, and an all-depth silhouette shows the complete separation. The
  historical six-voxel proximity diagnostic is a different measure, not this algorithm’s
  search radius.
visual: Three discrete native k201/k204/k207 sections beside a complete along-k silhouette.
  Exact fixed search box, saved prior, final mask and private reference have separate
  matching styles.
channels:
  view:
  - 0
  - 1
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
  stage:
  - 0
  - 0
cut: intentional-cut
```

## Better overlap can coexist with worse extent

```beat
id: canal-extent
scene: canal-extent
frames: 336
caption: Better overlap can coexist with worse extent
narration: For main canal four, Dice improves from point three-three-one to point
  four-three-nine, while HD95 worsens from three-point-zero-nine to seven-point-three-two
  millimetres. These silhouettes collapse each full native axis in turn. They show
  complete mask extent, not CT or three-dimensional overlap; silhouettes can overlap
  at different depths. The disagreement between overlap and tail surface distance
  is why one score is insufficient.
visual: Paired complete-axis canal-4 silhouettes switch discretely along i, j and
  k, with source-derived Dice and HD95 endpoints.
channels:
  view:
  - 0
  - 1
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
  stage:
  - 0
  - 0
cut: intentional-cut
```

## One informative development pair; explicit untested claims

```beat
id: limits
scene: limits
frames: 288
caption: One informative development pair; explicit untested claims
narration: 'This is one attempt per condition on a repeatedly examined development
  case. Chosen methods and realized compute differ: about twenty-four and twenty-nine
  minutes. The pair does not isolate a population benefit or the effect of revising
  the instructions. No restoration class and no confidently identified treated occupied
  pulp validate the new conventions here. Annotation intent and physical laterality
  remain under review. Original outputs and scores are preserved; this explanation
  replays saved evidence without a new medical attempt.'
visual: Matched contract, unequal execution, untested definitions and retained-evidence
  limits; no clinical or population conclusion.
channels:
  view:
  - 0
  - 0
  helper:
  - 0
  - 0
  transfer:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
  stage:
  - 0
  - 0
cut: intentional-cut
```
