+++
schema_version = 2
kind = "idea"
id = "resect-mri-us-correspondence"
group_id = "registration"
title = "Audit MRI-to-intraoperative-ultrasound correspondences"
idea_state = "exploring"
source = "chatgpt-conversation://6ab15587-d73c-83ee-a5d8-d5defad31b8d"
+++

# Audit MRI-to-intraoperative-ultrasound correspondences

Can an image-reasoning agent identify or repair homologous anatomical points between pre-operative FLAIR MRI and pre-resection 3D ultrasound without relying on shared world coordinates?

## Prior findings

RESECT provides pre-operative T2-FLAIR MRI, tracked pre-resection 3D ultrasound
and 15 paired MRI-to-US landmarks for each of Cases 1–3. A bounded local sample
retains those full volumes, the paired MNI tag files and separate RESECT-SEG
tumor masks. The masks are reader/helper context, not registration truth.

The natural shared-world-coordinate no-op is materially different across these
three cases: its mean target error is 1.82 mm for Case 1, 5.68 mm for Case 2 and
9.58 mm for Case 3. Thus Case 1 is mainly a preservation/control case, while
Cases 2–3 leave more correction to recover. This is source characterization,
not evidence that an image-reasoning agent can improve the correspondences.

The proposed first task is point-wise correspondence audit: show the complete
FLAIR and pre-resection US volumes, mark one MRI reference point and the same
world coordinate as the initial US candidate, then ask the agent to retain or
move the US point. Score final target-registration error against the evaluator-
only paired tag point and compare against the no-op baseline. A mask-assisted
condition may expose the two tumor masks; it narrows region search but does not
identify the homologous point.

One Astra/medium diagnostic trial has now exercised a related two-query,
world-coordinate-output contract on a preselected
Case 1 preservation point and Case 3 challenge point. It retained the 1.036 mm
Case 1 candidate and reduced the Case 3 error from 9.574 to 1.130 mm. The exact
saved-output replay matched, while an earlier empty-credential dispatch remains
an infrastructure exclusion rather than a model result. This is a promising
two-point capability observation, not a task qualification or generalization claim.

## Reopen when

Before promotion, expand to multiple preregistered landmarks and held-out cases,
define collateral-movement and case-level aggregation rules, compare image-only
reasoning with intensity/registration baselines, and audit whether public training
exposure or shared affine geometry makes any condition too easy. Keep published
US landmark coordinates evaluator-only.

## Presentation checkpoint — 2026-09-27

Assistant source audit: all 15 staged files match the acquisition manifest; all
45 tag pairs reproduce the recorded shared-frame baseline. NIfTI image sforms
and valid US-mask qforms agree within 0.000031 mm at volume corners. The
[canonical story](../presentation/stories/resect-point-correspondence.story.md)
keeps same-query-centred views separate from older independently GT-centred
figures, optional tumor masks separate from paired-point references, and this
three-case voxel-output proposal separate from the
[two-query world-output pilot](../presentation/briefs/tb3-resect-point-pilot.md).
These are presentation/source checks, not a new trial or a user study decision.
Reopen protocol design under the existing conditions above.

## Context reassessment — 2026-09-27

Assistant audit: the frozen instruction supplies Case B `[-30,15,15]`,
**0.505444 mm** from the private reference versus **1.130199 mm** for the
returned point. Trace steps 5, 18 and 19 establish prompt delivery and viewing
of that candidate. The later correlation search is centred on the original MRI
query, so the cue's causal necessity is unresolved. The historical distances
and outcomes remain unchanged; the earlier capability interpretation is narrowed
to a descriptive result with this cue present. It does not establish unaided
recovery or superiority to all supplied cues. Original no-op failure was a missing
artifact, not a valid unchanged-coordinate prediction. See the
[scoped report](../findings/resect-point-audit-context.md) and its pinned proof. Reopen unaided capability only with
a separately authorized prompt-neutral revision and preregistered points; this
presentation audit runs no trial. This is an assistant assessment, not a user decision.
