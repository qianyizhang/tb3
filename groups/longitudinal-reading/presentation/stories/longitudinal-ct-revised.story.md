---
schema: 2
id: longitudinal-ct-revised
title: 'Revised CT: include, partition, then track'
locale: en
purpose: Explain generic inclusion and instance rules, broad supplied context, native
  saved decisions and complete event denominators.
scope: Three retained Astra medium attempts across two purposively selected CT pairs.
  Reader-selected crops and private references remove search; saved-score replay is
  not a new trial.
recipe: longitudinal-ct-revised-v1
asset_pack: retained-longitudinal-ct-revised-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-revised.md
- groups/longitudinal-reading/presentation/sources/longitudinal-ct-revised-audit.json
- groups/longitudinal-reading/methods/longitudinal-ct-image-only-v2/instruction.md
- groups/longitudinal-reading/methods/longitudinal-ct-context-v1/context-block.md
- groups/longitudinal-reading/findings/longitudinal-ct-v2-and-localized.json
- groups/longitudinal-reading/findings/longitudinal-ct-case02-astra-medium-result.json
- groups/longitudinal-reading/findings/longitudinal-ct-context-hypothesis-result.json
- scripts/build_longitudinal_ct_revised_assets.py
---

# Revised decisions without target hints

## Start from full native volumes, without target hints

```beat
id: inputs
scene: inputs
frames: 216
caption: Start from full native volumes, without target hints
narration: The three retained attempts used Astra medium and the same private scorer.
  Revised image-only instructions were applied to each of two selected CT pairs. The
  second pair was also attempted with broad clinical context. These middle slices
  preview complete volumes; no target locations, counts, masks or prior answers were
  supplied.
visual: Four actual native middle slices, visit shapes and measured slice spacing.
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

## Make inclusion and instance rules explicit

```beat
id: rules
scene: rules
frames: 240
caption: Make inclusion and instance rules explicit
narration: Include findings judged more likely tumor, even without diagnostic certainty.
  Exclude findings judged more likely normal or benign. For uncertainty, record a
  native location, inclusion decision and reason. Distinguishable touching lesions
  receive separate local IDs; one connected foreground region is not automatically
  one instance. Neither rule supplies a target.
visual: Five generic rules with no private patient targets.
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

## Inspect what the revised first-case output changed

```beat
id: partition
scene: partition
frames: 264
caption: Inspect what the revised first-case output changed
narration: Compare original amber and revised purple masks on the same three native
  baseline sections. The revised result localizes three of six source instances rather
  than two, and two of four links rather than one. Neither recovers a complete reference
  event. The separate focus remains omitted, and fine-instance adjudication remains
  open. Two changed rules plus a fresh run do not establish prompt causality.
visual: Advance k108,116,120; actual saved local-ID labels, cyan private boundaries.
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

## Separate foreground overlap from complete discovery

```beat
id: inventory
scene: inventory
frames: 216
caption: Separate foreground overlap from complete discovery
narration: On the second case, one identity supplies about eighty-five percent of
  baseline and ninety-five percent of follow-up reference volume. The saved mask covers
  much of this large lesion. Useful foreground Dice therefore coexists with many undetected
  smaller lesions. These reference-selected crops remove the original localization
  search; they do not depict registered visits.
visual: Reveal saved purple contours on the two native source-ID-4 crops.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Retain every visit instance in the denominator

```beat
id: size
scene: size
frames: 240
caption: Retain every visit instance in the denominator
narration: The second pair has seven baseline and fifteen follow-up reference instances.
  Both conditions recover the same three. By native reference volume, they localize
  zero of eleven at or below one milliliter, one of nine above one through ten, and
  both larger instances. The two large annotations represent one lesion at two visits,
  not two independent patients.
visual: Reference ID rows and three volume strata; reveal matched fills.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Distinguish patient metadata from cohort background

```beat
id: context
scene: context
frames: 240
caption: Distinguish patient metadata from cohort background
narration: The supplied block contains released age forty-four, recorded sex female
  and a hundred-twenty-one-day interval. Age reference date is unspecified. Cohort
  background states metastatic melanoma and systemic therapy. No individual clinical
  report, regimen, surgery dates or lesion hints are supplied. The pinned prompt verifies
  delivery, but retained discussion does not establish how each field was used.
visual: List exactly supplied broad context and missing individual context.
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

## Read an exclusion before revealing its source label

```beat
id: decisions
scene: decisions
frames: 240
caption: Read an exclusion before revealing its source label
narration: 'The context report identifies these native points and favors a benign
  cyst-like or vascular explanation. Amber crosses locate its reported exclusions.
  Now reveal the cyan source boundaries: both points lie inside reference identity
  two, with no coverage by the context masks. This is an explicit report-reference
  disagreement; the teaching display does not clinically adjudicate the diagnosis.'
visual: Two report-selected crops; amber native-coordinate crosses first, cyan source
  masks separately.
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

## Accept uncertainty and inspect the saved boundary

```beat
id: focus
scene: newfocus
frames: 240
caption: Accept uncertainty and inspect the saved boundary
narration: Both reports include this small follow-up focus despite a possible benign
  cyst. Local output ID two matches source thirteen. Three native sections show the
  image-only purple and context amber contours. Instance Dice changes from point five
  seven nine to point seven three five, while the detected identity stays the same.
  The source one-voxel satellite remains part of its original instance.
visual: Advance k527,529,531 with actual CT, saved contours, local IDs and cyan source
  boundary.
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

## Interpret conditional events with their eligibility

```beat
id: events
scene: events
frames: 240
caption: Interpret conditional events with their eligibility
narration: Each second-case output contains a persistent group and a newly appearing
  group. Every positive mask ID belongs to exactly one event. After reference matching,
  one of seven links and two of fifteen events are correct. Conditional scores of
  one of one and two of two apply only to detected eligible endpoints; they exclude
  thirteen other reference groups.
visual: Saved local-ID groups first, private totals revealed separately.
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

## Keep detection and overlap outcomes separate

```beat
id: compare
scene: comparison
frames: 240
caption: Keep detection and overlap outcomes separate
narration: Contours differ between the retained attempts, without a gained detected reference
  identity in this pair. Both attempts recover three of twenty-two instances, one of seven
  links and two of fifteen events. Foreground Dice decreases while equal-instance
  Dice slightly increases. Zero instance false positives does not mean zero excess
  segmented tissue. One attempt each cannot isolate context effects or rule out a
  benefit from complete clinical reports.
visual: Show exact disaggregated image-only and context metrics with denominators.
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

## Return a complete inspectable answer

```beat
id: output
scene: output
frames: 216
caption: Return a complete inspectable answer
narration: Return two native integer instance masks, an events document and a report.
  Preserve exact grids and affines, use background zero and local positive IDs, and
  assign every ID to one event. Document uncertain candidates, native coordinates
  and reasons; retain useful scripts and views. This revision requires no probability
  sidecar. Empty outputs can be mechanically valid without scientific success.
visual: Four output files, evidence coordinates and the schema-versus-science boundary.
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

## Preserve the scope of these diagnostic comparisons

```beat
id: limits
scene: limits
frames: 216
caption: Preserve the scope of these diagnostic comparisons
narration: The first-case instance convention remains under review. The second case
  was selected purposively and contains persistence and new events, but no merging
  or disappearance. Broad context is not a full clinical report. These are public-source,
  single-attempt diagnostic comparisons. Replaying the three saved score sets preserves
  their original values; it is not new inference or a clinical response assessment.
visual: Close on case selection, clinical context, source exposure and unchanged scientific
  evidence.
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
