---
name: complete-explainers
description: Run the TB3 scoped explainer queue with explicit dependency deferral, bounded delegation and source-pinned review. Use for completing or resuming multiple Task Explorer entries.
metadata:
  version: "1.0.0"
---

# Complete explainers

Resolve the active workspace from `workbench.toml`. Read its
`presentation/EXPLAINER-CANDIDATES.md`, `presentation/EXPLAINER-SCOPE.json`,
`presentation/EXPLAINER-LEDGER.json` and `presentation/EXPLAINER-WORKFLOW.md`.
The scope ledger owns eligibility; the review ledger owns current status and
dependency reasons. Historical active entries and cached counts cannot select work.

## Select and prepare

Run `med explainer queue`. Continue through ready entries in its order. When the
user defers dependency resolution, use `med explainer defer-blocked` with the actual
actor, source and date; keep every reason and reopening action in the review ledger.
Do not ask the same pending question again or relabel deferred rows as complete.
An empty ready queue is an explicit result, not permission to leave core scope.

Use `med explainer prepare ENTRY --output FRESH-DIRECTORY` for the task packet.
Read prior audits before researching sources. Use `author-task-brief` for unresolved
contracts, `author-task-story` for canonical stories, and `video-explainer` for
established story exports. Apply only the needed workflow. Task packets and review
receipts are execution records; they do not replace the scientific source.

## Delegate and integrate

For authorized multi-entry production, use two bounded subagents when their work
can proceed independently. Start with GPT-6 Sol at medium effort; raise effort for
difficult numerical or evaluator reasoning. Give each a compact packet, exact write
ownership, evidence requirements and a stopping condition. No recursive delegation.
Workers must preserve concurrent edits and return files, checks, findings and gaps.

The main agent owns shared registries, generated contracts, catalogue bindings,
ledger updates, integration and acceptance. Parallel workers own disjoint entry
files or isolated checkouts. Keep one browser/render job initially. Finalize copy,
assets and shared code before freezing the export snapshot; no source edits during
rendering. Integrate and accept one entry at a time.

## Verify and hand off

Use the workspace workflow's existing batch exporter and reusable review collector.
Review actual decisive states, reference reveals, narrow layouts and motion. The
collector validates evidence and leaves visual review pending. Record scoped reviewer
observations separately; never derive acceptance from a worker's success summary.

Regression pilots use `prepare --regression` on reviewed core entries, preserve their
original receipts and cannot increment completion. Keep blocked entries unfinished.
Before committing tooling, stage only owned paths and run the repository gate on
the intended staged snapshot, isolated from unrelated work when necessary.

Hand off the queue snapshot, owned dirty paths, tested commit/snapshot, receipt
locations, last successful stage and next action. No model trial, runtime install,
source acquisition or publication is implied by this workflow.

At closeout, read [Active lessons](references/feedback-ledger.md). Record only
material reusable feedback, with the invoked version and source.
