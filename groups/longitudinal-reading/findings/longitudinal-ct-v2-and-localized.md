# Revised image-only instructions and localized recognition

2026-09-22 · [User request](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5)
· [Original comparison](longitudinal-ct-image-only-comparison.md)
· [Prior trace attribution](longitudinal-ct-trace-attribution.md)

**Result:** clarified instructions were followed by finer abdominal partitioning
and more recovered links, but the separate reference focus remained entirely
omitted. A fresh localized probe examined the exact supplied centers and rejected
both as normal/benign. This identifies a recognition/inclusion disagreement with
GT beyond whole-volume search; it does not adjudicate the anatomy or malignancy.

## What changed

The user selected a fresh Astra-medium attempt with clarified generic instructions,
followed by a narrower diagnostic if lesion omission persisted. The full-volume
task changes **only `instruction.md`**. CT bytes, reference masks/events, output
format, scorer, model/effort, tools, Docker images and two-hour allowance are the
same as the first attempt. New freezes and independent sessions preserve the old
task and outputs. No previous answer, score or case-specific hint reaches the
whole-volume solver.

The [revised prompt](../methods/longitudinal-ct-image-only-v2/instruction.md) adds
two rules: distinguishable touching lesions retain separate IDs, and findings
judged more likely tumor than normal/benign tissue are included without requiring
diagnostic certainty. Findings judged more likely normal/benign are excluded;
uncertain candidates require coordinates and an inclusion/exclusion reason.
Zero lesions remains allowed. These are generic annotation instructions, not
disclosure of this patient's lesion count, locations or event type.

## Whole-volume result

| Endpoint | Original Astra medium | Revised Astra medium |
| --- | ---: | ---: |
| Valid artifact contract | Yes | Yes |
| Strict instance localization TP / FP / FN | 2 / 0 / 4 | 3 / 0 / 3 |
| Foreground Dice, baseline | 0.68480 | 0.68466 |
| Foreground Dice, follow-up | 0.77921 | 0.76431 |
| GT-macro instance Dice | 0.23445 | 0.33532 |
| Correct end-to-end links | 1/4 | 2/4 |
| Exact typed event groups | 0/2 | 0/2 |
| Conditional link recovery | 1/1 eligible | 2/2 eligible |
| Complete reference event-group eligibility | 0/2 | 0/2 |
| Agent execution time | 17m 05s | 18m 48s |

The revised attempt (`attempt-4749bbfb347f4809`) completed normally, produced
valid artifacts, and all scores independently replay exactly. It distinguished
two baseline abdominal components and linked them to one follow-up region as
merging. In its report it explicitly distinguishes certainty about the presence
of abnormal tissue from uncertainty about subdivision. The original attempt had
treated the region as one persistent instance at each visit.

This is improved strict instance/link recovery, not improved foreground overlap
or complete recovery. Both wording changes and a fresh stochastic attempt differ;
one original versus one revised run cannot establish a causal prompt benefit.
Expert adjudication of the fine reference partition remains open. The revised
model's two baseline masks still do not reproduce the three reference abdominal
instances. The fixed centroid-based localization rule maps them to source B2/B4;
source B1 retains 62.2% foreground coverage despite lacking a separate matched
instance. Do not interpret every unmatched instance as unseen tissue.

| Reference region | Original foreground coverage | Revised foreground coverage |
| --- | ---: | ---: |
| Baseline 1 | 73.1% | 62.2% |
| Baseline 2 | 99.8% | 94.5% |
| Baseline 4 | 93.3% | 80.5% |
| Follow-up 4 | 93.7% | 83.4% |
| Separate focus, baseline 3 | 0% | 0% |
| Separate focus, follow-up 3 | 0% | 0% |

Coverage is reference-voxel recall and does not penalize extra tissue. The
predeclared narrower-test trigger was <10% coverage for any reference instance,
with persistent groups preferred and volume used to break ties. The separate
focus's complete omission at both visits triggers that test without conflating
the touching-instance convention with lesion discovery.

