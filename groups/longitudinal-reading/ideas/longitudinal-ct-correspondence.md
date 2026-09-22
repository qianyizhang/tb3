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
