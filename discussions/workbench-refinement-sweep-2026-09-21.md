# Workbench refinement sweep — 2026-09-21

Source task: `codex://threads/01a0c040-3777-7b72-b932-6e6b118304a2`.
Reviewed baseline: `a3c9be8383e28ded7b1ff3f30890f3964d80814f`.
Original review actor: assistant. The original proposals below are retained as a
dated review. The user subsequently accepted all four interview recommendations
and the full refinement pass in this source task. No trials are authorized.

## Accepted decisions — 2026-09-21

Actor: user. Source: the task above, response “all your rec” after the four-choice
decision interview.

1. Block reuse of controls from experiments with unresolved review issues until
   explicit scoped reassessment clears them, using the existing experiment-level
   review boundary.
2. Retain preview images with complete source notices and their individual usage
   restrictions. Previews with incomplete notices remain optional until resolved.
3. Park the MR frame association, triplanar SVG and source-depth registration
   ideas, retaining their results and concrete reopening conditions.
4. Put the scoped BR-042 branch-identity dispute into the attention queue for both
   affected experiments. Preserve original scores and geometric observations.

The implementation also includes the straightforward engineering refinements in
R01–R11. The existing BR-042 showcase files remain separately owned.

## Implementation closeout — 2026-09-21

All R01–R11 refinements are implemented. Controls now honor their owner's review
state and current execution evidence; neutral reassessment cannot bypass an
invalidation. Launcher failures return a failing command status, group membership
is derived, and export verification checks executable modes. Protocol and chapter
links resolve, source readers preserve exact text, navigation retains context and
keyboard focus, and tour/locale requests honor the latest selection.

Six finding summaries now state concrete results and limits. Six source records,
the three accepted parked-idea decisions and the scoped BR-042 naming issue are
recorded. Nine existing preview images are retained with complete notices and
individual restrictions. Two Imaging101 images remain optional pending recovery
of their complete source notice; the clean portable view explains their absence.

Clean staged snapshots passed `make check PYTHON=python3.12`: the complete
implementation ran 70 tests, with 69 passing and one optional imaging skip, plus
metadata, 153 source measurements, 38 protocol checks, artifact, lint and format
checks. `make presentation-check PYTHON=python3.12` passed against a fresh snapshot
with no local scans: seven chapters, ten chapter links, 160 briefs, 379 conditions,
nine exact embedded sources, keyboard/history/mobile checks and deferred tour
loads. Both browser suites reported zero page errors or remote requests. The
separate CI workflow is configured but has not been run remotely.

Independent reviews covered core behavior, research wording and presentation;
their actionable findings were repaired and rechecked. All nine separately owned
BR-042 work files retain their original hashes. No model trial, publication,
frozen-input change or score revision was performed. The
[implementation receipt](../docs/evidence/workbench-refinement-implementation-2026-09-21.json)
records the checks, scope and exact implementation hashes separately from the
unchanged baseline receipt below.

## Original proposal and baseline

The current small package, semantic groups and evidence-preservation workflow are
worth keeping. The next pass should repair demonstrated workflow and navigation
defects, then sharpen the summaries that help a reader understand what was learned.
The accepted [minimal design](../docs/migration/native-workbench-plan.md) remains
the boundary: ordinary files, compact authoring, experiment-level reviews and
native methods only where reuse justifies them.

## Scope and verification

Three independent read-only reviews covered core tooling, research records and
presentation. The coordinating review covered current guidance, CLI entry points,
checks, ownership and recent migration decisions. Coverage included seven groups,
38 experiments, 571 baseline records and the 160-brief Task Explorer. Historical
source records were inspected where relevant; this was not a full raw-run hash
audit, clinical adjudication or independent replay of every experiment.

- `uv run --no-sync make check PYTHON=python3.12` passed: 43 tests passed, one
  optional imaging test skipped; 2,039 index files passed the artifact gate;
  153 source measurements, metadata, lint and formatting passed.
- The existing Task Explorer browser check passed across 160 briefs, 284 source
  records and 379 conditions; 12 images decoded, with zero page errors or remote
  requests. Targeted additional interactions found gaps that suite does not cover.
- A fresh portable presentation built seven group pages and 571 records. Direct
  HTML targets existed, but chapter navigation still led to raw Markdown.
- A bounded link scan found no missing paths in 104 relative links across 26
  current guides/group READMEs. The protocol scan found 85 broken links out of 87,
  across 37 experiment protocol wrappers.
- Core reproductions used temporary workspaces and mocked launchers. Their
  [retained receipt](../docs/evidence/workbench-refinement-sweep-2026-09-21.json)
  distinguishes demonstrated behavior from possible impact on existing evidence.

The dirty tubular README, coronary idea and BR-042 presentation belonged to the
separate showcase task and were left untouched. The original sweep added only its review
record and concise receipt. No runtime installation, model trial, dataset
download, publication, score change, staging or commit was performed.

