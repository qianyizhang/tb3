+++
schema_version = 2
kind = "idea"
id = "idea-dicom-audit-28"
group_id = "anatomy-audit"
title = "Anatomical annotation audit: case-28"
next_action = "Retire this frozen condition from difficulty selection; retain as an expensive positive control."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "exploring"

[[sources]]
url = "codex://threads/01a0a248-241a-76b0-8ecf-15e259df9734"
note = "User requests one trial per task and resource benchmarking."

[historical_source]
path = "catalog/ideas/dicom-audit-28.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "f05bd1376344d742a3a1d3046fdc24e78a1fcae4e80fd835be98ed9ccbf92172"
+++

# Anatomical annotation audit: case-28

## Question

A single patient can expose a localized anatomical annotation reasoning gap without the cost of reviewing the full eight-patient batch.

## Prior findings

One healthy Terra/max pass found both exchanged rib identities and located both discrepancy regions, using 16.93 agent minutes and 37678 output tokens.

## Reopen when

Retire this frozen condition from difficulty selection; retain as an expensive positive control.
