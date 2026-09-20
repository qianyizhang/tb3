+++
schema_version = 2
kind = "idea"
id = "new-mri-lesions"
group_id = "longitudinal-reading"
title = "Find new lesions between brain MRIs"
next_action = "Assistant ranks this strongest for a new domain, conditional on official access, use terms and revised/adjudicated masks."
source = "codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d"
decision_provenance = "Assistant proposal; user requested explanation, not trial selection."
historical_ids = [
    "BR-043-C02",
]
idea_state = "exploring"

[[links]]
label = "Proposal and visual explanation links"
path = "docs/research-rounds/BR-043-medical-next-tasks.md"
+++

# Find new lesions between brain MRIs

## Question

Find new lesions between brain MRIs

## Prior findings

Paired FLAIR can isolate new lesions from existing lesions, registration error and intensity change. The BR-043 source screen notes revised MSSEG-2 references and expert disagreement; local agent difficulty is untested.

## Reopen when

Assistant ranks this strongest for a new domain, conditional on official access, use terms and revised/adjudicated masks.
