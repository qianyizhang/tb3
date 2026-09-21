Source: `docs/research-rounds/BR-042-results.md`; original SHA-256: `7f2bab084ac260c7499993e54c2d5156e766d8aecac95c39ee03ff424284c9d5`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-042 V2 — Broad extraction succeeds in producing useful geometry; completeness and labels remain uneven

One Astra/medium attempt completed normally in **27 min 56 s** (1676.19 seconds), exporting **27 named polylines, 4394 points and 1739.9 mm** of combined courses. Eleven polylines carry coronary labels; sixteen cover other major vessels and branches. No model retry or external anatomical correction was supplied.

Plan and revision history (repository source locator: `BR-042-all-coronary.md`) · GT audit (repository source locator: `../evidence/br042-v2-gt-audit.json`) · Frozen spec (repository source locator: `../evidence/br042-v2-freeze.json`) · Results, replay and runtime (repository source locator: `../evidence/br042-v2-results.json`) · [Local interactive review](http://127.0.0.1:8795/).

## What was evaluated

The original full ImageCAS case 1 CTA was delivered without seeds, masks, landmarks, case-specific branch inventory or previous answers. The prompt requested all identifiable clinically relevant vessels and anatomical names. The ImageCAS-X annotations support evaluation of **11 coronary categories across both trees**, not every thoracic vessel. All other output remains available for source-image review. The public dataset provides segmentation-derived centerlines and segment labels; these are not newly adjudicated clinical truth. [Dataset documentation](https://github.com/kitbransby/ImageCAS-X).

The user's revision was applied before model exposure. Passing depends only on coverage: mean same-label recall ≥90% and each reference category ≥80%, within 1 mm. No precision, exact endpoint or length-ratio failure gate. The attempt **does not pass because coverage is incomplete**, independently of any extension beyond reference endpoints.

## Coronary results

| Reference category | Same-label coverage within 1 mm |
| --- | ---: |
| LM | 55.9% |
| LAD | 97.0% |
| LCx | 91.6% |
| D1 | 100.0% |
| D2 | 0.0% |
| OM1 | 0.0% |
| OM2 | 0.0% |
| RCA | 97.1% |
| R-PDA | 25.9% |
| R-PLA | 100.0% |
| Other | 0.0% |

**Geometric reference-length coverage:** 87.0% within 1 mm; 88.6% within 2 mm, ignoring labels. **Correct-label reference-length coverage:** 77.2%. **Mean per-category correct-label coverage:** 51.6%. The latter gives small branches equal weight, so it must not be directly interpreted as the same denominator as 87.0% length coverage. Five of eleven categories satisfy the 80% individual requirement.

A post-outcome nearest-label diagnostic separates several issues:

- Astra's OM1 course follows 88.9% of reference OM2 within 1 mm. Reference OM1 itself has no coverage. This is consistent with a missing earlier marginal branch and a numbering mismatch.
- Astra's D2 covers 78.0% of the reference Other category, while reference D2 has only 4.6% geometric coverage and no same-label coverage. Other aggregates additional diagonal/marginal branches; this does not establish the exact alternative anatomical name.
- R-PDA has 25.9% coverage even ignoring labels (30.7% same-label at 2 mm). This discrepancy is not merely extending past the annotation endpoint.
- LM has 84.5% geometric coverage but only 55.9% same-label coverage, partly because nearby submitted portions use LAD/LCx labels. The short trunk and segment boundaries make that distinction consequential.

These are matches to dataset categories, not independent clinical adjudication. No relabeling or trimming was applied to the saved output or pass decision.

## Extensions and vessels without GT

Same-label coronary precision is 63.6%; unlabeled coronary-only precision is 72.3%. These are **review diagnostics, not pass gates**. About 215.5 mm of submitted coronary length lies more than 1 mm from the reference tree; it may include extensions, omitted-from-GT branches or erroneous courses. This number does not distinguish those explanations.

The sixteen unscored paths total 961.7 mm. Their submitted names include ascending/descending aorta, pulmonary trunk, right/left pulmonary arteries, left lobar/segmental branches, four pulmonary veins with tributaries, and superior vena cava. The viewer provides all unchanged polylines, anatomical-name selection, native CTA slices, and optional coronary GT overlays. These names are model assignments awaiting human inspection. Do not call them all verified vessels or infer clinical completeness. Astra explicitly omitted unresolved peripheral vessels, coronary veins, inferior vena cava, azygos and some small coronary branches.

## Effectiveness and reproducibility

The run used two CPU cores, no GPU and a one-hour allowance. Harbor reports 5,103,417 cumulative input tokens, including 4,816,384 cached tokens, and 43,961 output tokens. These are cumulative across tool turns, not unique context size. Monetary cost is unavailable. The runtime context records `gpt-6-astra` / `medium`; this is not provider identity attestation.

Astra used its own image inspections to choose guide points, then classical vessel filtering, shortest paths, recentering and resampling. It generated executable code with image-specific guide lists. Thus the **agent task is image-only**, but the resulting script is not a general automatic seed-free extractor for unseen CTAs. Twenty-eight image-view call candidates were retained. No network-retrieval command candidates or pretrained-weight use were found; its method declares no external case assistance. Large-vessel label accuracy remains unverified.

## Validation and limits

Same-byte V2 Docker oracle=1 and no-op=0; model completed with no Harbor exception. Local omission, swapped-label and displaced-path controls failed; extension and unscored-extra positive controls passed. Frozen file hashes, task checksum agreement, exact artifact replay, and independently computed dense distances all agree. Historical BR-030/041 bytes remain unchanged.

One diagnostic implementation issue was identified: the frozen *unlabeled* precision includes code-0 paths. That raw 32.3% value is not a valid coronary-only precision estimate. Collection reports a clearly marked post-hoc coronary-only diagnostic (72.3%) and confirms unchanged 87.0% coverage. The primary same-label coverage and reward exclude code 0 by construction and are unaffected. Frozen metrics and task bytes are preserved.

This is one public development image. Different field of view, task scope and reasoning setting prevent attributing changes against BR-041 solely to medium versus xhigh. No new clinical adjudication or held-out generalization claim. Final report and submission workspace were not edited.

Raw answer: `runs/br042-all-vessels-astra-medium-v2-20260920/all-vessels__5Wo8h5i/artifacts/app/answer/`. Reproduce collection and viewer with `collect.py` and `build_review.py` in `probes/vessel-geometry/authoring/br042/`, using `.venv-br030/bin/python`. Viewer startup: `.venv-br030/bin/python -m http.server 8795 --bind 127.0.0.1 --directory runs/br042-all-vessels-v2/review`.

Viewer validation: native slice rendering, named aorta selection, jump-to-vessel, reference toggle and drag rotation were exercised in the browser. The selected aorta overlay was visibly present on the source CTA. This validates viewer interaction, not every anatomical assignment. The downloadable output is byte-identical to the submission.
