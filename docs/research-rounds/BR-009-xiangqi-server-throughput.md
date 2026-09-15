# BR-009 — Sustained Xiangqi server performance

## Intake

- Captured 2026-09-15; complete, retired after a Terra pass. Predecessor: [BR-008](BR-008-results.md),
  whose frozen Terra pass remains retired.
- Source: [current design conversation](codex://threads/01a0a25c-e24d-77e1-9864-2827d7867d30).
  The latest user explicitly authorizes an optimized strong baseline, adjusted
  task/evaluation, mandatory failure for memory leaks, and a conditional
  Sol/xhigh trial after a genuine Terra failure. Exact message IDs unavailable.
- Evidence: local, post-submission [BR-008 memory diagnostic](../evidence/br008-terra-memory-diagnostic.json).
  This is an audited source defect, not a retroactive BR-008 model failure.
- Question: can the agent improve an already native game library beneath fixed
  callers while preserving semantics and bounded memory in a sustained service?

## Candidate specification

- **Candidate:** `xiangqi-server-throughput` (new deliverable/performance contract).
- **Intervention:** only game.py and native helpers. Preserve the supplied search,
  evaluator, ordering, adapter and service. Four concurrent process workers, serial
  calls per engine. No language restrictions or replacement searcher.
- **Baseline:** BR-008 author C1, with piece-directed native move generation and
  correct ownership of temporary Python objects. Retain independent original
  Python referee for semantics. Both baseline source and helpers are supplied.
- **Hypothesis:** identifying the remaining hot path and preserving bounded
  ownership matters more than implementing standard search strategy. A pass
  retires this condition; a leak or semantic violation is a task failure even
  when short games succeed.
- **Author calibration:** starts 2026-09-15T05:10:23Z. Use public/author positions
  before inspecting private results; retain variants and timing. Select the
  reference and performance target before model execution. This author uses
  prior Qi/BR-008 knowledge, so timing is informed reference work, not a blind
  model comparison or a mathematical upper bound.
- **Evaluation under preparation:** original semantic/fixed-node equivalence,
  sustained single-PID memory gate without supervisor restarts, paired CPU/work
  measurement against C1, concurrent service/routing checks. Budget-game results
  will be measured, with the exact grading role fixed after author calibration.
- **Memory controls:** frozen leaky BR-008 Terra artifact must fail the new memory
  gate; C1 and its one-line refcount repair must pass. Use independently generated
  legal positions, churn exceeding bounded caches, warm-up, repeated epochs and
  a 256 MiB ceiling. Native/Python allocation growth must both be observable.

## Execution plan

Preparing; no model launched. Freeze exact requirements and threshold after
attainability checks. One oracle and one nop on the same freeze precede one
Terra/high attempt, Codex/Harbor subscription runner, 3600 s authoring allowance.
A normally completed verifier-backed failure, with successful controls and no
infrastructure fault, triggers one fresh Sol/xhigh attempt on identical bytes.
Do not send author implementation or debugging hints to either trial. Preserve
raw results, prompt/model provenance, hashes and artifact receipts locally.

## Outcomes

Not run. Any calibration defect is author/harness work, not model evidence.

## 2026-09-15 — Execution lock

The [instruction](../../probes/xiangqi-server-throughput/instruction.md) now fixes
all gates. Use at most 80% of C1 CPU (median of three matched rounds, each with
16 histories, 4096 nodes/depth 4, four persistent pinned workers); exact decisions
and iteration progress must match. Independently require 32 epochs of 6144 legal
positions per worker, no restarts, 256 MiB address-space/process-tree cap and at
most 8 MiB settled RSS growth. Original Python semantics also cover 128 additional
random diagnostic boards. Sixteen complete paired budget games report W/D/L;
there is no minimum win count. This isolates infrastructure performance while
retaining direct evidence about play. The finite memory gate detects the known
leak; it cannot prove absence of every possible leak.

C3 was selected using public calibration before private outcomes. It adds direct
native calls for repeated geometry/ownership, bounded move parsing, and per-Game
cached immutable derived properties. It attained CPU ratio 0.7152 in the new
four-worker workload, passed expanded semantics and bounded memory, and scored
5 W / 2 D / 1 L in eight public calibration games against C1. This is an attainable
reference, not an upper bound. Native source ownership fixes are not disclosed
in the candidate prompt. The known leaky Terra submission fails the sustained
check; C1 and its repaired copy pass. [Author receipts](../evidence/br009-author-controls.json).

Freeze: [v1 file manifest](../evidence/br009-xiangqi-v1-freeze.json), archive at
`runs/br009-author/task-v1.tar.gz`. Unchanged upstream Linux static checks: 22/22.
Oracle and nop: Harbor 0.18.0; model: Codex via Harbor 0.14.0,
`openai/gpt-5.6-terra`, high, subscription-authenticated local Docker. One attempt
per condition; 3600-second agent and 5400-second verifier, public network,
four CPUs/4 GiB. Run oracle then nop then Terra sequentially. Require oracle=1,
nop=0, matching checksums, completed verification and no infrastructure errors.
After a genuine normally completed Terra failure, run one independent
`openai/gpt-5.6-sol` / xhigh attempt on the same bytes, without hints. A clean
Terra pass retires this snapshot and skips Sol. At most one documented
infrastructure retry; never retry a clean outcome. These diagnostic trials do
not replace final submission requirements.

### V1 oracle defect and v2 repair

The v1 oracle completed with reward 0 because the verifier attempted to set
another user's CPU affinity without the required Docker capability. The driver
stopped before nop or any model run. Preserve v1 as a verifier defect, with its
archive and [receipt](../evidence/br009-v1-affinity-defect.json). V2 changes only
four copies of the fixed worker/client: the worker sets its own assigned affinity
before imports; the coordinator checks it read-only. A non-root four-worker
regression passes; all 22 static checks pass. Search, library implementations,
workloads and thresholds are unchanged. Restart the complete control/model
sequence on [v2](../evidence/br009-xiangqi-v2-freeze.json); this repair is not a
model retry or task-result revision.

### Pre-model memory coverage revision

A second explicit negative control changes only C3's legal-move cache from a
4096-entry LRU to `maxsize=None`. It passes v2's repeated finite corpus because
no new keys arrive after the first epoch. This is evidence of a coverage gap,
not a model outcome or a retroactive failure of that finite workload. The v2
trial driver was stopped before nop/model launch; let its running oracle finish
and retain the result.

The calibrated v3 workload introduces 6144 previously unseen legal board/side
states in every epoch, 196608 distinct inputs per worker. Four candidate workers
remain uninterrupted. The trusted C1 library generates the deterministic legal
stream; original Python equivalence remains an independent gate. CPU work,
limits, thresholds, player/search and C3 source do not change. On a separate
author seed, both the native allocation leak and unbounded cache now exhaust
memory, while C1, C3 and the refcount repair complete all epochs with stable RSS.
The v3 freeze and complete fresh oracle/nop controls must precede any model trial.

V2 oracle finished normally: reward 1, CPU ratio 0.7051, stable repeated-corpus
memory, 5 W / 6 D / 5 L in 16 complete games. Preserve this pass as a superseded
control. It illustrates why faster fixed search does not guarantee a winning
score against C1 on a small timed suite. No nop/model ran on v2.

V3 execution is now locked by the [freeze](../evidence/br009-xiangqi-v3-freeze.json)
and [fresh-state controls](../evidence/br009-fresh-state-memory-controls.json).
All 22 static checks pass. Run the unchanged sequential oracle/nop/Terra plan
on v3 only. The model has not seen any earlier trial or author implementation.

### C4 reference API repair and final v4 lock

A separate ordinary keyword-call regression test found that C3's direct native
aliases reject `owner(piece=...)`, `reaches(board=..., source=..., target=...)`,
and `moved(...)` keyword calls, although the original API accepts them. Stop the
v3 driver before nop/model; preserve its normally completed oracle reward 1,
CPU ratio 0.7130, stable fresh-state memory and 6 W / 6 D / 4 L in 16 games.
Its finite verifier did not cover these calls. This is an author-reference/API
coverage issue, not a model result, and its recorded reward remains unchanged.

C4 retains the positional fast paths and correctly binds keyword and mixed
calls. Add explicit keyword checks to the public/private contract runner and
clarify that existing parameter names are part of the API. The expanded public
contract passes 222 cases/12 fixed searches. CPU ratio remains 0.7144; fresh-state
memory passes. [Repair receipt](../evidence/br009-keyword-reference-repair.json).
No threshold, budget, position stream, searcher or baseline changes.

The final [v4 freeze](../evidence/br009-xiangqi-v4-freeze.json) contains C4 as its
reference. All 22 static checks pass. Run a fresh oracle/nop pair and then the
single Terra/high trial; Sol/xhigh remains conditional on a genuine Terra failure.
No model outcome informed any of these pretrial corrections. Do not strengthen
this condition after a model pass.

## Final outcome — complete, retired

The final v4 controls passed: oracle 1 at CPU ratio 0.7075; nop 0 at 0.9694.
Terra/high then completed normally in 628.844 seconds and passed: CPU ratio
0.6983, 253 semantic cases, all 32 fresh-state memory epochs, at most 0.145 MiB
settled RSS growth, and 7 W / 5 D / 4 L in 16 valid service games. The fixed task
bytes and submitted artifact hashes were verified after evaluation. One model
attempt, zero model retries, zero Sol runs. The genuine-failure trigger was not
met. Retire v4 as a hard candidate; do not reinterpret the pretrial corrections
or out-of-domain behavior as a model failure.

[Results and interpretation](BR-009-results.md),
[matched controls](../evidence/br009-v4-controls.json),
[trace audit](../evidence/br009-terra-trace-summary.json),
[final receipt](../evidence/br009-round-summary.json).