![Original and revised masks on native CT](../../../.local/longitudinal-ct-image-only-v2/whole-volume/analysis/comparison.png)

These are post-hoc GT-selected maximum-area axial planes and 150 mm crops.
Cyan is reference, amber the original output and purple the revised output;
solid contours and numeric local IDs share each color. Native i points right,
j down; HU window [-160,240]. Neither solver saw GT overlays. Cropped figures
are evidence for these regions, not exhaustive false-positive review.

## Conditional localized test

The [localized prompt](../experiments/longitudinal-ct-localized-astra-medium/instruction.md)
retains the complete raw CT pair and adds only two exact candidate-center native
coordinates: baseline (304,263,213) and follow-up (302,221,216), named R01/R02.
It supplies no masks, diagnosis, anatomical labels, prior results or
guaranteed-positive statement. It asks for `tumor`, `normal_or_benign` or
`indeterminate` judgments, with reasons, and masks/events only for candidates
judged tumor. Other findings are explicitly out of scope.

This deliberately removes most whole-volume search and changes the attention
cue. It is a fresh session, not a correction sent to the earlier agent. The
private reference contains only the selected structures and their association;
original references are not edited. A separate recognition scorer reports
acceptance relative to the positive reference independently of localization,
mask overlap and association. Negative or indeterminate judgments with empty
masks can satisfy the output contract. No negative control is included, so
specificity cannot be estimated.

The localized attempt (`attempt-3756134eb4094e9f`) completed normally in 3m 20s
of agent execution, with ten retained image observations. It produced valid
artifacts; independent replay reproduced every metric exactly.

| Localized endpoint | Result |
| --- | ---: |
| Reference-positive candidates accepted as tumor | 0/2 |
| Rejected as normal/benign | 2/2 |
| Indeterminate | 0/2 |
| Foreground Dice, each visit | 0 |
| End-to-end reference links / typed events recovered | 0/1 / 0/1 |
| Conditional links / complete events eligible for scoring | 0 / 0 |

These are two visits of one selected focus, not two independent lesions. Empty
masks were intentional consequences of rejection, not output-generation failures.
Mask quality conditional on accepting this target remains untested; conditional
association is undefined because no endpoints were detected.

### What the localized agent actually did

It loaded the native CTs, rendered the supplied centers with red ticks, examined
successive axial slices, and produced sagittal/coronal reformats with physical
aspect-ratio correction. The saved code uses `array[:, :, k].T`, placing native
i horizontally and j vertically after crop/scale. Both supplied points are inside
the respective private reference label. The saved center images include the
specified k=213 and k=216 planes, and trajectory step 14 requests both images.
This verifies that the intended structures were presented to the model.

At step 12 it reported tracing a smooth structure through the thoracic inlet.
At step 16 it explicitly judged both candidates more likely normal/benign,
citing smooth elongated shape and continuity with adjacent neck soft tissue.
Its final report favors normal scalene-region tissue with moderate uncertainty
about exact tissue identity. It says exclusion rests on the more-likely-benign
judgment, rather than uncertainty alone, and distinguishes the candidate from
the nearby thyroid. These are **model interpretations**, not author adjudication.
The whole-volume thyroid exclusion was at different coordinates; that earlier
statement alone does not prove recognition of this exact reference lesion.

[Exact saved judgments](../../../.local/attempts/attempt-3756134eb4094e9f/job/task__YeEWgzy/artifacts/app/answer/candidate_judgments.json)
· [Agent report](../../../.local/attempts/attempt-3756134eb4094e9f/job/task__YeEWgzy/artifacts/app/answer/report.md)
· [Baseline center view](../../../.local/attempts/attempt-3756134eb4094e9f/job/task__YeEWgzy/artifacts/app/work/baseline_center.jpg)
· [Follow-up center view](../../../.local/attempts/attempt-3756134eb4094e9f/job/task__YeEWgzy/artifacts/app/work/followup_center.jpg).