## A. Workflow correctness

### R01 — Make control reuse respect review state and observation history

Priority: high. Scope: moderate, within the existing control selector.

[`check_controls`](../src/tb3_medical/workflow.py) at lines 286–301 accepts any
matching historical oracle-pass/no-op-fail observation. The run gate at lines
351–355 considers only the target experiment's assessment. In a temporary fixture,
an issue against experiment A's oracle set A to `needs_review`, yet an ordinary
nondiagnostic run of B with identical task bytes reached the mocked launcher.
This demonstrates a gate defect; it does not establish misuse in a real study.

The same selector can also reject good recollection: after a raw result gains
metadata and is collected again, the new observation verifies, but validating the
older observation first raises `Changed input` against its retained hash.

Select the applicable control observations before validating their evidence. Honor
affected-attempt issues, experiment assessments and scoped reassessment; retain
superseded observations without letting them authorize reuse or veto a valid
replacement. Do not infer that the earliest or latest passing score is sufficient.
Regression cases should cover cross-experiment reuse after a control issue,
recollection, replacement controls and explicit diagnostic behavior.

### R02 — Return a failing exit status for operational launch failure

Priority: high for scripting. Scope: small.

[`workflow.py`](../src/tb3_medical/workflow.py) lines 413–446 records launcher
failure and returns its receipt; [`cli.py`](../src/tb3_medical/cli.py) lines
245–246 then returns zero. A mocked launcher exit of 17 produced CLI exit 0,
`execution_state: error`, and no collected result. Return nonzero for operational
failure after retaining the receipt. Keep a completed model's failing scorer
outcome separate from a failed command. Verify both branches with mocked runs.

### R03 — Protect concurrent experiment membership updates

Priority: next robustness pass. Scope: small to moderate.

Two simultaneous `new()` calls can overwrite each other's group membership update
at [`workflow.py`](../src/tb3_medical/workflow.py) lines 66–69. A deterministic
temporary fixture retained both experiment files but only one new group member;
`validate()` still passed. Group review propagation uses this membership, so the
omission matters beyond navigation. Use a small lock/conflict retry, or derive
membership from the canonical experiment ownership. Detect inconsistency in the
existing validation pass. No existing lost update was established by the sweep.

### R04 — Verify the executable mode already declared by an export recipe

Priority: next export touch. Scope: small.

The exporter applies the recipe's mode, but verification at
[`packaging.py`](../src/tb3_medical/packaging.py) lines 162–168 checks content only.
Changing a temporary exported script from 0755 to 0644 still verified. Compare
the declared executable contract as well as bytes, with platform behavior stated
explicitly. This adds no new manifest system and does not concern clinical validity.

## B. Reader-facing correctness and discovery

### R05 — Repair protocol links and rendered chapter navigation

Priority: immediate. Scope: small.

The migrated protocol wrappers ascend five directories where four are needed.
For example, [BR-040](../groups/anatomical-landmarks/experiments/br040/protocol.md)
lines 9–11 resolve outside the checkout. Repair all 85 broken wrapper links while
preserving their historical targets. Extend the existing story-link validation to
these maintained protocol wrappers; intentional local-only sources need explicit
treatment rather than indiscriminate link checking of frozen history.

Separately, all ten previous/next chapter links in the generated site point to
copied `groups/.../story.md`, despite rendered `stories/*.html` pages being
available. [`presentation.py`](../src/tb3_medical/presentation.py) lines 253–267
needs a source-story-to-rendered-page mapping. Preserve fragments and ensure
rendered headings have matching IDs where required. Test the actual chapter chain,
not merely destination existence.

### R06 — Make local Task Explorer sources inspectable

Priority: next reader pass. Scope: moderate.

Thirteen local source references across eight briefs render as plain paths. The
internal vessel brief's Sources panel has five source rows and zero clickable
sources. [`task-explorer/app.js`](../presentation/task-explorer/app.js) line 210
links HTTP sources only; [`task_briefs.py`](../src/tb3_medical/task_briefs.py)
lines 142–148 checks local sources without packaging their content.

Embed a small source viewer or supply an explicit companion bundle for selected
protocols, task cards, attribution and visual-provenance receipts. Label omitted
local artifacts honestly. Reuse the existing allowlisted packaging approach;
do not automatically include raw scans or run directories. Verify source access
from the portable artifact without the original checkout.

### R07 — Preserve keyboard focus and honor the latest tour selection

Priority: next interaction repair. Scope: small to moderate.

Task/repository selection rebuilds its focused DOM node. Offline Chrome checks
showed Enter activation leaving focus on `BODY`; the existing tab, condition and
selector checks still pass. Restore focus to the selected navigation control or
deliberately move it to the new heading. Relevant code:
[`task-explorer/app.js`](../presentation/task-explorer/app.js) lines 121–126,
232 and 246.

