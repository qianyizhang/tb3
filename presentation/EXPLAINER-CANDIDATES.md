# Explainer completion plan

Complete the **106 unfinished core entries** identified by the 2026-09-29 scope
audit, one at a time. The [scope register](EXPLAINER-SCOPE.md) classifies all 205
entries; its [machine-readable ledger](EXPLAINER-SCOPE.json) owns queue eligibility
and group priority. The [review ledger](EXPLAINER-LEDGER.json) remains the single
authority for live review status, source blockers, bindings and acceptance receipts.

## Current scope gate

The user's 2026-09-29 request to classify, prioritize and exclude unrelated tasks
supersedes the original all-entry completion objective. Detailed membership and
priority are assistant judgments recorded in the scope ledger. **154 entries are
core**, **13 are held candidates**, and **38 are outside automatic completion**.
The audited core snapshot has **48 reviewed and 106 unfinished**; always join
current review status by `entry_id` before selecting the next entry.

1. **P0 — existing TB3 research:** six unfinished internal entries.
2. **P1 — clinical image tasks:** 38 structural-task and 30 reading/workflow entries.
3. **P2 — image formation/restoration:** 32 unfinished entries.
4. **P3 — candidates:** relevance review only; no automatic explainer completion.

Use scope-ledger group order, then review-ledger entry order; skip reviewed rows.
The old `completion_program.sequence` and `active_entry` are retained historical
program state, not selection authority when they conflict with this scope gate.
In particular, **`imaging101-eht-black-hole-original` is excluded**. Preserve its
in-progress files and later receipts; do not schedule additional nonmedical work.
The live explainer chat must reread this plan at its next selection boundary.
This document does not interrupt that chat or enforce a runtime scheduler.

The user's subsequent 2026-09-29 clarification replaces blanket dependency
deferral: **attempt source resolution first, then use a scientifically sound
symbolic illustration if actual data remains unavailable**. Noncommercial task
interpretation is the intended use; public redistribution is not required.
Every symbolic illustration needs a one-sentence warning at the very top stating
why actual data is absent and how to obtain it. The
[workflow](EXPLAINER-WORKFLOW.md) defines bounded attempts, evidence records,
symbolic acceptance and genuinely deferred dependencies. The ledger's
`dependency_resolution` is current; original blocker and deferral fields retain
history. No download attempt, rights clearance or visual acceptance is inferred.

No prior review, frozen bytes, score, receipt or source record is invalidated by
scope exclusion. Candidates require a specific biomedical question and source/
reference contract before promotion. Generic methods require a concrete medical
application; historical work remains closed. Record subsequent scope decisions
with actor, source and rationale in the scope ledger.

## Historical starting point

At commit `27fcca9`, the blueprint refactor is committed and locally verified;
remote delivery/CI remains open. The catalogue has 13 reviewed teaching stories,
42 pending operation reviews, 102 source-contract blockers and 48 source-input
blockers. These are assistant visual/engineering statuses, not clinical, model
or user acceptance. Preserve the existing 13 reviews and their original receipts.

The authorized local work covers source inspection, contracts and briefs, task-specific
story authoring, necessary shared recipe changes, local media exports, visual
review and focused commits. Push to `main` remains pending explicit user approval
after automatic approval review rejected the first push; remote CI depends on that
delivery. Continue local entries while this approval is pending. The work does not launch medical/model trials,
rewrite frozen evidence, install medical runtimes or publish the website. Public
source research and small licensed teaching inputs may resolve dependencies;
restricted access, unclear rights or large acquisitions need a concrete decision
if they become necessary. Never relabel missing evidence as completed content.

## Historical execution order

Counts below preserve the original 2026-09-27 plan for provenance. They are not
the current queue; the scope gate above controls all new selection.

| Order | Workstream | Entries | Main completion requirement |
| --- | --- | ---: | --- |
| 0 | Deliver the blueprint refactor | — | Push the existing commit; inspect repository and Node 22.18 presentation CI. Repair actual failures in a focused change. |
| 1 | Anatomy identity and audit | 5 | Start with supplied-object identity, then mixed-tissue audit; distinguish naming, ownership, mask reasoning, curation and annotation construction. |
| 2 | Correspondence | 4 | Distinguish rigid, respiratory and MRI–US correspondence; native frames and unavailable points remain explicit. |
| 3 | Tubular anatomy | 3 | Preserve source screening versus repair; show topology, allowed edit extent and unchanged controls. |
| 4 | Remaining WSI definitions | 2 | Preserve object inventory, tissue/cell context, annotation granularity and source coverage. |
| 5 | Longitudinal reading | 3 | Separate detection, segmentation and linking; supplied candidate locations must match the actual condition. |
| 6 | Cardiac shape and motion | 6 | Separate supplied contours/anchors/material trajectories from inference; retain calibration and observation limits. |
| 7 | Segmentation and localization | 8 | Task-specific targets, native coordinates, tool assistance and missing targets; no generic segmentation substitute. |
| 8 | Internal reporting and data | 4 | Show actual data transformations, provenance and output schema; distinguish proposed work from retained tasks. |
| 9 | External overview entries | 7 | Explain each repository's actual workflow and tier boundaries; overviews do not complete child definitions. |
| 10 | Imaging101 source contracts | 56 | Audit each pinned operator, measurement, assistance and evaluator; derive appropriate numerical or source-based teaching views. |
| 11 | HealthAgentBench source contracts | 14 | Resolve prompt/helper/evaluator visibility and construct reference-free worked records for each definition. |
| 12 | BCER source contracts | 8 | Pin the exact task revision, inputs, allowed helpers and output/evaluator contract before story selection. |
| 13 | ABRA source contracts | 5 | Explain tool/interaction and longitudinal boundaries from the exact source conditions. |
| 14 | RadAgent source contract | 1 | Establish the staged input, report/tool flow, output and reference boundary. |
| 15 | REXMLE source contracts | 18 | Preserve dataset/track/class conventions, targets, scoring and per-task source limits. |
| 16 | AutoMedBench Full inputs | 48 | Inspect each retained harness and tier; resolve `dataset.included=false`, model assistance, labels and scoring before choosing example assets. |
| 17 | Whole-catalogue closeout | — | Reconcile all 205 entries, perform integrated regression review, verify exports and final CI, and deliver a clean committed tree. |

