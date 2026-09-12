# Geometry probe pre-trial review

Reviewed `probes/clipper-polytree` before model trials. This is a feasibility probe.

## Controls

The separate verifier writes numeric reward `0` before execution, protects that reward directory as root-only, and writes `1` only after success. It declares `/app/clipper2/src`; both images provide the literal `/app/clipper2` parent, and the verifier Dockerfile contains a standalone `RUN mkdir -p /app/clipper2` for static validation.

`tests/test.sh` and `solution/solve.sh` retain executable modes. The verifier source is root-only. It runs candidate compilation, a non-gating historical PolyTree diagnostic suite, and every candidate driver query after clearing supplementary groups and dropping to `tbrunner`. Candidate source is copied into a private working tree, normalized before use, then root-owned and read-only after the root-owned driver is injected. This prevents candidate runtime code from replacing the driver through its parent directory.

The corrected reference is not readable by `tbrunner`: its source and target live beneath `/reference`, mode `0700`, owned by a distinct `tbref` account. The verifier compiles and queries it as `tbref`, canonicalizes its output in root Python before candidate build/run, and locks its target root-owned/read-only. Candidate code cannot read or replace the corrected engine, its driver, reference binary, or expected data.

The semantic driver emits a recursive pre-order sequence containing depth, hole parity, and each contour. Root Python removes duplicate/collinear points, canonicalizes ring rotation and orientation, and sorts complete child subtrees. This accepts different traversal and vertex starts while comparing the full nested tree and normalized contours. The trusted historical `Tests/test_cpp_polytree.rs` is staged privately into Cargo's normal lowercase `tests/` integration-test location, so all fourteen original cases can run diagnostically after the required semantic comparisons; historical test exit status does not affect reward.

The verifier image explicitly installs `python3`, bakes `cargo fetch --locked`, and has separate limits: 120 seconds for builds, 35 seconds for the historical regression run, and 8 seconds per driver query within a 150-second verifier deadline. Temporary build proxy arguments were used only for local image preparation and are not in any Dockerfile.

## Earlier native Docker evidence (before pickup revision)

The final archived-fixture verifier image built successfully. Its baked dependency step completed with the temporary proxy arguments and `python3 --version` reported 3.11.2.

- Historical parent source staged at `/app/clipper2/src`: failed with exit 1, reward `0`; the trusted regression reported 9 failures and 5 passes.
- Reference `solution/engine.rs` staged at the same artifact path: passed with exit 0, reward `1`, printing the then-current four-case success label (three base geometries plus one translation).

The checker suite passed 21 of 22 pinned static checks using project Python 3.12. The remaining `check-task-fields.sh` failure is deliberate: it requires a human-authored README with four experience/solution sections, which this feasibility probe must not generate.

The agent-visible historical snapshot was also checked for answer leakage: no `.git` directory, future-fix hash, HOW_WE_PORTED narrative, or compiled reference artifact is present. Public ignored historical PolyTree tests remain as legitimate task context. The corrected reference is present only in the protected verifier image.

## Pickup review before the first model trial

The read-only geometry audit found two genuine grading defects: historical
assertions required specific sibling indices despite the unordered-tree
contract, and simultaneous duplicate/collinear removal could turn a square
with a repeated closing vertex into a triangle. These defects were found before
Terra ran. The initial pickup oracle was cancelled during authoring revision;
it produced no verifier reward and cannot establish a validated snapshot.

The revised verifier uses semantic tree equivalence as its verdict and run
the historical suite as a diagnostic. It normalizes repeated endpoints
before removing intervening collinear vertices, retains backtracking segments,
and checks public parent/level consistency and clipping operation success.
The instruction explains how to expose uppercase historical `Tests/` to
Cargo. The semantic fixtures comprise three base geometries and one translation
check; the transform is not an independent base example.

Dependency fetching is moved before verifier-script COPY in the Dockerfile to
reuse baked dependencies when the grading script changes. Runtime dependencies
and the geometric task remain the same. Exact revised evidence will be recorded
in the pickup freeze and trial summary after the controls finish.

Final pickup v3 Docker controls completed: oracle reward 1 and nop reward 0,
with matching Harbor checksums and no exceptions. The corrected reference also
passes all 14 historical diagnostic tests. Final local static sanity is 21/22;
the sole remaining failure is the intentionally missing human-authored task
README. The [freeze](evidence/clipper-pilot-freeze.json) and
[trial summary](evidence/clipper-trial-summary.json) identify this revision.

The final Terra/high trial also returned reward 1 without exception. Its submitted
source changes horizontal registration/order and containment cleanup; it is not
identical to the upstream patch. The tested semantic queries and all 14 historical
diagnostics pass, which does not establish equivalence for arbitrary polygons.
Keep the frozen passing result; do not retrospectively change its grading.
