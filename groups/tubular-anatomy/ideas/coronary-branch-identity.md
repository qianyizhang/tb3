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

[[links]]
label = "Completed continuation trace and candidate audit"
path = "groups/tubular-anatomy/experiments/br042-v4-6h/resume1/trace-audit.md"

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

[[observations]]
date = "2026-09-21"
actor = "assistant"
source = "codex://threads/01a0c006-0f8c-78a1-8ab1-2f5868f21ee4"
finding = "Resumed V4 leaves all 15 prior coronary extraction specifications unchanged. Exact candidate-filter replay shows D2 retained as candidate 3 (87.8% reference coverage at 1 mm) but withheld as possible tissue; OM1 signal is discarded by component-size and 2.2-mm parent-gap gates. Lower vesselness alone still discards OM1 through an oversized component. This separates acceptance, filtering and downstream numbering failures; GT-imposed performance cap is not demonstrated. PDA identity remains under review. Resume token totals are cumulative, so incremental usage must be reported separately."
review = "groups/tubular-anatomy/experiments/br042-v4-6h/resume1/trace-audit.md"
next_action = "Assistant recommends candidate ledger, graph-path decomposition, targeted rejection review and separate reference adjudication before fresh controlled trials. No new trial authorized or launched."
[[links]]
label = "BR-042 final technical report and interactive showcase"
path = "groups/tubular-anatomy/presentation/br042/README.md"

[[observations]]
date = "2026-09-21"
actor = "assistant"
source = "codex://threads/01a0c006-0f8c-78a1-8ab1-2f5868f21ee4"
finding = "User requested a final showcase for technical ML/research readers. The retrospective consolidates six fresh BR-042 attempts and seven saved outputs with a common-scorer comparison, explicit partial-run states, native CTA overlay controls, candidate-filter diagnostics and static report. It separates coronary score from broad-vessel inventory and does not infer general model ranking, compute-scaling causality or a GT-imposed cap. Original artifacts and scores are preserved."
review = "groups/tubular-anatomy/presentation/br042/README.md"

+++

# Name coronary branches from supplied geometry

## Question

Name coronary branches from supplied geometry

## Prior findings

BR-042 separates recovered coronary geometry from correct branch labels; BR-041 endpoint extent alone did not establish fabricated anatomy. Supplying an unlabeled tree isolates branch identity, but it is explicit assistance.

## Reopen when

Assistant ranks this first for continuity; obtain fresh source-confirmed cases, remove label metadata and audit numbering conventions before a pilot.
