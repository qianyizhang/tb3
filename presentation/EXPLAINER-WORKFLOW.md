# Scoped explainer workflow

The [scope ledger](EXPLAINER-SCOPE.json) selects core entries and group priority.
The [review ledger](EXPLAINER-LEDGER.json) owns live status, exact dependency reasons,
reopening actions and acceptance receipts. The [completion plan](EXPLAINER-CANDIDATES.md)
owns the current user scope. Generated queues and dependency registers are projections.

## Resolve sources before deferring

The user's later 2026-09-29 instruction supersedes blanket deferral: the next
session first attempts missing downloads and unfinished source audits. Intended
use is noncommercial task interpretation; public redistribution is not a completion
requirement. This resolves the earlier unanswered delivery-scope questions without
asserting new source rights. Check the terms applicable to the actual local use.
The original all-205 goal remains paused and is not this workflow's selection authority.

`med explainer queue` separates `needs_resolution` from production `ready` and
`deferred`. The ledger's `dependency_resolution` owns the current category, attempt
state and next action; `dependency_deferral` and original blocker wording preserve
the earlier decision. A missing download or unperformed audit is actionable work,
not evidence of an external access barrier. All 106 unfinished core entries start
in the resolution queue; none gains visual acceptance from this policy change.

| Recorded issue at policy change | Entries | First action |
| --- | ---: | --- |
| Contract/visibility audit not established | 50 | Read pinned prompt, staging, operator and evaluator; inspect local examples |
| AutoMedBench Full declares data not included | 46 | Follow the official per-task dataset route; try a small matching sample |
| Missing case evidence | 4 | Resolve CT/report, CT/label or retained trace pairing |
| Low-dose CT source/version mismatch | 1 | Find matching 300-photon data and units; do not reuse incompatible 1000-photon results |
| Cardiac source-asset delivery scope | 5 | Apply interpretation scope; inspect retained audits and applicable local-use terms |

These are local-record classifications, not a fresh access audit. The four case
gaps are report-backed reading, HealthAgentBench CT-RATE, AutoMedBench KiTS19 and
RadAgent. An earlier KiTS19 request timed out; CT-RATE account authorization was
not tested. Neither establishes that acquisition is impossible.

For each entry, inspect retained audits/assets before revisiting the official
repository and dataset route. Reuse one dataset-level resolution receipt across
variants, while checking each variant's contract. Try a small task-matched sample
when access and terms permit. Record source/revision, requested case, URL or local
path, action/date, outcome and retained receipt; distinguish not attempted, timeout,
access gate, missing exact version and confirmed restriction. A practical default
is one focused pass of about 15 minutes per shared dependency, with a second route
when the first fails transiently; extend when progress is concrete. This is an
effort guide, not evidence that every alternative was exhausted.

If actual data remains unavailable, use the symbolic route below and continue.
Only an obstacle that also prevents a sound symbolic explanation stays deferred:
set `dependency_resolution.state` to `external-blocked`, with concrete `evidence`
and `reopen_condition`. Preserve attempts and distinguish external access from
an unresolved scientific contract. Do not ask the same scope question again.
The [dependency register](EXPLAINER-DEPENDENCIES.md) is a dated generated view;
regenerate it from the live ledger when dependency state changes.

```sh
uv run --no-sync med explainer queue --output .local/explainers/NEW-QUEUE.json
uv run --no-sync med explainer dependencies --output .local/explainers/NEW-DEPENDENCIES.md
```

The historical `defer-blocked` command is for an explicit decision to postpone
resolution; do not use it to undo this policy. Refresh the artifact-policy hash
before staging a changed ledger.

## Symbolic fallback and the top warning

The user authorizes symbolic illustrations after a documented resolution attempt.
Show a visually interpretable, task-specific input → operation → output sequence:
plausible geometry, correct operator relationships, meaningful labels and units,
supplied helpers distinct from hidden references, and a clear settled result.
Use original code/vector/geometry illustrations. A generic decorative animation
does not explain the task. Do not synthesize purported patient findings, ground
truth, retained model outputs or performance measurements. Where a contract detail
remains uncertain, say so and narrow the illustration to the supported mechanism.

At the very top of the task content and standalone illustration, before the first
visual, place one concise, high-contrast warning sentence with an official source
link. Keep it visible in mobile/no-GPU layouts and carry it into video opening
frames and captions. Example (fill with verified, entry-specific facts):

> **Symbolic illustration — the original scan is unavailable here; request the actual data through the linked dataset access page.**

Prefer a specific reason such as “access approval pending,” “matching case absent”
or “300-photon data missing,” and a specific route such as dataset page, download
command or access-request page. Do not claim an access restriction from a timeout.
Retain acquisition details below the concise sticker. Label synthetic coordinates,
labels and outputs as illustrative and keep references behind explicit reveal.

Record `illustration_basis` as `source-derived`, `symbolic` or `mixed`, along with
`source_resolution_receipt`, `actual_data_gap`, `acquisition_route` and, for any
symbolic content, `warning_text` in the ledger. A source record can document the
unresolved actual-data gap while the explainer is accepted within symbolic scope.
After authoring a supported contract and assets, move the entry to
`pending-operation-review`, clear its active `blocking_dependency`, and retain
the original reason and attempts in the dependency history. Archive its current
`dependency_resolution` object in `dependency_resolution_history` and remove the
active object so a ready or accepted entry is not still labelled needs-resolution.
Pin the resolution receipt through the existing `source_review` path/hash fields;
preserve previous source audit pointers in the resolution record. The transition
gate requires the archived resolution, basis/gap/route metadata and a valid pinned
receipt before a previously blocked row can become production-ready. It does not
require actual data recovery when symbolic scope is chosen. Prepare a fresh
production packet and perform the existing visual/export review. Explicitly check
the sticker's placement/readability and scientific faithfulness in inspection
observations; identify symbolic scope in `acceptance_scope`. Missing actual-data
recovery remains separate from completion of the approved task explanation.