## Per-entry workflow

1. **Resolve:** read group guidance, leaf catalogue, current brief, ledger row,
   exact prompt/staging/scorer and pinned sources. Record original inputs,
   assistance, tools, output, units/frame, reference visibility and scope.
2. **Establish assets:** inspect retained inputs and receipts first. Check source,
   license, hashes and sample/annotation coverage. Teaching geometry must be
   labeled and cannot stand in for source images or scientific evidence.
3. **Author:** choose a semantically suitable existing recipe. Add a small explicit
   operation contract when needed; retain the common player, stage and exporter.
   Draft through `med story new`, write meaningful input/operation/output/limit
   beats, validate with `med story check`, then explicitly bind the story.
4. **Build and export:** use a fresh local destination for HTML, MP4, captions,
   transcript, representative frames and source-pinned receipts. Check hashes,
   dimensions, frame counts, seeking and full decoding. Retain failed attempts.
5. **Inspect:** review first, decisive and ending frames plus motion and timing;
   inspect the actual Explorer entry, legends, output, source roles, narrow layout,
   keyboard/reduced-motion and no-GPU behavior. Fix defects before acceptance.
6. **Record and deliver:** retain entry-specific observations, reviewer, source
   snapshot and limits. Update only the reviewed entry and recompute ledger
   counts. Run relevant checks, stage exact owned paths, run the staged-index
   gate before tooling commits, commit and push a focused unit.

Use [canonical explainers](EXPLAINERS.md) for commands and contracts and
[fixture retention](assets/teaching-fixtures/EXPANSION.md) for provenance.
Browser launches use the disposable repository harness with approved execution
outside the restricted macOS sandbox. Startup permission failures block browser
verification; stop unchanged relaunches.

## Dependency handling and resumption

The user's 2026-09-29 follow-up defers all dependency-blocked core entries to a
later session. Retain each reason and reopening action in the review ledger's
`dependency_deferral` field; continue to the next ready entry. Use the
[scoped workflow](EXPLAINER-WORKFLOW.md) to derive the queue and dependency register.
If no ready core entry remains, report that state explicitly. Regression pilots
on already reviewed entries validate tooling without adding completions.

Work sequentially through the scope-filtered, priority-ordered queue. An entry is complete
only when its own integrated explanation and review are supported by receipts.
A family story, successful compilation, source download or batch receipt alone
does not complete its siblings. The existing 13 entries remain in final regression
scope but are not re-entered into the new-work queue.

For a source blocker, first inspect existing local receipts and the exact pinned
upstream source. Record the specific unresolved field/input, inspected evidence,
attempt date and concrete next action in that entry. If external access or a
user decision is indispensable, record it for the deferred dependency session
and continue the next actionable entry. Preserve existing unanswered questions.
Keep blocked core rows in the core denominator; retain all 205 inventory records.
Do not manufacture a reference or adopt a generic/static replacement solely to
increase completion. The current exclusions implement the user’s scope-audit request. Any later
change must record its actual actor, rationale and scope; do not attribute an
assistant classification to a user decision.

At each checkpoint, preserve the active entry, completed commit, local artifact
path and any specific blocker in the ledger/program record. Resume at the first
unfinished actionable entry; do not rerun accepted work without a changed
dependency or failure. Source audits are inspectable records, not new model runs.

## Final acceptance

- Every core entry has its own reviewed disposition and receipt; unresolved
  core blockers remain incomplete. Candidates and exclusions are reported
  separately and never counted as completed explainers.
- The 205-entry inventory, 154-entry core scope, story bindings, sources and
  both ledgers reconcile. Refresh snapshot counts if review status changes.
- All exports have source/asset/frontend provenance and verified artifacts.
  Entry review and standalone export review remain distinct.
- Shared-runtime changes pass relevant Python, TypeScript, browser and media
  checks. The final staged/committed tree passes repository checks and remote CI,
  including the declared Node 22.18 environment.
- Frozen task bytes, original scores and prior receipts remain intact. Generated
  media stays local; the final report links the review gallery, commits, evidence
  and any user-approved scope changes.
