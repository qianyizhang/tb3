# BR-002 local pilot execution

Authorized 2026-09-14 by the user's “go ahead to test them out”. This plan
advances the [captured designs](BR-002-sol-astra-capabilities.md) into local
experiments. It is a capability pilot, not final submission qualification.

## Predeclared protocol

Process D02, D04, D03, D01 sequentially. Complete author controls, freeze,
matching Harbor oracle/nop and the natural-task pair before the next model
task. Author preparation may proceed while an earlier run completes.

Each valid task receives one Codex / `openai/gpt-5.6-sol` / max run and one
Codex / `openai/gpt-6-astra` / max run, Sol first, Harbor 0.14.0, Docker,
1,800 agent seconds, one concurrent run. Oracle/nop use Harbor 0.18.0.
Keep Internet and ordinary libraries available; use the existing explicit
subscription proxy configuration from `docs/setup.md`. Each natural pair
uses identical frozen task bytes and the same tool/measurement/image access.
Record the installed CLI version and actual result config, not just this plan.

If both pass, retire the snapshot without repeating it or running ablations.
If a healthy pair splits, first independently reproduce the failed behavior and
audit fairness. For a genuine split, run two additional same-freeze pairs
(Sol then Astra each time), then one pair on the single targeted ablation if
the split recurs in at least two of the three natural pairs. Freeze ablations
separately. If both fail, audit both; retain the task as a lead without asserting
a capability difference. Infrastructure failures receive at most one repaired
same-task retry and never count as model failures. Preserve every attempt.

Before every model run: require a complete public contract, validated thresholds,
independent expected outputs, strongest straightforward permitted baseline,
targeted incorrect controls, healthy oracle 1/nop 0, and a saved freeze with
file digests. A fixture/reference defect is repaired before the freeze. No
post-result difficulty inflation, library bans or shortened reasoning budgets.
If a task cannot be made valid within its stated scope, retain the concrete
defect and park that pilot; continue the others.

## Design completions

D04's missing tail will be re-authored locally as a versioned design completion,
not attributed to the unavailable source download. GOLD-GLYPHS supplies glyph
identity and box coordinates but no voice assignment, event onsets, tie grouping
or accidental-to-note association. It runs only under the split rule above.
Both models get the same readable PNGs and image tool. The fixed artifact
baseline is an independent transcription of the final raster; output event
ordering is irrelevant. All four excerpts and exact F1 thresholds are public.

Record validity, task success and hypothesis support separately. Related fixture
encodings are not independent model attempts. Add outcomes and evidence to the
owning round, catalog and ledger; keep raw runs local. This protocol deliberately
uses a Sol/Astra pair rather than the usual Terra sanity screen, because the
round's experimental question is a Sol/Astra difference. It does not replace
the Sol/Opus final qualification requirements.

## Reproducing author checks

The local author environment is Python 3.12 with resolved dependencies in
`configs/br002-authoring.lock.txt`. Each probe contains `authoring/validate.py`.
Run authoring in a scratch copy with `PYTHONDONTWRITEBYTECODE=1`; generators and
the score validator emit derived files. Do not run them over retained freezes. The exact current
source bytes are enumerated by `docs/evidence/br002-*-freeze.json`.

Commands and immutable job naming are recorded in
`docs/evidence/br002-evaluation-plan.sh`. Existing job names must not be reused.
No dependency install or trial is launched by repository CI.
