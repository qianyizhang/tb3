---
schema: 2
id: history-sourcing
title: From work history to bounded task evidence
locale: en
purpose: Explain bounded retrieval, source claim classification, candidate contracts, frozen provenance
  and distinct recorded outcomes.
scope: Retained BR-003 source study; eight excerpts, five candidates, four historical model attempts and
  eight controls; no new execution.
recipe: history-sourcing-v1
asset_pack: retained-history-sourcing-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-history-sourcing.md
- groups/anatomy-audit/findings/history-sourcing-calibration.md
- groups/anatomy-audit/presentation/sources/history-sourcing-audit.json
- docs/research-rounds/BR-003-work-history.md
- docs/evidence/br003-source-audit.json
- docs/evidence/br003-round-summary.json
- archive/legacy/pre-medical/catalog/analyses/br003-work-history.md
- scripts/audit_history_sourcing.py
- scripts/build_history_sourcing_assets.py
---

# Canonical historical source investigation

## A bounded selection from retained history

```beat
id: retrieval
scene: retrieval
frames: 240
caption: A bounded selection from retained history
narration: The index contains 395 records. Remove 142 automatic reviews and sixteen other long titles,
  leaving 237 navigable records. Nine conversations were selected. Eight exact excerpts from six sessions
  are shown here; this is not exhaustive retrieval.
visual: Recounted source-record partition and selection counts.
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

## Read the record before making a claim

```beat
id: excerpts
scene: excerpts
frames: 624
caption: Read the record before making a claim
narration: Each short excerpt retains its original role, record line and SHA-256. The traversal covers
  all eight. Exact bytes authenticate a quotation, but do not independently validate a reported defect
  or an assistant diagnosis. None of these records is a BR-003 model trial.
visual: Eight exact source quotations, role labels and original record identifiers.
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

## Different source claims need different evidence

```beat
id: classification
scene: classification
frames: 288
caption: Different source claims need different evidence
narration: Recovered crop and resident-lifecycle reports differ from a new annotation-QA proposal and
  a recollection of SVG difficulty. The original SVG incident and exact timeout-reroute incident were
  not recovered. Keep those gaps visible.
visual: Three evidence classes with recovered and missing source boundaries.
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

## Translate a lead into an explicit contract

```beat
id: candidates
scene: candidates
frames: 600
caption: Translate a lead into an explicit contract
narration: Each candidate specifies what is given, what must be returned and how the private reference
  is built. Table curation, simulated chat recovery, annotation QA and supplied-mask SVG rendering are
  different contracts. Authentic vector-crop ownership remains an unauthored fifth lead.
visual: Five candidate cards with explicit input, output, reference and crux changes.
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

## Tie every recorded result to frozen task bytes

```beat
id: lineage
scene: lineage
frames: 384
caption: Tie every recorded result to frozen task bytes
narration: Four freezes contain 76 source files. Four retained archives and twelve raw result records
  match their receipts. Within each task, oracle, no-op and model share the task checksum. This verifies
  retained provenance, not a fresh run or container recovery.
visual: Selected task source-file count, archive-to-result lineage and exact checksum.
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

## Reveal four distinct retained outcomes

```beat
id: reference
scene: reference
frames: 384
caption: Reveal four distinct retained outcomes
narration: 'One Terra/high attempt passed each prototype: four PDF checks, 22 chat traces, five correlated
  QA packets and twelve SVG views with 72 perfect label comparisons. Eight control executions are separate.
  Different endpoints cannot be pooled; the two medical prototypes share one CT.'
visual: Delayed original outcome table with separate endpoint denominators and agent times.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## Ask which specific mistake the grader rejects

```beat
id: controls
scene: controls
frames: 384
caption: Ask which specific mistake the grader rejects
narration: Targeted author controls reject oversized crops, accepting results at the deadline, requiring
  anatomy outside scan coverage, and mirrored or crude box masks. They show discrimination on specified
  errors, not evidence that the model failed.
visual: Four actual negative-control examples and the limits of their implications.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## The original crop ownership question remains open

```beat
id: gap
scene: gap
frames: 288
caption: The original crop ownership question remains open
narration: The synthetic table-lineage prototype passed. It does not resolve the original vector-figure
  boundary problem. That fifth lead still lacks an authentic compact fixture and independent boundary
  truth. No executable task, attempt or score exists for it in this round.
visual: Solid H01 result branch and dashed untested H05 branch from the same crop reports.
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

## Preserve the pass and the unresolved source gap

```beat
id: limits
scene: limits
frames: 264
caption: Preserve the pass and the unresolved source gap
narration: This explanation preserves eight source quotations, four passing calibrations and the untested
  source gap. Selection limits, correlated data and single attempts prevent broad claims. The historical
  round remains closed; no new trial, saved-code replay or clinical validation is implied.
visual: Established observations, unresolved scope and closed historical disposition.
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