The tour player commits every asynchronous load at
[`tour.js`](../presentation/tours/tour.js) lines 119–121. A deferred-load fixture
executing the production function requested vessels then cardiac, completed
cardiac then vessels, and ended on vessels. Use a selection token so older
successes and errors cannot replace a later selection; include language changes
in that lifecycle. Add a deterministic race regression without loading real scans.

### R08 — Connect the main index and Task Explorer, and retain browsing state

Priority: usability enhancement. Scope: small to moderate.

The shared index and standalone Explorer remain separate entry points. Provide
a visible Explorer entry and an intentional way back to experiment evidence;
make the portable build's inclusion or omission explicit. The main index reads
`q`, `kind` and `group` once but does not write filter changes to the URL or restore
status at [`presentation/app.js`](../presentation/app.js) lines 119–125. Serialize
filters and selected records so a useful view can be shared, reloaded and revisited.
Treat this as a discoverability improvement, not a failure of the existing Explorer
route behavior, which already has regression coverage.

## C. Research interpretation and maintenance

### R09 — Replace generic synthesis with precise, bounded conclusions

Priority: high editorial value. Scope: moderate, group-owned writing.

Six synthesis records provide broad methodological lessons, one receipt and a
generic limitations paragraph while depending on most or all group experiments.
The [tubular synthesis](../groups/tubular-anatomy/findings/tubular-anatomy-current-synthesis.json)
cites BR-030 while also covering BR-041/042; the anatomy synthesis has the same
pattern. Use the existing fields to state a few concrete conclusions, supporting
experiments, assistance conditions and limits. The
[landmark finding](../groups/anatomical-landmarks/findings/landmarks-availability-and-localization.json)
is a useful local model. Keep experiment-level propagation; no claim-graph engine
or mandatory per-case paperwork is proposed.

For BR-042 specifically, the
[branch review](../docs/research-rounds/BR-042-v3-branch-review.md) lines 51–55 and
[six-hour protocol](../groups/tubular-anatomy/experiments/br042-v4-6h/protocol.md)
lines 46–50 describe pending anatomical identity adjudication, yet the current
experiment has no attention flag. Once its owner confirms the affected conditions,
record one scoped pending issue using the existing workflow. Preserve geometry
observations and original scores; this is not an invalidation of the reference.
Unassessed history remains neutral under the accepted status vocabulary.

### R10 — Reconcile a few stale idea summaries and source indexes

Priority: targeted editorial cleanup. Scope: small to moderate.

MR frame association and triplanar SVG cards say their snapshots were retired
while showing `Exploring`; source-depth registration says no further trial is
scheduled. Their reopening text often repeats the old disposition. Distinguish
the retired snapshot from any still-open scientific question, recover actual
decision provenance, and state a concrete reopening trigger. Do not invent a
user disposition or revive the historical failure-first selection policy.

The tubular source index lists ImageCAS but omits separately navigable TopCoW and
AeroPath records; cardiac sources use one umbrella entry for distinct synthetic,
model-derived and clinical references. Add small source records pointing to the
existing receipts and terms. Current access and redistribution permission require
checking only when those sources are selected for reuse.

### R11 — Make demonstrated regressions part of maintained checks

Priority: alongside each repair. Scope: moderate in total.

The current [Makefile](../Makefile) and [CI](../.github/workflows/ci.yml) run fast
Python checks, while the substantial
[browser suite](../tests/task_explorer_ui.cjs) is optional and currently assumes
the Chrome channel. Add an explicit presentation-check command and a changed-surface
CI job using a declared browser runtime. Cover rendered chapter routing, local
provenance access, keyboard navigation and the deferred tour-load race. Keep core
control/concurrency/exit-code/export regressions in the offline Python suite.

Document what each check proves. All six current task-card source hashes match,
but the narrative checker intentionally verifies selected values rather than the
stored source digests. If digest enforcement is needed, put it in an explicit
selected-publication verification step, not ordinary reads. Do not add raw-data
scans, media rendering or inference to routine checks.

## Recommended sequence and acceptance

1. **Reliability and navigation:** R01, R02, R05, R07, plus their focused R11
   regressions. Exit when the reproduced failures are covered and repaired while
   existing checks still pass. Preserve all scientific artifacts and outcomes.
2. **Usable evidence:** R06, R08 and R09. Exit when a reader can move from question
   to a concrete conclusion, inspect its exact source and retain the browsing
   context. Coordinate BR-042 changes with the showcase owner.
3. **Bounded maintenance:** R03, R04 and R10 on the relevant surfaces. Retain
   simple files and the current authoring model.

No broad directory refactor, second metadata framework, blanket historical review
queue or reconstruction of all old experiments is warranted by this sweep.
Reopen this review when the repair batch is accepted, a retained reproduction
changes, reader feedback reveals another concrete gap, or new maintained methods
make the current small-module boundary insufficient.
