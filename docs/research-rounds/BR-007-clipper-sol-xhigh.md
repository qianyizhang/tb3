# BR-007 — Clipper topology generalization, Sol/xhigh

Authorized by the user's 2026-09-15 request to tune Clipper difficulty and test
Sol/xhigh, in task `01a0a0cf-3d4b-7f00-a47f-4133211cb483`. The exact source-message
ID is unavailable. This follows BR-005's independently confirmed Terra failure;
BR-004 and BR-006 are separate concurrent work.

## Predeclared design and diagnostic

Keep the broken historical Rust source and source-only deliverable. Retain the
BR-005 removal of the C++ reference. Increase semantic coverage of the same
horizontal-join/topology crux: original rectilinear regressions, original new
joined-edge layouts, nested holes/islands, input-order and ring-start changes,
and integer affine transforms. Compute truth with an independent elementary-cell
Boolean arrangement, then compare complete normalized contour trees. Do not
substitute source-reference agreement for geometric truth.

The agent receives a working toolchain, usable public diagnostics, existing
source and a behavior contract without a repair recipe. Keep Internet access,
two CPUs and the full 1,800-second agent allowance. Require fast separate
verification, healthy oracle/nop controls, rejection of the BR-005 submitted
partial repair and targeted incomplete controls before freezing.

Hypothesis: Sol may repair the visible tree symptom through post-processing or
a partial join fix, while leaving the underlying contour topology sensitive to
layout, nesting or input order. Look for incorrect filled-component/hole
structure in a normally submitted source artifact, not merely a failed
historical order-sensitive assertion. The author controls cover 18 layouts and
144 variants; the full repair passes, the BR-005 artifact fails 72, and isolated
registration/order regressions fail 80/72. Removing persistent scan-position
updates passes and is retained as a simplification control, not a semantic
defect. No corpus case was removed during these controls.

Generate the corpus before Sol runs. Geometry-based exclusions and authoring
corrections must be recorded before freeze; never drop a case because Sol failed
it. Run one fresh Harbor/Codex `openai/gpt-5.6-sol`, `reasoning_effort=xhigh`
diagnostic. Allow at most one repaired retry for an infrastructure-only failure.
Inspect prompt exposure, actual model context, submitted source, normal
completion and semantic witnesses. A timeout, build-environment failure or
oracle defect is not a genuine model failure. A clean pass is retained as
evidence against this revision's difficulty; do not add arbitrary restrictions
or repeatedly tune the private grader against that answer.

This is a diagnostic study, not the six standard/two adversarial qualification
series. Success for the user's objective requires a normal, independently
verified Sol miss; execution alone does not establish it. Record either outcome.

Status at plan creation: preparing; no new model trial has run.

## Frozen execution record

The [freeze](../evidence/br007-clipper-freeze.json) records the exact task,
agent-visible inventory, local archive, model and allowance. Matched Harbor
oracle/nop controls returned 1/0 with no exceptions. The
[author controls](../evidence/br007-author-controls.json) retain complete native
control counts and representation/geometry/hierarchy checker checks.

Upstream static checks ran against this unchanged snapshot: 20/22 checks pass.
Two copied diagnostic files lack canary comments and the required human-authored
submission README is absent. These are packaging/submission gaps, not observed
runtime failures. They are recorded without modifying the snapshot while Sol is
running. Static-tool and Harbor aggregate hashes use different conventions;
all 62 frozen per-file hashes and the Harbor directory digest were rechecked.

Local static manifest: `runs/static-20260915T010959943031Z/manifest.json`.

## Completion

One fresh Sol/xhigh diagnostic completed normally: 144/144 private cases pass,
with matching artifact replay. The difficulty target was not reached. No retry
or post-answer corpus change was made. See [results](BR-007-results.md) and
[round evidence](../evidence/br007-round-summary.json).
