# Native workbench: minimal authoring and validation plan

Status: decisions confirmed by the user, 2026-09-20. Implementation is recorded in native-closeout.md. The plan narrows the architecture proposed in the
[review](architecture-review.md); the reproduced bugs remain valid findings.

## Design budget

The everyday workflow is **edit a study, run it, inspect the result, record what
was learned**. Replay and clean export are additional operations when needed.
Do not make authors maintain a dependency graph, inventories, hashes, plan IDs
or a collection of review records by hand.

- Keep a small installed Python package and normal imports. Start with modules,
  not the many subpackages sketched in the review. Split only for an actual
  responsibility that has become difficult to maintain.
- Keep ordinary directories and small file manifests. Do not build a generic
  artifact-store framework, database, schema migration engine or plugin system.
- Use one compact experiment config plus Markdown for scientific context.
  Generate execution receipts, exact task snapshots and export manifests.
- Let Git preserve edits to authoring documents. Preserve original execution
  outcomes; a replay is a new observation of the same attempt.
- Reuse the current importer and checks that protect demonstrated behavior.
  Do not add checks solely because an unusual corrupt input can be imagined.
- One fast developer command, `make check`; no extra pre-commit audit layers.
  No routine model, Docker, full-dataset or media-regeneration checks.

## Confirmed decisions

| Decision | Accepted choice | Tradeoff |
| --- | --- | --- |
| Historical execution coverage | Canonical records for all 37; native implementations for methods we intend to reuse; the rest explicitly historical | Avoids making reconstruction of every old trial a migration blocker. A historical record must not masquerade as runnable. |
| Authoring format | Small experiment config and editable Markdown; generated receipts | Easy Codex/manual editing, with fewer uniformly queryable narrative fields. |
| Exploration gates | Explicit diagnostic runs may precede successful controls; benchmark claims/promotion require verified controls | Faster exploration; diagnostic results must remain visibly nonqualifying. |
| Invalidation precision | Flag the affected experiment and its published summaries/exports; retain the affected run list in the issue | Some unaffected conclusions may need manual review. Avoids a general claim-level dependency engine. |

The user explicitly selected all four recommendations. Prior decisions remain fixed:
semantic groups, source-linked idea capture, recommendations distinct from user
decisions, preserved frozen evidence, independent submission ownership, no active
compatibility shims, and protected concurrent work.

## Shared vocabulary

Adopt the site discussion's [vocabulary catalogue](../../src/tb3_medical/vocabulary.json)
and [usage guide](../status-vocabulary.md) as the status authority. The catalogue
is package data consumed directly by the CLI and included in the existing static
frontend build. Remove the old independent definitions at cutover. Use ordinary
lookups; do not add generated enums, a schema system or another configuration layer.

The confirmed presentation rules also constrain the refactor:

- Status axes apply in their named contexts, not as required fields on every item.
  Experiments primarily show progress and assessment of their conclusions.
- Neutral absence of assessment creates no review obligation. The attention queue
  contains concrete unresolved issues or explicit requests with a pending action.
- Reuse authored assessments with clear scope and supporting evidence. A positive
  label must not be manufactured from an import, completion or scorer pass.
- An acknowledged withdrawal can remain in history without occupying the queue.
  Ordinary editing does not require individual approval records for every artifact.
- Historical provenance, replacement links, partial collection, diagnostic purpose
  and scoped replay receipts remain separate from experiment assessment.
- Running and availability observations show their recorded time. Reading the
  index does not poll processes or inspect all inputs. Unknown historical progress
  is left unspecified rather than silently converted to closed or active.

The final three recommendations are confirmed: explicit reassessment may label
narrower conclusions usable after a partial withdrawal; an unchanged diagnostic
attempt may become eligible after exact-task controls and scoped reassessment;
and draft exports may explicitly include flagged evidence with its reasons and
scope. None of these establishes submission readiness.

## Everyday authoring and operation

A group keeps its ideas/decisions, methods, sources, experiments and presentation
together. An experiment's config holds only machine-used fields: stable identity,
task preparation, selected inputs, conditions and relevant status. Its Markdown
explains the question, reference, method, findings and limitations. The scaffold
creates this small set; empty paperwork is not a gate.

The permanent interface should support discovery/scaffolding, run/collection,
replay, presentation and export. Freeze/plan/receipt creation happen inside those
operations. A preview exposes the selected task, condition and runtime before
execution without forcing the user to hand-create intermediate record IDs.
Collection remains a supported operation for externally launched Harbor runs.

The package resolves a workspace from an explicit argument or project marker,
not its installation location. Declare the runtime dependencies actually used.
Heavy imaging/Harbor/media dependencies stay optional. Do not use a personal
Codex cache or old virtualenv name as the supported dependency setup.

