# Provenance and scope

Retrieved 2026-09-12.

The environment ships Ninja **v1.12.1**, immutable upstream commit
`2daa09ba270b0a43e1929d29b073348aa985dfaa`, under Ninja's Apache-2.0 license
(`environment/ninja-src/COPYING`).  [Ninja issue #2641](https://github.com/ninja-build/ninja/issues/2641)
reports the symptom: a depfile dependency on a dyndep-discovered output is not
rebuilt in the invocation that changes the producer.  The issue reports Ninja
1.12.1 and was fixed upstream by [commit
36c1fd98332935b08b7e7e57b9ac8ac66055c7b5](https://github.com/ninja-build/ninja/commit/36c1fd98332935b08b7e7e57b9ac8ac66055c7b5).

That commit changes only `src/graph.cc` production behavior (and adds upstream
unit coverage, which this probe does **not** copy).  Its repair visits all an
edge's inputs before evaluating `outputs_ready_`; loading one input's dyndep
can add an in-edge to another input, so readiness cannot be evaluated during
the same discovery loop.  The implementation here uses that source attribution
for the oracle but authors fresh integration graphs and verifier assertions.

Native control on 2026-09-12: the pinned build bootstrapped in about ten
seconds.  In the local graph, after changing `version.txt`, v1.12.1 ran only
`produce` and left `copy` with `one`; a build containing the upstream
production correction ran both `produce` and `copy`, produced `two`, and then
reported no work.  This is a witnessed control, not a model result or
acceptance claim.

The core fix is a small source diff but requires understanding a mutable graph
traversal across dyndep loading, depfile ingestion, order-only edges, and
incremental/no-op behavior.  This remains a feasibility probe until independent
agent trajectories establish that the task is neither trivial source lookup nor
underspecified.
