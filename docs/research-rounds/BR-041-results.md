# BR-041 — Terra missed the named coronary route from CTA alone

One Terra/high attempt completed normally in **843.80 seconds (14 min 4 s)** and produced a valid 197-point centerline, but failed every anatomical geometry criterion. This is a substantial localization/route-selection failure on this development case, not a timeout, invalid output, CPR metadata failure or marginal distal endpoint disagreement.

[Plan](BR-041-image-only-centerline.md) · [Frozen task hashes](../evidence/br041-freeze.json) · [Results and controls](../evidence/br041-results.json) · [Coordinate/trace audit](../evidence/br041-audit.json) · [Local comparison figure](../../runs/br041-image-only-centerline/centerline-comparison.png).

## What changed

BR-030 already asked Terra to generate its centerline: it supplied a predicted lumen mask and exact start/end landmarks, not the full reference line. That attempt passed tracing. BR-041 supplies the **same CTA crop plus the named RCA ostium → distal R-PDA request**, without mask, landmarks, review marker or prior solution. CPR and mesh are omitted. The contrast removes several aids together, so it cannot isolate which aid mattered most.

## Measured result

| Check | Terra | Predeclared requirement |
| --- | ---: | ---: |
| Format and sampling | Pass; 197 points | 100–2000 finite RAS points, steps 0.05–0.75 mm |
| 95th-percentile route distance | 31.411 mm | ≤1 mm |
| Reference coverage within 1 mm | 0% | ≥95% |
| Reference coverage within 2 mm | 0% | Diagnostic only |
| Proximal / distal endpoint errors | 17.733 / 50.234 mm | Each ≤5 mm |
| Route length | 93.298 mm vs 161.394 mm reference | Within 15% |
| Overall | Fail | All required checks |

The separate Docker oracle passed and no-op failed. Reversed, translated and straight-route local negative controls failed their intended criteria. All three Docker runs shared the identical task checksum, and every frozen file remained unchanged. Artifact replay exactly matches the verifier; a separate dense pairwise-distance implementation agrees with the route metrics.

## Trace interpretation

The retained context records `gpt-5.6-terra` / `high`; no provider-side identity attestation is inferred. Terra made 26 image-view tool calls, constructed Hessian/tubularity and intensity-based path costs, inspected candidate geodesics, and exported a spline-smoothed route using `nib.affines.apply_affine(aff, ijk)`. The native image affine is the correct contract. Both reference and output lie inside the delivered image. There is no evidence of an evaluator-wide coordinate mismatch.

The reference has 100% of points within 1 mm of the full corrected coronary mask; Terra has 0%. Terra's median sampled intensity is nevertheless 363 HU (reference 382 HU): bright contrast alone does not establish coronary identity. We do not assign a specific alternative anatomical structure without expert adjudication.

Some model-authored MIP displays transpose arrays while retaining labels for the untransposed axes. This is a possible model-side visualization/localization contributor, not a proven sole cause. The model also restricts several intermediate searches to a smaller subvolume than the complete reference route occupies. These were its own choices; the delivered crop includes the full reference.

No external case-specific annotation retrieval was observed in the retained tool calls. Terra searched the container for coronary/ImageCAS files, but evaluator annotations were isolated in a separate verifier image. Its method note declares only the supplied source notice. The run had startup/model-list refresh warnings but a normal completed model turn and no Harbor exception. An initial sandboxed host invocation could not reach Docker and launched no trial; the actual controlled jobs ran after Docker access was enabled. No model retry or hints were given.

## Scope

This establishes one completed image-only failure with healthy controls. It does not establish a population failure rate, all-major-vessel capability, clinical validity, or an inability to generate centerlines with a segmentation aid. The public training/development case and author-selected coronary crop remain limitations. No new expert reference adjudication was performed. No thresholds were tightened after observing the result, and no historical task bytes were changed.

The output and method note remain under `runs/br041-named-rca-terra-high-v1-20260919/named-rca__FfwnqBT/artifacts/app/answer/`. The interview report and submission workspace were not modified.
