---
name: complete-explainers
description: Run the TB3 scoped explainer queue with source resolution, labelled symbolic fallback, bounded delegation and source-pinned review. Use for completing or resuming multiple Task Explorer entries.
metadata:
  version: "1.2.0"
---

# Complete explainers

Resolve the active workspace from `workbench.toml`. Read its
`presentation/EXPLAINER-CANDIDATES.md`, `presentation/EXPLAINER-SCOPE.json`,
`presentation/EXPLAINER-LEDGER.json` and `presentation/EXPLAINER-WORKFLOW.md`.
The scope ledger owns eligibility; the review ledger owns current status and
dependency reasons. Historical active entries and cached counts cannot select work.

## Select and prepare

Run `med explainer queue`. Follow the current user policy and ordered resolution
queue before treating missing assets as external barriers. `needs_resolution`
means actionable investigation; `ready` means production review can be prepared.
The 2026-09-29 policy authorizes source-resolution attempts and symbolic fallback
for noncommercial task interpretation. Old deferral records do not override it.
When the user explicitly postpones resolution, record the actor, source, reason
and reopening action; do not relabel deferral as completion. An empty production
queue does not stop resolution work or permit leaving core scope.

Inspect retained sources first, then attempt the official dataset/contract route;
reuse shared dataset receipts across variants. Follow the workspace workflow's
bounded effort and record actual outcomes. Not downloaded, not audited, timeout,
access approval and source mismatch are different states. Do not make public
redistribution of source assets a prerequisite for task interpretation; check terms
for the actual use.
Do not repeat a user-scope question already answered.

After a documented unresolved attempt, author a scientifically faithful symbolic
input/operation/output illustration. Put one concise warning sentence at the very
top stating why actual data is absent and linking how to acquire it. Preserve it
in mobile, fallback and exported opening views. Label symbolic values and outputs;
do not fabricate patient evidence, ground truth or model results. Narrow unsupported
contract details instead of inventing them. Record the basis, actual-data gap,
attempt receipt and acquisition route separately from explainer acceptance.
Defer only a dependency that still prevents this supported explanation, with
evidence and a reopening condition, then continue to the next core entry.

Use `med explainer prepare ENTRY --output FRESH-DIRECTORY` once the entry reaches
production review; source-resolution work starts from its queue row and sources.
Read prior audits before researching sources. Use `author-task-brief` for unresolved
contracts, `author-task-story` for canonical stories, and `video-explainer` for
established story exports. Apply only the needed workflow. Task packets and review
receipts are execution records; they do not replace the scientific source.

## Delegate and integrate

For authorized multi-entry production, use two bounded subagents when their work
can proceed independently. Default to GPT-6.1 Sol (`gpt-6.1-sol`) at medium effort;
preserve an explicit user model or effort choice. Raise effort for difficult
numerical or evaluator reasoning. Give each a compact packet, exact write
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
locations, last successful stage and next action. Follow the user's source-acquisition
scope; no model trial, runtime install or publication is implied by this workflow.

At closeout, read [Active lessons](references/feedback-ledger.md). Record only
material reusable feedback, with the invoked version and source.
