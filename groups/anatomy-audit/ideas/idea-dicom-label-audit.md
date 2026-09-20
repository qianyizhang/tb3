+++
schema_version = 2
kind = "idea"
id = "idea-dicom-label-audit"
group_id = "anatomy-audit"
title = "DICOM anatomical annotation sanity checker"
next_action = "BR-003 remains retired after its healthy Terra/high pass. Preserve the separate BR-004 batch timeout and completed single-patient resource screen; dicom-audit-32 is the current observed lead."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "exploring"

[[sources]]
url = "codex://threads/01a0a0cf-3d4b-7f00-a47f-4133211cb483"
note = "BR-003 user-authorized work-history hunt; follow-up messages add anatomy QA and patient-coordinate SVG."

[[sources]]
url = "https://zenodo.org/records/10047263"
note = "CC BY 4.0 TotalSegmentator small subset v2.0.1, subject s1245; derived research CT and labels."

[[sources]]
url = "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html"
note = "Patient geometry convention; reference consulted at DICOM 2026c."

[historical_source]
path = "catalog/ideas/dicom-label-audit.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "f02fb1bdcc7f19c1f79f9cb1d6580b53e9091e90bd713aa307ccd4dae2dfb29e"
+++

# DICOM anatomical annotation sanity checker

## Question

A checker must infer coverage-dependent omissions and anatomical label misassignments without a supplied anatomy rule list.

## Prior findings

Native BINARY SEG parsing and anatomical context interact; five fixed packets share one source and four focus labels. Terra repaired an initial DICOM row/column error and passed all five packets.

## Reopen when

BR-003 remains retired after its healthy Terra/high pass. Preserve the separate BR-004 batch timeout and completed single-patient resource screen; dicom-audit-32 is the current observed lead.
