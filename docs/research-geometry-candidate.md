# Geometry candidate: historical Clipper2-Rust horizontal joins

Retrieved 2026-09-12. This ledger records source history and Docker controls;
at initial research time no Harbor or model trial had been run. See the
pickup update below for later execution.

## Primary-source facts

| Source | Factual record |
| --- | --- |
| [Porting account](https://github.com/larsbrubaker/clipper2-rust/blob/main/HOW_WE_PORTED_CLIPPER2.md) | The author describes three horizontal-join port differences: early flag setting, reversed sort, and lost loop state; nine PolyTree tests failed. |
| [Fix `561f3f861f27cd2501678c3851e0d6cb2dd5c517`](https://github.com/larsbrubaker/clipper2-rust/commit/561f3f861f27cd2501678c3851e0d6cb2dd5c517) | The commit names the same three causes, says all 444 tests passed, removes nine `#[ignore]` attributes, and changes `src/engine.rs` by 20 additions/7 removals. |
| [Historical parent `4ae2372ddcb1bfae77ee6ae00b15e63cc66300c4`](https://github.com/larsbrubaker/clipper2-rust/tree/4ae2372ddcb1bfae77ee6ae00b15e63cc66300c4) | This checkoutable pre-fix commit contains the nine ignored tests in `Tests/test_cpp_polytree.rs`; their annotations say hierarchy is wrong (all paths at root or children not nested). |
| [Historical Cargo manifest](https://github.com/larsbrubaker/clipper2-rust/blob/4ae2372ddcb1bfae77ee6ae00b15e63cc66300c4/Cargo.toml) | Rust 2021; direct runtime dependency `num-traits = "0.2"`; dev dependency `criterion = "0.5"`; manifest declares `BSL-1.0`. The historical tree has a version-4 `Cargo.lock` but no committed license text. |

## Reproduction status

Local full clone and detached worktree succeeded (about 3.5 MB checkout):
`4ae2372ddcb1bfae77ee6ae00b15e63cc66300c4` is a valid broken historical
state. Source inspection confirms the ignored tests assert root/child counts
across union, intersection, and XOR fixtures. The correction has three
semantic parts in two horizontal-join areas: enqueue eligibility, ascending
left-x order, and persistence of four advanced loop positions. A small
temporary-variable refactor in the same diff is non-semantic.

Native Rust remains absent, but a disposable official
`rust:1.85-slim-bookworm` container (rustc/cargo 1.85.1) ran the exact parent
with its lockfile through the local registry proxy. All nine formerly ignored
tests failed while five existing tests passed; first compilation took 29.87 s
after dependency download. The corrected commit passed 14/14 in 0.18 s after
a 7.20 s compile. A custom driver also rejects the parent on three nested
hierarchies and accepts the correction on those plus a flat union. This is a
witnessed control, not a model result.

## Candidate assessment

This is richer than a one-line port mismatch: diagnosis links PolyTree nesting
to horizontal collection, ordering, and stateful traversal. The public fix is
also unusually discoverable, so it needs a source-lookup screen before
promotion. The BSL-1.0 declaration is preserved with standard upstream text
in the probe's authoring record; attribution remains a review item.

If prototyped, freeze the parent above and retain provenance. Use a small fresh
subset of the historical inputs plus held-out transforms. Compare **semantic
PolyTree equivalence**, not vertex order: normalize closed-ring rotation and
winding, compare polygons by geometry, then compare parent/child containment
and depth/hole parity as an unordered tree. Also require a simple flat union.
Do not package three invented mutations or copy upstream ignored tests whole.

**Status:** executable historical failure, corrected reference, and fast
container build are witnessed. Native Rust remains absent but does not block
the Docker target. Model difficulty and submission eligibility are unverified.

## Pickup execution

The geometry-only pickup corrected pre-trial semantic grading defects and ran
same-snapshot Harbor/Docker controls: oracle 1, nop 0, no exceptions. The
Terra/high diagnostic completed with reward 1 and no exception in 494.711s.
Retire this snapshot from difficulty selection; no Sol/Opus run is warranted. See [pickup](pickup-20260912.md),
[review](geometry-review.md), and [trial evidence](evidence/clipper-trial-summary.json).
Historical controls remain distinct from model outcomes.
