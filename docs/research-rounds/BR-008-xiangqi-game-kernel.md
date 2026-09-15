# BR-008 — Optimize the Xiangqi game library under a frozen searcher

## Intake and authorization

2026-09-15; preparing. Successor to the retired BR-006 v2. Conversation
`codex://threads/01a0a25c-e24d-77e1-9864-2827d7867d30`; exact message IDs are not
available. The user approved the intervention-boundary proposal and authorized
an author optimization before/concurrent with/after Terra to understand difficulty
and an approximate attainable performance ceiling. This is an explicit user-led
successor study, not a benchmark-backed failure claim. BR-006's pass stays intact.

Prior result: BR-006 Terra/high passed 56/64 wins using a native searcher; the
library-only author reference also won 56/64. The new contribution is to hold the
search and caller semantics fixed while comparing library implementations.
Qi experiment skill v1.0.0 informs the comparison/evidence method; TB3 owns all
new artifacts. Qi and the BR-006 task are read-only.

## Contract and hypothesis

Optimize the supplied `qi.game` implementation, preserving its API, legal-move
ordering, immutable state/history, adjudication and errors. Native helpers are
allowed. The grader assembles the library with protected copies of the supplied
searcher, evaluator, ordering, extensions, transposition policy and protocol
adapter. Search replacement or changes to caller behavior are outside the task.

Pass requires semantic equivalence, matching fixed-node search decisions and
progress, and at least 39 actual wins in 64 games against the original library
under identical frozen search and equal CPU. Keep BR-006's 750 ms/decision,
one CPU/player, 256 MiB, 16 MiB submission, 3,600-second agent and 5,400-second
verifier limits. Keep its exact public/author/grading family partition to isolate
the intervention change; this is not new or certified training-disjoint data.

The proposed crux is reducing game-state/movement cost without changing caller
semantics. Cases distinguish board-only legality caches from history-dependent
outcomes/hashes, deterministic move ordering, and immutable state transitions.
A native rewrite below the boundary remains legitimate and may make this task
easy. No explicit profiler invocation is required for reward.

## Persistent server decision (locked before controls/trials)

The user selected **fixed server/search; optimize the shared library** in the
2026-09-15 clarification. Supply a persistent JSON-lines service with request
and game IDs, out-of-order response routing, four process workers and four
concurrent game clients. Each worker owns one candidate and one baseline engine
process; both remain alive across unrelated games and requests. Only its active
engine runs. Four worker CPUs are assigned explicitly; the original 750 ms CPU,
256 MiB per engine and suspended-idle accounting remain. Queue/transport wall
latency is reported separately and earns no additional search CPU. The total
service uses at most eight engine processes plus fixed coordinator/referee code
inside the four-CPU, 4 GiB environment.

This tests process-local shared caches and cross-game history isolation. It does
not claim simultaneous calls from Python threads into one library instance.
Transport, scheduling, CPU accounting and the search remain trusted inputs;
`game.py` plus `helpers/` are overlaid into the trusted package at grading.
The grader does not execute the submitted build script; compiled runtime assets
must already be present. Public checks cover concurrent routing, legal outputs,
worker reuse and shutdown. No extra throughput threshold is added: equal-CPU
strength is the deployment objective, with throughput/latency as diagnostics.

## Author comparisons and stop rule

Predeclare four implementations: B0 original Python; P1 the already snapshotted
Qi Python geometry optimization; C0 a straightforward native port of the original
geometry loops; C1 native piece-directed candidates and direct attack detection.
C0/C1 may share their compatibility wrapper and build plumbing. Keep original
Game/history logic unless profiling supports a bounded transparent optimization.
Author implementation allowance: at most 60 minutes of active implementation,
excluding harness construction, compilation waits and game evaluation. Record
actual timing and revisions; this is informed author work, not an unaided model
trial. No mathematical upper bound is claimed.

Validate all against independent semantics and fixed-node searches. Compare
cold/warm generator and complete fixed-work search CPU, cache behavior, memory,
and profiles on public/author-validation inputs. Choose the fastest semantically
valid author implementation by median cold complete-search CPU; selection occurs
before private match outcomes. Run C0 on eight author-validation color pairs as
the cheap-port screen. Preserve an easy control pass as evidence against difficulty.
Run one fresh Terra diagnostic even if C0 is strong, because the user explicitly
requested the author-versus-Terra comparison; do not strengthen the task in
response to a successful control.

Freeze the full successor before official controls/model work. Harbor 0.18
oracle/nop must finish with rewards 1/0 and no infrastructure exceptions on the
same checksum. Then one Harbor 0.14 Codex Terra/high run, 3,600 seconds, existing
subscription/proxy settings. Sol/xhigh remains conditional on a genuine normally
completed Terra artifact failure, at most one diagnostic attempt. Permit at most
one retry for a documented infrastructure event, never for a clean outcome.

The author reference and Terra each receive the same final 64-game evaluation.
After the model artifact is frozen, measure it with the same author-validation
cold/warm fixed-search script used for B0/P1/C0/C1. This diagnostic compares
attained implementation performance; it cannot alter the pass gate or selection.
Do not use private outcomes to revise the corpus, threshold, reference or model
prompt. A clean Terra pass retires the successor. API/search mismatches in a
normally submitted artifact can be genuine correctness failures; agent timeouts,
harness faults, missing results and invalid controls cannot.

## Ownership and retention

Own `probes/xiangqi-game-kernel/`, BR-008 notes/receipts and its new candidate card.
Preserve other tasks and dirty files. Raw builds, profiles, games, model traces and
snapshots live under ignored `runs/br008-author/` and Harbor job directories.
No commits or publication are implied. Final qualification remains separate.

## Outcomes

Complete; retire v2 as a hard candidate. Oracle 62 W / 1 D / 1 L and no-op
24 W / 14 D / 26 L validated the same frozen v2. Terra/high completed normally
in 327.2 seconds and passed: 61 W / 2 D / 1 L, all 64 valid, reward 1. No Sol run:
the predeclared failure trigger was not met. The frozen task and submitted
artifact remained unchanged throughout evaluation.

V1 had one independently reproduced fixed-adapter JSON-line defect and is retained
as invalid control evidence. Only atomic line output changed in v2. A subsequent
native reference-count diagnostic found a real leak in Terra's artifact; a
one-line copied-artifact control repaired it. That extra workload does not alter
the official pass. It identifies a sustained-memory coverage gap for a possible
separate experiment.

See [results and interpretation](BR-008-results.md),
[v2 freeze](../evidence/br008-xiangqi-v2-freeze.json),
[control receipts](../evidence/br008-v2-controls.json),
[trace audit](../evidence/br008-terra-trace-summary.json),
[memory diagnostic](../evidence/br008-terra-memory-diagnostic.json) and
[final summary](../evidence/br008-round-summary.json).
