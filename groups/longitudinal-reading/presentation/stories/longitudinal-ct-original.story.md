---
schema: 2
id: longitudinal-ct-original
title: 'Original CT: find instances, then link events'
locale: en
purpose: Explain image-only discovery, native instance maps, local-ID matching, complete
  event groups and the unresolved confluence convention.
scope: One selected Longitudinal-CT v3 pair and two retained original-task attempts.
  Native reader crops, saved masks and private references are separate; saved-score
  replay is not a new trial.
recipe: longitudinal-ct-original-v1
asset_pack: retained-longitudinal-ct-original-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-original.md
- groups/longitudinal-reading/presentation/sources/longitudinal-ct-original-audit.json
- groups/longitudinal-reading/methods/longitudinal-ct-image-only/instruction.md
- groups/longitudinal-reading/methods/longitudinal-ct-image-only/score.py
- groups/longitudinal-reading/findings/longitudinal-ct-image-only-comparison.json
- groups/longitudinal-reading/examples/longitudinal-ct-instance-boundary-review.md
- scripts/build_longitudinal_ct_original_assets.py
---

# Find instances before interpreting temporal events

## Start with two full native CT volumes

```beat
id: inputs
scene: inputs
frames: 192
caption: Start with two full native CT volumes
narration: The solver receives baseline and follow-up CT volumes, without lesion locations,
  counts, masks, links or clinical history. Native shapes and affines are preserved.
  CPU image tools are available, but no pretrained weights or external dataset lookup.
  These middle slices only preview the complete search space.
visual: Two native middle slices with shapes, scale and patient orientation.
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

## Return native instance maps

```beat
id: instances
scene: instances
frames: 216
caption: Return native instance maps
narration: 'Assign each visible tumor instance a local integer ID and preserve the
  exact grid at each visit. Reveal the saved Astra masks: one ID per visit, shown
  in output-selected crops. Equal numbers across visits do not prove identity. Extent,
  instance partition and correspondence are separate outputs.'
visual: Reveal amber actual saved contours on independently selected native crops.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Inspect the unresolved instance convention

```beat
id: partition
scene: partition
frames: 264
caption: Inspect the unresolved instance convention
narration: Now reveal reference-selected baseline crops. Three source labels share
  one connected foreground component. The original instruction calls a confluent region
  one instance, while the reference keeps these labels separate. The six slices show
  voxel geometry. Contact alone does not establish clinical confluence or invalidate
  expert labels; this convention remains under review.
visual: Advance six native sections with cyan, pink and blue reference boundaries
  and amber saved output.
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

## Separate an omitted focus from under-partitioning

```beat
id: focus
scene: focus
frames: 216
caption: Separate an omitted focus from under-partitioning
narration: A second reference focus appears in both visits, with no coverage in the
  saved Astra masks. Green outlines reveal B3 and F3 in reader-selected crops. These
  crops remove localization search. Native slice numbers and physical coordinates
  differ across unregistered visits; this display does not establish what the model
  recognized or attended to.
visual: Reveal the separate source focus at native k213 and k216 with no saved mask
  coverage.
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

## Map local IDs with the frozen detection rule

```beat
id: matching
scene: matching
frames: 240
caption: Map local IDs with the frozen detection rule
narration: 'The private detector accepts a predicted centroid inside a reference,
  or within three millimetres of a labeled reference voxel center. It assigns matches
  one to one. Astra local one maps to reference four at each visit: two of six instances
  localized. Foreground Dice ignores partitions; GT-macro instance Dice includes zeros
  for missed references.'
visual: Show the centroid-to-mask rule, physical units and the two local-ID mappings.
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

## Score links with the eligible denominator

```beat
id: links
scene: links
frames: 216
caption: Score links with the eligible denominator
narration: 'The reference contains four edges. After detection, the saved Astra relation
  maps to B4 to F4: one correct edge out of four end to end. Conditional success is
  one of one eligible, but only one of four reference edges is eligible. The node
  layout is schematic and does not depict anatomy.'
visual: Reference graph with an amber saved mapped edge; retain one-of-four eligibility.
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

## Require complete typed event groups

```beat
id: events
scene: events
frames: 264
caption: Require complete typed event groups
narration: Persistent means one identity continues, not that its size is unchanged.
  Merging needs multiple baseline instances linked to one follow-up instance. New
  and disappearing events require their own cardinalities; check field of view before
  disappearance. Every ID belongs to one group. No complete reference event group
  was eligible here, so this run cannot isolate merging ability.
visual: List exact event cardinalities beside both complete reference groups.
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

## Keep the endpoint table disaggregated

```beat
id: results
scene: results
frames: 240
caption: Keep the endpoint table disaggregated
narration: Astra localized two of six instances, with foreground Dice about point
  six eight five and point seven seven nine. Only one of four links and zero of two
  complete events were correct. Sol submitted empty final masks and zero localized
  instances. Both completed normally and passed the artifact contract. The original
  scientific scores remain unchanged.
visual: Display detection, foreground, instance overlap, links and exact events with
  denominators.
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

## Submit an inspectable complete answer

```beat
id: output
scene: output
frames: 192
caption: Submit an inspectable complete answer
narration: Return two integer native instance masks, an events document and a report.
  Include method, uncertainty and representative evidence with filenames and zero-based
  slices; retain analysis scripts and views. Empty masks plus an empty event list
  can satisfy the file contract. Mechanical validity does not establish medical correctness.
visual: Show four output files, identifier limits and the empty-output counterexample.
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

## Keep the scientific review open

```beat
id: limits
scene: limits
frames: 216
caption: Keep the scientific review open
narration: One selected public pair and one attempt per model do not establish a general
  ranking. Source annotators had clinical reports; the solver had CT only. The instance
  convention remains under review, and this pair contains no new or disappearing reference
  event. Fresh saved-score replay confirms preserved calculations, not a clinical
  pass or new inference.
visual: Close on one-case, context, convention and event-coverage limits.
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
