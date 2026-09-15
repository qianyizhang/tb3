# BR-005 — remove supplied solution ingredients and retest

Authorized by the 2026-09-15 user message, “ok, fix and retest the cases with
\"leaked info\"”, in task `01a0a0cf-3d4b-7f00-a47f-4133211cb483`.
The exact source-message ID is not exposed here. Scope is the five clear cases
in the [completed audit](../research-specification-audit-20260915.md), not its
seven directed/borderline cases. BR-004's concurrent DICOM work is separate.

## Frozen comparison plan

Original tasks remain under `probes/<id>`. New revisions live under
`probes/revisions/br005/<id>` and keep the same candidate IDs. Preserve every
original run and retirement; comparisons must name the condition and checksum.

| Order | Task | Intervention | Remaining inference | Model retest |
| --- | --- | --- | --- | --- |
| 1 | collision-vjp | Empty callable replaces the complete forward graph with two detached tensors; remove derivative diagnosis and collision formulas. | Derive and implement the stated elastic two-disk dynamics and its derivative. | Terra/high |
| 2 | extxyz-stress | Remove parser/helper and near-complete conversion; infer fixed component order and virial sign from the retained calibration pairs. | Parse records, recover exporter conventions and normalize physical tensors. | Terra/high |
| 3 | quad-face-flux | Remove geometry helpers/reference-field starter and named corrective mapping. Define the unique field through flux preservation under the bilinear map. | Derive the mapping, compute geometry and reconstruct the field. | Terra/high |
| 4 | actuator-memory | Remove the three candidate recurrences, discriminating probe and fitted-parameter starter. Retain resettable measurements and historical sweep observations. | Design probes, infer the fixed response and fit a predictor. | Sol/max, then Astra/max |
| 5 | clipper-polytree | Agent build context contains Rust source/tests/manifests/bench and license only; remove C++ reference, repository guidance and ancillary scripts. | Diagnose and repair hierarchy behavior without the supplied working port. | Terra/high |

All five keep their original grading cases, verifier code, tolerances,
public examples, installed libraries, Internet availability, CPU allocation,
separate grading environment and 1,800-second agent budget. Private geometry
and header helpers needed by the original oracle move to its solution folder;
the normal agent cannot read them from its build context.

Stress calibration retains intensive/extensive units, laboratory basis,
six-component permutation without shear scaling, and no arbitrary extra scale
factor. These make the public calibration informative without handing over
the fitted order or sign. The flux definition preserves flux on every mapped
oriented curve, not just on outer edges; the latter would be underdetermined.

These are package revisions, **not prompt-only causal ablations**. In particular,
collision now requires implementing forward dynamics, stress includes parsing
and convention calibration, and flux includes geometry. The observed comparison
will show performance with these supplied ingredients removed; it cannot
attribute any change solely to a sentence in the original prompt.

## Execution and decision rules

Prepare and inspect the complete agent-visible package. Require matching
Harbor 0.18 oracle=1 and nop=0 with no infrastructure exceptions; freeze source
hashes and archive the condition before its model run. Model runs use Harbor
0.14, Codex, one attempt and one concurrent trial, with the same model/effort
as the corresponding original. They start as fresh Docker/CLI sessions without
this author's conversation or audit. Use the existing explicit network proxy.

Process the five conditions in the table's order. Inspect each result and
worker trace before the next task. Authoring of later tasks may proceed while
an earlier run executes. A clean pass retires that revised snapshot. A zero
requires checking normal completion, verifier validity, source access and the
submitted failure; do not automatically label it a conceptual failure. This
round schedules six model attempts, with at most one repaired retry for an
infrastructure failure per configuration. No automatic difficulty escalation,
shorter reasoning budget, model-parameter sweep or final qualifying trials.

Keep all raw logs and generated reports under `runs/br005-*`. Record result
receipts, comparisons, exclusions, source-prompt matching and artifact evidence
in the final round summary and catalog. Repository checks do not certify the
benchmark's difficulty. Outcome: preparing; no model results at plan creation.

## Completion — 2026-09-15

The planned six model runs and ten controls are complete. Five model runs pass;
the revised Clipper condition has one independently reproduced genuine semantic
failure. No model retry or additional model experiment ran. See
[results and dispositions](BR-005-results.md) and the
[round receipt](../evidence/br005-round-summary.json). The frozen plan above
and every original snapshot remain intact.
