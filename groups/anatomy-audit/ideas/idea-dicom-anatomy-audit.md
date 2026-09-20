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
