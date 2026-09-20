+++
schema_version = 2
kind = "idea"
id = "idea-dicom-triplanar-svg"
group_id = "anatomy-audit"
title = "DICOM patient-coordinate triplanar SVG"
next_action = "Parked after completed calibration; no follow-up trial is scheduled. Retain original evidence and reopen only under the conditions below."
decision_provenance = "User accepted the parking recommendation on 2026-09-21 in codex://threads/01a0c040-3777-7b72-b932-6e6b118304a2; decision decision-fd16fb33e2fc44ca. Historical outcomes remain unchanged."
idea_state = "parked"

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
path = "catalog/ideas/dicom-triplanar-svg.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "6190e894a062da794b360f2a1e6bf4c7ed5e6c22ee41e9f0c92cd9427811a09d"
+++

# DICOM patient-coordinate triplanar SVG

## Question

A viewer may mistake acquisition-array slices for patient-coordinate planes or misassociate sparse SEG frames.

## Prior findings

Requires a correct physical affine and source-reference mapping. Terra achieved Dice 1.0 on all 72 label/view comparisons.

## Reopen when

Reopen if a newly curated oblique acquisition or sparse SEG source-reference variant exposes a reproduced geometry or frame-association defect. Audit its physical-coordinate oracle and input-legal control before proposing a separately authorized trial.

## Current disposition

The completed patient-coordinate triplanar SVG calibration passed with Terra/high, including Dice 1.0 on all 72 retained label/view comparisons; no follow-up trial is scheduled. Preserve the frozen task and observed outcome. The user accepted parking on 2026-09-21 in [the refinement task](codex://threads/01a0c040-3777-7b72-b932-6e6b118304a2). This does not close the broader scientific question.
