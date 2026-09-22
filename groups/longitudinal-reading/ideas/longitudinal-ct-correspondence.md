+++
schema_version = 2
kind = "idea"
id = "longitudinal-ct-correspondence"
group_id = "longitudinal-reading"
title = "Track lesion identity across CT visits"
idea_state = "exploring"
source = "codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5"
+++

# Track lesion identity across CT visits

Can an agent discover, segment and link lesions across paired CTs without supplied masks?

## Prior findings

User requested bounded case acquisition, data/GT review and illustrations on
2026-09-22, following [Medical Image Reasoning Tasks](chatgpt-conversation://6ab15587-d73c-83ee-a5d8-d5defad31b8d).
This authorizes the sample review, not a model trial or task promotion.

Four Longitudinal-CT v3 patient pairs were acquired by ZIP member range requests;
300 small patient CSVs were screened. Three illustrate correspondence, merging,
new labels and disappearance; a fourth facial case is held for image/reference
review because defacing compromises interpretable original appearance. No model
runs or clinical adjudication were performed.

- [Review, exact cases, source terms and limitations](../examples/longitudinal-ct-review-20260922.md)
- [Proposed Task Brief](../presentation/briefs/longitudinal-ct-correspondence.md)
- [Geometry and source-file audit](../examples/longitudinal-ct-review-20260922.json)
- Local interactive reader: `.local/longitudinal-ct-review/review/index.html`.

Assistant recommendation, 2026-09-22: start with full baseline/follow-up CT and
marked baseline targets, requiring follow-up localization and a correspondence
graph allowing many-to-one links. Separate whole-volume new-lesion search. Compare
a fixed registration/matching baseline and a condition with both masks supplied,
with independent label permutation. The source's IDs and `inputsTr` metadata can
otherwise disclose the answer. This recommendation is not a user trial selection.

## Reopen when

Before freezing a trial, adjudicate selected image/reference pairs and comparable
coverage, resolve missing/unclear linking flags, establish coordinate conversion,
choose patient-disjoint development/evaluation cases, implement group-aware scoring
and verify an explicit solver file allowlist. Decide whether segmentation is an
endpoint or only follow-up localization is required. Set numerical tolerances only
after reference review. Obtain a separate explicit request to run agents.

## User-selected image-only comparison — 2026-09-22

The user explicitly selected full CT pairs with no masks or case-specific lesion
context, requiring native instance masks and evaluatable links/events; run Astra
medium and Sol xhigh. The generic invented format example is not an annotated
example. Localization, segmentation and association are independent endpoints.
Decision: `decision-af91b921939e40bd`, actor=user.

Assistant implementation: first compare both models on the same reviewed pair,
one independent attempt each, up to two hours, with references isolated and no
external dataset retrieval. This is a bounded exploratory study.

- [Astra medium protocol](../experiments/longitudinal-ct-image-only-astra-medium/protocol.md)
- [Sol xhigh protocol](../experiments/longitudinal-ct-image-only-sol-xhigh/protocol.md)
- [Shared generic instruction](../methods/longitudinal-ct-image-only/instruction.md)

A scoped instance-convention question was recorded during the first attempt:
source baseline labels 1/2/4 touch, while the generic prompt says a confluent
region is one instance. Connectivity is not clinical adjudication. Both model
experiments remain under review for fine-instance/event interpretation; frozen
inputs and scores are retained. [Boundary review](../examples/longitudinal-ct-instance-boundary-review.md).

Completed comparison: Astra medium captured the dominant abdominal region but
localized 2/6 fine GT instances; Sol xhigh submitted empty masks (0/6). Both
completed normally with valid artifacts, and independent replay reproduced every
original score exactly. Astra linked its one eligible reference edge correctly;
end-to-end recovery remains incomplete. This is one case, not a model ranking.
[Results and native illustrations](../findings/longitudinal-ct-image-only-comparison.md).

Assistant recommendation: retain image-only inputs, clarify distinguishable
touching-lesion conventions before a new frozen task, and review further pairs
with independent event types. No extra attempt was launched from this recommendation.

## User-requested trace attribution — 2026-09-22

The user requested reconstruction of both methods and attribution among model
capability, genuine task difficulty and instruction ambiguity. The
[trace audit](../findings/longitudinal-ct-trace-attribution.md) and finding
`longitudinal-ct-trace-attribution` retain exact step excerpts and source hashes.
Astra's single baseline mask covers 73.1%, 99.8% and 93.3% of the three abdominal
GT labels: under-separation contributes to its instance false negatives. The
separate focus is entirely omitted. Sol's retained breast candidates overlap no
GT; its final empty output reflects candidate interpretation and acceptance,
not failed file generation. Its scanner-coordinate pairing does not establish
anatomical registration. Neither attempt isolates complete event reasoning.

Assistant recommendation: clarify distinguishable touching lesions and the
generic uncertain-lesion inclusion policy, retain raw CT pairs as the primary
condition, and use separately reported component controls only if selected.
Instruction causality and expert reference partition remain unadjudicated.
No new model attempt, prompt revision, reference edit or score replacement was
performed by this analysis.

## User-selected instruction revision — 2026-09-22

Decision `decision-390f683cedae46ef`, actor=user: revise the generic instructions,
run Astra medium again, and conditionally run a narrower attribution test if
lesions remain missed. The [v2 protocol](../experiments/longitudinal-ct-v2-astra-medium/protocol.md)
preserves all images, references, scorer, runtime and budget; only generic
touching-instance and uncertain-lesion inclusion wording changes. A fresh attempt
receives no prior output or lesion-specific hint. The separately declared
localized test supplies candidate centers only if substantial lesion omission
persists; it is not scored as whole-volume discovery. Reference partition
adjudication remains open, and prompt causality cannot be established from one
original versus one revised attempt.

Completed selected work: revised Astra medium recovered 3/6 strict instances and
2/4 reference edges, versus 2/6 and 1/4 originally, but still zero complete event
groups. The separate focus retained 0% coverage at both visits, triggering the
declared fresh localized probe. With exact centers and no diagnosis/masks, the
agent inspected native axial and orthogonal views and judged both candidates
normal/benign (0/2 accepted). The remaining failure is not whole-volume search
alone; it includes recognition/inclusion disagreement with the positive reference.
This does not adjudicate the anatomy, clinical malignancy or image-only reference
suitability, and rejection leaves conditional contouring ability untested.
[Results, trace evidence and native illustrations](../findings/longitudinal-ct-v2-and-localized.md).

Assistant recommendation: expert review of the indicated source-positive focus
and image-only target suitability before additional model comparisons. If
confirmed, a known-positive point segmentation control could isolate boundary
construction but would explicitly supply positivity. No further trial is selected
or launched; original scores and source labels remain unchanged.

## User-selected second case — 2026-09-22

Decision `decision-7736bd9e5cb1412d`, actor=user: review source documentation and
GT statistics, select/download another suitable case, and run one fresh
Astra-medium attempt (explicit follow-up selection). The assistant's
[selection review](../examples/longitudinal-ct-case02-selection.md) retains the
300-patient metadata screen, six eligible cases, acquisition hashes and native
geometry checks. The selected new case has seven persistent and eight new
reference groups, mostly liver, with no touching distinct mask IDs. Preserve all
22 present instances. No model outcome informed this patient's selection.

The source card explicitly says annotators used clinical reports, while the
retained primary contract is CT-only. This is a deliberate information gap and
limits diagnostic interpretation. The exact revised v2 instructions/scientific
scorer are reused; no organ/count/location/event hint or clinical context reaches
the solver. Foreground overlap, equal-lesion scores, size strata and new-event
recovery are separated because one large lesion dominates total volume.
[Protocol](../experiments/longitudinal-ct-case02-astra-medium/protocol.md).

The second-case attempt completed normally in 17m02s, with valid outputs and
exact saved-score replay: 3/22 strict instance matches, 1/7 links, 2/15 exact
events (one persistent, one new). Foreground Dice 0.799/0.891 is dominated by
the large lesion; equal-instance Dice is 0.107. No <=1 mL instance was localized.
A reported follow-up vessel exclusion at (190,235,536) lies inside source GT14,
providing a concrete recognition/inclusion disagreement for one missed target.
All 22 survey panels were requested, but this does not isolate attention versus
recognition for the other omissions. Correct conditional associations do not
establish complete event reasoning. Source context and clinical adjudication
limitations remain; no labels or original scores were revised and no localized
follow-up was launched. [Full result and CT evidence](../findings/longitudinal-ct-case02-astra-medium.md).
