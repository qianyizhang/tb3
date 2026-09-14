# Brainstorm and experiment rounds

This register keeps recurring discussions, candidate decisions and experiment
handoffs together. It owns round identity and navigation. The
[benchmark-backed shortlist](research-benchmark-backed.md) still owns selection
priority; the [catalog](catalog.md) owns searchable candidate decisions;
[ledger](ledger.md) and linked freezes/results own local observations;
[requirements](requirements.md) owns final submission gates.

## Round register

| Round | Captured | Question and candidates | State | Outcome / next action |
| --- | --- | --- | --- | --- |
| BR-001 | 2026-09-14 | [Compact scientific extractions](research-brainstorm-experiments-20260914.md): E01–E06, six original pilots | Complete | Six healthy Terra/high passes; all snapshots retired. [Receipt](evidence/brainstorm-round-summary.json). |
| BR-002 | 2026-09-14 | [Sol/Astra capability experiments](research-rounds/BR-002-sol-astra-capabilities.md): D01 moving frames, D02 RF conventions, D03 actuator memory, D04 score images | Captured; preparation pending | Four proposed designs, zero local attempts. D02 source audit and baseline preparation first; D04 is the visual branch. |

BR-001 is a retrospective navigation label for the existing completed report;
its E IDs, ledger B IDs, probe names and evidence paths retain their meanings.
BR-002 comes from later turns in the **same conversation**. A conversation URL
alone does not identify a round. Use scoped references such as **BR-002/D01**;
bare D01 also occurs in historical ledger entries.

Earlier sourcing rounds remain available: the
[100-card bank](research-broad-task-bank.md), its
[completed screen](research-screening-20260912.md), and the
[12-record second search](research-candidate-search-r2-20260912.md).
They are source inventories/screens, not additional model experiments.

## Adding and closing a round

1. Allocate the next unused BR number and copy the
   [round template](research-rounds/TEMPLATE.md). Record conversation and message
   IDs, capture date, retrieval gaps and what changed since the previous round.
   New turns with a different question/design cohort get a new round; corrections
   to a current design get a dated entry in that round.
2. Preserve the proposed contract, hypothesis, discriminating cases, independent
   verifier, permitted baseline, failure interpretation and stop rule. Record
   source claims separately from locally reproduced evidence. A compact oracle
   establishes solvability; model difficulty requires a valid trial.
3. Reuse an existing catalog ID for the same candidate. Create a new ID for a
   materially different deliverable/crux and link its predecessor. Add a
   round-specific tag such as `brainstorm-round-002`, retaining prior tags and
   review history. Keep candidate IDs aligned with future probe directory names.
4. Before execution, link the owning plan with its exact frozen conditions,
   model/harness settings, attempts, controls and stopping rule. Record whether
   execution is proposed or part of the active task. Capturing a discussion does
   not launch its suggested runs. An ablation is a separate frozen condition;
   comparisons within each condition use identical task bytes.
5. Close with per-candidate dispositions, local attempt denominators, exclusions,
   hypothesis support, lessons and the next selection action. Retain easy passes
   and superseded designs. Update this register and catalog; import completed
   raw trials explicitly through the existing tooling.

Round states are **captured**, **preparing**, **running**, **complete**, or
**parked**. They describe work, not evidence strength. Candidate records continue
to use the existing catalog statuses; no new catalog schema is introduced.

## Evidence and search

Keep three judgments separate: **execution validity**, **task success**, and
**support for the proposed hypothesis**. Published aggregate scores, published
task-level verifier misses, locally checked fixtures, and local model trials
must retain separate denominators. Syntax errors can fail a task without
supporting a conceptual hypothesis; crashes, timeouts and oracle faults do not
establish genuine model failure.

```bash
.venv/bin/python scripts/tb3_catalog.py list --kind ideas --query brainstorm-round-002
.venv/bin/python scripts/tb3_catalog.py report
```

The existing `brainstorm-20260914` tag identifies BR-001's six cards. Use the
numbered tag for BR-002 and future rounds; dates alone can collide. Reports are
local snapshots. Authored summaries belong in docs/catalog; raw conversation
exports, traces and generated reports remain local under ignored paths.
