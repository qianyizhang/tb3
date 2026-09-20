+++
schema_version = 2
kind = "idea"
id = "coronary-branch-identity"
group_id = "tubular-anatomy"
title = "Name coronary branches from supplied geometry"
next_action = "Assistant ranks this first for continuity; obtain fresh source-confirmed cases, remove label metadata and audit numbering conventions before a pilot."
source = "codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d"
decision_provenance = "Assistant proposal; user requested explanation, not trial selection."
historical_ids = [
    "BR-043-C01",
]
idea_state = "exploring"

[[links]]
label = "Proposal and visual explanation links"
path = "docs/research-rounds/BR-043-medical-next-tasks.md"

[[observations]]
actor = "assistant"
source = "codex://threads/01a0bc95-2598-7810-809e-9c8b6c0969c3"
date = "2026-09-20"
finding = "Two-hour V4 xhigh timed out with 94.1% geometric and 74.8% correctly labeled length coverage. D1 identity improved; D2 candidate was explicitly noticed but unresolved, GT OM1 missed, GT OM2 partially traced as OM1, and PDA taxonomy disputes persist. Longer runtime and broader output did not establish clinical completeness or exceed completed V3 medium coverage."
review = "groups/tubular-anatomy/experiments/br042/reviews/v4-2h.md"

[[observations]]
date = "2026-09-20"
actor = "user"
source = "codex://threads/01a0bc95-2598-7810-809e-9c8b6c0969c3"
text = "Authorized a fresh Astra/xhigh six-hour attempt after reviewing two-hour timeout output, with babysitting every 20–30 minutes. New br042-v4-6h preserves clinical scope and evaluation and changes only timing/identifier; no case-specific feedback to solver."
+++

# Name coronary branches from supplied geometry

## Question

Name coronary branches from supplied geometry

## Prior findings

BR-042 separates recovered coronary geometry from correct branch labels; BR-041 endpoint extent alone did not establish fabricated anatomy. Supplying an unlabeled tree isolates branch identity, but it is explicit assistance.

## Reopen when

Assistant ranks this first for continuity; obtain fresh source-confirmed cases, remove label metadata and audit numbering conventions before a pilot.
