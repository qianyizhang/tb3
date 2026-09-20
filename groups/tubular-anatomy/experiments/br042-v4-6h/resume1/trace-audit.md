# Why the resumed BR-042 result plateaued

2026-09-21 · Assistant investigation requested by the user in
[Investigate BR042 resume results](codex://threads/01a0c006-0f8c-78a1-8ab1-2f5868f21ee4).
Original task, references, submitted answers and scores are unchanged. This is
post-hoc analysis, including reference-assisted diagnostics, not another model run.

The strongest explanation is a combination of **work allocation, candidate
filtering, candidate rejection, and dependent branch numbering**. Extra time did
produce additional work, but the resumed session left its scored coronary
reconstruction almost entirely unchanged. There is an unresolved reference naming
question; there is no demonstrated GT-imposed ceiling that explains the whole result.

## What the last session actually did

The original six-hour-allowance run executed for **2h47m45s**, then failed in
transport. The continuation executed for **1h26m07s** and completed normally:
**4h13m52s combined agent wall time**, including inference, tools and transport
delays. Neither the original nor the fresh resumed six-hour allowance was exhausted.
The continuation restored its own answer and conversation; no GT, scores or
case-specific reviewer advice was added. The original interruption remains a
separate outcome.

Observable tool-call timeline, UTC on September 20:

| Time | Work visible in the trace | Consequence |
| --- | --- | --- |
| 12:06–12:30, before interruption | Coronary origins, main courses, side-branch search, native views, geodesic extraction; early valid answer | Most of the coronary reconstruction established |
| 12:31 onward | Expanded pulmonary arteries/veins, aorta, caval and cardiac veins; later revisited coronary boundaries and distal PDA | Broader scope, with intermittent coronary corrections |
| 15:52–16:00, resumed | Regenerated path cache; wrote a complete inventory/report from restored specifications | Recovered deliverable state, not a fresh extraction strategy |
| 16:02–16:18 | Renamed an upper-lobe PA course; added three right pulmonary courses and trimmed unsupported distal portions | Broader inventory improved; coronary reference does not score these courses |
| 16:29–16:55 | Coordinate/proximity checks, IVC image review, pulmonary backtracking investigation, context compaction | QA and uncertainty review; no change to coronary specifications |
| 16:55–16:56 | Fixed a pulmonary loop and repeated branch-origin portion | Concrete geometry corrections outside coronary scoring |
| 16:56–17:02 | Reviewed existing coronary courses and regenerated low-threshold candidates; added a superior RCA atrial branch | One new coronary branch with category 0; existing scored assignments retained |
| 17:02–17:13 | Validation, static overlays, full rebuild, junction inspection, final inventory and uncertainty notes | Completed reproducible artifact; no further coronary-score improvement |

The before/after diff is decisive: **all 15 existing coronary extraction
specifications are identical**, including names, labels, controls and parameters.
Fourteen of their exported course objects are identical. RCA changes from 303 to
304 points because the new atrial daughter inserts a junction into its parent;
its anatomical specification is unchanged. Across all vessels, 53 course objects
are identical. The output grows from 60 to 64 courses, with pulmonary changes and
the new atrial branch accounting for the substantive edits.

The resumed trace has 34 `exec` orchestration calls, plus 11 structured transport
errors. Its final event is normal completion. Long elapsed gaps do not establish
long useful reasoning: precise time lost to transport is not recoverable here.
The 76.3-second final feature/extraction rebuild shows that replaying the saved
controls is cheap; discovering and reviewing those controls was the expensive part.

## The most useful new finding: different branches fail at different stages

I independently reimplemented the saved candidate-generation filters using its
retained image, vesselness and paths. After removing the later-added atrial branch
and its extra RCA junction point, the recreated candidate voxel set matches the
saved set **exactly: zero added or missing voxels**. No historical authoring or
solver module was imported/executed. The following measurements use GT only to
locate and measure signal after candidate generation.

| Stage | D2 reference covered within 1 mm | OM1 reference covered within 1 mm |
| --- | ---: | ---: |
| Raw low-threshold skeleton | 93.9% | 78.3% |
| Exclude points within 1.3 mm of existing paths | 87.8% | 78.3% |
| Keep components with 6–2499 voxels | 87.8% | 55.8% |
| Require component within 2.2 mm of an existing path | 87.8% | 0% |
| Final submitted geometry | 3.1% | 0% |

**D2 was detected, retained, considered, and withheld.** Candidate #3 has 87
voxels, covers 87.8% of GT D2 at 1 mm and 100% at 2 mm. Its nearest point to an
existing path is 1.69 mm away, so it passes the generator's gates. The pre-resume
trace explicitly generated views around this location (12:22 and 12:28); the
resumed candidate listing again contains it. The final method interprets it as a
possible left-atrial-appendage/myocardial ridge and declines to submit it.
This is an acceptance/identity failure relative to GT, rather than a total failure
of the image feature detector. It differs from the earlier V3 medium attempt,
whose retained candidate paths barely covered D2. An unordered candidate component
is not yet a continuous, correctly connected arterial reconstruction.

**OM1 is lost in the algorithm's filters.** Its reference-center median is about
121 HU; only 57.1% of reference-center samples exceed both the saved vesselness
and HU thresholds. The skeleton nevertheless contains nearby fragments. A
3-voxel fragment fails the minimum size; a 13-voxel fragment representing 6.39 mm
of nearby reference length survives size filtering but is **4.55 mm** from an
accepted path, so the **2.2 mm hard parent-gap cutoff discards it**. This is a
reproduced mechanism, more specific than the earlier hypothesis about weak contrast.
It explains loss from the automatic candidate list, not every possible visual miss.

**Lowering one threshold does not fix the pipeline.** A post-hoc sensitivity run
changes vesselness from 0.018 to 0.006, keeping HU >80. Raw-skeleton OM1 coverage
becomes 100%, but most of it enters a **6586-voxel component**, rejected by the
2499-voxel maximum. Accepted OM1 candidate coverage remains 0%; candidate count
rises from 17 to 37. This is not a validated threshold improvement. It motivates
splitting skeleton graphs into branch paths before filtering, rather than treating
whole connected components as candidate vessels.

**OM2 mixes incomplete geometry and renumbering.** Final geometric coverage is
57.2%, assigned OM1. The saved skeleton has additional nearby signal, including a
14-voxel component 3.45 mm from an existing path, also rejected by the parent-gap
gate. The completed V3 medium output covered the full reference OM2 course, so the
longer attempt's shorter result is not evidence of an intrinsic visibility ceiling.

## Does GT impose the performance ceiling?

The answer is **not demonstrated**, with a narrower naming dispute still open.

The frozen scorer replay exactly matches the saved result. Scoring the reference
geometry/labels against itself, adding only required display names, gives 100%
geometry and labeling and passes both gates. There is no demonstrated conversion
or internally contradictory scoring ceiling. This self-check does **not** validate
the reference anatomically or measure achievable blind performance.

Earlier retained audits check the original VTK, native affine and original
segmentation. D2 and OM1 have visible local signal in the reference-guided curved
and native views, which I inspected again. The mask and centerlines come from a
shared annotation pipeline, so their agreement is consistency evidence, not an
independent expert vote. Neither this audit nor the earlier one establishes that
GT D2/OM1 are mislabeled tissue. Their difficulty remains distinct from GT error.

The real convention question is R-PDA: the source contains more than one course
under that category, whereas the agent calls one course an inferior RV branch,
label 0. ImageCAS-X allows selected multiple PDA/PLA courses and excludes some
other coronary branches. Thus a broad anatomical inventory and this benchmark's
labels do not have a one-to-one mapping. The V4 prompt already says multiple
courses may share a category and warns against discovery-order numbering; merely
repeating these instructions is unlikely to fix the observed behavior.
[Source annotation protocol, Appendix B](https://arxiv.org/html/2608.30404v1#A2).

Quantitatively, the final 646.24 mm reference partitions into:

| Reference length | mm | Fraction |
| --- | ---: | ---: |
| Covered, correct category | 512.45 | 79.30% |
| Covered, different category | 94.92 | 14.69% |
| Missing geometry | 38.86 | 6.01% |

D2, OM1 and the missing portion of OM2 account for **80.2% of missing geometric
length**. Missed upstream branches also shift downstream numbering: 53.68 mm of
reference Other is called D2, and 8.08 mm of reference OM2 is called OM1.

Reference-assisted counterfactuals isolate the size of these effects, without
altering any result:

| Hypothetical label change on unchanged geometry | Correct-label length coverage | Correct-label category mean | Pass? |
| --- | ---: | ---: | --- |
| None, actual output | 79.30% | 54.09% | No |
| Map submitted D2 to Other and submitted OM1 to OM2 | 88.85% | 68.34% | No |
| Also map disputed inferior RV course to R-PDA | 91.03% | 71.12% | No |
| Optimistic perfect-label upper bound on fixed geometry | 93.99% | 75.53% | No |

The PDA dispute accounts for about **2.17 percentage points** of total reference
length here. It cannot explain the much larger plateau. Even perfect labels cannot
make the geometry pass: the gate requires category mean >=90% and **every category
>=80%**, while D2 and OM1 are nearly absent. These are 11 equally weighted
categories; a short missed branch matters as much as a long main artery.

The fixed nearest-geometry matching rule contributes some boundary sensitivity.
Allowing any correctly labeled course within 1 mm instead would raise labeled
length coverage from 79.30% to 81.50%. That alternative is more permissive and can
reward overlapping guesses, so it is a diagnostic, not a proposed retrospective
score change. It still cannot explain or repair the discovery misses.

## Compute accounting correction

The resumed Harbor result reports 135129 output tokens, but that is the session's
cumulative terminal counter, **including the original run**. Do not add it to the
original run's token count as if all those tokens were generated after resume.

| Counter | Initial | Added after resume |
| --- | ---: | ---: |
| Terminal output-token counter/delta | 108825 | 26304 |
| Sum of distinct response usage records, including compaction | 116001 | 33747 |
| Reasoning-output tokens in usage records | 68248 | 11837 |
| Input tokens in distinct usage records | 16314264 | 3993137 |
| Cached input tokens in those records | 15630720 | 3854464 |

Two compaction responses account for the output-counter differences: 7176 tokens
before interruption and 7443 after resume. These are reported usage measures, not
a billing receipt; input counts repeatedly include context, and cached tokens are
a subset of input tokens. The previous weekly-quota change was account-wide and
must not be assigned to this attempt.

V3 medium took 46m34s, versus 4h13m52s combined here: about 5.45 times the wall
time, not 5.45 times measured useful compute. Prompts, effort and interruption
also differ. More completed inventory/QA work and unchanged coronary coverage can
both be true; this single case is not a controlled test-time-scaling study.

## Concrete fixes to pursue

The new scripts fix the **diagnostic blind spot**: we now retain a reproducible
stage-by-stage account of why candidates disappear, exact output diffs, incremental
token accounting and score sensitivities. They do not change the solver or GT.
No new trial was launched.

For the extraction workflow, the next revision should:

1. **Keep a candidate ledger instead of silently dropping fragments.** Save
   threshold, component/branch size, nearest-parent distance, rejection reason,
   images reviewed and final disposition. Treat a weak disconnected component as
   an unresolved candidate requiring connection search, not proof of absence.
2. **Split large skeleton components into branch paths before selection.** Use
   multiple feature thresholds; rank weak/disconnected paths for bounded
   HU/vesselness-based reconnection and image review. A connection still needs
   image support; relaxing the gap cutoff must not automatically invent a vessel.
3. **Challenge consequential rejections.** For a candidate that would change
   branch numbering, require continuous parent-junction inspection and two
   complementary candidate-centered views. Compare arterial, venous and tissue
   hypotheses; retain uncertainty explicitly. A coarse projection and an old
   interpretation should not be the stopping condition.
4. **Reserve coronary review capacity before expanding inventory.** Record
   unresolved branch decisions and checkpoint actual coronary changes. After a
   plateau, spend the reserved budget on these decisions or stop with an honest
   uncertainty record. Extra pulmonary courses cannot improve coronary scoring.
5. **Adjudicate reference conventions separately.** Have an appropriate reader
   resolve the disputed PDA course and key junction boundaries on native CTA.
   Publish any resulting reference revision separately and re-evaluate all
   methods symmetrically. Do not delete difficult branches to raise the score.

A useful next experiment compares the original workflow against this revised
candidate-review workflow under the same model, effort, scope and token budget,
on fresh source-confirmed cases. This known case can serve as a declared
engineering regression case, not a new blind capability result. A guided rescue
on this case would be a separate assistance diagnostic. These are assistant
recommendations, not user approval to launch.

## Evidence and reproduction

- [Structured trace/score audit](trace-audit.json), [read-only audit script](trace_audit.py).
- [Exact candidate-filter replay and sensitivity](candidate-funnel.json), [script](candidate_funnel.py).
- [Original completed-resume review](review.md), [original evaluation](evaluation.json).
- [Prior source-branch audit](../../../../../docs/research-rounds/BR-042-v3-branch-review.md).
- Local observable trace: `runs/br042-resume-trace-audit-20260921/observable-trace.json`.
- Source session: `runs/br042-all-vessels-astra-xhigh-v4-6h-resume1/all-vessels__cr5kdch/agent/sessions/2026/09/20/rollout-2026-09-20T12-06-18-01a0beb5-c558-7ec2-b58b-d92f1e6818f2.jsonl`.
  Key tool-call lines: 333, 430 (pre-resume candidate review); 1340, 1356
  (pulmonary changes); 1441 (loop fix); 1471, 1480 (candidate regeneration/list);
  1498 (atrial addition); 1545 (rebuild); 1609 (final validation).
- Local figure: `runs/br042-resume-trace-audit-20260921/bottlenecks.png`, generated
  by [render script](render_trace_audit.py); the tables above are the static fallback.

Run each script with `.venv-br030/bin/python` from the repository root. Required
raw artifacts remain local. The audit hashes its retained sources and checks all
frozen task bytes; it never imports historical authoring modules or changes their
outputs. Reference-assisted relabeling is in-memory only. Clinical reference
validity and broader-vessel correctness remain unadjudicated.
