# CT alone: ten organ identities, uneven contour accuracy

2026-09-21 · [User task](codex://threads/01a0c38d-fcff-7670-9ac7-80d0ca352c35)
· [Protocol](../experiments/ct-organ-segmentation-astra-xhigh/protocol.md)
· [Evidence receipt](evidence/ct-organ-segmentation-astra-xhigh.json)

One fresh Astra/xhigh attempt produced all ten masks from CT alone in
**1,264.346 agent seconds (21 minutes 4 seconds)**, finishing voluntarily before
the two-hour ceiling. All masks have binary values and the exact CT grid.

Frozen **semantic macro Dice is 0.7380252178**. One-to-one matching without label
constraints gives exactly the same score: all ten masks match their intended
organs, without label swaps. This supports segmentation and naming on this case,
with substantial contour limitations. Correct matching does not establish correct
anatomical ownership of every voxel.

| Organ | Dice |
| --- | ---: |
| Spleen | 0.9076 |
| Right kidney | 0.7974 |
| Left kidney | 0.8152 |
| Gallbladder | 0.6671 |
| Liver | 0.9269 |
| Stomach | 0.7812 |
| Pancreas | 0.7279 |
| Right adrenal | 0.3879 |
| Left adrenal | 0.6070 |
| Duodenum | 0.7620 |

Foreground-union Dice is 0.9011, precision 0.9104 and recall 0.8919. Larger organs
dominate these measures. Right-adrenal output volume is about 40% of reference
volume and its recall is 27%; left-adrenal recall is 48%, gallbladder recall 53%.
These are discrepancies against the reference, not clinically adjudicated errors.

## Fairness and evidence

Original TotalSegmentator small v2.0.1 case s1233 provides all ten reference masks,
internal to the field of view. Complete labels means this fixed taxonomy, not
every visible structure. Independent masks preserve the source overlaps. Source
residual errors remain possible; author triplanar QC is not independent clinical
adjudication. A different candidate was rejected before any model result because
reference completeness was uncertain.

The solver received CT, fixed organ definitions, orientation and output rules.
No masks, source/case IDs, pathology hints, expected volumes, scores, method
suggestions or pretrained segmenter weights were supplied. Live checks verified
the pinned image, internal network and absence of source/repository/GT/socket
mounts. Ordinary per-attempt log mounts remained. Public-data memorization and
opaque model-service traffic cannot be ruled out.

Actual Harbor oracle/no-op controls scored 1/0 on the exact frozen task. Offline
label permutations distinguish semantic errors from geometry. Parent replay of
the unchanged saved masks exactly reproduces every verifier field. There was no
retry, extension, modified score or invented clinical pass threshold.

## Method and scope

The saved method describes visually chosen axial contours, signed-distance
interpolation, mild smoothing, local intensity-based boundary trimming and
multi-plane refinement. Submitted scripts and trace review are retained separately
from the score; source masks were not supplied to the solver.

The full trace contains 37 image-view calls over 36 unique images and 42 local
commands, all successful. No external retrieval, additional pretrained segmenter,
reference-mask access or scorer call was observed. All 59 allowed transport
connections went to chatgpt.com; 26 CDN/telemetry connections were denied. Image
observations are retained in the rollout/trajectory rather than CLI stdout.
Final small adrenal/stomach edits had structural validation but no fresh overlay;
explicit renal-cyst subtraction was not evidenced. This narrows the submitted
method's review claims without changing the score.

Total trial time was 1,307.910 seconds; verifier time 19.669 seconds. Harbor records
2,468,203 input tokens (including 2,375,424 cached) and 33,537 output tokens. These
are cumulative counts, not unique context size. Dollar cost was unavailable;
author/operator effort is separate. The 12 GiB container cap was not guaranteed
RAM: the Docker VM had approximately 7.74 GiB total. Execution completed normally.

One selected public case establishes neither a population success rate nor a model
ranking. This bounded study ends after one attempt. The protocol provides source
hashes/acquisition, runtime transfer, preparation and standalone scoring. External
directory preparation and replay were checked on this machine; upstream ZIP
redownload and independent-machine runtime transfer remain untested. Original
evaluator-only bytecode remains in the freeze; maintained controls no longer
create it or mutate prepared task bytes.

Local figures:

- [Per-organ scores](../../../.local/ct-organ-segmentation-astra-xhigh/review/organ-dice.png)
- [CT, GT and agent contours](../../../.local/ct-organ-segmentation-astra-xhigh/review/organ-contours.png)

Contour panels use each organ's largest-GT-area axial slice and identical crops;
they illustrate selected planes, not full 3D adjudication. Regenerate with
`authoring/render_review.py --task TASK --answer MASKS --metrics JSON --output DIR`.
