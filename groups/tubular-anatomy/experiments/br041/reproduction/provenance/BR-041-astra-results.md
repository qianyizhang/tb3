Source: `docs/research-rounds/BR-041-astra-results.md`; original SHA-256: `00c0393025916b8c0ae072078e24dd4df3ce7dca0a1724c844c1ce504666ea33`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-041 A01 — Astra traces R-PDA accurately, then extends beyond the reference

Astra/xhigh completed normally in **795.52 seconds (13 min 16 s)** on the unchanged CTA-only task. It selected the requested R-PDA and achieved **100% reference coverage within 1 mm**. The frozen score remains **fail**: its final route extends approximately **15 mm** beyond the reference endpoint, causing a 13.63 mm endpoint error and 6.10 mm full-route 95th-percentile distance.

Predeclared comparison (repository source locator: `BR-041-image-only-centerline.md#a01--astraxhigh-comparison-2026-09-19`) · Plan and hashes (repository source locator: `../evidence/br041-astra-plan.json`) · Results and replay (repository source locator: `../evidence/br041-astra-results.json`) · Trace/extent audit (repository source locator: `../evidence/br041-astra-audit.json`) · Local comparison figure (repository source locator: `../../runs/br041-image-only-centerline/astra-centerline-comparison.png`).

| Frozen task metric | Terra/high | Sol/xhigh | Astra/xhigh | Requirement |
| --- | ---: | ---: | ---: | ---: |
| Reference coverage within 1 mm | 0% | 80.62% | **100%** | ≥95% |
| 95th-percentile route distance | 31.41 mm | 20.44 mm | 6.10 mm | ≤1 mm |
| Proximal endpoint error | 17.73 mm | 3.08 mm | 1.95 mm | ≤5 mm |
| Distal endpoint error | 50.23 mm | 20.97 mm | 13.63 mm | ≤5 mm |
| Length | 93.30 mm | 180.32 mm | 179.67 mm | 161.39 mm ±15% |
| Format / sampling | Pass | Pass | Pass | Required |
| Overall | Fail | Fail | Fail | All required checks |

## Interpretation of the extension

Astra's saved 361-point route follows the requested reference, unlike Sol's R-PLA continuation. The nearest saved point to the reference endpoint is index 330, just 0.303 mm away. Thirty subsequent points add **14.965 mm** of arc. All full-route points farther than 1 mm from the reference occur at the first three proximal samples or after index 331; the proximal endpoint itself is within the predeclared 5 mm tolerance.

As a **post-outcome diagnostic only**, stopping at index 330 gives 100% coverage, 0.468 mm 95th-percentile distance, 164.71 mm length, and endpoint errors of 1.95/0.303 mm. Those values satisfy the geometric thresholds, but reference-assisted trimming is not a model success or a revised score. The submitted file remains unchanged.

Only 10% of the 30 extension points lie within 1 mm of the complete reference coronary mask. Their source intensities range from about 48 to 182 HU, median 103 HU. This establishes disagreement with the annotation extent; it does not independently prove that the extra course is fabricated anatomy. Faint distal vessel visibility, partial-volume effects and annotation scope need expert review before classifying this as a clean anatomical failure. The initial plan explicitly cautioned against interpreting terminal-extent disagreement alone that way.

For the user's feasibility question, Astra generated a closely matching image-derived centerline for the entire requested annotated route, with unresolved stopping-point accuracy. This is materially different from Terra's broad localization failure and Sol's wrong named branch. It is one case, not general capability or clinical validation.

## Execution and validation

One fresh `gpt-6-astra` / `xhigh` attempt, no hints, retries, previous answers or branch-error feedback. The same frozen task checksum matches oracle, no-op, Terra and Sol. All frozen bytes were verified before and after; saved-artifact replay and an independent dense pairwise-distance calculation agree exactly on the metrics. No Harbor exception or timeout occurred.

The retained runtime context records Astra/xhigh; no provider-side identity attestation is inferred. The trace contains 19 image-view calls, native image inspections, image-derived skeletons, Sato filtering, candidate anchors, physical shortest paths, transverse center refinement and native-affine export. Astra explicitly noticed a thinner candidate beside a brighter posterolateral continuation. Its method note flags distal uncertainty. No external case-specific retrieval was observed in the retained calls; the model declares no external assistance or pretrained segmentation use.

Raw output: `runs/br041-named-rca-astra-xhigh-v1-20260919/named-rca__i7yHodF/artifacts/app/answer/`. Reproduce collection, alternate-branch comparison, extent/trace audit and plotting with `collect_astra.py`, `branch_astra.py`, `audit_astra.py`, and `plot_astra.py` under `probes/vessel-geometry/authoring/br041/`, using `.venv-br030/bin/python`.

No frozen task, previous outcome, authored interview report or submission artifact was changed. This compares model plus reasoning setting on a public development image with an author-selected coronary crop.
