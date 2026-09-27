---
schema: 2
id: dental-v2
title: 'Dental v2: what an annotated example transfers'
locale: en
purpose: Explain the same-target v2 comparison with saved example transfer, unchanged
  outputs, separate private-reference reveals and measured pulp/canal mechanisms.
scope: One F002 target; two Astra-medium attempts; unequal realized compute; native
  reader views and unresolved reference conventions.
recipe: dental-v2-v1
asset_pack: retained-dental-v2-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-dental-v2.md
- groups/anatomy-audit/presentation/sources/dental-v2-audit.json
- groups/anatomy-audit/experiments/dental-f002-contract-v2-astra-medium/protocol.md
- groups/anatomy-audit/experiments/dental-f002-reference-v2-astra-medium/protocol.md
- groups/anatomy-audit/methods/dental-reference-ablation/instruction.md
- groups/anatomy-audit/findings/dental-reference-example-comparison.md
- groups/anatomy-audit/findings/dental-fine-structure-failure-analysis.md
- scripts/audit_dental_v2_evidence.py
- scripts/build_dental_v2_assets.py
---

# Dental contract v2

## Same scan, dictionary and common contract

```beat
id: inputs
scene: inputs
frames: 192
caption: Same scan, dictionary and common contract
narration: Both independent Astra-medium attempts receive the complete F002 CBCT,
  seventy-seven possible foreground labels and the same revised contract. The dictionary
  names possible classes, not this target’s inventory. Target labels, previous answers
  and score feedback are withheld. Each attempt has a two-hour CPU ceiling and chooses
  its own method.
visual: Actual F002 native j150 input section without masks, beside the shared task
  dimensions and input boundary.
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

## Explicit names; preserve the native grid

```beat
id: contract
scene: contract
frames: 264
caption: Explicit names; preserve the native grid
narration: 'Version two makes increasing native i, j and k authoritative for Right,
  Posterior and Inferior semantic names. The original header and grid must still be
  preserved. One integer map assigns exclusive classes: mineralized tooth tissue and
  internal pulp have different IDs, whose union forms a whole tooth. This operational
  convention does not adjudicate acquisition laterality.'
visual: Unannotated CT and explicit native-axis and exclusive-label contract; no target
  reference.
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
narration: The assisted solver additionally receives a separate F008 CT and its original
  annotation. All thirty-two tooth and pulp pairs and five canals are labeled, but
  no restoration examples occur. The inventory and sampled views justified source
  selection, not a clinical normality certificate. The first run’s outputs or findings
  are not supplied.
visual: Separate target and example sections; reveal cyan supplied example contours
  without target annotation.
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

## Transfer a prior, then adapt it to the target

```beat
id: transfer
scene: transfer
frames: 336
caption: Transfer a prior, then adapt it to the target
narration: 'The assisted agent actually uses the example: affine and smooth registration,
  label transfer, jaw and tooth priors, and pulp calibration. This wipe compares target
  CT with example CT sampled by the saved displacement field. Purple contours are
  the saved transferred labels. Extra candidate teeth and imperfect boundaries still
  need adaptation. This is a reader comparison, not optimizer playback or a new registration.'
visual: Continuous wipe of target and saved-field-sampled F008 CT on the same native
  plane; transferred prior contours stay fixed. Retained method flow.
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

## Original answers before reference reveal

```beat
id: outputs
scene: outputs
frames: 240
caption: Original answers before reference reveal
narration: Here are the two saved answers on the same target section. Orange is the
  no-example output; cyan is the F008-assisted output. These contours union each tooth
  with its own pulp so geometry and numerical tooth identity can be read together.
  Both files pass native-grid validity. Neither valid output nor matching object count
  establishes correct anatomy.
visual: Two native k55 panels with unchanged saved tooth IDs. No target reference
  or score visible.
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

## Reveal the posterior identity difference

```beat
id: identity
scene: identity
frames: 288
caption: Reveal the posterior identity difference
narration: The private reference now appears separately. Reference teeth twenty-six
  and twenty-seven were named twenty-seven and twenty-eight without the example, but
  twenty-six and twenty-seven with it. Across the full volume, correctly detected
  and identified teeth increase from seventeen of twenty-two to nineteen of twenty-two.
  Reference tooth thirty-seven still matches output thirty-eight, and the baseline
  match is below the detection threshold.
visual: 'Three independently labeled panels, same posterior crop and grid: baseline,
  assisted, private target reference. Full-volume denominators below.'
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

## Gains coexist with lower pulp agreement

```beat
id: metrics
scene: metrics
frames: 336
caption: Gains coexist with lower pulp agreement
narration: Original macro Dice rises from point four-five-four to point five-zero-one,
  but the active label denominator changes from sixty-one to fifty-nine. A separately
  labeled common-label diagnostic retains the same sixty-one IDs and gives point four-eight-five
  for the assisted answer. Whole-tooth geometry changes little. Main and small canal
  scores improve, while pooled pulp agreement falls even when pulp IDs are ignored.
  Original scores remain unchanged.
