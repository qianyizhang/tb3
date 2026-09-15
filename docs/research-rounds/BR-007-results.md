# BR-007 — stronger Clipper coverage, Sol/xhigh pass

**The requested difficulty target was not reached.** One fresh Sol/xhigh run
passed all 144 private semantic cases and completed normally in **1,315.843
seconds** of a 1,800-second allowance. A separate replay of the submitted source
also passed 144/144. Retire this exact condition from Sol difficulty selection;
retain the earlier BR-005 Terra failure as a different model and condition.

## Task, hypothesis and frozen evaluation

The [predeclared plan](BR-007-clipper-sol-xhigh.md) kept the historical broken
Rust clipping engine and source-only deliverable, without the original bundled
working C++ reference. It expanded the previous three base layouts/four semantic
checks to **18 base layouts × four integer transforms × two input-order
variants = 144 cases**. Seven layouts come from historical rectilinear
regressions; eleven are original joined ladders, deep nesting, signed fill,
Boolean-operation and empty-result layouts. The 144 variants are correlated;
they are not 144 independent task families.

The conceptual crux remains correct contours and containment around shared
edges. The hypothesis was that a partial repair or reconstruction of nesting
might pass visible examples while retaining incorrect contour topology. The
agent received a working Rust toolchain, four public examples, an API driver,
an order-independent output checker and the existing historical diagnostics.
The prompt specified behavior and input bounds, without a repair algorithm.

The author computed expected geometry through exact elementary-cell Boolean
membership and boundary extraction, independently of either Clipper version.
The grader contains baked trees, not a working reference implementation. It
compares complete normalized contours, hierarchy, links, levels, hole flags and
repeat execution. All cases and controls preceded the model run; none was
removed or added after its answer. The [freeze](../evidence/br007-clipper-freeze.json)
retains all 62 input hashes, build inventory, archive and execution settings.

## Controls and result

| Source/agent | Passed | Failed | Interpretation |
| --- | ---: | ---: | --- |
| Full historical repair, native control | 144 | 0 | Independent truth agrees with the known repair |
| Original broken source | 64 | 80 | Grader detects the starting defect |
| BR-005 Terra submission | 72 | 72 | Earlier partial repair does not generalize |
| Registration update reverted | 64 | 80 | Incomplete repair rejected |
| Ordering update reverted | 72 | 72 | Incomplete repair rejected |
| Persistent scan-position updates removed | 144 | 0 | Passing simplification control; no semantic defect established |
| **Sol/xhigh, fresh Harbor/Codex** | **144** | **0** | **Normal model pass** |
| Submitted Sol source, author replay | 144 | 0 | Matches the private trial result |

Matched Harbor oracle/nop controls also returned 1/0 without exceptions on the
same task checksum. Native full-repair verification, including compilation,
took 1.813 seconds on two CPUs; the submitted-source replay took 2.737 seconds.
The model's Harbor verifier stage took 13.5 seconds including harness work.
The 45-second execution allowance did not decide the outcome. Controls used
Harbor 0.18; the model used Harbor 0.14 and Codex CLI 0.154.0.

[Author controls](../evidence/br007-author-controls.json),
[round evidence](../evidence/br007-round-summary.json), and
[model trial](../../catalog/trials/clipper-polytree__N4WmGSY-a5c7522c.json)
retain exact counts, hashes and raw-source links. Only this round's three
completed receipts were imported; no other experiment was synchronized.

## Trace audit and actual solution

The one fresh session records `gpt-5.6-sol`, effort `xhigh`, the frozen prompt,
**55 paired top-level tool calls**, and normal `turn.completed`. Its initial
source reads and public reproductions precede the first source patch. The
recorded calls show no private-reference read, online solution fetch or
delegation. The agent image contains neither the private geometry generator nor
the oracle solution or prior model artifact. This supports a valid observed
solution; it cannot prove absence of model pretraining knowledge.

Only `engine_public.rs` differs in the submitted source. Sol added roughly 440
lines to split directed boundary walks at junctions, cancel coincident opposite
edges, trace planar faces with integer predicates and assign the smallest
containing parent. It retained the clipping sweep in `engine.rs` byte-for-byte.
This is a substantive alternative repair of the stated behavior, not a copy of
the historical oracle, which changes `engine.rs`.

Sol also wrote a rectangle-cell oracle during the run: **320 generated rectangle
cases and 96 shear cases passed**. Those checks are worker-authored diagnostics,
separate from our 144 private cases. Its final claims of 4/4 public examples,
14/14 historical tests and 392/392 library tests match recorded command outputs.
Temporary historical-test edits only added and then removed debug printing;
assertions were not weakened. Removing its copied public driver at cleanup was
legitimate: the grader supplies that driver independently.

Useful raw trace anchors (JSONL line numbers):

| Evidence | Line |
| --- | ---: |
| Recorded model and effort | 8 |
| First public reproduction | 40 |
| Substantive Rust implementation patch | 140 |
| Self-authored 320-case rectangle checker | 263 |
| Temporary test logging removed; assertions retained | 310 |
| Self-authored 96-case shear checker | 395 |
| Final 14-test historical run | 418 |
| Public-driver cleanup | 432 |
| Final submission summary | 447 |

Raw trace:
`runs/br007-clipper-sol-xhigh-v1-20260915/clipper-polytree__N4WmGSY/agent/sessions/2026/09/15/rollout-2026-09-15T01-08-19-01a0a29b-9324-7642-af51-36c68ef649ac.jsonl`.
The [evidence summary](../evidence/br007-round-summary.json) hashes that trace,
the compact inspection, submitted files and replay outputs. Local report:
`runs/br007-clipper/report.html`, with expected/actual contour inspection for
every case. The report is generated and structurally checked; no browser visual
inspection is claimed.

## Interpretation and limits

Stronger coverage rejected the earlier Terra patch but did not make the
underlying task difficult enough for this Sol run. Sol's reconstruction
approach generalized across the frozen layouts. More transformed cases alone
would not establish a harder conceptual problem. Do not restrict a valid
alternative repair after seeing it or convert a passing run into a failure by
retrofitting the private tests.

This was one diagnostic, not a pass-rate estimate or the final qualification
series. The older Terra and current Sol results differ in model, effort,
prompt/package and grader; they are not a controlled model ranking or an
isolated estimate of the effect of removed hints. BR-005's genuine Terra failure
remains intact. BR-007's Sol pass is retained as counterevidence to its difficulty
hypothesis; further selection should begin from an independently demonstrated
Sol miss or a separately motivated conceptual problem.

[Static checks](../evidence/br007-static-summary.json) passed 20/22: two copied
files lack canary comments, and the required human-authored submission README
is absent. These packaging gaps did not affect execution and remain in this
frozen diagnostic snapshot. Any submission cleanup needs a later snapshot and
the separately owned qualification gates.
