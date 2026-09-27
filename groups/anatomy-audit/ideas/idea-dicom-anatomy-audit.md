+++
schema_version = 2
kind = "idea"
id = "idea-dicom-anatomy-audit"
group_id = "anatomy-audit"
title = "CT annotation audit with localized anatomical defects"
next_action = "Preserve the batch timeout as inconclusive. The completed single-patient screen identifies dicom-audit-32 as the lead and dicom-audit-83 as a second reviewed miss; source holds remain for cases 46 and 61. See the separate resource benchmark before any newly frozen design."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "parked"

[[sources]]
url = "codex://threads/01a0a248-241a-76b0-8ecf-15e259df9734"
note = "BR-004 user explicitly requests harder subtle test set and Terra/max attempt."

[[sources]]
url = "https://zenodo.org/records/10047263"
note = "CC BY 4.0 TotalSegmentator small v2.0.1; eight independently sourced patients."

[historical_source]
path = "catalog/ideas/dicom-anatomy-audit.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "5359c131f27c117eab0b566a72f2515fcd9522a5c9cbe701d6e9ff8e1d2e53ce"
+++

# CT annotation audit with localized anatomical defects

## Question

A solver must detect localized mask defects while accepting plausible annotations on real scans with coverage and pathology variation; global label presence, side and tissue summaries are insufficient.

## Prior findings

Localized changes preserve plausible whole-mask shape and tissue class, but the fresh Terra/max run timed out after 1800 seconds with its empty starter unchanged. Genuine short-horizon difficulty is not established.

## Reopen when

Preserve the batch timeout as inconclusive. The completed single-patient screen identifies dicom-audit-32 as the lead and dicom-audit-83 as a second reviewed miss; source holds remain for cases 46 and 61. See the separate resource benchmark before any newly frozen design.

## Author explanation checkpoint — 2026-09-27

Assistant review for the [sequential explainer completion task](codex://threads/01a0e024-3705-7a91-9181-d237131801fa):
[BR-010](../../../docs/research-rounds/BR-010-mask-only-anatomy.md) qualifies the
older case-32 lead and documents relational reasoning already present in the
traces. [BR-011](../../../docs/research-rounds/BR-011-unlabeled-anatomy.md) finds
23/24 anatomical groups solved by coordinate ordering and 109/131 organ identities
recovered by a baseline with labeled examples from seven other patients. No new
model trial or historical score change follows from this presentation work.

The [canonical study explanation](../presentation/briefs/tb3-mask-reasoning-study.md)
uses actual selected source geometry and reader-only reference comparisons.
All eight source arrays and seven trajectory hashes were checked; every retained
ordering row and organ prediction was independently recomputed without importing
historical authoring code. This confirms the retained computation, not clinical
truth or mask-only identifiability. Reopen difficulty claims only after blind
identity/ambiguity review, a unique supported answer and appropriate clean controls.
This is an assistant explanation and recommendation, not a new user decision.

## Source curation explanation checkpoint — 2026-09-27

Assistant review for the same sequential completion task: the retained
[BR-012 curation](../../../docs/research-rounds/BR-012-anatomy-curation.md)
separates five candidate decisions from task admission. Six patients and seven
volumes supply 145 annotated instances, including three overlapping identities.
Both author ordering screens reproduce; all 21 source member hashes and 104,100
teaching boundary points were checked against the original masks. The
[canonical curation explanation](../presentation/briefs/tb3-anatomy-curation.md)
shows the 547/585 count ambiguity, 406 preservation and unresolved C1 centroid
exception, 823 calibration, 642 reserve and 581 exact-key rejection. Reference
labels remain an explicit reader reveal, separate from hypothetical solver inputs.

Zero hard tasks were admitted and no new model trial follows. Reopening requires
qualified context, independent input-only identifiability review, defensible
acceptable-answer rules and verified controls. This is an assistant explanation
and recommendation, not a new user decision or clinical adjudication.
