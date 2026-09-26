---
name: explain-medical-evidence
description: Explain medical experiment results, GT comparisons, traces, failure modes, or multi-run differences from pinned workbench evidence. Use after a task or experiment has evidence to interpret; use author-task-brief for task-only explanations.
metadata:
  version: "1.1.1"
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

Read the relevant sections of [references/modes.md](references/modes.md); combine
modes when the request spans them. The shared requirements below apply to every mode:

- one result or result-versus-GT;
- trace/intermediate artifacts and failure attribution;
- multi-run or multi-condition comparison;
- cross-experiment synthesis or data/reference audit.

For task-only explanations without results, use the local task-brief convention or
the `author-task-brief` skill.

## Check task and reference fitness

Every score interpretation needs a proportional check of solver-visible context,
instruction/scorer alignment and GT fitness. Use the
[shared fitness checks](references/modes.md#task-context-and-reference-fitness),
reusing an applicable pinned audit when available. Treat missing context, unclear
instructions and reference defects as live alternatives to an agent limitation.
Record evidence for and against consequential alternatives and what remains
unknown. Score disagreement alone establishes neither model failure nor bad GT.

## Interpret, then persist

- State solver-visible input, assistance, requested output, scorer and private
  reference boundary before interpreting a score.
- Put exact measures and denominators before meaning. Keep frozen evaluation
  outcomes separate from post-hoc diagnostics and anatomical interpretation.
- Inspect actual source/result/GT and consequential intermediate artifacts. For
  claims about appearance, spatial coverage or visual errors, open the relevant
  images at useful scale; paths, crop geometry and generated figures alone do not
  establish visual inspection. Reuse a previously inspected view only when it
  supports the current claim. Record unavailable evidence and narrow the claim.
- Follow consequential actions and intermediate artifacts, not routine chronology.
  Separate observation, interpretation, hypothesis and unresolved alternative.
- Locate the failed stage separately from its possible cause: task/context,
  reference/scorer, tool/runtime or agent behavior. Test alternatives against the
  full available evidence; do not turn an unresolved dispute into a corrected score.
- For comparisons, declare `matched`, `endpoint_only`, `diagnostic`, or
  `not_comparable` and name task/refinement/runtime confounders.
- Prefer an at-a-glance table, compact bullets and decisive source-derived views.
  Use a small flowgraph for method branches/comparisons and pseudocode for a
  consequential calculation. Short phrases are welcome; avoid paragraphs inside
  table cells. Choose the forms that explain the result, without a figure quota.
- Put shared caveats once and specific limits beside the affected claim. Keep
  detailed provenance/reproduction linked. Mark conceptual drawings, selected
  crops and private-reference reveals explicitly. In tb3, follow
  `docs/visual-explanations.md` and `docs/evidence-explanations.md`.

Persist substantive work as the owning group's first-class `finding` plus report,
evidence receipt and figures. Use `med evidence new` only when no suitable finding
exists. Keep `analysis_kind` accurate and allow review flags to propagate from
experiments.

## Check the explanation

Before closeout, check that each requested task/condition has a method and a
supported interpretation or explicit unresolved status. Can the reader follow
each material attribution to a specific source location and artifact (trace
step/line when applicable)? Have you inspected
the relevant visual evidence and shown the decisive views with readable legends,
coordinates and derivation? Are context, specification and GT alternatives
addressed with evidence or explicit gaps? Remove repetition and unsupported
efficiency claims.
A valid manifest or passing repository checks do not establish these qualities.

## Close out the skill invocation

The invoked version is the `metadata.version` loaded from this `SKILL.md`. Near
closeout, read only **Active lessons** in
[references/feedback-ledger.md](references/feedback-ledger.md). Append one History
entry only for material reusable feedback, recording that invoked version.
Do not log routine success or delay the requested deliverable. If the canonical
ledger is not writable or in scope, surface a compact suggested entry instead.

When maintaining this skill, use the
[behavioral review cases](references/behavioral-cases.md) to check that instruction
changes preserve inspection and attribution. They are not an automatic gate on
ordinary explanation requests.