Before converting the remaining families, the pilot must reveal which preparation,
scoring and view operations are actually reused. Extract those helpers; preserve
bespoke methods as normal group-owned modules rather than forcing them into a
generic adapter framework.

## Minimal checks, at the point where they matter

| Operation | Necessary check | Excluded routine work |
| --- | --- | --- |
| Read/search/present existing records | Parse known metadata; show stored status, observation time and unavailable local artifacts honestly | Hashing all runs, probing Docker or revalidating the whole evidence tree |
| Save/generated record; `make check` | Required machine-used fields, unique identities, referenced IDs and record/payload separation | A general ontology, schema framework or validators for unused fields |
| Launch a selected run | Selected task/config/inputs exist; snapshot those inputs; record condition and attempt identity; apply the chosen diagnostic/control policy | Verifying unrelated experiments or requiring submission paperwork |
| Collect/replay a selected attempt | Parse the supported result format; preserve attempt identity; distinguish partial/error/results; verify the exact inputs consumed by replay | Auditing all historical raw evidence |
| Record a defect | Name affected experiment/runs, describe evidence, flag its dependent summaries/exports | Automatically proving every scientific claim or guessing which conclusions are valid |
| Export selected work | Verify selected inputs and their declared origins; write into a fresh destination; check the resulting manifest | Making the whole repo reproducible first or certifying current submission eligibility |
| Regenerate a view | Check the geometry/measurement invariants that its renderer relies on | Full media regeneration on unrelated code/docs changes |

Read-only status means recorded status, not a fresh integrity audit. A bug fix
does not restore a conclusion automatically. Assistant recommendations remain
separate from accepted user decisions. These are ordinary workflow semantics,
not an additional compliance process.

Use a small regression set for the demonstrated defects: task JSON must not
become metadata, invalidation must reach the displayed summary, recommendations
must not overwrite decisions, interrupted collection must preserve attempt
identity, and exports must use correct origins and stable recipe hashing. Add
one ordinary end-to-end authoring/replay/export example. Extend tests when a
real failure or new supported operation justifies them.

## Temporary migration work

One-off conversion/reconciliation scripts belong under `tools/migration/` while
needed. They are never imported by the package or exposed as regular `med`
commands. Old catalog/round parsers, pathname relocation maps, mass backfill and
baseline comparison belong here, not in the permanent reader.

Convert existing metadata once into the selected canonical format; retain source
links and attempt identities. Reconcile counts and selected evidence hashes at
cutover. Keep the migration report and recovery manifest; remove completed
conversion code from the active tree once the cutover is accepted. Git retains
the code if another recovery is ever needed. Do not keep dual readers or aliases.

Historical task/scorer bytes remain recoverable evidence. The active application
does not import historical authoring code. Isolated historical replay may execute
its own verified snapshot when explicitly requested. Ordinary metadata should
not require old directory layouts to exist.

## Fix milestones

1. **Package and simplify the core.** Installable entry point; workspace discovery;
   explicit metadata locations; only required field/reference checks; simple
   decision and invalidation semantics. Keep the package small. Validate the
   installed command outside the source checkout and fix the reproduced bugs.
2. **Prove one daily workflow with landmarks.** Edit its config/protocol, recover
   inputs, replay saved CT/MRI outputs, view findings and create a clean export.
   Verify real scientific equivalence where artifacts are available. Use this to
   settle authoring ergonomics before copying the pattern across families.
3. **Convert retained work to the agreed depth.** All experiments use canonical
   records. Reusable methods become native; historical-only entries carry honest
   gaps. Preserve BR-042's owner's latest changes and BR-043's ongoing discussion.
   Do not re-run models as a migration requirement.
4. **Delete temporary scaffolding and close out.** Remove old entry points,
   fallback imports/path maps and duplicate active docs. Run the normal checks,
   a clean install, selected replay/export and a browser smoke check. Have the
   final independent review assess ordinary usage and remaining shims, not invent
   a new integrity certification system.

Make meaningful scoped commits at each milestone. Completion does not require
recovering unknown historical settings or running expensive new experiments.

## What will count as done

- A new experiment needs a compact config and scientific Markdown; generated
  receipts carry the execution details without manual record bookkeeping.
- The installed command works in a clean environment, finds an explicit
  workspace, and does not mutate import paths or require a personal tool cache.
- All retained experiments are represented in the canonical format. Only those
  with native methods and available inputs are presented as runnable.
- Diagnostic attempts, accepted decisions, partial runs and review flags remain
  clear in the ordinary index. A recorded defect reaches the affected experiment
  and the summaries/exports that cite it.
- Selected saved outputs replay and export using their declared inputs; the
  package provenance and recipe serialization defects are fixed.
- The normal checks cover those supported behaviors. Completed conversion tools,
  dual readers, path fallbacks and migration-only checks are absent from daily use.
