# Clipper calibration: completed geometry repair

Reviewed 2026-09-12. Classification: **legitimate completed Terra/high pass on
the recorded geometry probe**, suitable as calibration evidence. This single
pass provides no evidence that the task is difficult for Terra and establishes
neither a success rate nor general Clipper correctness.

The [trial result](../../runs/clipper-terra-high-v3-20260912/clipper-polytree__mhTdP5c/result.json)
records `openai/gpt-5.6-terra`, reasoning effort `high`, reward `1.0`, and
`exception_info: null`. Its Harbor task checksum is
`257b1d4e31e6812797ccdf34aaa5550c654d3700174b02b1fdb848d9bf48e96e`.
The [verifier output](../../runs/clipper-terra-high-v3-20260912/clipper-polytree__mhTdP5c/verifier/test-stdout.txt)
confirms the normalized hierarchy comparisons for three base geometries and one
translation check; the additional historical diagnostic passes all 14 tests.

The [artifact manifest](../../runs/clipper-terra-high-v3-20260912/clipper-polytree__mhTdP5c/artifacts/manifest.json)
records successful collection of `/app/clipper2/src`. A byte comparison against
the [supplied source](../../probes/clipper-polytree/environment/clipper2-src/src)
finds the same 22 files, with exactly two changed:

- [engine.rs](../../runs/clipper-terra-high-v3-20260912/clipper-polytree__mhTdP5c/artifacts/app/clipper2/src/engine.rs):
  horizontal trial joins exclude open paths and defer assigning `horz` until
  segment conversion; valid segments are stably sorted in ascending x order.
- [engine_fns.rs](../../runs/clipper-terra-high-v3-20260912/clipper-polytree__mhTdP5c/artifacts/app/clipper2/src/engine_fns.rs):
  temporary contour cleanup for containment follows the bundled C++ axis-aligned
  procedure instead of removing all collinear points.

These are changes to the existing clipping algorithm. The final artifact
contains no case-specific outputs or replacement wrapper, and its existing
source tests are unchanged. The [recorded command output](../../runs/clipper-terra-high-v3-20260912/clipper-polytree__mhTdP5c/agent/codex.txt)
shows a baseline of 5 passing and 9 failing historical cases, followed by a final
14/14 pass. The regular Cargo run also passes 392 unit tests, 5 active historical
tests with 9 ignored, and 2 doc tests; the separate `--include-ignored` run is
the evidence for all historical cases.

The [trajectory](../../runs/clipper-terra-high-v3-20260912/clipper-polytree__mhTdP5c/agent/trajectory.json)
contains 42 `exec_command` requests and 17 `apply_patch` requests. No online
solution retrieval or task-instruction violation was observed. It explicitly
uses the already supplied `CPP/Clipper2Lib` sources as a local porting reference,
which the [instructions](../../probes/clipper-polytree/instruction.md) permit.
Initial missing Cargo/Git commands, intermediate failing tests, an unavailable
`cargo-fmt`, and a rejected cleanup command do not invalidate the later
completed verifier pass. Formatting was not successfully checked.

The repair is not identical to the [grader reference](../../probes/clipper-polytree/tests/reference-engine.rs).
Both fix trial-join registration and sorting. Terra retains baseline behavior
where the reference persists advanced `left_op` values during join pairing,
and Terra additionally changes `get_clean_path`, which the reference leaves
unchanged. The observed fixtures accept both implementations; this review did
not test whether those differences affect other geometries. Treat the outcome
as **one completed model pass, with broader equivalence unestablished**.
