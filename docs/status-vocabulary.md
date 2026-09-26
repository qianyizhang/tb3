# Workbench status vocabulary

The single source of truth for status codes, display labels, applicability and
definitions is [vocabulary.json](../src/tb3_medical/vocabulary.json). This guide
explains its use. Do not maintain another
label dictionary in the CLI, frontend or documentation.

The three product decisions were confirmed by the user on 2026-09-20:

- The attention queue requires a concrete issue or explicit review request.
  Unassessed historical work is neutral.
- A positive assessment means the stated conclusions are usable within their
  recorded limits. It is not a clinical or submission certificate.
- Experiment progress and evidence assessment are separate primary badges.
  Execution outcomes, availability and submission status appear in context.

Source discussion: `codex://threads/01a0beac-4403-7993-a52f-be13be6d4bb5`.

The CLI and static frontend consume the same catalogue.

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

The [experiment support and verification checklist](reproduce.md#experiment-support-and-verification)
tracks operation support and scoped proof independently. It is not another
experiment-stage ladder or a replacement for these status codes.
