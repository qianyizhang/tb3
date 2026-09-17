# BR-040 — Sol/xhigh landmark comparison

Same frozen 3D arrays, instructions, coordinate conventions and verifiers as the completed Terra/high runs. Both model and reasoning setting differ. One new Sol/xhigh attempt per condition; no retries.

| Input | Model / effort | Localization | Mean error, mm | False outside / absent detections |
|---|---|---|---:|---|
| ct-full | terra-high | 2/24 / 7/24 / 9/24 at [5, 10, 20] mm | 24.77 | 0/0 outside; 0/2 absent |
| ct-full | sol-xhigh | 1/24 / 13/24 / 23/24 at [5, 10, 20] mm | 10.24 | 0/0 outside; 0/2 absent |
| ct-partial | terra-high | 1/13 / 2/13 / 5/13 at [5, 10, 20] mm | 20.85 | 1/11 outside; 0/2 absent |
| ct-partial | sol-xhigh | 4/13 / 8/13 / 12/13 at [5, 10, 20] mm | 7.44 | 0/11 outside; 0/2 absent |
| mri32-full | terra-high | 3/32 / 8/32 / 20/32 at [3, 5, 10] mm | 9.40 | Not tested |
| mri32-full | sol-xhigh | 14/32 / 23/32 / 32/32 at [3, 5, 10] mm | 3.87 | Not tested |

CT false detections distinguish outside centres from genuinely absent T13/L6 under the source numbering convention. MRI has all 32 reference targets inside the scan; MRI hallucination was not tested. Each localization denominator includes all visible targets. The 0/0 full-CT outside entry means no such requests.

## Verification

Frozen file hashes were checked before and after each run. Sol task checksums must equal completed same-byte oracle, nop and Terra controls. The host scorer replays the frozen verifier; physical distances are independently recomputed in world coordinates. Trace audits retain actual image input counts and candidate network commands.

## Limits

One CT subject with two correlated views, one MRI subject, one attempt per condition and model. Sol/xhigh versus Terra/high changes both model and effort. CT labels follow the source convention; partial coverage can make enumeration uncertain. Exact reward alone is not a clinical or population capability claim.

## Evidence

- [Plan](BR-040-sol-landmarks.md)
- [Comparison data and trace audit](../evidence/br040-results.json)
- [Frozen inputs and control checksums](../evidence/br040-plan.json)
- Local comparison with per-landmark overlays: `runs/br040-sol-landmarks/review/index.html`.

## Interpretation and methods

Sol partial CT missed the visible T5 centre and marked T13 uncertain. It made no observed claims for unavailable targets; this does not equal perfect coverage. The mean 7.44 mm covers its 12 returned visible points, while localization success uses all 13 reference points.

Full CT improved substantially at 10/20 mm and in mean error, but its 5 mm count was 1/24 versus Terra 2/24. These endpoints should not be collapsed into a claim that Sol won every metric.

Sol MRI used AFIDs protocol illustrations and a labelled generic MNI152NLin2009cAsym template with affine registration, followed by manual review. B-spline refinement first failed, then was terminated without reported proposal files. The agent completed normally afterward. This is allowed atlas-assisted agent performance, not unaided visual localization. No target-subject annotation retrieval was found in the preserved commands or copied archive audit; the AFIDs index exposed dataset URLs but contained no subject FCSV files.

[Source assistance audit](../evidence/br040-source-audit.json) · [Configuration difference audit](../evidence/br040-config-audit.json) · [CT mask diagnostic](../evidence/br040-ct-diagnostic.json). The mask diagnostic does not alter the frozen score.
