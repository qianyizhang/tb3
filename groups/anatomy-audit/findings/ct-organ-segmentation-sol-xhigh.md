# Sol/xhigh: valid outputs, substantial organ-localization errors

2026-09-21 · [Comparison protocol](../methods/ct-organ-three-condition-comparison/protocol.md)
· [Evidence and trace receipt](evidence/ct-organ-segmentation-sol-xhigh.json)

The fresh Sol/xhigh attempt completed normally in **1,872.73 agent seconds
(31 minutes 13 seconds)**, without a retry or time extension. All ten masks pass
the structural contract. Independent replay of the unchanged saved outputs
exactly reproduces every verifier field.

Semantic macro Dice is **0.32907**, versus the retained Astra/xhigh pilot's
0.73803. Label-agnostic matched Dice is 0.34878, so an optimal reassignment of
names repairs little of the discrepancy. Geometry/localization remains limiting.
This is a descriptive comparison on one case, not a general model ranking.

| Organ | Sol/xhigh Dice |
| --- | ---: |
| Spleen | 0.77865 |
| Right kidney | 0.67555 |
| Left kidney | 0.76474 |
| Gallbladder | 0.01135 |
| Liver | 0.80537 |
| Stomach | 0.07335 |
| Pancreas | 0.02872 |
| Right adrenal | 0.15300 |
| Left adrenal | 0 |
| Duodenum | 0 |

Foreground Dice is 0.70308, precision 0.60656 and recall 0.83615. The stomach
prediction contains 229,659 voxels versus 25,117 reference voxels, a 9.14-fold
volume ratio. Duodenum and left-adrenal predictions have zero same-name reference
overlap. These failures exceed a small boundary-refinement discrepancy.

The maximum-weight assignment has six correct names among nine positive-overlap
pairs. One zero-overlap pair supplies no identity evidence. Several other assigned
pairs have very low overlap, so this number must not be described as a robust
organ-recognition accuracy or as proof of a simple systematic label permutation.

## What the saved code actually does

Like Astra/xhigh, Sol writes numerical polygon coordinates after viewing the CT,
then interpolates signed-distance fields between axial keyframes. Nine organs
have 5–12 keyframes each. Sol also uses **actual binary closing**, connected-
component filtering and hole filling. Unlike the first Astra pipeline's protected
interior/boundary-only trim, Sol's solid-organ HU interval applies throughout the
polygon envelope.

```python
for solid_organ in solid_organs:
    envelope = interpolate_signed_distances(visual_polygon_keyframes)
    tissue = envelope & (CT >= organ_min_HU) & (CT <= organ_max_HU)
    tissue = binary_closing(tissue, organ_iterations)
    tissue = largest_component(tissue)
    mask = fill_small_axial_holes(tissue) & envelope

stomach = interpolate_signed_distances(stomach_polygons)
gallbladder = interpolate_signed_distances(gallbladder_polygons)
duodenum = union_of_11_hand_positioned_ellipsoids()
apply_selected_organ_exclusions_and_component_cleanup()
save_named_masks_on_original_grid()
```

The duodenum is particularly revealing: its final construction is a union of
eleven overlapping ellipsoids, with manually specified centers and radii. It has
no CT-intensity constraint. Its same-name Dice is zero. This demonstrates that a
connected, plausible-looking geometric object and a valid output file do not
establish correct localization. It does not isolate whether the originating
mistake arose from visual interpretation, coordinate choice or another decision.

The selected post-run overlays show substantial displaced or oversized masks for
several smaller/central organs. They use each reference's largest-area axial
slice and identical crops, and are illustrative rather than full clinical
adjudication. Original reference bytes and scores remain unchanged.

![CT, reference and Sol contours](../../../.local/ct-organ-comparison/sol-xhigh/review/organ-contours.png)

## Trace, isolation and accounting

The complete retained rollout has 86 tool calls: 41 command calls, 16 patches
and 29 image views over 29 unique images. All commands returned exit code zero,
although one package-directory probe used a nonexistent Python3.11 directory and
suppressed its failure. A filesystem weight search returned no candidates;
Torch and MONAI were unavailable. No external retrieval, reference/scorer access
or pretrained segmenter use was observed.

The live main container passed all nine isolation checks on the same pinned
image and exact frozen task as Astra/xhigh. Transport retained 106 allowed
connections to chatgpt.com; 32 telemetry and four CDN connections were denied.
This evidence does not rule out public-data pretraining exposure or opaque
model-service traffic. No prior model answer or feedback was supplied.

The final largest-component changes to liver/stomach/pancreas had structural
validation but no fresh subsequent overlay. Correct affine, filenames, binary
values and side checks therefore coexist with poor anatomical agreement.

Total trial time was 1,937.63 seconds. Token counts were 7,214,819 input, including
7,056,128 cached, and 47,773 output, including 23,524 reasoning tokens. These are
cumulative counts, not unique context size. Harbor reported an estimated cost of
$4.4126752; this is not a billing receipt, and the original Astra/xhigh cost is
unavailable. Author/supervisor effort is separate.

The supervising helper later hit a model-capacity error. That was separate from
this successfully completed solver attempt. The parent adopted the healthy
operator and released the fresh Astra/medium condition after checking terminal
execution, isolation and remaining quota. The completed
[three-condition comparison](ct-organ-three-condition-comparison.md) retains all
original results and documents the shared methodological limits.