The resolution receipt is concise JSON with `schema: 1`,
`kind: "explainer-source-resolution"`, matching `entry_id` and a nonempty `attempts`
list. Each attempt records `action`, `source` (URL or retained path), `outcome` and
`attempted_at`; retain supporting receipts or hashes for substantive claims. Set
the ledger's `source_resolution_receipt` and `source_review.receipt` to that file
and `source_review.receipt_sha256` to its hash. An honest unavailable outcome is
valid evidence for symbolic fallback; an invented or unperformed attempt is not.
For source-derived content, `actual_data_gap` explicitly states any remaining gap
or that the selected matching data was recovered. Reviewer inspection establishes
whether the recorded attempts and symbolic explanation are credible; a schema
check alone does not.

## Task packets and ownership

```sh
uv run --no-sync med explainer prepare ENTRY --output .local/explainers/NEW-PACKET
```

Production preparation rejects excluded, blocked and already reviewed entries.
The packet pins scope, live ledger and entry sources. Refresh it after relevant
changes. With `--regression`, preparation permits reviewed core entries solely for
tooling pilots; existing acceptance stays unchanged.

Use the repository-owned `skills/complete-explainers/SKILL.md` for orchestration.
Two Sol workers may prepare disjoint source/implementation work while the main agent
owns shared registries, catalogue bindings, integration, review and commits. Supply
each worker its entry packet, allowed paths, deliverables and stopping condition.
Workers do not accept their own work. Use an isolated checkout when ownership overlaps.

## Export and collect review evidence

Use the existing [canonical story workflow](EXPLAINERS.md), including frontend
builds and `med story batch new/run/check --decode`. Export from a stable snapshot,
use fresh destinations and preserve failed attempts. Browser commands require
approved execution outside the restricted macOS command sandbox, using disposable
profiles and the repository harness.

```sh
node scripts/review_story.mts --export=EXPORT-DIRECTORY \
  --output=FRESH-REVIEW-DIRECTORY --playback --frames=DECISIVE-FRAME-NUMBERS
```

The collector validates artifact fingerprints, timeline/captions and normal-speed
video playback, captures canonical and explicitly selected states, and writes an
offline review gallery and machine-readable report. Omit `--frames` when no extra
states are needed. Omit `--playback` for a still preview only. This never assigns
visual acceptance. Full decoding remains the batch check's responsibility.

Inspect full-size decisive images and actual playback, plus entry-specific Explorer,
mobile, reference reveal/reset and no-GPU behavior. Write observations with the exact
source snapshot, inspected artifacts, reviewer and limits. Shared-runtime changes
need broader regression checks; unchanged successful checks need not be repeated.
Before committing tooling, stage intended paths and run `make check PYTHON=python3.12`
with the project environment active on the intended staged/committed tree.

Bind the existing integrated browser matrix to its exact inputs before sign-off:

```sh
node scripts/review_explainer_browser.mts BATCH-DIRECTORY EXPLORER-HTML
```

The wrapper runs the existing disposable-browser matrix and writes
`browser-witness.json`, pinning the batch, each export, Explorer and harness before
and after execution. A previously attempted matrix is never overwritten.

## Reviewer sign-off

Create a fresh task packet after authoring changes, then write a local inspection
JSON with `schema: 1`, `entry_id`, `reviewer`, `reviewed_at`, `scope`, nonempty
`observations` and `limits`, and `rendered_mode` (`planar` or `spatial`). Record
`inspected_images` as workspace-relative path-to-SHA256 pairs. `collection` and
`browser_matrix` each contain a workspace-relative `path` and its `sha256`; the
latter names `browser-witness.json`. Its underlying matrix must cover the story,
both locales, endpoint captures and no-GPU fallback, with no page errors or remote requests.
The explicit `checks` keys are `visual`, `motion`, `explorer`, `mobile`, `no_gpu`
and `reference_boundaries`; set each true only after inspecting that surface.

```sh
uv run --no-sync med explainer review --packet PACKET-DIRECTORY \
  --batch BATCH-DIRECTORY --inspection INSPECTION.json --output FRESH-RECORD.json
```

This verifies current packet pins, collected images, export identity, completed
normal-speed playback, three seeks and full video decoding. Regression sign-off
preserves the entire ledger. Only an unblocked production packet permits `--accept`,
which updates that entry's review state and recomputes counts. An inspection is an
attributed reviewer claim; the validator checks its evidence, not medical truth.
Update the retained ledger's artifact-policy hash before staging acceptance.

## Resumption and reporting

An empty production-ready queue does not stop source-resolution work. Report ready,
needs-resolution, deferred, reviewed and outside scope separately. Report accepted
source-derived, symbolic and mixed explanations distinctly. Continue to the next
resolution entry when one external dependency is recorded, without leaving core scope.
Never restart an attempted batch in place or overwrite earlier review receipts.

Keep a compact local checkpoint containing ownership, tested source hashes, commands,
attempt paths, the last successful stage and the next action. Track only concise
source records and workflow results; generated media stays local. A regression pilot
proves the exercised tools and cases, not new task completion or throughput gains.
The [2026-09-29 pilot and handoff](EXPLAINER-PILOT.md) records the exercised cases,
verification limits and next-session starting state.