![Supplied reference focus remains excluded at both visits](../../../.local/longitudinal-ct-image-only-v2/localized/analysis/comparison.png)

Cyan solid contours are GT. Amber/purple would show revised whole-volume and
localized predictions; both are empty in these regions. Planes and crops were
selected using GT after inference. They were never supplied as overlays to the
agent. The reference focus has 5.4 mL baseline and 7.4 mL follow-up volume;
these dimensions alone do not establish its diagnosis or visibility.

### Failure attribution and next decision

| Explanation | Evidence and remaining limits |
| --- | --- |
| Whole-volume search/attention alone | Insufficient: after exact centers were supplied, the agent inspected and rejected the structures. Search may still contribute to the original omission. |
| Recognition/anatomical interpretation | Directly supported relative to GT: the agent calls the indicated reference-positive tissue normal/benign. This does not establish why the interpretation differs. |
| Conservative uncertainty policy | The new instruction explicitly permits inclusion without diagnostic certainty. The localized report says benignity was favored; this is not simple refusal because certainty was unavailable. |
| Touching-instance ambiguity | Relevant to abdominal partition and merge completeness, not this spatially separate focus. Revised partitioning improves strict matching, while expert fine-boundary review remains open. |
| Segmentation or event reasoning failure | Cannot be isolated for the localized focus: rejection prevents contouring and removes correspondence endpoints. Whole-volume eligible links were both correct, but no complete event group was available. |
| Intrinsic case difficulty or reference suitability | Still unresolved: crowded adjacent anatomy, 3 mm slices and withheld clinical context may matter. This experiment cannot distinguish model misconception from an image-only ambiguity or reference disagreement. |

The current result is a **recognition/inclusion bottleneck relative to this GT**,
not evidence that a better search sweep alone would fix it. The next useful step
is independent expert review of this source-positive structure and whether its
target status is inferable under the image-only contract. If the reference and
image-only suitability are confirmed, a separately reported known-positive point
segmentation task could then isolate boundary construction; it would disclose
positivity and could no longer test recognition. This is an assistant
recommendation, not a selected or launched additional trial.

One adaptive positive-only target cannot estimate specificity, population
performance or a causal prompt effect. No clinical reference or frozen score has
been changed. Two new model attempts were run: the revised whole-volume attempt
and its triggered localized probe. No further dispatch is implied by the
localized analysis script's residual low-coverage diagnostics.

## Controls and provenance

Both new tasks have fresh native oracle/no-op controls, pinned runtime images,
separate private evaluators and live solver isolation checks. Synthetic tests
cover oracle acceptance, negative and indeterminate judgments, missing judgments,
duplicate candidates and invalid judgment enums. Only ordinary model usage is
authorized; no reset credit is used. The shared frozen mask/link/event scorer
remains unchanged; the localized wrapper adds judgment validation and scopes GT.
Both oracle controls passed and both no-op controls failed as expected. Both
model attempts completed without exceptions, retained unchanged frozen payloads,
and passed live isolation checks. Retained trajectories contain 56 whole-volume
and 10 localized image observations (a montage counts as one). Proxy denials are
logged separately; the observed image payloads and responses do not support
classifying these attempts as image-delivery failures.

Whole-volume digest:
`110a8ffd31c0991525ff33800c7a91023bb7cb24cddda518fecd3395f34d75f1`.
Localized digest:
`aeb14dde7d41ffd34bb4dfc83616ade0b1ba8350c9c25a5cbcca046be4671719`.

[Whole-volume preparation](../examples/longitudinal-ct-v2-whole-volume-preparation.json)
· [Localized preparation](../examples/longitudinal-ct-v2-localized-preparation.json)
· [Reproduction methods](../methods/longitudinal-ct-image-only-v2/README.md).

[Machine-readable results, exact trace statements and source hashes](evidence/longitudinal-ct-v2-and-localized.json).
