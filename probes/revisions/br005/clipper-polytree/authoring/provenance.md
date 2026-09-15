# Provenance and witnessed controls

Retrieved and controlled 2026-09-12. The environment source is the exact
historical parent `4ae2372ddcb1bfae77ee6ae00b15e63cc66300c4` from
[larsbrubaker/clipper2-rust](https://github.com/larsbrubaker/clipper2-rust).
The reference `solution/engine.rs` is the corresponding production file from
[fix `561f3f861f27cd2501678c3851e0d6cb2dd5c517`](https://github.com/larsbrubaker/clipper2-rust/commit/561f3f861f27cd2501678c3851e0d6cb2dd5c517).
The historical Cargo manifest declares BSL-1.0. Its Git tree lacks a separate
license file, while current upstream supplies the standard Boost Software
License 1.0 text. That exact text is preserved in
`authoring/BOOST-LICENSE-1.0.txt`, copied verbatim from
https://github.com/larsbrubaker/clipper2-rust/blob/main/LICENSE on 2026-09-12.
Retain provenance
and obtain redistribution review before any external submission.

Controls used official Rust image digest
`rust@sha256:9f841bbe9e7d8e37ceb96ed907265a3a0df7f44e3737d0b100e7907a679acb36`
(rustc/cargo 1.85.1) and the checked-in version-4 Cargo.lock. The lockfile is
part of the historical Git tree (introduced by `d01210376df51dae70a464c8c15e9b5d5e2d41fc`), not generated during this control. The parent ran
14 upstream PolyTree tests with `--include-ignored`: 9 failed, 5 passed. The
fix ran 14/14. First dependency resolution/compile was 29.87 s through the
local registry proxy; corrected compilation was 7.20 s and tests 0.18 s.

The verifier does not grade upstream test exit status. It builds a root-owned
driver against only the submitted `src` tree as `tbrunner`, runs that binary as
the same user, and compares its complete recursive contours and hierarchy to a
separately built, root-locked corrected reference. Python canonicalizes
rotation, winding, repeated/collinear vertices, and unordered child subtrees
for two nested source cases, a translated invariant case, and a flat union.
