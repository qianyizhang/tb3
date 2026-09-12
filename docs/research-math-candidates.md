# Mathematical and numerical candidates (screen only)

Research date: 2026-09-12. These are primary-source leads, not authored
probes or model trials. They deliberately exclude parser, binary-format,
infrastructure, and security work. Each needs a vulnerable-baseline and build
time witness before promotion.

## 1. SoPlex exact LP hot-start after a row-range change

**Best optimization candidate.** [SoPlex issue #38](https://github.com/scipopt/soplex/issues/38)
(2024-04-16, open) gives a 2-variable *exact rational* LP and a three-solve
reproducer. The first solve has optimum 1; enabling `x0 + x1 <= 0` changes it
to 0; disabling that row must restore 1 but instead retains 0 unless
`clearBasis()` is called. This is a real parametric-LP workflow: repeatedly
enabling/disabling constraints while retaining a hot basis is central to
planning and decomposition applications.

* SoPlex's [official README](https://github.com/scipopt/soplex) identifies it
  as a revised-simplex LP solver with hot starting and exact rational support;
  it is SCIP's standard LP solver. The issue's supplied C++ program checks
  `OPTIMAL`, rational objective, primal, and dual values with zero tolerances.
* Package a source snapshot known to reproduce #38 plus that driver. The
  verifier should rebuild the submitted library, run the cycle repeatedly with
  several row ranges and objective signs, and independently enumerate the
  intersection vertices of these 2D rational half-spaces. Verify objective,
  primal feasibility, and that the post-mutation result equals a fresh solver
  built from the same model. No basis reset, patch location, or algorithm
  switch should be mandated.
* This is difficult for the right reason: model mutation, the rational LP
  mirror, cached factorization/basis validity, and post-solve solution
  synchronization must agree. Returning a correct objective with a stale
  primal/dual pair is still wrong. The tiny exact oracle avoids accepting an
  arbitrary floating tolerance workaround.
* Risk: this is a mature C++ project rather than a tiny library. Screen a
  minimal CMake build and the exact driver first; the calculation itself is
  milliseconds, but the source build may exceed the desired cold-start budget.

## 2. SUNDIALS KINSOL: reused Anderson-accelerated fixed-point solve

**Best compact scientific-computing candidate.** SUNDIALS fixed a real
state-reuse regression in commit
[`49763f35`](https://github.com/LLNL/sundials/commit/49763f35da7bacd3a384b12ec46feb1f83422807)
(2025-09-17), whose vulnerable parent is
[`5f5a8c3f`](https://github.com/LLNL/sundials/tree/5f5a8c3facdd413e54e02361afc47a2032091175).
The official [v7.8.0 release](https://github.com/LLNL/sundials/releases/tag/v7.8.0)
records that an Anderson acceleration depth from one `KINSol` call was not
reinitialized on the next call using the same solver instance.

* The upstream repair adds `kin_test_reuse_fp.c`: solve the scalar fixed point
  `x = 0.5x^2 + 0.25` twice from `0.1`. The attracting exact root is
  `(2 - sqrt(2))/2`; both solves must return the same root, nonlinear-iteration
  count, and function-evaluation count, for Anderson depth 0 and 1.
* Package only the KINSOL and serial-vector build configuration plus a trusted
  driver derived from that maintained test. Verify residual, root tolerance,
  iteration/evaluation equality, a fresh-instance equivalence control, and a
  different initial guess converging to the same attracting root. This has a
  small independent analytic reference and seconds-long execution.
* The reasoning is lifecycle-sensitive: options set before the first call,
  adaptive/current acceleration depth, history vectors, and counters must reset
  at the correct boundary without losing configured maximum depth. A solver can
  still converge while violating the deterministic reuse contract, so numeric
  output alone is insufficient.
* Risk: the upstream fix is only a reset after the correct state boundary is
  found, so this may be too direct for the hard lane. It is a good calibration
  probe only after measuring a minimal SUNDIALS build.

## 3. SUNDIALS MRIStep MERK unordered-stage forcing

**Most algorithmically rich, but needs a deterministic fixture first.** Commit
[`fab78f3a`](https://github.com/LLNL/sundials/commit/fab78f3a168801d99c929ea8b189b9b07021c863)
(2025-07-07; vulnerable parent
[`6b16f530`](https://github.com/LLNL/sundials/tree/6b16f5300686db39a7032355506155b15f85783f))
fixes MERK43/MERK54 multirate integration. Their stage groups are not ordered
by stage index, so forcing construction included slow-stage RHS vectors that
had not yet been evaluated. The official commit explains why this is normally
masked by zero coefficients but becomes erroneous with `inf`/`nan` state.

* A viable task would use the published MERK43 table and a small two-rate ODE
  with a closed-form solution, then instrument the slow RHS callback to record
  every stage value consumed by forcing. The verifier must require finite
  numerical state, correct final error against the analytic solution, and no
  access to a stage before its callback ran. Repeat for MERK54 and an ordered
  table control.
* The hard invariant is mathematical dataflow, not a prescribed source patch:
  forcing may use only already-computed lower-triangular stages even when the
  table's group ordering is temporal rather than ordinal. It ties method-table
  interpretation, stage scheduling, and vector arithmetic together.
* Risk: upstream did not add a focused reproducer and the bad path depends on
  undefined/not-finite stage contents. Do not author this until a clean,
  public-API fixture deterministically fails on the vulnerable tree; otherwise
  it would manufacture a hidden requirement.

## Disposition

Start with **SoPlex #38** if its minimal build fits the time envelope: it is
the only lead with a tiny exact optimization oracle and an authentic stale
hot-start failure. KINSOL is the low-cost numerical fallback. MERK is a
research lead, not yet a fair benchmark task.
