# Second raw-CT pair — Astra medium

User selection, 2026-09-22: review original dataset documentation/statistics/GT,
choose and download another suitable case, set up a test, and run one fresh
Astra-medium attempt. The run was explicitly selected in the follow-up question.
[Source task](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5).
Decision `decision-7736bd9e5cb1412d`, actor=user.

## Question and selection

Does the same revised image-only task recover distinct non-nodal targets and
new-lesion events in a second patient, beyond the first nodal-merger example?
The [author selection review](../../examples/longitudinal-ct-case02-selection.md)
records the metadata screen and native GT review before inference. Selection is
purposive and informed by the first study, not random or population-representative.
No scores on this new patient informed selection. One complete case is retained;
no difficult reference label is removed or simplified.

The pinned v3 case has 7 baseline and 15 follow-up labels: seven persistent
identities and eight newly appearing groups. Twelve longitudinal rows are liver,
two lymph node, one skeleton. All links are explicitly clear in source metadata;
there are no source merging/disappearing groups or inter-label 6-connected
contacts. One source label has a one-voxel satellite under 6-connectivity;
its original instance ID and bytes are retained. Clinical interpretation is not
adjudicated by this technical author review.

## Frozen solver contract

Use exactly the revised v2 instruction bytes: no source identity, disease,
anatomical distribution, lesion count, event mix, masks, points, prior results,
GT illustrations or clinical reports. Only the complete renamed native baseline
and follow-up CTs are available. Clean identifying NIfTI text/extensions while
checking every voxel and affine is unchanged. Output two native instance masks,
`events.json` and `report.md`, with independent local instance IDs.

One fresh `openai/gpt-6-astra`, reasoning effort `medium`, two-hour ceiling,
4 CPU/12 GiB configured solver ceilings and the existing pinned imaging runtime.
Case-specific data-only solver and separate offline private evaluator images
are built from that runtime. No additional pretrained model or runtime install.
External dataset/model retrieval is blocked by the existing transport design.
Record live mount/network/image checks. Use ordinary account usage only; reset
credits are not authorized. No automatic retry, continuation, or localized test.

## Controls, scoring and interpretation

New native oracle/no-op controls must pass/fail respectively on this fresh digest
before model execution. Run as a diagnostic; source GT uses clinical-report context
that the agent intentionally lacks. This remains an image-only capability study,
not a clean test of clinical malignancy inference or submission qualification.

Retain the exact original mask/link/event scorer and its 3 mm centroid-to-reference
matching rule. Report strict TP/FP/FN, per-visit foreground Dice, equal-GT-instance
macro Dice, conditional mask overlap, links and exact typed event groups, both
end-to-end and conditional on detected endpoints. Newly appearing events are
reported separately from persistence. Contract validity is not scientific success.
No merging/disappearance ability is measured by this case.

Before inference, additionally declare descriptive lesion-size strata: <=1 mL,
>1 to 10 mL, >10 mL, using native GT volume. Report instance localization and
macro Dice per stratum, and covered GT fraction per label. Foreground Dice may be
dominated by one large liver lesion; equal-lesion scores remain essential. Do not
change primary matching, drop labels, or reweight frozen scores after seeing output.

Retain source/cleaned-input hashes, frozen task digest, exact submitted artifacts,
trace and independent saved-output score replay. Inspect whether omissions reflect
unvisited candidates, explicit rejection, under-separation or poor contouring;
image presentation alone cannot establish attention. Disagreements remain source
agreement results pending appropriate expert adjudication. Cross-case score
changes do not establish prompt causality or a model ranking.
