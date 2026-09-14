# BR-002 — Sol/Astra capability experiments

Captured 2026-09-14. **Historical intake snapshot below; execution is complete.**
All four pilots subsequently passed with both Sol/max and Astra/max and were
retired. See the [execution plan](BR-002-execution.md),
[local results](BR-002-results.md) and [round register](../research-rounds.md).
The proposal statuses, untested claims and next actions below describe the
intake before execution; they are retained as the original design record.

## Provenance and change of question

Source: [Brainstorm New Tasks](chatgpt-conversation://6aa74ac6-4190-83ee-9eaf-603e1ae6ab9e).
The later research turn asks which capabilities improved from Sol to Astra;
the latest turn asks for experiments to test those leads. Source message IDs,
retrieved-prefix digests and limits are in the
[intake receipt](../evidence/brainstorm-round-002-intake.json).

Both later assistant messages reach the retrieval tool's 20,000-character cap.
The design prefix includes D01–D03 and D04 through its verifier; it cuts off
during D04's GOLD-GLYPHS ablation. Referenced downloadable specifications,
research index and numerical-check artifacts were not returned as attachments.
This is an authored synopsis of the available text, not an intact downloaded
specification. Raw retrieved text stays in ignored
`.cache/brainstorm-round-002/retrieved-discussion.json`.

[BR-001](../research-brainstorm-experiments-20260914.md) tested six small
scientific extractions and observed six healthy Terra/high passes. This round
asks whether **the same valid task separates Sol and Astra**, then whether a
controlled information change helps explain the difference. Scientific meaning
across representations, informative experimentation, and visual relationships
are proposed mechanisms. They are not established explanations of model gains.

The discussion reports 20 Sol-fail/Astra-pass tasks among 119 SWE-bench Science
tasks (40 both pass, 8 reverse, 51 both fail), with 11 of those 20 also missed by
Opus. These are **unverified imported discussion claims**, not receipts audited
in this repository. The available text explicitly says usable original
trajectories/patches were not recovered. Do not promote them to genuine failures.

| Source lead reported in discussion | Reported Sol → Astra private tests | Proposed audit question |
| --- | --- | --- |
| 005 Osprey, edited MRS polarity | 1/4 → 4/4 | Signal semantics or ordinary array handling? |
| 041 SunPy, near-Earth vectors | 8/24 → 24/24 | Physical operator, conventions or routine implementation? |
| 047 scikit-rf, broadband composite | 6/7 → 7/7 | What exactly does the remaining assertion enforce? |
| 073 Biotite, alternate conformers | 5/6 → 6/6 | Molecular identity/connectivity or a small edge case? |
| 089 cclib, oscillator strengths | 2/4 → 4/4 | Scientific correspondence or a parser branch? |
| 099 gnss_lib_py, point solution | 3/4 → 4/4 | Which positioning condition can be isolated? |

These fractions count private tests, not independent model attempts. Tasks 060
and 109 are additional reported leads held for workflow-size review. The
discussion prioritizes source audits of 041, 005, 073 and 047. Start from the
[release](https://github.com/OpenMOSS/SWE-bench-Science) and
[matrix](https://swescience.github.io/task-matrix/gradient/) and recover actual
instructions, assertions, completion status, patches and historical digests
before adopting a claimed failure mechanism. No new upstream audit is claimed
by this intake.

## Queue and proposed order

| Scoped ID | Catalog ID | Deliverable / role | Next bounded action |
| --- | --- | --- | --- |
| BR-002/D02 | `rf-wave-compose` | One RF composition function; main scientific candidate | Audit source 047's missing check; compare an allowed scikit-rf baseline with an independent nodal oracle. |
| BR-002/D04 | `score-sounding-events` | Four image transcriptions as JSON; main visual candidate | Recover or explicitly re-author the incomplete ablation; validate one rendered excerpt and equal image access. |
| BR-002/D03 | `actuator-memory` | Predictor for one fixed stateful instrument; interactive candidate | Confirm service packaging and identify one instance with a fixed ramp/reversal/dwell baseline. |
| BR-002/D01 | `moving-frame-velocity` | One velocity conversion function; cheap calibration | Audit source 041 and check whether its actual miss relates to frame motion; validate the small witness. |

All four catalog statuses are `idea`; none is runnable or promoted. This order
captures the new discussion's priorities within BR-002. The
[benchmark-backed shortlist](../research-benchmark-backed.md) still owns the
workshop's reproduction priorities. The new source outcomes need auditing
before they can displace localization or stellar-period inference.

## D01 — Moving-frame velocity

**Task.** Repair `convert_track(track, frame) -> (p_frame, v_frame)` for float64
times and world positions/velocities of shape `[N,3]`. A smooth, inspectable
`frame.pose(t)` returns rotation R from local to world and local-origin position
c in world coordinates. Output velocity is the time derivative of the output
position coordinates. Supply units, time domain and smooth pose helpers; permit
analytic, automatic or numerical differentiation.

**H-D01.** A rotation-only solution passes static-frame controls but misses
translation/rotation of the observer. At t=0, a stationary world point (2,0,0)
viewed in a coincident frame rotating at +1 rad/s about z has coordinate velocity
(0,-2,0). The proposed author reference differentiates
`p_F = R.T @ (p_W - c)` to obtain
`v_F = R.T @ (v_W - c_dot) - R.T @ R_dot @ p_F`.
This constructed witness is not an audited explanation of source 041.

**Fixtures and evaluation.** Proposed v0: 12 analytic tracks, 5–11 timestamps
each, covering static, translating, rotating and combined frames, successive
rotations about different axes and equivalent world-origin shifts. Independently
compare the analytic derivative with finite differences of transformed positions
at several step sizes. Proposed tolerances: position error 1e-8 m; normalized
velocity error 1e-7; finite values, correct shape and ordering. Define the
normalization and differentiation boundary domain before freezing. Avoid noisy
samples, extreme scales and astronomy infrastructure. An ordinary derivative
baseline is permitted.

**Inspect and ablate.** Distinguish omitted origin velocity, omitted rotational
term and a rotation-sign error. Inspect actual code and executed examples. Compare
the natural contract with a formula-supplied condition; optionally supply only
R_dot/c_dot to isolate derivative extraction. Improvements are diagnostic
evidence, not a complete causal explanation. A clean Sol pass retires the
snapshot; do not add accelerations or artificial restrictions to rescue it.

**Evidence status.** The discussion reports 32 manufactured checks with maximum
analytic/finite-difference discrepancy about 1.22e-9 m/s and a rotation-only
failure on every checked case. No executable check or raw result was retrieved;
these are reported author checks, not local reproduction or model trials.

## D02 — RF wave conventions

**Task.** Implement `compose(left, right) -> complex128[F,2,2]`. Each decoded
input has a shared `frequency_hz` grid, S matrix, per-port complex `z0[F,2]`, and
`wave_definition` of power or pseudo. Connect left port 2 to right port 1; return
S under real 50-ohm power-wave references. Publish exact wave definitions, inward
port-current directions, connection equations, allowed impedance domain and port
order. The supplied metadata must be enough to identify the physical network.

**H-D02.** A familiar cascade silently uses common real references or a default
wave convention. Ordinary 50-ohm controls pass but equivalent representations
produce different composites. The discussion's one-port witness is a 50-ohm load
under reference 50+30j: power reflection 0.0825688+0.2752294j versus pseudo
-0.0825688-0.2752294j. Recheck definitions and this witness before fixture use;
neither establishes the cause of source 047's seventh-check miss.

**Fixtures and evaluation.** Proposed v0: eight physical pairs of T circuits
(two series impedances and a shunt), four representations per pair, sixteen
frequency samples. Include real/complex and unequal port references, both wave
definitions and mixed conventions. Exclude singular ideal components,
interpolation, noise and larger network graphs. Construct an independent nodal
admittance system for the connected physical circuits, eliminate internal nodes,
and compute the target response. Proposed maximum error in each real/imaginary
component: 1e-8; require finite output and correct port order. Equivalent
encodings supplement the physical oracle. Representations/frequencies are not
independent model attempts. Validate conditioning and threshold before freeze.

**Baselines, inspection and ablation.** Run a convention-aware scikit-rf wrapper
and an independent circuit solution. Incorrect controls separately ignore z0,
ignore wave tags, or relabel metadata without transforming S. Inspect which
mistake the delivered artifact exhibits and check connected-current signs.
GOLD-Z supplies each input network's correct physical impedance matrix, leaving
connection and output conversion to the agent. A smaller deficit then implicates
input conversion. A correct library wrapper is a legitimate success. If both
models solve the snapshot readily, retire it; do not prohibit scikit-rf.

**Evidence status.** The discussion reports 128 single-frequency representation
checks, maximum complex-S discrepancy about 5.19e-16 against a nodal oracle, and
at least 0.132 error for a metadata-discarding implementation on each tested
case. Raw checks were not retrieved. Broadband generation and the scikit-rf
baseline were explicitly not run in that discussion. All remain local prep work.

## D03 — Actuator memory

**Task.** Use `lab probe --commands '[...]'` to calibrate one fixed instrument;
each call resets it and returns output after every command. Deliver
`predict(commands)` for the same instrument from the known reset state, without
lab access at evaluation. Historical data contains increasing sweeps. Publish
exact recurrences and bounded parameter/input domains for the allowed families:
static dead zone, play/backlash and first-order lag. Measurements are
deterministic with no noise, drift, hidden delay or query-count rationing.

**H-D03.** The agent fits an increasing sweep without collecting or integrating
observations that reveal memory. The reported width-0.2 witness uses commands
`[0, .4, .8, .7, .6, .3]`: static outputs `[0, .2, .6, .5, .4, .1]`, play outputs
`[0, .2, .6, .6, .6, .5]`. The increasing prefix agrees; a reversal distinguishes
the models. This is a new stateful mechanism relative to BR-001/E04's affine
clamped instrument, not a harder revision of its retired freeze.

**Fixtures and evaluation.** Freeze one instrument/parameter instance for both
models; held-out tests vary histories, not mechanisms. Proposed twelve short
sequences span sweeps, reversals, repeated commands, dwells and sign changes;
maximum absolute prediction error 1e-6 against independent recurrences. Accept
predictive equivalence, independent of terminology or graph/parameter names.
A predetermined ramp/reversal/dwell baseline must fit all allowed families and
solve the selected instance. Validate identifiability across its declared bounds.

**Inspect and ablate.** Retain every probe/response and check whether the submitted
predictor reproduces its own observations. Separate never requesting a reversal
from ignoring a revealing response. Compare active investigation, informative
reversal/dwell logs supplied, and the true rule/parameters supplied. Those
conditions distinguish measurement selection, inference and state bookkeeping.
Retire if sensible probes solve the small task; do not add hidden state or
restrict measurements merely to obtain a miss.

**Preparation boundary.** Confirm that the harness can expose the measurement
service separately from the agent filesystem and remove access during grading.
Exact recurrences, bounds and deployment are still to be authored and checked.
The conversation reports executing the witness but returned no raw artifact;
there is no local model evidence for H-D03.

## D04 — Score images to sounding events

**Task.** Transcribe four visible typeset excerpts into JSON entries with
`excerpt_id` and `events` containing MIDI pitch, `onset_quarters`, and
`duration_quarters` as exact rational strings. Merge tied segments into one
sustained event; retain untied repeated attacks and simultaneous voices. Declare
the time origin and all supported notation semantics. All target images are
visible; this is a fixed artifact task, not unseen-image generalization. Manual
correction and conventional optical music recognition are permitted.

**H-D04.** Symbol recognition succeeds while relationships fail: voices become
serial, accidental scope is wrong, ties become extra attacks, or repeated notes
merge. The proposed witness ties C4 at beat 3 for one quarter to C4 at beat 4 for
two quarters: one `(60, 3, 3)` event. A G4 at beat 4 is simultaneous with the
sustained C4; a later untied C4 starts a new event. Fix beat-origin notation in
the actual pack before constructing this example.

**Fixtures and evaluation.** Proposed four newly authored four-bar excerpts,
roughly 20–40 sounding events each, at most two voices, standard treble/bass
clefs, chords, rests, dots, accidentals and bar-crossing ties. Exclude tuplets,
ornaments, repeats, cross-staff beaming, changing meter, transposing instruments
and ambiguous overlapping unisons. Use readable ordinary typesetting, a pinned
renderer, canonical notation/events and an independent transcription/review of
the actual raster. A source-file round trip alone cannot validate image truth.

Canonicalize exact `(pitch, onset, duration)` multisets; ignore event order,
internal voice IDs and enharmonic spelling for the same sounding pitch. Proposed
published thresholds: aggregate exact-event F1 >= 0.98 and each excerpt >= 0.95.
Define aggregation/multiset matching and empty/malformed submissions before
freeze. Relation-specific errors are diagnostics, not extra hidden gates.

**Ablation gap and next step.** The retrieved text begins GOLD-GLYPHS, supplying
glyph identities and bounding boxes, then truncates. Its remaining information
contract, baseline, stop rule and any later shared run plan were not recovered.
Recover those sections or explicitly author a replacement revision before
execution; do not present invented details as the source design. First validate
one excerpt's raster/ground truth and equal image-tool support for both models.
No locally verified fixture or model outcome is available.

## Proposed comparison protocol and unresolved choices

The available discussion proposes repeated Sol/Astra trials on the same frozen
natural task and a controlled simplification. It does not supply a retrievable
complete execution lock. Exact model IDs, effort, harness/version, repeated
attempt counts, ordering, stopping rules and resource limits remain unset.
The repository currently uses Terra/high for early diagnostics and reserves
Sol/Opus for mature candidates. A Sol/Astra capability study is a distinct
diagnostic protocol to resolve explicitly before launching, not an implicit
change to [requirements](../requirements.md) or an instruction extracted from
the referenced chat. No execution is launched by this intake.

Before trials, validate each contract, independent oracle, strongest permitted
baseline and targeted incorrect controls; freeze every natural/ablation condition
separately. Within a condition match task bytes, harness, available tools/images,
network and measurement access. Record full settings and normal completion with
verifier evidence. Keep substantial reasoning time; retain passes and legitimate
library solutions. Trial count and optional stopping must be declared before
observing the comparison.

Judge **validity**, **success**, and **hypothesis support** separately. The useful
signature is a control/discriminating-case contrast, a corresponding artifact
mistake, and improvement under the targeted information change. One different
result does not estimate a general capability gap; an ablation also changes task
information. Infrastructure errors, timeouts and task/oracle faults are excluded
from model-failure conclusions. Final qualification remains separately governed.

## Intake outcome and dated decisions

- 2026-09-14 — Registered BR-002 and four `idea` catalog cards with tag
  `brainstorm-round-002`; captured the six differential source leads for audit.
- Local fixture checks this intake: **0**. Local model attempts: **0**. Imported
  local trial records: **0**. H-D01–H-D04 remain untested.
- The existing local denominator remains **12 healthy Terra/high passes,
  0 genuine failures, 2 historical infrastructure-only attempts**; see the
  [ledger](../ledger.md). Published fractions and discussion-reported numerical
  checks do not enter it.
- Next bounded work: D02 source-assertion audit and baseline/oracle preparation;
  keep D04 available as a different task type. This is a preparation queue,
  not a frozen model-run schedule.
