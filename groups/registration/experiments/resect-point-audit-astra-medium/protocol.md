# RESECT standard/challenge point audit — Astra medium

## Question and method

Can one fresh `openai/gpt-6-astra` / `medium` agent improve a shared-navigation
MRI-to-ultrasound point correspondence when displacement is substantial without
overcorrecting an already-close point? The user selected one standard and one
challenge case on 2026-09-22. This is a diagnostic two-query pilot, not task
promotion, population validation or a general model ranking.

## Inputs and reference

One frozen task contains two neutral case labels. Case A is source Case 1,
published MRI-to-pre-resection-US landmark index 1 (zero-based), whose initial
same-world-coordinate error is 1.036 mm. Case B is source Case 3, landmark index
12, whose initial error is 9.574 mm. Selection occurred before inference: both
points were the published landmarks nearest the paired evaluator-only tumor-mask
centroids and already illustrated in the task brief.

The solver receives the complete native FLAIR and pre-resection US NIfTI volumes,
the MRI world coordinate and the identical initial US world coordinate for each
case, plus a generic tool that renders orthogonal native-array views around any
requested MRI/US world coordinates. It receives no source dataset/case names,
tag files, tumor masks, paired reference coordinates, reference-centered crops,
other landmark counts or prior outputs. The task image allows only model-service
transport; additional retrieval and pretrained weights are unavailable.

The private reference is the exact paired US coordinate from the pinned MNI tag
file. Primary descriptive metrics are final 3D target-registration error, absolute
and relative improvement over the fixed no-op, whether each case improved, and
movement magnitude. Harbor reward checks only artifact validity. Oracle must pass
and no-op must fail the artifact contract before the model launch; these controls
do not establish task difficulty. The diagnostic model run gets one attempt,
3,600 agent seconds, four configured CPUs, 8 GiB memory and no GPU or retry.

## Findings and limits

The oracle passed and no-op failed the artifact contract on task digest
`d36a43d256a590d6756b09c8fc3cb480e1b32bc14e4641ef68e2f6dadde04c8d`.
An initial model dispatch received an empty credential and ended with HTTP 401;
it is retained as an infrastructure exclusion. The one scientifically eligible
authenticated attempt completed normally, passed the artifact contract and kept
the frozen payload unchanged.

Astra retained Case A's supplied point: its target-registration error remained
1.036 mm. For Case B it moved 10.640 mm to `[-30.7, 14.4, 14.4]`, reducing error
from 9.574 to 1.130 mm (8.444 mm, or 88.2%, improvement). Mean error across the
two preselected points fell from 5.305 to 1.083 mm. Independent saved-output
replay reproduced the verifier metrics byte-for-byte.

This supports a qualified capability finding on these two public training cases:
the agent avoided overcorrecting the already-close point and substantially repaired
the larger displacement. It does not establish unseen-data performance, robustness,
calibrated confidence or a population estimate. The challenge selection used
evaluator-only masks before inference, foundation-model exposure is unknown, and
the agent's exploratory local correlation helped choose the Case B candidate even
though its final rationale also cited visual correspondence.
