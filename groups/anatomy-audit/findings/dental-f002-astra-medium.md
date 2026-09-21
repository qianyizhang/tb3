# F002 Astra/medium: completed CT-only segmentation

2026-09-21 · [User task](codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f)
· [Protocol](../experiments/dental-f002-astra-medium/protocol.md)
· [Hashed evidence](evidence/dental-f002-astra-medium.json)

The single authorized F002 attempt completed voluntarily after **945.87 seconds
(15m46s)**. It saved a full-grid integer-label segmentation and method notes;
geometry/label checks passed, with no execution exception. Independent offline
replay exactly reproduced every private metric. The original answer is unchanged.

| Observed metric | Value |
| --- | ---: |
| Original mean per-label Dice | 0.0496408765 |
| Foreground Dice, ignoring identity | 0.8744514676 |
| Fixed left/right ID permutation, diagnostic only | 0.4633789236 |
| Predicted / reference nonbackground IDs | 48 / 56 |

The same laterality disagreement remains visible. The fixed permutation is a
post-hoc confusion-matrix diagnostic, not an accepted revised score or output
correction. F002 also independently noted that low slice indices show maxilla and
high indices show mandibular base, despite the archive header's superior-positive
third axis. It preserved that header and assigned left/right from its affine.
No operator supplied orientation advice. Source orientation and semantic-side
conventions require adjudication before attributing all identity errors to the
agent. This observation does not prove the clinical GT is wrong.

There are substantial limitations beyond the side convention. All five canal IDs
(3, 4, 103, 104, 105) are empty in the output despite being populated in the GT.
The agent explicitly abstained because it could not resolve continuous bounded
canals. Original Dice is 0.8484 for lower jaw, 0.7432 for upper jaw and 0.9240 for
pharynx. Implant Dice is 0.5430. The agent predicted 62,073 bridge-label voxels
where GT has none; its crown mask has zero same-ID overlap. These describe
reference disagreement, not an adjudicated diagnosis of restoration type.
Tooth numbering and pulp boundaries also differ, particularly around restored
regions. Foreground overlap should not be interpreted as full semantic accuracy.

The method uses local thresholding, connectivity, morphology, slice-interpolated
tooth envelopes, nearest-envelope partitioning and conservative pulp extraction.
It reports uncertainty from metal streaks/blooming, missing teeth, restored roots,
thin bone and truncated field of view. These are the agent's observations; no
expert clinical adjudication is claimed. Its prediction is an exploratory result.

## Access, cost and completion

The retained session contains 37 top-level exec calls. Inspection found no
external dataset requests or GT/scorer reads. The proxy accepted 52 CONNECT
requests, all to chatgpt.com; it rejected four CDN and 16 telemetry-subdomain
requests. Live launch isolation was verified. This is bounded observed-access
evidence and does not inspect encrypted payloads or exclude public-data pretraining.
Neither F018 output, GT-derived findings nor scoring feedback was supplied.

Reported cumulative tokens: 2,005,006 input, including 1,920,512 cached input
(84,494 uncached), and 24,096 output. No monetary cost is available. These are
per-call totals, not unique input context. Account remaining was 89% at review;
shared-account percentages cannot be assigned solely to this run.

F018-xhigh and F002-medium are both terminal-reviewed; no retries, extensions or
additional cases were dispatched. See [F018 effort comparison](dental-f018-effort-comparison.md).
F002's lower diagnostic overlap is consistent with greater difficulty for this
attempt, but the different cases/class inventories and one attempt per condition
do not establish a general difficulty ranking. Monitoring closes after this review.

Raw answer/method: `.local/attempts/attempt-4338cd3dae024fc8/job/task__UYKc23A/artifacts/app/answer/`.
Replay, native-slice visual, access audit and diagnostic:
`.local/dental-f002-astra-medium/`. Preserve all original frozen evidence.
