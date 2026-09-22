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

Can an agent recover lesion correspondence and merging from paired CTs after baseline targets are marked?

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
