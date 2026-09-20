# Workbench status vocabulary

The single source of truth for status codes, display labels, applicability and
definitions is [vocabulary.json](../src/tb3_medical/vocabulary.json). This guide
explains its use and the conversion of existing labels. Do not maintain another
label dictionary in the CLI, frontend or documentation.

The three product decisions were confirmed by the user on 2026-09-20:

- The attention queue requires a concrete issue or explicit review request.
  Unassessed historical work is neutral.
- A positive assessment means the stated conclusions are usable within their
  recorded limits. It is not a clinical or submission certificate.
- Experiment progress and evidence assessment are separate primary badges.
  Execution outcomes, availability and submission status appear in context.

Source discussion: `codex://threads/01a0beac-4403-7993-a52f-be13be6d4bb5`.

## Adoption status

The vocabulary defines the target contract. The current CLI and frontend have
**not yet been wired to it** and still use the old fields. This side-conversation
change adds definitions only; it does not reclassify experiments, alter receipts,
change the main migration plan or add validation gates.

During the main refactor, load the vocabulary as package data and include it in
the frontend's existing static build data. Help text, badges, filters and a small
legend should use the same entries. A direct lookup is sufficient; no schema
framework, generated type system or new service is needed. Remove old hardcoded
definitions when consumers switch.

## Usage rules

An experiment has work progress and an assessment of its conclusions. A run has
an execution state and its scoring observations. An idea has an accepted
disposition. These are different questions; most records need only their own
context's fields. Technical manifests and decisions do not require review badges.

For example, an experiment may be closed while a subsequent defect makes its
conclusions need review. A completed model run can have a failing scorer verdict.
A no-op control failing the scorer can be exactly the expected control behavior.

Record review at experiment level, naming affected runs and the conclusion under
consideration. Published summaries and exports that use that experiment receive
the relevant review flag. Do not add a separate approval obligation to every
attempt, evaluation, idea or artifact. A review can reuse an existing authored
assessment when its scope and evidence are clear.

An unresolved concern and an established invalid conclusion are different. Once
an invalidation is acknowledged and there is no follow-up action, it may remain
visible in history without occupying the attention queue. Fixing code does not
restore the conclusion; reassessment does.

Status describes the recorded scope and observation time. Reading or searching
the index does not inspect every raw artifact or certify a live process. A stale
running observation must show its timestamp. Reproduction badges name the task,
cases and receipt they cover.

## Existing-label conversion

This table is a one-time migration guide, not runtime aliases or a fallback reader.
Preserve historical source bytes and attribution. Reuse existing review evidence
where possible; unknown history may remain unassessed without becoming a queue.

| Existing label/field | Treatment |
| --- | --- |
| `unreviewed` | Use `assessment.not_assessed` only for conclusions that require assessment. Remove the meaningless default from attempts, decisions and other inapplicable records. |
| `supported`, general `qualified` | Map to `assessment.usable` where an explicit authored assessment supports the scope. Do not infer it from a pass score, copied label or import alone. |
| `under_review`, `need_fix` | Consolidate to `assessment.needs_review` with a concrete reason or review request. Repair instructions belong in that reason. |
| `invalidated` | Preserve the assessed scope and explanation; use `assessment.invalidated`. Do not rewrite original scores. |
| Experiment `lifecycle: reviewed` | Preserve/link the review event and recover its actual verdict if possible. Determine work progress separately; do not mechanically infer that it is closed or usable. |
| `curated` | Preserve as import/editorial provenance if useful. It is not work progress or an evidence verdict. |
| `screening`, `calibration` | Keep as descriptive phase/purpose tags when useful, not idea disposition. |
| Idea `rejected` | Map to `idea_state.dropped`, retaining the reason. |
| `superseded` | Keep an explicit replacement link and reason. Replacement alone does not invalidate earlier results. |
| `promoted` | Keep the resulting experiment/export link and decision event. It is not submission qualification. |
| `model_pass`, `model_failure_candidate` | Separate agent role from `outcome.pass` or `outcome.fail`. Keep the original classification in historical receipts; task failure alone does not establish a capability claim. |
| `control_pass`, `control_fail` | Separate raw scorer outcome from whether the control met its expectation. A no-op fail can produce `control_expected`. |
| `execution_error`, `launcher_error` | Use `execution_state.error` and retain the specific reason. Do not count it as task failure. |
| `incomplete`, `partial`, `observed` | Preserve actual execution facts; use `partial` only for incomplete evidence collection. `observed` is not a verdict or proof of completeness. |
| `pending` | Use `execution_state.planned` only if it actually describes an unstarted plan. |
| `externally_running_at_migration` | Retain as a timestamped historical observation, never an assertion of current liveness. |
| `available`, `missing_local` | Describe the selected operation's local inputs through `local_availability`, retaining check time and scope. |
| `unverified`, `not_yet_verified`, `historical_recipe_only` | Keep meaningful recovery notes. Display reproduction proof only when a scoped receipt exists; do not create blanket failure/review states. |
| `qualification: draft` | Use `submission_status.draft` for a candidate package. Reserve submission-ready for an explicit assessment against a named, dated profile. |
| `execution_enabled` | Operational configuration, not evidence validity, work progress or user authorization. It should not become a general badge. |

The examples and conversion table do not introduce new mandatory authoring
fields. Generated receipts retain execution facts; the vocabulary controls how
their meaning is presented.
