# Integral homology certificate probe

This is a non-security, short-horizon constructive algebra task. One small
module consumes two matrices and returns four certificate fields. It is an
original chain-complex extraction motivated by Hatcher's homology construction,
not a reproduced upstream defect or a final TB3 submission.

The oracle uses SymPy 1.14.0 transformation matrices twice. The verifier uses
only exact standard-library arithmetic: determinant, rational rank, and matrix
identities. It does not import the oracle, compare an arbitrary basis with the
oracle's basis, or grade internal algorithm choices. SymPy is installed for the
agent too; avoiding a library is not part of the task.

The proof of sufficiency is short. Unimodularity of C makes its first z columns
a saturated direct summand. Their images under A vanish, and the remaining
images are rationally independent, hence they span the whole integer kernel.
Unimodularity of W preserves exactly the integer image of B. The boundary
identity gives its generators in that same kernel basis. Positive divisibility
factors then describe the quotient, including unit factors and its free part.

Seven named fixtures cover zero maps, injective A, unit boundaries, primitive
kernel, nondividing diagonal inputs and dependent columns. Thirty-six seed-fixed
cases start from valid diagonal chain complexes and change all three integral
bases. Their dimensions, input bounds and chain identity are asserted before
use. The generated cases are computed before any model trial and not changed
in response to a model output. Hidden values contain no hidden semantics.

Submitted code runs as tbrunner against a root-owned read-only copy. The verifier
and reward directory are root-only. Only the deliverable directory is
transferred. This is ordinary verifier isolation, not a security task or an
adversarial qualification claim. Final static/rubric/human-authoring and official
standard/adversarial gates are not claimed.

Controls, freeze, elapsed times and diagnostic disposition are recorded by the
owning short-horizon screen. Do not promote based on source plausibility alone.
