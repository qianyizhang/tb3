---
name: design-medical-study
description: Design a TB3 medical capability study or condition comparison from existing evidence and sources. Use for research planning and protocol drafting before execution.
metadata:
  version: "1.0.1"
---

# Design a Medical Study

Turn an unresolved question into a bounded study that can distinguish its proposed
explanations, using the workbench's existing records.

## Establish the question

Run `med list QUERY`; read repository/group guidance and relevant ideas/findings.
From the workspace root, use `docs/research-design.md`, `datasets/README.md` and
`docs/reproduce.md` for research, source and recovery contracts.

State prior support, the remaining question and what evidence would change the
decision. Preserve user decisions and identify recommendations by their actual
actor. Check source availability and reference fitness for the proposed endpoint.

## Define the comparison

Use the [condition table](references/condition-table.md) to expose consequential
differences: sampled unit, exact source/release/selection, supplied helpers and
tools, private reference, output coordinates, scoring unit and annotation coverage.
State what stays fixed, what changes and what remains confounded.

Choose controls and independent checks, runtime needs, attempt bounds and stopping
conditions proportionate to the question. Distinguish diagnostic, infrastructure,
scored-model and saved-output observations. Feasibility work need not meet benchmark
promotion gates.

## Persist and hand off

Update an idea or use `med idea`; for concrete task drafting, use `med new` and
complete its protocol/contracts. Reuse source receipts and briefs where semantics
match. Keep missing data, scoring and clinical/reference adjudication explicit.

Planning alone authorizes no acquisition, runtime installation or trial. For
already-authorized execution, follow the workspace launch rulebook and
`med run --preview`, preserving the chosen model, effort, network and tools.
A draft or preview is not a fresh trial; use the existing freeze workflow.

At closeout, read **Active lessons** in the
[feedback ledger](references/feedback-ledger.md). Record material reusable feedback
with the invoked version and source; routine success needs no entry.
