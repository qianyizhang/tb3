# BR-042 V3 — All-vessel CTA extraction: geometry versus labeling

Two attempts completed normally; Astra/xhigh reached the 3600-second timeout after transport interruptions. **Astra/medium recovered 95.5% of annotated coronary length geometrically, but only 79.3% with the correct benchmark label.** Small-branch omissions and identity errors remain significant. Neither normally completed attempt passed either coverage gate. The Astra/xhigh saved output is included as an interrupted-attempt diagnostic, not a clean model-quality failure or completed comparison.

[Prospective plan](BR-042-v3-comparison.md) · [Exact prompt](../../probes/vessel-geometry/authoring/br042_v3/instruction.md) · [Input audit](../evidence/br042-v3-input-audit.json) · [Frozen task](../evidence/br042-v3-freeze.json) · [Numerical evidence](../evidence/br042-v3-results.json) · [Post-run audit](../evidence/br042-v3-review-audit.json).

## Scope and exposure

The output request remains all identifiable clinically relevant vessels in the full native CTA, including coronary arteries, other major arteries and veins. Automated evaluation covers only the available coronary reference: 11 present benchmark categories and 646.24 mm of annotated centerline. Unannotated vessels and continuations remain in the source-image viewer for human inspection. This GT cannot establish a complete thoracic vessel inventory or validate every submitted anatomical name.

Each setting received one fresh model attempt with a 3600-second allowance, 2-CPU configuration and 8192-MB memory configuration. Jobs ran sequentially because the Docker runtime had only four CPUs and approximately 8 GB total memory. All used the same frozen task checksum. The public prompt clarifies generic taxonomy, branch numbering, boundaries, uncertainty reporting and evaluation. No previous answer, patient-specific vessel inventory, target landmark, reference annotation or case feedback was supplied. The original full CTA and private reference bytes are unchanged; earlier frozen experiments remain untouched.

## Separate geometry and identity results

All Astra/xhigh values below describe its saved partial artifact. Coverage does not override its timeout or missing required method report.

| Model / effort | Attempt status | Time | Geometry length coverage | Labeled length coverage | Geometry macro | Labeled macro | Label accuracy on matched length | Geometry / labeled pass |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sol-xhigh | Completed | 41.60 min | 26.2% | 19.4% | 15.8% | 8.6% | 74.1% | False / False |
| astra-medium | Completed | 46.57 min | 95.5% | 79.3% | 81.3% | 55.3% | 83.1% | False / False |
| astra-xhigh | **Timed out; partial** | 60.00 min | 91.8% | 68.3% | 72.0% | 48.2% | 74.4% | False / False |

All coverage above uses 1 mm. Geometry and labeled columns share reference denominators. Geometry matches ignore submitted labels, including code 0. Passing requires macro ≥90% and each present category ≥80%.

| Category | sol-xhigh geometry / labeled | astra-medium geometry / labeled | astra-xhigh geometry / labeled |
| --- | ---: | ---: | ---: |
| LM | 0.0% / 0.0% | 100.0% / 88.7% | 100.0% / 83.1% |
| LAD | 0.0% / 0.0% | 100.0% / 98.7% | 100.0% / 94.5% |
| LCx | 0.0% / 0.0% | 99.8% / 99.8% | 86.6% / 86.6% |
| D1 | 17.1% / 0.0% | 100.0% / 100.0% | 100.0% / 0.0% |
| D2 | 0.0% / 0.0% | 3.1% / 0.0% | 4.6% / 0.0% |
| OM1 | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 0.0% |
| OM2 | 0.0% / 0.0% | 100.0% / 0.0% | 6.9% / 0.0% |
| RCA | 94.8% / 94.8% | 100.0% / 99.1% | 100.0% / 98.2% |
| R-PDA | 1.4% / 0.0% | 91.2% / 23.4% | 95.0% / 67.8% |
| R-PLA | 60.2% / 0.0% | 100.0% / 99.0% | 100.0% / 99.7% |
| Other | 0.0% / 0.0% | 100.0% / 0.0% | 99.1% / 0.0% |

| Model / effort | Geometry length at 2 mm | Labeled length at 2 mm | Geometry macro at 2 mm | Labeled macro at 2 mm |
| --- | ---: | ---: | ---: | ---: |
| sol-xhigh | 30.6% | 20.5% | 26.6% | 9.1% |
| astra-medium | 96.7% | 79.6% | 85.5% | 55.7% |
| astra-xhigh | 92.8% | 68.6% | 74.4% | 48.5% |

