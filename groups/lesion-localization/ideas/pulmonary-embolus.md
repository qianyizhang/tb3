+++
schema_version = 2
kind = "idea"
id = "pulmonary-embolus"
group_id = "lesion-localization"
title = "Localize emboli in CTPA"
next_action = "Assistant keeps this as a source-curation reserve. Define 3D lesion instances and inspect negative controls before promoting a task."
source = "codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d"
decision_provenance = "Assistant proposal; user requested explanation, not trial selection."
historical_ids = [
    "BR-043-C06",
]
idea_state = "exploring"

[[links]]
label = "Proposal and visual explanation links"
path = "docs/research-rounds/BR-043-medical-next-tasks.md"
+++

# Localize emboli in CTPA

## Question

Localize emboli in CTPA

## Prior findings

The BR-043 screen describes a small FUMPE reference pool whose negatives have thicker slices than most positives. Lesion continuity, geometry and matched negatives need curation; no local agent failure was established.

## Reopen when

Define 3D lesion instances and inspect negative controls before promoting a task.
