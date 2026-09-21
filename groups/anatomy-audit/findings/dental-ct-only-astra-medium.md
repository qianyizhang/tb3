# CT-only Astra/medium: completed, with unresolved side convention

2026-09-21 · [User task](codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f)
· [Protocol](../experiments/dental-ct-only-astra-medium/protocol.md)
· [Hashed evidence receipt](evidence/dental-ct-only-astra-medium.json)

Astra/medium completed a single independent F_018 segmentation attempt in
947.10 seconds (15 minutes 47 seconds), finishing voluntarily before the two-hour
ceiling. The saved integer NIfTI preserves the CT dimensions and affine and uses
allowed IDs. No evaluator exception occurred. An earlier authentication-only
invocation remains separately recorded and produced no model work.

## Frozen result and interpretation

The original private macro Dice is **0.0393942826**. Independent offline replay
of the unchanged answer exactly reproduces every verifier metric. Binary
foreground Dice is **0.9686094251**, which ignores semantic identity and is
dominated by large structures; it is not overall anatomical accuracy. Original
class Dice: lower jaw 0.9413, upper jaw 0.7810, pharynx 0.9769, lingual canal
0.0566. Most lateralized classes have zero same-ID overlap.

The output contains 66 nonbackground IDs; the reference contains 68. Astra
segmented 29 tooth/pulp pairs, both jaws, sinuses, pharynx, bilateral inferior
alveolar canals and a small lingual canal. It explicitly omitted the two incisive
canals because it could not distinguish them confidently. It assigned the
impacted posterior tooth ID 48 where the reference uses 38.

There is a systematic **left/right identity disagreement**, not a mirrored array:
the same spatial objects overlap but carry opposing IDs. A fixed anatomical
left/right permutation, applied only to the confusion matrix, yields diagnostic
macro Dice **0.6924568797**. This is post-hoc analysis, not a corrected answer,
replacement score, passing result or permission to change the frozen outcome.
Under that permutation canal Dice remains low (0.214 and 0.154), so the side
disagreement does not account for all segmentation limitations.

The viewer NIfTI header has LPI axis directions, and Astra explicitly follows
increasing first index as patient-left. Yet the reference's upper-right incisor
(11) has first-index centroid 214.32 and upper-left incisor (21) 190.23; Astra's
corresponding centroids are 189.22 and 213.63. Analogous opposition occurs in the
canals and sinuses. This raises a **source-header/semantic-side convention issue**.
Technical pair alignment alone did not establish that laterality is correct.
Do not assign the discrepancy solely to the model or declare the clinical GT
wrong without checking authoritative acquisition orientation/source conventions.
This interpretation remains under review; original scores are retained.

## Method and access audit

The agent independently chose local classical image processing: intensity
thresholds, connected components, morphology, visually chosen tooth regions,
interpolated trajectories and constrained minimum-cost paths for canals. It
generated axial/coronal/sagittal and curved views and documented uncertainty.
No pretrained segmentation weights were available in this condition.

The saved session has 35 top-level exec calls. Inspection of retained calls found
no dataset retrieval, GT/scorer read, or external website request. Proxy logs
contain 50 accepted CONNECT requests, all to chatgpt.com; four model CDN and
16 telemetry-subdomain connections were rejected. Live isolation evidence shows
the pinned image, one internal network, dropped capabilities and only this
trial's log mounts. These support bounded absence of observed retrieval; they do
not prove that public data was absent from model pretraining or inspect encrypted
traffic. No score or method feedback was supplied during the attempt.

Reported tokens: 2,089,202 input, including 1,984,512 cached input, and 24,304
output (9,192 reasoning tokens included in output). Input is cumulative across
calls, not unique context. Uncached input is 104,690. Monetary cost was not
reported. Account remaining was 94% at terminal review versus 95% at launch;
that rounded shared-account change is not attributable trial cost.

## Retained artifacts and next boundary

Raw answer and method:
`.local/attempts/attempt-21af29aaf8034aa6/job/task__g7iAZDR/artifacts/app/answer/`.
Replay, confusion-matrix diagnostic, native-slice comparison and access receipt:
`.local/dental-ct-only-astra-medium/`. The original segmentation was not modified.

Supervision closes after this review; no replacement, continuation, extension or
second case is dispatched. Resolve the header/label laterality convention before
using this result to compare anatomical identity performance or promoting a new
trial. Reference disputes require appropriate adjudication; any subsequent
corrected fixture or score must be separately versioned.
