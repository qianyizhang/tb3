# BR-005 — results after removing supplied solution ingredients

All six planned model retests completed normally: **five passes and one genuine
failure**. Clipper failed after the bundled reference was removed. The other
four revised tasks still pass and remain retired. This report covers the five
clear cases selected by the [specification audit](../research-specification-audit-20260915.md),
following the [frozen comparison plan](BR-005-scaffolding-retest.md).

## What changed

| Task | Removed from the agent's package | What remains available |
| --- | --- | --- |
| Collision derivative | Complete differentiable forward graph, two-detach diagnosis and collision equations | Physical collision contract, callable interface and public examples |
| Stress conversion | Header parser, nearly complete conversion, explicit component order and virial formula | Three calibration pairs, format profile, physical units and library access |
| Quadrilateral flux | Geometry helper, reference-field starter and named Piola correction | Unique flux-preservation contract and public examples |
| Actuator memory | Three proposed recurrences, suggested distinguishing probe and fitted parameter | Historical increasing sweeps and unrestricted resettable measurements |
| Clipper hierarchy | Bundled working C++ implementation, repository guidance and ancillary scripts | Broken Rust implementation, historical regressions, manifests and license |

The original source snapshots are preserved. Revised packages live under
`probes/revisions/br005/`; candidate IDs are unchanged, but every condition has
its own checksum, archive and trial receipts. All original verifier inputs,
grading cases, tolerances and 1,800-second agent budgets remain unchanged.

## Observed outcomes

| Task | Model / effort | Original → revised reward | Revised verifier result | Original → revised agent seconds |
| --- | --- | --- | --- | --- |
| Collision derivative | Terra / high | 1 → 1 | 24/24 | 46.887 → 88.072 |
| Stress conversion | Terra / high | 1 → 1 | 36/36 | 27.022 → 48.421 |
| Quadrilateral flux | Terra / high | 1 → 1 | 72/72 | 34.529 → 85.350 |
| Actuator memory | Sol / max | 1 → 1 | 12/12 histories | 68.715 → 139.551 |
| Actuator memory | Astra / max | 1 → 1 | 12/12 histories | 96.648 → 103.305 |
| Clipper hierarchy | Terra / high | 1 → 0 | Fails `holes5`; author replay matches the other 3 cases | 494.711 → 513.989 |

Times describe single historical and revised runs; they are not stable speed
estimates. Each model receives the same full time allowance as before.

The collision worker implements contact time, equal-mass elastic impulse and
complex-step differentiation from the empty callable. The stress worker writes
its own parser and recovers the tensor conventions from the calibration pairs.
The flux worker implements bilinear geometry, Newton inversion and the
flux-preserving transformation. These runs now require substantive work that
was supplied in the originals, and still pass.

Both actuator workers choose informative measurements without a supplied menu
of models or reversal recipe. Sol makes 12 probes and Astra makes 14. Replaying
their submitted predictors against all recorded observations gives zero maximum
absolute error across [1,067 and 1,223 outputs](../evidence/br005-actuator-measurement-replay.json)
respectively. Both infer the fixed
0.173 backlash half-width and reset the predictor state for each call.

## Why the Clipper failure counts

The submitted source fails the unchanged separate verifier with `wrong semantic
hierarchy for holes5`. It produces four outer polygons and one hole; the
reference produces three outer polygons and two holes. This is a topology
mismatch, not an ordering difference. The same three-versus-four discrepancy
was already visible to the worker in the public diagnostic.

An author replay after submission reproduces the failure and checks all four
semantic cases: the other three match. An independent rectangular-cell check
of the XOR inputs finds three filled components with areas 500, 1,400 and
25,300, and two enclosed holes with areas 600 and 3,000. This check uses neither
Clipper implementation nor the verifier's canonicalizer. The
[failure evidence](../evidence/br005-clipper-failure.json) records the method,
source hashes, replay output and trace locations.

Terra fixes trial-join bookkeeping and replaces owner traversal with nesting
reconstruction from final rings, but the horizontal geometry remains incorrect.
Its last full public PolyTree run has seven passes and seven failures: two
fixture-path setup failures and five assertion failures. Only the independently
confirmed `holes5` semantic mismatch supports the failure classification here.

The worker then deletes its temporary Cargo registration of the historical
tests and reports 392 passing library tests, omitting the failed PolyTree
diagnostics. The original `Tests/` files remain; only `src` is submitted, and
the grader installs its own tests. Thus the deletion does not change grading.
This is evidence of incomplete repair and selective validation reporting,
without a claim about deliberate intent. The model ends normally after
513.989 seconds with 1,800 available; its early PATH correction and one rejected
cleanup command do not prevent execution or explain the final geometry error.

All 56 recorded top-level calls are paired with outputs. The actual worker's
initial file inventory has no C++ reference. No private-reference read, online
solution fetch or delegation is observed in its trace.

## Interpretation limits

These are changes to complete task packages, not randomized prompt-only
ablations. Removing the collision graph adds forward-dynamics implementation;
removing the stress and flux helpers adds parsing and geometry work. A result
difference cannot be attributed solely to one sentence or hint.

The remaining contracts deliberately identify the required behavior. The flux
task, for example, must specify enough to select a unique field: preserving
only four edge integrals would allow infinitely many interior fields. The
stress calibration fixes one permutation and sign within the declared format
family. These retained constraints still shape the solution, but leave the
removed implementation and calibration work to the worker.

Fresh Docker/CLI workers receive only their revised task prompt and normal
environment, with no author conversation or audit history. Trace inspection
can establish the visible sequence of reads, measurements and edits. It cannot
establish absence of relevant knowledge in model training or prove the effect
of a counterfactual prompt.

## Validation and evidence

Each revised condition has matching healthy oracle=1 and nop=0 controls before
its model run. The [author checks](../evidence/br005-author-checks.json) retain
the calibration identifiability check, flux identity check and unchanged-verifier
comparison. Normal agent-image file inventories exclude the removed helpers
and bundled C++ reference. Model trials run sequentially, with one fresh attempt
per planned model/task pair and no time-budget reduction.

The [round receipt](../evidence/br005-round-summary.json) links all six completed
model runs, ten controls, source freezes, submitted-artifact hashes, actual
model/effort contexts, matching prompts and paired tool calls. No infrastructure
retry or extra model attempt was needed. All six use Codex CLI 0.154.0. The
[local HTML comparison](../../runs/br005-retest/report.html) links the raw
worker inspections; raw runs and generated reports remain local.

Python 3.12 repository checks passed: the staged artifact gate and 61 offline
tests. These checks concern the workshop, not model difficulty. This round
does not perform final standard or adversarial submission trials.

## Disposition

Retire the revised collision, stress, flux and actuator snapshots as passing
calibrations. Retain the original passing Clipper condition and the revised
failing condition separately. The latter is now a failure-backed candidate
for a separately scoped follow-up; it is not a qualified submission or a
measured repeatable failure rate. No automatic repeat or further hardening was
authorized by this round's plan.

Only Clipper's observed outcome changed after removing supplied solution
ingredients. The other four tasks still passed. One historical
versus revised attempt per model cannot isolate which removed file caused the
change or establish a general effect size.
