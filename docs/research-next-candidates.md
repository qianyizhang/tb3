# Next runtime candidates (screen only)

Research date: 2026-09-12. These are source-backed leads, not completed
probes or demonstrated model failures. Local source snapshots are ignored in
`runs/research-next/`; no model or large build was run. The host lacks Go, so
the GoAWK executable reproduction below is from the upstream issue and merged
regression tests, not a local execution claim.

## 1. GoAWK: nested post-increment must preserve lvalue/index state

**Disposition: strongest next implementation candidate, if a Go toolchain
layer is acceptable.** GoAWK is a small Go implementation of AWK. Use official
source commit [`d4cd0afb`](https://github.com/benhoyt/goawk/tree/d4cd0afb1b243e6a9459efde120322cf337f8e0e), the immediate parent of the
fix; it is two commits after the released `v1.25.0` and before `v1.26.0`.

* Firsthand report: [issue #79](https://github.com/benhoyt/goawk/issues/79),
  opened 2021-12-24, shows `$$0++` parsed as `($($0))++` and rejects the
  compact `$$a++++` form. The merged fix [PR #215](https://github.com/benhoyt/goawk/pull/215),
  commit [`9241da4c`](https://github.com/benhoyt/goawk/commit/9241da4cf81b87284e341ee0bba6358559cfef15),
  adds maintained end-to-end regressions and records a second independent
  wrong-result case (`34345` versus `33345`).
* This is not a single syntax branch. The upstream repair changes parser
  precedence for `$` with postfix operators, compiler evaluation of field and
  indexed lvalues, and the VM stack order (new `Rote` opcode). Correctness
  needs each index expression evaluated once, mutation applied to the intended
  field/array cell, and the expression value retained in the specified order.
* A compact task can package that exact vulnerable tree, ask the candidate to
  repair the interpreter, and build only `./cmd/goawk`. `go.mod` declares Go
  1.16 and has no external module requirements; expected build is seconds
  after the toolchain image is present. A `golang:1.22-bookworm` builder is a
  meaningful cold-image cost, so measure it before promotion.
* A trusted verifier should rebuild the submitted tree and compare byte output
  for: the issue's input `echo '2 3 4' | goawk '{ $$0++; print $0 }'` -> `3`;
  `$$a++++` -> `7`, then `3 4 6 6 8 8 9`, then `3`; and the PR's nested-array
  increment -> `33345`. Add the PR's `a[f()]+=g()` and functional field target
  controls to catch duplicated or reordered evaluation. Keep plain variable
  increment, simple `$2++`, and ordinary array assignment as regressions.
* Do not require an opcode name, patch shape, or a disabled optimization. The
  oracle is observable AWK behavior; GNU awk output is a useful independent
  reference for the fixed fixtures.

**Difficulty and risk.** This has interacting parser/compiler/VM invariants
and several valid-looking wrong implementations, so it is worth one fresh
Terra/high trial before reserving Sol. Its primary risk is operational rather
than semantic: the Go base image is much larger than the C/Python images used
by the current probes. It must also be mounted in a source-only task with a
root-owned verifier so editing tests or replacing the executable cannot pass.

## 2. Zstandard: valid two-byte zero-sequence header

**Disposition: credible C binary-decoder fallback, but probably too narrow for
the requested hard lane.** The official Zstandard decompressor errata says
`v1.5.5` and earlier rejected a valid compressed block when zero sequences were
encoded in the two-byte header form. The fix is commit
[`3732a08f`](https://github.com/facebook/zstd/commit/3732a08f5b82ed87a744e65daa2f11f77dabe954)
(2023-06-05), released in `v1.5.6`; the
[errata entry](https://github.com/facebook/zstd/blob/dev/doc/decompressor_errata.md)
names the last affected version and the exact fixture.

* Package official `v1.5.5` source and the 25-byte valid frame from the fix,
  `28b52ffd00008500006848656c6c6f20576f726c64210a8000`. The upstream golden
  test runs `zstd -t zeroSeq_2B.zst`; decompression yields `Hello World!\n`.
  Also retain malformed `zeroSeq_extraneous.zst` as a rejection control.
* It is a real decoder-state boundary: after decoding the two-byte count, zero
  must terminate the sequence section before any FSE-table parse. The source
  change moves the early-zero decision after variable-width count decoding and
  consumes the right number of bytes.
* `make zstd` is a small C build with no language runtime dependency, and a
  verifier can run decode output plus valid/invalid controls deterministically.

**Why it ranks second.** The published repair is only about ten lines and the
fixture isolates one unusual encoding (the reference encoder never emitted it).
It is excellent provenance and binary-format coverage, but is likely too
direct to explain three recent Terra successes. Use it only if a small,
honest decoder regression is more valuable than another hard pilot.

## Rejected during this pass

* **zlib `inflateSync()` bit-buffer fix** (`5af7cef`, 2023-08-24) is authentic
  but changes one shift direction: too close to the single-guard/single-token
  class the task excludes.
* **TinyCBOR available-buffer checks** (`5521ccf`, 2021-09-03) and **LZ4 small
  dictionary random-access example** (`855a0978`, 2024-11-18) are real but are
  boundary/error handling or example-only fixes, not an interacting runtime
  repair.
* **Tree-sitter Markdown incremental parse #5636** has a compelling stale-tree
  versus fresh-tree reproduction, but requires grammar/reproduction packaging
  and its fix history is too recent and insufficiently inspected for a fair
  source snapshot.