visual: Source-derived whole-volume comparison table; original macro and common-union
  diagnostic visibly distinct.
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
  - 0
cut: intentional-cut
```

## The same pulp rule fails to transfer

```beat
id: pulp-rule
scene: pulp-rule
frames: 336
caption: The same pulp rule fails to transfer
narration: 'An author-only diagnostic applies the same fixed rule to internal tooth
  voxels: smoothed intensity below twelve-fifty and distance greater than two voxels
  from the tooth boundary. It gives pooled Dice point seven-six-five on the example’s
  matching tooth IDs, but only point two-nine-nine on true target tooth masks. These
  true target masks were never solver inputs. Predicted tooth masks give point two-eight-seven;
  envelope errors alone do not explain the loss.'
visual: Three measured bars on a common zero-to-one scale; target true-mask intervention
  explicitly author-only.
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

## Bright contents expose an unresolved convention

```beat
id: pulp-contents
scene: pulp-contents
frames: 336
caption: Bright contents expose an unresolved convention
narration: These two source-selected examples compare pulp labels one-sixteen and
  one-thirty-one. The target contains near-saturated voxels inside reference pulp
  labels, unlike the supplied example. The source contract does not fully settle occupied,
  treated or calcified chamber contents. The images establish an appearance mismatch,
  not material identity or clinically wrong labels. Excluding these IDs explains only
  part of the residual pulp disagreement.
visual: 'Two discrete native-section pairs, same intensity window and independent
  crop scales: authorized example annotation and assisted target output plus private
  reference.'
channels:
  view:
  - 0
  - 1
  helper:
  - 1
  - 1
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

## An inaccurate prior deletes correct pulp voxels

```beat
id: pulp-clip
scene: pulp-clip
frames: 432
caption: An inaccurate prior deletes correct pulp voxels
narration: For tooth fourteen, the agent removes pulp farther than three-and-a-half
  voxels, or one-point-zero-five millimetres, from a shifted transferred prior. Step
  through the saved pre-filter mask, prior allowance, deleted region and saved result.
  This exact rule removes four hundred forty of four hundred forty-three correctly
  placed voxels, leaving three. It also removes false positives. These full-region
  counts are reference agreement, not proof that removing the filter would be a safe
  repair.
visual: Four discrete stages on identical native j82 coordinates, with a dotted prior
  allowance and separate private-reference contour; no invented intermediate masks.
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

## Canal improvement still leaves low coverage

```beat
id: canals
scene: canals
frames: 336
caption: Canal improvement still leaves low coverage
narration: The assisted main-canal paths improve agreement but remain offset and incomplete
  in these two native sections. Full-volume reference recall rises from eight to fourteen
  percent. Only about twenty and forty-four percent of assisted main-canal path samples
  lie inside their respective references. Most missed reference voxels already lie
  outside the uncut tubes; final assembly is not the principal source of these misses.
visual: Both unchanged outputs beside one another with private reference overlays;
  switch between actual j145 and j205 sections.
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

## Placement and width are different problems

```beat
id: small-canals
scene: small-canals
frames: 288
caption: Placement and width are different problems
narration: Small canals show different failures. Label one-zero-three has useful placement
  but incomplete coverage. Label one-zero-four has zero overlap in the saved answer.
  Enlarging a tube can improve a post-hoc overlap diagnostic without solving localization.
  Across all small canals, assisted pooled recall remains about eight-and-a-half percent.
  Selected sections illustrate the distinction; full-volume measurements establish
  the counts.
visual: Switch between exact native sections of canals 103 and 104; unchanged outputs
  and private reference remain separately styled.
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

## One informative pair, with qualified conclusions

```beat
id: limits
scene: limits
frames: 264
caption: One informative pair, with qualified conclusions
narration: 'The example was used and some measures improved, while pulp agreement
  declined. One attempt per condition on a development case cannot establish a population
  effect or isolate assistance from different methods and realized compute: twenty-three
  versus forty-nine minutes. Acquisition laterality, restoration subtypes and occupied-pulp
  conventions remain under review. The source audit replays all six saved model and
  control evaluations exactly; it performs no new medical attempt.'
visual: Concise limits and evidence boundaries; original arrays and scores retained.
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
