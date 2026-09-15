# BR-006 — Xiangqi budget-player results

## Decision

**Retire v2 from hard-task selection.** The task is viable, but one fresh
Terra/high trial passed. The requested Terra-failure target was not reached.
Sol was not run because the frozen plan permits it only after a genuine Terra
failure. No threshold, corpus or task bytes were changed after the model answer.

| Entrant | W | D | L | Actual wins | Reward |
| --- | ---: | ---: | ---: | ---: | ---: |
| Author reference | 56 | 5 | 3 | 87.5% | 1 |
| Unchanged starter (nop) | 25 | 13 | 26 | 39.1% | 0 |
| Terra/high submission | 56 | 7 | 1 | 87.5% | 1 |

Each row is 64 complete games against the frozen baseline, using 32 opening
families with colors swapped. Rows are separate matches; this is not a direct
Terra-versus-reference ranking. Terra's draw-adjusted score is 92.96875%.

## Task and hypothesis

[Task specification](../../probes/xiangqi-budget-player/instruction.md): build
an offline player with at least 39 actual wins in 64 games, while preserving the
supplied game API. All player code, including movement and state handling, is
editable. Each player receives one CPU, 750 ms CPU per decision, 256 MiB and a
16 MiB deployed-file limit. The authoring allowance is one hour on four CPU /
4 GiB. A separate referee owns legality, adjudication and results.

The underlying performance hypothesis was useful. One Qi profile attributed
89.3% of cumulative decision time to legal generation; the cold author sample
measured about a 12.5x generator speedup. The author reference changed only
`qi/game.py`, retained the search recipe, and won 56/64 while the two sides used
1553.85 and 1555.88 decision CPU seconds. These are scoped measurements, not an
exact general cost share or a claim of exhaustive rule equivalence.

The difficulty hypothesis did not hold for this trial. Terra inspected the
supplied source, then wrote a small C++17 engine with piece-directed movement,
mutable make/unmake, iterative search, transpositions, ordering and quiescence.
It left the Python `qi.game` API byte-identical. Its trace contains no explicit
profiler invocation or external engine download command. This supports a
successful implementation route, not a claim that Terra measured the original
hotspot. It recovered from an ARM compiler-flag error during development and
finished normally.

## Budget and execution evidence

- Terra authoring: **797.199 seconds (13.3 minutes)** of 3,600 allowed.
- Private verification: **640.764 seconds (10.7 minutes)**; total trial 24.8 minutes.
- Submitted logical file size: **137,004 bytes**; its reported 232 KiB disk usage
  includes filesystem allocation. Source and compiled binary were retained.
- Terra decisions: mean 678.3 ms CPU, maximum sampled 710 ms; no forced stops or
  fallback-only decisions; peak observed process-tree RSS about 26.9 MiB.
- Reported completed search depth: 5.23 for Terra and 1.58 for its opponent.
  This is diagnostic, not an independently standardized strength metric.
- Runner token report: 14,247 completion tokens, 1,634,041 aggregate input tokens,
  including 1,562,624 cached tokens. Aggregate input repeats context across steps;
  this is not 1.6 million fresh input tokens or a statement of subscription billing.

The baseline had 157 normal budget-forced stops across 24 games in Terra's match.
Terra won 37 W / 3 D / 0 L in the 40 games without such baseline stops, and
19 W / 4 D / 1 L in the other 24. This post-hoc split is descriptive; it does not
replace the full grade or establish a causal effect of stopping. Three baseline
turns had sampled CPU values above 760 ms, with a maximum of 770 ms: stopping
has detection latency. The supervisor accepts only move updates observed by
760 ms. Do not interpret this arena as hard real-time CPU enforcement.

## Validity and limits

The matching [oracle/nop controls](../evidence/br006-xiangqi-v2-controls.json)
returned 1/0 with no infrastructure exceptions. All 22 unchanged upstream Linux
static checks passed. The actual model context confirms Terra/high; its supplied
instruction matched the frozen prompt exactly. The extra user-context item was
standard plugin/environment metadata. Fresh image and transferred-artifact
inventories excluded the author solution and private grading inputs.

The private grader passed explicit movement/adjudication fixtures, 98 API
histories, and all 64 replayed games. All 84 frozen file hashes and the Harbor
checksum were rechecked after completion:
`27db494fad49aafb2c389e781f1ec06b36450d469d064bbff9b4a821eedbc532`.
The cancelled v1 oracle and its 13 partial games remain separate infrastructure
evidence; no model ran on v1.

This is one diagnostic run against a fixed suite, not a model pass-rate estimate,
tournament Elo, or final TB3 qualification. Openings are a new withheld partition
of exposed Qi development inputs, not certified training-disjoint data. Human
README explanations and author metadata remain explicit feasibility placeholders.

## Inspectable artifacts

- [Round receipt](../evidence/br006-round-summary.json),
  [trace and artifact audit](../evidence/br006-terra-trace-summary.json),
  [v2 freeze](../evidence/br006-xiangqi-v2-freeze.json).
- [Execution history](BR-006-execution.md) and
  [initial design](BR-006-xiangqi-budget-player.md).
- [Terra source](../../runs/br006-xiangqi-terra-high-v2-20260915/xiangqi-budget-player__Mo6uyb3/artifacts/app/submission/xiangqi.cpp),
  [raw result](../../runs/br006-xiangqi-terra-high-v2-20260915/xiangqi-budget-player__Mo6uyb3/result.json),
  [verifier output](../../runs/br006-xiangqi-terra-high-v2-20260915/xiangqi-budget-player__Mo6uyb3/verifier/test-stdout.txt).

Raw logs, games, binary and snapshots stay local under `runs/`; they are not
published or substituted with generated catalog data.
