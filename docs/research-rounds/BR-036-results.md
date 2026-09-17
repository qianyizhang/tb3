# BR-036 — semantic landmark results

Two source-order subjects, four frozen conditions, one fresh Terra/high attempt per condition. These are reference-agreement pilots, not clinical validation or a repeatability study.

[Candidate shortlist and protocol](BR-036-semantic-landmarks.md) · [Measured receipt](../evidence/br036-results.json) · [Local comparison panels](../../runs/br036-semantic-landmarks/review/index.html)

| Condition | Accepted targets | Mean / maximum point error | Outside-FOV handling | Agent duration |
| --- | ---: | --- | --- | ---: |
| ct-C001 | 1/4 | 5.77 / 8.22 mm | Not tested | 323 s |
| mri-C001 | 0/8 | 11.18 / 21.13 mm | Not tested | 405 s |
| mri32-crop | 0/32 | 18.70 / 28.03 mm | 0/7 | 347 s |
| ct-crop | 2/4 | 8.83 / 12.03 mm | 2/2 | 260 s |

Point errors above use submitted in-view coordinates; visibility failures and missing points are counted separately. An all-target pass requires every target to satisfy its fixed rule. See the receipt for per-point errors and output status.

## ct-C001

Normal completion: True. Fixed all-target reward: 0.0.

| Landmark | Error (mm) | Output / accepted |
| --- | ---: | --- |
| chin | 8.222 | coordinate |
| mand_r | 5.723 | coordinate |
| mand_l | 6.093 | coordinate |
| odont_proc | 3.041 | coordinate |

## mri-C001

Normal completion: True. Fixed all-target reward: 0.0.

| Landmark | Error (mm) | Output / accepted |
| --- | ---: | --- |
| AC | 7.955 | coordinate |
| PC | 5.735 | coordinate |
| infracollicular_sulcus | 9.500 | coordinate |
| pontomesencephalic_junction | 17.722 | coordinate |
| right_mammillary_body | 11.906 | coordinate |
| left_mammillary_body | 11.775 | coordinate |
| genu | 21.125 | coordinate |
| splenium | 3.694 | coordinate |

## mri32-crop

Normal completion: True. Fixed all-target reward: 0.0.

| Landmark | Error (mm) | Output / accepted |
| --- | ---: | --- |
| 1 | 25.860 | in_view / False |
| 2 | 27.327 | in_view / False |
| 3 | 14.610 | in_view / False |
| 4 | 14.005 | in_view / False |
| 5 | 15.056 | in_view / False |
| 6 | 23.845 | in_view / False |
| 7 | 23.427 | in_view / False |
| 8 | 17.034 | in_view / False |
| 9 | 17.036 | in_view / False |
| 10 | 10.394 | in_view / False |
| 11 | 18.605 | in_view / False |
| 12 | 20.279 | in_view / False |
| 13 | 20.169 | in_view / False |
| 14 | 28.034 | in_view / False |
| 15 | 15.432 | in_view / False |
| 16 | 17.871 | in_view / False |
| 17 | 15.325 | in_view / False |
| 18 | 15.219 | in_view / False |
| 19 | 22.088 | in_view / False |
| 20 | 12.001 | in_view / False |
| 21 | 32.671 | in_view / False |
| 22 | 26.734 | in_view / False |
| 23 | 26.163 | in_view / False |
| 24 | 24.648 | in_view / False |
| 25 | 32.629 | in_view / False |
| 26 | 29.899 | in_view / False |
| 27 | 20.527 | in_view / False |
| 28 | 22.375 | in_view / False |
| 29 | 17.466 | in_view / False |
| 30 | 14.850 | in_view / False |
| 31 | 7.778 | in_view / False |
| 32 | 8.118 | in_view / False |

## ct-crop

Normal completion: True. Fixed all-target reward: 0.0.

| Landmark | Error (mm) | Output / accepted |
| --- | ---: | --- |
| chin | — | empty / True |
| mand_r | 12.025 | in_view / False |
| mand_l | 5.625 | in_view / False |
| odont_proc | — | empty / True |

## Interpretation limits

CT slice spacing is 3 mm; MRI voxels are about 0.7 mm. Thresholds were fixed before results at 5/3 mm respectively. For cropped inputs, empty answers are valid only when the reference lies outside the FOV; an extrapolation must lie outside and be within 10 mm of the withheld point. MRI point 27 has one rater 3.138 mm from the consensus and requires caution near the threshold.

The CT full/crop tasks share the same four queries. The MRI eight/full and 32/crop conditions differ in both query set and FOV; they cannot isolate a crop effect. Full and cropped data come from the same subjects, not four independent patients. No blind author solver, independent clinical adjudication, or population accuracy estimate is claimed. Public training exposure remains possible.

Original freezes and first attempts remain unchanged. No retries or post-result threshold changes were used.
