---
schema: 2
id: localized-ct
title: Judge the supplied candidate before drawing a mask
locale: en
purpose: Explain supplied-location CT judgment through exact native views, explicit
  rejection, conditional outputs, private reference and scorer/context limits.
scope: One outcome-selected focus at two visits; retained Astra/medium result; no
  clinical verdict, new trial or population estimate.
recipe: localized-ct-v1
asset_pack: retained-localized-ct-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/longitudinal-reading/presentation/briefs/tb3-localized-candidate-recognition.md
- groups/longitudinal-reading/findings/longitudinal-ct-v2-and-localized.md
- groups/longitudinal-reading/presentation/sources/localized-ct-audit.json
- groups/longitudinal-reading/experiments/longitudinal-ct-localized-astra-medium/protocol.md
- groups/longitudinal-reading/experiments/longitudinal-ct-localized-astra-medium/instruction.md
- scripts/audit_localized_ct_evidence.py
- scripts/build_localized_ct_assets.py
---

# Supplied candidate judgment

## Two full CTs, with locations supplied

```beat
id: inputs
scene: inputs
frames: 240
caption: Two full CTs, with locations supplied
narration: The agent receives the full baseline and follow-up CTs plus two exact native
  voxel locations. These red crosses are input assistance, not predictions. The views
  show the supplied center planes; both complete volumes remain available. No source
  masks or diagnosis are provided.
visual: Two full-field native axial planes, supplied red points and independent physical
  scales.
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

## Judge first; segment only accepted candidates

```beat
id: rules
scene: rules
frames: 288
caption: Judge first; segment only accepted candidates
narration: Each candidate needs an explicit tumor, normal-or-benign or indeterminate
  judgment with image evidence. Only candidates judged tumor receive masks. Every
  positive instance must enter an event group. Other findings are outside scope, and
  an empty inventory does not declare disappearance.
visual: Three decision branches, conditional mask rules and local-ID boundary.
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

## Inspect the saved close-up one native slice at a time

```beat
id: axial
scene: axial
frames: 288
caption: Inspect the saved close-up one native slice at a time
narration: The retained trace displays these four-slice close-ups for both visits.
  The red location is fixed in three dimensions. On neighboring sections, its cross
  is only an in-plane projection; the signed offset says how far that section lies
  from the supplied point.
visual: Four discrete saved crop planes per visit, native bounds, signed offsets and
  scale bars.
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

## Use the other planes to inspect continuity

```beat
id: orthogonal
scene: orthogonal
frames: 432
caption: Use the other planes to inspect continuity
narration: 'The agent also viewed six orthogonal sections per visit: three sagittal
  and three coronal, at the center and five voxels to each side. The displayed aspect
  follows actual voxel spacing. The 3 mm through-plane sampling limits fine detail;
  enlarged pixels do not add anatomical resolution.'
visual: Six successive native i/j sections per visit, preserving physical aspect and
  k reversal.
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

## Follow the saved serial detail views

```beat
id: serial
scene: serial
frames: 576
caption: Follow the saved serial detail views
narration: This reader replay steps through the twelve native slices used in the saved
  detail montages, every second section. It reconstructs the displayed evidence, not
  a new search or model execution. The image window and crop bounds stay fixed within
  each visit.
visual: Twelve exact step-10 native sections per visit, two seconds each, with a fixed
  projected point.
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

## Both decisions are explicit normal-or-benign judgments

```beat
id: judgments
scene: judgments
frames: 288
caption: Both decisions are explicit normal-or-benign judgments
narration: After viewing the indicated structures, the agent explicitly excludes both.
  It favors normal scalene-region soft tissue based on smooth shape and continuity,
  while noting uncertainty in tissue attribution. That explanation belongs to the
  saved model report. It is not our clinical diagnosis.
visual: Center crops remain visible beside the two saved categorical decisions.
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

## The negative judgments lead to zero masks and no events

```beat
id: outputs
scene: outputs
frames: 288
caption: The negative judgments lead to zero masks and no events
narration: Both submitted masks are all-background uint16 volumes with the exact input
  grids and affines. The event list is empty. The judgment file and report preserve
  reasons and image citations. These outputs consistently implement the agent’s rejection;
  they do not assess unrelated findings elsewhere.
visual: Five-file contract and the actual zero-mask/empty-event result.
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

## Reveal the private reference on the same candidate views

```beat
id: reference
scene: reference
frames: 384
caption: Reveal the private reference on the same candidate views
narration: Cyan now reveals the selected source annotation. Both supplied points lie
  inside label 3, one focus at two visits. The agent accepted zero of the two reference-positive
  candidates and produced no mask overlap. This is a reference disagreement after
  location assistance, not a clinical adjudication.
visual: Delayed source-outline reveal without changing the CT, native plane or supplied
  point.
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

## Valid files, reference agreement and linking use different tests

```beat
id: scoring
scene: scoring
frames: 384
caption: Valid files, reference agreement and linking use different tests
narration: 'The saved answer has zero of two localized instances and zero of one end-to-end
  link and event. No reference link or event group is eligible for conditional scoring.
  Specificity is undefined. An offline control exposes a separate gap: negative judgments
  paired with oracle masks still validate. The original consistent answer and scores
  are retained.'
visual: Original denominators and a separately labelled synthetic verifier control.
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

## The source annotators had clinical reports

```beat
id: context
scene: context
frames: 288
caption: The source annotators had clinical reports
narration: The release describes annotation from CT together with clinical examination
  reports. This solver received CT and coordinates only. The missing reports and unresolved
  clinical review are live alternatives to a pure model limitation. Exact source reconstruction
  and score replay cannot settle whether this focus is decidable from CT alone.
visual: Source versus solver information table and explicit unresolved adjudication.
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

## A recognition disagreement remains after localization

```beat
id: limits
scene: limits
frames: 288
caption: A recognition disagreement remains after localization
narration: This one fresh attempt rejects an explicitly displayed, outcome-selected
  focus. Whole-volume search alone does not explain the localized result. Positive-acceptance
  contouring and linking remain untested. Two visits are not two independent lesions,
  and this diagnostic supplies no population estimate or isolated causal effect.
visual: Observed behavior, supported attribution and untested stages; no new trial
  implied.
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
