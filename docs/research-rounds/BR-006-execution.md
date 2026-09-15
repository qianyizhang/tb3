# BR-006 — Authorized implementation and conditional trials

2026-09-15. The follow-up in task
`01a0a25c-e24d-77e1-9864-2827d7867d30` authorizes implementing the Xiangqi task,
using all Qi evidence for authoring, trying Terra, and trying Sol only after a
genuine Terra failure. The exact follow-up message ID is unavailable here.
This record extends the [design](BR-006-xiangqi-budget-player.md); the initial
design and source receipt remain historical. It owns the active execution plan.

## Accepted change

The participant owns the entire deployed player, including move generation,
validation and state transitions. It must preserve the exported Qi game API.
The independent grader retains the original referee and checks legality/API
equivalence. The participant receives working source and an arena without the
author's cost diagnosis, fast implementation, reference solution or grading
families. Source comments describe existing behavior; they do not prescribe the
optimized geometry tables.

The source experiment's completed report attributes 2.974/3.329 seconds (89.3%)
of one profiled decision's cumulative time to legal move generation, with 2.78
million `reaches` calls. This is CPU-heavy geometry work; profiler overhead and
overlapping call stacks prevent interpreting it as a general uninstrumented
cost share. The author snapshots Qi's subsequent fast move generator for a
reference, then checks its behavior against the original independently.

## Implementation and calibration lock

- Own `probes/xiangqi-budget-player/`, BR-006 docs/evidence and its candidate
  card. Read Qi only; preserve other TB3 experiments and their changes.
- Initial deployment profile: one active CPU, 256 MiB, 250 ms CPU per move,
  one-second pre-position initialization; 16 MiB transferred submission.
  Runtime is offline. Libraries and replacement engines are permitted.
- Grading: 32 color-swapped families, 64 complete games; at least 39 actual
  wins, API equivalence and valid resource/protocol behavior. No result-based
  threshold adjustment after freezing.
- Authoring allowance: 3,600 seconds on four CPU / 4 GiB with no GPU. Four CPU
  supports the provided arena; each active player is restricted to one CPU.
  This resolves the original draft's two-CPU authoring suggestion and retains
  its longer-than-standard 3,600-second diagnostic allowance.
- Split before outcomes: exclude the 12 source optimization families, take
  one start per other Qi **development** family, order by SHA256 of
  `tb3-br006-v1:` plus family; first eight public, next eight author validation,
  next 32 grading. Source-game/family disjointness is checked. This is a new
  TB3 partition of previously exposed development inputs, not a claim of fresh
  Qi confirmation data. No Qi locked pool is opened.
- Compare original versus adapted search under fixed budgets; check old/fast
  legal moves, checks, state and replay. Measure quiet-opening completion at
  proposed CPU allowance before accepting that envelope.
- Run baseline self-play, a superficial player, equal-CPU recipe controls and
  the author reference on public/author-validation inputs. Any envelope revision
  occurs before the task freeze and model trials and is recorded below.
- A permitted existing-engine route is an authoring difficulty concern, not a
  reason to ban reuse. The user specifically requests trying this natural task;
  retain that exploratory trial even if the author suspects a readily reusable
  solution. A clean Terra pass retires this snapshot from hard-task selection.

## Conditional model sequence

1. Freeze the complete package and prove matching Harbor 0.18 oracle=1 / nop=0
   without infrastructure exceptions. Audit the agent-visible build context.
2. Run one fresh Harbor 0.14 Docker/Codex trial with
   `openai/gpt-5.6-terra`, `reasoning_effort=high`, 3,600 seconds, subscription
   authentication and the existing explicit proxy. The authoring conversation,
   host Qi repo and author solution are absent from the agent environment.
3. Inspect normal agent completion, actual model configuration, verifier logs,
   artifact and games. A healthy pass ends this candidate's difficulty test.
   A completed zero is a failure candidate until its cause is reviewed.
4. Only after a genuine Terra task failure, run one fresh same-snapshot
   `openai/gpt-5.6-sol`, `reasoning_effort=xhigh` trial with the same resources,
   prompt and time allowance. This is a conditional diagnostic, not the three
   final qualifying Sol trials in requirements.
5. Allow at most one retry of a model configuration for a documented
   infrastructure failure. Preserve both attempts. Do not retry a clean failure
   to get a preferred result or revise a passed task to force difficulty.

Engine supervisor stops at the declared decision budget are normal bounded
search. Agent timeouts, crashes, faulty referee/control behavior, host stalls and
incomplete grading do not establish a model reasoning failure. All passes,
exclusions, denominators and actual failure mechanisms remain visible.

## Calibration and outcomes

Implementation in progress. No task freeze or model results at creation.

### CPU calibration, before any game outcome or model freeze

The frozen 16 public/author-validation starts gave fallback counts 4/16 at
250 ms, 2/16 at 500 ms, 1/16 at 750 ms and 0/16 at 1000 ms. Select **750 ms**:
the smallest measured envelope below the design's 10% fallback review threshold.
Both players receive it. The 64-game threshold and paired starts remain fixed.
The worst-case allowance is now 14,400 CPU seconds (about 60 minutes over four
lanes, before referee/initialization overhead), so the verifier timeout becomes
5,400 seconds. The original 30-minute verifier target is superseded; measure
actual throughput and report it. The solver still receives 3,600 seconds.

