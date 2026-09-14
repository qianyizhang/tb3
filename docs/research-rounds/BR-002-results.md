# BR-002 local results

Completed 2026-09-14 under the [predeclared plan](BR-002-execution.md).
**All four tasks passed with both Sol/max and Astra/max: eight valid model
attempts, zero genuine failures, zero infrastructure exclusions.** All four
snapshots are retired. The [original intake](BR-002-sol-astra-capabilities.md)
retains the proposed designs and provenance limitations.

| Pilot | Local author verification | Sol/max | Astra/max | Disposition |
| --- | --- | --- | --- | --- |
| D02 RF composition | Library baseline 32/32; independent nodal error <7e-16; metadata controls rejected | Pass 32/32, 203.718 s | Pass 32/32, 214.608 s | Retired; H-D02 unsupported on this snapshot |
| D04 Score events | Four readable raster transcriptions match 96 events; relation controls rejected | Pass, exact 96/96 events, 849.882 s | Pass, exact 96/96 events, 195.167 s | Retired; H-D04 unsupported |
| D03 Actuator memory | Independent recurrence/service agree on 12 histories; identification baseline checked on 15 family/parameter instances | Pass 12/12, 68.715 s | Pass 12/12, 96.648 s | Retired; H-D03 unsupported |
| D01 Moving-frame velocity | Baseline agrees on 24 cases; independent trajectory derivative check passes | Pass 24/24, 132.703 s | Pass 24/24, 184.816 s | Retired; H-D01 unsupported |

Seconds are agent execution time, not the available 1,800-second allowance.
Counts in the author column are fixtures, not model attempts. Four scores use
two notation patterns across two clefs; RF representations and shifted frame
tracks also share underlying physical fixtures. No population pass rate is
estimated from these diagnostics. Final submission qualification is separate.

The [round receipt](../evidence/br002-round-summary.json) verifies eight sequential
model runs, unchanged frozen bytes, matching historical oracle/nop checksums,
Codex CLI 0.154.0, and the shared 1,800-second allowance. There are eight final
snapshot control attempts and four retained pre-freeze controls; none enters
the model denominator. No repeats or ablations were triggered. Required final
standard/adversarial trial counts remain 0/6 and 0/2.

## RF outcome

[Receipt](../evidence/br002-rf-summary.json),
[freeze](../evidence/br002-rf-freeze.json),
[author checks](../evidence/br002-rf-author-controls.json).
Both runs end normally with reward 1 and all 32 private cases passing on the
same Harbor checksum as oracle/nop. Both preserve the wave definitions and connect through physical voltage/current
relations. Sol eliminates the joined current using impedance matrices; Astra
solves for the input incident waves directly. Both encode 50-ohm power-wave S.
The straightforward scikit-rf wrapper also passes every case. No repeat or
GOLD-Z ablation is triggered by the predeclared rule.

## Source audit and preparation corrections

[Four published trace receipts](../evidence/br002-source-receipts.json) confirm
normal Sol/Astra completion and the reported 041/047 verifier fractions. Their
historical task digests are unavailable. Source 041 concerns Cartesian-vector
origin/rotation semantics; source 047's remaining Sol miss is generated-media
representation, while real-measurement composition passes. Those failures do
not transfer to our smaller derivative/composition tasks.

The RF environment's optional plotting-import notice was removed by supplying
a pinned matplotlib dependency before its freeze; mathematical controls were
unchanged. Generated Python caches were relocated from score/actuator source
trees before their final freezes. Both sets of controls were repeated on clean
source trees as v2; v1 control evidence is retained separately. These are
preparation changes, not model failures or post-result task repairs.

The score source's missing ablation tail was explicitly re-authored in the
execution plan. All four final rasters were visually transcribed and compared
with independently generated notation/event truth; no human expert review is
claimed. PNGs are required original task inputs, with exact retained-artifact
hashes, not generated runtime reports.

## Score outcome

[Receipt](../evidence/br002-score-summary.json),
[freeze](../evidence/br002-score-freeze.json),
[author checks](../evidence/br002-score-author-controls.json).
Both models produce exactly the independent 96-event multiset, aggregate and
per-excerpt F1 1.00. Sol uses 849.882 agent seconds; Astra 195.167. Both use the
same four images, contract, grader and Codex CLI 0.154.0. The one observed timing
difference is not a population speed estimate or a success-rate difference.
Both pass, so no GOLD-GLYPHS condition is triggered.

Sol's [artifact/inspection receipt](../evidence/br002-score-sol-inspection.json)
retains its executed image-tool evidence and output digest. It uses enlarged
crops and pixel/staff checks; the final artifact correctly merges both cross-bar
ties, preserves simultaneity and carries/cancels accidentals. Astra also writes
all 96 events correctly after visual and crop checks; its
[inspection receipt](../evidence/br002-score-astra-inspection.json) retains the
artifact digest and image-tool evidence. The small fixed task does
not exhibit the proposed Sol relationship-reconstruction failure.

## Actuator outcome

[Receipt](../evidence/br002-actuator-summary.json),
[freeze](../evidence/br002-actuator-freeze.json),
[author checks](../evidence/br002-actuator-author-controls.json).
Both models pass all 12 held-out histories and implement the correct play
recurrence with radius 0.173, resetting to zero on each predictor call. Their
first recorded probe includes a reversal and observes the held response; neither
remains with the static model that fits the increasing historical sweep.

The [Sol inspection](../evidence/br002-actuator-sol-inspection.json) records
3 probe calls containing 22 command steps; the
[Astra inspection](../evidence/br002-actuator-astra-inspection.json) records
14 calls containing 1,237 steps, including additional validation histories.
Each delivered predictor exactly reproduces its own recorded measurements.
These are single-run observations, not general query-efficiency estimates.
The active task is solved by both, so neither supplied-log nor supplied-rule
conditions run under the predeclared stopping rule.

## Moving-frame outcome

[Receipt](../evidence/br002-frame-summary.json),
[freeze](../evidence/br002-frame-freeze.json),
[author checks](../evidence/br002-frame-author-controls.json),
[artifact inspection](../evidence/br002-frame-inspection.json).
Both models pass all 24 cases, including motion, world-origin shifts and
nonmonotonic timestamp order. Sol differentiates the elementary rotation
matrices and applies the product rule. Astra derives the world angular velocity
and subtracts its cross product with the relative position before rotation.
Both subtract the frame origin's velocity. Neither exhibits the rotation-only
mistake targeted by H-D01; no formula-supplied condition is triggered.

## What this round establishes

The four original pilots are solvable and did not separate the two models on
their first natural-task pair. This does not show that the broader mechanisms
or source tasks are easy. The tested instances are small: one actuator, two
score patterns across clefs, eight circuit pairs, and twelve frame tracks.
The longer Sol score-transcription run is an observation from one pair, not a
reliable speed comparison. H-D01–H-D04 receive no support from these snapshots.

For the next selection round, inspect the exact failed requirement and submitted
artifact before proposing a smaller extraction. Source 041 tests vector
semantics rather than a moving-frame derivative; source 047's failed media
generation requirement was absent from D02. Preserve the established
[benchmark-backed priorities](../research-benchmark-backed.md), and leave the
remaining discussion-reported differential source claims unaudited until their
individual evidence is read. Do not add restrictions to rescue these retired
snapshots.