| Model / effort | Missed geometry, mm | Covered with wrong label, mm | Covered with correct label, mm |
| --- | ---: | ---: | ---: |
| sol-xhigh | 476.8 | 43.8 | 125.6 |
| astra-medium | 29.4 | 104.3 | 512.5 |
| astra-xhigh | 52.8 | 152.2 | 441.2 |

## What the separation reveals

**Sol/xhigh:** RCA coverage was strong (94.8% at 1 mm), while the annotated left main, LAD and LCx were not geometrically recovered. Its low score is not primarily a label-mapping problem: 476.8 mm of reference was geometrically missed. The submitted free-text inventory names a broader set of coronary vessels than the GT comparison supports. The run completed normally with 16 polylines.

**Astra/medium:** both main trees were largely recovered, but D2 had only 3.1% geometry coverage and OM1 had none. These short categories reduce the equal-category geometry mean to 81.3%, despite 95.5% length-weighted coverage. Identity errors are distinct: 13.57 mm of GT OM2 is labeled OM1; all 53.89 mm of GT Other is labeled D2. Of GT R-PDA, 19.50 mm matches the submitted inferior-LV branch and 11.75 mm the inferior-RV branch, both label 0; only 10.77 mm matches label 10. These are benchmark identity disagreements, not failures caused by endpoint extension. The missing upstream categories and shifted downstream labels are consistent with incomplete branch discovery affecting numbering, although the score alone cannot prove the model's reasoning mechanism.

Astra/medium completed with 65 polylines. Its inventory describes 17 coronary arterial courses/divisions, four cardiac venous courses and 44 great-vessel/pulmonary courses/divisions. Its method notes identify uncertainty in branch identities, distal arterial/venous apposition and segment boundaries, and distinguish untraced candidates from anatomical absence. These notes are model-authored observations, not independent clinical adjudication.

**Astra/xhigh, interrupted:** the saved 33-polyline output recovered 91.8% of annotated length geometrically and 68.3% with the correct label. GT D1 is geometrically recovered but labeled ramus intermedius (72.35 mm, code 8); GT Other is mostly labeled D1 (53.38 mm, code 4). D2, OM1 and OM2 remain poorly recovered. R-PDA labeled coverage is higher than Astra/medium's saved result (67.8% versus 23.4%), while other disagreements lower the overall labeled score. These partial differences do not establish an effort-level ranking.

Astra/xhigh retained executable extraction code, centerlines, validation JSON and an inventory CSV, but **did not finish method.md or issue a final completion response**. Its CSV refers to the missing method file for uncertainty details. The trajectory mentions unresolved ramus-versus-early-diagonal identity. The viewer explicitly marks this output partial and links the retained CSV rather than fabricating a method report.

Polyline count and output length are not counts of independently validated vessels. Longer, broader output is not automatically more complete or more correct. Unannotated courses, distal continuations and anatomical connections require human inspection.

## Evaluation contract

Both metrics use the same label-independent nearest geometric correspondence. Reference and submitted segments are sampled at intervals no greater than 0.25 mm with physical arc-length weights; endpoint-label transitions switch at their midpoint. Distance ties are resolved in original submitted order, without consulting labels. Code-0 output can recover geometry; correctly labeled coverage requires that same nearest match to carry the reference code. Thus finding geometry and identifying it cannot substitute for one another.

Both pass gates require equal-category macro coverage ≥90% and every present category ≥80% at 1 mm. Harbor's scalar reward records the labeled pass. The tables also retain length-weighted coverage, 2 mm sensitivity, conditional label accuracy, and a reference-length partition into missed geometry, covered with a wrong label, and covered with a correct label.

No precision, endpoint or length-ratio pass gate is imposed. Per-output reference agreement and unmatched length are diagnostics only. Unmatched output is not automatically an extension or false vessel, because the reference omits other vascular anatomy. A geometry-coverage result does not by itself establish continuous central-lumen tracing, correct branch connections, correct free-text names or clinical completeness. Category 14 also aggregates additional branch identities.

## Execution, exclusions and verification

The two initial Astra job setups failed during Debian package installation before model execution: no model turn or session was recorded. Both setup records are retained. A disposable installation check succeeded, and fresh setup-recovery jobs used identical task bytes and agent settings. These were recoveries before any model attempt, not second scored model attempts. No started model attempt was rerun.

