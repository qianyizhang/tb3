---
name: author-task-brief
description: Create concise, source-backed task explanations and browsable task catalogues with explicit inputs, helper artifacts, outputs and visual reveals. Use for explaining existing tasks or drafting proposed tasks.
metadata:
  version: "1.1.0"
---

# Author a Task Brief

A Task Brief lets a reader understand the work before reading results. A Task
Explorer groups briefs and makes definitions, conditions and cases reachable.

## Find the local contract

Read repository instructions and locate an existing task-brief rulebook/template
before creating another convention. Search filenames for `task-explorer`,
`task-brief`, `RULEBOOK.md` and `brief-template.md`. Reuse the local authoring and
build commands. The repository owns its medical/domain rules and storage layout;
do not hardcode one checkout's paths into this reusable skill.

Without a local convention, use concise Markdown covering task/value, given
material, specification, expected output/evaluation, visuals, difficulty/sources.
Keep any navigation metadata small and avoid duplicating authored facts in JSON.

## Author from the actual condition

- Read the task prompt, relevant scorer and source staging when available.
  Keep unverified access boundaries and missing references explicit.
- Separate original images/data, pre-supplied helpers, callable tools and
  evaluator/reader-only references. Helpers include masks, landmarks, crops,
  hints, algorithms, code, model checkpoints and prior outputs.
- State what the assistance removes from the work and what remains. A variant
  that gives an answer through a tool is a different condition.
- Give a concrete output shape, units/coordinates when consequential, and what
  success checks establish. Explain clinical/scientific relevance without turning
  intended benefit into a demonstrated result.
- Mark proposed definitions visibly and identify unresolved scoring, reference
  or resource questions. A brief does not create permission to run a trial.

## Make the task inspectable

Start with input and supplied helpers; let the reader reveal reference answers
or actual outputs. Label those roles separately. Reuse task-specific viewers
with useful static fallbacks. Preserve source, caption, derivation and attribution.
Explain post-hoc crops or view selection; they can remove the original search
problem. A conceptual diagram explains structure, not measured difficulty.

Use one shared brief per definition and index repeated conditions/cases beneath
it. Distinguish published counts, imported IDs, authored briefs and media coverage.
Do not claim a catalogue is complete because every repository has one example.

Aim for a 60–90 second first read, then optional detail. Keep the executable task
specification and scorer separately authoritative; reader reveals must not become
solver inputs. Validate the rendered navigation and input/helper/reveal states,
and use the repository's relevant offline checks after tooling changes.

## Close out the skill invocation

The invoked version is the `metadata.version` loaded from this `SKILL.md`. Near
closeout, read only **Active lessons** in
[references/feedback-ledger.md](references/feedback-ledger.md). Append one History
entry only for material reusable feedback, recording that invoked version.
Do not log routine success or delay the requested deliverable. If the canonical
ledger is not writable or in scope, surface a compact suggested entry instead.
