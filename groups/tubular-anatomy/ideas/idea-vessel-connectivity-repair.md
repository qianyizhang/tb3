+++
schema_version = 2
kind = "idea"
id = "idea-vessel-connectivity-repair"
group_id = "tubular-anatomy"
title = "Repair one communicating-artery connection from MRA evidence"
next_action = "Bounded feasibility experiment complete; no trial queued. Retain V01 as calibration and hold V02 as a reference disagreement. Any future promotion requires independent review of the added L-ACA-adjacent structure and a separately admitted natural segmentation-model error with reproducible prediction provenance."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "parked"

[[sources]]
url = "https://arxiv.org/abs/2312.17670"
note = "User-pasted brainstorm citation. Earlier brainstorm session and message IDs were not supplied or retrieved. Historical topology failures motivate screening, not an agent failure claim."

[[sources]]
url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC13496301/"
note = "Updated TopCoW paper; binary/multiclass distinction, annotation protocol, and hypoplastic-vessel handling."

[[sources]]
url = "https://zenodo.org/records/15692630"
note = "Public paired CTA/MRA image and mask reference source. Four MRA source candidates downloaded and technically checked."

[[sources]]
url = "https://zenodo.org/records/17358162"
note = "Matching curated centerline graph and node source. Derived from TopCoW masks, not independent anatomical truth."

[[sources]]
url = "https://zenodo.org/records/15665435"
note = "Potential author-side prediction route through released segmentation containers; not executed."

[historical_source]
path = "catalog/ideas/vessel-connectivity-repair.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "7b514d4ed1ce0970b3aa5c58d2cceccfb6208d024a13730f6668aab896bfdc2c"
+++

# Repair one communicating-artery connection from MRA evidence

## Question

Given one small MRA region and a proposed vessel mask, an agent can use image evidence to repair a broken or false connection while preserving an annotated asymmetric or incomplete Circle of Willis configuration.

## Prior findings

Not established. The synthetic gap passes with Terra/high and an ordinary image-guided baseline. The unchanged-case Terra output fails preservation, but follows visible signal omitted from the reference near L-ACA; clinical/anatomical adjudication is unresolved. Published TopCoW errors do not transfer automatically to this binary-mask task.

## Reopen when

Bounded feasibility experiment complete; no trial queued. Retain V01 as calibration and hold V02 as a reference disagreement. Any future promotion requires independent review of the added L-ACA-adjacent structure and a separately admitted natural segmentation-model error with reproducible prediction provenance.

## Source explanation audit — 2026-09-27

Assistant observation, not a user decision or task promotion: the
[BR-025 explainer](../presentation/stories/vessel-source-screen.story.md) preserves
source curation separately from later BR-026 feasibility. The
[read-only audit](../presentation/sources/vessel-source-audit.json) verifies all
30 selected files by size, SHA-256 and retained ZIP CRC, twelve screened MRA edge
files, four image/mask grids, four present Pcom label components and expected
parent contacts. All 146 graph-node entries reproduce the stored alignment screen;
the largest nearest-foreground-centre distance is 0.33460045 mm. Shared-boundary
entries are repeated, and full VTP edge geometry is not independently validated.

[Source projections and native slices](../../../presentation/task-explorer/vessel-source/NOTICE.md)
are author teaching views with separately revealed annotations. Case 007's slice
extent is annotation-selected; it is not a solver crop. The graph source derives
from the same masks. Paired CTA labels agree, but CTA images were not reviewed.
No natural faulty prediction, admitted defect fixture, numeric verifier threshold
or model trial is added. Original receipts and outcomes are unchanged. The
reopening conditions above remain in force; commercial redistribution remains
subject to source-owner permission.
