---
schema: 2
id: ct-organ-segmentation
title: 'CT organs: construct masks, assign names and review boundaries'
locale: en
purpose: Explain native CT-only segmentation and the separate skill/tool condition
  through saved contours and actual image-conditioned candidates.
scope: One public CT · four attempts · reader-selected sections · separate private-reference
  reveal.
recipe: ct-organ-v1
asset_pack: retained-ct-organ-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-ct-organ-segmentation.md
- groups/anatomy-audit/presentation/sources/ct-organ-audit.json
- groups/anatomy-audit/findings/ct-organ-three-condition-comparison.md
- groups/anatomy-audit/findings/ct-organ-segmentation-astra-medium-litemedsam.md
- groups/anatomy-audit/findings/ct-organ-slice-construction-audit.md
- scripts/build_ct_organ_assets.py
---

# Native CT organ segmentation

## Full CT and ten definitions; no organ locations

```beat
id: inputs
scene: inputs
frames: 192
caption: Full CT and ten definitions; no organ locations
narration: The solver receives the complete native CT, ten target definitions and
  the output conventions. The centre section shown here is a reader view, not a supplied
  detection. There are no masks or private scores in the baseline packet. Three standalone
  attempts use scientific imaging libraries; a fourth condition adds a generic skill
  and callable LiteMedSAM.
visual: Actual unannotated native coronal section and full numeric target dictionary.
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

## Save ten independent binary masks on the native grid

```beat
id: contract
scene: contract
frames: 168
caption: Save ten independent binary masks on the native grid
narration: The answer is ten binary NIfTI masks and a method note, not one exclusive
  label volume. Preserve the input shape and affine, and use patient anatomy for right
  and left. Organ envelopes include the specified contents. The source masks overlap
  at fifty-seven voxels; keeping separate masks avoids an arbitrary priority rule.
  This overlap count was private to evaluation.
visual: Keep CT unannotated; show all ten filenames, target names and independent-mask
  contract.
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

## Draw anchors, interpolate geometry, then refine

```beat
id: polygon
scene: polygon
frames: 240
caption: Draw anchors, interpolate geometry, then refine
narration: These are six actual stomach sections from native k two hundred thirty-five
  through two hundred forty. Astra medium explicitly draws the two endpoint polygons.
  Between them, the baseline interpolates signed-distance fields. The left contours
  reconstruct those stored coordinates; the right contours are final submitted masks
  after processing. They are numerical stages with final decisions fixed, not a learning
  curve.
visual: Step all six native planes; label endpoint versus between-anchor class. Raw
  polygon outline dashed purple; final baseline orange.
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

## Interpolate boxes; infer each contour from its own image

```beat
id: tool
scene: tool
frames: 240
caption: Interpolate boxes; infer each contour from its own image
narration: The tool condition uses explicit boxes at both endpoints and interpolated
  boxes on the four interior planes. Every plane still has its own CT image and learned
  mask prediction. Purple rectangles are saved prompts; cyan contours are saved candidates
  and final masks. The agent assigns the organ ID, selects prompts and later unions
  candidates with cleanup. The segmenter receives an image and rectangle, not an anatomical
  name.
visual: The same six sections show exact saved prompt boxes, stored candidate masks
  and final tool output; no new inference.
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

## The submitted stomach masks differ before reference reveal

```beat
id: output
scene: output
frames: 192
caption: The submitted stomach masks differ before reference reveal
narration: Inspect both saved stomach masks on the same native section. Orange is
  standalone Astra medium; cyan is Astra medium with the skill and tool. The reference
  and scores remain hidden. This maximum-reference-area section and crop were selected
  only after submission for reader comparison; they were not hints supplied to either
  solver.
visual: Show both saved masks on identical native CT crops; no reference contour or
  score.
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

## Reveal the private stomach contour and full-volume score

```beat
id: reference
scene: reference
frames: 240
caption: Reveal the private stomach contour and full-volume score
narration: The green dashed outline is the private research reference. Stomach whole-volume
  Dice improves from zero point six six four to zero point eight eight eight. This
  chosen section illustrates the boundary difference, but the score includes the entire
  three-dimensional organ. Human-reviewed source labels are useful research references,
  with possible residual errors and no new clinical adjudication here.
visual: Reveal matching green dashed reference on both panels midway through the beat;
  only then expose full 3D scores.
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

## Gallbladder, pancreas and right adrenal regress

```beat
id: regressions
scene: regressions
frames: 360
caption: Gallbladder, pancreas and right adrenal regress
narration: 'The mean gain does not apply to every organ. Cycle through the three regressions:
  gallbladder, pancreas and right adrenal. The saved prompt union covers about sixty-six
  percent of gallbladder reference voxels and twenty-four percent of right adrenal.
  These are post-submission localization diagnostics, not prompts or feedback given
  to the agent. A box is not a hard mask boundary or mathematical score ceiling.'
visual: Hold each of the three actual reference-selected comparison sections for five
  seconds, with complete 3D Dice.
channels:
  view:
  - 0
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Keep all ten organ outcomes visible

```beat
id: inventory
scene: inventory
frames: 480
caption: Keep all ten organ outcomes visible
narration: Cycle through all ten named outputs. Seven whole-organ Dice values improve
  and three worsen in the tool condition. Both Astra medium outputs retain ten positive-overlap
  matched identities, which does not certify each boundary voxel. The same crop and
  private reference are used within every pair. These selected planes make the comparison
  inspectable without pretending to be a full clinical review of the volume.
visual: Show every organ in dictionary order for two seconds; preserve condition colors
  and private-reference line style.
channels:
  view:
  - 0
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Semantic overlap and recoverable geometry answer different questions

```beat
id: comparison
scene: comparison
frames: 240
caption: Semantic overlap and recoverable geometry answer different questions
narration: Semantic macro Dice gives all ten named organs equal weight. Matched Dice
  permits the best one-to-one relabelling. Sol increases only from zero point three
  two nine to zero point three four nine after matching, so renaming alone cannot
  repair its geometry and localization. The three standalone attempts share task bytes;
  the tool condition changes instruction, skill and runtime. These are descriptive
  single-case results.
visual: Display all four original semantic and matched means; no invented confidence
  intervals or population ranking.
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

## Fix baseline slice sets before comparing construction quality

```beat
id: slices
scene: slices
frames: 240
caption: Fix baseline slice sets before comparing construction quality
narration: A directly authored plane is not the same as a displayed plane or a corrected
  contour. Comparing both final masks on the same baseline-defined sets improves organ-balanced
  Dice from zero point seven three five to zero point seven five zero on anchors,
  and zero point seven four two to zero point seven seven two between anchors. These
  are conditional diagnostics; the nine outside-extent pairs stay separate. Correlated
  planes are not independent patients.
visual: Show 119 anchor and 372 between-anchor pairs with equal-organ means and the
  separate nine-pair exception.
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

## Separate localization, contours, naming and orchestration

```beat
id: limits
scene: limits
frames: 192
caption: Separate localization, contours, naming and orchestration
narration: 'One public case and one attempt per condition support a useful local observation:
  the tool condition improves seven organs while three regress. They cannot establish
  general model ranking, a causal tool advantage or clinical accuracy. Original scores
  remain unchanged. Eight saved model and control evaluations replay exactly, and
  the independent slice audit reproduces forty organ scores. No new inference occurs.'
visual: End with the supported conclusion, reference uncertainty, unknown training
  overlap and audited execution count.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```
