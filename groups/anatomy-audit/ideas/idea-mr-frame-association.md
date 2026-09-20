+++
schema_version = 2
kind = "idea"
id = "idea-mr-frame-association"
group_id = "anatomy-audit"
title = "Canonical multiframe acquisition reconstruction"
next_action = "Parked after completed calibration; no follow-up trial is scheduled. Retain original evidence and reopen only under the conditions below."
decision_provenance = "User accepted the parking recommendation on 2026-09-21 in codex://threads/01a0c040-3777-7b72-b932-6e6b118304a2; decision decision-19be29c5ff684715. Historical outcomes remain unchanged."
idea_state = "parked"

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

Reopen if a concrete equivalent DICOM encoding exposes a reproduced association defect, or a new source-backed acquisition variant needs independent calibration. First define the invariant and a passing input-legal control; any new model trial needs separate authorization.

## Current disposition

The completed MR frame-association calibration passed cleanly with Terra/high; no follow-up trial is scheduled. Preserve the frozen task and observed outcome. The user accepted parking on 2026-09-21 in [the refinement task](codex://threads/01a0c040-3777-7b72-b932-6e6b118304a2). This does not close the broader scientific question.
