# F018 contract v3, with and without the F008 annotated example

Completed on 2026-09-22 local time: both authorized attempts and terminal reviews
are finished. See the [final finding](../../findings/dental-f018-contract-v3-comparison.md)
and its local report for metrics, methods and native-coordinate figures. No further
inference is queued. The protocol below retains the fixed design and historical
operation procedure; completion does not authorize another execution.

User authorization, 2026-09-22: revise the instructions using best judgment to be
fair without leaking target answers; retest F18 with Astra-medium, with F08 and
without it; babysit both. Source task:
codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad.
This new authorization does not reopen any completed v1/v2 attempt.

## Fixed design

| Experiment | Target | Extra example |
| --- | --- | --- |
| dental-f018-contract-v3-astra-medium | Retained F_018 CT, original paired GT private | None |
| dental-f018-reference-v3-astra-medium | Identical target bytes | Original F_008 CT and mask |

One fresh `openai/gpt-6-astra` / `medium` inference per condition, in the table's
order. 7200 agent seconds maximum per condition, 4 CPUs, no GPU, existing unchanged
Codex/scientific runtime, no extra model/tool/weights. Preserve the prior nominal
12 GiB container ceiling; the shared Docker VM has less aggregate physical memory,
so serialize the runs and distinguish resource failure from segmentation quality.
No automatic inference retry, continuation or extension. A poor first score does
not cancel the second condition. No feedback between conditions.

Common [solver instruction](instruction.md) is identical, apart from the final
example-availability paragraph. F008 is the previously reviewed apparently
uncomplicated example; the [prior source review](../dental-reference-ablation/README.md)
retains its limits. No new example is selected to fit F018's GT. The unchanged
original target pair comes from the first F018 package, preserving its paired
viewer-source geometry rather than mixing it with an archive header variant.
Preparation records exact file hashes and strips example free-text header fields.
The target's corresponding header fields were already empty.

## Fairness and leakage decisions — assistant implementation

The user authorized operational decisions, so the non-dispatchable general draft
is converted into a concrete convention table here. These choices are explicit
and reusable; they are not claims to have recovered unpublished annotator intent.

- Native RPI semantic directions, array-order examples, sparse dictionary and FDI
  identities are explicit. Output remains on the original grid; physical clinical
  laterality remains unadjudicated.
- Pulp is an anatomical compartment, including supported occupied portions rather
  than viable-tissue diagnosis; unsupported obliterated space is not invented.
  This general choice follows the prior documentation/F002 audit, not an inspection
  of F018's error locations or reference contents during prompt authoring.
- Canal lumen/extent/gaps, mixed restoration ownership, sinus contents, jawbone
  compartments, unlabeled materials and uncertain partial-volume boundaries now
  have explicit operational rules. Where original GT differs, preserve and report
  disagreement rather than declaring an automatic clinical error.
- Keep original GT and the v2 numeric metrics. Only evaluator contract metadata
  and interpretive warning change. Report all class groups; do not selectively
  ignore difficult target voxels, relabel GT, tune thresholds or optimize the prompt
  using candidate solver scores. No scalar clinical success criterion is claimed.
- Both solver packets omit dataset/case identity, target label inventory/counts,
  prior target findings, scores, paths, source programs, intensity cutoffs, anatomy
  landmarks and previous methods. Source identities stay in author records.
  Both fresh solvers have no parent chat or previous solver workspace.
- The author has seen earlier F018 results. This is an explicitly requested repeat
  on a development case, not an untouched held-out validation claim. Cross-run
  differences remain exploratory, with one draw per condition.

The [source audit](../../findings/dental-dataset-contract-audit.md) remains the
authority for which publisher rules are documented and which are unresolved.
An operational instruction is not proof that the frozen original GT obeys it.

## Preparation, controls and execution

Use the fresh scripts in this directory only. They are adapted from the retained
v2 operators; never execute a historical authoring module to inspect metadata.
Local packet: `.local/dental-f018-contract-v3-20260922/HANDOFF.md` and `queue.json`.

1. Create fresh native experiments with `med new`, then prepare fresh local tasks.
2. Audit equal target/GT/dictionary/common instruction/scorer bytes; check only the
   intended example differs. Run synthetic exact, empty, identity-swap, pulp-merge,
   invalid-grid/label and missing-output controls. Review the prompt for leakage.
3. Build offline using pinned existing runtime
   `sha256:3de5f01c3d98a0ed47c9c6ac2ef202807e2761e0ece826d0b514c994f033f107`.
   Pin new solver and private evaluator images. No runtime installation.
4. Run both isolation preflights and native oracle=1/nop=0 lifecycle controls.
   Require BOTH conditions' controls before first inference. Retain every failure.
5. Check account usage above the inherited 20% reserve, shared capacity and task
   fingerprints, mark the first condition ready, then actually run its launcher.
6. Verify real model commands, intended pinned image, one internal network,
   log-only mounts and retained model-transport log. No repo/socket/GT/evaluator
   access. No feedback or method coaching.
7. At each terminal boundary, replay the frozen scorer, audit saved evidence and
   access, distinguish failures from segmentation shortfalls, then launch the next
   authorized condition if resources and invariants permit.

The launcher owns `operator-state.json`; the monitor owns the queue. One dispatcher
per batch, persistent once marker, no duplicate launch. On user stop or reserve
exhaustion, persist `no_further_dispatch` first, stop only verified owned processes,
retain partial outputs, and pause the monitor. Never redeem reset credits.
Bounded pre-inference operational fixes are allowed after retaining evidence and
checking invariants; inference failures are retained without automatic restart.

## Completion and interpretation

After both terminal reviews, record validity, elapsed agent time/tokens, strict
macro and split metrics, actual example use, method pseudocode/process diagram,
and native-coordinate visuals with legends. Original scores remain unchanged.
Any operational-policy mismatch is a qualified interpretation, not retrospective
rescoring. This one-case pair supports no population claim or isolated causal
estimate of the reference's effect. Pause the shared heartbeat after final review.
