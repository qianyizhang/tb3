# BR-009 — Sustained Xiangqi server optimization

**Terra/high passed. Retire v4 as a hard candidate; no Sol trial was triggered.**
It completed normally in **10 min 29 s**, with 30.2% lower CPU than the supplied
C1 baseline, stable memory, exact checked semantics, and 7 W / 5 D / 4 L in
16 complete budget games. The intended optimization behavior occurred, but no
Terra capability failure was demonstrated.

## Task and final results

The [task](../../probes/xiangqi-server-throughput/instruction.md) starts from C1,
the previous native author implementation. Search, evaluation and service runners
are fixed; only the game library and native helpers may change. Requirements:

- Preserve API/history/errors, move order and fixed-search decisions/progress.
- Use at most 80% of C1 CPU: median of three matched rounds, 16 held-out histories,
  4096 nodes/depth 4, four persistent pinned workers.
- Keep each worker alive for 196608 distinct legal board/side inputs, with no
  restart, a 256 MiB address-space/process-tree cap, and at most 8 MiB settled
  RSS growth after warm-up.
- Complete 16 equal-budget paired games through the four-worker service, with
  valid moves and replay. W/D/L is diagnostic, not a minimum-win gate.

All final rows use the identical [v4 freeze](../evidence/br009-xiangqi-v4-freeze.json):
`ea096a337849515fbdc728fb9274b671e4064996da9770a2b5638dc09cb3b188`.

| Entrant | CPU / C1 (limit 0.80) | Largest settled RSS growth | Games W/D/L | Reward |
| --- | ---: | ---: | --- | ---: |
| Author C4 oracle | 0.7075 | 0.115 MiB | 4 / 8 / 4 | 1 |
| No-op C1 | 0.9694 | 0.113 MiB | Not reached: CPU gate failed | 0 |
| Terra/high | **0.6983** | **0.145 MiB** | **7 / 5 / 4** | **1** |

Each row passed 253 semantic cases, including 12 fixed searches, additional
random diagnostic geometry and keyword/mixed-call coverage. All completed the
32 memory epochs. Terra's largest observed fixed-worker RSS was 36.8 MiB.
All final trials completed without infrastructure exceptions. Both the task
checksum and the submitted artifact hashes were rechecked after evaluation.

Terra and C4 attained similar CPU savings; their small difference does not
establish a performance ranking. Terra's game score was 59.4% including draws,
but 16 games do not establish tournament strength or a reliable Elo estimate.
C4's 50% game score also shows that faster execution does not guarantee stronger
play with this fixed evaluator. [Matched controls](../evidence/br009-v4-controls.json),
[final receipt](../evidence/br009-round-summary.json).

## What Terra did

The submitted changes stay within `game.py`, the native helper and build flags:

- Bounded move-parsing cache, 4096 entries.
- Native fast-call entry points with keyword/mixed-call support.
- Direct access to the declared one-byte board representation and cached owner
  strings, reducing repeated library-call overhead in the fixed evaluator.
- Native compiler tuning (`-march=native`, `-flto`).

It retained Game/history/outcome behavior, the move-generation algorithm/order,
and the baseline's correct temporary-list reference handling. Legal, replay and
parse caches remain bounded. Its implementation specializes helpers to the
declared ASCII piece/board domain; arbitrary-string behavior outside that domain
is not certified here.

The trace contains three profiling commands and several measured iterations.
One intermediate implementation repeatedly missed the CPU target at about 0.815;
Terra continued and passed its public checks before submitting. Thus the stronger
baseline did elicit performance diagnosis and revision, rather than a replacement
searcher. It still produced a healthy pass within the normal allowance.

[Trace audit](../evidence/br009-terra-trace-summary.json): Codex 0.154.0,
`gpt-5.6-terra` / high; 30 completed commands, 38 exec calls, no observed delegation
or network-fetch commands. Two user messages were present: ordinary environment
context and the exact task instruction. No additional author hints were sent.
Trace consistency does not prove provider-side identity or unaided discovery.
The artifact is 90077 logical bytes. Resource metadata: 13069 completion tokens,
109060 uncached prompt tokens, 1440000 cached prompt tokens; the harness reports
an estimated $0.663, not an invoice for this subscription-backed run.

## Author reference and memory controls

The author used the earlier Qi/BR-008 profile. C2 reduced Python/native wrapper
overhead; C3 added bounded parsing and cached immutable Game properties; C4
repaired keyword-call support. C4 passed public calibration at CPU ratio 0.7144
before model execution. This is an informed attainable reference, not a
mathematical upper bound or an unaided-model timing comparison.

The new memory gate rejects both the known native allocation leak from BR-008
and an explicit unbounded legal-move-cache control. C1, the repaired artifact,
and the author reference stay stable. A repeated finite corpus had hidden the
unbounded cache; introducing fresh states exposes both kinds of retention.
A finite test cannot prove absence of every possible leak.

See the [memory-control plot](../../runs/br009-author/memory-controls.svg),
[fresh-state controls](../evidence/br009-fresh-state-memory-controls.json), and
[initial author comparisons](../evidence/br009-author-controls.json).
These are controlled artifact observations, not additional model trials.
BR-008's original graded pass remains unchanged.

## Pre-model revisions retained

| Snapshot | Control result | Interpretation |
| --- | --- | --- |
| v1 | Oracle 0: cross-UID affinity denied | Verifier defect. Worker now sets its own assigned affinity. |
| v2 | Oracle 1; CPU ratio 0.7051; 5 W / 6 D / 5 L | Valid finite-workload pass. Repeated corpus masked an unbounded cache; superseded before model trials. |
| v3 | Oracle 1; CPU ratio 0.7130; 6 W / 6 D / 4 L | Fresh-state memory passed. A separate valid-keyword test exposed a C3 reference API omission. |
| v4 | Oracle 1, nop 0, Terra 1 | C4 preserves keyword/mixed calls; final matched controls and model pass. |

No nop or model trial launched on v1–v3; the pending drivers were stopped before
those launches. Their frozen rewards are unchanged. All archives and raw
controls remain local. [Affinity defect](../evidence/br009-v1-affinity-defect.json),
[keyword reference repair](../evidence/br009-keyword-reference-repair.json).
All 22 unchanged upstream static checks pass on the final package.

## Disposition

One fresh Terra/high model attempt; no model retry and no Sol attempt. The
predeclared trigger required a genuine normally completed Terra failure, which
did not occur. Retire this exact snapshot. The sustained-memory tests and
performance harness remain useful, but a new difficulty claim requires separate
source evidence and a newly declared experiment. Final submission qualification
remains separate from this local feasibility work.

[Owning plan](BR-009-xiangqi-server-throughput.md). Raw builds, profiles, games,
trajectories and archives remain under `runs/br009-author/` and the specifically
named Harbor job directories in the receipts. No Qi files or prior task freezes
were modified.