The snapshotted fast generator matched 392 board/side comparisons from 196
positions. On that same cold-cache sample, uninstrumented generation consumed
0.2025 CPU seconds for the original and 0.0162 for the optimized version (about
12.5x). Public movement, initial perft-two, immutability, repetition, stalemate
and ply-limit fixtures passed for the reference. These checks establish bounded
behavioral equivalence, not playing strength or exhaustive rules correctness.

### Failure classification clarification

The per-decision CPU boundary is part of this task's functional contract.
A normally completed model submission that produces no legal move within it,
or that breaks the required game API, can be a genuine **artifact correctness
or resource-budget failure** after healthy controls and runner inspection. It
need not support the profiling hypothesis. Distinguish such submitted-code
errors from an agent/harness crash, wall-clock host stall, missing verifier,
or exhausted 3,600-second authoring window, which remain excluded events.

### Author validation complete; packaging ready for controls

The optimized move-generator reference completed all eight author-validation
color pairs: **12 W / 4 D / 0 L**, 75% actual wins and 87.5% draw-adjusted score.
This was an author-validation set, not the 64-game grading suite. The arena's
`pass: false` field on this 16-game run is not a failure: that field is defined
only for the full 64-game grade. Raw games are retained under
`runs/br006-author/reference-calibration/`.

The root-publication adapter matched all original Decision fields in eight
fixed-node comparisons. The reference passed explicit movement/adjudication
fixtures and the separate unprivileged API adapter on 98 histories. Deadline
controls exercised legal forced stopping, restart accounting, missing output,
illegal output and early completion. All 22 unchanged upstream packaging checks
passed on Linux. The first Linux check used a temporary directory with the wrong
slug; preserve that excluded path error separately. README explanation slots
remain explicit human-author placeholders; these mechanical checks are not final
submission approval.

### Infrastructure revision v2, before model trials

The v1 oracle control was deliberately cancelled after 13 game files were
retained because its per-engine `PID modulo CPU count` assignment could collide
across games. This underutilized the four-CPU verifier and prolonged wall time;
it did not change the declared per-move CPU allowance. The original v1 freeze,
archive, interrupted Harbor result (`CancelledError`) and partial games under
`runs/br006-author/oracle-v1-interrupted-games/` remain evidence. No model was run
on v1; this is not an oracle-solution failure or model failure.

V2 allocates one distinct CPU to each game worker and runs both sides on that
worker's CPU. Game records expose the assigned CPU. It also retains bounded
engine stderr and the offending move/API field on failure for reliable diagnosis.
The solver prompt, algorithms, budget, starts and win threshold are unchanged.
Recheck CPU assignment, deadline controls and Linux packaging; then freeze v2
and rerun oracle/nop before Terra. V1's 12/4/0 author-validation result remains
CPU-budget evidence under its recorded implementation, not a v2 throughput claim.

V2 preflight passed: four distinct worker CPUs, all deadline controls, 22/22
unchanged Linux static checks, and explicit rules plus 98-history API checks
under the unprivileged separate verifier. A first-legal player completed four
public games with 0 W / 0 D / 4 L. The [v2 freeze](../evidence/br006-xiangqi-v2-freeze.json)
records the three harness-only changed files and all 84 file hashes.

A fresh image built directly from the frozen v2 `environment/` matched all 44
expected `/app` file hashes, including the original game module in both starter
and baseline. Author solution, authoring, tests, protected verifier and host Qi
paths were absent. Receipt: `runs/br006-author/starter-image-audit-v2.json`.
This audits fresh build contents, not an oracle-mutated live container.

### Official v2 oracle

Harbor 0.18 oracle completed with reward **1**, no exception, and checksum
`27db494fad49aafb2c389e781f1ec06b36450d469d064bbff9b4a821eedbc532`.
All 64 games replayed: **56 W / 5 D / 3 L**, 87.5% actual wins and 91.40625%
draw-adjusted score. Elapsed trial time was 930.53 seconds (15.5 minutes).
Candidate/baseline used 1553.85 / 1555.88 decision CPU seconds respectively;
reported mean completed depth was 2.830 / 2.048, fallback count 0 / 59,
and neither side required forced stops. Depth is diagnostic, not grading proof.
Raw authority: `runs/br006-xiangqi-oracle-v2-20260915/xiangqi-budget-player__ySpc33E/`;
summary: `runs/br006-author/oracle-v2-summary.json`. The task hash was rechecked
before starting the same-snapshot nop control.

### Official v2 nop

The unchanged starter completed all 64 games with **25 W / 13 D / 26 L**,
39.0625% actual wins and 49.21875% draw-adjusted score. Harbor returned reward
**0**, no infrastructure exception, and the same v2 checksum. Its only failed
assertion was the declared 39-win threshold. Both control artifacts matched
their intended sources exactly; the oracle differed from the starter only in
`qi/game.py`. See [matched control receipt](../evidence/br006-xiangqi-v2-controls.json).
Terra/high is now authorized to begin under the frozen conditional sequence.

### Completed disposition

One fresh Terra/high trial completed normally and passed: **56 W / 7 D / 1 L**
over all 64 private games, reward 1, no exception, same v2 checksum. Authoring
took 797.199 seconds of the 3,600-second allowance. See the
[results and limitations](BR-006-results.md) and [round receipt](../evidence/br006-round-summary.json).
The difficulty target was not reached. Retire this snapshot from hard-task
selection; the conditional Sol trial was not launched. No post-answer task
revision or outcome-driven retry was made.
