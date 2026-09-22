# Explanation modes

Read only the section matching the request. These are decision prompts, not fixed
report-length requirements.

## Result or result versus GT

Lead with task/condition and the smallest sufficient score table. Explain each main
metric's object, denominator, direction and blind spot. Pair aggregate numbers with
one representative and one failure-oriented source view when available. Distinguish
official GT comparison from post-hoc anatomical judgment.

## Trace and failure attribution

Start from the final output and work backward to consequential decisions. For each
claimed mechanism, link an observable trace/artifact and state alternatives.

| Layer | Examples |
| --- | --- |
| Data | missing coverage, orientation, acquisition mismatch |
| Reference | ambiguity, annotation protocol, incomplete class scope |
| Instruction/scorer | underspecified identity, wrong incentive, hidden convention |
| Tools/runtime | unavailable dependency, transport failure, lossy conversion |
| Agent | search omission, recognition error, rejected correct candidate, bad transform |

Do not infer cognition from the final score alone. A localized rejected candidate
supports a different claim from a region never inspected.

## Multi-run comparison

Create a condition matrix before comparing outcomes: task/reference digest,
solver-visible inputs, tools, model/effort, runtime, scorer and execution status.
Declare comparability. Use deltas only for shared endpoints; keep nonshared
diagnostics in separate columns. Do not turn one run per condition into a causal
model or effort ranking.

## Synthesis or audit

Preserve each experiment's endpoint and review status. Group compatible evidence;
do not average unlike tasks. For data/GT audits, distinguish official reference,
independent source evidence, plausible discrepancy and adjudicated correction.
End with what can be concluded now and the observation that would change it.