Astra/xhigh later recorded repeated WebSocket disconnects, fallback to HTTPS, and two network-wait messages. It resumed work but ultimately reached the fixed one-hour limit. Transport interruptions affect elapsed time and available work time; their exact contribution is not isolated. **The timeout is an interrupted execution, not a normally completed anatomical failure.** No wall-time correction or hypothetical uninterrupted score is claimed.

Oracle/no-op Docker controls returned 1/0 on the same task bytes. Local controls cover correct output, label swapping, all-zero labels, missing trees/short branches, translation, extensions, unscored extra vessels and exact duplicate alternative geometry. Geometry remains passing under label swaps while labeled coverage fails; extensions and unscored extra curves do not create a pass penalty.

Frozen-scorer replay exactly matches each retained verifier result, including the interrupted artifact. Independently computed dense nearest distances reproduce the reported coverage values. All saved points lie inside the native field with a 1e-5-voxel numerical boundary tolerance; Astra/medium has only approximately 4.75e-7-voxel serialization excursions beyond strict voxel-center bounds. The diagnostic preserves original coordinates and does not modify scoring. Centerline schemas are valid in all three artifacts. Source intensity is a diagnostic, not proof of vessel identity.

The limited source-access trace scan found no case-annotation retrieval. Its one Astra/xhigh candidate was manually cleared: `requests.items()` iterates a local dictionary of image-derived route endpoints, not an HTTP request. Runtime contexts record the requested model/effort settings; that is configuration evidence, not provider identity attestation.

## Effort and retained artifacts

Wall time below is agent execution, excluding setup and verification, but including computation, review and any transport interruption. Token counts are recorded cumulative usage, including repeated/cached context; interrupted-run counts should not be treated as complete billing. Sol's monetary value is a Harbor-recorded estimate; Astra monetary cost was unavailable.

| Setting | Agent wall time | Polylines / points | Submitted length | Input / cached / output tokens | Recorded cost |
| --- | ---: | ---: | ---: | --- | ---: |
| sol-xhigh | 41m 36s | 16 / 2,366 | 1164.1 mm | 19,178,931 / 18,924,800 / 86,759 | $10.3216 |
| astra-medium | 46m 34s | 65 / 6,289 | 2460.8 mm | 9,236,374 / 9,021,824 / 78,669 | Unavailable |
| astra-xhigh (partial) | 60m 00s | 33 / 4,075 | 1806.4 mm | 6,911,192 / 6,619,008 / 46,852 | Unavailable |

Astra/medium's internal replay returned exit 0 and reproduced its output bytes in 35.10 seconds. That replays case-specific image-derived choices and code; it is not autonomous rediscovery in 35 seconds. Interactive discovery and review took 46m 34s.

Local review: [comparative native-CTA viewer](http://127.0.0.1:8796/). Its output JSON copies match the retained submission hashes. Run selection, vessel selection, native-slice navigation, reference toggling and 3D rotation are available. The original downloads retain all submitted names, labels and coordinates. Local bundle: `runs/br042-all-vessels-v3/`; serve its `review/` directory over loopback if the viewer server is stopped.

Retained answer directories:

- sol-xhigh: `runs/br042-all-vessels-sol-xhigh-v3-20260920/all-vessels__5U7REa4/artifacts/app/answer`.
- astra-medium: `runs/br042-all-vessels-astra-medium-v3-20260920-setup-recovery1/all-vessels__tvkf3rA/artifacts/app/answer`.
- astra-xhigh: `runs/br042-all-vessels-astra-xhigh-v3-20260920-setup-recovery1/all-vessels__6wwRK7K/artifacts/app/answer`.

## Limits on conclusions

Astra/medium provides the strongest normally completed result in this small comparison: broad coronary geometry recovery, with substantial remaining labeling and small-branch discovery gaps. The interrupted Astra/xhigh run does not supply a clean completed comparison of reasoning effort. One public development case and one model attempt per setting do not establish a general model ranking or clinical readiness.

V3 was authored after earlier outcomes, although no case answers were exposed; it is not an independently designed held-out prompt. V2 and V3 also differ in matching semantics, so their original reported numbers do not isolate a causal prompt-refinement effect. No expert has adjudicated every vessel, anatomical name, connection or distal extent. Noncoronary completeness remains unmeasured by this GT.
