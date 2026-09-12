# Homology diagnostic: completed pass

The frozen `homology-basis` task has healthy matching oracle 1 / nop 0 controls
and one Terra/high result of 1. All 43 certificate cases passed. Total elapsed
time was 399.743 seconds, with 340.514 seconds of agent execution and 12.735
seconds of verifier phase. These are Docker/Harbor diagnostics, not final trials.

The [summary](../../docs/evidence/homology-trial-summary.json) links the individual
results and verifier outputs. The [freeze](../../docs/evidence/homology-pilot-freeze.json)
retains the separate runner hash and case manifest hash; all three trials share
the Harbor checksum `b50ec6509dff4764b59b179b7edbf6e0926b2bd356f4a0dfd2922c2260ae87dd`.

## What the model actually did

Terra inspected the local starter and installed SymPy interface, then wrote its
own tracked integer row/column reduction. It found a unimodular kernel basis
from A, expressed B in that basis, reduced the image there, and applied the
inverse left transformation back to the cycle basis. Its final source uses
standard-library integer and Fraction arithmetic. The two reductions preserve
the shared coordinates required by the task.

The trajectory includes an early local test shape error for an empty matrix,
an intermediate self-test timeout and unavailable optional `ps`/`git` commands.
Terra revised the algorithm to use Euclidean division and continued testing.
Those intermediate commands do not turn the completed passing diagnostic into
a model failure or an infrastructure-only attempt. The final agent completed
normally and the separate verifier returned 1 without a Harbor exception.

The observed commands inspect local files and run local Python tests. The
submitted code and complete trajectory remain local under
`runs/homology-terra-high-20260912/homology-basis__Wzt9BCY/`.

## Disposition and limits

Retire this snapshot from difficulty selection. It achieved field diversity,
a compact specification and exact acceptance of nonunique certificates, but
the conceptual crux was within Terra's demonstrated capability. Do not remove
SymPy, enlarge matrices, add unrelated topology features or shorten timeouts
to manufacture a failure. No same-snapshot failure confirmation, Sol/Opus or
adversarial trial was run.

Coverage is seven named cases and 36 seed-fixed transformed chains, at sizes
up to 8 and observed input magnitudes up to 2,880. This is finite diagnostic
coverage, not a proof that the submitted program meets every allowed input up
to magnitude 1,000,000. Final human authoring, Linux static/rubric checks and
submission trial requirements remain incomplete. The independent numerical
follow-up is a source reproduction, not another model result.
