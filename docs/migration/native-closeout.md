# Native workbench implementation

Implemented on `codex/native-medical-workbench`, isolated from the active BR-042
owner at baseline `077cfdca8abc2f66be6682a46e32b476391aed5a`.

## Delivered

- Installed Python package and `med` entry point; explicit workspace marker,
  declared core/imaging dependencies and normal imports.
- Compact experiment TOML plus protocol Markdown; Markdown idea cards and accepted
  decisions distinct from recommendations. Generated snapshots, attempts, execution
  receipts and observations replace manual freeze/plan authoring.
- One vocabulary catalogue drives canonical fields, CLI labels and frontend badges.
  Ordinary reads parse known metadata only. Review flags apply to experiments and
  their summaries/exports, including comparisons that reuse an earlier attempt.
- All 555 baseline records retain their IDs: 38 experiments, 218 attempts and 225
  observations, plus source/idea/review records. Six native replay receipts and
  one new export record bring the current total to 562. Original observations and
  historical task/scorer bytes remain unchanged. See the conversion receipt and
  per-experiment inventory.
- Native CT/MRI preparation, scoring replay and plane views. All six saved model
  outputs match their retained metric dictionaries exactly. Historical method
  sources stay explicit evidence; they are not imported by the application.
- Exports use immutable Git bytes or explicit artifacts and preserve recipe bytes.
  The 25-file standalone MRI package passes saved Terra/Sol replay, saved oracle,
  empty-output control and subsequent inventory verification. It remains a draft.
- Portable stories, source-linked figures and canonical retained tour inputs.
  Media rendering uses declared Playwright dependencies, with no personal cache.
  Raw-data derivation and old launchers are retired with Git recovery locators.

## Verification and independent review

`make check` passes using the staged index and Python 3.12: artifact policy,
38 tests (one existing optional SciPy-dependent BR-042 test skipped), metadata
and 153 source-measurement comparisons, Ruff checks and formatting. Selected
asset checks verify 17 figures; selected tour checks verify 985 retained derived
files and display invariants. These optional checks are not part of daily browsing.

A built wheel installs in a clean environment and works from `/private/tmp` with
an explicit workspace. Standalone package verification works without any workspace.
Browser smoke covers seven group cards, BR-040 search/details, attention filtering,
a group story and a rendered landmark tour frame, with zero browser exceptions.
Native CT-partial preparation and a geometry-based review image were generated.
No model, Docker or new Harbor trial was run for this migration.

The independent reviewer reproduced three workflow defects: missing group coverage
for a new experiment, partial collection overwriting interruption with running,
and standalone verification requiring a workspace. All were fixed and regression
tested. A further shared-attempt comparison case was fixed and covered. Bounded
independent re-review found no remaining actionable findings in those fixes.

## Cutover and retained limits

The original `/Users/zhangqy/pkgs/tb3` checkout remains at its owner's branch.
BR-042's six-hour recovery runner still invokes the old launcher when collecting
its eventual result. Replacing that checkout now would break its closeout. The
native implementation is committed in the attached isolated worktree; this is
not a claim that the original checkout has already switched.

Before cutover, let the owner finish collection and commit its run records; inspect
its latest changes, convert any newly generated records to the documented canonical
format, reconcile stable IDs and preserve frozen evidence. Then integrate the
native branch. Preserve the owner's BR-043 discussion and site vocabulary edits.
No dual reader or temporary compatibility launcher is retained in the native app.

Only the selected landmark method has fresh saved-output equivalence proof.
Historical Docker tags/dependency artifacts, other old methods' ignored inputs,
independent off-machine backup and current TB3 qualification remain separate work
when needed. These limits do not create a blanket review queue.

## Final cleanup

Milestone commit `7177822` retains the completed one-time conversion source.
It is removed from the final active tree, along with the superseded exact-export
recipe and its bytecode-producing replay helper. Historical recipes remain frozen
under `exports/history`; active recipes have explicit origins. No migration-only
command, relocation reader, import-path mutation or personal dependency cache
remains in the daily package, tests or media launcher.

The native worktree is clean after the final cleanup commit. Integration into the
original checkout remains deferred solely to preserve the active BR-042 closeout.
