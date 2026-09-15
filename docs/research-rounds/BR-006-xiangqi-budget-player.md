# BR-006 — Build a Xiangqi player under a deployment budget

**State: captured design; no task package or trials yet.** Candidate:
[`xiangqi-budget-player`](../../catalog/ideas/xiangqi-budget-player.json).

## Recommendation

Build a small offline player that **wins at least 39 of 64 games** against a
frozen, clock-adapted Qi enhanced alpha-beta engine. Give both engines the same
**one-CPU, 256 MiB, 250 ms CPU-per-move** envelope. Supply the rules, working
baseline and arena; the deliverable is the player, not a new referee or UI.

The crux is **turning a fixed compute allowance into better moves**. Extra search
components can cost more than they contribute when an iteration never finishes.
This is a useful engineering task; its difficulty for TB3 remains unestablished.
The numeric limits and win threshold below are proposed calibration targets,
not measured feasibility or a promised winning solution.

## Intake and source evidence

- Captured 2026-09-15 from the current user's request to design a budget-limited
  Xiangqi engine with a favorable win rate against a default solution. The
  current request's exact message ID is not exposed in this task context.
- Context: [Optimize enhanced alpha-beta](codex://threads/01a0a24e-8af0-7761-95f4-9b7c7fc73a81),
  `/Users/zhangqy/pkgs/qi`, active turn
  `01a0a24f-ea6f-7d62-8f7c-fe0c4cbff669`, user message
  `01a0a24f-ef8f-7771-a3e2-6e272a31f014`. Retrieval included the active turn;
  large tool outputs were truncated, so relevant repository files were read
  directly. Follow-up execution was still in progress at inspection.
- Prior experiment IDs: `search-components-v1`,
  `saved-checkpoint-elo-20260914`, and `enhanced-potential-20260915`. Recall used
  Qi's `.codex/skills/experiment/SKILL.md` v1.0.0; this record is authored in TB3.
- The active report records 5/12 depth-zero fallbacks at 128 visits, versus 0/12
  at 512 visits on its opening probes. Its original/scaled/lean/PVS screen has
  **0 W / 0 D / 8 L for each profile** against small Pikafish. This pass
  recomputed the four W/D/L totals from retained outcome fields; it did not
  independently replay the games. The report owns the probe measurements.
- The active task later reported 6/6 completed follow-up wins for PVS at 1024
  visits against original enhanced at 128. That is an interim, unequal-budget
  observation, not proof of a PVS gain at equal compute. It is not a final result.
- The [source receipt](../evidence/br006-xiangqi-design-sources.json) retains
  inspected-file hashes, committed baseline blob hashes, screen denominators
  and retrieval limits. Source hashes are provenance, not a frozen task package.

**Selection boundary:** this is a user-requested work-history design. No
published task-level LLM failure supports it yet. Engine losses are not model
authoring failures. It does not displace the
[benchmark-backed shortlist](../research-benchmark-backed.md). BR-005's
scaffolding lesson applies: expose contracts and the real baseline, but keep
the author's proposed repairs and stronger control implementations out of the
solver package.

## Proposed solver-facing task

> Our offline Xiangqi application needs a stronger player within its existing
> deployment budget. Implement a player that runs through the supplied launcher
> and beats the supplied enhanced alpha-beta baseline. You may modify the starter
> or replace its search implementation. The arena and referee are provided.
>
> Submit `/app/submission/` with `build.sh`, `run.sh`, source, required runtime
> assets, and dependency/license notices. Builds must use the documented Linux
> toolchain. The installed player, including custom libraries, books and weights,
> must fit in 16 MiB; the supplied standard runtime is excluded. Run within one
> CPU and 256 MiB, using at most 250 ms of CPU time per decision. The opponent
> receives the same limits. At evaluation time the player must work offline.
>
> Follow the supplied versioned JSON-lines protocol and `xiangqi-training-v1`
> rules. Return legal moves using the full game history. You pass by winning at
> least 39 of 64 complete games over 32 undisclosed opening families, playing
> both colors from each opening. Draws are not wins. All protocol, legality and
> resource checks must also pass. The public arena uses the same conditions on
> different opening families.

The final instruction must contain the complete protocol, accounting policy,
toolchain pins and required timeout trailer. This quoted draft is not a
submission-ready `instruction.md`.

### Supplied surface and budget

| Item | Proposed contract |
| --- | --- |
| Starter | Working enhanced alpha-beta and its source; public referee API, transport wrapper, build example, rules, smoke cases, eight development families and paired arena. |
| Player interface | One JSON-lines process. Each request contains an ID, version-1 Qi snapshot (`initial_fen`, complete ordered `moves`, ruleset), current root legal moves, seed and CPU allowance. |
| Response | `{"id":1,"type":"best","move":"a0a1"}` updates the proposed move; `{"id":1,"type":"done"}` finishes. Flush complete lines. Move shown is syntax only, not a required answer. Diagnostics use stderr. |
| History | Moves use Qi's coordinates: `a0` is Red's left back-rank square. Inputs start at the standard position and carry every prior move, including the opening prefix. A board alone is insufficient. |
| Move allowance | 250 ms aggregate user + system CPU for the entire player process tree; no credit carries between moves. Parsing, search, evaluation, output and position reconstruction are charged. |
| Initialization | Once per game, up to 1 CPU second and 5 wall seconds before any position is sent, solely to load the player. Reinitialization after a forced search stop is charged to the next move. |
| Runtime | One CPU allocation, 256 MiB process-tree memory, no swap or GPU. The process is suspended outside its initialization and own decision windows, so it cannot ponder for free. |
| Packaging | 16 MiB total installed player content; source/build tooling excluded. The fixed standard-runtime allowlist must be published. All submitted books, weights and nonstandard dependencies count. |
| Solver development | Proposed 3,600-second authoring window, 2 CPU / 4 GiB, no GPU. Internet, documentation and reusable libraries/engines are allowed during development. Runtime dependencies must be packaged. |

At the CPU deadline, the supervisor selects the most recent complete, legal
`best` update received within budget. Forced stopping with such an update is
normal completion, not a loss. Kill an unfinished worker and restart it on its
next turn; charge that restart as specified above. An early `done` freezes the
choice and gives no extra budget later. Bound output size and reject stale IDs,
malformed messages and illegal moves as contract failures.

The supervisor measures consumption outside submitted code. Before freezing,
publish the Linux accounting mechanism, sampling/overshoot tolerance and
attribution of CPU at receipt of each update. A separate five-second wall guard
detects stuck decisions; host stalls and runner faults invalidate execution,
not chess outcomes. Self-reported node counts are diagnostic only: Qi visits
and native engine nodes are different units.

Libraries, compiled search, opening books and learned evaluation remain permitted
within the same envelope. These deployment limits are design assumptions to
validate, not observed requirements of the existing Qi application. Do not add
a Python-only rule, engine ban or model ban merely to make a successful solution
fail.

### Default opponent

Use Qi `alphabeta-enhanced` from commit
`6471971fba7f954aea362db6435f4545e5f65ae6` as the **source baseline**. It combines
positional evaluation, quiescence, move ordering, exchange ordering, check
extensions and a 2048-entry transposition table.

Create a separately versioned `enhanced-clock-v1` adapter that publishes its
initial legal fallback and every completed iterative-deepening result. Replace
the old 128-visit/depth-two termination with the common clock allowance and a
depth-eight ceiling. Preserve its search/evaluation semantics. Freeze the
complete dependency closure, adapter diff, build and image, not just this commit.
The adapter does not exist yet; this design does not identify it with an already
measured entrant.

Before clock tests, compare all deterministic decision fields with the original
under equal fixed visit/depth limits on public positions. Before any model
trial, check depth-one completion on quiet calibration positions. More than 10%
fallback-only decisions, unstable baseline self-play, or failure of the
verification-time target triggers a design review. Do not use a starved baseline
to advertise an easy improvement. Any revised allowance requires a new recorded
design before freezing and must apply to both players.

The historical 128-visit enhanced profile may be reported as a secondary
diagnostic. It is not the pass opponent. Pikafish is a stretch comparison after
a valid pass, with separately declared conditions; beating it is not required.

## Evaluation and interpretation

1. **Correctness:** use the frozen referee for every move and replay each terminal
   game. Check cannon screens, horse legs, flying generals, check evasions,
   stalemate-as-loss and history-dependent repetition. Supplied movement helpers
   are allowed; implementing movement rules is not the intended crux.
2. **Adjudication:** retain `xiangqi-training-v1`: a player with no legal moves
   loses; third repetition draws; 300 total legal plies from the original
   standard position draw. The opening prefix counts. Ordinary terminal outcomes
   take precedence. No teacher-evaluation adjudication, survival-length reward,
   move-agreement score or Elo threshold substitutes for actual games.
3. **Starts:** curate eight public development and 32 private grading families,
   one 12-ply start per family, with a frozen sampling policy, source attribution,
   legal replay and duplicate-board checks. Related prefixes and source games
   must remain in one split. Do not select starts based on candidate outcomes.
   Establish a new TB3-owned pool; do not open, reserve or repurpose Qi's active
   locked pool. Retain the CCPD source license if that source is used. Public
   source ancestry does not certify absence from model training.
4. **Pairs:** run the candidate as Red and Black from each identical start,
   using a published seed policy, clean game state and matched CPU conditions.
   Freeze all 64 slots before grading. A partial pair cannot enter the score;
   missing slots prevent a pass. Do not keep adding games until a threshold is met.
5. **Primary grade:** with all 64 games valid and complete, require `W >= 39`
   and no contract/resource failure. This means at least **60.9375% actual
   wins**, with draws in the denominator. Separately report draw-adjusted score
   `(W + D/2)/64`, W/D/L by color, pair outcomes, CPU and peak memory.
6. **Claim limits:** a pass means this fixed suite was beaten. Report an
   opening-family bootstrap interval for score as a secondary diagnostic;
   resample both color games together and expose degenerate results. Do not
   change the grade after inspecting uncertainty. Broader superiority requires
   a fresh preregistered confirmation pool and is outside this initial task.
7. **Runtime:** a dedicated 4-CPU / 4-GiB verifier may run four games at once,
   each with one active player CPU. At the full 300-ply ceiling, the proposed
   search allowance alone is at most 4,800 CPU seconds, about 20 minutes over
   four lanes. Target at most 30 minutes including initialization/referee/replay;
   this is arithmetic and a calibration target, not measured throughput.

The verifier runs separately and receives only the deliverable. Its referee,
opening book, baseline and reward writer remain evaluator-owned. Audit the
referee with known rule fixtures and a second implementation where semantics
agree; engine-reported wins are never authoritative. Preserve all failures and
invalid runs without converting them to losses, draws or model reasoning failures.

## Hypothesis, controls and stop rule

**Hypothesis:** a solver that adds plausible heuristics without allocating work
well will fail to produce a 60% win rate at fixed compute. Evidence to inspect:
completed depths, fallback frequency, tactical mistakes, per-move CPU, and
paired game results. A specific feature such as PVS is not prescribed or assumed
necessary. Teacher agreement and longer games do not support the hypothesis.

| Control / comparison | What it establishes or challenges |
| --- | --- |
| Unchanged clocked baseline versus itself | Color balance, timing stability and whether identical implementations can spuriously clear the grade. |
| First-legal-move and capture-only players | That protocol completion and superficial heuristics do not suffice. |
| Fixed-node equivalence and deadline boundary fixtures | That clock adaptation preserves baseline choices when not interrupted, and CPU deadlines select the correct last update. |
| Existing budget-only, lean and PVS variants at equal CPU | Whether a trivial permitted configuration change already solves the task. No unequal-budget attribution. |
| Ready-made compact engine | Whether reuse alone makes this an easy integration task. Screen [ElephantEye](https://github.com/xqbase/eleeye), whose source documents an engine and UCCI interface; size, compatibility and wins here are unmeasured. |
| Strong author solution | Solvability with comfortable grade and runtime margins on development and a separate author-validation set. Keep its code and diagnostic repair hints outside the solver image. |
| Harbor oracle and nop | Matching frozen package gives oracle=1 and nop=0 without infrastructure exceptions. These controls do not establish model difficulty. |

The source's budget-only gains and existing reusable engines are evidence
**against assuming hardness**. If a simple permitted baseline passes, retain
the engineering benchmark but retire this snapshot from hard-task selection.
Do not respond by moving the threshold, hiding a needed interface, banning the
successful library or cutting reasoning time. If no author solution reliably
passes, revise or park the design before any model attempt.

## Proposed execution handoff

This request authorizes task design; no engine match, model trial, dependency
installation or mutation of the active Qi optimization was performed.

Next bounded implementation: package the referee/clocked baseline/arena, audit
source redistribution, measure the deployment envelope, test the easy controls,
and build a strong reference solution. Freeze source, toolchain, Linux image,
start pool, budget enforcement, threshold and runtime target together.

Only after healthy same-snapshot oracle/nop controls, propose one fresh
Terra/high diagnostic with the repository's pinned Harbor versions. The
3,600-second proposed authoring allowance is an explicit design difference from
the 1,800-second early diagnostic in [requirements](../requirements.md); it must
be resolved in the execution lock. No trial configuration is locked by this
design. Final Sol/Opus qualification and human-authored submission sections
remain separately governed by requirements.

A normal completed submission that misses the win threshold is a task failure.
Attribute it to the proposed conceptual crux only after inspecting the actual
implementation and games. An illegal-move bug is an implementation failure;
API errors, exhausted agent time, process crashes, faulty controls, incomplete
grading and host stalls do not establish the hypothesized reasoning failure.

| Candidate | Execution validity | Task result | Hypothesis support | Disposition |
| --- | --- | --- | --- | --- |
| BR-006 / xiangqi-budget-player | Not run | Unknown | Unknown | Design captured; calibrate before packaging as a hard benchmark. |

## Dated decision

- 2026-09-15 — Default design uses enhanced alpha-beta, equal measured CPU,
  actual wins and paired openings. An optional baseline-choice question was
  offered; no reply was available while writing, so enhanced is a stated design
  assumption. Limits and difficulty remain provisional.
