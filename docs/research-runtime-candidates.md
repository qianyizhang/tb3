# Runtime regression screen

Retrieved 2026-09-12. Research only: no task, Docker image, oracle, verifier,
or model trial has been created or run. Nothing here is evidence of model
difficulty.

## Disposition of the first two ideas

| Idea | Primary source | Disposition |
| --- | --- | --- |
| Fixed-width binary outer-join null materialization | [DataFusion #19067](https://github.com/apache/datafusion/issues/19067) | A real stale-value/NULL defect, but it overlaps the selected Dremel/Arrow representation lane. Do not build it as a third task. |
| Duplicate-label projection filter pushdown | [DataFusion #21246](https://github.com/apache/datafusion/issues/21246) | A real optimizer defect, but a miniature Python plan engine would be a single-defect toy. Requiring a gather or pushdown trace merely to forbid disabling the optimizer would make difficulty artificial. Do not build it. |

## SQLite lead — EXISTS-to-JOIN with LIMIT/OFFSET

**Primary incident.** The official SQLite forum report
[2c43f36255a630e3](https://sqlite.org/forum/info/2c43f36255a630e3)
contains a compact wrong-result query. Two `t2` rows satisfy a correlated
`EXISTS` predicate, so an enclosing `LIMIT 2 OFFSET 3` must yield zero rows.
SQLite 3.53.0 returned one. Disabling optimization `0x40000000` returned zero,
isolating an optimizer error rather than a SQL-semantics dispute.

**Pinned lineage.** The reporter bisected the first bad canonical SQLite
check-in to `aa54d7a0ca03a4df516f25e66ff3c4801be07a7b` (2025-07-02), the merge
that relaxed the indexed-join requirement of EXISTS-to-JOIN. SQLite maintainer
Richard Hipp fixed the reported OFFSET case at canonical check-in
[1dd3c6a5e5](https://sqlite.org/src/info/2026-04-21T12:59:43.077Z),
2026-04-21 12:59:43Z. The official check-in records changes only to
`src/select.c` and `test/existsexpr.test`, which is the right compact repair
surface.

**Why this is more credible than a toy interpreter.** It is the actual SQLite
core, an existing optimizer transformation, a wrong final row count, and a
native C build rather than an invented SQL subset. A repair has to preserve
correlated `EXISTS`, LIMIT/OFFSET accounting, and the fast path when its
preconditions hold. The oracle can run SQL scripts and compare results; it
need not prescribe an internal plan shape.

**Candidate task shape, not an implementation.** Start from the pre-fix source
snapshot, expose a tiny make target for the CLI or test harness, and ask for
the observed report to be corrected without disabling the optimization
globally. The verifier should execute independently authored scripts covering:

1. the incident's correlated `EXISTS` plus LIMIT/OFFSET count;
2. OFFSET 0, no OFFSET, empty/right-empty inputs, and matching cardinalities
   above and below the limit;
3. uncorrelated EXISTS and a normal indexed EXISTS control; and
4. a plan/performance-neutral behavior check that the global EXISTS-to-JOIN
   option remains enabled, if the source exposes a stable test control.

The expected results should come from simple row-set calculations in the
verifier, or from a separately built known-good SQLite binary, never from a
source-text diff. A worked oracle must show the fix is generic and that the
controls do not rely on a special table/query name.

**Observed feasibility result.** The GitHub mirror tags `version-3.53.0` and
`version-3.53.1` were compiled natively. The report's SQL gave `2, 1` on
3.53.0 and `2, 0` on 3.53.1. Their source diff confirms two compact hunks in
the same EXISTS-to-JOIN helper: reject a parent `OFFSET`, then avoid a recursive
rewrite after attachment. A real-source probe now lives in
`probes/sqlite-exists`; its baseline fails the incident and its reference
passes six SQL-result cases.

**Honest difficulty boundary.** This is authentic but the repair is probably
direct and publicly discoverable. It is not a TB3 difficulty candidate yet.
Do not add plan-shape gates or arbitrary query cases to force a failure. One
Terra/high trajectory may establish whether it produces a substantive diagnosis;
otherwise retain it only as a runtime/verifier calibration fixture.

## Other authentic SQLite incidents, not selected

* [Outer-join NOT NULL regression](https://sqlite.org/forum/forumpost/4fc70203b61c7e12): SQLite correctly diagnosed a missed nullable flag when a
  NATURAL/USING join followed a RIGHT JOIN. This is too close to a direct flag
  fix without reviewing its source patch.
* [One-pass UPDATE with a correlated subquery](https://sqlite.org/forum/forumpost/0007d1fdb1?t=c): SQLite explains that mutation during a one-pass scan changes the later
  subquery result, and fixed it by disabling one-pass in that condition. It is
  authentic, but the stated remedy is too directly exposed for this screen.

Recommendation: run one Terra/high feasibility screen only after Docker and
separate-verifier checks. Reserve Sol unless the trajectory shows a meaningful
failure rather than an obvious source lookup or build fault.
