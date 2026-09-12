# Build-system candidates: primary-source screen

Retrieved 2026-09-12. This is research only: no task, Docker image, oracle, or model trial has been run. It does not alter the frozen cache-invalidation probe.

## Sources and factual record

| Primary source | Factual record | What it supports |
| --- | --- | --- |
| [Ninja #2641: depfile dependency on dyndep output does not trigger rebuild](https://github.com/ninja-build/ninja/issues/2641) | The reporter provides a four-rule reproducer: a generated dyndep makes `other` an implicit output; a later rule’s depfile says `copy` depends on `other`; editing the producing command rebuilds `other` but initially does not rebuild `copy`. The issue was closed through #2749. | A real two-phase dependency-discovery failure: static manifest, dyndep loading, generated output, and a depfile edge disagree about when a downstream target is dirty. |
| [Ninja #2721: absolute and relative depfile paths](https://github.com/ninja-build/ninja/issues/2721) | An upstream maintainer describes generated headers as a common case where an absolute compiler depfile path and a relative manifest path do not reconcile. | This is not merely stale file content; it is a path-identity/provenance problem between a producer, compiler, and dependency database. |
| [CMake !6143: handle depfiles with absolute generated paths](https://gitlab.kitware.com/cmake/cmake/-/merge_requests/6143) | CMake maintainers describe the same failure and their remedy: custom-command outputs use relative names in the Ninja manifest while compiler depfiles can use absolute names; the change emits an additional absolute implicit output alias. | A production-grade example of the necessary invariant: one generated file must have one dependency identity even when tools report different spellings. It also makes direct-solution leakage a real risk. |
| [Ninja manual: header dependencies and depfiles](https://ninja-build.org/manual.html) | The manual explains that compilers discover header dependencies during compilation, and later changes must rebuild the dependent target; it also documents depfile cooperation. | A stable behavioral contract for a verifier; it should test incremental outcomes, not a particular manifest line. |

## Candidate A — generated-header identity bridge

**Problem shape.** A small preexisting build-manifest emitter generates a Ninja graph for an IDL-to-header step and a downstream compile/link step. The compiler writes an ordinary Make-style depfile containing an absolute path to the generated header, while the emitter registers the generator output only by its build-relative path. A changed IDL can update the header but leave the consumer stale.

**Why it is more than the cache probe.** Diagnosis crosses three mechanisms: generated-output declaration, compiler-produced dynamic metadata, and Ninja’s path identity. A plausible wrong repair changes timestamps, forces all compiles, or replaces the build with a script; each violates a stated incremental contract. The correct result has to support both absolute and relative spelling without making no-op builds rebuild.

**Bounded implementation.** Ship a compact build-generator codebase plus a local Python “compiler” that emits a depfile and deterministic object payload; use the actual `ninja` binary for scheduling. The defect belongs in the manifest emitter, not in a bespoke cache. An expert should be able to inspect `build.ninja -t graph`, the depfile, and `ninja -d explain` before repairing the emitter. A Python-slim image plus `ninja-build` should build in under two minutes; the generated project is tiny and each verifier run should take well below 30 seconds.

**Behavioral verifier.** Run the submitted emitter in two fresh project roots so an absolute-path literal cannot pass. For each root: (1) clean build and inspect the program’s payload, (2) no-op rebuild and require zero producer/compile/link records, (3) modify the IDL so the header bytes change and require producer, consumer, and link to run with a new payload, (4) modify unrelated input and require a no-op, and (5) run a variant whose compiler reports the generated header relative rather than absolute. The verifier should derive the expected payload independently and grade command records plus final artifact content, never manifest text.

**Unknowns before promotion.** CMake’s public merged fix makes a too-faithful reproduction easily searchable online. The environment therefore needs a genuine local emitter and a failure chain that differs materially from CMake’s exact patch, while retaining the same production invariant. It is a credible **prototype candidate**, not yet a TB3 candidate; only a worked oracle and witnessed Terra-high trajectories can establish difficulty or fairness.

## Candidate B — direct Ninja dyndep/depfile regression repair

**Problem shape.** Patch a pinned Ninja checkout so a depfile dependency on a dyndep-produced output is reconsidered after dynamic dependencies load; verify the #2641-style graph plus withheld graph permutations.

**Strength.** This is highly authentic, has an executable upstream reproducer, and Ninja itself compiles quickly enough for the requested build/check budgets.

**Concrete feasibility probe, 2026-09-12.** A non-submission probe now pins
Ninja v1.12.1 at `2daa09ba270b0a43e1929d29b073348aa985dfaa`, the release named in
#2641.  Native control reproduced the failure: after changing the source,
v1.12.1 ran the dynamic producer but left the depfile consumer stale; the
upstream production correction ran both in one invocation and then reached a
no-op.  The exact upstream provenance is [commit
36c1fd98332935b08b7e7e57b9ac8ac66055c7b5](https://github.com/ninja-build/ninja/commit/36c1fd98332935b08b7e7e57b9ac8ac66055c7b5), which fixes #2641 by completing
input visitation before testing readiness.  The probe's separate verifier
accepts the submitted `src` tree, overlays it onto a trusted release scaffold,
rebuilds it, and checks three fresh integration graphs as an unprivileged
user.  Its graphs and assertions were written for this probe; they do not copy
upstream unit coverage.  This is attribution, not a claim that an agent trial
has shown suitable difficulty.

**Difficulty and fairness assessment.** The production diff is small, so this
should be screened aggressively for source-lookup or one-shot pattern matching.
It still asks the solver to diagnose a mutable graph traversal across dyndep
loading, depfile ingestion, order-only edges, and no-op behavior, which is
substantively richer than the cache-digest pilot.  The instruction confines
solving to the local source/reproducer and does not name the future patch.  If
Terra/high succeeds by immediately locating a known commit or by a mechanical
one-block edit without inspecting the graph behavior, reject it rather than
adding artificial cases.

## Similarity screen against current merged TB names

The local merged-task inventory includes `batched-eval-parity`, `wal-recovery-ordering`, `mvcc-lsm-compaction`, `nextjs-performance`, `bun-sourcemap-leak`, and `cargo-flight-dispatch`. The first three are model-evaluation parity, WAL recovery, and LSM compaction, which are separate domains. Full instruction review also found `nextjs-performance` concerns WarehouseUI latency, `bun-sourcemap-leak` concerns release provenance/source maps, and `cargo-flight-dispatch` concerns flight-route physics. None overlaps a C++ build-engine's dynamic-dependency graph traversal. This is semantic clearance against the checked merged set, not a guarantee against future additions.

## Recommendation

Candidate B is now the better next screen because the release, failure, and
oracle are directly witnessed and source provenance is precise.  It remains a
feasibility probe, not an acceptance-ready Terminal-Bench task.  Run one
tightly scoped Terra/high trajectory, inspect whether its diagnosis actually
uses local graph behavior, and retain the outcome.  Advance to Sol only if the
failure or success is substantive, repeatable, and not caused by task framing,
source lookup, or infrastructure.  Do not add arbitrary graph cases or reduce
timeouts to manufacture failures.
