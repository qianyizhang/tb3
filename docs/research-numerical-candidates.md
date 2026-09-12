# Numerical correctness candidates — source screen

Retrieved 2026-09-12. Two new leads beyond the existing
[SoPlex/SUNDIALS screen](research-math-candidates.md) and Clipper2 probe.
Only upstream reports, patches, and mathematical references were inspected:
**no local reproduction, build, control, or model trial was performed**.

## 1. SciPy barycentric interpolation: stable weights and incremental updates

**Worth a bounded reference check; not ready to package.**
[PR #14255](https://github.com/scipy/scipy/pull/14255) reports interpolation
failure beyond roughly 800 nodes, caused by underflow/overflow while forming
barycentric weights. Its added test uses 801 Chebyshev nodes and compares
normalized weights with their analytical values; the old implementation emits
a divide-by-zero warning. The patch combines interval scaling and permuted
factor multiplication. Its test comments report that scaling alone still fails
at degree 1097; these are upstream observations, not local measurements.

- Exact patch parent:
  [`bcea20c65ef728dbfd4297dcd99a65a621404992`](https://github.com/scipy/scipy/tree/bcea20c65ef728dbfd4297dcd99a65a621404992).
  Patch:
  [`4f11f1ea84a16ef220f51c0237f2bef92c418e4c`](https://github.com/scipy/scipy/commit/4f11f1ea84a16ef220f51c0237f2bef92c418e4c),
  merged through
  [`6caa337fdc93159a49d8ad80a0a92d0cded7cb23`](https://github.com/scipy/scipy/commit/6caa337fdc93159a49d8ad80a0a92d0cded7cb23)
  on 2021-07-16.
- Independent mathematical oracle: Berrut and Trefethen's
  [barycentric interpolation paper](https://people.maths.ox.ac.uk/trefethen/barycentric.pdf),
  especially equations 3.2 and 4.2, the Chebyshev weights, and the stability
  discussion on page 510. A common weight factor cancels, so raw weight
  equality would be an invalid grading requirement. Candidate checks could use
  finite interpolation values for known polynomials, affine interval changes,
  reordered nodes, and constructor-versus-incremental equivalence. Freeze
  random seeds and input sizes before any trial; accept alternative stable
  algorithms.
- **Reference concern from static algebra:** the
  [patched constructor and `add_xi`](https://github.com/scipy/scipy/blob/4f11f1ea84a16ef220f51c0237f2bef92c418e4c/scipy/interpolate/polyint.py)
  use inconsistent difference signs. Starting with nodes `[0,1]` and appending
  `[2]` appears to produce relative weights `[-1,2,1]`, whereas the polynomial
  formula requires `[1,-2,1]` up to a common factor. This has not been executed.
  Check it before accepting that commit as a complete oracle. Upstream also
  documents a separate [incremental-update stability limitation](https://github.com/scipy/scipy/issues/19373).
- **Setup estimate:** the changed implementation is a Python module importing
  NumPy and SciPy helpers. A compatible wheel-backed environment could avoid
  compiling SciPy; identifying and testing that combination remains work.
  Budget minutes for setup and seconds for approximately 1,100-node checks,
  provisionally. Do not claim a small source build has been demonstrated.

## 2. ForwardDiff: nested derivatives of a three-argument norm

**Compact scientific fallback with an unmerged reference.**
[Issue #834](https://github.com/JuliaDiff/ForwardDiff.jl/issues/834) supplies
`inner(x) = derivative(y -> hypot(x,y,1.0), 2.0)`: differentiating `inner` at
`x=3` returns `0.0`, but the analytical mixed derivative is
`-6 / 14^(3/2) ≈ -0.11454053224818188`. The implementation strips independent
dual-number tags and combines unrelated partial derivatives. Ordinary
single-tag gradient tests miss this. Retaining the stable norm evaluation also
matters: squaring inputs near `1e200` would overflow.

- Baseline:
  [`b74280951361c4bc1b51ef1726f1cd8d9eb39ee0`](https://github.com/JuliaDiff/ForwardDiff.jl/tree/b74280951361c4bc1b51ef1726f1cd8d9eb39ee0).
  Proposed fix:
  [`232d36d52e1ebed7b13aa87b2c5c4dd529c62a99`](https://github.com/JuliaDiff/ForwardDiff.jl/commit/232d36d52e1ebed7b13aa87b2c5c4dd529c62a99),
  in [PR #835](https://github.com/JuliaDiff/ForwardDiff.jl/pull/835), still open
  at retrieval. Its tests cover argument permutations, nested tags, and large
  inputs. Upstream reports a passing suite on Julia 1.12.6; no local witness.
- A fair numerical verifier could compare mixed derivatives with closed-form
  derivatives of `sqrt(x²+y²+z²)` at moderate nonzero points, then separately
  check stable first derivatives at large magnitudes. Cover each argument
  position and independent nesting, while retaining ordinary gradients.
  Do not require non-Type tags or a chosen derivative at the origin: the issue
  explicitly retracts the former complaint and excludes the latter.
- **Setup estimate:** the baseline's
  [Project.toml](https://github.com/JuliaDiff/ForwardDiff.jl/blob/b74280951361c4bc1b51ef1726f1cd8d9eb39ee0/Project.toml)
  permits Julia 1.10+ and has package dependencies including SpecialFunctions.
  Expect minutes for runtime/dependency provisioning and precompilation, then
  short numerical checks. Neither time nor artifact availability was measured.
- **Difficulty/provenance limitation:** the proposed commit credits Claude
  Opus 5 as a coauthor. That is not an independent benchmark trial, but makes
  this a weak basis for predicting a hard Opus failure. Keep it a calibration
  or fallback lead until the reference and intended difficulty are assessed.

## Local follow-up: SciPy numerical blocks only

On 2026-09-12 the incremental-sign hypothesis above was **confirmed within a
limited local check**, superseding its earlier "not executed" status. Existing
Python 3.12.13 / NumPy 2.5.3 were used; SciPy was absent. The harness executed
unchanged AST statements from the two downloaded historical methods, supplying
float64 nodes directly. It omitted historical input normalization, `yi`/axis
validation, and the public evaluation wrapper. No dependencies were installed.

| Check | Historical parent | Published patch |
| --- | --- | --- |
| Start `[0,1]`, append `[2]`: weights normalized by final weight | `[1,-2,1]` | `[-1,2,1]` |
| Independent barycentric evaluation of `y=x` at `x=0.5` after append | `0.5000000000000001` | `0.7999999999999999` |
| Fresh constructor at `[0,1,2]`, same evaluation | `0.5000000000000001` | `0.5000000000000001` |
| Chebyshev degree 800, normalized-weight maximum absolute error | `9.24e-4`, all 801 finite, no warning | `1.03e-11`, all 801 finite |
| Chebyshev degree 1097, seed 0 | 0/1098 finite weights; reciprocal warnings | 1098/1098 finite; maximum error `4.29e-12` |

The degree-800 local behavior differs from the upstream warning report; retain
the numeric error and environment instead of assuming identical diagnostics.
Constructor blocks took approximately 3–5 ms after imports. These are measured
kernel times, **not** SciPy build or end-to-end test times.

[Raw results](../runs/research-numerical/scipy-barycentric/results.json),
[exact-source provenance](../runs/research-numerical/scipy-barycentric/provenance.json),
and the [reproduction/limitations record](../runs/research-numerical/scipy-barycentric/README.md)
are local scratch evidence. The lead now has a witnessed numerical-block
failure and an incomplete upstream reference. It still needs a compatible
full-package check and a corrected reference before any task/model trial.

Durable copies of the limited local check are retained in
[results](evidence/barycentric-reference-check.json) and
[source provenance](evidence/barycentric-source-provenance.json). The exact
source files and execution harness remain in the local `runs/` research folder.
