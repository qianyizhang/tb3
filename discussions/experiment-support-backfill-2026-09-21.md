# Experiment support and verification

Source task: [canonical checklist request](codex://threads/01a0c205-b14e-7e71-9609-c753c1fe24ac).
Related explanation: [Evidence Versus Reproducibility](chatgpt-conversation://6ab0ac5d-f98c-83e8-995b-0c33e36dcd0f).
The available explanation ends mid-table; no unseen continuation is treated as a decision.

## User direction and implementation choice

On 2026-09-21 the user asked whether the stages/steps were correct, requested
better terminology if needed, and asked to consolidate an explicit canonical list
and gradually complete/backfill it. That direction authorizes this consolidation
and initial documentation backfill. It does not select a new model trial.

Assistant recommendation, implemented here: call it **experiment support and
verification**. Use independent operation capabilities with scoped proof rather
than one maturity ladder. The suggested first reusable scope in each group is an
assistant recommendation, not a user decision to reopen a parked scientific study.

## Corrections to the earlier explanation

- Canonical evidence records, protocols and group links preserve discoverability
  and provenance. They do not establish that every entry contains completed
  trials, or that the scientific conclusion is valid merely because it is linked.
- Shared Harbor result collection and authored stories already serve historical
  groups. A table marking their collection and inspection as universally absent
  is too strong. Family-specific preparation, native scoring replay and raw-data
  view regeneration remain distinct operations.
- BR-040's preparation restores exact retained task files; it does not demonstrate
  a full upstream-data preprocessing rebuild. Its six native scoring replays and
  standalone MRI proof do not establish fresh model/runtime execution.
- BR-042's completed resume review records exact verifier agreement without a
  maintained native replay method. Historical scoring proof must not be lost when
  identifying the missing maintained implementation. Reproducing extraction is a
  separate question, as are the unresolved anatomical reference disputes.
- Fresh execution verification records an actual new attempt. It need not reproduce
  stochastic model answers byte-for-byte, and cannot be inferred from a successful
  saved-output replay or a passing control scored from a saved answer.

## Canonical homes and first backfill

The [reproduction guide](../docs/reproduce.md#experiment-support-and-verification)
defines eight checklist items and links the seven group lists. Current coverage,
scoped receipts and actionable next backfill live in each group's existing
`methods/README.md`; experiment configs and input manifests remain executable
authority. The old migration inventory remains dated provenance. No second
machine-readable status dictionary or recurring inventory framework is added.

The initial read-only metadata inspection enumerated 38 unique experiments,
220 owned attempt records and 236 owned evaluation records. All 38 protocols
exist and every experiment is referenced by a group finding; all seven stories
exist. Eight entries have zero owned attempt records: anatomy BR-010/011/012,
cardiac BR-025/027/029, tubular BR-025 and longitudinal BR-018. This is a metadata
boundary, not a claim that all eight lack author work. BR-018 explicitly records
an unfinished scaffold with zero model trials.

Only BR-040 declares the maintained `landmarks` method; the current CLI dispatches
native replay/view to that method. BR-042's continuation config separately retains
a local task path with no preparation command. The first pass links these facts
and existing proof without launching preparation, replay, Docker or inference.
Raw-input recovery, current runtime availability and full historical receipt
coverage were not audited by this metadata pass.

## Completion and reopening

Backfill one selected operation and case set at a time, beginning with existing
sources and selected-input recovery. Mark a deliverable complete only with a
scoped source or receipt; retain unknowns, discrepancies and missing inputs.
Historical-only entries need not all acquire execution recipes. A real reuse need
can select one later without changing its original evidence or a parked idea's
scientific disposition.

Reopen the owning checklist when a maintained operation changes, a selected use
requires a historical method, inputs are recovered, or new verification evidence
is retained. Reference adjudication, submission qualification and new model trials
remain separate work.

## Validation of the first backfill

A clean staged snapshot passed `make check PYTHON=python3.12`: 69 tests passed
and one optional imaging test was skipped; metadata, 38 protocol links, 153 source
measurements, artifact policy and Ruff checks passed. A bounded link/coverage check
also confirmed all 12 changed Markdown files' local targets and exactly one entry
for each of the 38 experiments in its owning list, with eight operations per group.
The clean snapshot reports the two already optional Imaging101 previews absent;
this is unrelated to experiment recovery. No browser, model or historical authoring
script was launched, and the separately owned BR-042 showcase files were excluded.
