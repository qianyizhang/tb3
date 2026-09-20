+++
schema_version = 2
kind = "idea"
id = "idea-dicom-audit-19"
group_id = "anatomy-audit"
title = "Anatomical annotation audit: case-19"
next_action = "Retire this condition from difficulty selection; preserve its resource observation and negative-control role."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "exploring"

[[sources]]
url = "codex://threads/01a0a248-241a-76b0-8ecf-15e259df9734"
note = "User requests one trial per task and resource benchmarking."

[historical_source]
path = "catalog/ideas/dicom-audit-19.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "01dccf97f5e327d74f66082c6befba7a38f66d339084ad5fc5a7522de115feee"
+++

# Anatomical annotation audit: case-19

## Question

A single patient can expose a localized anatomical annotation reasoning gap without the cost of reviewing the full eight-patient batch.

## Prior findings

One healthy Terra/max pass required 14.48 agent minutes and 31291 output tokens; no difficulty failure is demonstrated.

## Reopen when

Retire this condition from difficulty selection; preserve its resource observation and negative-control role.
