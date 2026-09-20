# BR-041 S01 — Sol/xhigh traces the coronary well, but chooses R-PLA

Sol/xhigh completed the unchanged image-only task normally in **1055.89 seconds (17 min 36 s)**. Its 363-point centerline covers **80.6%** of the requested RCA → R-PDA reference within 1 mm, substantially more than Terra/high's 0%. It nevertheless fails because its distal continuation follows the released **R-PLA** (posterolateral) route rather than the requested **R-PDA** (posterior descending) route.

[Predeclared comparison](BR-041-image-only-centerline.md#s01--solxhigh-comparison-2026-09-19) · [Plan and unchanged hashes](../evidence/br041-sol-plan.json) · [Results/replay](../evidence/br041-sol-results.json) · [Trace and branch audit](../evidence/br041-sol-audit.json) · [Local branch comparison](../../runs/br041-image-only-centerline/sol-centerline-comparison.png).

| Frozen task metric | Terra/high | Sol/xhigh | Requirement |
| --- | ---: | ---: | ---: |
| Reference coverage within 1 mm | 0% | 80.62% | ≥95% |
| Coverage within 2 mm | 0% | 81.23% | Diagnostic |
| 95th-percentile route distance | 31.41 mm | 20.44 mm | ≤1 mm |
| Proximal endpoint error | 17.73 mm | 3.08 mm | ≤5 mm |
| Distal endpoint error | 50.23 mm | 20.97 mm | ≤5 mm |
| Length | 93.30 mm | 180.32 mm | 161.39 mm ±15% |
| Format / sampling | Pass | Pass | Required |
| Overall | Fail | Fail | All required checks |

## Why the failure is narrower

After completion, the same saved Sol output was compared to the already retained ImageCAS-X right-coronary graph, using its published label map (10 = R-PDA, 11 = R-PLA). Against **R-PLA**, Sol has **0.351 mm** 95th-percentile distance, **98.62%** reference coverage within 1 mm, and proximal/distal endpoint errors of **3.08 / 3.23 mm**. The shared proximal course aligns closely; the output follows the alternative distal branch. This is a post-outcome diagnostic, not a changed task, retest, or passing score. It relies on released anatomical labels, without new clinical adjudication.

Sol's method note and messages identify the output as R-PDA and claim separation from posterolateral signal. The retained geometry contradicts that branch identity claim. The evidence supports good image-derived coronary centerline extraction on this case with a named-branch selection error, rather than Terra's broad failure to localize the coronary route.

## Validation and limits

The task bytes remained unchanged. Sol, Terra and the healthy oracle/no-op controls have the same Harbor task checksum. Exact artifact replay and an independent dense-distance calculation agree. Native voxel-to-RAS conversion uses the supplied NIfTI affine. Sol's retained context records `gpt-5.6-sol` / `xhigh`; this is runtime provenance, not provider-side identity attestation.

The trace contains 13 image-view calls, multiscale Sato vesselness, skeleton connectivity, proximal/distal crop expansion, smoothing, transverse subvoxel refinement, and cross-sectional image checks. No external case-specific retrieval was observed; the method note declares no internet or external assistance. There was one fresh attempt, no hints, retries, or Terra answers supplied. Harbor reports no exception and the model turn completed normally.

This compares **model plus reasoning setting** on one public development case. It does not establish overall model superiority, all-vessel completeness, clinical accuracy or a held-out benchmark result. Existing authored interview and submission artifacts remain untouched.

The saved output is in `runs/br041-named-rca-sol-xhigh-v1-20260919/named-rca__J54GxH2/artifacts/app/answer/`. Reproduce the post-outcome branch comparison with `branch_sol.py` and the figure with `plot_sol.py`, after `collect_sol.py`, under `probes/vessel-geometry/authoring/br041/`.
