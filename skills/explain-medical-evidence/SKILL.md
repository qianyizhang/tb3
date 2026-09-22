---
name: explain-medical-evidence
description: Explain medical experiment results, GT comparisons, traces, failure modes, or multi-run differences from pinned workbench evidence. Use after a task or experiment has evidence to interpret; use author-task-brief for task-only explanations.
metadata:
  version: "1.0.0"
---

# Explain Medical Evidence

Produce a concise, inspectable explanation that connects task contract, frozen
measures, actual result/reference views, consequential trace evidence and calibrated
interpretation. The `med evidence` CLI is model-free collection; you are the
explaining agent.

## Establish the evidence boundary

Read repository instructions and the owning group's guidance. Find an existing
finding before scaffolding another. Use `med evidence collect TARGET...` to inspect
record identities, task digests, conditions, reviews and available pointers. Save
a manifest only to an explicit path, then run `med evidence check` before relying
on it.

Do not launch a trial, rewrite a frozen score, expose evaluator-only material to a
solver, or treat missing raw artifacts as model failure. An evidence manifest is a
durable index, not an interpretation.

## Select the explanation mode

Read [references/modes.md](references/modes.md) for the selected mode only:

- one result or result-versus-GT;
- trace/intermediate artifacts and failure attribution;
- multi-run or multi-condition comparison;
- cross-experiment synthesis or data/reference audit.

For task-only explanations without results, use the local task-brief convention or
the `author-task-brief` skill.

## Build the explanation

- State solver-visible input, assistance, requested output, scorer and private
  reference boundary before interpreting a score.
- Put exact measures and denominators before meaning. Keep frozen evaluation
  outcomes separate from post-hoc diagnostics and anatomical interpretation.
- Inspect actual source/result/GT artifacts when available. Mark conceptual
  drawings, selected crops and unavailable references explicitly.
- Follow consequential actions and intermediate artifacts, not routine chronology.
  Separate observation, interpretation, hypothesis and unresolved alternative.
- Test failure explanations against data, GT, instruction, scorer, tools, runtime
  and agent behavior. Question GT when evidence warrants it without relabeling the
  official outcome.
- For comparisons, declare `matched`, `endpoint_only`, `diagnostic`, or
  `not_comparable` and name task/refinement/runtime confounders.
- Prefer an at-a-glance table, compact bullets and a few decisive visuals. In tb3,
  follow `docs/visual-explanations.md` and `docs/evidence-explanations.md`.

Persist substantive work as the owning group's first-class `finding` plus report,
evidence receipt and figures. Use `med evidence new` only when no suitable finding
exists. Keep `analysis_kind` accurate and allow review flags to propagate from
experiments.

## Close out the skill invocation

The invoked version is the `metadata.version` loaded from this `SKILL.md`. Near
closeout, read only **Active lessons** in
[references/feedback-ledger.md](references/feedback-ledger.md). Append one History
entry only for material reusable feedback, recording that invoked version.
Do not log routine success or delay the requested deliverable. If the canonical
ledger is not writable or in scope, surface a compact suggested entry instead.
