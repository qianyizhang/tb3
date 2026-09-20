+++
schema_version = 2
kind = "idea"
id = "idea-mr-frame-association"
group_id = "anatomy-audit"
title = "Canonical multiframe acquisition reconstruction"
next_action = "Retired after a clean Terra/high pass. Preserve the frozen calibration task; return selection to the benchmark-backed shortlist."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "exploring"

[[sources]]
url = "https://swescience.github.io/task-matrix/gradient/"
note = "Source lead only; audited Sol misses differ from the pilot's chosen crux."

[[sources]]
url = "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.17.html"
note = "Dimension descriptors and logical ordinals."

[historical_source]
path = "catalog/ideas/mr-frame-association.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "dbcb58589e5c6a6935cfaa5f04eb629bf1474875443cc4a8f41de6dc378957f5"
+++

# Canonical multiframe acquisition reconstruction

## Question

A repair may retain storage-order assumptions and lose sample-to-metadata association under equivalent encodings.

## Prior findings

Physical and acquisition coordinates need independent canonical ordering; source benchmark misses do not establish this original pilot's difficulty.

## Reopen when

Retired after a clean Terra/high pass. Preserve the frozen calibration task; return selection to the benchmark-backed shortlist.
