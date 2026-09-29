# Scoped explainer workflow

The [scope ledger](EXPLAINER-SCOPE.json) selects core entries and group priority.
The [review ledger](EXPLAINER-LEDGER.json) owns live status, exact dependency reasons,
reopening actions and acceptance receipts. The [completion plan](EXPLAINER-CANDIDATES.md)
owns the current user scope. Generated queues and dependency registers are projections.

## Deferred dependencies

The user requested on 2026-09-29 that dependency-blocked entries be explicitly
marked with their reasons and left for a follow-up session. Continue to the next
ready core entry. Keep deferred entries in the unfinished denominator; neither
deferral nor scope exclusion counts as completion. The original all-205 goal remains
paused and is not this workflow's selection authority.
The [dependency register](EXPLAINER-DEPENDENCIES.md) is a dated generated view;
regenerate it from the live ledger when dependency state changes.

```sh
uv run --no-sync med explainer defer-blocked --actor user \
  --source codex://threads/01a0e024-3705-7a91-9181-d237131801fa --date 2026-09-29
uv run --no-sync med explainer queue --output .local/explainers/NEW-QUEUE.json
uv run --no-sync med explainer dependencies --output .local/explainers/NEW-DEPENDENCIES.md
```

Deferral preserves original status and evidence. It records reason, next action,
actor, source and date on each blocked core row in the existing review ledger.
The command is idempotent for the same decision. It does not repair missing inputs,
resolve rights, infer answers to pending questions or launch source research.
Refresh the artifact-policy hash before staging a changed ledger.

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

An empty ready queue is a complete scheduling result with unresolved dependencies,
not completion of the explainer program. Report ready, deferred, reviewed and outside
scope separately. Reopen a dependency only after its recorded condition is met.
Never restart an attempted batch in place or overwrite earlier review receipts.

Keep a compact local checkpoint containing ownership, tested source hashes, commands,
attempt paths, the last successful stage and the next action. Track only concise
source records and workflow results; generated media stays local. A regression pilot
proves the exercised tools and cases, not new task completion or throughput gains.
The [2026-09-29 pilot and handoff](EXPLAINER-PILOT.md) records the exercised cases,
verification limits and next-session starting state.
